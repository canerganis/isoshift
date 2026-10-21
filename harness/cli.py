"""Command-line entry for agents that can only run shell commands.

    python -m harness.cli --model gpt-6-astra --effort xhigh --prompt-file p.md --out reply.md
    python -m harness.cli --model gemini-4-argon --prompt "Say hi"

Prints the reply (or writes it to --out). Exit code 1 on model error.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .llm import MODELS, ask


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="harness.cli")
    ap.add_argument("--model", required=True, choices=MODELS)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file")
    ap.add_argument("--system-file")
    ap.add_argument("--effort", choices=["low", "medium", "high", "xhigh"])
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    prompt = a.prompt if a.prompt is not None else Path(a.prompt_file).read_text(encoding="utf-8")
    system = Path(a.system_file).read_text(encoding="utf-8") if a.system_file else None
    r = ask(a.model, prompt, system=system, timeout=a.timeout, cache=not a.no_cache, effort=a.effort)
    if r.error:
        print(f"ERROR: {r.error}", file=sys.stderr)
        return 1
    if a.out:
        Path(a.out).write_text(r.text, encoding="utf-8")
        print(f"wrote {a.out} ({len(r.text)} chars, {r.latency_s}s, cached={r.cached})")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(r.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
