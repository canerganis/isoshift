"""Publication versions of the paper figures (Figs. 1, 2, 4 and 3), written only to docs/paper/figures.

    python -m src.isoshift_event.paper_figures

Same data and counts as fig_headline, fig_rule, stretch_check and paper_stats; only labels and layout differ.
The root figures/ used by the hackathon write-up and video are not touched.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import paper_stats, rule_cv, stretch_check  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "paper" / "figures"
NAMES = {"mace": "MACE", "orb": "ORB", "mattersim": "MatterSim", "sevenn": "SevenNet", "dft_pbesol": "PBEsol (DFT)"}
COLORS = {"mace": "#0072B2", "orb": "#E69F00", "mattersim": "#009E73", "sevenn": "#CC79A7"}
GREY = "0.55"
COUNTEREXAMPLE = "mp-985293"
DDF = r"$\Delta\Delta F_{\mathrm{iso}}$"

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def panel(ax, letter):
    ax.text(-0.02, 1.02, f"({letter})", transform=ax.transAxes, ha="right", va="bottom", fontsize=10, fontweight="bold")


def fig_headline():
    cv = json.loads((ROOT / "results" / "F01_cv.json").read_text(encoding="utf-8"))
    head, slopes = cv["oh_unfiltered_strong"], cv["oh_strong_slopes"]
    pm = head["unique_pair_majority"]
    d = rule_cv.load()
    d = d[d.OH & (d.x.abs() >= rule_cv.MIN_DXH)].copy()
    strong = d.rmax >= rule_cv.MAIN_THR
    s, w = d[strong], d[~strong]
    assert (int(s.right.sum()), len(s)) == (head["right"], head["n"]), "disagrees with F01_cv.json"
    k_w, n_w = int(w.right.sum()), len(w)
    ce = s.pair_id.str.contains(COUNTEREXAMPLE)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.axhline(0, color="0.7", lw=0.8)
    ax.axvline(0, color="0.7", lw=0.8)
    ax.scatter(w.x, w.y, s=22, color=GREY, alpha=0.65, lw=0, zorder=2,
               label=f"weak H bonds, $r_{{\\max}}<0.99$ Å ({k_w}/{n_w} right)")
    for m, col in COLORS.items():
        if m == "sevenn":
            continue
        g = s[(s.model == m) & ~ce]
        ax.scatter(g.x, g.y, s=24, color=col, alpha=0.8, lw=0, zorder=3, label=NAMES[m])
        g = s[(s.model == m) & ce]
        ax.scatter(g.x, g.y, s=52, facecolors="none", edgecolors=col, lw=1.4, zorder=4)
    ax.scatter([], [], s=52, facecolors="none", edgecolors="k", lw=1.4,
               label=f"Al(OH)$_3$ {COUNTEREXAMPLE} ({int(ce.sum())} evaluations)")
    ax.set_xlabel(r"$\Delta\bar r$, change in mean O-H length from $a$ to $b$ (mÅ)")
    ax.set_ylabel(f"{DDF} at 300 K (meV per H)")
    ax.text(0.03, 0.72,
            f"$r_{{\\max}}\\geq0.99$ Å: {head['right']}/{head['n']} right "
            f"(constant sign {head['baseline_right']}/{head['n']})\n"
            f"pairs: {pm['right']} right, {pm['wrong']} wrong",
            transform=ax.transAxes, ha="left", va="top", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.6", lw=0.6), zorder=6)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False, bbox_to_anchor=(0.0, 1.0))

    ins = ax.inset_axes([0.66, 0.08, 0.32, 0.26])
    ms = ["mace", "orb", "mattersim"]
    xs = range(len(ms))
    ins.bar([i - 0.2 for i in xs], [slopes[m]["stretch_slope"] for m in ms], 0.38, color="0.25", label="stretch")
    ins.bar([i + 0.2 for i in xs], [slopes[m]["perp_slope"] for m in ms], 0.38, color="0.8", ec="0.25", lw=0.6,
            label="bend and libration")
    ins.axhline(0, color="k", lw=0.6)
    ins.set_xticks(list(xs))
    ins.set_xticklabels([NAMES[m] for m in ms], fontsize=6.5)
    ins.tick_params(axis="y", labelsize=6.5)
    ins.set_ylabel("slope (meV per H per mÅ)", fontsize=6.5)
    ins.set_ylim(-0.26, 0.62)
    ins.legend(fontsize=6, loc="upper left", ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_headline.png", dpi=300)
    return {"strong": [head["right"], head["n"]], "weak": [k_w, n_w], "open": int(ce.sum())}


def fig_rule():
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    c = d[(d.clean == True) & (d.covalent_XH == True)].copy()  # noqa: E712
    for k in ("ddF_total", "ddF_str", "ddF_perp"):
        c[k + "_H"] = c[k] / c.H_per_atom
    c["dXH_mA"] = c.dXH_mean_A * 1000
    oh = rule_cv.load()
    oh = oh[oh.OH].copy()
    elig = oh.x.abs() >= rule_cv.MIN_DXH
    strong = oh.rmax >= rule_cv.MAIN_THR
    head = json.loads((ROOT / "results" / "F01_cv.json").read_text(encoding="utf-8"))["oh_unfiltered_strong"]
    k_s, n_s = int(oh[elig & strong].right.sum()), int((elig & strong).sum())
    k_w, n_w = int(oh[elig & ~strong].right.sum()), int((elig & ~strong).sum())
    assert (k_s, n_s) == (head["right"], head["n"]), "panel c disagrees with F01_cv.json"

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
    fits = {}
    ax = axes[0]
    for m, g in c.groupby("model"):
        k, b = np.polyfit(g.dXH_mA, g.ddF_total_H, 1)
        r = np.corrcoef(g.dXH_mA, g.ddF_total_H)[0, 1]
        fits[m] = [round(float(k), 3), round(float(r), 2), len(g)]
        ax.scatter(g.dXH_mA, g.ddF_total_H, s=10, alpha=0.5, color=COLORS[m],
                   label=f"{NAMES[m]}: slope {k:.2f}, $r$ = {r:.2f}, $n$ = {len(g)}")
        x = np.linspace(c.dXH_mA.quantile(0.01), c.dXH_mA.quantile(0.99), 2)
        ax.plot(x, k * x + b, color=COLORS[m], lw=1.4)
    ax.axhline(0, color="0.7", lw=0.8)
    ax.axvline(0, color="0.7", lw=0.8)
    ax.set_xlabel("change in mean X-H length, $b$ minus $a$ (mÅ)")
    ax.set_ylabel(f"{DDF} at 300 K (meV per H)")
    ax.legend(fontsize=7, loc="upper left", frameon=False, title="slope in meV per H per mÅ", title_fontsize=7)
    panel(ax, "a")

    ax = axes[1]
    for i, (m, g) in enumerate(c.groupby("model")):
        ks = np.polyfit(g.dXH_mA, g.ddF_str_H, 1)[0]
        kp = np.polyfit(g.dXH_mA, g.ddF_perp_H, 1)[0]
        ax.scatter(g.dXH_mA, g.ddF_str_H, s=7, alpha=0.4, color=COLORS[m], marker="o")
        ax.scatter(g.dXH_mA, g.ddF_perp_H, s=7, alpha=0.4, color=COLORS[m], marker="x")
        ax.text(0.02, 0.96 - 0.065 * i, f"{NAMES[m]}: stretch {ks:+.2f}, bend and libration {kp:+.2f}",
                transform=ax.transAxes, fontsize=7, color=COLORS[m], va="top")
    ax.scatter([], [], s=12, color="0.3", marker="o", label="stretch")
    ax.scatter([], [], s=12, color="0.3", marker="x", label="bend and libration")
    ax.legend(fontsize=7, loc="lower right", frameon=False)
    ax.axhline(0, color="0.7", lw=0.8)
    ax.set_xlabel("change in mean X-H length (mÅ)")
    ax.set_ylabel("contribution at 300 K (meV per H)")
    panel(ax, "b")

    ax = axes[2]
    for mask, mk, col, lab in (
            (strong, "o", "#0072B2", f"$r_{{\\max}}\\geq0.99$ Å: {k_s}/{n_s} right (constant sign {head['baseline_right']})"),
            (~strong, "x", "#D55E00", f"$r_{{\\max}}<0.99$ Å: {k_w}/{n_w} right")):
        g = oh[mask]
        ax.scatter(g.x, g.y, s=10, alpha=0.6, marker=mk, color=col, label=lab)
    ax.axhline(0, color="0.7", lw=0.8)
    ax.axvline(0, color="0.7", lw=0.8)
    ax.axvspan(-5, 5, color="0.9", zorder=0)
    ax.set_xlabel("change in mean O-H length (mÅ)")
    ax.set_ylabel(f"{DDF} at 300 K (meV per H)")
    ax.legend(fontsize=7, loc="upper left", frameon=False)
    panel(ax, "c")
    fig.tight_layout()
    fig.savefig(OUT / "fig4_xh_rule.png", dpi=300)
    return {"fits": fits, "strong": [k_s, n_s], "weak": [k_w, n_w]}


def fig_stretch():
    df = pd.read_csv(ROOT / "results" / "stretch_check.csv")
    rows = list(df.itertuples(index=False, name=None))
    win = stretch_check.windowed_analysis(df)
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    colors = {**COLORS, "dft_pbesol": "black"}
    ns = {}
    for src in colors:
        s = [(d, nu) for so, _sid, _oh, d, nu, wt in rows
             if so == src and np.isfinite(d) and 2.4 < d < 3.2 and wt > 0.3]
        if not s:
            continue
        d, nu = np.array(s).T
        ns[src] = len(d)
        f = win["main_2.50-2.80"].get(src, {}).get("f_OLS")
        lab = f"{NAMES[src]} ($n$ = {len(d)}" + (f", $f$ = {f:.2f})" if f is not None and src != "dft_pbesol" else ")")
        ax.scatter(d, nu, s=9 if src != "dft_pbesol" else 28, alpha=0.5, color=colors[src], label=lab,
                   marker="o" if src != "dft_pbesol" else "D")
    lo, hi = stretch_check.WINDOWS["main_2.50-2.80"]
    ax.axvspan(lo, hi, color="0.5", alpha=0.12, lw=0, label=f"slope window, {lo:.2f} to {hi:.2f} Å")
    x = np.linspace(2.45, 3.15, 100)
    ax.plot(x, stretch_check.libowitzky(x), "k--", lw=1.4, label="Libowitzky 1999 (measured spectra)")
    ax.set_xlabel("donor-acceptor O$\\cdots$O distance (Å)")
    ax.set_ylabel("O-H stretch frequency (cm$^{-1}$)")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "fig5_stretch_check.png", dpi=300)
    return ns


def fig_accuracy():
    out = json.loads((ROOT / "results" / "paper_stats.json").read_text(encoding="utf-8"))
    paper_stats.figure(out, None)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"fig_headline": fig_headline(), "fig4_xh_rule": fig_rule(), "fig5_stretch_check": fig_stretch()}, indent=1))
    fig_accuracy()


if __name__ == "__main__":
    main()
