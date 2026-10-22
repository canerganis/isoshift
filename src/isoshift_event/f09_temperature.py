"""F09 (post-freeze addendum): score the predeclared H1 to H4 of docs/predictions/P09_temperature.md.

Inputs: frozen headline rows from rule_cv.load() (212 rows), decompose.py runs at 0, 300 and 600 K in
results/post_freeze/T{0,300,600}/, the stored pre-freeze column ddF_iso_2000K_refined_meV_atom
(results/screen_pairs_refined.csv) and the cached force constants (.cache/isoshift). Reads frozen files only.

    python -m src.isoshift_event.f09_temperature [--workers 12]
writes results/post_freeze/F09_temperature.json
"""
from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from . import rule_cv as R

ROOT = R.ROOT
PF = ROOT / "results" / "post_freeze"
CROSS_GRID = [300.0 + 25.0 * i for i in range(13)]  # 300 to 600 K, descriptive crossover location only


def headline() -> pd.DataFrame:
    c = R.load()
    h = c[(c.rmax >= R.MAIN_THR) & c.OH & (c.x.abs() >= R.MIN_DXH)].copy()
    assert len(h) == 212 and int(h.right.sum()) == 185, (len(h), int(h.right.sum()))
    return h.reset_index(drop=True)


def regression() -> dict:
    f = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    n = pd.read_csv(PF / "T300" / "decompose_pairs.csv")
    m = f.merge(n, on=["pair_id", "model"], suffixes=("_f", "_n"))
    err = float(np.abs(m.ddF_total_f - m.ddF_total_n).max())
    return {"rows_frozen": len(f), "rows_rerun": len(n), "rows_shared": len(m), "max_abs_diff_ddF_total_meV_atom": err,
            "tolerance": 1e-9, "pass": bool(len(m) == len(f) and err <= 1e-9)}


def _cache_dir(model: str, sid: str, idx) -> str | None:
    from . import refine

    r = json.loads((refine.RAW / model / f"{sid}.json").read_text())
    calc = "{name}-{model}".format(**r["calc"])
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
    key = (safe, round(r["fc_meta"]["energy_eV"], 6), round(r["fc_meta"]["volume_A3"], 4))
    return str(idx[key]) if key in idx else None


def _struct_checks(args):
    """H3 product rule on the decompose.py mesh and H4 on-site H force-constant trace for one structure."""
    model, sid, cache_dir = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import phonopy

    from isoshift import phonons as P

    from .decompose import _atoms

    ph = phonopy.load(str(Path(cache_dir) / "phonopy_params.yaml"), produce_fc=False, log_level=0)
    uc = ph.unitcell
    sym = np.array(uc.symbols)
    H = np.flatnonzero(sym == "H")
    mesh = [int(min(12, max(4, 2 * round(40.0 / l / 2)))) for l in np.linalg.norm(np.asarray(uc.cell), axis=1)]
    mH = P.make_masses(_atoms(uc), {}, default="light")
    mD = P.make_masses(_atoms(uc), {"H": "D"}, default="light")
    w2 = {}
    for iso, m in (("H", mH), ("D", mD)):
        p = P.phonopy_with_masses(ph, m)
        p.run_mesh(mesh, with_eigenvectors=False, is_mesh_symmetry=False, is_gamma_center=False)
        w2[iso] = np.abs(np.array(p.mesh.frequencies)) ** 2
    s = np.log(w2["D"] / w2["H"]).sum(axis=1)  # per q
    target = float(np.sum(np.log(mH[H] / mD[H])) * 3)
    dev = float(np.abs(s - target).max() / len(H))
    # H4: on-site 3x3 blocks of the H atoms of the primitive cell (compact or full force constants)
    fc = np.asarray(ph.force_constants)
    prim = ph.primitive
    p2s = np.asarray(prim.p2s_map)
    psym = np.array(prim.symbols)
    tr = 0.0
    for r_, s_ in enumerate(p2s):
        if psym[r_] == "H":
            row = r_ if fc.shape[0] != fc.shape[1] else s_
            tr += float(np.trace(fc[row, s_]))
    return {"model": model, "struct_id": sid, "n_H_cell": int(len(H)), "mesh": mesh, "n_q": int(len(s)),
            "product_rule_max_dev_per_H": dev, "trH_per_atom_eV_A2": tr / len(prim), "n_prim": int(len(prim))}


