"""Live smoke test: tiny JSON call and ~2k-token prompt latency per model. Writes prep/harness_smoke.md.
Usage: python -m harness.smoke"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from .llm import MODELS, ask, extract_json
from .cache import ROOT


def big_prompt(n_words: int = 1500) -> str:
    filler = " ".join(f"item{i} alpha beta gamma delta" for i in range(n_words // 5))
    return ("Below is filler text. Ignore it. After it, answer the question.\n\n" + filler +
            '\n\nQuestion: reply with ONLY the JSON {"ok": true, "words_seen": "many"}')


def main():
    rows = []
    for m in MODELS:
        tiny = ask(m, f'Reply with ONLY this JSON: {{"ok": true, "model": "{m}"}}', cache=False, timeout=300)
        try:
            tiny_ok = extract_json(tiny.text).get("ok") is True if not tiny.error else False
        except Exception:
            tiny_ok = False
        bp = big_prompt()
        big = ask(m, bp, cache=False, timeout=600)
        try:
            big_ok = extract_json(big.text).get("ok") is True if not big.error else False
        except Exception:
            big_ok = False
        rows.append((m, tiny, tiny_ok, big, big_ok, len(bp)))
        print(m, tiny.latency_s, tiny.error, big.latency_s, big.error, flush=True)
    out = ["# Harness live smoke test", "", f"Run: {time.strftime('%Y-%m-%d %H:%M:%S')}", "",
           "| model | tiny latency (s) | tiny ok | ~2k-token latency (s) | big ok | big prompt chars | errors |",
           "|---|---|---|---|---|---|---|"]
    for m, t, tok, b, bok, n in rows:
        errs = "; ".join(x for x in (t.error, b.error) if x) or "none"
        out.append(f"| {m} | {t.latency_s} | {tok} | {b.latency_s} | {bok} | {n} | {errs[:200]} |")
    out += ["", "## Raw replies", ""]
    for m, t, _, b, _, _ in rows:
        out += [f"### {m}", "tiny:", "```", t.text[:500] or str(t.error), "```",
                "big:", "```", b.text[:500] or str(b.error), "```", ""]
    (ROOT / "prep").mkdir(exist_ok=True)
    (ROOT / "prep" / "harness_smoke.md").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
