"""Does the MLIP ensemble get the O-H stretch frequency vs hydrogen-bond geometry right? (F01 core check)

For every O-H donor in clean screened structures: O-H length, donor-acceptor O...O distance (nearest O to H
other than the donor, within 3.2 A), and the Gamma-point stretch frequency of that H (frequency of the mode
with the largest projection on its O-H bond, H masses). Compared with the empirical spectroscopic
correlation of Libowitzky (1999): nu = 3592 - 304e9 * exp(-d(O...O) / 0.1321) cm^-1, and with DFT
phonons (MDR phonondb force constants, PBEsol) where available.

    python -m src.isoshift_event.stretch_check               # recompute phonons (slow), then analyse
    python -m src.isoshift_event.stretch_check --from-csv    # re-analyse results/stretch_check.csv only (seconds)
writes results/stretch_check.csv (unless --from-csv), results/stretch_check_summary.json and figures/fig5_stretch_check.png

Windowed analysis (decision 04, action 4): symmetry-equivalent donors are removed per structure, only donors with
stretch_weight > 0.5 are used, and the slope ratio f = (model d nu / d nu_Libowitzky) is fitted per O...O window by OLS and
Theil-Sen, regressing the model frequency on the Libowitzky frequency at the same d(O...O). f = 1 means the model
reproduces the measured slope. Main window 2.50 to 2.80 A, second window 2.80 to 3.10 A.
"""
from __future__ import annotations

import csv
import json
import lzma
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
THZ_CM = 33.35641


def libowitzky(d_oo):
    return 3592.0 - 304e9 * np.exp(-np.asarray(d_oo) / 0.1321)


# Windowed analysis settings ---------------------------------------------------------------------------------------
WINDOWS = {"main_2.50-2.80": (2.50, 2.80), "outer_2.80-3.10": (2.80, 3.10)}
SUBWINDOWS = {"sub_2.50-2.65": (2.50, 2.65), "sub_2.65-2.80": (2.65, 2.80)}  # sensitivity only
MIN_WEIGHT = 0.5
DEDUP_TOL = {"d_OH_A": 0.001, "d_OO_A": 0.002, "nu_stretch_cm": 2.0}  # symmetry-equivalent donors agree to these
# Harmonic-minus-fundamental gap of the O-H stretch. The mismatch between a harmonic model frequency and a measured
# fundamental grows with H-bond strength; the CHANGE of that gap across the window (strong end minus weak end) flattens
# the true harmonic slope by gap_change / (nu_Lib span). ASSUMPTION (no literature table for solids found): the gap
# grows from about 150 cm-1 (weak end, 2.8 A) to about 300 cm-1 (strong end, 2.5 A), i.e. a change of 150 cm-1 (central
# case), and by up to 400 cm-1 in a pessimistic case. A free-OH gap of 150 to 200 cm-1 is 2*omega_e*x_e of the gas-phase
# stretch; the growth with H-bond strength is the chair's estimate in docs/decisions/04-discovery-claim.md.
GAP_CHANGE_CM = {"central_150": 150.0, "pessimistic_400": 400.0}


def dedup_donors(df):
    """Drop symmetry-equivalent donors: per (source, struct_id) keep one row among rows whose d_OH, d_OO and nu agree
    within DEDUP_TOL. Greedy, in file order."""
    keep = []
    tols = list(DEDUP_TOL.values())
    for _, g in df.groupby(["source", "struct_id"], sort=False):
        kept = []
        for idx, r in zip(g.index, g[list(DEDUP_TOL)].to_numpy()):
            if not any(all(abs(r[i] - k[i]) <= tols[i] for i in range(3)) for k in kept):
                kept.append(r)
                keep.append(idx)
    return df.loc[keep]


