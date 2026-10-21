"""F01 sign-rule statistics: regime scan, O-H split, unique-pair majority, formula-clustered CV.

Rows are clean covalent X-H pair-model evaluations from results/decompose_pairs.csv (341 rows, 197 unique pairs).
x = change of the mean X-H length between the two polymorphs (mA), y = ddF_iso per H (meV/H).
"Family" = reduced formula (leave-one-formula-out CV).

Two eligibility variants are reported everywhere:
  all_eligible     |dX-H| >= 5 mA
  signal_filtered  |dX-H| >= 5 mA and |ddF_iso| > 0.1 meV/H (the same cut as the original rule_cv and decision 04)

Regime variable: rmax = larger of the two structures' mean model X-H length (decompose_structures.csv, same model).
"Strong" side: rmax >= threshold, "weak" side: rmax < threshold. The 0.99 A cut was chosen after looking at the data.
The constant-sign baseline always uses the majority sign of y in the TRAINING fold only.

    python -m src.isoshift_event.rule_cv
writes results/F01_cv.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
THRESHOLDS = [round(0.97 + 0.01 * i, 2) for i in range(7)]
MAIN_THR = 0.99
MIN_DXH = 5.0  # mA
MIN_SIGNAL = 0.1  # meV/H
# Decision 01 G1 / ledger freeze rule: quantitative F01 numbers use these three models; SevenNet enters as sign votes
# on a separately labelled line (sevenn_sign_votes block), never in slopes or the headline counts.
QUANT_MODELS = ("mace", "orb", "mattersim")
SIGN_ONLY_MODELS = ("sevenn",)


def load(models: tuple[str, ...] | None = QUANT_MODELS) -> pd.DataFrame:
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    s = pd.read_csv(ROOT / "results" / "decompose_structures.csv")
    pairs = pd.read_csv(ROOT / "data" / "isoshift" / "pairs.csv").set_index("pair_id")
    c = d[(d.clean == True) & (d.covalent_XH == True)].copy()  # noqa: E712
    c["family"] = c.pair_id.map(pairs.formula)
    c["y"] = c.ddF_total / c.H_per_atom
    c["x"] = c.dXH_mean_A * 1000
    xh = s.set_index(["model", "struct_id"]).XH_mean_A
    c["rmax"] = [max(xh[(m, p.split("__")[0])], xh[(m, p.split("__")[1])]) for m, p in zip(c.model, c.pair_id)]
    oh_structs = set(pd.read_csv(ROOT / "results" / "stretch_check.csv").struct_id)
    c["OH"] = [any(q in oh_structs for q in p.split("__")) for p in c.pair_id]
    c["right"] = np.sign(c.x) == np.sign(c.y)
    if models is not None:
        c = c[c.model.isin(models)]
    return c.reset_index(drop=True)


def variants(c: pd.DataFrame) -> dict[str, pd.Series]:
    big = c.x.abs() >= MIN_DXH
    return {"all_eligible": big, "signal_filtered": big & (c.y.abs() > MIN_SIGNAL)}


def _acc(g: pd.DataFrame) -> dict:
    return {"right": int(g.right.sum()), "n": int(len(g)), "acc": round(float(g.right.mean()), 3) if len(g) else None,
            "n_pairs": int(g.pair_id.nunique())}


def _majority(g: pd.DataFrame) -> dict:
    if not len(g):
        return {"n_pairs": 0, "right": 0, "tie": 0, "wrong": 0}
    m = g.groupby("pair_id").right.mean()
    return {"n_pairs": int(len(m)), "right": int((m > 0.5).sum()), "tie": int((m == 0.5).sum()), "wrong": int((m < 0.5).sum())}


def _side(c: pd.DataFrame, mask_side: pd.Series, elig: pd.Series) -> dict:
    g = c[mask_side & elig]
    out = _acc(g)
    out["per_model"] = {m: {"right": int(q.right.sum()), "n": int(len(q))} for m, q in g.groupby("model")}
    out["unique_pair_majority"] = _majority(g)
    # constant-sign baseline fitted on the side itself (descriptive; the CV below uses training folds)
    out["baseline_const_sign_in_sample"] = int((np.sign(g.y) == np.sign(np.median(g.y))).sum()) if len(g) else 0
    out["frac_dXH_positive"] = round(float((g.x > 0).mean()), 3) if len(g) else None
    return out


def _slopes(g: pd.DataFrame) -> dict:
    out = {}
    for m, q in g.groupby("model"):
        if len(q) >= 4 and q.x.nunique() > 1:
            k, b = np.polyfit(q.x, q.y, 1)
            out[m] = {"n": int(len(q)), "slope_meV_per_H_per_mA": round(float(k), 4), "intercept": round(float(b), 3),
                      "r": round(float(np.corrcoef(q.x, q.y)[0, 1]), 3)}
        else:
            out[m] = {"n": int(len(q))}
    return out


def regime_scan(c: pd.DataFrame) -> dict:
    v = variants(c)
    scan = {}
    for t in THRESHOLDS:
        strong, weak = c.rmax >= t, c.rmax < t
        e = {"n_rows_strong": int(strong.sum()), "n_rows_weak": int(weak.sum()),
             "slopes_strong_all_rows": _slopes(c[strong]), "slopes_weak_all_rows": _slopes(c[weak])}
        for name, elig in v.items():
            e[name] = {"strong": _side(c, strong, elig), "weak": _side(c, weak, elig)}
        scan[f"{t:.2f}"] = e
    return scan


def oh_split(c: pd.DataFrame) -> dict:
    v = variants(c)
    out = {"definition": "O-H = at least one structure of the pair has an O-H donor in results/stretch_check.csv",
           "all_pairs": {"O-H": int(c[c.OH].pair_id.nunique()), "non-O-H": int(c[~c.OH].pair_id.nunique())}}
    for name, elig in v.items():
        out[name] = {"all_regimes": {k: _acc(c[(c.OH == f) & elig]) for k, f in (("O-H", True), ("non-O-H", False))}}
        for t in THRESHOLDS:
            s = c.rmax >= t
            out[name][f"strong_{t:.2f}"] = {k: _acc(c[(c.OH == f) & elig & s]) for k, f in (("O-H", True), ("non-O-H", False))}
    return out


def pair_table(c: pd.DataFrame, thr: float) -> list[dict]:
    v = variants(c)["signal_filtered"]
    g = c[(c.rmax >= thr) & v]
    rows = []
    for p, q in g.groupby("pair_id"):
        r = q.right.mean()
        rows.append({"pair_id": p, "formula": q.family.iloc[0], "OH": bool(q.OH.iloc[0]), "n_models": int(len(q)),
                     "n_right": int(q.right.sum()), "majority": "right" if r > 0.5 else ("tie" if r == 0.5 else "wrong")})
    return rows


def _majority_sign(y: np.ndarray) -> float:
    s = np.sign(y).sum()
    return 1.0 if s >= 0 else -1.0


def lofo(g: pd.DataFrame, min_train: int = 10, min_x: float = MIN_DXH, orient: float = 1.0) -> dict:
    """Leave-one-formula-out. Returns held-out line-sign accuracy, raw sign(dX-H) accuracy and the training-fold
    constant-sign baseline accuracy on held-out rows with |x| >= min_x, plus held-out R^2 over all held-out rows.
    orient = -1 for a predictor expected to anti-correlate with y (e.g. O...O)."""
    g = g.reset_index(drop=True)
    pred = np.full(len(g), np.nan)
    base = np.full(len(g), np.nan)
    for fam in g.family.unique():
        te = (g.family == fam).values
        tr = ~te
        if tr.sum() < min_train or g.x[tr].nunique() < 2:
            continue
        k, b = np.polyfit(g.x[tr], g.y[tr], 1)
        pred[te] = k * g.x[te] + b
        base[te] = _majority_sign(g.y[tr].values)
    ok = ~np.isnan(pred)
    gg, p, bs = g[ok], pred[ok], base[ok]
    big = (gg.x.abs() >= min_x).values
    out = {"n_rows": int(ok.sum()), "n_formulas": int(gg.family.nunique()), "n_eligible": int(big.sum()),
           "n_eligible_pairs": int(gg[big].pair_id.nunique())}
    if big.sum():
        yy, xx = gg.y.values[big], gg.x.values[big]
        out["line_sign_acc"] = round(float((np.sign(p[big]) == np.sign(yy)).mean()), 3)
        out["raw_sign_acc"] = round(float((orient * np.sign(xx) == np.sign(yy)).mean()), 3)
        out["train_fold_baseline_acc"] = round(float((bs[big] == np.sign(yy)).mean()), 3)
        out["line_sign_right"] = int((np.sign(p[big]) == np.sign(yy)).sum())
        out["raw_sign_right"] = int((orient * np.sign(xx) == np.sign(yy)).sum())
        out["baseline_right"] = int((bs[big] == np.sign(yy)).sum())
    y = gg.y.values
    out["R2_heldout"] = round(float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()), 3)
    return out


def cv_block(c: pd.DataFrame, fitset: pd.Series) -> dict:
    g = c[fitset]
    out = {m: lofo(q) for m, q in g.groupby("model")}
    out["pooled"] = lofo(g)
    return out


def strong_regime_cv(c: pd.DataFrame) -> dict:
    """Formula-clustered CV inside the strong regime. all_eligible: fit on every clean covalent strong row.
    signal_filtered: fit and test only on rows with |ddF| > 0.1 meV/H."""
    out = {}
    for t in THRESHOLDS:
        s = c.rmax >= t
        out[f"{t:.2f}"] = {"all_eligible": cv_block(c, s), "signal_filtered": cv_block(c, s & (c.y.abs() > MIN_SIGNAL))}
    return out


def legacy_cv(c: pd.DataFrame) -> dict:
    """Original F01 test (all regimes, signal-filtered), now with the baseline taken from each training fold."""
    return {**{m: lofo(q) for m, q in c[c.y.abs() > MIN_SIGNAL].groupby("model")}, "pooled": lofo(c[c.y.abs() > MIN_SIGNAL])}


def _fold_baseline(g: pd.DataFrame, col: str = "y") -> np.ndarray:
    """Training-fold constant-sign baseline sign for every row of g (leave one formula out)."""
    base = np.full(len(g), np.nan)
    for fam in g.family.unique():
        te = (g.family == fam).values
        if (~te).sum():
            base[te] = _majority_sign(g.loc[~te, col].values)
    return base


def _block(g: pd.DataFrame, fit: pd.DataFrame) -> dict:
    """Held-out sign count of the bare dX-H rule on g, with the baseline taken from leave-one-formula-out folds of `fit`
    (fit is the fit set the baseline sign is computed from; g is a subset of fit)."""
    base = pd.Series(_fold_baseline(fit.reset_index(drop=True)), index=fit.index)
    b = base.loc[g.index]
    return {"right": int(g.right.sum()), "n": int(len(g)), "n_pairs": int(g.pair_id.nunique()), "n_formulas": int(g.family.nunique()),
            "baseline_right": int((b.values == np.sign(g.y.values)).sum())}


def oh_unfiltered_strong(c: pd.DataFrame) -> dict:
    """O-H strong-side sign test with no cut on the target (decision 05): |dX-H| >= 5 mA, rmax >= 0.99 A, O-H pairs only.
    Baseline: majority sign of y over all strong-side O-H rows of the training formulas (same fit set as strong_regime_cv)."""
    big = c.x.abs() >= MIN_DXH
    fit = c[(c.rmax >= MAIN_THR) & c.OH]
    g = fit[big.loc[fit.index]]
    out = _block(g, fit)
    out["per_model"] = {m: {"right": int(q.right.sum()), "n": int(len(q))} for m, q in g.groupby("model")}
    out["unique_pair_majority"] = _majority(g)
    out["definition"] = "O-H pairs, rmax >= 0.99 A, |dX-H| >= 5 mA, no |ddF_iso| cut; baseline = leave-one-formula-out majority sign of ddF_iso/H"
    return out


def _nested_one(base: pd.DataFrame) -> dict:
    """Leave one formula out; on each training fold choose the threshold from THRESHOLDS that maximises
    (right - wrong) of the bare sign rule on the training strong side (lowest threshold wins ties), then score the
    held-out formula's rows with rmax >= chosen threshold. Baseline: training-fold majority sign on that strong side."""
    folds = []
    R = N = B = 0
    for f in sorted(base.family.unique()):
        tr, te = base[base.family != f], base[base.family == f]
        best_t, best_s = None, None
        for t in THRESHOLDS:
            sd = tr[tr.rmax >= t]
            sc = int(sd.right.sum() - (~sd.right).sum())
            if best_s is None or sc > best_s:
                best_t, best_s = t, sc
        sgn = _majority_sign(tr[tr.rmax >= best_t].y.values)
        h = te[te.rmax >= best_t]
        r, n, b = int(h.right.sum()), int(len(h)), int((np.sign(h.y.values) == sgn).sum())
        R, N, B = R + r, N + n, B + b
        folds.append({"formula": f, "chosen_threshold": best_t, "heldout_right": r, "heldout_n": n, "heldout_baseline_right": b})
    picks = pd.Series([x["chosen_threshold"] for x in folds]).value_counts().sort_index()
    return {"right": R, "n": N, "baseline_right": B, "n_folds": len(folds), "threshold_counts": {f"{k:.2f}": int(v) for k, v in picks.items()},
            "all_folds_choose_0.99": bool((picks.index == MAIN_THR).all()), "folds": folds}


