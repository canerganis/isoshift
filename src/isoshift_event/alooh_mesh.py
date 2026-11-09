"""q-mesh convergence of the AlOOH (diaspore -> delta) isotope shift of the transition pressure at 300 K (CPU only).

Council C-terra-v2 action 4 (Terra review W6). Same estimator as card_temperature.py (Gamma-free 'omit' QHA from the
cached force constants of results/raw/qha_pressure, linear fit of dG through 10, 15, 20 GPa), repeated for
mesh densities 40, 60 and 80 points per 1/a (clip [4, 24]) on a Gamma-centred mesh (3 smallest |w| at Gamma
dropped, as in the paper) and on a shifted, Gamma-free even mesh (all modes kept). Reads frozen files only;
no relaxation, no force calls, no GPU.

    python -m src.isoshift_event.alooh_mesh [--workers 8]
writes results/validation/alooh_mesh.json
"""
from __future__ import annotations

import argparse
import json
import os
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "raw" / "qha_pressure"
STRUCTS = ROOT / "data" / "isoshift" / "structs"
OUT = ROOT / "results" / "validation" / "alooh_mesh.json"
LOW, HIGH, PRESS = "mp-625152", "mp-23807", (10, 15, 20)
TEMPS = np.arange(0.0, 401.0, 50.0)  # phonopy QHA drops the last T
T_REPORT = 300.0
DENSITIES = (40, 60, 80)
KINDS = ("gamma", "shifted")


def _mesh(atoms, density, kind):
    n = [int(min(24, max(4, round(density / l)))) for l in atoms.cell.lengths()]
    if kind == "shifted":
        n = [k + (k % 2) for k in n]  # even and shifted -> no Gamma point
    return tuple(n)


def _spectrum_shifted(ph, masses, mesh):
    from isoshift import phonons as P

    p = P.phonopy_with_masses(ph, masses)
    p.run_mesh(list(mesh), with_eigenvectors=False, is_mesh_symmetry=True, is_gamma_center=False)
    f = np.array(p.mesh.frequencies, float)
    w = np.array(p.mesh.weights, float)
    q = np.array(p.mesh.qpoints, float)
    assert not np.any(np.all(np.abs(q - np.round(q)) < 1e-8, axis=1)), "shifted mesh contains Gamma"
    return f, w / w.sum(), np.ones(f.shape, bool), 0.0


def _job(args):
    model, sid, P = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    from ase import Atoms
    from phonopy import PhonopyQHA

    from isoshift import phonons as PH
    from src.isoshift_event import validate as V

    V.PRIM = STRUCTS
    V.V_TOL = 1e-3  # as card_temperature.py
    r = json.loads((RAW / model / f"{sid}_P{P}.json").read_text())
    vols, e0 = np.array(r["volumes"]), np.array(r["E0"])
    fcs = V._qha_fcs(sid, r)  # raises if any QHA volume has no cached force constants
    assert len(fcs) == len(vols)
    uc0 = fcs[int(np.argmin(np.abs(vols - r["V0_relaxed"])))][0].unitcell
    a0 = Atoms(uc0.symbols, cell=uc0.cell, scaled_positions=uc0.scaled_positions, pbc=True)
    it = int(np.argmin(np.abs(TEMPS - T_REPORT)))
    out = {}
    for kind in KINDS:
        for dens in DENSITIES:
            mesh = _mesh(a0, dens, kind)
            row = {"mesh": list(mesh)}
            for iso, sub in (("H", {}), ("D", {"H": "D"})):
                masses = PH.make_masses(a0, sub, default="light")
                spec = [(V._spectrum(ph, masses, mesh) if kind == "gamma" else _spectrum_shifted(ph, masses, mesh))
                        for ph, _m in fcs]
                th = [V._thermo(f, w, k, "omit", TEMPS) for f, w, k, _a in spec]
                fe, se, cv = (np.array(x).T for x in zip(*th))
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", DeprecationWarning)
                    q = PhonopyQHA(volumes=vols, electronic_energies=e0, temperatures=TEMPS, free_energy=fe, cv=cv,
                                   entropy=se, eos="vinet", pressure=float(P), t_max=float(TEMPS[-1]))
                g, v = np.array(q.gibbs_temperature), np.array(q.volume_temperature)
                row[f"G_{iso}"] = float(g[it] / r["n_atoms_cell"])
                row[f"in_range_{iso}"] = bool(vols.min() - 1e-9 <= v[it] <= vols.max() + 1e-9)
            out[f"{kind}/{dens}"] = row
    print("done", model, sid, P, flush=True)
    return (model, sid, P), out


def _root(x, y):
    k, b = np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)
    return float(-b / k)


def main(argv=None):
    from concurrent.futures import ProcessPoolExecutor

    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args(argv)
    models = [m for m in sorted(p.name for p in RAW.iterdir())
              if all((RAW / m / f"{s}_P{P}.json").exists() for s in (LOW, HIGH) for P in PRESS)]
    jobs = [(m, s, P) for m in models for s in (LOW, HIGH) for P in PRESS]
    with ProcessPoolExecutor(a.workers) as ex:
        done = dict(ex.map(_job, jobs))
    res = {"note": "C-terra-v2 action 4; 300 K; dG = G(delta) - G(diaspore) in meV/atom; P_t from a linear fit "
                   "through 10, 15, 20 GPa; dP_iso = P_t(D) - P_t(H)", "T_K": T_REPORT, "models": {}}
    for m in models:
        res["models"][m] = {}
        for kind in KINDS:
            for dens in DENSITIES:
                key = f"{kind}/{dens}"
                row = {"mesh_low": done[(m, LOW, 10)][key]["mesh"], "mesh_high": done[(m, HIGH, 10)][key]["mesh"]}
                ok = True
                for iso in ("H", "D"):
                    dg = [(done[(m, HIGH, P)][key][f"G_{iso}"] - done[(m, LOW, P)][key][f"G_{iso}"]) * 1000 for P in PRESS]
                    ok &= all(done[(m, s, P)][key][f"in_range_{iso}"] for s in (LOW, HIGH) for P in PRESS)
                    row[f"dG_{iso}_meV_atom"] = [round(x, 4) for x in dg]
                    row[f"Pt_{iso}_GPa"] = round(_root(PRESS, dg), 4)
                row["dP_iso_GPa"] = round(row["Pt_D_GPa"] - row["Pt_H_GPa"], 4)
                row["all_volumes_in_range"] = bool(ok)
                res["models"][m][key] = row
                print(m, key, row["dP_iso_GPa"], flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
