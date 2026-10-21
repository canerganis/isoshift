"""F01 out-of-sample test: fit ddF_iso per H = k * dX-H + b on all chemical families but one, predict the held-out family.

Family = reduced formula. Reports, per model and pooled over models: held-out sign accuracy for |dX-H| >= 5 mA
and for all pairs, held-out R^2, and the same for a constant-sign baseline. Writes results/F01_cv.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def main():
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    pairs = pd.read_csv(ROOT / "data" / "isoshift" / "pairs.csv").set_index("pair_id")
    c = d[(d.clean == True) & (d.covalent_XH == True)].copy()  # noqa: E712
    c["family"] = c.pair_id.map(pairs.formula)
    c["y"] = c.ddF_total / c.H_per_atom
    c["x"] = c.dXH_mean_A * 1000
    c = c[c.y.abs() > 0.1 / c.H_per_atom.clip(lower=1e-9) * 0 + 0.1]  # resolvable signal only (|ddF| > 0.1 meV/H)
    out = {}
    for model, g in [*c.groupby("model"), ("pooled", c)]:
        pred = np.full(len(g), np.nan)
        for fam in g.family.unique():
            train, test = g.family != fam, g.family == fam
            if train.sum() < 10:
                continue
            k, b = np.polyfit(g.x[train], g.y[train], 1)
            pred[test.values] = k * g.x[test] + b
        ok = ~np.isnan(pred)
        y, x, p = g.y.values[ok], g.x.values[ok], pred[ok]
        big = np.abs(x) >= 5
        base = np.sign(np.median(y))
        out[model] = {
            "n": int(ok.sum()), "families": int(g.family.nunique()),
            "sign_acc_all": round(float((np.sign(p) == np.sign(y)).mean()), 3),
            "sign_acc_dXH_ge_5mA": round(float((np.sign(p[big]) == np.sign(y[big])).mean()), 3), "n_ge_5mA": int(big.sum()),
            "baseline_sign_acc_ge_5mA": round(float((base == np.sign(y[big])).mean()), 3),
            "R2_heldout": round(float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()), 3),
        }
    (ROOT / "results" / "F01_cv.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
