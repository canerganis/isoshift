"""Blind predictions of the volume isotope effect V_H/V_D - 1 for experimentally known H compounds.

Protocol (decision 04): predictions are computed and committed BEFORE the measured values gathered by
the literature agents (data/isoshift/validation.csv rows added after the commit) are read. The git
commit time of docs/predictions/P01_volume_isotope_blind.csv is the timestamp of the prediction.

Same method as the gate validation (validate.py collect, G2): Gamma-free QHA from cached force
constants, four imaginary-mode treatments. Inputs: results/raw/qha_top/<model>/<struct_id>.json.

    python -m src.isoshift_event.predict
"""
from __future__ import annotations

import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "raw" / "qha_top"
OUT = ROOT / "docs" / "predictions"
TEMPS_REPORT = (0, 100, 300)


def _job(args):
    sid, model = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    from . import validate

    validate.PRIM = ROOT / "data" / "isoshift" / "structs"
    r = json.loads((RAW / model / f"{sid}.json").read_text())
    try:
        temps, vols, v, diag = validate._vie_case(sid, r)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:  # recorded, never silently dropped
        print(f"skip {sid} {model}: {exc}", flush=True)
        return []
    rows = []
    for T in TEMPS_REPORT:
        it = int(np.argmin(np.abs(temps - T)))
        vals, ok = [], True
        for t in validate.TREATMENTS:
            vh, vd = v[("H", t)][it], v[("D", t)][it]
            ok &= bool(vols.min() - 1e-9 <= min(vh, vd) and max(vh, vd) <= vols.max() + 1e-9)
            vals.append((vh / vd - 1) * 100)
        rows.append({"struct_id": sid, "model": model, "T_K": int(temps[it]),
                     "VIE_pct_median": round(float(np.median(vals)), 4),
                     "VIE_pct_min": round(min(vals), 4), "VIE_pct_max": round(max(vals), 4),
                     "in_range": ok, "imag_frac_max_pct": round(max(diag["imag_frac"]) * 100, 3)})
    return rows


def main():
    jobs = [(f.stem, d.name) for d in sorted(RAW.iterdir()) for f in sorted(d.glob("*.json"))]
    with ProcessPoolExecutor(min(len(jobs), 8)) as ex:
        rows = [r for rs in ex.map(_job, jobs) for r in rs]
    meta = {r["struct_id"]: r for r in csv.DictReader(open(ROOT / "data" / "isoshift" / "structures.csv"))}
    for r in rows:
        r["formula"], r["spg"] = meta[r["struct_id"]]["formula"], meta[r["struct_id"]]["spg"]
    OUT.mkdir(parents=True, exist_ok=True)
    fields = ["struct_id", "formula", "spg", "model", "T_K", "VIE_pct_median", "VIE_pct_min", "VIE_pct_max",
              "in_range", "imag_frac_max_pct"]
    with open(OUT / "P01_volume_isotope_blind.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["formula"], r["struct_id"], r["model"], r["T_K"])))
    for r in rows:
        if r["T_K"] == 300:
            print(f"{r['formula']:10s} {r['struct_id']:13s} spg {r['spg']:>3s} {r['model']:5s} "
                  f"VIE(300K) {r['VIE_pct_median']:+.3f}% [{r['VIE_pct_min']:+.3f}, {r['VIE_pct_max']:+.3f}] in_range={r['in_range']}")


if __name__ == "__main__":
    main()
