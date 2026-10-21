"""Gate G4 and F3 (docs/decisions/01-gate.md) on MgH2 alpha (rutile) vs gamma:
G4  ddF_iso at 0/300/600 K with the screen supercell (min length 9.5 A) vs a larger one (14 A); P13 threshold 0.01 meV/atom.
F3  classical limit: T * ddF_iso should approach a constant over 1000..3000 K (Wigner-Kirkwood 1/T, M01).
Appends to results/validation/convergence.csv.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "validation" / "convergence.csv"
VS = ROOT / "data" / "isoshift" / "validation_structures"
PAIR = ("MgH2_mp-23710_P4_2-mnm.cif", "MgH2_mp-23711_Pbcn.cif")
TEMPS = [0.0, 300.0, 600.0, 1000.0, 2000.0, 3000.0]


def run(model):
    from pymatgen.core import Structure
    from pymatgen.io.ase import AseAtomsAdaptor

    from isoshift import phonons as P
    from isoshift.calculators import calculator_info, get_calculator
    from isoshift.relax import relax

    calc = get_calculator(model, "cuda")
    cid = "{name}-{model}".format(**calculator_info(calc))
    relaxed = [relax(AseAtomsAdaptor.get_atoms(Structure.from_file(VS / f).get_primitive_structure()), calc, fmax=1e-3)[0]
               for f in PAIR]
    res = {}
    for label, (ml, cap) in {"sc9.5": (9.5, 160), "sc14": (14.0, 600)}.items():
        dF = []
        for a in relaxed:
            sc = np.array(P.supercell_for_min_length(a, ml, cap))
            ph, meta, _ = P.get_force_constants(a, calc, cid, supercell=sc)
            mesh = P.choose_mesh(a, density=60)
            f = {iso: P.mesh_frequencies(ph, P.make_masses(a, sub, default="light"), mesh, is_gamma_center=False)
                 .helmholtz_free_energy(TEMPS) * 1000 / len(a) for iso, sub in (("H", {}), ("D", {"H": "D"}))}
            dF.append((f["D"] - f["H"], meta["supercell"]))
        res[label] = (dF[1][0] - dF[0][0], [dF[0][1], dF[1][1]])
    rows = []
    for i, t in enumerate(TEMPS):
        a, b = res["sc9.5"][0][i], res["sc14"][0][i]
        rows.append({"model": model, "T_K": t, "ddF_sc9.5": a, "ddF_sc14": b, "diff": b - a, "T_x_ddF": t * b,
                     "supercells": f"{res['sc9.5'][1]} -> {res['sc14'][1]}"})
    return rows


def main():
    rows = [r for m in sys.argv[1].split(",") for r in run(m)]
    new = not OUT.exists()
    with open(OUT, "a", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        if new:
            w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['model']:9s} T={r['T_K']:6.0f} ddF9.5={r['ddF_sc9.5']:+.4f} ddF14={r['ddF_sc14']:+.4f} diff={r['diff']:+.4f} TxddF={r['T_x_ddF']:+.1f}  {r['supercells']}")


if __name__ == "__main__":
    main()
