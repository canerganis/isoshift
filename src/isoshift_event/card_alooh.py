"""Candidate card (GOAL S7): isotope shift of the diaspore -> delta-AlOOH transition pressure.

Inputs: QHA G(T) at fixed pressure for diaspore (mp-625152) and delta-AlOOH (mp-23807), H and D masses,
results/raw/qha_pressure/<model>/<sid>_P<P>.json (isoshift.qha.qha_gibbs with pressure_GPa).
dG_X(P) = G_delta - G_diaspore per atom at 300 K; P_t^X = root by linear interpolation between the pressures
run; dP_iso = P_t^D - P_t^H. Also prints the 0 GPa harmonic estimate -ddF/dV from results/card_alooh.json.

    python -m src.isoshift_event.card_alooh
writes results/card_alooh_pressure.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "raw" / "qha_pressure"
PRESSURES = (10, 15, 20)
T = 300.0


def _g(model, sid, P, iso):
    r = json.loads((RAW / model / f"{sid}_P{P}.json").read_text())
    v = r["variants"][iso]
    i = int(np.argmin(np.abs(np.array(v["T"]) - T)))
    return v["G_eV"][i] / r["n_atoms_cell"] * 1000, bool(v["in_range"][i])  # meV/atom


def main():
    out = {}
    for model in sorted(p.name for p in RAW.iterdir()):
        res = {"dG_meV_atom": {}, "in_range": True}
        for iso in ("H", "D"):
            dg = []
            for P in PRESSURES:
                try:
                    gb, okb = _g(model, "mp-23807", P, iso)
                    ga, oka = _g(model, "mp-625152", P, iso)
                except FileNotFoundError:
                    dg.append(np.nan)
                    continue
                res["in_range"] &= okb and oka
                dg.append(gb - ga)
            res["dG_meV_atom"][iso] = [round(x, 4) for x in dg]
            x, y = np.array(PRESSURES, float), np.array(dg)
            ok = np.isfinite(y)
            root = None
            if ok.sum() >= 2:  # one estimator for H and D (council 05): linear fit over all pressures run
                k, b = np.polyfit(x[ok], y[ok], 1)
                root = float(-b / k)
                res[f"Pt_{iso}_extrapolated"] = not (x[ok].min() <= root <= x[ok].max())
                res[f"n_points_{iso}"] = int(ok.sum())
            res[f"Pt_{iso}_GPa"] = None if root is None else round(root, 3)
        if res.get("Pt_H_GPa") is not None and res.get("Pt_D_GPa") is not None:
            res["dP_iso_GPa"] = round(res["Pt_D_GPa"] - res["Pt_H_GPa"], 3)
        out[model] = res
        print(model, json.dumps(res))
    (ROOT / "results" / "card_alooh_pressure.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