def nested_threshold_cv(c: pd.DataFrame) -> dict:
    big = c.x.abs() >= MIN_DXH
    sig = big & (c.y.abs() > MIN_SIGNAL)
    out = {"grid": THRESHOLDS, "objective": "maximise right minus wrong on the training strong side; lowest threshold wins ties"}
    for name, e in (("all_covalent_signal_cut", sig), ("all_covalent_no_cut", big)):
        out[name] = _nested_one(c[e])
    for name, e in (("OH_signal_cut", sig), ("OH_no_cut", big)):
        out[name] = _nested_one(c[e & c.OH])
    return out


def no_threshold(c: pd.DataFrame) -> dict:
    """No regime threshold: all clean covalent rows, signal-filtered (the legacy 129/150 set), with formula majority."""
    from scipy.stats import binomtest
    sig = c[variants(c)["signal_filtered"]]
    cv = lofo(c[c.y.abs() > MIN_SIGNAL])
    fm = sig.groupby("family").right.mean()
    r, w, t = int((fm > .5).sum()), int((fm < .5).sum()), int((fm == .5).sum())
    ms = sig[sig.rmax >= MAIN_THR].groupby("family").right.mean()
    return {"right": int(sig.right.sum()), "n": int(len(sig)), "n_pairs": int(sig.pair_id.nunique()), "n_formulas": int(sig.family.nunique()),
            "baseline_right_lofo": cv.get("baseline_right"), "lofo_line_sign_right": cv.get("line_sign_right"),
            "formula_majority": {"right": r, "wrong": w, "tie": t, "binomial_p_two_sided_descriptive": round(float(binomtest(r, r + w).pvalue), 5),
                                 "note": "descriptive, not a confirmatory test"},
            "formula_majority_strong_side": {"right": int((ms > .5).sum()), "wrong": int((ms < .5).sum()), "tie": int((ms == .5).sum())}}


