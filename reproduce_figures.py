"""Reproduce figures from committed/cached CSVs. CPU only, < 1 min.
Writes figures/*.png (300 dpi) and figures/*.svg. Missing inputs skip a panel."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

# Okabe-Ito colour-blind safe palette
MODEL_COL = {"mace": "#0072B2", "orb": "#E69F00", "mattersim": "#009E73", "sevenn": "#CC79A7"}
MODEL_MK = {"mace": "o", "orb": "s", "mattersim": "^", "sevenn": "D"}
C_EXP, C_NOEXP, GREY = "#D55E00", "#0072B2", "#BBBBBB"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 10, "legend.frameon": False, "svg.fonttype": "none"})


def read(rel):
    p = ROOT / rel
    if not p.exists():
        print(f"[skip] missing {rel}")
        return None
    return pd.read_csv(p)


def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote figures/{name}.png/.svg")


def panel_validation(ax):
    v = read("results/validation/volume_isotope.csv")
    if v is None:
        ax.text(0.5, 0.5, "volume_isotope.csv missing", ha="center", transform=ax.transAxes)
        return
    v = v[v["T_K"] > 0]
    targets = [("brucite", 295, False), ("LiH", 300, False), ("iceXI", 100, True)]
    allv = []
    for case, tt, hollow in targets:
        d = v[v["case"] == case]
        if d.empty:
            continue
        Ts = d["T_K"].unique()
        T = Ts[np.argmin(np.abs(Ts - tt))]
        d = d[d["T_K"] == T]
        for m, g in d.groupby("model"):
            x = g["exp_VIE_pct"].iloc[0]
            y = g["VIE_pct"]
            med, lo, hi = y.median(), y.min(), y.max()
            allv += [x, lo, hi]
            col = MODEL_COL.get(m, "k")
            ax.errorbar(x, med, yerr=[[med - lo], [hi - med]], fmt=MODEL_MK.get(m, "o"),
                        color=col, mfc="white" if hollow else col,
                        ms=6, capsize=2.5, lw=1.2, mew=1.4)
        xe = d["exp_VIE_pct"].iloc[0]
        lab = f"{case} {T:g} K" + (" (reported only)" if hollow else "")
        ax.annotate(lab, (xe, d["VIE_pct"].max()), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=8)
    if allv:
        lim = (min(allv) - 0.15, max(allv) + 0.3)
        ax.plot(lim, lim, color="0.4", lw=0.8, ls="--", zorder=0)
        ax.set_xlim(lim)
        ax.set_ylim(lim)
    ax.set_xlabel("Measured $V_H/V_D - 1$ (%)")
    ax.set_ylabel("Computed $V_H/V_D - 1$ (%)")
    ax.set_title("Validation: volume isotope effect")
    hs = [plt.Line2D([], [], marker=MODEL_MK[m], color=MODEL_COL[m], ls="", label=m) for m in MODEL_COL]
    hs.append(plt.Line2D([], [], marker="o", mfc="white", mec="0.3", color="0.3", ls="", label="reported only"))
    hs.append(plt.Line2D([], [], color="0.4", ls="--", label="parity"))
    ax.legend(handles=hs, loc="lower right", fontsize=8)
    ax.text(0.02, 0.97, "portlandite: no clean experimental pair\n(not plotted)\n"
            "bars: min to max over imaginary-mode\ntreatments; marker: median",
            transform=ax.transAxes, va="top", fontsize=7.5, color="0.25")


def panel_candidates(ax):
    clean = read("results/candidates.csv")
    ext = read("results/candidates_extended.csv")
    ref = read("results/screen_pairs_refined.csv")
    exp = read("data/isoshift/experimental.csv")
    if ref is not None:
        r = ref.dropna(subset=["ddF_iso_300K_meV_atom", "dE_static_meV_atom"])
        ax.scatter(r["dE_static_meV_atom"], r["ddF_iso_300K_meV_atom"], s=4, c=GREY, alpha=0.5,
                   lw=0, zorder=1, rasterized=True)
    ax.axhspan(-0.1, 0.1, color="#999999", alpha=0.3, zorder=0)
    if clean is None and ext is None:
        return
    cl = clean[clean["eligible"] == True] if clean is not None else pd.DataFrame()
    ex = ext[ext["eligible"] == True] if ext is not None else pd.DataFrame()
    clean_ids = set(cl["pair_id"]) if len(cl) else set()
    br = ex[~ex["pair_id"].isin(clean_ids)] if len(ex) else ex
    expmap = {}
    if exp is not None:
        expmap = dict(zip(exp["struct_id"], exp["experimental"].astype(str).str.lower() == "true"))
    pts = []
    for df, filled in ((cl, True), (br, False)):
        for _, r in df.iterrows():
            both = expmap.get(r["struct_a"], False) and expmap.get(r["struct_b"], False)
            col = C_EXP if both else C_NOEXP
            x, y = r["dE_static_median_meV_atom"], r["ddF_iso_300K_median_meV_atom"]
            lo, hi = r["ddF_iso_300K_min_meV_atom"], r["ddF_iso_300K_max_meV_atom"]
            ax.errorbar(x, y, yerr=[[max(y - lo, 0)], [max(hi - y, 0)]], fmt="o", color=col,
                        mfc=col if filled else "white", ms=5.5, mew=1.3, lw=1, capsize=2, zorder=3)
            pts.append((abs(y), x, y, r["formula"], bool(both)))
    pts.sort(reverse=True)
    chosen = {(p[1], p[2], p[3]): p for p in pts[:8]}
    chosen.update({(p[1], p[2], p[3]): p for p in pts if p[4]})
    seen = set()
    offs = [(6, 6), (-6, 9), (8, -10), (-8, -10), (10, 14), (-10, 16)]
    for i, (_, x, y, f, both) in enumerate(sorted(chosen.values(), key=lambda t: (t[1], t[2]))):
        if f in seen:
            continue
        seen.add(f)
        dx, dy = offs[len(seen) % len(offs)]
        ax.annotate(f, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=7.5,
                    ha="left" if dx > 0 else "right",
                    arrowprops=dict(arrowstyle="-", lw=0.4, color="0.4"))
    if pts:
        xs = [p[1] for p in pts]; ys = [p[2] for p in pts]
        ax.set_xlim(min(xs) - 8, max(xs) + 8)
        ax.set_ylim(min(ys) - 3, max(ys) + 3)
    ax.set_xlabel("MLIP static polymorph gap, median (meV/atom)")
    ax.set_ylabel(r"$\Delta\Delta F_{iso}$ at 300 K, median (meV/atom)")
    ax.set_title("Candidate map")
    ax.annotate("below resolution floor ($|\\Delta\\Delta F| < 0.1$ meV/atom)", xy=(0.01, -0.1),
                xycoords=("axes fraction", "data"), xytext=(0, -3), textcoords="offset points",
                ha="left", va="top", fontsize=7, color="0.3")
    hs = [plt.Line2D([], [], marker="o", color=C_EXP, ls="", label="both polymorphs observed"),
          plt.Line2D([], [], marker="o", color=C_NOEXP, ls="", label="not both observed"),
          plt.Line2D([], [], marker="o", color="0.3", ls="", label="clean tier (filled)"),
          plt.Line2D([], [], marker="o", mfc="white", mec="0.3", color="0.3", ls="",
                     label="bracketed tier (hollow)"),
          plt.Line2D([], [], marker="o", color=GREY, ls="", ms=3, label="other screened pairs")]
    ax.legend(handles=hs, loc="lower right", fontsize=7.5)
    ax.text(0.01, 0.99, "error bars: min to max over models", transform=ax.transAxes,
            ha="left", va="top", fontsize=7, color="0.3")


def fig1():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    panel_validation(axs[0])
    panel_candidates(axs[1])
    fig.tight_layout()
    save(fig, "fig1_main")


def fig2():
    pairs = read("data/isoshift/pairs.csv")
    ref = read("results/screen_pairs_refined.csv")
    clean = read("results/candidates.csv")
    ext = read("results/candidates_extended.csv")
    st = read("results/screen_structures.csv")
    labels, vals = [], []
    if st is not None:
        labels.append("structures screened")
        vals.append(st["struct_id"].nunique())
    if pairs is not None:
        labels.append("pairs")
        vals.append(len(pairs))
    if ref is not None:
        labels.append("pairs with screen result")
        vals.append(ref.dropna(subset=["ddF_iso_300K_meV_atom"])["pair_id"].nunique())
        labels.append("identity-checked")
        vals.append(ref[ref["identity_checked"].astype(str).str.lower() == "true"]["pair_id"].nunique())
    ids_cl = set()
    if clean is not None:
        ids_cl = set(clean.loc[clean["eligible"] == True, "pair_id"])
        labels.append("eligible, clean tier")
        vals.append(len(ids_cl))
    if ext is not None:
        e = ext[ext["eligible"] == True]
        labels.append("eligible, bracketed tier")
        vals.append(int((~e["pair_id"].isin(ids_cl)).sum()))
    if not vals:
        print("[skip] fig2: no inputs")
        return
    fig, ax = plt.subplots(figsize=(7, 3.6))
    y = np.arange(len(vals))[::-1]
    ax.barh(y, vals, color="#0072B2", height=0.6)
    for yi, v in zip(y, vals):
        ax.text(v, yi, f" {v}", va="center", fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlim(0, max(vals) * 3)
    ax.set_xlabel("Count (symlog axis)")
    ax.set_title("Pipeline counts")
    fig.tight_layout()
    save(fig, "fig2_pipeline_counts")


def fig3():
    b = read("results/benchmark/summary.csv")
    if b is None or b.empty:
        print("[skip] fig3: no benchmark summary")
        return
    b = b.copy()
    b["grp"] = b["model"] + "\n" + b["setting"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, col, lab in ((axs[0], "dzpe_MAE_meV", r"MAE of $\Delta$ZPE per H (meV)"),
                         (axs[1], "dF300_MAE_meV", r"MAE of $\Delta F_{300K}$ per H (meV)")):
        cols = [MODEL_COL.get(m, "#666666") for m in b["model"]]
        ax.bar(range(len(b)), b[col], color=cols)
        ax.set_xticks(range(len(b)))
        ax.set_xticklabels(b["grp"], fontsize=8)
        ax.set_ylabel(lab)
    axs[0].set_title("Isotope benchmark (placeholder, n=%s)" % ",".join(map(str, b["n"].unique())))
    fig.tight_layout()
    save(fig, "fig3_benchmark")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        try:
            f()
        except Exception as e:  # keep going if one figure fails
            print(f"[skip] {f.__name__}: {e!r}")
