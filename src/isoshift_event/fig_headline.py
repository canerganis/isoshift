"""Headline figure (decision 07, action 7): O-H pairs, strong regime vs weak, mp-985293 as open markers.

    python -m src.isoshift_event.fig_headline  -> figures/fig_headline.png/.svg, figures/fig_headline_caption.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import rule_cv  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "figures"
COLORS = {"mace": "#0072B2", "orb": "#E69F00", "mattersim": "#009E73"}  # Okabe-Ito
GREY = "0.55"
COUNTEREXAMPLE = "mp-985293"
CAPTION = ("O-H pairs with |Δ mean O-H| ≥ 5 mÅ. Regime by the larger mean model O-H of the pair; the 0.99 Å boundary "
           "was chosen after inspecting the data (nested re-choice picks 1.00 Å in 30 of 31 folds). Open markers: "
           "evaluations involving Al(OH)3 mp-985293, kept in the counts. Evaluations share structures and models.")


def main():
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
    print(f"strong: {int(s.right.sum())}/{len(s)}; weak: {k_w}/{n_w}; open markers ({COUNTEREXAMPLE}): {int(ce.sum())}; "
          f"filled strong: {int((~ce).sum())}; pairs {pm}")

    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    ax.axhline(0, color="0.7", lw=0.8)
    ax.axvline(0, color="0.7", lw=0.8)
    ax.scatter(w.x, w.y, s=26, marker="o", color=GREY, alpha=0.65, lw=0, zorder=2,
               label=f"weak side (grey): fails, {k_w}/{n_w}")
    for m, col in COLORS.items():
        g = s[(s.model == m) & ~ce]
        ax.scatter(g.x, g.y, s=28, marker="o", color=col, alpha=0.8, lw=0, zorder=3, label=f"{m}")
        g = s[(s.model == m) & ce]
        ax.scatter(g.x, g.y, s=60, marker="o", facecolors="none", edgecolors=col, lw=1.6, zorder=4)
    ax.scatter([], [], s=60, marker="o", facecolors="none", edgecolors="k", lw=1.6,
               label=f"open: mp-985293 ({int(ce.sum())})")
    ax.set_xlabel("change in mean O-H length, b minus a (mÅ)")
    ax.set_ylabel(r"$\Delta\Delta F_{iso}$ per H at 300 K (meV)")
    ax.text(0.02, 0.98,
            f"{head['right']}/{head['n']} evaluations (baseline {head['baseline_right']}/{head['n']}); "
            f"pairs {pm['right']} right, {pm['tie']} ties, {pm['wrong']} wrong (all contain Al(OH)3 {COUNTEREXAMPLE})",
            transform=ax.transAxes, ha="left", va="top", fontsize=8.5, wrap=True,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="0.4", lw=0.8), zorder=6)
    ax.legend(loc="lower right", fontsize=8, frameon=True)
    # weak-side label next to the grey cloud
    ax.annotate(f"weak H bonds: fails, {k_w}/{n_w}", xy=(-9.0, 5.0),
                xytext=(0.43, 0.80), textcoords="axes fraction", fontsize=8.5, color="0.3",
                arrowprops=dict(arrowstyle="-", color="0.5", lw=0.8))

    ins = ax.inset_axes([0.075, 0.53, 0.30, 0.28])
    ms = list(COLORS)
    xs = range(len(ms))
    ins.bar([i - 0.2 for i in xs], [slopes[m]["stretch_slope"] for m in ms], 0.38, color="0.25", label="stretch")
    ins.bar([i + 0.2 for i in xs], [slopes[m]["perp_slope"] for m in ms], 0.38, color="0.75", ec="0.25", lw=0.6,
            label="bend/libration")
    ins.axhline(0, color="k", lw=0.6)
    ins.set_xticks(list(xs))
    ins.set_xticklabels(["MACE", "ORB", "MatterSim"], fontsize=6.5)
    ins.tick_params(axis="y", labelsize=6.5)
    ins.set_ylabel("slope (meV/H per mÅ)", fontsize=6.5)
    ins.set_title("strong regime: stretch vs bend/libration", fontsize=7)
    ins.set_ylim(-0.26, 0.55)
    ins.legend(fontsize=6, loc="upper right", ncol=2, frameon=False)
    ax.set_title("Deuteration favours the polymorph with the shorter O-H bonds", fontsize=11)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "fig_headline.png", dpi=200)
    fig.savefig(FIG / "fig_headline.svg")
    (FIG / "fig_headline_caption.txt").write_text(CAPTION + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
