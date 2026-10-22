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
            experimental=_csv(resolve(root, "data/isoshift/experimental.csv")),
            lit=_csv(resolve(root, "data/isoshift/validation.csv")),
            bond=read_jsonl(resolve(root, "logs/bond_queries.jsonl")),
            gate_text=read_text(resolve(root, "docs/decisions/01-gate.md")),
        )

    def resolve(root, rel):
        """root/rel if it exists, else the same path in the repo (demo_data folders only carry the CSVs)."""
        p = Path(root) / rel
        return p if p.exists() else REPO / rel

    def read_text(path):
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception:
            return ""

    def read_jsonl(path):
        """[(line_number, dict)] for every parsable line of a JSONL file (line numbers are 1-based)."""
        out = []
        for i, line in enumerate(read_text(path).splitlines(), 1):
            try:
                out.append((i, json.loads(line)))
            except Exception:
                continue
        return out

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

    DEFAULT_PAIR = "mp-23807__mp-625152"
    CARD_URL = "https://github.com/canerganis/isoshift/blob/main/docs/findings/CARD-AlOOH.md"
    STRONG_XH_A = 0.99
    MIN_DXH_A = 0.005  # F01 eligibility: |d(X-H)| >= 5 mA

    def _sgn(x):
        return 0 if (x is None or pd.isna(x) or x == 0) else (1 if x > 0 else -1)

    def _sgn_txt(n):
        return {1: "+", -1: "-", 0: "0"}[n]

    def pair_options(data):
        """{label: pair_id} for the pairs in screen_pairs_refined.csv, labelled from data/isoshift/pairs.csv."""
        rf = data["refined"]
        ids = sorted(rf.pair_id.unique()) if len(rf) else []
        return {pair_label(data["meta_pairs"], data["meta_structs"], i): i for i in ids}

    def _struct_row(data, sid):
        out = {"struct_id": sid, "spg": "?", "source": "?", "experimental": "?", "evidence": ""}
        ms = data["meta_structs"]
        if len(ms):
            r = ms[ms.struct_id == sid]
            if len(r):
                out["spg"] = str(r.iloc[0].get("spg", "?"))
                out["source"] = str(r.iloc[0].get("source", "?"))
        ex = data.get("experimental")
        if ex is not None and len(ex):
            r = ex[ex.struct_id == sid]
            if len(r):
                out["experimental"] = str(r.iloc[0]["experimental"])
                out["evidence"] = str(r.iloc[0]["evidence"])
        return out

    def pair_report(data, pid):
        """Everything the 'Check a pair' tab shows for one pair (all precomputed; None if the pair is not in the refined CSV)."""
        rf = data["refined"]
        rows = rf[rf.pair_id == pid] if len(rf) else rf
        if not len(rows):
            return None
        dp, ds = data["dec_pairs"], data["dec_structs"]
        out = []
        for m in MODELS:
            r = rows[rows.model == m]
            if not len(r):
                continue
            r = r.iloc[0]
            sa, sb = str(r["struct_a"]), str(r["struct_b"])

            def xh(sid):
                if not len(ds):
                    return np.nan, False
                q = ds[(ds.model == m) & (ds.struct_id == sid)]
                if not len(q):
                    return np.nan, False
                return float(q.iloc[0]["XH_mean_A"]), str(q.iloc[0]["covalent_XH"]).lower() == "true"

            (xa, ca), (xb, cb) = xh(sa), xh(sb)
            d = dp[(dp.pair_id == pid) & (dp.model == m)] if len(dp) else dp
            dxh = xb - xa if (ca and cb) else np.nan
            ddf_str = ddf_perp = np.nan
            if len(d):
                d = d.iloc[0]
                ddf_str, ddf_perp = float(d["ddF_str"]), float(d["ddF_perp"])
                if not (ca and cb) and pd.notna(d.get("dXH_mean_A")):
                    dxh = float(d["dXH_mean_A"])
            cov = [x for x, c in ((xa, ca), (xb, cb)) if c and pd.notna(x)]
            if not cov:
                regime = "no covalent X-H"
            else:
                regime = "strong" if max(cov) >= STRONG_XH_A else "weak"
            rule = _sgn(dxh) if (pd.notna(dxh) and abs(dxh) >= MIN_DXH_A) else 0
            ddf = float(r["ddF_iso_300K_meV_atom"]) if pd.notna(r["ddF_iso_300K_meV_atom"]) else np.nan
            msign = _sgn(ddf)
            if not rule or not msign:
                agree = "n/a"
            else:
                agree = "yes" if rule == msign else "no"
            out.append({
                "model": m, "ddF_iso 300 K (meV/atom)": ddf,
                "ddF_iso 300 K (meV/H)": float(r["ddF_iso_300K_meV_H"]) if pd.notna(r["ddF_iso_300K_meV_H"]) else np.nan,
                "mean X-H a (A)": xa, "mean X-H b (A)": xb,
                "d(X-H) b minus a (mA)": dxh * 1000 if pd.notna(dxh) else np.nan,
                "regime": regime, "rule call": _sgn_txt(rule), "model sign": _sgn_txt(msign), "agree": agree,
                "stretch (meV/atom)": ddf_str, "bend/libration (meV/atom)": ddf_perp,
                "flags": "; ".join(split_flags(r.get("flags"))) or "none",
            })
        r0 = rows.iloc[0]
        sa, sb = str(r0["struct_a"]), str(r0["struct_b"])
        mp = data["meta_pairs"]
        formula = ""
        if len(mp):
            q = mp[mp.pair_id == pid]
            formula = str(q.iloc[0]["formula"]) if len(q) else ""
        return {"pair_id": pid, "formula": formula, "a": _struct_row(data, sa), "b": _struct_row(data, sb),
                "models": pd.DataFrame(out)}

    BRUCITE_STEPS = [
        "Bond query on deuteration and hydroxide volume returns Horita 2010 and Chakoumakos 2013.",
        "Stage 1 sweep worker reports \"about 0.3%, sign D smaller\" without a quote.",
        "Stage 2 agent finds the abstract sentence (0.31% larger volume for Mg(OH)2 at room temperature) "
        "and records DOI and quote.",
        "QHA with four models and four imaginary-mode treatments gives the computed volume isotope effect.",
        "Board ruling (01-gate): brucite sign right in 4/4 models under every treatment, tier B passes.",
    ]
    AUDIT = {"sweep_items": 11, "ok_single_pass": 9, "survived": 2}

    def bond_hits(bond, needles=("brucite", "mg(oh)2")):
        """[(line_number, row)] of the Bond log whose text mentions any needle (case-insensitive)."""
        return [(i, r) for i, r in bond if any(n in json.dumps(r, ensure_ascii=False).lower() for n in needles)]

    def _bond_table(hits):
        rows = []
        for i, r in hits:
            kept = r.get("kept")
            rows.append({"log line": i, "agent": r.get("agent", "sweep:" + str(r.get("sweep", ""))),
                         "query": r.get("query", ""), "n_results": r.get("n_results", ""),
                         "kept": "; ".join(kept)[:200] if isinstance(kept, list) else ""})
        return pd.DataFrame(rows, columns=["log line", "agent", "query", "n_results", "kept"])

    def brucite_trace(data):
        hits = bond_hits(data["bond"])
        lit = data["lit"]
        if len(lit):
            m = lit["system"].astype(str).str.contains("brucite", case=False)
            m &= lit["doi"].notna() & lit["quote"].notna() & lit["derived_isotope_effect_pct"].notna()
            lit = lit[m][["system", "observable", "doi", "source_location", "quote", "derived_isotope_effect_pct"]]
        v = data["validation"]
        if len(v):
            v = v[(v.case == "brucite") & (v.T_K == 290)][["model", "treatment", "T_K", "VIE_pct", "in_range"]]
        gate = [ln.strip() for ln in str(data.get("gate_text", "")).splitlines()
                if ln.startswith("**Tier B under P12 passes with margin") or ln.startswith("Sign 4/4 under every treatment")]
        return {"n_log": len(data["bond"]), "n_sweep": sum(1 for _, r in data["bond"] if "sweep" in r),
                "n_agent": sum(1 for _, r in data["bond"] if "agent" in r),
                "agent_rows": _bond_table([h for h in hits if "sweep" not in h[1]]),
                "sweep_rows": _bond_table([h for h in hits if "sweep" in h[1]]),
                "lit": lit, "vie": v, "gate": gate}


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
    f01_models = mo.ui.multiselect(options=MODELS[:3], value=MODELS[:3], label="Models")
    _fl = sorted(f01.formula.unique()) if len(f01) else []
    hl = mo.ui.dropdown(options=["(none)"] + _fl, value="(none)", label="Highlight formula")
    return f01, f01_models, hl, thr


