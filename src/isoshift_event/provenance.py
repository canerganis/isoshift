"""Experimental origin of every screened structure (is a polymorph pair testable in the lab?).

MP: `theoretical` False means the entry matches an ICSD (experimental) structure.
JARVIS: a non-empty `icsd` field. Writes data/isoshift/experimental.csv (struct_id, experimental, evidence).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "isoshift"


def main():
    mp = {r["mp_id"]: r for r in json.loads((DATA / "mp_h.json").read_text())}
    jv = pd.read_pickle(DATA / "dft_3d.pkl").set_index("jid")
    rows = []
    for s in csv.DictReader(open(DATA / "structures.csv", newline="")):
        sid = s["struct_id"]
        if sid in mp:
            exp = mp[sid]["theoretical"] is False
            ev = "MP theoretical=False" if exp else "MP theoretical=True"
        elif sid in jv.index:
            icsd = str(jv.loc[sid, "icsd"] or "").strip()
            exp = bool(icsd)
            ev = f"JARVIS icsd={icsd}" if exp else "JARVIS no icsd"
        else:
            exp, ev = False, "unknown"
        rows.append({"struct_id": sid, "experimental": exp, "evidence": ev})
    with open(DATA / "experimental.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, ["struct_id", "experimental", "evidence"])
        w.writeheader()
        w.writerows(rows)
    p = pd.read_csv(DATA / "pairs.csv")
    e = {r["struct_id"]: r["experimental"] for r in rows}
    both = p.apply(lambda r: e.get(r.struct_a, False) and e.get(r.struct_b, False), axis=1)
    print(f"{sum(r['experimental'] for r in rows)}/{len(rows)} structures experimental; "
          f"{int(both.sum())}/{len(p)} pairs with both members experimental ({int(both[p.tier == 16].sum())} tier16)")


if __name__ == "__main__":
    main()
