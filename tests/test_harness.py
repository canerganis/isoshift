import json
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness import llm
from harness.cache import DiskCache, append_jsonl, sha256_hex
from harness.literature import OpenAlexSource, reconstruct_abstract, parse_work, LiteratureSource
from harness.llm import extract_json, ask_json


def test_hash_stable_and_distinct():
    assert sha256_hex("a", "b") == sha256_hex("a", "b")
    assert sha256_hex("ab", "") != sha256_hex("a", "b")


def test_disk_cache_roundtrip(tmp_path):
    c = DiskCache(tmp_path)
    assert c.get("k") is None
    c.set("k", {"x": [1, 2], "u": "é"})
    assert c.get("k") == {"x": [1, 2], "u": "é"}


def test_jsonl_append(tmp_path):
    p = tmp_path / "sub" / "log.jsonl"
    append_jsonl(p, {"a": 1})
    append_jsonl(p, {"a": 2})
    rows = [json.loads(l) for l in p.read_text().splitlines()]
    assert [r["a"] for r in rows] == [1, 2] and "ts" in rows[0]


@pytest.mark.parametrize("text,expected", [
    ('{"ok": true}', {"ok": True}),
    ('```json\n{"ok": true}\n```', {"ok": True}),
    ('Sure! Here:\n```\n[1, 2, 3]\n```\nDone', [1, 2, 3]),
    ('Answer is {"a": {"b": "}"}, "c": 1} thanks', {"a": {"b": "}"}, "c": 1}),
])
def test_extract_json(text, expected):
    assert extract_json(text) == expected


def test_extract_json_fails():
    with pytest.raises(ValueError):
        extract_json("no json here")


def _fake_ask_factory(replies):
    calls = []

    def fake(model, prompt, **kw):
        calls.append(prompt)
        return llm.Result(text=replies[len(calls) - 1], model=model, latency_s=0.0, cached=False, prompt_hash="h")
    return fake, calls


class M(BaseModel):
    ok: bool


def test_ask_json_repair(monkeypatch):
    fake, calls = _fake_ask_factory(["not json", '```json\n{"ok": true}\n```'])
    monkeypatch.setattr(llm, "ask", fake)
    obj, _ = ask_json("opus-5.5", "q", M)
    assert obj.ok is True and len(calls) == 2


def test_ask_json_schema_dict_invalid_then_fail(monkeypatch):
    fake, calls = _fake_ask_factory(['{"ok": "x"}', '{"ok": "y"}'])
    monkeypatch.setattr(llm, "ask", fake)
    with pytest.raises(ValueError):
        ask_json("opus-5.5", "q", {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]})
    assert len(calls) == 2


def test_ask_uses_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "c")
    monkeypatch.setattr(llm, "LOG_PATH", tmp_path / "log.jsonl")
    n = {"c": 0}

    def fake_run(model, text, timeout):
        n["c"] += 1
        return "hello"
    monkeypatch.setattr(llm, "_run_agy", fake_run)
    r1 = llm.ask("opus-5.5", "p", system="s")
    r2 = llm.ask("opus-5.5", "p", system="s")
    r3 = llm.ask("opus-5.5", "p", system="s", cache=False)
    assert (r1.cached, r2.cached, r3.cached) == (False, True, False)
    assert n["c"] == 2 and r2.text == "hello" and r1.prompt_hash == r2.prompt_hash
    rows = [json.loads(l) for l in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert len(rows) == 3 and rows[1]["cached"] is True


def test_ask_error_not_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "c")
    monkeypatch.setattr(llm, "LOG_PATH", tmp_path / "log.jsonl")

    def boom(model, text, timeout):
        raise RuntimeError("x")
    monkeypatch.setattr(llm, "_run_agy", boom)
    r = llm.ask("opus-5.5", "p")
    assert r.error and not r.ok
    assert not list((tmp_path / "c").glob("*.json"))


def test_unknown_model():
    with pytest.raises(ValueError):
        llm.ask("nope", "x")


def test_reconstruct_abstract():
    assert reconstruct_abstract({"hello": [0, 2], "big": [1], "world": [3]}) == "hello big hello world"
    assert reconstruct_abstract(None) == ""


def test_parse_work():
    p = parse_work({"id": "https://openalex.org/W1", "doi": "https://doi.org/10.1/x", "title": "T",
                    "publication_year": 2024, "abstract_inverted_index": {"a": [0]}, "cited_by_count": 3})
    assert (p.doi, p.year, p.abstract, p.cited_by_count) == ("10.1/x", 2024, "a", 3)


def test_literature_interface():
    assert issubclass(OpenAlexSource, LiteratureSource)


@pytest.mark.live
def test_openalex_live(tmp_path):
    src = OpenAlexSource(cache_dir=tmp_path)
    res = src.search("machine learning interatomic potential", year_from=2023, year_to=2025, limit=5)
    assert res and all(2023 <= p.year <= 2025 for p in res)
    assert any(p.abstract for p in res)
    # second call served from cache
    assert [p.id for p in src.search("machine learning interatomic potential", year_from=2023, year_to=2025, limit=5)] == [p.id for p in res]