@app.cell
def _(data, mo):
    _h = data["f01_cv"].get("oh_unfiltered_strong") if isinstance(data["f01_cv"], dict) else None
    if not _h:
        f01_banner = mo.md("_Frozen F01 counts (`results/F01_cv.json`) not found here._")
    else:
        _pm = _h["unique_pair_majority"]
        f01_banner = mo.callout(mo.md(
            f"**{_h['right']}/{_h['n']} O-H evaluations agree with the rule "
            f"({100 * _h['right'] / _h['n']:.1f}%; baseline {_h['baseline_right']}/{_h['n']}).** "
            f"Pair majorities: {_pm['right']} right, {_pm['tie']} ties, {_pm['wrong']} wrong; "
            f"all {_pm['wrong']} involve mp-985293."), kind="info")
    f01_posthoc = mo.accordion({
        "Post hoc sensitivity (not the result)": mo.md(
            "Post hoc, chosen after seeing the frozen data, and only to locate the failure: leaving out the 10 pairs "
            "that contain mp-985293 gives 177 of 184 (74 pairs right, none wrong); raising the boundary to 1.00 Å gives "
            "175 of 182 (73 pairs, none wrong). These are nearly the same intervention, because 28 of the 30 evaluations "
            "between 0.99 and 1.00 Å come from mp-985293 (the other 2, both right, from mp-697136__JVASP-54742). "
            "Neither replaces the frozen result or the nested 183 of 210.")})
    return f01_banner, f01_posthoc


