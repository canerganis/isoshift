"""Gate tier A (PLAN.md P1): implementation sanity of the H/D machinery on real force constants.

    python -m src.isoshift_event.sanity mace,orb          # .venv
    .venv-sevenn/Scripts/python.exe -m src.isoshift_event.sanity sevenn,mattersim

Appends rows to results/validation/tier_a.csv. Checks per model:
  equal_mass   ddF with D mass set to the H mass is exactly zero
  swap_sign    swapping the H and D roles flips ddF
  classical    ddF(2000 K) is small relative to ddF(0 K) (Wigner-Kirkwood 1/T decay, M01)
  LiH Gamma TO frequency for H and D vs experiment 17.7 / 13.4 THz (validation.csv)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "validation" / "tier_a.csv"
PRIM = ROOT / "data" / "isoshift" / "validation_structures" / "prim"
PAIR = ("MgH2_mp-23710_P4_2-mnm.cif", "MgH2_mp-23711_Pbcn.cif")  # rutile vs gamma MgH2
TO_EXP_THZ = {"H": 17.7, "D": 13.4}


def _fc(atoms, calc, cid):
    from isoshift import phonons as P
    from isoshift.relax import relax

    a, _ = relax(atoms, calc, fmax=1e-3)
    ph, _, _ = P.get_force_constants(a, calc, cid, min_length=9.5, max_atoms=160)
    return a, ph


def _free(a, ph, sub, temps):
    from isoshift import phonons as P

    mf = P.mesh_frequencies(ph, P.make_masses(a, sub, default="light"), P.choose_mesh(a))
    return np.asarray(mf.helmholtz_free_energy(list(temps))) * 1000 / len(a)  # meV/atom


def check(model):
    from ase.io import read
    from pymatgen.core import Structure
    from pymatgen.io.ase import AseAtomsAdaptor

    from isoshift import phonons as P
    from isoshift.calculators import calculator_info, get_calculator

    calc = get_calculator(model, "cuda")
    cid = "{name}-{model}".format(**calculator_info(calc))
    temps = (0.0, 300.0, 2000.0)
    vs = ROOT / "data" / "isoshift" / "validation_structures"
    sa, sb = (AseAtomsAdaptor.get_atoms(Structure.from_file(vs / f).get_primitive_structure()) for f in PAIR)
    (a, pa), (b, pb) = _fc(sa, calc, cid), _fc(sb, calc, cid)
    heavy_as_light = {"H": "H"}
    dd = lambda x, y: (_free(b, pb, y, temps) - _free(b, pb, x, temps)) - (_free(a, pa, y, temps) - _free(a, pa, x, temps))
    H, D = {}, {"H": "D"}
    ddf = dd(H, D)
    rows = [
        {"model": model, "check": "equal_mass", "value": float(np.abs(dd(H, heavy_as_light)).max()), "pass": bool(np.abs(dd(H, heavy_as_light)).max() == 0.0)},
        {"model": model, "check": "swap_sign", "value": float(np.abs(ddf + dd(D, H)).max()), "pass": bool(np.allclose(ddf, -dd(D, H), atol=1e-12))},
        {"model": model, "check": "classical_decay", "value": float(abs(ddf[2]) / max(abs(ddf[0]), 1e-12)), "pass": bool(abs(ddf[2]) < 0.5 * abs(ddf[0]))},
        {"model": model, "check": "MgH2_ddF_0K_meV_atom", "value": float(ddf[0]), "pass": ""},
    ]
    li, pl = _fc(AseAtomsAdaptor.get_atoms(Structure.from_file(vs / "LiH_mp-23703_Fm-3m.cif").get_primitive_structure()), calc, cid)
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        p = P.phonopy_with_masses(pl, P.make_masses(li, sub, default="light"))
        p.run_qpoints([[0, 0, 0]])
        to = float(np.max(p.qpoints.frequencies[0]))  # no NAC: the Gamma optical modes are TO-like
        rows.append({"model": model, "check": f"LiH_TO_{iso}_THz", "value": to,
                     "pass": bool(abs(to / TO_EXP_THZ[iso] - 1) < 0.15)})
    return rows


def main():
    rows = [r for m in sys.argv[1].split(",") for r in check(m)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    new = not OUT.exists()
    with open(OUT, "a", newline="") as fh:
        w = csv.DictWriter(fh, ["model", "check", "value", "pass"])
        if new:
            w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['model']:10s} {r['check']:24s} {r['value']:+.6g} {r['pass']}")


if __name__ == "__main__":
    main()
