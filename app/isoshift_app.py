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
        )

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
                _g = _g.sort_values("T_K")
                _ax.plot(_g.T_K, _g.VIE_pct, marker="o", ms=3, label=_m)
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
                _txt.append(f"**{_r['model']}**: no curves ({'; '.join(_fl) or 'missing'})")
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


if __name__ == "__main__":
    app.run()
