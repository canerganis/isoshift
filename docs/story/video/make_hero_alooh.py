"""Hero shot: diaspore vs delta-AlOOH, slowly orbiting ball-and-stick models.

Renders 210 frames (7 s at 30 fps, 1920x1080) to docs/story/video/anim/hero_alooh/
and encodes C:/Users/can02/Videos/IsoShift/hero_alooh.mp4 with ffmpeg.

Geometry comes from the Materials Project CIFs in data/isoshift/structs. Bonds are
found by distance only (O-H < 1.2 A, Al-O < 2.1 A). H atoms are unwrapped to their
nearest O under periodic boundaries so no O-H bond is cut by the supercell edge.

Usage: .venv/Scripts/python.exe docs/story/video/make_hero_alooh.py [--no-video] [--frames 0,60,105]
"""
import argparse
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pymatgen.core import Structure

ROOT = Path(__file__).resolve().parents[3]
STRUCTS = ROOT / "data" / "isoshift" / "structs"
OUT_DIR = ROOT / "docs" / "story" / "video" / "anim" / "hero_alooh"
VIDEO = Path("C:/Users/can02/Videos/IsoShift/hero_alooh.mp4")

W, H = 1920, 1080
FPS = 30
N_FRAMES = 210
DUR = N_FRAMES / FPS

BG = "#0D1B2A"
COL = {"Al": "#9DB0C8", "O": "#F26B3A", "H": "#56B4E9", "D": "#E69F00"}
WHITE = "#F4F7FB"
GREEN = "#2FBF8F"

OH_CUT = 1.2
ALO_CUT = 2.1
RADIUS = {"Al": 0.44, "O": 0.38, "H": 0.25}  # display radii in Angstrom

PANELS = [
    dict(cif="mp-625152.cif", label="diaspore", sub="shorter O-H", scale=(2, 2, 1), cx=500),
    dict(cif="mp-23807.cif", label="\u03b4-AlOOH", sub="longer O-H", scale=(2, 2, 2), cx=1420),
]
CY = 560          # vertical centre of the models
PX_PER_A = 54.0   # same scale for both panels
CAM_D = 34.0      # camera distance in Angstrom (perspective strength)

# timeline (seconds)
T_FADE_IN = 0.5
T_HD0, T_HD1 = 2.5, 3.5       # H -> D colour fade
T_CAP0, T_CAP1 = 2.5, 3.1     # "H -> D" caption
T_FAV0, T_FAV1 = 4.0, 4.8     # "favoured with D"
YAW0, YAW1 = -26.0, 26.0      # degrees, 52 degree orbit
PITCH = 16.0


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- geometry
def build_model(cif, scale):
    s = Structure.from_file(str(STRUCTS / cif))
    s.make_supercell(scale)
    lat = s.lattice
    sym = np.array([site.specie.symbol for site in s])
    frac0 = np.array([site.frac_coords for site in s])
    # choose the cell origin that keeps the most Al-O bonds inside the block,
    # so the cut does not leave loose O or Al atoms on the faces
    al, ox = np.where(sym == "Al")[0], np.where(sym == "O")[0]
    best, frac = -1, None
    g = np.arange(8) / 8.0
    for sh in np.array(np.meshgrid(g, g, g)).reshape(3, -1).T:
        f = (frac0 + sh / np.array(scale)) % 1.0
        c = lat.get_cartesian_coords(f)
        dd = np.linalg.norm(c[al][:, None] - c[ox][None], axis=2)
        nb = (dd < ALO_CUT)
        score = nb.sum() - 4 * (nb.sum(axis=0) == 0).sum() - 4 * (nb.sum(axis=1) < 3).sum()
        if score > best:
            best, frac = score, f
    cart = lat.get_cartesian_coords(frac)
    o_idx = np.where(sym == "O")[0]
    # unwrap every H next to its nearest O (minimum image in the supercell)
    for i in np.where(sym == "H")[0]:
        df = frac[o_idx] - frac[i]
        df -= np.round(df)
        d = np.linalg.norm(lat.get_cartesian_coords(df), axis=1)
        k = int(np.argmin(d))
        cart[i] = cart[o_idx[k]] - lat.get_cartesian_coords(df[k])
    cart -= cart.mean(axis=0)
    bonds = []
    n = len(sym)
    for i in range(n):
        for j in range(i + 1, n):
            pair = {sym[i], sym[j]}
            d = np.linalg.norm(cart[i] - cart[j])
            if pair == {"O", "H"} and d < OH_CUT:
                bonds.append((i, j, "OH"))
            elif pair == {"Al", "O"} and d < ALO_CUT:
                bonds.append((i, j, "AlO"))
    return dict(xyz=cart, sym=sym, bonds=bonds)


