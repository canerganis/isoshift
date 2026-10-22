"""Fill the freeze placeholders in the story files from the frozen result files (decisions 06 action 8 and 07 action 4).

Placeholders are written as a key in double braces. Numeric keys are the pre-freeze values of the video script and
only serve as names (for example 123 = rows right, 130 = evaluations); SEVENN is the separately labelled SevenNet
sentence of decision 07. Every value is read from results/F01_cv.json, except the screen-wide all-row slopes, which
are refitted from results/decompose_pairs.csv (three models).

    python -m src.isoshift_event.fill_placeholders            # fill placeholders in place, then verify
    python -m src.isoshift_event.fill_placeholders --check    # print the value map and verify, change nothing

Targets: README.md, docs/story, docs/findings and state/GOAL.md (app/ reads F01_cv.json itself and is not touched).
The verify step checks that the decision 07 headline numbers, as computed from the JSON, appear in the four headline
files. Exits non-zero on an unknown key, a double brace left after filling, or a headline file that misses a number.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
QUANT = ("mace", "orb", "mattersim")
PLACEHOLDER = re.compile(r"\{\{([^{}]+)\}\}")
TARGET_DIRS = ("docs/story", "docs/findings")
TARGET_FILES = ("README.md", "state/GOAL.md")
HEADLINE_FILES = ("README.md", "docs/story/writeup.md", "docs/findings/F01-xh-length-rule.md", "state/GOAL.md")


def all_row_slopes() -> dict[str, float]:
    """Screen-wide fit (all clean covalent rows per model), the population of the headline slope sentence."""
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    c = d[(d.clean == True) & (d.covalent_XH == True)]  # noqa: E712
    out = {}
    for m in QUANT:
        g = c[c.model == m]
        out[m] = float(np.polyfit(g.dXH_mean_A * 1000, g.ddF_total / g.H_per_atom, 1)[0])
    return out


def _cv() -> dict:
    return json.loads((ROOT / "results" / "F01_cv.json").read_text(encoding="utf-8"))


def sevenn_sentence(cv: dict) -> str:
    sv = cv.get("sevenn_sign_votes", {})
    four, alone = sv.get("four_models_oh_unfiltered_strong"), sv.get("sevenn_only_oh_unfiltered_strong")
    if not (four and alone):
        return "SevenNet runs did not finish before the compute freeze and are not used."
    fm = four["unique_pair_majority"]
    same = "the same " if fm["wrong"] == cv["oh_unfiltered_strong"]["unique_pair_majority"]["wrong"] else ""
    return (f"SevenNet, used for sign votes only, gets {alone['right']} of {alone['n']} on the same population "
            f"(baseline {alone['baseline_right']} of {alone['n']}); as a fourth vote the count is {four['right']} of "
            f"{four['n']} against {four['baseline_right']}, with {fm['right']} pairs right and {same}{fm['wrong']} wrong.")


def frozen_values(cv: dict | None = None) -> dict[str, str]:
    cv = cv or _cv()
    h = cv["oh_unfiltered_strong"]
    maj = h["unique_pair_majority"]
    oh_all = cv["oh_split"]["all_eligible"]["all_regimes"]["O-H"]
    s = all_row_slopes()
    return {
        "123": str(h["right"]),
        "130": str(h["n"]),
        "82": str(h["baseline_right"]),
        "197": str(cv["n_unique_pairs"]["unique_pairs"]),
        "0.12 to 0.15": f"{min(s.values()):.2f} to {max(s.values()):.2f}",
        "62": str(maj["right"]),
        "5": str(maj["tie"]),
        "0": str(maj["wrong"]),
        "1": str(oh_all["right"] - h["right"]),
        "16": str(oh_all["n"] - h["n"]),
        "SEVENN": sevenn_sentence(cv),
    }


def headline_numbers(cv: dict, v: dict[str, str]) -> list[str]:
    """Decision 07 headline fragments as computed from the frozen JSON."""
    h = cv["oh_unfiltered_strong"]
    maj = h["unique_pair_majority"]
    return [f"Across {v['197']} hydrogen-compound polymorph pairs",
            f"changes by {v['0.12 to 0.15']} meV per H",
            f"in {h['right']} of {h['n']} O-H model evaluations",
            f"({h['n_pairs']} pairs, {h['n_formulas']} formulas)",
            f"against {h['baseline_right']} of {h['n']} for a constant-sign baseline",
            f"By model majority {maj['right']} pairs are right and {maj['wrong']} are wrong"]


def targets() -> list[Path]:
    files = [ROOT / f for f in TARGET_FILES]
    for d in TARGET_DIRS:
        files += sorted(p for p in (ROOT / d).rglob("*.md") if p.is_file())
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print the map and verify; write nothing")
    args = ap.parse_args(argv)
    cv = _cv()
    vals = frozen_values(cv)
    for k, v in vals.items():
        print(f"{{{{{k}}}}} -> {v}")
    bad = 0
    for p in targets():
        txt = p.read_bytes().decode("utf-8")
        if "{{" not in txt:
            continue
        rel = p.relative_to(ROOT)
        unknown = sorted({m for m in PLACEHOLDER.findall(txt) if m.strip() not in vals})
        if unknown:
            print(f"{rel}: unknown placeholder(s) {unknown}", file=sys.stderr)
            bad += 1
            continue
        new = PLACEHOLDER.sub(lambda m: vals[m.group(1).strip()], txt)
        print(f"{rel}: {len(PLACEHOLDER.findall(txt))} placeholder(s)")
        if "{{" in new:
            print(f"{rel}: double brace left after filling", file=sys.stderr)
            bad += 1
        if not args.check:
            p.write_bytes(new.encode("utf-8"))
    for f in HEADLINE_FILES:
        txt = (ROOT / f).read_bytes().decode("utf-8")
        missing = [s for s in headline_numbers(cv, vals) if s not in txt]
        if missing:
            print(f"{f}: headline numbers missing {missing}", file=sys.stderr)
            bad += 1
    print("verify:", "FAILED" if bad else "ok")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
