"""Regenerate the video slides changed by decision 12 action 4 (visual-only fixes).

Run from the repo root:  .venv/Scripts/python.exe docs/story/video/make_slides_d12.py

Slides 01 and 03 are edited as overlays on the committed d14c125 PNGs (read from git,
so reruns are idempotent). Slides 06, 07b, 07c and 08 are drawn from scratch in the
kit style: 1920x1080, white background, Arial, Okabe-Ito blue and vermillion, all text
48 px or larger. Narration and captions are not touched.
"""
import io
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE_COMMIT = "d14c125"
W, H, DPI = 1920, 1080, 100
INK, BLUE, VERM, GREY = "#141414", "#0072B2", "#D55E00", "#666666"
SANS, MONO = "Arial", "Consolas"
X0, XMAX = 90, 1830


def px(size):
    """Font size in points for a given pixel em size at 100 dpi."""
    return size * 72 / DPI


def canvas(base_png=None):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    if base_png is not None:
        ax.imshow(base_png, extent=(0, W, H, 0), interpolation="none")
        ax.set_xlim(0, W)
        ax.set_ylim(H, 0)
    return fig, ax


def text(ax, x, y, s, size, color=INK, weight="normal", family=SANS, ha="left"):
    return ax.text(x, y, s, fontsize=px(size), color=color, weight=weight,
                   family=family, ha=ha, va="top")


def wrap(ax, x, y, s, size, width, line_h=1.25, **kw):
    """Draw s wrapped to width pixels; return y below the last line."""
    fig = ax.figure
    r = fig.canvas.get_renderer()
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


def title(ax, s):
    text(ax, X0, 52, s, 84, weight="bold")
    ax.add_patch(Rectangle((X0, 160), 261, 9, color=BLUE, lw=0))


def save(fig, name):
    fig.savefig(OUT / name, dpi=DPI, facecolor="white")
    plt.close(fig)
    img = mpimg.imread(OUT / name)
    assert img.shape[:2] == (H, W), (name, img.shape)
    print("wrote", name, img.shape[1], "x", img.shape[0])


def base(name):
    raw = subprocess.run(["git", "show", f"{BASE_COMMIT}:docs/story/video/{name}"],
                         cwd=ROOT, check=True, capture_output=True).stdout
    return mpimg.imread(io.BytesIO(raw), format="png")


def slide_01():
    fig, ax = canvas(base("slide_01_title.png"))
    ax.add_patch(Rectangle((60, 438), 1800, 152, color="white", lw=0))
    text(ax, X0, 440, "185 of 212 model evaluations (baseline 131),", 60, BLUE, "bold")
    text(ax, X0, 518, "moderate-to-strong H bonds", 56)
    save(fig, "slide_01_title.png")


def slide_03():
    fig, ax = canvas(base("slide_03_headline.png"))
    text(ax, 1880, 52, "Slope 0.11 to 0.13 meV per H per mÅ", 48, ha="right")
    text(ax, 1880, 114, "screen-wide, all X-H rows", 48, BLUE, "bold", ha="right")
    save(fig, "slide_03_headline.png")


def slide_06():
    fig, ax = canvas()
    title(ax, "A direct test")
    y = wrap(ax, X0, 250, "Boundary isotope shift and D/H fractionation between the two phases",
             76, XMAX - X0, 1.2, weight="bold")
    y = wrap(ax, X0, y + 30, "linked through isotope free energy, up to a coupling term R (M02)",
             56, XMAX - X0)
    y = wrap(ax, X0, y + 10, "Equal only when R = 0", 52, XMAX - X0, color=GREY)
    wrap(ax, X0, y + 60, "So D/H partitioning between coexisting polymorphs is a direct test.",
         60, XMAX - X0, color=BLUE)
    save(fig, "slide_06_m02_bridge.png")


def slide_07b():
    fig, ax = canvas()
    title(ax, "Committed before the data")
    rows = [
        ("21 Oct 21:36", "f3ac0ac", "P04 blind prediction: D/H fractionation", INK),
        ("21 Oct 21:43", "e7ee2d5", "Measured data committed, still unread", INK),
        ("22 Oct 01:15", "bec68d7", "P05 blind prediction: ice boundaries", INK),
        ("22 Oct 01:27", "2eb6b8a", "F07 scored: Ih-II and Ih-III wrong sign, failed", VERM),
    ]
    y = 230
    for when, sha, what, col in rows:
        text(ax, X0, y, when, 52, weight="bold")
        text(ax, 450, y + 2, sha, 52, BLUE, family=MONO)
        y = max(y + 130, wrap(ax, 700, y, what, 52, XMAX - 700, 1.2, color=col) + 40)
    ax.plot([X0, XMAX], [y, y], color="#dddddd", lw=3)
    wrap(ax, X0, y + 30, "F06: a blind reimplementation matches to 1e-9 meV/atom. "
         "It checks the code, not the physics.", 52, XMAX - X0, 1.2)
    save(fig, "slide_07b_commit_timeline.png")


def slide_07c():
    fig, ax = canvas()
    title(ax, "One literature value, traced")
    rows = [
        ("Bond search", "validation sweep, brucite queries: Mg(OH)2 Mg(OD)2 "
                       "lattice parameters, isotope effect", INK),
        ("Source", "Chakoumakos et al. 2013, doi 10.2138/am.2013.4202", INK),
        ("Value", "Mg(OH)2 volume 0.31% larger than Mg(OD)2, room temperature "
                  "(295 K), neutron diffraction", INK),
        ("First pass", "\"about 0.3%\" with no quote: not accepted", VERM),
        ("Decision", "Used: quote recorded, gate passed, sign right in 4 of 4 models", BLUE),
    ]
    y = 225
    for lab, val, col in rows:
        text(ax, X0, y, lab, 50, weight="bold")
        y = wrap(ax, 420, y, val, 50, XMAX - 420, 1.18, color=col) + 34
    save(fig, "slide_07c_bond_trace.png")


def slide_08():
    fig, ax = canvas()
    title(ax, "Limits")
    bullets = [
        "Blind tests: F07 ice boundaries failed, F02 mixed (details in repo)",
        "Harmonic physics, no proton tunnelling",
        "The potentials share similar training data, so three models are not three validations",
    ]
    y = 225
    for b in bullets:
        ax.add_patch(Circle((107, y + 22), 16, color=VERM, lw=0))
        y = wrap(ax, 160, y, b, 58, XMAX - 160, 1.25) + 34
    y = max(y, 720)
    ax.plot([X0, XMAX], [y, y], color="#dddddd", lw=3)
    text(ax, X0, y + 40, "Code, data and every decision are public", 56)
    text(ax, X0, y + 125, "https://github.com/canerganis/isoshift", 76, BLUE, "bold")
    save(fig, "slide_08_limits_repo.png")


if __name__ == "__main__":
    for f in (slide_01, slide_03, slide_06, slide_07b, slide_07c, slide_08):
        f()