@app.cell
def _(f01, f01_banner, f01_models, f01_posthoc, hl, mo, thr):
    if not len(f01):
        f01_tab = mo.vstack([f01_banner, mo.md("_No decomposition data found._"), f01_posthoc])
    else:
        _d = f01[f01.model.isin(f01_models.value)].copy()
        _d["strong"] = _d.XH_max >= thr.value
        _oh = bool(f01["OH"].notna().all())
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
            f01_banner,
            mo.vstack([thr, f01_models, hl]),
            mo.md(f"Interactive recount at the slider settings: sign rule right {_k} of {_n} "
                  f"({_label}) | leave-one-formula-out constant-sign baseline: {_b} of {_n} "
                  f"| weak side: {_kw_} of {_nw} _(precomputed)_"),
            _fig,
            mo.md("The frozen result is the banner above: the 0.99 Å model-derived boundary, chosen after inspecting "
                  "the data, with the three quantitative models. Deuteration favours the polymorph with the shorter "
                  "O-H bonds once H bonds are moderate to strong; the stretch term is about half cancelled by "
                  "bend/libration (see `docs/findings/F01-xh-length-rule.md`)."),
            f01_posthoc,
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
def _(data, mo):
    _opts = pair_options(data)
    check_dd = mo.ui.dropdown(options=_opts, label="Pair (formula, space groups, pair_id)",
                              value=next((k for k, v in _opts.items() if v == DEFAULT_PAIR), next(iter(_opts), None)),
                              full_width=True)
    return (check_dd,)


@app.cell
def _(check_dd, data, mo):
    _rep = pair_report(data, check_dd.value) if check_dd.value else None
    if _rep is None:
        _body = mo.md("_No pair data found (`results/screen_pairs_refined.csv`)._")
    else:
        _t = _rep["models"].copy()
        _num = [c for c in _t.columns if c not in ("model", "regime", "rule call", "model sign", "agree", "flags")]
        _t[_num] = _t[_num].astype(float).round(3)
        _prov = lambda s: (f"`{s['struct_id']}` (space group {s['spg']}, {s['source']}): experimental = "
                           f"**{s['experimental']}**, evidence: {s['evidence'] or 'not listed'}")
        _agree = _t[_t.agree != "n/a"]
        _n_yes = int((_agree.agree == "yes").sum())
        _summary = (f"Rule vs models: {_n_yes} of {len(_agree)} models with a defined sign agree with the sign of the "
                    f"O-H change (rule: deuteration favours the polymorph with the shorter O-H bonds; it is claimed "
                    f"only in the strong regime, either member with mean O-H >= {STRONG_XH_A:.2f} A).")
        _items = [
            mo.md(f"**{_rep['formula'] or _rep['pair_id']}**, pair `{_rep['pair_id']}` _(precomputed)_. "
                  f"Sign convention: ddF_iso = [F_D(b) - F_H(b)] - [F_D(a) - F_H(a)], so a positive value means "
                  f"deuteration disfavours b; d(X-H) is b minus a, so the rule calls + when b has the longer bond."),
            mo.ui.table(_t, selection=None, page_size=10),
            mo.md(_summary + " The stretch and bend/libration columns are the split of ddF_total (meV/atom, "
                  "`results/decompose_pairs.csv`)."),
            mo.md("### Experimental provenance (`data/isoshift/experimental.csv`)\n\n"
                  f"- a: {_prov(_rep['a'])}\n- b: {_prov(_rep['b'])}"),
        ]
        if _rep["pair_id"] == DEFAULT_PAIR:
            _items.append(mo.callout(mo.md(
                f"Default pair: diaspore (mp-625152) vs delta-AlOOH (mp-23807). Candidate card with the pressure "
                f"shift of the boundary: [docs/findings/CARD-AlOOH.md]({CARD_URL}). Exploratory, outside the "
                f"harmonic domain."), kind="info"))
        _body = mo.vstack(_items)
    check_tab = mo.vstack([mo.md("All numbers on this tab are **precomputed** from cached results; nothing is computed "
                                 "live."), check_dd, _body])
    return (check_tab,)


