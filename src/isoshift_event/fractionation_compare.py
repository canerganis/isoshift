"""P04 comparison: blind harmonic 1000 ln beta vs measured mineral-water D/H factors.
Rule: docs/predictions/P04_comparison_rule.md (written before this was run). Output: results/P04_comparison.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODELS = ["mace", "orb", "mattersim"]
TC = [25, 100, 200, 300, 400]
MIN = {"brucite": "mp-30247", "goethite": "mp-605437", "manganite": "mp-29159"}


def lnb(df, sid, model, T):
    r = df[(df.struct_id == sid) & (df.model == model)].iloc[0]
    y = np.array([r[f"1000lnbeta_{c}C"] for c in TC], float)
    x = 1.0 / (np.array(TC) + 273.15) ** 2
    return float(np.interp(1.0 / (T + 273.15) ** 2, x[::-1], y[::-1]))


def meas(mineral, T):
    K = T + 273.15
    if mineral == "goethite":
        return 1000 * np.log(0.905), 4.4
    if mineral == "brucite":
        return -4.88e6 / K**2 - 22.5, None
    if mineral == "manganite":
        a = {150: 0.7894, 200: 0.7958, 250: 0.8078}[T]
        return 1000 * np.log(a), None


def pred(df, A, B, T):
    d = {m: lnb(df, MIN[A], m, T) - lnb(df, MIN[B], m, T) for m in MODELS}
    v = np.array(list(d.values()))
    return float(np.median(v)), float(v.min()), float(v.max()), d


def main():
    df = pd.read_csv(ROOT / "docs/predictions/P04_fractionation_blind.csv")
    rows = []
    def add(A, B, T, mA, mB, tag):
        p, lo, hi, d = pred(df, A, B, T)
        rows.append(dict(pair=f"{A}-{B}", T_C=T, meas=mA - mB, pred=p, pred_min=lo, pred_max=hi, **{f"pred_{k}": v for k, v in d.items()}, tag=tag))
    for T in (25, 50, 75, 100, 120):
        add("brucite", "goethite", T, meas("brucite", T)[0], meas("goethite", T)[0], "scored")
    brucite250 = 1000 * np.log(1 - 32 / 1000)
    add("brucite", "manganite", 250, brucite250, meas("manganite", 250)[0], "scored_weak")
    add("goethite", "manganite", 150, meas("goethite", 150)[0], meas("manganite", 150)[0], "sensitivity_extrapolated")
    # Sultan 70 C outlier sensitivity for brucite-goethite
    add("brucite", "goethite", 70, meas("brucite", 70)[0], -115.78, "sensitivity_sultan")
    out = pd.DataFrame(rows)
    # absolute 1000 ln beta (ensemble median) at each mineral and T
    ab = {m: {str(T): [lnb(df, MIN[m], k, T) for k in MODELS] for T in (25, 100, 150, 250)} for m in MIN}
    def stats(sub):
        x, y = sub.meas.values, sub.pred.values
        o = np.polyfit(x, y, 1)
        return dict(n=len(sub), slope=float(o[0]), intercept=float(o[1]), r=float(np.corrcoef(x, y)[0, 1]) if len(sub) > 2 else None, ratio_origin=float((x @ y) / (x @ x)))
    sc = out[out.tag.isin(["scored", "scored_weak"])]
    allp = out[out.tag.isin(["scored", "scored_weak", "sensitivity_extrapolated"])]
    res = dict(table=out.to_dict("records"), stats_scored=stats(sc), stats_with_goethite_manganite150=stats(allp), abs_lnbeta=ab,
               sign=out.assign(ok=np.sign(out.meas) == np.sign(out.pred))[["pair", "T_C", "tag", "ok"]].to_dict("records"))
    (ROOT / "results" / "P04_comparison.json").write_text(json.dumps(res, indent=1))
    pd.set_option("display.width", 250)
    print(out.round(1).to_string())
    print(res["stats_scored"]); print(res["stats_with_goethite_manganite150"])
    for m in ab: print(m, {k: np.round(v, 0).tolist() for k, v in ab[m].items()})

if __name__ == "__main__":
    main()
