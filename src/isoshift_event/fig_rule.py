"""Figure for finding F01: isotope shift of polymorph stability vs the change in mean X-H bond length.

    python -m src.isoshift_event.fig_rule      -> figures/fig4_xh_rule.png/.svg
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COLORS = {"mace": "#0072B2", "orb": "#E69F00", "mattersim": "#009E73", "sevenn": "#CC79A7"}


def main():
    d = pd.read_csv(ROOT / "results" / "decompose_pairs.csv")
    c = d[(d.clean == True) & (d.covalent_XH == True)].copy()  # noqa: E712
    for k in ("ddF_total", "ddF_str", "ddF_perp"):
        c[k + "_H"] = c[k] / c.H_per_atom
    c["dXH_mA"] = c.dXH_mean_A * 1000
    # regime (decision 04): strong if either polymorph has mean model X-H >= 0.99 A
    st = pd.read_csv(ROOT / "results" / "decompose_structures.csv").set_index(["model", "struct_id"]).XH_mean_A
    pr = pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv").set_index(["pair_id", "model"])
    def _strong(r):
        a, b = pr.loc[(r.pair_id, r.model), ["struct_a", "struct_b"]]
        return max(st.get((r.model, a), 0), st.get((r.model, b), 0)) >= 0.99
    c["strong"] = [_strong(r) for r in c.itertuples()]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    ax = axes[2]
    for strong, mk, lab in ((True, "o", "moderate/strong H bond (max O-H >= 0.99 A)"), (False, "x", "weak H bonds on both sides")):
        g = c[c.strong == strong]
        ax.scatter(g.dXH_mA, g.ddF_total_H, s=12, alpha=0.6, marker=mk, color="#0072B2" if strong else "#D55E00",
                   label=f"{lab}: n={len(g)}")
    ax.axhline(0, color="0.6", lw=0.8)
    ax.axvline(0, color="0.6", lw=0.8)
    ax.axvspan(-5, 5, color="0.9", zorder=0)
    ax.set_xlabel("change in mean X-H bond length (mA)")
    ax.set_ylabel(r"$\Delta\Delta F_{iso}$ at 300 K (meV per H)")
    ax.set_title("Sign rule by regime (all covalent, signal cut): strong 128/134, weak 1/16")
    ax.legend(fontsize=7.5, loc="upper left")
    ax = axes[0]
    for m, g in c.groupby("model"):
        k, b = np.polyfit(g.dXH_mA, g.ddF_total_H, 1)
        r = np.corrcoef(g.dXH_mA, g.ddF_total_H)[0, 1]
        ax.scatter(g.dXH_mA, g.ddF_total_H, s=12, alpha=0.55, color=COLORS.get(m), label=f"{m}: {k:.2f} meV/H per mA, r={r:.2f}, n={len(g)}")
        x = np.linspace(c.dXH_mA.quantile(0.01), c.dXH_mA.quantile(0.99), 2)
        ax.plot(x, k * x + b, color=COLORS.get(m), lw=1.5)
    ax.axhline(0, color="0.6", lw=0.8)
    ax.axvline(0, color="0.6", lw=0.8)
    ax.set_xlabel("change in mean X-H bond length, polymorph b minus a (mA)")
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
    ax.set_xlabel("change in mean X-H bond length (mA)")
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