@app.cell
def _(data, mo):
    _tr = brucite_trace(data)

    def _tbl(df, empty):
        return mo.ui.table(df, selection=None, page_size=10) if len(df) else mo.md(empty)

    _lit = _tr["lit"]
    if len(_lit):
        _r = _lit.iloc[0]
        _lit_md = mo.md(f"`data/isoshift/validation.csv`: **{_r['system']}**, {_r['observable']}, "
                        f"DOI [{_r['doi']}](https://doi.org/{_r['doi']}), {_r['source_location']}.\n\n"
                        f"> {_r['quote']}\n\nDerived effect: +{_r['derived_isotope_effect_pct']}%.")
    else:
        _lit_md = mo.md("_validation.csv row not found._")
    _v = _tr["vie"]
    if len(_v):
        _vie = mo.vstack([
            mo.md(f"`results/validation/volume_isotope.csv`, brucite at the 290 K grid point (measured +0.31% at 295 K): "
                  f"{int((_v.VIE_pct > 0).sum())} of {len(_v)} model x treatment rows positive, range "
                  f"{_v.VIE_pct.min():+.2f} to {_v.VIE_pct.max():+.2f}% _(precomputed)_."),
            mo.ui.table(_v.round(3), selection=None, page_size=16)])
    else:
        _vie = mo.md("_volume_isotope.csv brucite rows not found._")
    _gate = mo.md("\n\n".join(f"> {g}" for g in _tr["gate"]) if _tr["gate"]
                  else "_Decision lines not found (`docs/decisions/01-gate.md`)._")
    _steps = [
        ("1", BRUCITE_STEPS[0], mo.vstack([
            mo.md(f"Matching rows of `logs/bond_queries.jsonl` (text contains brucite or Mg(OH)2), "
                  f"{len(_tr['agent_rows'])} agent queries; the log line number is the query id."),
            _tbl(_tr["agent_rows"], "_No matching agent rows._")])),
        ("2", BRUCITE_STEPS[1], mo.vstack([
            mo.md(f"{len(_tr['sweep_rows'])} sweep queries (stage 1 workers) mention brucite or Mg(OH)2. "
                  "This stage gave the sign but no quote and no paired lattice table."),
            _tbl(_tr["sweep_rows"], "_No matching sweep rows._")])),
        ("3", BRUCITE_STEPS[2], _lit_md),
        ("4", BRUCITE_STEPS[3], _vie),
        ("5", BRUCITE_STEPS[4], _gate),
    ]
    _counts = mo.md(
        f"**Counts.** Bond queries in the log: **{_tr['n_log']}** ({_tr['n_sweep']} sweep, {_tr['n_agent']} agent). "
        f"Agent audit (`docs/story/agent_extraction_audit.md`): of {AUDIT['sweep_items']} sweep items, "
        f"**{AUDIT['ok_single_pass']} returned \"ok\" on a single pass**, but only **{AUDIT['survived']} survived** as "
        f"quantitative validation targets (brucite and LiH) after the second reader and the board.")
    how_tab = mo.vstack([
        mo.md("One claim traced from the first literature query to the gate decision (brucite, V_H/V_D - 1 = +0.31%). "
              "All evidence below is read from files in the repo _(precomputed)_."),
        _counts,
        *[mo.vstack([mo.md(f"### Step {n}. {t}"), e]) for n, t, e in _steps],
        mo.md("Lesson: single-pass agent extraction found sources but could not be trusted for numbers; the "
              "second reader and the board made the table usable."),
    ])
    return (how_tab,)


@app.cell
def _(bench_tab, check_tab, f01_tab, how_tab, mo):
    mo.ui.tabs({"F01 isotope rule": f01_tab, "Benchmark & atlas": bench_tab,
                "Check a pair": check_tab, "How we know": how_tab})
    return


if __name__ == "__main__":
    app.run()