def rot(yaw_deg, pitch_deg):
    a, b = np.radians(yaw_deg), np.radians(pitch_deg)
    # crystal axes: b -> screen x, c -> screen up, a (short axis) -> toward viewer,
    # so the channel view lines up mid-orbit
    base = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float)
    ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    return rx @ ry @ base


# ---------------------------------------------------------------- drawing
def new_canvas():
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    return fig, ax


def to_array(fig):
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].astype(np.float32) / 255.0
    plt.close(fig)
    return arr


def particles(t):
    rng = np.random.default_rng(7)
    n = 90
    x0 = rng.uniform(0, W, n)
    y0 = rng.uniform(0, H, n)
    sp = rng.uniform(4, 14, n)
    ph = rng.uniform(0, 2 * np.pi, n)
    r = rng.uniform(1.0, 2.6, n)
    al = rng.uniform(0.06, 0.22, n)
    x = (x0 + 10 * np.sin(0.35 * t + ph)) % W
    y = (y0 - sp * t) % H
    return x, y, r, al


def draw_scene(ax, models, t, glow_only=False):
    yaw = YAW0 + (YAW1 - YAW0) * (0.25 * (t / DUR) + 0.75 * smooth(t / DUR))
    R = rot(yaw, PITCH)
    zoom = 1.0 + 0.04 * (t / DUR)
    hd = smooth((t - T_HD0) / (T_HD1 - T_HD0))
    hcol = (1 - hd) * hex2rgb(COL["H"]) + hd * hex2rgb(COL["D"])
    bg = hex2rgb(BG)

    if not glow_only:
        px, py, pr, pa = particles(t)
        for x, y, r, a in zip(px, py, pr, pa):
            ax.add_patch(Circle((x, y), r, color=hex2rgb(WHITE), alpha=a, lw=0, zorder=-1e6))

    for m, panel in zip(models, PANELS):
        p = m["xyz"] @ R.T
        persp = CAM_D / (CAM_D - p[:, 2])
        sx = panel["cx"] + p[:, 0] * PX_PER_A * zoom * persp
        sy = CY - p[:, 1] * PX_PER_A * zoom * persp
        zmin, zmax = p[:, 2].min(), p[:, 2].max()
        fog = 0.5 + 0.5 * (p[:, 2] - zmin) / (zmax - zmin)  # 1 near, 0.45 far
        rad = np.array([RADIUS[s] for s in m["sym"]]) * PX_PER_A * zoom * persp

        def atom_rgb(i):
            c = hcol if m["sym"][i] == "H" else hex2rgb(COL[m["sym"][i]])
            return c

        def fogged(c, f):
            return bg + (c - bg) * f

        # bonds, trimmed to sphere surfaces
        for i, j, kind in m["bonds"]:
            if glow_only and kind != "OH":
                continue
            d = np.array([sx[j] - sx[i], sy[j] - sy[i]])
            L = np.hypot(*d)
            if L < rad[i] + rad[j] + 1:
                continue
            u = d / L
            a0 = np.array([sx[i], sy[i]]) + u * rad[i] * 0.85
            a1 = np.array([sx[j], sy[j]]) - u * rad[j] * 0.85
            z = 0.5 * (p[i, 2] + p[j, 2])
            f = 0.5 * (fog[i] + fog[j])
            pp = 0.5 * (persp[i] + persp[j])
            if kind == "AlO":
                c = fogged(0.65 * hex2rgb(COL["Al"]) + 0.35 * bg, f)
                ax.plot([a0[0], a1[0]], [a0[1], a1[1]], color=c, lw=2.6 * pp,
                        solid_capstyle="round", zorder=z - 0.01)
            else:
                c = 0.55 * hcol + 0.45 * np.ones(3)
                c = fogged(c, 0.6 + 0.4 * f)
                lw = (9.0 if glow_only else 5.5) * pp
                ax.plot([a0[0], a1[0]], [a0[1], a1[1]], color=c, lw=lw,
                        solid_capstyle="round", zorder=z - 0.01)

        # atoms as shaded spheres
        for i in range(len(m["sym"])):
            s = m["sym"][i]
            if glow_only and s != "H":
                continue
            c = atom_rgb(i)
            f = fog[i]
            z = p[i, 2]
            r = rad[i]
            if glow_only:
                ax.add_patch(Circle((sx[i], sy[i]), r * 1.25, color=c, lw=0, zorder=z))
                continue
            ax.add_patch(Circle((sx[i], sy[i]), r, color=fogged(0.45 * c, f), lw=0, zorder=z))
            for k, kk in enumerate((0.92, 0.78, 0.62, 0.46, 0.30)):
                lift = k / 4.0
                cc = c * (0.72 + 0.28 * lift) + (1 - c) * 0.22 * lift ** 2
                off = (1 - kk) * r * 0.42
                ax.add_patch(Circle((sx[i] - off, sy[i] - off), r * kk,
                                    color=fogged(np.clip(cc, 0, 1), f), lw=0,
                                    zorder=z + 1e-4 * (k + 1)))
            hr = r * 0.16
            ax.add_patch(Circle((sx[i] - r * 0.38, sy[i] - r * 0.38), hr,
                                color=fogged(np.ones(3), f), alpha=0.4, lw=0, zorder=z + 1e-3))


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.ones((H, W, 3), np.float32) * hex2rgb(BG)
    spot = np.zeros((H, W), np.float32)
    for panel in PANELS:
        d2 = ((xx - panel["cx"]) / 520.0) ** 2 + ((yy - CY) / 460.0) ** 2
        spot += np.exp(-d2)
    bg += spot[..., None] * np.array([0.035, 0.05, 0.075], np.float32)
    return bg