def window_stats(w, lo, hi, n_boot=2000, seed=0):
    """w: donors of one source with d_OO_A in [lo, hi]. Slope ratios f of nu_model on nu_Libowitzky(d_OO)."""
    from scipy.stats import theilslopes

    out = {"n_donors": int(len(w)), "n_structures": int(w.struct_id.nunique())}
    if len(w) < 6 or w.d_OO_A.nunique() < 3:
        return out
    L = libowitzky(w.d_OO_A.values)
    nu = w.nu_stretch_cm.values
    f_ols, f_ts = float(np.polyfit(L, nu, 1)[0]), float(theilslopes(nu, L)[0])
    span = float(libowitzky(hi) - libowitzky(lo))
    rng = np.random.default_rng(seed)  # bootstrap over structures (donors of one structure are not independent)
    groups = [np.flatnonzero((w.struct_id == s).values) for s in w.struct_id.unique()]
    boots = []
    for _ in range(n_boot):
        idx = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        if len(np.unique(L[idx])) > 2:
            boots.append(np.polyfit(L[idx], nu[idx], 1)[0])
    out.update({"f_OLS": round(f_ols, 3), "f_TheilSen": round(f_ts, 3),
                "f_OLS_boot95": [round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)] if boots else None,
                "median_offset_cm": round(float(np.median(nu - L)), 1), "mean_offset_cm": round(float((nu - L).mean()), 1),
                "rms_residual_cm": round(float(np.sqrt(((nu - L) ** 2).mean())), 1),
                "libowitzky_span_cm": round(span, 1),
                "slope_dnu_ddOO_model_cm_per_A": round(float(np.polyfit(w.d_OO_A, nu, 1)[0]), 1),
                "slope_dnu_ddOO_libowitzky_cm_per_A": round(float(np.polyfit(w.d_OO_A, L, 1)[0]), 1)})
    # harmonic vs fundamental: harmonic reference slope = Libowitzky slope * (1 - gap_change / span)
    # (reported only where the gap change is below half the window span; otherwise the correction is not meaningful)
    out["f_harmonic_corrected"] = {k: ({"OLS": round(f_ols / (1 - g / span), 3), "TheilSen": round(f_ts / (1 - g / span), 3)} if g < 0.5 * span else None)
                                   for k, g in GAP_CHANGE_CM.items()}
    return out


def windowed_analysis(df):
    """df: stretch_check.csv as a dataframe. Returns the 'windowed' block of the summary."""
    raw_n = df.groupby("source").size().to_dict()
    d = df[(df.stretch_weight > MIN_WEIGHT) & np.isfinite(df.d_OO_A)]
    after_w = d.groupby("source").size().to_dict()
    d = dedup_donors(d)
    out = {"settings": {"min_stretch_weight": MIN_WEIGHT, "dedup_tolerance": DEDUP_TOL, "windows_A": {**WINDOWS, **SUBWINDOWS},
                        "gap_change_bracket_cm": GAP_CHANGE_CM,
                        "gap_assumption": "harmonic-minus-fundamental O-H gap grows by 150 cm-1 (central) to 400 cm-1 (pessimistic) from the weak to the strong end of 2.50-2.80 A; an assumption, no literature table found"},
           "counts": {s: {"rows": int(raw_n.get(s, 0)), "weight_gt_0.5_finite_OO": int(after_w.get(s, 0)), "after_dedup": int((d.source == s).sum())}
                      for s in sorted(raw_n)}}
    for name, (lo, hi) in {**WINDOWS, **SUBWINDOWS}.items():
        out[name] = {s: window_stats(d[(d.source == s) & (d.d_OO_A >= lo) & (d.d_OO_A <= hi)], lo, hi)
                     for s in ["mace", "orb", "mattersim", "dft_pbesol"]}
    return out


def _donors(ph):
    uc = ph.primitive
    sym = np.array(uc.symbols)
    cell = np.asarray(uc.cell)
    frac = np.asarray(uc.scaled_positions)
    O = np.flatnonzero(sym == "O")
    out = []
    for i in np.flatnonzero(sym == "H"):
        if len(O) < 2:
            break
        d = frac[O] - frac[i]
        d -= np.round(d)
        cart = d @ cell
        r = np.linalg.norm(cart, axis=1)
        order = np.argsort(r)
        if r[order[0]] > 1.15:  # not an O-H donor
            continue
        don = order[0]
        # acceptor: nearest O other than the donor, H...O < 2.6 A; O...O measured donor-acceptor
        acc = order[1]
        if r[acc] > 2.6:
            d_oo = np.nan
        else:
            v = cart[acc] - cart[don]
            d_oo = float(np.linalg.norm(v))
        out.append((int(i), cart[don] / r[don], float(r[don]), d_oo))
    return out


def _stretch(ph, donors):
    p = ph
    p.run_qpoints([[0, 0, 0]], with_eigenvectors=True)
    f = p.qpoints.frequencies[0] * THZ_CM
    ev = p.qpoints.eigenvectors[0].reshape(len(ph.primitive.symbols), 3, -1)
    res = []
    for i, b, d_oh, d_oo in donors:
        w = np.abs(np.einsum("a,ab->b", b, ev[i])) ** 2
        k = int(np.argmax(w * (f > 1500)))
        res.append((d_oh, d_oo, float(f[k]), float(w[k])))
    return res


