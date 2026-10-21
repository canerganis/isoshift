"""F01 refit against the mean donor O...O distance (the X-ray-accessible predictor).

Per structure and model, the mean donor O...O distance is the mean of d_OO over the O-H donors of the primitive cell
in results/stretch_check.csv (donor-acceptor distance as built by stretch_check._donors: acceptor = nearest other O of
the H, H...O < 2.6 A; donors without such an acceptor are dropped). The pair predictor is
dOO = OO(b) - OO(a), same orientation as dX-H. Since a shorter O...O goes with a longer O-H, the F01 rule reads
"deuteration favours the polymorph with the LONGER mean O...O", i.e. sign(ddF) = -sign(dOO).

Also translates the 0.99 A model O-H threshold into an O...O threshold and compares the O...O-defined regime with the
O-H-defined regime on the same rows.

    python -m src.isoshift_event.rule_oo
writes results/F01_oo.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import rule_cv

ROOT = Path(__file__).resolve().parents[2]
MIN_DOO = 0.03  # A, eligibility cut (about 4 mA of O-H at the fitted dOH/dOO of -0.13)
OO_THRESHOLDS = [2.60, 2.65, 2.70, 2.75, 2.80, 2.85, 2.90]


def structure_table(cap: float | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """cap: optional upper limit on donor d_OO (A) to drop contacts that are not hydrogen bonds (sensitivity only)."""
    s = pd.read_csv(ROOT / "results" / "stretch_check.csv")
    s = s[s.source != "dft_pbesol"]
    don = s[np.isfinite(s.d_OO_A)]
    if cap is not None:
        don = don[don.d_OO_A <= cap]
    st = don.groupby(["source", "struct_id"]).agg(OO=("d_OO_A", "mean"), OH=("d_OH_A", "mean"), n_donors=("d_OO_A", "size")).reset_index()
    return don, st


def load(cap: float | None = None) -> pd.DataFrame:
    c = rule_cv.load()
    _, st = structure_table(cap)
    oo = st.set_index(["source", "struct_id"]).OO
    # orientation: decompose.py forms b - a with struct_a/struct_b of results/screen_pairs_refined.csv per model
    # (not the order in pair_id), so take a and b from there.
    sp = pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv").set_index(["pair_id", "model"])
    a = [oo.get((m, sp.loc[(p, m)].struct_a), np.nan) for m, p in zip(c.model, c.pair_id)]
    b = [oo.get((m, sp.loc[(p, m)].struct_b), np.nan) for m, p in zip(c.model, c.pair_id)]
    c["OO_a"], c["OO_b"] = a, b
    c["dOO"] = c.OO_b - c.OO_a
    c["ooMin"] = np.fmin(c.OO_a, c.OO_b)
    c = c[np.isfinite(c.dOO)].copy()
    c["right_oo"] = (-np.sign(c.dOO)) == np.sign(c.y)
    return c.reset_index(drop=True)


def fit(g: pd.DataFrame, xcol: str) -> dict:
    k, b = np.polyfit(g[xcol], g.y, 1)
    return {"n": int(len(g)), "slope_meV_per_H": round(float(k), 3), "intercept": round(float(b), 3),
            "r": round(float(np.corrcoef(g[xcol], g.y)[0, 1]), 3)}


def sign_block(g: pd.DataFrame, col: str, mask: pd.Series) -> dict:
    q = g[mask]
    return {"right": int(q[col].sum()), "n": int(len(q)), "acc": round(float(q[col].mean()), 3) if len(q) else None,
            "n_pairs": int(q.pair_id.nunique())}


def translate_threshold(don: pd.DataFrame, st: pd.DataFrame, t_oh: float = 0.99) -> dict:
    out = {}
    for m in ["mace", "orb", "mattersim"]:
        d = don[(don.source == m) & (don.d_OO_A < 3.2)]
        s = st[(st.source == m)]
        k, b = np.polyfit(d.d_OO_A, d.d_OH_A, 1)
        ks, bs = np.polyfit(s.OO, s.OH, 1)
        near = s[(s.OH > t_oh - 0.012) & (s.OH < t_oh + 0.012)]
        ko, bo = np.polyfit(s.OH, s.OO, 1)  # inverse regression (OO on OH), evaluated at the threshold
        out[m] = {
            "donor_fit_dOH_vs_dOO": {"n": int(len(d)), "slope_A_per_A": round(float(k), 4), "OO_at_threshold": round(float((t_oh - b) / k), 3)},
            "structure_fit_meanOH_vs_meanOO": {"n": int(len(s)), "slope": round(float(ks), 4), "OO_at_threshold": round(float((t_oh - bs) / ks), 3),
                                                "r": round(float(np.corrcoef(s.OO, s.OH)[0, 1]), 3)},
            "structure_inverse_fit_OO_on_OH": {"OO_at_threshold": round(float(ko * t_oh + bo), 3)},
            "median_OO_of_structures_with_meanOH_within_12mA": {"n": int(len(near)), "median_OO": round(float(near.OO.median()), 3) if len(near) else None},
        }
    return out


def analyse(cap: float | None = None, full: bool = True) -> dict:
    don, st = structure_table(cap)
    c = load(cap)
    n_all_rows = len(rule_cv.load())
    out = {"donor_cap_A": cap, "definition": "dOO = mean donor O...O of polymorph b minus a (A); rule: sign(ddF) = -sign(dOO)",
           "coverage": {"rows_with_OO": int(len(c)), "of_rows": n_all_rows, "unique_pairs": int(c.pair_id.nunique()), "formulas": int(c.family.nunique()),
                        "rows_per_model": {m: int(n) for m, n in c.model.value_counts().items()}},
           "min_abs_dOO_A": MIN_DOO}
    big = c.dOO.abs() >= MIN_DOO
    sig = big & (c.y.abs() > rule_cv.MIN_SIGNAL)
    elig = {"all_eligible": big, "signal_filtered": sig}
    # global fits
    out["fit_all_rows"] = {m: fit(g, "dOO") for m, g in [*c.groupby("model"), ("pooled", c)]}
    out["fit_all_rows_dXH_same_rows"] = {m: fit(g, "x") for m, g in [*c.groupby("model"), ("pooled", c)]}
    # threshold translation
    out["threshold_translation_0.99"] = translate_threshold(don, st)
    allv = [v["donor_fit_dOH_vs_dOO"]["OO_at_threshold"] for v in out["threshold_translation_0.99"].values()]
    allv += [v["structure_fit_meanOH_vs_meanOO"]["OO_at_threshold"] for v in out["threshold_translation_0.99"].values()]
    t_oo = float(np.median(allv))
    out["threshold_translation_summary"] = {"range_OO_A": [round(min(allv), 3), round(max(allv), 3)], "median_OO_A": round(t_oo, 3)}
    # sign accuracy: O...O rule vs O-H rule on the same rows, all regimes and O...O-defined strong regime scan
    c["right_xh"] = c.right
    out["sign_accuracy"] = {}
    for name, e in elig.items():
        blk = {"all_regimes": {"OO_rule": sign_block(c, "right_oo", e), "XH_rule_same_rows_eligibility_of_OO": sign_block(c, "right_xh", e)},
               "OO_regime_scan": {}}
        for t in OO_THRESHOLDS:
            s, w = c.ooMin <= t, c.ooMin > t
            blk["OO_regime_scan"][f"{t:.2f}"] = {"strong_OO<=t": sign_block(c, "right_oo", e & s), "weak_OO>t": sign_block(c, "right_oo", e & w),
                                                  "strong_per_model": {m: sign_block(q, "right_oo", e[q.index] & (q.ooMin <= t)) for m, q in c.groupby("model")}}
        # regime defined by the translated threshold, and agreement with the O-H-defined regime
        s_oh = c.rmax >= 0.99
        s_oo = c.ooMin <= t_oo
        blk["translated_threshold_OO"] = round(t_oo, 3)
        blk["translated_strong"] = sign_block(c, "right_oo", e & s_oo)
        blk["translated_weak"] = sign_block(c, "right_oo", e & ~s_oo)
        blk["OH_strong_0.99_with_OO_rule"] = sign_block(c, "right_oo", e & s_oh)
        blk["OH_weak_0.99_with_OO_rule"] = sign_block(c, "right_oo", e & ~s_oh)
        blk["regime_agreement_rows"] = {"both_strong": int((s_oh & s_oo & e).sum()), "both_weak": int((~s_oh & ~s_oo & e).sum()),
                                        "OH_strong_OO_weak": int((s_oh & ~s_oo & e).sum()), "OH_weak_OO_strong": int((~s_oh & s_oo & e).sum())}
        out["sign_accuracy"][name] = blk
    # slopes in the strong regime (OO-defined and O-H-defined), per model
    out["fit_strong_translated"] = {m: fit(g, "dOO") for m, g in [*c[c.ooMin <= t_oo].groupby("model"), ("pooled", c[c.ooMin <= t_oo])]}
    out["fit_weak_translated"] = {m: fit(g, "dOO") for m, g in [*c[c.ooMin > t_oo].groupby("model"), ("pooled", c[c.ooMin > t_oo])] if len(g) > 4}
    # formula-clustered CV (leave one formula out), baseline from training folds
    cv = {}
    for label, sel in [("all_regimes", c.y.abs() >= 0), ("strong_translated_OO", c.ooMin <= t_oo), ("strong_OH_0.99", c.rmax >= 0.99)]:
        cv[label] = {}
        for name, fitset in [("all_eligible", sel), ("signal_filtered", sel & (c.y.abs() > rule_cv.MIN_SIGNAL))]:
            g = c[fitset].assign(x=c.dOO)  # lofo works on column x: use dOO (A) here
            cv[label][name] = {**{m: rule_cv.lofo(q, min_x=MIN_DOO, orient=-1.0) for m, q in g.groupby("model")},
                               "pooled": rule_cv.lofo(g, min_x=MIN_DOO, orient=-1.0)}
    out["formula_cv_OO"] = cv
    return out


def main():
    out = analyse(None)
    out["sensitivity_donor_cap"] = {}
    for cap in (3.2, 3.0):
        o = analyse(cap)
        out["sensitivity_donor_cap"][f"{cap:.1f}"] = {k: o[k] for k in ["coverage", "fit_all_rows", "threshold_translation_summary", "sign_accuracy", "formula_cv_OO"]}
        print("cap", cap, o["coverage"], o["fit_all_rows"]["pooled"], o["sign_accuracy"]["signal_filtered"]["all_regimes"],
              o["sign_accuracy"]["signal_filtered"]["translated_strong"], o["sign_accuracy"]["signal_filtered"]["translated_weak"], o["threshold_translation_summary"],
              o["formula_cv_OO"]["all_regimes"]["signal_filtered"]["pooled"])
    cv = out["formula_cv_OO"]
    (ROOT / "results" / "F01_oo.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ["coverage", "fit_all_rows", "fit_all_rows_dXH_same_rows", "threshold_translation_summary", "fit_strong_translated"]}, indent=1))
    for n in ("all_eligible", "signal_filtered"):
        b = out["sign_accuracy"][n]
        print(n, "all", b["all_regimes"], "translated", b["translated_threshold_OO"], b["translated_strong"], b["translated_weak"], b["regime_agreement_rows"])
        for t, v in b["OO_regime_scan"].items():
            print("  ", t, v["strong_OO<=t"], v["weak_OO>t"])
    for lab, v in cv.items():
        for n, q in v.items():
            print(lab, n, q["pooled"])
    print(json.dumps(out["threshold_translation_0.99"], indent=1))


if __name__ == "__main__":
    main()