def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return (1.0 - 0.5 * smooth((r - 0.55) / 0.9))[..., None]


def font(size, bold=False):
    names = ["seguisb.ttf", "segoeuib.ttf"] if bold else ["segoeui.ttf"]
    for nm in names:
        p = Path("C:/Windows/Fonts") / nm
        if p.exists():
            return ImageFont.truetype(str(p), size)
    dj = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(str(dj), size)


def text_layer(t):
    """RGBA text overlay for time t."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    wr = tuple(int(255 * v) for v in hex2rgb(WHITE))
    f_lab, f_sub = font(64, bold=True), font(44)
    for panel in PANELS:
        d.text((panel["cx"], 108), panel["label"], font=f_lab, fill=wr + (255,), anchor="mm")
        d.text((panel["cx"], 172), panel["sub"], font=f_sub, fill=wr + (200,), anchor="mm")
    a = smooth((t - T_CAP0) / (T_CAP1 - T_CAP0))
    if a > 0:
        f_hd = font(60, bold=True)
        cx, cy = W // 2, CY
        # "H" in H blue, arrow white, "D" in D orange
        parts = [("H", hex2rgb(COL["H"])), (" \u2192 ", hex2rgb(WHITE)), ("D", hex2rgb(COL["D"]))]
        widths = [d.textlength(s, font=f_hd) for s, _ in parts]
        x = cx - sum(widths) / 2
        for (s, c), wdt in zip(parts, widths):
            d.text((x, cy), s, font=f_hd, fill=tuple(int(255 * v) for v in c) + (int(255 * a),), anchor="lm")
            x += wdt
    b = smooth((t - T_FAV0) / (T_FAV1 - T_FAV0))
    if b > 0:
        gr = tuple(int(255 * v) for v in hex2rgb(GREEN))
        dy = 14 * (1 - b)
        d.text((PANELS[0]["cx"], 985 + dy), "favoured with D", font=font(54, bold=True),
               fill=gr + (int(255 * b),), anchor="mm")
    return img


def glow_text(img, radius=10, strength=0.6):
    g = img.filter(ImageFilter.GaussianBlur(radius))
    arr = np.asarray(g).astype(np.float32) / 255.0
    return arr[..., :3] * arr[..., 3:4] * strength


def blur(arr, radius):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255.0


def screen(a, b):
    return 1 - (1 - a) * (1 - np.clip(b, 0, 1))


_MODELS = None
_BG = None
_VIG = None


def _init():
    global _MODELS, _BG, _VIG
    _MODELS = [build_model(p["cif"], p["scale"]) for p in PANELS]
    _BG = background()
    _VIG = vignette()


def render_frame(k):
    t = k / FPS
    fig, ax = new_canvas()
    fig.patch.set_alpha(0)
    ax.add_patch(plt.Rectangle((0, 0), W, H, color="black", zorder=-1e7))
    draw_scene(ax, _MODELS, t)
    scene = to_array(fig)

    fig, ax = new_canvas()
    ax.add_patch(plt.Rectangle((0, 0), W, H, color="black", zorder=-1e7))
    draw_scene(ax, _MODELS, t, glow_only=True)
    glow_src = to_array(fig)

    img = screen(_BG, scene)
    img = screen(img, 0.9 * blur(glow_src, 14) + 0.5 * blur(glow_src, 32))
    img = screen(img, 0.35 * blur(scene, 8))
    img = img * _VIG

    tl = text_layer(t)
    img = screen(img, glow_text(tl, 12, 0.35))
    ta = np.asarray(tl).astype(np.float32) / 255.0
    img = img * (1 - ta[..., 3:4]) + ta[..., :3] * ta[..., 3:4]

    img = img * smooth(t / T_FADE_IN) if t < T_FADE_IN else img
    out = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(out).save(OUT_DIR / f"f{k:03d}.png")
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--frames", default="")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _init()
    for p, m in zip(PANELS, _MODELS):
        n_oh = sum(1 for b in m["bonds"] if b[2] == "OH")
        n_alo = sum(1 for b in m["bonds"] if b[2] == "AlO")
        d_oh = [np.linalg.norm(m["xyz"][i] - m["xyz"][j]) for i, j, k in m["bonds"] if k == "OH"]
        print(f"{p['cif']}: supercell {p['scale']}, atoms {len(m['sym'])}, "
              f"O-H bonds {n_oh} (mean {np.mean(d_oh):.3f} A), Al-O bonds {n_alo}")

    frames = [int(x) for x in args.frames.split(",") if x] or list(range(N_FRAMES))
    with Pool(min(12, os.cpu_count() or 4), initializer=_init) as pool:
        for _ in pool.imap_unordered(render_frame, frames):
            pass
    print(f"rendered {len(frames)} frames to {OUT_DIR}")

    if not args.no_video and len(frames) == N_FRAMES:
        VIDEO.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
               "-i", str(OUT_DIR / "f%03d.png"), "-c:v", "libx264", "-preset", "slow",
               "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(VIDEO)]
        subprocess.run(cmd, check=True)
        print(f"wrote {VIDEO}")


if __name__ == "__main__":
    sys.exit(main())
