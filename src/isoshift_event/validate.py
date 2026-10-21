"""Gate validation runs (PLAN.md P1 tier B): QHA H/D for structures with measured isotope volume effects.

    python -m src.isoshift_event.validate submit      # write primitive CIFs, queue QHA jobs for 4 models
    python -m src.isoshift_event.validate run         # serve the queue one model at a time (blocking)
    python -m src.isoshift_event.validate collect     # results/validation/volume_isotope.csv

Uses the pre-event pool (isoshift.pool) and QHA (isoshift.qha) unchanged.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "results" / "queue" / "validation"
RAW = ROOT / "results" / "raw" / "validation"
OUT = ROOT / "results" / "validation"
PRIM = ROOT / "data" / "isoshift" / "validation_structures" / "prim"
MODELS = ("mace", "orb", "mattersim", "sevenn")
# name -> (MP CIF in validation_structures, measured V_H/V_D - 1 in %, T of measurement K, source)
CASES = {
    "brucite": ("MgOH2_mp-30247_P-3m1.cif", 0.31, 295, "10.2138/am.2013.4202"),
    "portlandite": ("CaOH2_mp-23879_P-3m1.cif", None, 295, "no same-condition pair (cross-lab estimate +0.67%)"),
    "LiH": ("LiH_mp-23703_Fm-3m.cif", 0.81, 300, "via 10.1088/0953-8984/24/43/435402"),
    "iceXI": ("H2O_mp-697111_Cmc2_1.cif", -0.15, 100, "10.1103/PhysRevLett.108.193003 (ice Ih, -0.09 to -0.21%)"),
}
QHA_KW = {"n_vol": 9, "vol_range": [-0.04, 0.12], "min_length": 9.5, "max_atoms": 160,
          "temps": list(range(0, 401, 10))}


def submit():
    from pymatgen.core import Structure

    from isoshift import pool

    PRIM.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, (cif, *_rest) in CASES.items():
        prim = PRIM / f"{name}.cif"
        if not prim.exists():
            Structure.from_file(ROOT / "data" / "isoshift" / "validation_structures" / cif).get_primitive_structure().to(filename=str(prim))
        for m in MODELS:
            jid = pool.submit(QUEUE, "qha", str(prim), m, str(RAW / m / f"{name}.json"), **QHA_KW)
            n += jid is not None
    print(f"queued {n} jobs in {QUEUE}")


def run(idle_exit_s: float = 20.0):
    from isoshift import pool

    for m in MODELS:
        cmd = pool.launch_cmd(m, QUEUE, idle_exit_s=idle_exit_s, mem_fraction=0.5)
        print("serve", m, flush=True)
        subprocess.run(cmd, cwd=ROOT, check=False)


def _vmin(res, variant, T):
    v = res["variants"][variant]
    i = v["T"].index(float(T)) if float(T) in v["T"] else min(range(len(v["T"])), key=lambda k: abs(v["T"][k] - T))
    return v["V_A3"][i], bool(v["in_range"][i])


def collect():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (_cif, exp, T, src) in CASES.items():
        for m in MODELS:
            f = RAW / m / f"{name}.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            for t in (0, T):
                vh, okh = _vmin(r, "H", t)
                vd, okd = _vmin(r, "D", t)
                rows.append({"case": name, "model": m, "T_K": t, "V_H_A3": vh, "V_D_A3": vd,
                             "VIE_pct": (vh / vd - 1) * 100, "in_range": okh and okd,
                             "exp_VIE_pct": exp if t == T else "", "source": src if t == T else ""})
    with open(OUT / "volume_isotope.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['case']:12s} {r['model']:10s} T={r['T_K']:4d} VIE={r['VIE_pct']:+.3f}%  exp={r['exp_VIE_pct']}  in_range={r['in_range']}")


if __name__ == "__main__":
    {"submit": submit, "run": run, "collect": collect}[sys.argv[1]]()
