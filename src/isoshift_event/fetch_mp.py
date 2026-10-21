"""Pull Materials Project hydrogen compounds (no carbon, E_hull <= 50 meV/atom).

Writes data/isoshift/mp_h.json (structures, local only) and data/isoshift/mp_h.csv (published summary).
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "isoshift"
FIELDS = ["material_id", "formula_pretty", "symmetry", "nsites", "energy_above_hull",
          "formation_energy_per_atom", "energy_per_atom", "volume", "theoretical", "structure"]


def _api_key() -> str:
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("MP_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    return os.environ["MP_API_KEY"]


def main():
    from mp_api.client import MPRester

    with MPRester(_api_key()) as m:
        docs = m.materials.summary.search(elements=["H"], exclude_elements=["C"],
                                          energy_above_hull=(0, 0.05), fields=FIELDS)
    rows = []
    for d in docs:
        rows.append({
            "mp_id": str(d.material_id), "formula": d.formula_pretty,
            "spg": d.symmetry.number, "spg_symbol": d.symmetry.symbol, "nsites": d.nsites,
            "e_hull_eV": d.energy_above_hull, "e_form_eV": d.formation_energy_per_atom,
            "e_per_atom_eV": d.energy_per_atom, "volume": d.volume, "theoretical": d.theoretical,
            "structure": d.structure.as_dict(),
        })
    rows.sort(key=lambda r: (r["formula"], r["e_hull_eV"]))
    (OUT / "mp_h.json").write_text(json.dumps(rows))
    keys = [k for k in rows[0] if k != "structure"]
    with open(OUT / "mp_h.csv", "w", newline="") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows({k: r[k] for k in keys} for r in rows)
    print(f"mp_h: {len(rows)} entries, {len({r['formula'] for r in rows})} formulas")


if __name__ == "__main__":
    main()