def oh_strong_slopes(c: pd.DataFrame) -> dict:
    """All clean rows of O-H pairs with rmax >= 0.99 A: total, stretch and perpendicular (bend/libration) slopes per model."""
    out = {}
    g0 = c[(c.rmax >= MAIN_THR) & c.OH]
    for m, q in g0.groupby("model"):
        tot = np.polyfit(q.x, q.y, 1)[0]
        st = np.polyfit(q.x, q.ddF_str / q.H_per_atom, 1)[0]
        pp = np.polyfit(q.x, q.ddF_perp / q.H_per_atom, 1)[0]
        out[m] = {"n": int(len(q)), "total_slope": round(float(tot), 4), "stretch_slope": round(float(st), 4),
                  "perp_slope": round(float(pp), 4), "compensation": round(float(-pp / st), 3)}
    return out


def sevenn_sign_votes(c4: pd.DataFrame) -> dict:
    """Separately labelled SevenNet line (freeze rule): the headline O-H population with SevenNet added as a fourth
    sign vote, and SevenNet alone. Not used for slopes, compensation or any quantitative claim (decision 01 G1)."""
    big = c4.x.abs() >= MIN_DXH
    oh_all = c4[c4.OH & big]
    sv = c4[c4.model.isin(SIGN_ONLY_MODELS)]
    out = {"note": "SevenNet in sign votes only (decision 01 G1); headline blocks above use " + ", ".join(QUANT_MODELS),
           "four_models_oh_unfiltered_strong": oh_unfiltered_strong(c4),
           "four_models_oh_weak": _acc(oh_all[oh_all.rmax < MAIN_THR]),
           "four_models_oh_all_regimes": _acc(oh_all),
           "sevenn_rows_clean_covalent": int(len(sv)), "sevenn_unique_pairs": int(sv.pair_id.nunique())}
    if len(sv[sv.OH & (sv.rmax >= MAIN_THR)]):
        out["sevenn_only_oh_unfiltered_strong"] = oh_unfiltered_strong(sv)
        out["sevenn_oh_strong_slope_not_quantitative"] = oh_strong_slopes(sv)
    svb = sv[sv.OH & (sv.x.abs() >= MIN_DXH)]
    out["sevenn_only_oh_weak"] = _acc(svb[svb.rmax < MAIN_THR])
    return out


