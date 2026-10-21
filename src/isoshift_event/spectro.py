"""Decision 04 item 5, step A: model differential O-H spectroscopy for real oxyhydroxide polymorph pairs.

For each structure and model (cached force constants, H masses, Gamma point = what IR/Raman probe):
per H, the frequency of its O-H stretch, in-plane bend (delta OH, in the plane of O-H and the H...O
acceptor) and out-of-plane bend (gamma OH), each as the projection-weighted mean over modes above
500 cm-1 (bends) or 1500 cm-1 (stretch), averaged over symmetry-distinct H. Pair differences b minus a
are the predictions; ddF_iso per H (both imaginary-mode treatments) comes from refine.py's arrays.

    python -m src.isoshift_event.spectro
writes docs/predictions/P02_spectro_model.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
THZ_CM = 33.35641
MODELS = ("mace", "orb", "mattersim")
PAIRS = {  # (a, b, label); phase names from space group + ICSD/MP provenance, see P02 file
    "diaspore_boehmite": ("mp-625152", "JVASP-12038"),
    "diaspore_deltaAlOOH": ("mp-625152", "mp-23807"),
    "goethite_epsilonFeOOH": ("mp-605437", "JVASP-92228"),
}


def _bands(model, sid):
    import phonopy

    from . import refine

    raw = json.loads((refine.RAW / model / f"{sid}.json").read_text())
    calc = "{name}-{model}".format(**raw["calc"])
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
    key = (safe, round(raw["fc_meta"]["energy_eV"], 6), round(raw["fc_meta"]["volume_A3"], 4))
    ph = phonopy.load(str(refine._cache_index()[key] / "phonopy_params.yaml"), produce_fc=False, log_level=0)
    pc = ph.primitive
    sym = np.array(pc.symbols)
    cell = np.asarray(pc.cell)
    frac = np.asarray(pc.scaled_positions)
    O = np.flatnonzero(sym == "O")
    ph.run_qpoints([[0, 0, 0]], with_eigenvectors=True)
    f = ph.qpoints.frequencies[0] * THZ_CM
    ev = ph.qpoints.eigenvectors[0].reshape(len(sym), 3, -1)
    out = {"stretch": [], "bend_ip": [], "bend_op": [], "d_OH": [], "d_OO": []}
    for i in np.flatnonzero(sym == "H"):
        d = frac[O] - frac[i]
        d -= np.round(d)
        cart = d @ cell
        r = np.linalg.norm(cart, axis=1)
        o = np.argsort(r)
        b = cart[o[0]] / r[o[0]]  # H -> donor O
        acc = cart[o[1]] / r[o[1]]
        n_op = np.cross(b, acc)
        n_op /= np.linalg.norm(n_op)
        n_ip = np.cross(n_op, b)
        for name, u, fmin in (("stretch", b, 1500), ("bend_ip", n_ip, 500), ("bend_op", n_op, 500)):
            w = np.abs(np.einsum("a,ab->b", u, ev[i])) ** 2 * (f > fmin)
            out[name].append(float((w * f).sum() / w.sum()))
        out["d_OH"].append(float(r[o[0]]))
        donor = cart[o[0]]
        out["d_OO"].append(float(np.linalg.norm(cart[o[1]] - donor)))
    return {k: float(np.mean(v)) for k, v in out.items()} | {"n_H": int((sym == "H").sum())}


def main():
    rows = []
    for label, (a, b) in PAIRS.items():
        for m in MODELS:
            try:
                ba, bb = _bands(m, a), _bands(m, b)
            except Exception as exc:  # recorded, never silently dropped
                rows.append({"pair": label, "model": m, "error": str(exc)})
                continue
            row = {"pair": label, "a": a, "b": b, "model": m}
            for k in ("stretch", "bend_ip", "bend_op", "d_OH", "d_OO"):
                row[f"{k}_a"], row[f"{k}_b"] = round(ba[k], 4), round(bb[k], 4)
                row[f"d_{k}"] = round(bb[k] - ba[k], 4)
            rows.append(row)
    out = ROOT / "docs" / "predictions" / "P02_spectro_model.csv"
    fields = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("pair", "model", "a", "b"), k))
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, restval="")
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if "error" in r:
            print(r)
            continue
        print(f"{r['pair']:22s} {r['model']:9s} stretch {r['stretch_a']:7.0f}->{r['stretch_b']:7.0f} (d {r['d_stretch']:+6.0f})  "
              f"bend_ip {r['bend_ip_a']:6.0f}->{r['bend_ip_b']:6.0f} (d {r['d_bend_ip']:+5.0f})  bend_op {r['bend_op_a']:6.0f}->{r['bend_op_b']:6.0f} "
              f"(d {r['d_bend_op']:+5.0f})  dOH {r['d_d_OH']*1000:+5.1f} mA  dOO {r['d_d_OO']*1000:+6.1f} mA")


if __name__ == "__main__":
    main()
