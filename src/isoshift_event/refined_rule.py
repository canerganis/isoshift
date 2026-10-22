"""F08 (post-freeze addendum): can H-bond geometry predict when bend/libration cancels more than the stretch term?

F01 predicts sign(ddF_iso) = sign(dX-H). It fails in the 10 pairs that contain Al(OH)3 mp-985293, where bend and
libration cancel 95 to 132% of the stretch term instead of about half. This module tests one refined, geometry-only
rule with two inputs, dX-H and the change of the mean O-H...O angle, with constants taken from component fits
(stretch and bend/libration terms separately), never from the sign outcome. Predeclared test:
docs/predictions/P06_refined_rule.md. Finding: docs/findings/F08-refined-rule.md.

Geometry (per relaxed structure and model, phonopy unit cell from the force-constant cache):
  donor      H whose nearest non-H atom is O at <= 1.15 A
  acceptor   nearest O other than the donor with H...O < 2.6 A (periodic neighbour list), as in stretch_check._donors
  theta      O_donor-H...O_acceptor angle at H (degrees); 180 = linear hydrogen bond
  structure  means over O-H donors (theta and O...O over donors with an acceptor)
Pair inputs, same orientation as decompose.py (b minus a, struct_a/struct_b of results/screen_pairs_refined.csv):
  x       = dXH_mean_A * 1000 (mA, from results/decompose_pairs.csv, the F01 input)
  dtheta  = theta(b) - theta(a) (degrees)

Physical model (McKenzie-type stretch/bend competition; bend and libration stiffen with H-bond strength and linearity):
  stretch term per H   = s * x
  bend/libration term  = p_x * x + p_t * dtheta
  refined prediction   = sign((s + p_x) * x + p_t * dtheta) = sign(x - C * dtheta),  C = -p_t / (s + p_x)
Equivalently a predicted compensation fraction f = -(p_x * x + p_t * dtheta) / (s * x) = A + B * dtheta / x with
A = -p_x / s, B = -p_t / s; the refined rule reverses F01 exactly when f > 1. Rows without dtheta fall back to sign(x).
Fit set: clean covalent O-H rows of MACE, ORB and MatterSim with rmax >= 0.99 A and finite dtheta, any |dX-H|, no cut
on the target (the population of rule_cv.oh_strong_slopes); least squares through the origin.

    python -m src.isoshift_event.refined_rule geometry    # rebuild results/hbond_geometry.csv from .cache (minutes)
    python -m src.isoshift_event.refined_rule constants   # step 1 of P06: constants and three-model numbers only
    python -m src.isoshift_event.refined_rule             # step 2: LOFO and SevenNet scores -> results/F08_refined_rule.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import rule_cv

ROOT = Path(__file__).resolve().parents[2]
GEOM_CSV = ROOT / "results" / "hbond_geometry.csv"
OUT_JSON = ROOT / "results" / "F08_refined_rule.json"
DONOR_CUT = 1.15  # A
HB_CUT = 2.6  # A, H...O acceptor cut (stretch_check._donors)
STRUCT = rule_cv.POSTHOC_STRUCT  # mp-985293
HEADLINE_MODELS = rule_cv.QUANT_MODELS
HELDOUT_MODELS = ("sevenn",)
CANDIDATES = ("dtheta", "dOO", "dHO", "dnacc", "dbif")  # explored during derivation (three models only)


# ---------------------------------------------------------------------------------------------------------------- geometry
def _unit_cell(path: Path):
    from ase import Atoms
    import yaml

    lines, on = [], False
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("unit_cell:"):
                on = True
            elif on and ln.startswith("supercell:"):
                break
            if on:
                lines.append(ln)
    u = yaml.safe_load("".join(lines))["unit_cell"]
    return Atoms([p["symbol"] for p in u["points"]], cell=u["lattice"],
                 scaled_positions=[p["coordinates"] for p in u["points"]], pbc=True)


def donor_geometry(at) -> list[dict]:
    from ase.neighborlist import neighbor_list

    sym = np.array(at.get_chemical_symbols())
    i, j, d, D = neighbor_list("ijdD", at, HB_CUT)  # D = r_j - r_i
    rows = []
    for h in np.flatnonzero(sym == "H"):
        m = (i == h) & (sym[j] != "H")
        if not m.any():
            continue
        k = int(np.argmin(np.where(m, d, 1e9)))
        if sym[j[k]] != "O" or d[k] > DONOR_CUT:
            continue
        v_oh, d_oh = D[k], float(d[k])
        acc = []
        for q in np.flatnonzero(m & (sym[j] == "O")):
            if q == k:
                continue
            v_ha = D[q]
            theta = float(np.degrees(np.arccos(np.clip(np.dot(v_oh, v_ha) / (d_oh * d[q]), -1, 1))))
            acc.append((float(d[q]), theta, float(np.linalg.norm(v_ha - v_oh))))
        acc.sort()
        a1 = acc[0] if acc else (np.nan, np.nan, np.nan)
        rows.append({"d_OH": d_oh, "d_HO": a1[0], "theta": a1[1], "d_OO": a1[2],
                     "n_acc": sum(1 for a in acc if a[1] >= 110.0)})
    return rows


def build_geometry() -> pd.DataFrame:
    from . import refine

    idx = refine._cache_index()
    s = pd.read_csv(ROOT / "results" / "decompose_structures.csv")
    s = s[s.covalent_XH == True]  # noqa: E712
    out = []
    for model, sid in zip(s.model, s.struct_id):
        raw = json.loads((refine.RAW / model / f"{sid}.json").read_text())
        calc = "{name}-{model}".format(**raw["calc"])
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in calc)
        key = (safe, round(raw["fc_meta"]["energy_eV"], 6), round(raw["fc_meta"]["volume_A3"], 4))
        if key not in idx:
            continue
        don = pd.DataFrame(donor_geometry(_unit_cell(idx[key] / "phonopy_params.yaml")))
        if don.empty:
            continue
        out.append({"model": model, "struct_id": sid, "n_OH_donors": len(don), "n_with_acceptor": int(don.d_HO.notna().sum()),
                    "OH_mean_A": round(float(don.d_OH.mean()), 5), "OO_mean_A": round(float(don.d_OO.mean()), 5),
                    "HO_mean_A": round(float(don.d_HO.mean()), 5), "theta_mean_deg": round(float(don.theta.mean()), 3),
                    "n_acc_mean": round(float(don.n_acc.mean()), 4), "bifurcated_frac": round(float((don.n_acc >= 2).mean()), 4)})
    g = pd.DataFrame(out)
    g.to_csv(GEOM_CSV, index=False)
    return g


# ---------------------------------------------------------------------------------------------------------------- rows
def load(models=None) -> pd.DataFrame:
    """rule_cv.load rows (clean covalent) with pair geometry differences in decompose orientation."""
    c = rule_cv.load(models=models)
    g = pd.read_csv(GEOM_CSV).set_index(["model", "struct_id"])
    sp = pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv").drop_duplicates(["pair_id", "model"]).set_index(["pair_id", "model"])
    ab = [(sp.loc[(p, m)].struct_a, sp.loc[(p, m)].struct_b) for p, m in zip(c.pair_id, c.model)]
    for col, name, scale in (("theta_mean_deg", "dtheta", 1.0), ("OO_mean_A", "dOO", 1000.0), ("HO_mean_A", "dHO", 1000.0),
                             ("n_acc_mean", "dnacc", 1.0), ("bifurcated_frac", "dbif", 1.0), ("OH_mean_A", "dOH_donor", 1000.0)):
        va = np.array([g[col].get((m, a), np.nan) for m, (a, _) in zip(c.model, ab)], float)
        vb = np.array([g[col].get((m, b), np.nan) for m, (_, b) in zip(c.model, ab)], float)
        c[name] = (vb - va) * scale
        if col == "theta_mean_deg":
            c["theta_a"], c["theta_b"] = va, vb
    c["ystr"] = c.ddF_str / c.H_per_atom
    c["yperp"] = c.ddF_perp / c.H_per_atom
    c["has_struct"] = c.pair_id.str.contains(STRUCT, regex=False)
    return c


def headline(c: pd.DataFrame) -> pd.DataFrame:
    return rule_cv._headline(c)


def fit_set(c: pd.DataFrame, feat: str = "dtheta") -> pd.DataFrame:
    return c[c.OH & (c.rmax >= rule_cv.MAIN_THR) & np.isfinite(c[feat])]


def _ls(X, y):
    return np.linalg.lstsq(np.asarray(X, float), np.asarray(y, float), rcond=None)[0]


def constants(f: pd.DataFrame, feat: str = "dtheta") -> dict:
    s = float(_ls(f[["x"]], f.ystr)[0])
    px, pt = (float(v) for v in _ls(f[["x", feat]], f.yperp))
    res = f.yperp - px * f.x - pt * f[feat]
    return {"feature": feat, "n_fit": int(len(f)), "s_stretch": s, "p_x": px, "p_feat": pt,
            "C": -pt / (s + px), "A": -px / s, "B": -pt / s, "R2_perp": float(1 - res.var() / f.yperp.var())}


def predict(g: pd.DataFrame, k: dict) -> np.ndarray:
    feat = g[k["feature"]].values
    p = np.sign((k["s_stretch"] + k["p_x"]) * g.x.values + k["p_feat"] * np.nan_to_num(feat))
    return np.where(np.isfinite(feat), p, np.sign(g.x.values))


def _count(g: pd.DataFrame, pred: np.ndarray) -> dict:
    r = pred == np.sign(g.y.values)
    s = g.has_struct.values
    out = {"right": int(r.sum()), "n": int(len(g)), "acc": round(float(r.mean()), 4) if len(g) else None,
           "n_pairs": int(g.pair_id.nunique()),
           "struct_rows": {"right": int(r[s].sum()), "n": int(s.sum())},
           "other_rows": {"right": int(r[~s].sum()), "n": int((~s).sum())},
           "per_model": {m: {"right": int(r[(g.model == m).values].sum()), "n": int((g.model == m).sum())} for m in sorted(g.model.unique())}}
    gg = g.assign(_r=r)
    out["unique_pair_majority"] = rule_cv._majority(gg.assign(right=gg._r))
    return out


def three_model_insample(c3: pd.DataFrame, k: dict) -> dict:
    h = headline(c3)
    return {"F01": _count(h, np.sign(h.x.values)), "refined": _count(h, predict(h, k)),
            "n_rows_without_dtheta_fallback_to_F01": int((~np.isfinite(h.dtheta)).sum())}


def candidate_table(c3: pd.DataFrame) -> dict:
    """Every geometric input explored during derivation, each with its component-fit constants (three models)."""
    h = headline(c3)
    out = {}
    for feat in CANDIDATES:
        k = constants(fit_set(c3, feat), feat)
        out[feat] = {**{a: round(b, 6) if isinstance(b, float) else b for a, b in k.items()}, "insample_headline": _count(h, predict(h, k))}
    return out


def lofo(c3: pd.DataFrame, feat: str = "dtheta") -> dict:
    """Leave one formula out: refit s, p_x, p_feat without the held-out formula, score its headline rows."""
    h = headline(c3)
    f = fit_set(c3, feat)
    pred = np.full(len(h), np.nan)
    folds = []
    for fam in sorted(h.family.unique()):
        k = constants(f[f.family != fam], feat)
        te = (h.family == fam).values
        pred[te] = predict(h[te], k)
        r = pred[te] == np.sign(h.y.values[te])
        folds.append({"formula": fam, "C": round(k["C"], 4), "right": int(r.sum()), "n": int(te.sum()),
                      "F01_right": int((np.sign(h.x.values[te]) == np.sign(h.y.values[te])).sum())})
    base = rule_cv._block(h, c3[(c3.rmax >= rule_cv.MAIN_THR) & c3.OH])
    return {"refined": _count(h, pred), "F01": _count(h, np.sign(h.x.values)), "train_fold_baseline_right": base["baseline_right"],
            "C_range": [min(x["C"] for x in folds), max(x["C"] for x in folds)],
            "AlOH3_fold": next((x for x in folds if x["formula"] == "Al(HO)3"), None), "folds": folds}


def sevenn_scores(c_all: pd.DataFrame, k: dict) -> dict:
    sv = c_all[c_all.model.isin(HELDOUT_MODELS)]
    h = headline(sv)
    oh_all = sv[sv.OH]
    f01, ref = _count(h, np.sign(h.x.values)), _count(h, predict(h, k))
    gap = None if not h.shape[0] else round(100 * (ref["acc"] - f01["acc"]), 2)
    s = h.has_struct.values
    clause2 = bool(s.sum()) and ref["struct_rows"]["right"] >= 0.5 * s.sum()
    return {"population": "SevenNet rows of the headline definition: O-H pairs, rmax >= 0.99 A, |dX-H| >= 5 mA, no target cut",
            "F01": f01, "refined": ref, "gain_points": gap,
            "clause1_gain_ge_5_points": bool(gap is not None and gap >= 5.0),
            "clause2_struct_rows_right_at_least_half": clause2,
            "clause2_note": f"{int(s.sum())} SevenNet rows contain {STRUCT}",
            "verdict": "success" if (gap is not None and gap >= 5.0 and clause2) else "failure",
            "secondary_all_OH_rows_no_dXH_cut": {"F01": _count(oh_all, np.sign(oh_all.x.values)), "refined": _count(oh_all, predict(oh_all, k))},
            "n_rows_without_dtheta": int((~np.isfinite(h.dtheta)).sum())}


def compensation_tracking(c3: pd.DataFrame, k: dict) -> dict:
    """Does the predicted fraction f = A + B * dtheta / x track the computed compensation -ddF_perp / ddF_str?"""
    from scipy.stats import spearmanr

    h = headline(c3).dropna(subset=["dtheta"])
    f = k["A"] + k["B"] * h.dtheta / h.x
    comp = -h.ddF_perp / h.ddF_str
    m = h.has_struct.values
    q = lambda v: {"median": round(float(np.median(v)), 3), "min": round(float(np.min(v)), 3), "max": round(float(np.max(v)), 3)}  # noqa: E731
    return {"n": int(len(h)), "spearman_all": round(float(spearmanr(f, comp)[0]), 3),
            "spearman_without_struct": round(float(spearmanr(f[~m], comp[~m])[0]), 3),
            "struct_rows": {"predicted": q(f[m]), "computed": q(comp[m])},
            "other_rows": {"predicted": q(f[~m]), "computed": q(comp[~m]),
                           "n_predicted_gt1": int((f[~m] > 1).sum()), "n_computed_gt1": int((comp[~m] > 1).sum()),
                           "n_both_gt1": int(((f[~m] > 1) & (comp[~m] > 1)).sum())}}


def step1() -> dict:
    c3 = load(models=HEADLINE_MODELS)
    # orientation sanity: the O-H donor mean from the geometry table must track the decompose dX-H (same b minus a)
    assert np.nanmedian(np.abs(c3.dOH_donor - c3.x)[c3.OH]) < 0.1
    k = constants(fit_set(c3))
    return {"constants": k, "three_model_insample": three_model_insample(c3, k), "candidates": candidate_table(c3), "lofo": lofo(c3),
            "compensation_tracking": compensation_tracking(c3, k)}


def main(argv):
    if argv and argv[0] == "geometry":
        g = build_geometry()
        print(len(g), "structure-model rows ->", GEOM_CSV)
        return
    out = step1()
    if argv and argv[0] == "constants":
        k = out["constants"]
        print(json.dumps(k, indent=1))
        print("in-sample", {a: {b: v[b] for b in ("right", "n", "struct_rows", "other_rows")} for a, v in out["three_model_insample"].items() if isinstance(v, dict)})
        print("LOFO refined", {b: out["lofo"]["refined"][b] for b in ("right", "n", "struct_rows", "other_rows")}, "baseline", out["lofo"]["train_fold_baseline_right"],
              "AlOH3 fold", out["lofo"]["AlOH3_fold"], "C range", out["lofo"]["C_range"])
        for f, v in out["candidates"].items():
            print(f, "C", v["C"], "R2_perp", round(v["R2_perp"], 3), "insample", v["insample_headline"]["right"], "/", v["insample_headline"]["n"],
                  "struct", v["insample_headline"]["struct_rows"], "other", v["insample_headline"]["other_rows"])
        return
    c_all = load(models=None)
    out["sevenn_heldout"] = sevenn_scores(c_all, out["constants"])
    out["predeclared_in"] = "docs/predictions/P06_refined_rule.md"
    out["note"] = "post-freeze addendum; does not change the frozen F01 headline (decision 07)"
    OUT_JSON.write_text(json.dumps(out, indent=1, default=float))
    sv = out["sevenn_heldout"]
    print("SevenNet F01", sv["F01"]["right"], "/", sv["F01"]["n"], "refined", sv["refined"]["right"], "/", sv["refined"]["n"],
          "gain", sv["gain_points"], sv["clause2_note"], "verdict", sv["verdict"])
    print("secondary", {a: (v["right"], v["n"]) for a, v in sv["secondary_all_OH_rows_no_dXH_cut"].items()})


if __name__ == "__main__":
    main(sys.argv[1:])
