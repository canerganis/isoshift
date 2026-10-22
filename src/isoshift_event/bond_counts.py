"""Recount logs/bond_queries.jsonl and locate cited sources in it.

Usage: python -m src.isoshift_event.bond_counts

Prints the row breakdown quoted in README, the submission packet and
docs/story/agent_extraction_audit.md, then the 1-based log line numbers
for each source in the provenance table (empty means no matching log row).
Read-only: it never writes to the log.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / "logs" / "bond_queries.jsonl"

PRIOR_ART = "prior-art check for 'first' claim (council 11)"
ATLAS = "isotope-induced polymorphism atlas test"
ICE = "measured H2O vs D2O ice phase boundaries"

# (label, case-insensitive substring searched in each raw log line)
SOURCES = [
    ("brucite, Chakoumakos 2013", "am.2013.4202"),
    ("brucite, Chakoumakos (name)", "chakoumakos"),
    ("LiH, Dammak 2012", "0953-8984/24/43/435402"),
    ("alpha-AlH3, Turley and Rinn 1969", "ic50071a005"),
    ("beta-CrOOH 1976", "0022-4596(76"),
    ("alpha-CrOOH 1977", "0022-4596(77"),
    ("F03, Libowitzky", "libowitzky"),
    ("eps-FeOOH, Thompson 2020 DOI", "am-2020-7468"),
    ("eps-FeOOH, Thompson (name)", "thompson"),
    ("goethite, Liu 2013", "saa.2013.06.102"),
    ("goethite, Ruan 2002", "ruan"),
    ("delta-AlOOH, Kagi 2010", "1742-6596/215/1/012052"),
    ("F05 goethite, Yapp 1987", "0016-7037(87)90247"),
    ("F05 brucite, Xu and Zheng 1999", "0016-7037(99)00047"),
    ("F05 manganite, Hariya and Tsutsumi 1981", "0009-2541(81)90070"),
    ("F07 Bridgman 1935", "1.1749561"),
    ("F07 Herrig 2018", "1.5053993"),
    ("ice, Mishima 2000 (PMID 10991276)", "10991276"),
    ("F12 Graham 1980", "0016-7037(80)90143"),
    ("F12 Graham (name)", "graham"),
    ("F12 Chacko (name)", "chacko"),
    ("CARD, Sano-Furukawa 2018", "s41598-018-33598-2"),
    ("CARD, Ikeda 2025", "jacs.4c11982"),
    ("prior art, McKenzie 2014", "10.1063/1.4873352"),
    ("prior art, McKenzie 2015", "10.1063/1.4927391"),
    ("prior art, Bourgeois 2018", "aad259"),
    ("prior art, Du et al. 2026", "mass-differentiable"),
]


def main() -> None:
    lines = LOG.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines]
    sweep = [r for r in rows if "sweep" in r]
    agent = [r for r in rows if "purpose" in r]
    purposes = Counter(r["purpose"] for r in agent)
    atlas_relog = sum(1 for p in purposes.elements() if p.startswith(ATLAS) and p != ATLAS)
    named = purposes[PRIOR_ART] + purposes[ATLAS] + atlas_relog + purposes[ICE]
    print(f"rows {len(rows)}: sweep {len(sweep)} (no ts, no purpose), agent {len(agent)}")
    print(f"agent rows: prior-art {purposes[PRIOR_ART]}, atlas test {purposes[ATLAS]} "
          f"(+{atlas_relog} re-log), ice boundaries {purposes[ICE]}, other {len(agent) - named}")
    print("sweeps:", dict(Counter(r["sweep"] for r in sweep)))
    print("\nsource -> log lines (1-based)")
    for label, needle in SOURCES:
        hits = [i for i, line in enumerate(lines, 1) if needle.lower() in line.lower()]
        print(f"  {label}: {hits if hits else 'no matching log row'}")


if __name__ == "__main__":
    main()
