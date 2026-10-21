"""Append-only log of Valency Bond queries (logs/bond_queries.jsonl, published)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / "logs" / "bond_queries.jsonl"


def log(tool: str, query: str, purpose: str, n_results: int, kept: list[str], agent: str = "claude-opus"):
    LOG.parent.mkdir(exist_ok=True)
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "agent": agent, "tool": tool, "query": query,
           "purpose": purpose, "n_results": n_results, "kept": kept}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    a = json.loads(sys.stdin.read())
    log(**a)
