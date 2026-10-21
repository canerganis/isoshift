"""F01 as a structure-only predictor: X-H bond lengths from the database (DFT) structures, no phonons.

Predicts ddF_iso per H for every covalent X-H polymorph pair in data/isoshift/pairs.csv with the pooled F01 line,
and checks it against the ensemble-computed ddF_iso where available. Writes results/rule_map.csv.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.core import Structure

ROOT = Path(__file__).resolve().parents[2]


def mean_xh(cif):
    s = Structure.from_file(str(ROOT / cif))
    d = []
    for i, site in enumerate(s):
        if site.specie.symbol != "H":
            continue
        nb = [n for n in s.get_neighbors(site, 1.6) if n.specie.symbol != "H"]
        if nb:
            d.append(min(n.nn_distance for n in nb))
    return (float(np.mean(d)), float(max(d)), sum(1 for x in s if x.specie.symbol == "H") / len(s)) if d else (np.nan, np.nan, np.nan)


def main():
    st = pd.read_csv(ROOT / "data" / "isoshift" / "structures.csv").set_index("struct_id")
    geo = {sid: mean_xh(r.cif) for sid, r in st.iterrows()}
    p = pd.read_csv(ROOT / "data" / "isoshift" / "pairs.csv")
    p["xh_a"], p["xh_b"] = p.struct_a.map(lambda s: geo[s][0]), p.struct_b.map(lambda s: geo[s][0])
    p["covalent"] = p.struct_a.map(lambda s: geo[s][1] < 1.3) & p.struct_b.map(lambda s: geo[s][1] < 1.3)
    p["dXH_mA_db"] = (p.xh_b - p.xh_a) * 1000
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    c = d[(d.clean == True) & (d.covalent_XH == True)]  # noqa: E712
    k, b = np.polyfit(c.dXH_mean_A * 1000, c.ddF_total / c.H_per_atom, 1)
    p["ddF_H_rule"] = k * p.dXH_mm if False else k * p.dXH_mA_db + b
    ens = c.assign(y=c.ddF_total / c.H_per_atom).groupby("pair_id").y.median()
    p["ddF_H_ensemble"] = p.pair_id.map(ens)
    p = p[p.covalent]
    m = p.dropna(subset=["ddF_H_ensemble"])
    big = m[m.dXH_mA_db.abs() >= 5]
    out = {"line": {"slope_meV_H_per_mA": round(k, 4), "intercept_meV_H": round(b, 3)},
           "covalent_pairs_predicted": int(len(p)), "with_ensemble": int(len(m)),
           "r_rule_vs_ensemble": round(float(np.corrcoef(m.ddF_H_rule, m.ddF_H_ensemble)[0, 1]), 3),
           "sign_acc_dXH_ge_5mA": round(float((np.sign(big.ddF_H_rule) == np.sign(big.ddF_H_ensemble)).mean()), 3), "n_ge_5mA": int(len(big))}
    p.to_csv(ROOT / "results" / "rule_map.csv", index=False)
    (ROOT / "results" / "rule_map_summary.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
