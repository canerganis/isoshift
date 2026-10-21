"""Mineral D/H fractionation from the same H/D free energies (blind predictions, then comparison).

Harmonic reduced partition function ratio per H (Bigeleisen-Mayer / Urey), from the cached force constants:
    ln beta = -[(F_D - F_H) - (F_D - F_H)_classical] / (n_H kT),  (F_D - F_H)_classical = -(3/2) n_H kT ln(m_D/m_H)
so 1000 ln beta (permil) needs no reference; between two minerals (or polymorphs) A and B
    1000 ln alpha(A-B) = 1000 (ln beta_A - ln beta_B) = -1000 [dF_A - dF_B] / kT   (dF per H),
i.e. 1 meV/H of ddF_iso is 38.7 permil at 300 K. Mineral-water factors need water's beta, which cancels in
mineral-mineral and polymorph-polymorph differences; those differences are the test.
Imaginary modes: |w| treatment (decision 02), imaginary fraction reported.

    python -m src.isoshift_event.fractionation --structs mp-30247,mp-625152,...
writes docs/predictions/P04_fractionation_blind.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
KB = 8.617333262e-5
M_H, M_D = 1.00782503, 2.01410178
TEMPS_C = (25, 100, 200, 300, 400)


def _cache_dir(model, sid):
    from . import refine

    raw = json.loads((refine.RAW / model / f"{sid}.json").read_text())
    calc = "{name}-{model}".format(**raw["calc"])
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
    key = (safe, round(raw["fc_meta"]["energy_eV"], 6), round(raw["fc_meta"]["volume_A3"], 4))
    return refine._cache_index().get(key)


def _one(args):
    model, sid, d = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import phonopy
    from ase import Atoms

    from isoshift import phonons as P

    ph = phonopy.load(str(Path(d) / "phonopy_params.yaml"), produce_fc=False, log_level=0)
    uc = ph.unitcell
    a = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    nH = int(sum(1 for s in uc.symbols if s == "H"))
    mesh = tuple(int(min(16, max(4, 2 * round(60.0 / l / 2)))) for l in a.cell.lengths())
    T = np.array(TEMPS_C, float) + 273.15
    F = {}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        mf = P.mesh_frequencies(ph, P.make_masses(a, sub, default="light"), mesh, is_gamma_center=False)
        imag = float(mf.imaginary_fraction)
        F[iso] = np.asarray(P.MeshFreqs(np.abs(mf.freqs), mf.weights, mf.n_atoms).helmholtz_free_energy(list(T)))  # eV/cell
    dF = (F["D"] - F["H"]) / nH  # eV per H
    classical = -1.5 * KB * T * np.log(M_D / M_H)
    lnbeta = -(dF - classical) / (KB * T)
    return {"model": model, "struct_id": sid, "n_H": nH, "imag_fraction": round(imag, 4),
            **{f"dF_meV_H_{c}C": round(float(x) * 1000, 4) for c, x in zip(TEMPS_C, dF)},
            **{f"1000lnbeta_{c}C": round(float(x) * 1000, 2) for c, x in zip(TEMPS_C, lnbeta)}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--structs", required=True)
    ap.add_argument("--models", default="mace,orb,mattersim")
    ap.add_argument("--out", default="docs/predictions/P04_fractionation_blind.csv")
    args = ap.parse_args(argv)
    jobs = []
    for m in args.models.split(","):
        for sid in args.structs.split(","):
            try:
                d = _cache_dir(m, sid)
            except FileNotFoundError:
                d = None
            if d:
                jobs.append((m, sid, str(d)))
    with ProcessPoolExecutor(6) as ex:
        rows = list(ex.map(_one, jobs))
    meta = {r["struct_id"]: r for r in csv.DictReader(open(ROOT / "data" / "isoshift" / "structures.csv"))}
    for r in rows:
        r["formula"], r["spg"] = meta[r["struct_id"]]["formula"], meta[r["struct_id"]]["spg"]
    fields = ["struct_id", "formula", "spg", "model", "n_H", "imag_fraction"] + [k for k in rows[0] if k.startswith(("dF_", "1000ln"))]
    with open(ROOT / args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["formula"], r["struct_id"], r["model"])))
    for r in sorted(rows, key=lambda r: (r["formula"], r["struct_id"], r["model"])):
        print(f"{r['formula']:9s} {r['struct_id']:13s} spg {r['spg']:>3s} {r['model']:9s} imag {r['imag_fraction']:.3f}  "
              f"1000lnbeta 25C {r['1000lnbeta_25C']:8.1f}  300C {r['1000lnbeta_300C']:7.1f}")


if __name__ == "__main__":
    main()
