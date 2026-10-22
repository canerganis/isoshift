"""Video slides, v3 design: dark theme, one claim per slide, a progress bar of the story.

Run from the repo root:  .venv/Scripts/python.exe docs/story/video/make_slides_v3.py

Writes the 12 slide PNGs that build_video.py uses (same file names as the earlier kit).
Numbers and claim wording follow decisions 05, 07 and 11 (no "first", no "discovery");
AlOOH values from docs/findings/CARD-AlOOH.md, stretch ratios from decision 07 F03.
Bottom 130 px of the centre are kept clear for burned-in captions.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
W, H, DPI = 1920, 1080, 100
BG, PANEL, PANEL2 = "#0D1B2A", "#15263B", "#1D3452"
INK, MUTED, FAINT = "#F4F7FB", "#9DB0C8", "#3A5070"
BLUE, ORANGE, VERM, GREEN = "#56B4E9", "#E69F00", "#F26B3A", "#2FBF8F"
SANS = ["Segoe UI", "Segoe UI Symbol", "DejaVu Sans"]
NUM = ["Bahnschrift", "Segoe UI", "DejaVu Sans"]
X0, XR = 90, 1830
P = 1.0  # animation progress 0..1 for the slides that build up; 1 = final still
FRAME = None  # (dir, index) while rendering animation frames
ANIM_FRAMES = 36  # 1.2 s at 30 fps


def ease(p):
    return 1 - (1 - p) ** 3


SECTIONS = ["Claim", "Method", "Result", "Check", "Prediction", "Lab test", "Process", "Limits"]


def px(size):
    return size * 72 / DPI


def canvas(section):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    # story progress bar
    seg_w = (XR - X0 - 7 * 10) / 8
    for i, name in enumerate(SECTIONS):
        x = X0 + i * (seg_w + 10)
        col = BLUE if i == section else (FAINT if i > section else "#2B4A6E")
        ax.add_patch(Rectangle((x, 30), seg_w, 8, color=col, lw=0))
        text(ax, x, 48, name.upper(), 22, INK if i == section else MUTED, "bold" if i == section else "normal")
    return fig, ax


def text(ax, x, y, s, size, color=INK, weight="normal", family=None, ha="left", va="top", **kw):
    return ax.text(x, y, s, fontsize=px(size), color=color, weight=weight, family=family or SANS,
                   ha=ha, va=va, **kw)


def wrap(ax, x, y, s, size, width, line_h=1.22, **kw):
    r = ax.figure.canvas.get_renderer()
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        t = text(ax, 0, -500, trial, size, **kw)
        wid = t.get_window_extent(renderer=r).width
        t.remove()
        if wid > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    for i, ln in enumerate(lines):
        text(ax, x, y + i * size * line_h, ln, size, **kw)
    return y + len(lines) * size * line_h


def title(ax, s, y=100, size=72, color=INK):
    return wrap(ax, X0, y, s, size, XR - X0, 1.12, color=color, weight="bold")


def box(ax, x, y, w, h, fc=PANEL, ec=None, lw=0, r=22):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec or fc, lw=lw))


def chip(ax, x, y, s, color, size=30, fill=False):
    r = ax.figure.canvas.get_renderer()
    t = text(ax, 0, -500, s, size, weight="bold")
    w = t.get_window_extent(renderer=r).width
    t.remove()
    box(ax, x, y, w + 40, size * 1.75, fc=color if fill else BG, ec=color, lw=3, r=size * 0.85)
    text(ax, x + 20, y + size * 0.3, s, size, BG if fill else color, "bold")
    return x + w + 40


def arrow(ax, x1, y1, x2, y2, color=MUTED, lw=4, ms=34):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=ms,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0))


def image_card(ax, path, x, y, w):
    img = mpimg.imread(path)
    h = w * img.shape[0] / img.shape[1]
    box(ax, x - 14, y - 14, w + 28, h + 28, fc="white", r=18)
    ax.imshow(img, extent=(x, x + w, y + h, y), interpolation="lanczos", zorder=3)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    return y + h


def dots(ax, x, y, n, n_hi, cols, d, gap, hi=BLUE, lo=VERM, hi_first=True):
    for i in range(n):
        r, c = divmod(i, cols)
        col = hi if (i < n_hi) == hi_first else lo
        ax.add_patch(Circle((x + c * (d + gap) + d / 2, y + r * (d + gap) + d / 2), d / 2, color=col, lw=0))


def save(fig, name):
    if FRAME is not None:
        d, k = FRAME
        fig.savefig(d / f"f{k:03d}.png", dpi=DPI, facecolor=BG)
        plt.close(fig)
        return
    fig.savefig(OUT / name, dpi=DPI, facecolor=BG)
    plt.close(fig)
    img = mpimg.imread(OUT / name)
    assert img.shape[:2] == (H, W), (name, img.shape)
    print("wrote", name)


def bond(ax, x, y, length, label, sub, good, iso="D"):
    """O-H...O drawn to scale-ish: covalent O-H of `length` px, then a dashed H...O."""
    o1, h = x, x + length
    o2 = x + 360
    ax.plot([o1, h], [y, y], color=INK, lw=9, solid_capstyle="round", zorder=2)
    ax.plot([h, o2], [y, y], color=MUTED, lw=4, ls=(0, (3, 3)), zorder=1)
    for cx, lab, col, r in ((o1, "O", VERM, 46), (o2, "O", VERM, 46), (h, iso, ORANGE if iso == "D" else BLUE, 34)):
        ax.add_patch(Circle((cx, y), r, color=col, lw=0, zorder=3))
        text(ax, cx, y + 2, lab, 40, BG, "bold", ha="center", va="center", zorder=4)
    text(ax, x - 46, y + 80, label, 46, INK, "bold")
    text(ax, x - 46, y + 138, sub, 36, MUTED)
    if good:
        chip(ax, x + 170, y + 84, "favoured with D", GREEN, 28, fill=True)


def slide_01():
    fig, ax = canvas(0)
    text(ax, X0, 105, "IsoShift", 150, INK, "bold")
    chip(ax, X0, 292, "THE SHORT-BOND RULE", ORANGE, 34, fill=True)
    text(ax, X0, 380, "Deuteration favours the polymorph", 64, INK, "bold")
    text(ax, X0, 458, "with the shorter O-H bonds", 64, BLUE, "bold")
    E = ease(P)
    text(ax, X0 - 6, 560, f"{round(185 * E)}/212", 210, BLUE, "bold", family=NUM)
    text(ax, X0, 800, "model evaluations agree, moderate-to-strong H bonds", 40, INK)
    text(ax, X0, 856, "Baseline (one fixed sign): 131/212", 40, MUTED)
    box(ax, 1360, 380, XR - 1360, 520, fc=PANEL)
    iso = "D" if E > 0.5 else "H"
    bond(ax, 1430, 480, 105, "diaspore", "shorter O-H", E > 0.95, iso)
    bond(ax, 1430, 720, 165, "δ-AlOOH", "longer O-H", False, iso)
    save(fig, "slide_01_title.png")


def slide_02():
    fig, ax = canvas(1)
    title(ax, "One phonon calculation gives both isotopes")
    y = 330
    steps = [("Crystal pair", "polymorphs a and b"), ("ML potential", "MACE · ORB · MatterSim"),
             ("Force constants", "no mass in them")]
    x = X0
    for i, (a, b) in enumerate(steps):
        box(ax, x, y, 350, 200, fc=PANEL)
        text(ax, x + 26, y + 38, a, 40, INK, "bold")
        text(ax, x + 26, y + 112, b, 29, MUTED)
        if i < 2:
            arrow(ax, x + 358, y + 100, x + 412, y + 100)
        x += 420
    # split into H and D
    sx = x - 70
    arrow(ax, sx, y + 70, sx + 120, y - 20, BLUE)
    arrow(ax, sx, y + 130, sx + 120, y + 220, ORANGE)
    box(ax, sx + 130, y - 90, 360, 130, fc=PANEL2, ec=BLUE, lw=3)
    text(ax, sx + 160, y - 60, r"mass H  →  $F_\mathrm{H}$", 44, BLUE, "bold")
    box(ax, sx + 130, y + 160, 360, 130, fc=PANEL2, ec=ORANGE, lw=3)
    text(ax, sx + 160, y + 190, r"mass D  →  $F_\mathrm{D}$", 44, ORANGE, "bold")
    box(ax, X0, 640, XR - X0, 140, fc=PANEL)
    text(ax, X0 + 40, 668, r"$\Delta\Delta F_\mathrm{iso} = [F_\mathrm{D} - F_\mathrm{H}]_b - [F_\mathrm{D} - F_\mathrm{H}]_a$",
         54, INK)
    text(ax, X0, 820, "The static energy gap between polymorphs cancels, so its error drops out.", 44, GREEN, "bold")
    x = chip(ax, X0, 890, "SevenNet: sign votes only", MUTED, 30)
    save(fig, "slide_02_method.png")


def slide_03():
    fig, ax = canvas(2)
    title(ax, "The short-bond rule: shorter O-H bonds win")
    image_card(ax, ROOT / "figures" / "fig_headline.png", X0 + 14, 214, 1110)
    x = 1300
    text(ax, x, 220, "220", 120, BLUE, "bold", family=NUM)
    text(ax, x, 360, "polymorph pairs screened", 38, INK)
    text(ax, x, 450, "0.11 to 0.13", 96, BLUE, "bold", family=NUM)
    wrap(ax, x, 570, "meV per H for each mÅ of O-H length change", 38, XR - x, color=INK)
    box(ax, x, 700, XR - x, 200, fc=PANEL)
    text(ax, x + 30, 725, "O-H stretch drives it", 40, ORANGE, "bold")
    wrap(ax, x + 30, 790, "bending and libration cancel about half", 36, XR - x - 60, color=MUTED)
    save(fig, "slide_03_headline.png")


def slide_03b():
    fig, ax = canvas(2)
    title(ax, "The scoreboard")
    E = ease(P)
    text(ax, X0 - 6, 200, f"{round(185 * E)}/212", 200, BLUE, "bold", family=NUM)
    text(ax, X0, 430, "model evaluations agree with the rule", 40, INK)
    text(ax, X0, 482, "where H bonds are moderate or strong", 40, MUTED)
    bw = 780
    for i, (lab, v, col) in enumerate((("Rule", 185, BLUE), ("Baseline, one fixed sign", 131, MUTED))):
        yy = 585 + i * 120
        text(ax, X0, yy, lab, 34, INK)
        ax.add_patch(Rectangle((X0, yy + 50), bw, 34, color=FAINT, lw=0))
        ax.add_patch(Rectangle((X0, yy + 50), bw * v / 212 * E, 34, color=col, lw=0))
        text(ax, X0 + bw * v / 212 * E + 16, yy + 42, str(round(v * E)), 40, col, "bold", family=NUM)
    x = 1060
    box(ax, x, 200, XR - x, 700, fc=PANEL)
    text(ax, x + 40, 230, "Counted per pair", 44, INK, "bold")
    text(ax, x + 40, 300, f"{round(74 * E)} right", 56, BLUE, "bold", family=NUM)
    text(ax, x + 330, 300, f"{round(10 * E)} wrong", 56, VERM, "bold", family=NUM)
    text(ax, x + 640, 312, "0 ties", 40, MUTED, family=NUM)
    dots(ax, x + 44, 400, round(84 * E), 74, 14, 38, 12)
    wrap(ax, x + 40, 760, "All 10 wrong pairs contain one Al(OH)₃ structure, mp-985293, "
         "where bending and libration outweigh the stretch.", 34, XR - x - 80, color=VERM)
    save(fig, "slide_03b_counts_zoom.png")


def slide_03c():
    fig, ax = canvas(2)
    title(ax, "Where the short-bond rule stops working")
    y0, x1, xb, x2 = 330, X0, 760, XR
    ax.add_patch(Rectangle((x1, y0), xb - x1, 300, color="#3A2420", lw=0))
    ax.add_patch(Rectangle((xb, y0), x2 - xb, 300, color="#14304A", lw=0))
    ax.plot([xb, xb], [y0 - 30, y0 + 330], color=INK, lw=4)
    text(ax, xb, y0 + 345, "0.99 Å", 36, INK, "bold", ha="center")
    text(ax, x1 + 40, y0 + 30, "weak H bonds", 44, VERM, "bold")
    text(ax, x1 + 40, y0 + 100, "2/20", 130, VERM, "bold", family=NUM)
    text(ax, xb + 50, y0 + 30, "moderate to strong H bonds", 44, BLUE, "bold")
    text(ax, xb + 50, y0 + 100, f"{round(185 * ease(P))}/212", 130, BLUE, "bold", family=NUM)
    arrow(ax, x1, y0 + 420, x2, y0 + 420, MUTED, 3, 26)
    text(ax, (x1 + x2) / 2, y0 + 440, "larger mean model O-H of the pair  →", 32, MUTED, ha="center")
    box(ax, X0, 840, XR - X0, 92, fc=BG, ec=ORANGE, lw=3, r=18)
    text(ax, (X0 + XR) / 2, 862, "We chose that boundary after seeing the data, and we say so.", 40, ORANGE, "bold",
         ha="center")
    save(fig, "slide_03c_weak_side_zoom.png")


def slide_04():
    fig, ax = canvas(3)
    title(ax, "Do the models get the O-H stretch right?")
    image_card(ax, ROOT / "figures" / "fig5_stretch_check.png", X0 + 14, 214, 980)
    x = 1180
    text(ax, x, 220, "Model slope ÷ measured slope", 38, INK, "bold")
    text(ax, x, 272, "O···O 2.50 to 2.80 Å, mineral spectra", 32, MUTED)
    bw = 520
    for i, (m, v) in enumerate((("MACE", 0.91), ("ORB", 0.92), ("MatterSim", 0.92))):
        yy = 360 + i * 120
        text(ax, x, yy, m, 36, INK)
        ax.add_patch(Rectangle((x, yy + 50), bw, 30, color=FAINT, lw=0))
        ax.add_patch(Rectangle((x, yy + 50), bw * v * ease(P), 30, color=GREEN, lw=0))
        text(ax, x + bw + 20, yy + 38, f"{v * ease(P):.2f}", 44, GREEN, "bold", family=NUM)
    ax.plot([x + bw, x + bw], [345, 720], color=INK, lw=2, ls=(0, (4, 4)))
    text(ax, x + bw, 724, "1.00", 28, MUTED, ha="center")
    box(ax, x, 800, XR - x, 100, fc=BG, ec=ORANGE, lw=3, r=18)
    text(ax, x + (XR - x) / 2, 828, "A consistency check, not a validation", 32, ORANGE, "bold", ha="center")
    save(fig, "slide_04_stretch_check.png")


def slide_05():
    fig, ax = canvas(4)
    y = title(ax, "Prediction: deuterium pushes the diaspore → δ-AlOOH boundary up", size=64)
    chip(ax, X0, y + 20, "EXPLORATORY SIGN PREDICTION", ORANGE, 30)
    # pressure axis, 6 to 16 GPa
    ax0, ax1, p0, p1 = 300, 1340, 6.0, 16.0
    def X(p):
        return ax0 + (p - p0) / (p1 - p0) * (ax1 - ax0)
    ya = 760
    arrow(ax, ax0, ya, ax1 + 40, ya, MUTED, 3, 26)
    for p in (6, 8, 10, 12, 14, 16):
        ax.plot([X(p), X(p)], [ya - 10, ya + 10], color=MUTED, lw=3)
        text(ax, X(p), ya + 22, str(p), 30, MUTED, ha="center", family=NUM)
    text(ax, ax1 + 60, ya - 20, "GPa", 32, MUTED)
    text(ax, ax0 - 10, 460, "300 K", 40, INK, "bold", ha="right")
    for i, (m, ph, pd, dp) in enumerate((("MACE", 8.76, 10.09, "+1.33 GPa"), ("ORB", 13.00, 14.13, "+1.13 GPa"))):
        yy = 540 + i * 120
        text(ax, ax0 - 10, yy - 22, m, 36, INK, ha="right")
        ax.plot([ax0, ax1], [yy, yy], color=FAINT, lw=2)
        ax.add_patch(Circle((X(ph), yy), 16, color=BLUE, lw=0, zorder=3))
        E = ease(P)
        xd = X(ph) + (X(pd) - X(ph)) * E
        ax.add_patch(Circle((xd, yy), 16, color=ORANGE, lw=0, zorder=3))
        if xd - X(ph) > 40:
            arrow(ax, X(ph) + 18, yy, xd - 18, yy, ORANGE, 4, 24)
        if E > 0.85:
            text(ax, X(pd) + 30, yy - 26, dp, 44, ORANGE, "bold", family=NUM)
    text(ax, ax0, 415, "●", 30, BLUE)
    text(ax, ax0 + 34, 412, "boundary with H", 30, BLUE)
    text(ax, ax0 + 330, 415, "●", 30, ORANGE)
    text(ax, ax0 + 364, 412, "with D", 30, ORANGE)
    text(ax, ax0, 830, "About 1000 K: +0.7 to +0.9 GPa in MACE, ORB and MatterSim, same sign", 34, INK)
    text(ax, ax0, 880, "MACE H root extrapolated below 10 GPa. Harmonic physics leaves out the proton disorder of δ-AlOOH.",
         26, MUTED)
    box(ax, 1480, 380, XR - 1480, 300, fc=PANEL)
    wrap(ax, 1510, 410, "δ-AlOOH: a possible deep-Earth water carrier", 38, XR - 1540, color=INK, weight="bold")
    save(fig, "slide_05_alooh_card.png")


def slide_06():
    fig, ax = canvas(5)
    title(ax, "A direct lab test")
    import random
    rnd = random.Random(4)
    for i, (name, n_d, x) in enumerate((("diaspore", 13, X0), ("δ-AlOOH", 13, X0 + 560))):
        box(ax, x, 240, 500, 420, fc=PANEL)
        text(ax, x + 30, 262, name, 44, INK, "bold")
        pts = [(x + 60 + 380 * rnd.random(), 360 + 260 * rnd.random()) for _ in range(28)]
        for j, (a, b) in enumerate(pts):
            ax.add_patch(Circle((a, b), 15, color=ORANGE if j < n_d else BLUE, lw=0))
    text(ax, X0 + 530, 430, "⇄", 70, MUTED, ha="center")
    text(ax, X0, 690, "coexisting polymorphs: measure D/H in each phase (schematic)", 34, MUTED)
    ax.add_patch(Circle((X0 + 15, 755), 15, color=BLUE, lw=0))
    text(ax, X0 + 42, 738, "H", 32, BLUE)
    ax.add_patch(Circle((X0 + 115, 755), 15, color=ORANGE, lw=0))
    text(ax, X0 + 142, 738, "D", 32, ORANGE)
    x = 1250
    wrap(ax, x, 250, "Boundary isotope shift and D/H fractionation between the two phases", 46, XR - x,
         color=INK, weight="bold")
    wrap(ax, x, 480, "linked through isotope free energy, up to a coupling term R (M02). Equal only when R = 0.",
         32, XR - x, color=MUTED)
    box(ax, X0, 800, XR - X0, 110, fc=PANEL2)
    text(ax, (X0 + XR) / 2, 826, "So D/H partitioning between coexisting polymorphs is a direct test.", 44, BLUE,
         "bold", ha="center")
    save(fig, "slide_06_m02_bridge.png")


def slide_07():
    fig, ax = canvas(6)
    title(ax, "How an AI team ran the work")
    cards = [("Literature agents", "182 Valency Bond queries, every one logged", BLUE),
             ("Predictions first", "committed to git before the data were read", ORANGE),
             ("Model councils", "three models argue each claim, dissent recorded", GREEN),
             ("Blind rewrite", "a second model reimplemented the calculation and matched", VERM)]
    cw, ch = (XR - X0 - 40) / 2, 300
    for i, (a, b, col) in enumerate(cards):
        r, c = divmod(i, 2)
        x, y = X0 + c * (cw + 40), 240 + r * (ch + 40)
        box(ax, x, y, cw, ch, fc=PANEL)
        ax.add_patch(Rectangle((x, y + 30), 10, ch - 60, color=col, lw=0))
        text(ax, x + 50, y + 40, a, 52, col, "bold")
        wrap(ax, x + 50, y + 130, b, 38, cw - 100, color=INK)
    save(fig, "slide_07_ai_process.png")


def slide_07c():
    fig, ax = canvas(6)
    title(ax, "One literature value, traced")
    steps = [("Bond query", "brucite Mg(OH)₂ Mg(OD)₂ lattice parameters, isotope effect", INK),
             ("Source", "Chakoumakos et al. 2013, doi 10.2138/am.2013.4202", INK),
             ("Value", "Mg(OH)₂ volume 0.31% larger than Mg(OD)₂, 295 K, neutron diffraction", INK),
             ("First pass", "\"about 0.3%\" with no quote: not accepted", VERM),
             ("Decision", "quote recorded, gate passed, sign right in 4 of 4 models", GREEN)]
    cw = (XR - X0 - 4 * 30) / 5
    for i, (a, b, col) in enumerate(steps):
        x = X0 + i * (cw + 30)
        box(ax, x, 250, cw, 560, fc=PANEL, ec=col if col != INK else PANEL, lw=3)
        text(ax, x + 24, 275, f"{i + 1}", 60, col if col != INK else BLUE, "bold", family=NUM)
        text(ax, x + 24, 370, a, 36, col if col != INK else INK, "bold")
        wrap(ax, x + 24, 440, b, 30, cw - 48, 1.25, color=INK if col == INK else col)
        if i < 4:
            arrow(ax, x + cw + 2, 530, x + cw + 28, 530, MUTED, 3, 22)
    save(fig, "slide_07c_bond_trace.png")


def slide_07b():
    fig, ax = canvas(6)
    title(ax, "Committed before the data")
    ty = 470
    ax.plot([X0 + 40, XR - 40], [ty, ty], color=FAINT, lw=6)
    events = [("21 Oct 21:36", "f3ac0ac", "P04 blind prediction:\nD/H fractionation", BLUE),
              ("21 Oct 21:43", "e7ee2d5", "measured data\ncommitted, unread", MUTED),
              ("22 Oct 01:15", "bec68d7", "P05 blind prediction:\nice boundaries", BLUE),
              ("22 Oct 01:27", "2eb6b8a", "F07 scored:\nwrong sign, failed", VERM)]
    xs = [X0 + 120, X0 + 560, X0 + 1060, X0 + 1500]
    for (when, sha, what, col), x in zip(events, xs):
        ax.add_patch(Circle((x, ty), 24, color=col, lw=0, zorder=3))
        text(ax, x, ty - 150, when, 36, INK, "bold", ha="center")
        text(ax, x, ty - 95, sha, 32, col, family=["Consolas", "DejaVu Sans Mono"], ha="center")
        text(ax, x, ty + 50, what, 32, col if col != MUTED else INK, ha="center", linespacing=1.3)
    text(ax, (xs[0] + xs[1]) / 2, ty + 190, "7 minutes", 40, BLUE, "bold", ha="center")
    text(ax, (xs[2] + xs[3]) / 2, ty + 190, "the failure is reported", 36, VERM, "bold", ha="center")
    box(ax, X0, 780, XR - X0, 110, fc=PANEL)
    text(ax, X0 + 40, 808, "F06: a blind reimplementation matches to 1e-9 meV/atom. It checks the code, not the physics.",
         34, INK)
    save(fig, "slide_07b_commit_timeline.png")


def slide_08():
    fig, ax = canvas(7)
    title(ax, "Limits")
    items = [("Blind tests", "F07 ice boundaries failed, F02 mixed (details in repo)"),
             ("Harmonic physics", "no proton tunnelling"),
             ("Shared training data", "three models agreeing are not three validations")]
    cw = (XR - X0 - 2 * 30) / 3
    for i, (a, b) in enumerate(items):
        x = X0 + i * (cw + 30)
        box(ax, x, 230, cw, 330, fc=PANEL)
        ax.add_patch(Rectangle((x + 30, 260), 60, 8, color=VERM, lw=0))
        text(ax, x + 30, 290, a, 44, VERM, "bold")
        wrap(ax, x + 30, 370, b, 36, cw - 60, color=INK)
    text(ax, (X0 + XR) / 2, 640, "Code, data and every decision are public", 44, INK, ha="center")
    box(ax, X0 + 260, 720, XR - X0 - 520, 140, fc=PANEL2, ec=BLUE, lw=3)
    text(ax, (X0 + XR) / 2, 752, "github.com/canerganis/isoshift", 66, BLUE, "bold", ha="center")
    save(fig, "slide_08_limits_repo.png")


ANIMATED = {"slide_01_title": "slide_01", "slide_03b_counts_zoom": "slide_03b", "slide_03c_weak_side_zoom": "slide_03c",
            "slide_04_stretch_check": "slide_04", "slide_05_alooh_card": "slide_05"}


def render_animations():
    """Frames 0..ANIM_FRAMES-1 for each animated slide into anim/<slide>/; build_video.py plays them first."""
    global P, FRAME
    for stem, fn in ANIMATED.items():
        d = OUT / "anim" / stem
        d.mkdir(parents=True, exist_ok=True)
        for k in range(ANIM_FRAMES):
            P, FRAME = k / (ANIM_FRAMES - 1), (d, k)
            globals()[fn]()
        print("animated", stem)
    P, FRAME = 1.0, None


if __name__ == "__main__":
    for f in (slide_01, slide_02, slide_03, slide_03b, slide_03c, slide_04, slide_05, slide_06,
              slide_07, slide_07c, slide_07b, slide_08):
        f()
    render_animations()
