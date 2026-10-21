"""Figure for finding F01: isotope shift of polymorph stability vs the change in mean X-H bond length.

    python -m src.isoshift_event.fig_rule      -> figures/fig4_xh_rule.png/.svg
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import rule_cv

ROOT = Path(__file__).resolve().parents[2]
COLORS = {"mace": "#0072B2", "orb": "#E69F00", "mattersim": "#009E73", "sevenn": "#CC79A7"}


def main():
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    c = d[(d.clean == True) & (d.covalent_XH == True)].copy()  # noqa: E712
    for k in ("ddF_total", "ddF_str", "ddF_perp"):
        c[k + "_H"] = c[k] / c.H_per_atom
    c["dXH_mA"] = c.dXH_mean_A * 1000
    # panel 3: O-H pairs, no cut on the target (decision 05 headline population), via rule_cv.load()
    oh = rule_cv.load()
    oh = oh[oh.OH].copy()
    elig = oh.x.abs() >= rule_cv.MIN_DXH
    strong = oh.rmax >= rule_cv.MAIN_THR
    head = json.loads((ROOT / "results" / "F01_cv.json").read_text(encoding="utf-8"))["oh_unfiltered_strong"]
    k_s, n_s = int(oh[elig & strong].right.sum()), int((elig & strong).sum())
    k_w, n_w = int(oh[elig & ~strong].right.sum()), int((elig & ~strong).sum())
    assert (k_s, n_s) == (head["right"], head["n"]), "panel 3 disagrees with F01_cv.json oh_unfiltered_strong"
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    ax = axes[2]
    for mask, mk, col, lab in (
            (strong, "o", "#0072B2", f"moderate/strong H bond (max O-H ≥ 0.99 Å): {k_s}/{n_s} right, baseline {head['baseline_right']}/{n_s}"),
            (~strong, "x", "#D55E00", f"weak H bonds on both sides: {k_w}/{n_w} right")):
        g = oh[mask]
        ax.scatter(g.x, g.y, s=12, alpha=0.6, marker=mk, color=col, label=lab)
    ax.axhline(0, color="0.6", lw=0.8)
    ax.axvline(0, color="0.6", lw=0.8)
    ax.axvspan(-5, 5, color="0.9", zorder=0)
    ax.set_xlabel("change in mean O-H bond length (mÅ)")
    ax.set_ylabel(r"$\Delta\Delta F_{iso}$ at 300 K (meV per H)")
    ax.set_title(f"O-H pairs, no ddF cut: strong {k_s}/{n_s}, weak {k_w}/{n_w}", fontsize=10)
    ax.legend(fontsize=7, loc="upper left")
    ax = axes[0]
    for m, g in c.groupby("model"):
        k, b = np.polyfit(g.dXH_mA, g.ddF_total_H, 1)
        r = np.corrcoef(g.dXH_mA, g.ddF_total_H)[0, 1]
        ax.scatter(g.dXH_mA, g.ddF_total_H, s=12, alpha=0.55, color=COLORS.get(m), label=f"{m}: {k:.2f} meV/H per mÅ, r={r:.2f}, n={len(g)}")
        x = np.linspace(c.dXH_mA.quantile(0.01), c.dXH_mA.quantile(0.99), 2)
        ax.plot(x, k * x + b, color=COLORS.get(m), lw=1.5)
    ax.axhline(0, color="0.6", lw=0.8)
    ax.axvline(0, color="0.6", lw=0.8)
    ax.set_xlabel("change in mean X-H bond length, polymorph b minus a (mÅ)")
    ax.set_ylabel(r"$\Delta\Delta F_{iso}$ at 300 K (meV per H)")
    ax.set_title("Deuteration favours the polymorph with shorter X-H bonds")
    ax.legend(fontsize=7.5, loc="upper left")
    ax = axes[1]
    for m, g in c.groupby("model"):
        ks = np.polyfit(g.dXH_mA, g.ddF_str_H, 1)[0]
        kp = np.polyfit(g.dXH_mA, g.ddF_perp_H, 1)[0]
        ax.scatter(g.dXH_mA, g.ddF_str_H, s=8, alpha=0.4, color=COLORS.get(m), marker="o")
        ax.scatter(g.dXH_mA, g.ddF_perp_H, s=8, alpha=0.4, color=COLORS.get(m), marker="x")
        ax.annotate(f"{m}: stretch {ks:+.2f}, bend/libration {kp:+.2f}", xy=(0.02, 0.95 - 0.07 * list(COLORS).index(m)),
                    xycoords="axes fraction", fontsize=7.5, color=COLORS.get(m))
    ax.axhline(0, color="0.6", lw=0.8)
    ax.set_xlabel("change in mean X-H bond length (mÅ)")
    ax.set_ylabel("contribution (meV per H)")
    ax.set_title("Stretch (o) and bend/libration (x) compensate")
    fig.tight_layout()
    out = ROOT / "figures"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "fig4_xh_rule.png", dpi=300)
    fig.savefig(out / "fig4_xh_rule.svg")
    print("figures/fig4_xh_rule.png")


if __name__ == "__main__":
    main()