def _mlip(args):
    model, sid, cache_dir = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import phonopy

    ph = phonopy.load(str(Path(cache_dir) / "phonopy_params.yaml"), produce_fc=False, log_level=0)
    don = _donors(ph)
    return [(model, sid, *r) for r in _stretch(ph, don)] if don else []


def _dft(path):
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import phonopy

    with tempfile.TemporaryDirectory() as tmp:
        y = Path(tmp) / "phonopy_params.yaml"
        y.write_bytes(lzma.open(path).read())
        ph = phonopy.load(str(y), log_level=0)
        ph.nac_params = None
    don = _donors(ph)
    return [("dft_pbesol", Path(path).parent.name, *r) for r in _stretch(ph, don)] if don else []


def main():
    from . import refine

    idx = refine._cache_index()
    clean = set()
    dec = ROOT / "results" / "decompose_structures.csv"
    for r in csv.DictReader(open(dec)):
        if abs(float(r["dF_quad_meV_atom"]) - float(r["dF_direct_meV_atom"])) < 0.01 and r["covalent_XH"] == "True":
            clean.add((r["model"], r["struct_id"]))
    jobs = []
    for model, sid in sorted(clean):
        raw = json.loads((refine.RAW / model / f"{sid}.json").read_text())
        calc = "{name}-{model}".format(**raw["calc"])
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
        key = (safe, round(raw["fc_meta"]["energy_eV"], 6), round(raw["fc_meta"]["volume_A3"], 4))
        if key in idx:
            jobs.append((model, sid, str(idx[key])))
    dft = sorted(str(p) for p in (ROOT / "data" / "isoshift" / "dft_phonons" / "mdr_phonondb").rglob("phonopy_params.yaml.xz"))
    with ProcessPoolExecutor(6) as ex:
        rows = [r for rs in ex.map(_mlip, jobs, chunksize=4) for r in rs]
        rows += [r for rs in ex.map(_dft, dft) for r in rs]
    with open(ROOT / "results" / "stretch_check.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "struct_id", "d_OH_A", "d_OO_A", "nu_stretch_cm", "stretch_weight"])
        w.writerows(rows)
    analyse()


def analyse():
    """Legacy residual summary + windowed analysis + figure, from results/stretch_check.csv."""
    import matplotlib.pyplot as plt
    import pandas as pd

    df = pd.read_csv(ROOT / "results" / "stretch_check.csv")
    rows = list(df.itertuples(index=False, name=None))
    win = windowed_analysis(df)
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    colors = {"mace": "#0072B2", "orb": "#E69F00", "mattersim": "#009E73", "sevenn": "#CC79A7", "dft_pbesol": "black"}
    summary = {}
    for src in colors:
        s = [(d, nu) for so, _sid, _oh, d, nu, wt in rows if so == src and np.isfinite(d) and 2.4 < d < 3.2 and wt > 0.3]
        if not s:
            continue
        d, nu = np.array(s).T
        res = nu - libowitzky(d)
        summary[src] = {"n": len(d), "mean_residual_cm": round(float(res.mean()), 1), "rms_residual_cm": round(float(np.sqrt((res ** 2).mean())), 1),
                        "slope_dnu_ddOO_cm_per_A": round(float(np.polyfit(d, nu, 1)[0]), 1)}
        f = win["main_2.50-2.80"].get(src, {}).get("f_OLS")
        lab = f"{src} (n={len(d)})" + (f", f={f:.2f}" if f is not None and src != "dft_pbesol" else "")
        ax.scatter(d, nu, s=10 if src != "dft_pbesol" else 30, alpha=0.5, color=colors[src], label=lab,
                   marker="o" if src != "dft_pbesol" else "D")
    lo, hi = WINDOWS["main_2.50-2.80"]
    ax.axvspan(lo, hi, color="0.5", alpha=0.12, lw=0, label=f"slope window {lo:.2f}-{hi:.2f} A (f = model/measured slope)")
    x = np.linspace(2.45, 3.15, 100)
    ax.plot(x, libowitzky(x), "k--", lw=1.5, label="Libowitzky 1999 (measured spectra)")
    ax.set_xlabel("donor-acceptor O...O distance (A)")
    ax.set_ylabel("O-H stretch frequency (cm$^{-1}$)")
    ax.set_title("O-H stretch vs H-bond length: models vs experiment")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "fig5_stretch_check.png", dpi=300)
    summary["windowed"] = win
    (ROOT / "results" / "stretch_check_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    import sys

    analyse() if "--from-csv" in sys.argv else main()
