"""Does the MLIP ensemble get the O-H stretch frequency vs hydrogen-bond geometry right? (F01 core check)

For every O-H donor in clean screened structures: O-H length, donor-acceptor O...O distance (nearest O to H
other than the donor, within 3.2 A), and the Gamma-point stretch frequency of that H (frequency of the mode
with the largest projection on its O-H bond, H masses). Compared with the empirical spectroscopic
correlation of Libowitzky (1999): nu = 3592 - 304e9 * exp(-d(O...O) / 0.1321) cm^-1, and with DFT
phonons (MDR phonondb force constants, PBEsol) where available.

    python -m src.isoshift_event.stretch_check
writes results/stretch_check.csv and figures/fig5_stretch_check.png
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
    import matplotlib.pyplot as plt

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
        ax.scatter(d, nu, s=10 if src != "dft_pbesol" else 30, alpha=0.5, color=colors[src], label=f"{src} (n={len(d)})",
                   marker="o" if src != "dft_pbesol" else "D")
    x = np.linspace(2.45, 3.15, 100)
    ax.plot(x, libowitzky(x), "k--", lw=1.5, label="Libowitzky 1999 (measured spectra)")
    ax.set_xlabel("donor-acceptor O...O distance (A)")
    ax.set_ylabel("O-H stretch frequency (cm$^{-1}$)")
    ax.set_title("O-H stretch vs H-bond length: models vs experiment")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "fig5_stretch_check.png", dpi=300)
    (ROOT / "results" / "stretch_check_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