def _cross_one(args):
    from .decompose import _one

    model, sid, cache_dir, t = args
    r = _one((model, sid, cache_dir, t))
    return model, sid, t, r["dF_quad_meV_atom"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args(argv)
    from . import refine

    h = headline()
    # orientation: ddF and x are struct_b minus struct_a of screen_pairs_refined.csv, which is NOT always pair_id order
    ref = pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv").drop_duplicates(["pair_id", "model"], keep="last")
    ref = ref.set_index(["pair_id", "model"])
    h["sa"] = [ref.loc[(p, m), "struct_a"] for p, m in zip(h.pair_id, h.model)]
    h["sb"] = [ref.loc[(p, m), "struct_b"] for p, m in zip(h.pair_id, h.model)]
    reg = regression()
    dec = {}
    for T in (0, 300, 600):
        d = pd.read_csv(PF / f"T{T}" / "decompose_pairs.csv").set_index(["pair_id", "model"])
        k = list(zip(h.pair_id, h.model))
        h[f"str{T}"] = d.loc[k, "ddF_str"].values / h.H_per_atom.values
        h[f"perp{T}"] = d.loc[k, "ddF_perp"].values / h.H_per_atom.values
        h[f"tot{T}"] = d.loc[k, "ddF_total"].values / h.H_per_atom.values
        h[f"C{T}"] = -h[f"perp{T}"] / h[f"str{T}"]
        h[f"clean{T}"] = d.loc[k, "clean"].values.astype(bool)
        dec[T] = d
    sx = np.sign(h.x)
    acc = {f"{T}K": {"right": int((np.sign(h[f'tot{T}']) == sx).sum()), "n": 212,
                     "per_model": {m: int((np.sign(q[f'tot{T}']) == np.sign(q.x)).sum()) for m, q in h.groupby("model")},
                     "rows_clean_at_T": int(h[f"clean{T}"].sum()),
                     "mp985293_right": int((np.sign(h[f'tot{T}']) == sx)[h.pair_id.str.contains("mp-985293")].sum())}
           for T in (0, 300, 600)}

    # H1
    e1 = (h.str0.abs() >= 0.1) & (h.str600.abs() >= 0.1)
    ok1 = h.C600 < 0.6 * h.C0
    g = h[e1]
    frac1 = float(ok1[e1].mean())
    H1 = {"rule": "C(600 K) < 0.6 C(0 K) in >= 80% of rows with |ddF_str| >= 0.1 meV/H at 0 and 600 K",
          "n_eligible": int(e1.sum()), "n_ok": int(ok1[e1].sum()), "fraction": round(frac1, 4), "pass": frac1 >= 0.80,
          "per_model": {m: {"n": int(len(q)), "ok": int((q.C600 < 0.6 * q.C0).sum())} for m, q in g.groupby("model")},
          "median_C0": round(float(g.C0.median()), 3), "median_C300": round(float(g.C300.median()), 3),
          "median_C600": round(float(g.C600.median()), 3),
          "median_ratio_C600_over_C0": round(float((g.C600 / g.C0).median()), 3),
          "descriptive_not_scored": {"n_C600_lt_C0": int((g.C600 < g.C0).sum()), "n_C300_lt_C0": int((g.C300 < g.C0).sum()),
                                     "ratio_C600_over_C0_quartiles": [round(float(q), 3) for q in (g.C600 / g.C0).quantile([0.25, 0.5, 0.75])],
                                     "n_ratio_lt_0p7": int((g.C600 < 0.7 * g.C0).sum()),
                                     "n_C0_negative": int((g.C0 < 0).sum())}}

    # H2
    s = h[h.pair_id.str.contains("mp-985293")].copy()
    s["str0_ok"] = np.sign(s.str0) == np.sign(s.x)
    s["str600_ok"] = np.sign(s.str600) == np.sign(s.x)
    s["C0_gt1"] = s.C0 > 1
    s["C600_lt1"] = s.C600 < 1
    s["all_ok"] = s.str0_ok & s.str600_ok & s.C0_gt1 & s.C600_lt1
    H2 = {"rule": "all 28 mp-985293 rows: ddF_str F01 sign at 0 and 600 K, C(0 K) > 1, C(600 K) < 1",
          "n_rows": int(len(s)), "n_all_ok": int(s.all_ok.sum()),
          "n_str0_ok": int(s.str0_ok.sum()), "n_str600_ok": int(s.str600_ok.sum()),
          "n_C0_gt1": int(s.C0_gt1.sum()), "n_C600_lt1": int(s.C600_lt1.sum()), "pass": bool(len(s) == 28 and s.all_ok.all()),
          "rows": [{"pair_id": r.pair_id, "model": r.model, "x_mA": round(r.x, 2),
                    **{k: round(float(getattr(r, k)), 4) for k in ("str0", "perp0", "tot0", "C0", "str300", "C300",
                                                                   "str600", "perp600", "tot600", "C600")},
                    "all_ok": bool(r.all_ok)} for r in s.itertuples()]}

    # H3 and H4 structure checks
    idx = refine._cache_index()
    structs = set()
    for p, m in zip(h.pair_id, h.model):
        a, b = p.split("__")
        structs.update({(m, a), (m, b)})
    jobs = [(m, sid, _cache_dir(m, sid, idx)) for m, sid in sorted(structs)]
    missing = [j[:2] for j in jobs if j[2] is None]
    jobs = [j for j in jobs if j[2] is not None]
    cross_structs = sorted({(m, sid) for p, m in zip(s.pair_id, s.model) for sid in p.split("__")})
    cjobs = [(m, sid, _cache_dir(m, sid, idx), t) for m, sid in cross_structs for t in CROSS_GRID]
    with ProcessPoolExecutor(args.workers) as ex:
        st = {(r["model"], r["struct_id"]): r for r in ex.map(_struct_checks, jobs, chunksize=2)}
        cr = list(ex.map(_cross_one, cjobs, chunksize=2))

    h3_rows = [st[k] for k in cross_structs]
    bad3 = [{"model": r["model"], "struct_id": r["struct_id"], "dev": r["product_rule_max_dev_per_H"]}
            for r in h3_rows if r["product_rule_max_dev_per_H"] > 1e-3]
    all_dev = [r["product_rule_max_dev_per_H"] for r in st.values()]
    H3 = {"rule": "|sum ln(w_D^2/w_H^2) - 3 n_H ln(m_H/m_D)| / n_H <= 1e-3 at every q, mp-985293 pair structures, every model",
          "n_structure_models": len(h3_rows), "n_fail": len(bad3), "failures": bad3,
          "max_dev_per_H": max(r["product_rule_max_dev_per_H"] for r in h3_rows), "pass": not bad3,
          "all_headline_structures_max_dev_per_H": max(all_dev), "all_headline_structures_n": len(all_dev)}

    # H4
    h["dd2000"] = [ref.loc[(p, m), "ddF_iso_2000K_refined_meV_atom"] for p, m in zip(h.pair_id, h.model)]
    h["dTr"] = [st[(m, b)]["trH_per_atom_eV_A2"] - st[(m, a)]["trH_per_atom_eV_A2"] for m, a, b in zip(h.model, h.sa, h.sb)]
    ok4 = np.sign(h.dd2000) == -np.sign(h.dTr)
    ok4_600 = np.sign(h.tot600) == -np.sign(h.dTr)
    tr_vs_x = np.sign(h.dTr) == -np.sign(h.x)
    H4 = {"rule": "sign(ddF(2000 K)) = -sign(dTr K_H per atom) in >= 95% of 212 headline rows (>= 202)",
          "n": 212, "n_agree": int(ok4.sum()), "fraction": round(float(ok4.mean()), 4), "pass": int(ok4.sum()) >= 202,
          "per_model": {m: {"n": int(len(q)), "agree": int(ok4[q.index].sum())} for m, q in h.groupby("model")},
          "disagreeing_rows": [{"pair_id": p, "model": m, "dTr_eV_A2_per_atom": round(float(t), 5), "ddF2000_meV_atom": float(d)}
                               for p, m, t, d, o in zip(h.pair_id, h.model, h.dTr, h.dd2000, ok4) if not o],
          "descriptive_not_scored": {"agree_with_decompose_600K": int(ok4_600.sum()),
                                     "trace_larger_in_shorter_OH_phase": int(tr_vs_x.sum()),
                                     "mp985293_rows_agree": int(ok4[h.pair_id.str.contains("mp-985293")].sum())},
          "missing_cache": missing}

    # descriptive: crossover temperature of the total for each mp-985293 row (linear interpolation, 25 K grid)
    F = {(m, sid, t): v for m, sid, t, v in cr}
    xrows = []
    for r in s.itertuples():
        a, b = r.sa, r.sb
        y = [(F[(r.model, b, t)] - F[(r.model, a, t)]) / r.H_per_atom * np.sign(r.x) for t in CROSS_GRID]
        assert abs(y[0] - r.tot300 * np.sign(r.x)) < 1e-6, (r.pair_id, r.model)  # same orientation as the 300 K run
        tc = None
        for i in range(len(y) - 1):
            if y[i] <= 0 < y[i + 1]:
                tc = CROSS_GRID[i] + 25.0 * (-y[i]) / (y[i + 1] - y[i])
                break
        if tc is None and y[0] > 0:
            tc = "below 300 K"
        xrows.append({"pair_id": r.pair_id, "model": r.model, "T_cross_K": round(tc, 0) if isinstance(tc, float) else tc})
    cross = {"note": "descriptive, not predeclared; F01-signed ddF_total from decompose.py on a 25 K grid, 300 to 600 K",
             "rows": xrows}

    out = {"status": "post-freeze addendum; frozen F01 headline (decision 07) unchanged",
           "prediction_file": "docs/predictions/P09_temperature.md", "regression_300K": reg,
           "headline_accuracy_decompose": acc, "H1": H1, "H2": H2, "H3": H3, "H4": H4, "mp985293_crossover": cross}
    (PF / "F09_temperature.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"regression 300 K: {reg['rows_shared']}/{reg['rows_frozen']} rows, max |d ddF_total| = "
          f"{reg['max_abs_diff_ddF_total_meV_atom']:.3g} meV/atom, pass={reg['pass']}")
    print("accuracy", {k: v["right"] for k, v in acc.items()})
    for k in ("H1", "H2", "H3", "H4"):
        print(k, "PASS" if out[k]["pass"] else "FAIL")


if __name__ == "__main__":
    main()
