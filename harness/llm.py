"""One entry point for the three subscription-CLI models.

    from harness import ask
    r = ask("gpt-6-astra", "Say hi")
    r.text, r.latency_s, r.cached, r.error

Models: "gpt-6-astra" (codex exec), "gemini-4-argon", "opus-5.5" (agy).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .cache import DiskCache, ROOT, append_jsonl, sha256_hex

AGY = os.environ.get(
    "AGY_EXE",
    r"C:\Users\can02\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\agy\bin\agy.exe",
)
CODEX = os.environ.get("CODEX_EXE", "codex")

AGY_MODELS = {
    "gemini-4-argon": "gemini-4-argon-high",
    "opus-5.5": "claude-opus-5-5-high",
}
CODEX_MODELS = {"gpt-6-astra": "gpt-6-astra"}
MODELS = tuple(list(CODEX_MODELS) + list(AGY_MODELS))

CACHE_DIR = Path(os.environ.get("HARNESS_CACHE_DIR", ROOT / ".cache" / "llm"))
LOG_PATH = Path(os.environ.get("HARNESS_LOG", ROOT / "logs" / "llm_calls.jsonl"))
# Windows CreateProcess limit is 32767 chars for the whole command line.
AGY_ARGV_MAX = 30000


@dataclass
class Result:
    text: str
    model: str
    latency_s: float
    cached: bool
    prompt_hash: str
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict:
        return asdict(self)


def _full_prompt(prompt: str, system: str | None, json_schema: dict | None) -> str:
    parts = []
    if system:
        parts.append(f"[SYSTEM INSTRUCTIONS]\n{system}\n[END SYSTEM INSTRUCTIONS]\n")
    parts.append(prompt)
    if json_schema is not None:
        parts.append(
            "\n\nRespond with ONLY a single JSON value (no prose, optional json code fence) "
            "matching this JSON schema:\n" + json.dumps(json_schema)
        )
    return "\n".join(parts)


_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def _run_codex(model: str, text: str, timeout: int, effort: str | None = None) -> str:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.txt"
        cmd = [CODEX, "exec", "--skip-git-repo-check", "-s", "read-only",
               "-m", CODEX_MODELS[model], "-o", str(out)]
        if effort:
            cmd += ["-c", f"model_reasoning_effort={effort}"]
        cmd.append("-")
        p = subprocess.run(cmd, input=text, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout,
                           shell=(os.name == "nt" and CODEX == "codex"), cwd=td)
        if p.returncode != 0:
            raise RuntimeError(f"codex exit {p.returncode}: {(p.stderr or p.stdout)[-800:]}")
        if not out.exists() or not out.read_text(encoding="utf-8", errors="replace").strip():
            raise RuntimeError(f"codex produced no output file; stderr tail: {p.stderr[-500:]}")
        return out.read_text(encoding="utf-8", errors="replace").strip()


def _run_agy(model: str, text: str, timeout: int) -> str:
    # agy -p has no stdin support. Short prompts go in argv; long ones via a temp file
    # that the agent is asked to read (workspace is a scratch dir).
    td_ctx = None
    cwd = None
    prompt_arg = text
    if len(text) > AGY_ARGV_MAX:
        td_ctx = tempfile.TemporaryDirectory()
        cwd = td_ctx.name
        pf = Path(cwd) / "prompt.txt"
        pf.write_text(text, encoding="utf-8")
        prompt_arg = (f"Read the file {pf} in full and follow the instructions inside it exactly. "
                      "Reply with only the answer the file asks for, nothing else.")
    try:
        # Headless agy auto-denies reads outside the workspace; adding the repo makes its
        # files readable (workspace reads are auto-granted, writes still need approval).
        cmd = [AGY, f"-p={prompt_arg}", "--model", AGY_MODELS[model], "--output-format", "text",
               "--add-dir", str(ROOT)]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, cwd=cwd)
        if p.returncode != 0:
            raise RuntimeError(f"agy exit {p.returncode}: {(p.stderr or p.stdout)[-800:]}")
        out = _ANSI.sub("", p.stdout).strip()
        if not out:
            raise RuntimeError(f"agy empty output; stderr tail: {p.stderr[-500:]}")
        return out
    finally:
        if td_ctx:
            td_ctx.cleanup()


def ask(model: str, prompt: str, *, system: str | None = None,
        json_schema: dict | None = None, timeout: int = 600, cache: bool = True,
        effort: str | None = None) -> Result:
    """effort: codex reasoning effort (low/medium/high/xhigh); ignored for agy models."""
    if model not in MODELS:
        raise ValueError(f"unknown model {model!r}; choose from {MODELS}")
    full = _full_prompt(prompt, system, json_schema)
    if model not in CODEX_MODELS:
        effort = None
    key = sha256_hex(model, system or "", prompt,
                     json.dumps(json_schema, sort_keys=True) if json_schema else "",
                     *([effort] if effort else []))
    store = DiskCache(CACHE_DIR)
    if cache:
        hit = store.get(key)
        if hit and hit.get("error") is None:
            append_jsonl(LOG_PATH, {"model": model, "hash": key, "latency_s": 0.0, "ok": True,
                                    "cached": True, "error": None})
            return Result(text=hit["text"], model=model, latency_s=0.0, cached=True, prompt_hash=key)
    t0 = time.time()
    text, err = "", None
    try:
        if model in CODEX_MODELS:
            text = _run_codex(model, full, timeout, effort)
        else:
            text = _run_agy(model, full, timeout)
    except subprocess.TimeoutExpired:
        err = f"timeout after {timeout}s"
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    lat = round(time.time() - t0, 3)
    r = Result(text=text, model=model, latency_s=lat, cached=False, prompt_hash=key, error=err)
    append_jsonl(LOG_PATH, {"model": model, "hash": key, "latency_s": lat, "ok": err is None,
                            "cached": False, "error": err})
    if err is None and cache:
        store.set(key, {"model": model, "system": system, "prompt": prompt, "text": text,
                        "latency_s": lat, "error": None})
    return r


# ---------------- JSON extraction ----------------

_FENCE = re.compile(r"```(?:json|JSON)?\s*\n?(.*?)```", re.S)


def _balanced_candidates(s: str):
    for i, ch in enumerate(s):
        if ch in "{[":
            close = "}" if ch == "{" else "]"
            depth, in_str, esc = 0, False, False
            for j in range(i, len(s)):
                c = s[j]
                if in_str:
                    if esc:
                        esc = False
                    elif c == "\\":
                        esc = True
                    elif c == '"':
                        in_str = False
                    continue
                if c == '"':
                    in_str = True
                elif c == ch:
                    depth += 1
                elif c == close:
                    depth -= 1
                    if depth == 0:
                        yield s[i:j + 1]
                        break


def extract_json(text: str) -> Any:
    """Parse JSON from raw text, a fenced block, or prose with an embedded JSON value.
    Raises ValueError if nothing parses."""
    t = text.strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    for m in _FENCE.finditer(t):
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            continue
    for cand in _balanced_candidates(t):
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            continue
    raise ValueError("no valid JSON found in text")


def _validate(obj: Any, schema):
    """schema: pydantic v2 model class, or a JSON-schema dict. Returns validated object."""
    if schema is None:
        return obj
    if isinstance(schema, dict):
        import jsonschema
        jsonschema.validate(obj, schema)
        return obj
    return schema.model_validate(obj)


def ask_json(model: str, prompt: str, schema=None, *, system: str | None = None,
             timeout: int = 600, cache: bool = True, repair: bool = True,
             effort: str | None = None):
    """ask() + extract + validate; on failure re-ask once with the error. Returns (obj, Result).
    `schema` may be a pydantic model class or a JSON-schema dict. Raises ValueError on failure."""
    js = None
    if isinstance(schema, dict):
        js = schema
    elif schema is not None:
        js = schema.model_json_schema()
    r = ask(model, prompt, system=system, json_schema=js, timeout=timeout, cache=cache, effort=effort)
    if r.error:
        raise ValueError(f"LLM call failed: {r.error}")
    try:
        return _validate(extract_json(r.text), schema), r
    except Exception as e:  # noqa: BLE001
        if not repair:
            raise ValueError(f"bad JSON: {e}") from e
        fix = (f"{prompt}\n\nYour previous reply was not valid ({type(e).__name__}: {str(e)[:500]}).\n"
               f"Previous reply:\n{r.text[:4000]}\n\nReply again with ONLY the corrected JSON.")
        r2 = ask(model, fix, system=system, json_schema=js, timeout=timeout, cache=cache, effort=effort)
        if r2.error:
            raise ValueError(f"repair call failed: {r2.error}")
        try:
            return _validate(extract_json(r2.text), schema), r2
        except Exception as e2:  # noqa: BLE001
            raise ValueError(f"bad JSON after repair: {e2}") from e2