def main():
    c4 = load(models=None)
    c = c4[c4.model.isin(QUANT_MODELS)].reset_index(drop=True)
    v = variants(c)
    out = {
        "n_unique_pairs": {
            "clean_covalent_rows": int(len(c)), "unique_pairs": int(c.pair_id.nunique()), "formulas": int(c.family.nunique()),
            "unique_pairs_OH": int(c[c.OH].pair_id.nunique()), "unique_pairs_non_OH": int(c[~c.OH].pair_id.nunique()),
            "rows_per_model": {m: int(n) for m, n in c.model.value_counts().items()},
            **{f"{k}_rows": int(m.sum()) for k, m in v.items()}, **{f"{k}_pairs": int(c[m].pair_id.nunique()) for k, m in v.items()},
        },
        "variants": {"all_eligible": "|dX-H| >= 5 mA", "signal_filtered": "|dX-H| >= 5 mA and |ddF_iso| > 0.1 meV/H"},
        "regime_variable": "rmax = max over the two structures of the mean model X-H length (A); strong: rmax >= threshold",
        "regime_scan": regime_scan(c),
        "oh_split": oh_split(c),
        "pair_majority_0.99_signal_filtered": pair_table(c, MAIN_THR),
        "strong_regime_cv": strong_regime_cv(c),
        "legacy_cv_all_regimes": legacy_cv(c),
        "oh_unfiltered_strong": oh_unfiltered_strong(c),
        "nested_threshold_cv": nested_threshold_cv(c),
        "no_threshold": no_threshold(c),
        "oh_strong_slopes": oh_strong_slopes(c),
        "sevenn_sign_votes": sevenn_sign_votes(c4),
    }
    (ROOT / "results" / "F01_cv.json").write_text(json.dumps(out, indent=1))
    m = out["regime_scan"][f"{MAIN_THR:.2f}"]["signal_filtered"]
    print("unique pairs", out["n_unique_pairs"])
    for t, e in out["regime_scan"].items():
        for k in ("all_eligible", "signal_filtered"):
            s, w = e[k]["strong"], e[k]["weak"]
            print(t, k, f"strong {s['right']}/{s['n']} ({s['n_pairs']}p)", f"weak {w['right']}/{w['n']} ({w['n_pairs']}p)")
    print("0.99 signal pooled CV", out["strong_regime_cv"]["0.99"]["signal_filtered"]["pooled"])
    print("0.99 all pooled CV", out["strong_regime_cv"]["0.99"]["all_eligible"]["pooled"])
    print("legacy pooled", out["legacy_cv_all_regimes"]["pooled"])
    print("oh_unfiltered_strong", out["oh_unfiltered_strong"])
    for k, v in out["nested_threshold_cv"].items():
        if isinstance(v, dict) and "right" in v:
            print("nested", k, v["right"], v["n"], "baseline", v["baseline_right"], v["threshold_counts"])
    print("no_threshold", out["no_threshold"])
    print("oh_strong_slopes", out["oh_strong_slopes"])
    sv = out["sevenn_sign_votes"]
    print("sevenn: four-model strong", {k: sv["four_models_oh_unfiltered_strong"][k] for k in ("right", "n", "baseline_right", "unique_pair_majority")},
          "sevenn only", {k: v for k, v in sv.get("sevenn_only_oh_unfiltered_strong", {}).items() if k in ("right", "n", "baseline_right")})


if __name__ == "__main__":
    main()
