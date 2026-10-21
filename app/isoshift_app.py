import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="IsoShift")

with app.setup:
    import json
    import os
    from pathlib import Path

    import matplotlib
    import numpy as np
    import pandas as pd

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    APP_DIR = Path(__file__).resolve().parent
    REPO = APP_DIR.parent
    MODELS = ["mace", "orb", "mattersim", "sevenn"]
    TEMPS = np.arange(0, 1001, 5, dtype=float)

    def data_root(app_dir=APP_DIR, repo=REPO):
        """app/demo_data if present (same layout as the repo root), else the repo."""
        env = os.environ.get("ISOSHIFT_DATA")
        if env:
            return Path(env)
        demo = Path(app_dir) / "demo_data"
        return demo if demo.is_dir() else Path(repo)

    def _csv(path):
        path = Path(path)
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path, dtype={"struct_id": str, "pair_id": str,
                                            "struct_a": str, "struct_b": str})
        except Exception:
            return pd.DataFrame()

    def load_data(root):
        root = Path(root)
        return dict(
            root=root,
            pairs=_csv(root / "results" / "screen_pairs.csv"),
            structs=_csv(root / "results" / "screen_structures.csv"),
            meta_pairs=_csv(root / "data" / "isoshift" / "pairs.csv"),
            meta_structs=_csv(root / "data" / "isoshift" / "structures.csv"),
            validation=_csv(root / "results" / "validation" / "volume_isotope.csv"),
            dec_pairs=_csv(root / "results" / "decompose_pairs.csv"),
            dec_structs=_csv(root / "results" / "decompose_structures.csv"),
            refined=_csv(root / "results" / "screen_pairs_refined.csv"),
            bench=_csv(root / "results" / "benchmark" / "summary.csv"),
            stretch=read_json(root / "results" / "stretch_check_summary.json"),
            stretch_check=_csv(root / "results" / "stretch_check.csv"),
            f01_cv=read_json(root / "results" / "F01_cv.json"),
        )

    def read_json(path):
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            return {}

    def f01_frame(data):
        """Clean covalent rows with per-H x (mA), y (meV/H) and the max X-H length of the pair's two structures."""
        dp, ds, rf, mp = data["dec_pairs"], data["dec_structs"], data["refined"], data["meta_pairs"]
        if not len(dp) or not len(ds) or not len(rf):
            return pd.DataFrame()
        ok = dp["clean"].astype(str).str.lower().eq("true") & dp["covalent_XH"].astype(str).str.lower().eq("true")
        d = dp[ok].drop(columns=["formula"], errors="ignore")
        d = d.merge(rf[["pair_id", "model", "struct_a", "struct_b"]].drop_duplicates(["pair_id", "model"]),
                    on=["pair_id", "model"], how="inner")
        xh = ds.drop_duplicates(["model", "struct_id"]).set_index(["model", "struct_id"])["XH_mean_A"].to_dict()
        d["XH_a"] = [xh.get((m, a), np.nan) for m, a in zip(d.model, d.struct_a)]
        d["XH_b"] = [xh.get((m, b), np.nan) for m, b in zip(d.model, d.struct_b)]
        d["XH_max"] = d[["XH_a", "XH_b"]].max(axis=1)
        d["x_mA"] = d["dXH_mean_A"] * 1000.0
        d["y_total"] = d["ddF_total"] / d["H_per_atom"]
        d["y_str"] = d["ddF_str"] / d["H_per_atom"]
        d["y_perp"] = d["ddF_perp"] / d["H_per_atom"]
        fm = mp.drop_duplicates("pair_id").set_index("pair_id")["formula"].to_dict() if len(mp) else {}
        d["formula"] = d.pair_id.map(fm).fillna("?")
        sc = data.get("stretch_check")
        if sc is not None and len(sc) and "struct_id" in sc:
            oh = set(sc["struct_id"].astype(str))
            d["OH"] = [(a in oh) or (b in oh) for a, b in zip(d.struct_a, d.struct_b)]
        else:
            d["OH"] = np.nan  # O-H population not available (results/stretch_check.csv missing)
        return d.dropna(subset=["x_mA", "y_total", "XH_max"]).reset_index(drop=True)

    def _fold_majority(y, family):
        """Leave-one-formula-out constant-sign baseline: for each row, the majority sign of y over the other formulas."""
        y = np.asarray(y, float)
        family = np.asarray(family)
        out = np.zeros(len(y))
        for fam in np.unique(family):
            te = family == fam
            out[te] = 1.0 if np.sign(y[~te]).sum() >= 0 else -1.0
        return out

    def sign_rule(d, threshold, x_min=5.0, y_min=None, oh_only=False, weak=False):
        """(right, n, baseline) on one side of the regime threshold (max X-H of the pair, strong = >=).
        Eligible rows have |x| >= x_min mA; y_min cuts on |ddF| (meV/H, the all-covalent signal cut) and oh_only keeps
        O-H pairs. Rule: sign(y) == sign(x). Baseline: leave-one-formula-out majority sign of y over the same side."""
        if not len(d):
            return 0, 0, 0
        fit = d[(d.XH_max < threshold) if weak else (d.XH_max >= threshold)]
        if oh_only:
            fit = fit[fit["OH"].astype(bool)]
        if y_min is not None:
            fit = fit[fit.y_total.abs() > y_min]
        if not len(fit):
            return 0, 0, 0
        base = _fold_majority(fit.y_total, fit.formula)
        el = (fit.x_mA.abs() >= x_min).values
        g = fit[el]
        right = int((np.sign(g.y_total) == np.sign(g.x_mA)).sum())
        return right, len(g), int((base[el] == np.sign(g.y_total.values)).sum())

    def structure_curves(data, struct_id, model):
        """(F_H, F_D) in meV/atom on TEMPS, or None. CSV JSON columns first, raw JSON second."""
        s = data["structs"]
        if len(s) and "F_H_meV_atom_json" in s:
            row = s[(s.struct_id == struct_id) & (s.model == model)]
            if len(row) and isinstance(row.iloc[0]["F_H_meV_atom_json"], str):
                r = row.iloc[0]
                return (np.array(json.loads(r["F_H_meV_atom_json"]), float),
                        np.array(json.loads(r["F_D_meV_atom_json"]), float))
        raw = Path(data["root"]) / "results" / "raw" / "screen" / model / f"{struct_id}.json"
        if raw.exists():
            try:
                r = json.loads(raw.read_text(encoding="utf-8"))
                n = float(r["n_atoms"])
                return tuple(np.array(r["variants"][k]["F_eV_cell"], float) * 1000 / n for k in ("H", "D"))
            except Exception:
                return None
        return None

    def dG_curves(dE, fa, fb):
        """dG_X(T) = dE + F_X(b) - F_X(a) for X in H, D (meV/atom). fa, fb = (F_H, F_D)."""
        return tuple(dE + fb[i] - fa[i] for i in (0, 1))

    def ddF_curve(fa, fb):
        """ddF_iso = [F_D(b) - F_H(b)] - [F_D(a) - F_H(a)] (M01 eq. 2)."""
        return (fb[1] - fb[0]) - (fa[1] - fa[0])

    def crossings(temps, g):
        """Sign-change roots of g(T), linear interpolation, as [(T_K, '+-' or '-+')]."""
        temps = np.asarray(temps, float)
        g = np.asarray(g, float)
        out = []
        for i in range(len(g) - 1):
            if g[i] * g[i + 1] < 0:
                t = temps[i] - g[i] * (temps[i + 1] - temps[i]) / (g[i + 1] - g[i])
                out.append((float(t), "+-" if g[i] > 0 else "-+"))
            elif g[i] == 0 and i > 0 and g[i - 1] * g[i + 1] < 0:
                out.append((float(temps[i]), "+-" if g[i - 1] > 0 else "-+"))
        return out

    def pair_label(meta_pairs, meta_structs, pair_id):
        formula, sa, sb = "", "", ""
        if len(meta_pairs):
            r = meta_pairs[meta_pairs.pair_id == pair_id]
            if len(r):
                formula = str(r.iloc[0].get("formula", ""))
                sa, sb = str(r.iloc[0]["struct_a"]), str(r.iloc[0]["struct_b"])

        def spg(s):
            if len(meta_structs) and s and "spg" in meta_structs:
                r = meta_structs[meta_structs.struct_id == s]
                if len(r):
                    return str(r.iloc[0]["spg"])
            return "?"

        if formula:
            return f"{formula}  ({spg(sa)} / {spg(sb)})  {pair_id}"
        return pair_id

    def split_flags(value):
        return [f for f in str(value if isinstance(value, str) else "").split(";") if f]

    def candidate_table(pairs, meta_pairs=None, meta_structs=None):
        """One row per pair: median |ddF_iso(300 K)| over models, sign agreement count."""
        cols = ["pair", "formula", "n_models", "median_abs_ddF_300K_meV_atom", "median_ddF_300K_meV_atom",
                "sign_agree", "dE_median_meV_atom", "flagged"]
        if pairs is None or not len(pairs) or "ddF_iso_300K_meV_atom" not in pairs:
            return pd.DataFrame(columns=cols)
        rows = []
        for pid, g in pairs.groupby("pair_id"):
            v = pd.to_numeric(g["ddF_iso_300K_meV_atom"], errors="coerce").dropna()
            if v.empty:
                continue
            pos, neg = int((v > 0).sum()), int((v < 0).sum())
            de = pd.to_numeric(g["dE_static_meV_atom"], errors="coerce").dropna() \
                if "dE_static_meV_atom" in g else pd.Series(dtype=float)
            fl = set(f for x in g["flags"] for f in split_flags(x)) if "flags" in g else set()
            formula = ""
            if meta_pairs is not None and len(meta_pairs):
                m = meta_pairs[meta_pairs.pair_id == pid]
                formula = str(m.iloc[0]["formula"]) if len(m) else ""
            rows.append({"pair": pid, "formula": formula, "n_models": len(v),
                         "median_abs_ddF_300K_meV_atom": float(np.median(np.abs(v))),
                         "median_ddF_300K_meV_atom": float(np.median(v)),
                         "sign_agree": f"{max(pos, neg)}/{len(v)}",
                         "dE_median_meV_atom": float(np.median(de)) if len(de) else np.nan,
                         "flagged": ";".join(sorted(f for f in fl if "quarantined" in f
                                                    or "above_600K" in f or "anharm" in f))})
        df = pd.DataFrame(rows, columns=cols)
        return df.sort_values("median_abs_ddF_300K_meV_atom", ascending=False).reset_index(drop=True)


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # IsoShift
    For hydrogen compounds with two polymorphs, IsoShift computes harmonic free energies with H and with D from the same
    ML-potential force constants (four models), and reports how deuteration shifts the relative stability, ddF_iso(T) in meV/atom.
    """)
    return


@app.cell
def _():
    data = load_data(data_root())
    return (data,)


@app.cell
def _(data, mo):
    mo.md(f"Data root: `{data['root']}`  |  pair rows: {len(data['pairs'])}  |  structure rows: {len(data['structs'])}")
    return


@app.cell
def _(mo):
    mo.md("## Validation: volume isotope effect")
    return


@app.cell
def _(data, mo):
    v = data["validation"]
    if not len(v):
        _out = mo.md("_No validation data found._")
    else:
        _cases = sorted(v.case.unique())
        _fig, _axes = plt.subplots(1, len(_cases), figsize=(4.2 * len(_cases), 3.6), squeeze=False)
        for _ax, _c in zip(_axes[0], _cases):
            _d = v[v.case == _c]
            for _m, _g in _d.groupby("model"):
                # one point per T: imaginary-mode treatments (if present) become an error bar
                _s = _g.groupby("T_K").VIE_pct.agg(["median", "min", "max"]).sort_index()
                _ax.errorbar(_s.index, _s["median"], yerr=[_s["median"] - _s["min"], _s["max"] - _s["median"]],
                             marker="o", ms=4, capsize=3, label=_m)
            _e = _d.dropna(subset=["exp_VIE_pct"])
            if len(_e):
                _ee = _e.groupby("T_K").exp_VIE_pct.first()
                _ax.scatter(_ee.index, _ee.values, marker="*", s=160, c="k", zorder=5, label="measured")
            _ax.set_title(_c)
            _ax.set_xlabel("T (K)")
            _ax.set_ylabel("V_H/V_D - 1 (%)")
            _ax.grid(alpha=0.3)
        _axes[0][0].legend(fontsize=8)
        _fig.tight_layout()
        _out = _fig
    _out
    return


@app.cell
def _(mo):
    mo.md("## Pair explorer")
    return


@app.cell
def _(data, mo):
    _p = data["pairs"]
    _ids = sorted(_p.pair_id.unique()) if len(_p) else []
    _labels = {pair_label(data["meta_pairs"], data["meta_structs"], i): i for i in _ids}
    pair_dd = mo.ui.dropdown(options=_labels, value=next(iter(_labels), None), label="Pair")
    model_ms = mo.ui.multiselect(options=MODELS, value=MODELS, label="Models")
    offset = mo.ui.slider(-30, 30, step=0.5, value=0, label="Static dE offset (meV/atom)", show_value=True)
    mo.vstack([pair_dd, model_ms, offset])
    return model_ms, offset, pair_dd


@app.cell
def _(data, mo, model_ms, offset, pair_dd):
    pid = pair_dd.value
    if pid is None:
        _out = mo.md("_No pairs available._")
    else:
        _rows = data["pairs"][(data["pairs"].pair_id == pid) & data["pairs"].model.isin(model_ms.value)]
        _fig, (_a1, _a2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True,
                                        gridspec_kw={"height_ratios": [3, 2]})
        _txt, _dds = [], []
        for _i, (_, _r) in enumerate(_rows.iterrows()):
            _fa = structure_curves(data, _r["struct_a"], _r["model"])
            _fb = structure_curves(data, _r["struct_b"], _r["model"])
            _fl = split_flags(_r.get("flags"))
            if _fa is None or _fb is None or pd.isna(_r.get("dE_static_meV_atom")):
                _txt.append(f"**{_r['model']}**: no curves in the published CSVs and no `results/raw` cache in this "
                            f"checkout ({'; '.join(_fl) or 'missing'})")
                continue
            _dE = float(_r["dE_static_meV_atom"]) + offset.value
            _gh, _gd = dG_curves(_dE, _fa, _fb)
            _col = f"C{_i}"
            _a1.plot(TEMPS, _gh, color=_col, ls="-", label=f"{_r['model']} H")
            _a1.plot(TEMPS, _gd, color=_col, ls="--", label=f"{_r['model']} D")
            _ch, _cd = crossings(TEMPS, _gh), crossings(TEMPS, _gd)
            _a1.scatter([t for t, _ in _ch], [0] * len(_ch), color=_col, marker="o", zorder=5)
            _a1.scatter([t for t, _ in _cd], [0] * len(_cd), color=_col, marker="s", zorder=5)
            _dd = ddF_curve(_fa, _fb)
            _dds.append(_dd)
            _a2.plot(TEMPS, _dd, color=_col, label=_r["model"])
            _f = lambda cs: ", ".join(f"{t:.0f} K" for t, _ in cs) or "none"
            _txt.append(f"**{_r['model']}**: T_c^H = {_f(_ch)}; T_c^D = {_f(_cd)}; "
                        f"ddF_iso(300 K) = {np.interp(300, TEMPS, _dd):+.3f} meV/atom; "
                        f"flags: {'; '.join(_fl) or 'none'}")
        if _dds:
            _arr = np.array(_dds)
            _a2.fill_between(TEMPS, _arr.min(0), _arr.max(0), color="gray", alpha=0.2, label="model band")
        _a1.axhline(0, color="k", lw=0.6)
        _a2.axhline(0, color="k", lw=0.6)
        _a1.axvline(600, color="r", lw=0.6, ls=":")
        _a1.set_ylabel("dG = dE + F(b) - F(a)  (meV/atom)")
        _a2.set_ylabel("ddF_iso  (meV/atom)")
        _a2.set_xlabel("T (K)")
        _a1.set_title(f"{pid}  (dE offset {offset.value:+.1f} meV/atom; solid H, dashed D; dots = T_c)")
        _a1.legend(fontsize=7, ncol=2)
        _a2.legend(fontsize=7, ncol=3)
        for _a in (_a1, _a2):
            _a.grid(alpha=0.3)
        _fig.tight_layout()
        _out = mo.vstack([_fig, mo.md("\n\n".join(_txt))])
    _out
    return


@app.cell
def _(mo):
    mo.md("## Candidates: ranked by median |ddF_iso(300 K)|")
    return


@app.cell
def _(data, mo):
    _t = candidate_table(data["pairs"], data["meta_pairs"], data["meta_structs"])
    mo.ui.table(_t, selection=None, page_size=15)
    return


@app.cell
def _(mo):
    mo.md("## Extra views (all numbers here are **precomputed** from cached results)")
    return


@app.cell
def _(data, mo):
    f01 = f01_frame(data)
    thr = mo.ui.slider(0.97, 1.03, step=0.005, value=0.99, label="Strong-regime threshold, max X-H (A)", show_value=True)
    f01_models = mo.ui.multiselect(options=MODELS, value=MODELS, label="Models")
    _pops = {"O-H pairs, no cut on ddF (headline)": "oh",
             "All covalent X-H, signal cut |ddF| > 0.1 meV/H": "cov"}
    pop = mo.ui.dropdown(options=_pops, value="O-H pairs, no cut on ddF (headline)", label="Population")
    _fl = sorted(f01.formula.unique()) if len(f01) else []
    hl = mo.ui.dropdown(options=["(none)"] + _fl, value="(none)", label="Highlight formula")
    return f01, f01_models, hl, pop, thr


@app.cell
def _(f01, f01_models, hl, mo, pop, thr):
    if not len(f01):
        f01_tab = mo.md("_No decomposition data found._")
    else:
        _d = f01[f01.model.isin(f01_models.value)].copy()
        _d["strong"] = _d.XH_max >= thr.value
        _oh = pop.value == "oh" and bool(f01["OH"].notna().all())
        if pop.value == "oh" and not _oh:
            _pop_note = " _(O-H flags unavailable here, showing all covalent with signal cut)_"
        else:
            _pop_note = ""
        _kw = dict(oh_only=True) if _oh else dict(y_min=0.1)
        _k, _n, _b = sign_rule(_d, thr.value, **_kw)
        _kw_, _nw, _bw = sign_rule(_d, thr.value, weak=True, **_kw)
        _label = ("O-H pairs, |dX-H| >= 5 mA, no cut on ddF" if _oh
                  else "all covalent X-H, |dX-H| >= 5 mA, |ddF| > 0.1 meV/H (signal cut)")
        _fig, (_a1, _a2) = plt.subplots(1, 2, figsize=(11, 4.2))
        for _flag, _col, _lab in ((False, "tab:blue", "weak"), (True, "tab:red", "strong")):
            _g = _d[_d.strong == _flag]
            _a1.scatter(_g.x_mA, _g.y_total, s=14, c=_col, alpha=0.6, label=f"{_lab} regime (n={len(_g)})")
        _a2.scatter(_d.x_mA, _d.y_str, s=12, c="tab:orange", alpha=0.6, label="stretch ddF_str/H")
        _a2.scatter(_d.x_mA, _d.y_perp, s=12, c="tab:green", alpha=0.6, label="bend/libration ddF_perp/H")
        if hl.value != "(none)":
            _h = _d[_d.formula == hl.value]
            _a1.scatter(_h.x_mA, _h.y_total, s=90, facecolors="none", edgecolors="k", lw=1.5, label=hl.value)
            _a2.scatter(_h.x_mA, _h.y_str, s=90, facecolors="none", edgecolors="k", lw=1.5, label=hl.value)
            _a2.scatter(_h.x_mA, _h.y_perp, s=90, facecolors="none", edgecolors="k", lw=1.5)
        for _a, _yl in ((_a1, "ddF_total / H  (meV per H)"), (_a2, "contribution per H (meV)")):
            _a.axhline(0, color="k", lw=0.6)
            _a.axvline(0, color="k", lw=0.6)
            _a.set_xlabel("d(X-H) mean, b minus a (mÅ)")
            _a.set_ylabel(_yl)
            _a.grid(alpha=0.3)
            _a.legend(fontsize=8)
        _a1.set_title("F01: isotope shift vs bond-length change (precomputed)")
        _a2.set_title("stretch vs bend/libration (precomputed)")
        _fig.tight_layout()
        f01_tab = mo.vstack([
            mo.vstack([thr, f01_models, pop, hl]),
            mo.md(f"**Sign rule right: {_k} of {_n}** (strong regime, {_label}) "
                  f"| leave-one-formula-out constant-sign baseline: {_b} of {_n} "
                  f"| weak side: {_kw_} of {_nw} _(precomputed)_{_pop_note}"),
            _fig,
            mo.md("Default: 123 of 130 O-H model evaluations (baseline 82 of 130) at the 0.99 Å model-derived threshold with all three models; "
                  "the all-covalent signal-cut population is a labelled alternative. "
                  "Deuteration favours the polymorph with the shorter O-H bonds once H bonds are moderate to strong. "
                  "The stretch term is about half cancelled by bend/libration "
                  "(see `docs/findings/F01-xh-length-rule.md`)."),
        ])
    return (f01_tab,)


@app.cell
def _(data, mo):
    _b = data["bench"]
    if not len(_b):
        _bench = mo.md("_No benchmark summary found._")
    else:
        _cols = [c for c in ("dzpe_MAE_meV", "dF300_MAE_meV", "stretch_MAE_cm1") if c in _b]
        _lab = _b.model.astype(str) + "\n" + _b.setting.astype(str)
        _fig, _axes = plt.subplots(1, len(_cols), figsize=(4.2 * len(_cols), 3.8), squeeze=False)
        for _ax, _c in zip(_axes[0], _cols):
            _ax.bar(range(len(_b)), _b[_c])
            _ax.set_xticks(range(len(_b)))
            _ax.set_xticklabels(_lab, rotation=60, ha="right", fontsize=7)
            _ax.set_title(_c + " (precomputed)")
            _ax.grid(alpha=0.3, axis="y")
        _fig.tight_layout()
        _bench = mo.vstack([mo.md("### Benchmark summary (precomputed)"), mo.ui.table(_b, selection=None), _fig])
    _st = data["stretch"]
    _rows = []
    for _m, _v in (_st.get("windowed", {}).get("main_2.50-2.80", {}) or {}).items():
        if isinstance(_v, dict):
            _rows.append({"model": _m, "n_donors": _v.get("n_donors"), "f_OLS (2.50-2.80 A)": _v.get("f_OLS"),
                          "f_TheilSen": _v.get("f_TheilSen"), "f_OLS_boot95": str(_v.get("f_OLS_boot95"))})
    if not _rows:
        for _m, _v in _st.items():
            if isinstance(_v, dict) and "n" in _v:
                _rows.append({"model": _m, **{k: v for k, v in _v.items()}})
    _items = [_bench]
    if _rows:
        _items += [mo.md("### Stretch check (precomputed)"), mo.ui.table(pd.DataFrame(_rows), selection=None)]
    _img = Path(data["root"]) / "figures" / "fig5_stretch_check.png"
    if not _img.exists():
        _img = REPO / "figures" / "fig5_stretch_check.png"
    if _img.exists():
        _items.append(mo.image(src=_img.read_bytes()))
    bench_tab = mo.vstack(_items)
    return (bench_tab,)


@app.cell
def _(bench_tab, f01_tab, mo):
    mo.ui.tabs({"F01 isotope rule": f01_tab, "Benchmark & atlas": bench_tab})
    return


if __name__ == "__main__":
    app.run()
