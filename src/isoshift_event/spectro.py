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
    "diaspore_boehmite": ("mp-625152", "JVASP-12038"),  # structure check only (see P02)
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
    from pymatgen.core import Lattice, Structure

    st = Structure(Lattice(np.asarray(pc.cell)), list(pc.symbols), np.asarray(pc.scaled_positions))
    sym = np.array(pc.symbols)
    ph.run_qpoints([[0, 0, 0]], with_eigenvectors=True)
    f = ph.qpoints.frequencies[0] * THZ_CM
    ev = ph.qpoints.eigenvectors[0].reshape(len(sym), 3, -1)
    out = {k: [] for k in ("stretch", "bend_ip", "bend_op", "stretch_peak", "bend_ip_peak", "bend_op_peak",
                           "stretch_peak_w", "bend_ip_peak_w", "bend_op_peak_w", "d_OH", "d_OO", "angle_OHO", "linear_flag")}
    for i in np.flatnonzero(sym == "H"):
        nb = sorted((n for n in st.get_neighbors(st[i], 3.0) if n.specie.symbol == "O"), key=lambda n: n.nn_distance)
        don = nb[0]
        h = st[i].coords
        best = None
        for n in nb[1:]:  # acceptor: periodic image, H...O <= 2.6 A, O-H...O angle >= 110 deg
            v1, v2 = don.coords - h, n.coords - h
            ang = np.degrees(np.arccos(np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)))
            if n.nn_distance <= 2.6 and ang >= 110 and np.linalg.norm(n.coords - don.coords) > 1.8:
                best = (n, ang)
                break
        b = (don.coords - h) / don.nn_distance
        if best is None:
            acc_dir, ang, d_oo = None, float("nan"), float("nan")
        else:
            acc_dir = (best[0].coords - h) / np.linalg.norm(best[0].coords - h)
            ang, d_oo = best[1], float(np.linalg.norm(best[0].coords - don.coords))
        n_op = np.cross(b, acc_dir) if acc_dir is not None else np.cross(b, [0.0, 0.0, 1.0] if abs(b[2]) < 0.9 else [1.0, 0.0, 0.0])
        linear = acc_dir is None or np.linalg.norm(n_op) < 0.26  # O-H...O within 15 deg of linear: plane ill-defined
        n_op /= np.linalg.norm(n_op)
        n_ip = np.cross(n_op, b)
        for name, u, fmin in (("stretch", b, 1500), ("bend_ip", n_ip, 500), ("bend_op", n_op, 500)):
            w = np.abs(np.einsum("a,ab->b", u, ev[i])) ** 2 * (f > fmin)
            out[name].append(float((w * f).sum() / w.sum()))
            k = int(np.argmax(w))
            out[name + "_peak"].append(float(f[k]))
            out[name + "_peak_w"].append(float(w[k]))
        out["d_OH"].append(float(don.nn_distance))
        out["d_OO"].append(d_oo)
        out["angle_OHO"].append(float(ang))
        out["linear_flag"].append(float(linear))
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
            for k in ("stretch", "bend_ip", "bend_op", "stretch_peak", "bend_ip_peak", "bend_op_peak", "d_OH", "d_OO", "angle_OHO", "linear_flag"):
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
        print(f"{r['pair']:22s} {r['model']:9s} peaks: stretch {r['d_stretch_peak']:+6.0f} bend_ip {r['d_bend_ip_peak']:+5.0f} bend_op {r['d_bend_op_peak']:+5.0f} | angle {r['angle_OHO_a']:.0f}->{r['angle_OHO_b']:.0f} OO {r['d_OO_a']:.3f}->{r['d_OO_b']:.3f} | mean: stretch {r['stretch_a']:7.0f}->{r['stretch_b']:7.0f} (d {r['d_stretch']:+6.0f})  "
              f"bend_ip {r['bend_ip_a']:6.0f}->{r['bend_ip_b']:6.0f} (d {r['d_bend_ip']:+5.0f})  bend_op {r['bend_op_a']:6.0f}->{r['bend_op_b']:6.0f} "
              f"(d {r['d_bend_op']:+5.0f})  dOH {r['d_d_OH']*1000:+5.1f} mA  dOO {r['d_d_OO']*1000:+6.1f} mA")


if __name__ == "__main__":
    main()
