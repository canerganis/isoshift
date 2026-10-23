"""Statistics for the paper revision (referee round 1). Reads frozen CSVs only; no phonon or GPU work.

    .venv/Scripts/python.exe -I -c "import sys; sys.path.insert(0, '.'); import runpy; runpy.run_module('src.isoshift_event.paper_stats', run_name='__main__')"
    (from the repo root; -I drops the working directory from sys.path, hence the explicit insert)

writes results/paper_stats.json and docs/paper/figures/fig6_accuracy.png.

Populations
  rows      clean covalent X-H pair-model rows of results/decompose_pairs.csv, three models (rule_cv.load)
  headline  O-H pairs, rmax >= 0.99 A, |x| >= 5 mA, no cut on |ddF| (185/212, decision 07)
Orientation: x and y are struct_b minus struct_a of results/screen_pairs_refined.csv, where struct_a is the
polymorph with the lower database energy (data/isoshift/pairs.csv). y > 0: deuteration destabilises b.
Nothing here changes a frozen number; every block is labelled descriptive or post hoc where it is.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from src.isoshift_event import rule_cv

ROOT = Path(__file__).resolve().parents[2]
RNG_SEED = 0
N_BOOT = 2000
N_NULL = 200000
MODELS = ("mace", "orb", "mattersim")


def _r(v, k=3):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), k)


def _ols(x, y):
    return float(np.polyfit(x, y, 1)[0])


def load_all() -> tuple[pd.DataFrame, pd.DataFrame]:
    c = rule_cv.load()
    ref = pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv").set_index(["pair_id", "model"])
    c["struct_a"] = [ref.loc[(p, m), "struct_a"] for p, m in zip(c.pair_id, c.model)]
    c["struct_b"] = [ref.loc[(p, m), "struct_b"] for p, m in zip(c.pair_id, c.model)]
    c["pflags"] = [str(ref.loc[(p, m), "flags"]) for p, m in zip(c.pair_id, c.model)]
    c["dE_static"] = [ref.loc[(p, m), "dE_static_meV_atom"] for p, m in zip(c.pair_id, c.model)]
    for T in (0, 600, 2000):
        c[f"y{T}"] = [ref.loc[(p, m), f"ddF_iso_{T}K_refined_meV_atom"] for p, m in zip(c.pair_id, c.model)] / c.H_per_atom
    s = pd.read_csv(ROOT / "results" / "screen_structures.csv").set_index(["struct_id", "model"])
    ds = pd.read_csv(ROOT / "results" / "decompose_structures.csv").set_index(["model", "struct_id"])
    oo = pd.read_csv(ROOT / "results" / "stretch_check.csv").groupby(["source", "struct_id"]).d_OO_A.mean()

    def sval(st, m, col):
        try:
            return s.loc[(st, m), col]
        except KeyError:
            return np.nan

    def ooval(m, st):
        try:
            return float(oo.loc[(m, st)])
        except KeyError:
            return np.nan

    for k in ("a", "b"):
        c[f"V_{k}"] = [sval(st, m, "V_A3_atom") for st, m in zip(c[f"struct_{k}"], c.model)]
        c[f"conv_{k}"] = [sval(st, m, "relax_converged") for st, m in zip(c[f"struct_{k}"], c.model)]
        c[f"imag_{k}"] = [sval(st, m, "imag_fraction_H") for st, m in zip(c[f"struct_{k}"], c.model)]
        c[f"minf_{k}"] = [sval(st, m, "min_freq_THz_H") for st, m in zip(c[f"struct_{k}"], c.model)]
        c[f"fmax_{k}"] = [sval(st, m, "fmax_final_eV_A") for st, m in zip(c[f"struct_{k}"], c.model)]
        c[f"oh_{k}"] = [ds.loc[(m, st), "XH_mean_A"] for st, m in zip(c[f"struct_{k}"], c.model)]
        c[f"oo_{k}"] = [ooval(m, st) for st, m in zip(c[f"struct_{k}"], c.model)]
    c["rmin"] = c[["oh_a", "oh_b"]].min(axis=1)
    c["rmean"] = c[["oh_a", "oh_b"]].mean(axis=1)
    c["oomin"] = c[["oo_a", "oo_b"]].min(axis=1)
    c["dOO"] = (c.oo_b - c.oo_a) * 1000
    return c, ds


def headline_mask(c, thr=0.99, min_x=5.0, var="rmax"):
    return c.OH & (c[var] >= thr) & (c.x.abs() >= min_x)


def acc(pred, y):
    pred, y = np.asarray(pred), np.asarray(y)
    ok = ~np.isnan(pred)
    return int((np.sign(pred[ok]) == np.sign(y[ok])).sum()), int(ok.sum())


def lofo_direction(g: pd.DataFrame, d: np.ndarray) -> np.ndarray:
    """Predicted sign = s * sign(d), with s in {+1,-1} chosen on the training formulas (leave one formula out)."""
    g = g.reset_index(drop=True)
    out = np.full(len(g), np.nan)
    sd = np.sign(d)
    for fam in g.family.unique():
        te = (g.family == fam).values
        tr = ~te & ~np.isnan(sd)
        if not tr.sum():
            continue
        right_plus = (sd[tr] == np.sign(g.y.values[tr])).sum()
        s = 1.0 if right_plus >= tr.sum() - right_plus else -1.0
        out[te] = s * sd[te]
    return out


def majority(g, col="right"):
    m = g.groupby("pair_id")[col].mean()
    return {"n": int(len(m)), "right": int((m > 0.5).sum()), "tie": int((m == 0.5).sum()), "wrong": int((m < 0.5).sum())}


def formula_majority(g, col="right"):
    m = g.groupby("family")[col].mean()
    return {"n": int(len(m)), "right": int((m > 0.5).sum()), "tie": int((m == 0.5).sum()), "wrong": int((m < 0.5).sum()),
            "wrong_formulas": sorted(m[m < 0.5].index.tolist())}


def cluster_boot(g: pd.DataFrame, fn, n=N_BOOT, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    g = g.reset_index(drop=True)
    fams = g.family.unique()
    idx = {f: np.flatnonzero((g.family == f).values) for f in fams}
    vals = []
    for _ in range(n):
        pick = rng.choice(fams, size=len(fams), replace=True)
        rows = np.concatenate([idx[f] for f in pick])
        bg = g.iloc[rows].reset_index(drop=True)
        # keep repeated formulas distinct so within-formula demeaning stays per draw
        bg["family"] = np.repeat([f"{f}#{k}" for k, f in enumerate(pick)], [len(idx[f]) for f in pick])
        try:
            vals.append(fn(bg))
        except Exception:  # degenerate resample
            continue
    v = np.array(vals, dtype=float)
    v = v[~np.isnan(v)]
    return [_r(np.percentile(v, 2.5)), _r(np.percentile(v, 97.5))], int(len(v))


def main():
    c, ds = load_all()
    out: dict = {"note": "Revision statistics (referee round 1). Descriptive unless labelled; frozen numbers unchanged.",
                 "seed": RNG_SEED, "n_boot": N_BOOT}
    h = headline_mask(c)
    H = c[h].reset_index(drop=True)
    base = rule_cv._fold_baseline(H)
    H["base_right"] = base == np.sign(H.y)
    out["headline_check"] = {"right": int(H.right.sum()), "n": int(len(H)), "baseline_right": int(H.base_right.sum()),
                             "pairs": majority(H), "formulas": formula_majority(H)}

    # ---- 1. statistical unit -------------------------------------------------------------------------
    structs = set(H.struct_a) | set(H.struct_b)
    rows_per_formula = H.family.value_counts()
    top5 = rows_per_formula.head(5)
    out["unit"] = {
        "unique_structures": len(structs), "n_pairs": int(H.pair_id.nunique()), "n_formulas": int(H.family.nunique()),
        "rows_per_formula_top5": {k: int(v) for k, v in top5.items()}, "top5_rows": int(top5.sum()),
        "formula_equal_weight_acc": _r(H.groupby("family").right.mean().mean()),
        "formula_equal_weight_baseline_acc": _r(H.groupby("family").base_right.mean().mean()),
        "pair_equal_weight_acc": _r(H.groupby("pair_id").right.mean().mean()),
    }
    ci, nb = cluster_boot(H, lambda g: g.right.mean())
    ci_fw, _ = cluster_boot(H, lambda g: g.groupby("family").right.mean().mean())
    ci_gain, _ = cluster_boot(H, lambda g: g.right.mean() - g.base_right.mean())
    out["unit"]["acc_pooled"] = _r(H.right.mean())
    out["unit"]["acc_pooled_formula_boot_ci95"] = ci
    out["unit"]["acc_formula_equal_weight_boot_ci95"] = ci_fw
    out["unit"]["acc_minus_fixed_baseline_boot_ci95"] = ci_gain
    out["unit"]["note"] = ("Formula-clustered bootstrap: formulas resampled with replacement; the baseline correctness per row "
                           "is held at its leave-one-formula-out value, not refitted inside each resample.")

    # slopes: OLS, formula-clustered CI, Theil-Sen, O-H only, leave-one-formula-out range
    slopes = {}
    for m in MODELS:
        g = c[c.model == m]
        ols = _ols(g.x, g.y)
        bci, _ = cluster_boot(g, lambda q: _ols(q.x, q.y) if q.x.nunique() > 1 else np.nan)
        ts = stats.theilslopes(g.y, g.x)[0]
        goh = g[g.OH]
        loo = {}
        for f in g.family.unique():
            q = g[g.family != f]
            loo[f] = _ols(q.x, q.y)
        lo_f, hi_f = min(loo, key=loo.get), max(loo, key=loo.get)
        slopes[m] = {"n": int(len(g)), "ols": _r(ols), "ols_formula_boot_ci95": bci, "theil_sen": _r(ts),
                     "n_formulas": int(g.family.nunique()),
                     "ols_OH_pairs_only": _r(_ols(goh.x, goh.y)), "n_OH_rows": int(len(goh)), "n_nonOH_rows": int((~g.OH).sum()),
                     "loo_formula_min": [lo_f, _r(loo[lo_f])], "loo_formula_max": [hi_f, _r(loo[hi_f])],
                     "rows_of_largest_formula": [g.family.value_counts().index[0], int(g.family.value_counts().iloc[0])],
                     "max_abs_x_mA": _r(g.x.abs().max(), 1)}
    out["slopes_all_rows"] = slopes

    # structure-level formulation with formula fixed effects (removes pair combinatorics)
    pairs = pd.read_csv(ROOT / "data" / "isoshift" / "pairs.csv")
    s2f = {**dict(zip(pairs.struct_a, pairs.formula)), **dict(zip(pairs.struct_b, pairs.formula))}
    fe = {}
    for m in MODELS:
        g = c[c.model == m]
        st = sorted(set(g.struct_a) | set(g.struct_b))
        d = ds.loc[m].loc[st].copy()
        d["family"] = [s2f[i] for i in d.index]
        d["yH"] = d.dF_direct_meV_atom * d.n_atoms / d.n_H
        d["xx"] = d.XH_mean_A * 1000
        d = d[d.groupby("family").xx.transform("count") >= 2]

        def fe_slope(q):
            xd = q.xx - q.groupby("family").xx.transform("mean")
            yd = q.yH - q.groupby("family").yH.transform("mean")
            return float((xd * yd).sum() / (xd ** 2).sum())

        bci, _ = cluster_boot(d.reset_index(), fe_slope)
        fe[m] = {"n_structures": int(len(d)), "n_formulas": int(d.family.nunique()), "slope": _r(fe_slope(d)),
                 "formula_boot_ci95": bci}
    out["structure_level_fixed_effects"] = {"definition": "per-structure F_D - F_H per H (direct, 300 K) on mean X-H (mA), "
                                            "within-formula (demeaned) OLS, structures in the 521 clean covalent rows", **fe}

    # ---- 2. baselines and competitors on the headline rows ---------------------------------------------
    rng = np.random.default_rng(RNG_SEED)
    per_pair = H.groupby("pair_id").agg(r=("right", "sum"), n=("right", "size"))
    r, n = per_pair.r.values, per_pair.n.values
    flips = rng.integers(0, 2, size=(N_NULL, len(r)), dtype=np.int8)
    null = (np.where(flips == 1, n - r, r)).sum(axis=1)
    p_null = (int((null >= H.right.sum()).sum()) + 1) / (N_NULL + 1)
    out["null_pair_orientation"] = {
        "definition": "predicted sign of each pair (shared by its models) flipped at random; orientation invariant",
        "draws": N_NULL, "mean": _r(null.mean(), 1), "sd": _r(null.std(), 1), "q99_9": int(np.percentile(null, 99.9)),
        "max": int(null.max()), "observed": int(H.right.sum()), "p_upper": p_null,
        "hist": {int(k): int(v) for k, v in zip(*np.unique(null, return_counts=True))}}
    comp = {}
    y = H.y.values
    comp["constant_plus_db_energy"] = {"meaning": "deuteration destabilises the polymorph with the higher database energy (b)",
                                       "fixed": acc(np.ones(len(H)), y), "lofo": acc(base, y)}
    dEs = H.dE_static.values
    comp["mlip_static_energy"] = {"meaning": "deuteration destabilises the polymorph with the higher MLIP static energy",
                                  "fixed": acc(np.sign(dEs), y), "lofo": acc(lofo_direction(H, dEs), y)}
    dV = (H.V_a - H.V_b).values
    comp["denser_destabilised"] = {"meaning": "deuteration destabilises the denser polymorph (MLIP volumes)",
                                   "fixed": acc(np.sign(dV), y), "lofo": acc(lofo_direction(H, dV), y)}
    comp["OO_longer_favoured"] = {"meaning": "deuteration favours the polymorph with the longer mean donor O...O (same rows)",
                                  "fixed": acc(-np.sign(H.dOO.values), y), "lofo": acc(lofo_direction(H, -H.dOO.values), y),
                                  "n_rows_with_OO": int(H.dOO.notna().sum()),
                                  "r_x_vs_dOO": _r(np.corrcoef(H.x[H.dOO.notna()], H.dOO[H.dOO.notna()])[0, 1])}
    comp["OH_shorter_favoured"] = {"meaning": "the short-bond rule", "fixed": acc(np.sign(H.x.values), y),
                                   "lofo": acc(lofo_direction(H, H.x.values), y)}
    oo_ok = H.dOO.notna()
    comp["same_rows_OH_vs_OO"] = {"OH_right": int(H.right[oo_ok].sum()),
                                  "OO_right": int((-np.sign(H.dOO[oo_ok]) == np.sign(H.y[oo_ok])).sum()), "n": int(oo_ok.sum()),
                                  "pair_majority_OO": majority(H[oo_ok].assign(rOO=(-np.sign(H.dOO[oo_ok]) == np.sign(H.y[oo_ok]))), "rOO")}
    out["competitors_headline_rows"] = comp

    # ---- 3. accuracy versus |ddF|, model spread, flags, coverage ----------------------------------------
    bins = [0, 0.5, 1, 2, 5, np.inf]
    ab = {}
    for lo, hi in zip(bins[:-1], bins[1:]):
        q = H[(H.y.abs() >= lo) & (H.y.abs() < hi)]
        ab[f"{lo}-{hi}"] = {"right": int(q.right.sum()), "n": int(len(q))}
    big = H.y.abs() >= 1
    out["accuracy_vs_abs_ddF_meV_per_H"] = {"bins": ab, "ge1": [int(H.right[big].sum()), int(big.sum())],
                                            "lt1": [int(H.right[~big].sum()), int((~big).sum())]}
    sp = H.groupby("pair_id").y.agg(["min", "max", "size", "mean"])
    sp = sp[sp["size"] >= 2]
    disagree = int(((sp["min"] < 0) & (sp["max"] > 0)).sum())
    spread = (sp["max"] - sp["min"])
    H["spread"] = H.pair_id.map(spread)
    H["z"] = H.y.abs() / H.spread
    zb = {}
    for lo, hi in ((0, 0.5), (0.5, 1), (1, 2), (2, np.inf)):
        q = H[(H.z >= lo) & (H.z < hi)]
        zb[f"{lo}-{hi}"] = {"right": int(q.right.sum()), "n": int(len(q))}
    out["model_spread"] = {"pairs_with_2plus_models": int(len(sp)), "pairs_models_disagree_in_sign": disagree,
                           "median_spread_meV_per_H": _r(spread.median()), "median_abs_ddF_meV_per_H": _r(H.y.abs().median()),
                           "accuracy_vs_abs_ddF_over_spread": zb}
    fl = {}
    for flag in ("classical_limit_violation", "relax_not_converged", "soft_mode_bracketed", "theoretical"):
        f = H.pflags.str.contains(flag)
        fl[flag] = {"flagged": [int(H.right[f].sum()), int(f.sum())], "unflagged": [int(H.right[~f].sum()), int((~f).sum())]}
    f = H.pflags.str.contains("classical_limit_violation")
    fl["classical_limit_violation"]["unflagged_0K"] = [int((np.sign(H.x[~f]) == np.sign(H.y0[~f])).sum()), int((~f).sum())]
    out["flags_headline_rows"] = fl

    O = c[c.OH & (c.x.abs() >= 5)]
    curve = []
    for t in np.round(np.arange(0.950, 1.0401, 0.0025), 4):
        s_, w_ = O[O.rmax >= t], O[O.rmax < t]
        curve.append({"t": float(t), "strong_right": int(s_.right.sum()), "strong_n": int(len(s_)),
                      "weak_right": int(w_.right.sum()), "weak_n": int(len(w_))})
    out["accuracy_coverage_rmax"] = {"population": "O-H rows, |x| >= 5 mA, three models (232 rows)", "curve": curve}

    # ---- 4. physically cleaner subset -----------------------------------------------------------------
    conv = (H.conv_a == True) & (H.conv_b == True)  # noqa: E712
    noimag = (H.imag_a.fillna(1) == 0) & (H.imag_b.fillna(1) == 0)
    smallimag = (H.imag_a.fillna(1) <= 1e-3) & (H.imag_b.fillna(1) <= 1e-3)
    phys = {}
    for name, msk in (("converged", conv), ("no_imag_H_mesh", noimag), ("converged_and_no_imag", conv & noimag),
                      ("converged_and_imag_frac_le_1e-3", conv & smallimag)):
        q = H[msk]
        b = rule_cv._fold_baseline(q.reset_index(drop=True)) if len(q) else np.array([])
        phys[name] = {"right": int(q.right.sum()), "n": int(len(q)), "pairs": majority(q) if len(q) else None,
                      "formulas": int(q.family.nunique()), "lofo_baseline_right": int((b == np.sign(q.y.values)).sum()),
                      "mp985293_rows": int(q.pair_id.str.contains("mp-985293").sum())}
    allrows = c.copy()
    ac = (allrows.conv_a == True) & (allrows.conv_b == True) & (allrows.imag_a.fillna(1) == 0) & (allrows.imag_b.fillna(1) == 0)  # noqa: E712
    phys["slopes_all_rows_converged_and_no_imag"] = {m: {"n": int(len(q)), "ols": _r(_ols(q.x, q.y)) if len(q) > 3 else None}
                                                     for m, q in allrows[ac].groupby("model")}
    phys["source"] = ("results/screen_structures.csv: relax_converged, imag_fraction_H (share of H-mass mesh modes that are "
                      "imaginary) from the screen run of each structure and model; the refined free energies reuse these force "
                      "constants. No re-relaxation was done.")
    out["physically_cleaner_subset"] = phys

    # ---- 5. weak side ------------------------------------------------------------------------------------
    W = c[c.OH & (c.rmax < 0.99) & (c.x.abs() >= 5)]
    Wall = c[c.OH & (c.rmax < 0.99)]
    out["weak_side"] = {"right": int(W.right.sum()), "n": int(len(W)), "reversed": int((~W.right).sum()),
                        "pairs": majority(W), "formulas": formula_majority(W),
                        "slope_all_weak_OH_rows": {m: {"n": int(len(q)), "ols": _r(_ols(q.x, q.y)) if len(q) > 3 else None}
                                                   for m, q in Wall.groupby("model")},
                        "per_model": {m: [int(q.right.sum()), int(len(q))] for m, q in W.groupby("model")}}

    # ---- multiverse ----------------------------------------------------------------------------------------
    mv = []
    for var in ("rmax", "rmin", "rmean"):
        for mx in (3.0, 5.0, 10.0):
            g = c[headline_mask(c, 0.99, mx, var)].reset_index(drop=True)
            b = rule_cv._fold_baseline(g)
            mv.append({"regime": f"{var} >= 0.99", "min_x": mx, "right": int(g.right.sum()), "n": int(len(g)),
                       "baseline": int((b == np.sign(g.y)).sum()), "pairs": majority(g)})
    for mx in (3.0, 5.0, 10.0):
        g = c[c.OH & (c.oomin <= 2.93) & (c.x.abs() >= mx)].reset_index(drop=True)
        b = rule_cv._fold_baseline(g)
        mv.append({"regime": "shorter mean O...O <= 2.93", "min_x": mx, "right": int(g.right.sum()), "n": int(len(g)),
                   "baseline": int((b == np.sign(g.y)).sum()), "pairs": majority(g)})
    for T in (0, 600, 2000):
        g = H.copy()
        g["yT"] = g[f"y{T}"]
        b = rule_cv._fold_baseline(g, "yT")
        mv.append({"regime": "rmax >= 0.99", "min_x": 5.0, "T_K": T, "right": int((np.sign(g.x) == np.sign(g.yT)).sum()),
                   "n": int(len(g)), "baseline": int((b == np.sign(g.yT)).sum()),
                   "source": "screen_pairs_refined.csv refined columns"})
    out["multiverse"] = mv

    # ---- 7. AlOOH: QHA isotope term, conditional fractionation conversion ---------------------------------
    pc = json.load(open(ROOT / "results" / "card_alooh_pressure.json"))
    tc = json.load(open(ROOT / "results" / "card_alooh_temperature.json"))
    cj = json.load(open(ROOT / "results" / "card_alooh.json"))
    al = {"isotope_term_meV_atom_at_10_15_20_GPa_300K": {m: [_r(d - h) for h, d in zip(v["dG_meV_atom"]["H"], v["dG_meV_atom"]["D"])]
                                                         for m, v in pc.items()},
          "isotope_term_meV_atom_0GPa_harmonic_300K": {m: _r(v["ddF300"]) for m, v in cj.items()}}
    kB = 0.08617333262  # meV/K
    conv_L = {}
    for key, v in tc.items():
        if not key.startswith("AlOOH"):
            continue
        m = key.split("/")[1]
        P = np.array(v["pressures_GPa"], float)
        for T in ("300", "1000"):
            t = v["T"][T]
            iso = np.array(t["dG_meV_atom_D"]) - np.array(t["dG_meV_atom_H"])
            iso_at_pt = float(np.interp(t["Pt_H_GPa"], P, iso, left=None, right=None)) if P.min() <= t["Pt_H_GPa"] <= P.max() \
                else float(np.polyval(np.polyfit(P, iso, 1), t["Pt_H_GPa"]))
            ddG_fu = 4 * iso_at_pt  # meV per AlOOH formula unit (4 atoms, n_H = 1)
            conv_L.setdefault(m, {})[T] = {"Pt_H_GPa": t["Pt_H_GPa"], "isotope_term_meV_atom_at_Pt": _r(iso_at_pt),
                                           "1000lnalpha_permil_if_R0": _r(1000 * ddG_fu / (kB * float(T)), 1)}
    al["conditional_fractionation"] = {"definition": "1000 ln alpha(diaspore - delta) = 1000 ddG/(n_H kT) with R = 0 (M02), "
                                       "ddG = QHA isotope term at the model H transition pressure; conditional conversion, "
                                       "not a fractionation prediction", **conv_L}
    out["alooh"] = al

    # ---- volume isotope ranges for the three models only --------------------------------------------------
    v = pd.read_csv(ROOT / "results" / "validation" / "volume_isotope.csv")
    v = v[v.T_K.isin([290, 300])]  # room-temperature rows: brucite 290 K, LiH 300 K
    v3 = v[v.model.isin(MODELS)]
    out["volume_isotope_three_models_pct"] = {cse: [_r(q.VIE_pct.min(), 2), _r(q.VIE_pct.max(), 2)]
                                              for cse, q in v3.groupby("case") if cse in ("brucite", "LiH")}
    out["volume_isotope_four_models_pct"] = {cse: [_r(q.VIE_pct.min(), 2), _r(q.VIE_pct.max(), 2)]
                                             for cse, q in v.groupby("case") if cse in ("brucite", "LiH")}
    rp = pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv")
    rp = rp[rp.ddF_iso_300K_meV_atom.notna()]
    out["pairs_with_screen_result"] = {"three_models": int(rp[rp.model.isin(MODELS)].pair_id.nunique()),
                                       "four_models": int(rp.pair_id.nunique())}

    # ---- mp-985293 exact ranges -------------------------------------------------------------------------
    mp = H[H.pair_id.str.contains("mp-985293")].copy()
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv").set_index(["pair_id", "model"])
    mp["C"] = [-d.loc[(p, m), "ddF_perp"] / d.loc[(p, m), "ddF_str"] for p, m in zip(mp.pair_id, mp.model)]
    partner_V = []
    for _, rrow in mp.iterrows():
        other = rrow.struct_b if rrow.struct_a == "mp-985293" else rrow.struct_a
        partner_V.append(rrow.V_b if rrow.struct_a == "mp-985293" else rrow.V_a)
    out["mp985293"] = {"compensation_by_model": {m: [_r(q.C.min(), 4), _r(q.C.max(), 4)] for m, q in mp.groupby("model")},
                       "partner_V_A3_atom_min_max": [_r(min(partner_V), 3), _r(max(partner_V), 3)]}

    # ---- analytic estimate ratio ------------------------------------------------------------------------
    rho = 1.373607
    S = [0.016861 * s for s in (19.0, 19.5)]
    fitted = (0.245, 0.259, 0.252, 0.277, 0.308, 0.293)
    out["analytic"] = {"S_str": [_r(x, 3) for x in S], "ratio_min": _r(min(S) / max(fitted)), "ratio_max": _r(max(S) / min(fitted)),
                       "one_over_sqrt2_overstatement_0K": _r((1 - 2 ** -0.5) / (1 - 1 / rho))}

    out["round2"] = round2(c, H, W)

    (ROOT / "results" / "paper_stats.json").write_text(json.dumps(out, indent=1))
    figure(out, H)
    print(json.dumps({k: out[k] for k in ("headline_check", "unit")}, indent=1)[:3000])


def round2(c: pd.DataFrame, H: pd.DataFrame, W: pd.DataFrame) -> dict:
    """Numbers added in referee round 2 (decision 16). Post-freeze and descriptive; no frozen number changes."""
    r: dict = {"note": "Decision 16 additions; post-freeze, descriptive sensitivities, not error estimates."}
    miss = W[~W.right]
    lo = W[W.rmax < 0.98]
    r["weak_side_pattern"] = {"n": int(len(W)), "right": int(W.right.sum()), "y_pos": int((W.y > 0).sum()),
                              "x_neg": int((W.x < 0).sum()), "misses": int(len(miss)),
                              "misses_rmax_0.98_0.99": int(((miss.rmax >= 0.98) & (miss.rmax < 0.99)).sum()),
                              "below_0.98": [int(lo.right.sum()), int(len(lo))]}

    def count(yk):
        return int((np.sign(yk) == np.sign(H.x)).sum())

    r["perp_scaling_k"] = {str(k): count((H.ddF_str + k * H.ddF_perp) / H.H_per_atom)
                           for k in (0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5)}
    r["stretch_division_f"] = {str(f): count((H.ddF_str / f + H.ddF_perp) / H.H_per_atom)
                               for f in (1.1, 1.22, 1.3, 1.5, 1.8, 2.0)}
    per = {}
    for m, q in c.groupby("model"):
        ks = _ols(q.x, q.ddF_str / q.H_per_atom)
        kp = _ols(q.x, q.ddF_perp / q.H_per_atom)
        k, b = np.polyfit(q.x, q.y, 1)
        per[m] = {"C_slope": _r(-kp / ks), "one_over_C": _r(-ks / kp, 2), "intercept_meV_per_H": _r(b),
                  "through_origin_slope": _r((q.x * q.y).sum() / (q.x ** 2).sum())}
    r["all_rows_slope_ratio_intercepts"] = per
    # 300 K at the refinement mesh (about 60/a, even, 4 to 16): screen_pairs_refined.csv
    ref =pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv").set_index(["pair_id", "model"])
    y60 = np.array([ref.loc[(p, m), "ddF_iso_300K_refined_meV_atom"] for p, m in zip(H.pair_id, H.model)]) / H.H_per_atom.values
    r["mesh_60a_300K"] = {"right": count(y60), "n": int(len(H)),
                          "sign_flips_vs_headline": int((np.sign(y60) != np.sign(H.y.values)).sum()),
                          "max_abs_change_meV_per_H": _r(np.nanmax(np.abs(y60 - H.y.values)))}
    yd = H.ddF_direct / H.H_per_atom
    r["direct_route_300K"] = {"right": count(yd), "n": int(len(H))}
    others = H[~H.pair_id.str.contains("mp-985293")]
    r["median_C_other_headline_rows"] = {"n": int(len(others)),
                                         "median": _r((-others.ddF_perp / others.ddF_str).median())}
    nmod = H.groupby("pair_id").model.transform("size")
    r["single_model_headline_rows"] = int((nmod < 2).sum())
    bm = pd.read_csv(ROOT / "results" / "benchmark" / "summary.csv")
    r["benchmark"] = {f"{row.model}/{row.setting}": {"dzpe_MAE": _r(row.dzpe_MAE_meV, 2), "dF300_MAE": _r(row.dF300_MAE_meV, 2),
                                                     "stretch_MAE": _r(row.stretch_MAE_cm1, 1),
                                                     "stretch_bias": _r(row.stretch_bias_cm1, 1),
                                                     "n": int(row.n), "n_imag_dft": int(row.n_imag_dft)}
                      for row in bm.itertuples()}
    r["soft_mode_flag_headline_rows"] = int(H.pflags.str.contains("soft_mode_bracketed").sum())
    return r


def figure(out, H):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, grid, c1, c2 = "#222222", "#dddddd", "#0072B2", "#999999"
    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.4))
    cv = out["accuracy_coverage_rmax"]["curve"]
    t = [q["t"] for q in cv]
    sacc = [q["strong_right"] / q["strong_n"] if q["strong_n"] else np.nan for q in cv]
    wacc = [q["weak_right"] / q["weak_n"] if q["weak_n"] else np.nan for q in cv]
    a = ax[0]
    a.plot(t, sacc, color=c1, lw=1.8, label="rule right, rows with $r_{max}\\geq t$")
    a.plot(t, wacc, color=c2, lw=1.8, ls="--", label="rule right, rows with $r_{max}< t$")
    a2 = a.twinx()
    a2.plot(t, [q["strong_n"] for q in cv], color=c1, lw=0.8, alpha=0.5)
    a2.set_ylabel("rows with $r_{max}\\geq t$ (thin line)", color=ink, fontsize=8)
    a.axvline(0.99, color=ink, lw=0.6, ls=":")
    a.text(0.991, 0.05, "0.99 Å (post hoc)", fontsize=7, color=ink)
    a.set_xlabel("boundary t on larger mean O-H of the pair (Å)")
    a.set_ylabel("fraction right")
    a.set_ylim(0, 1.02)
    a.legend(fontsize=7, loc="center left", frameon=False)
    a.set_title("(a) accuracy and coverage across the boundary", fontsize=9, loc="left")
    b = ax[1]
    bins = out["accuracy_vs_abs_ddF_meV_per_H"]["bins"]
    labels = ["<0.5", "0.5-1", "1-2", "2-5", ">5"]
    vals = [v["right"] / v["n"] for v in bins.values()]
    ns = [v["n"] for v in bins.values()]
    b.bar(range(5), vals, color=c1, width=0.65)
    for i, (vv, nn, rr) in enumerate(zip(vals, ns, [v["right"] for v in bins.values()])):
        b.text(i, vv + 0.02, f"{rr}/{nn}", ha="center", fontsize=7, color=ink)
    base = out["headline_check"]["baseline_right"] / out["headline_check"]["n"]
    b.axhline(base, color=c2, lw=1, ls="--")
    b.text(0.5, base + 0.015, "constant-sign baseline (131/212)", fontsize=7, color=ink, ha="center", va="bottom",
           bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
    b.set_xticks(range(5), labels)
    b.set_xlabel("|ΔΔF$_{iso}$| per H at 300 K (meV)")
    b.set_ylim(0, 1.1)
    b.set_title("(b) headline rows by size of the effect", fontsize=9, loc="left")
    for a_ in (ax[0], ax[1], a2):
        a_.tick_params(labelsize=7)
        for sname in ("top",):
            a_.spines[sname].set_visible(False)
    ax[1].spines["right"].set_visible(False)
    ax[0].grid(color=grid, lw=0.4)
    fig.tight_layout()
    fig.savefig(ROOT / "docs" / "paper" / "figures" / "fig6_accuracy.png", dpi=300)


if __name__ == "__main__":
    main()
