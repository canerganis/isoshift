"""P11 eigenvector following for candidate structures (decision 02 rule 4).

For a (structure, model) whose screen result has imaginary modes: take the MLIP-relaxed cell from the
force-constant cache, displace along the most unstable mode commensurate with a 2x2x2 (or smaller)
supercell, relax without symmetry, reduce to the primitive cell, recompute force constants and the
H/D free energies, and record whether the structure is still the same polymorph.

    python -m src.isoshift_event.stabilize --pairs PAIR_ID[,PAIR_ID...] --models mace,orb
Writes results/raw/stabilize/<model>/<struct_id>.json and results/stabilized_pairs.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "raw" / "stabilize"
TEMPS = (0.0, 300.0, 600.0, 2000.0)
AMP = 0.1  # A, largest atomic displacement along the mode


def _cached(model, sid):
    """Relaxed unit cell + phonopy object of the screen run, located like refine.py does."""
    import phonopy

    from . import refine

    raw = json.loads((refine.RAW / model / f"{sid}.json").read_text())
    calc = "{name}-{model}".format(**raw["calc"])
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
    key = (safe, round(raw["fc_meta"]["energy_eV"], 6), round(raw["fc_meta"]["volume_A3"], 4))
    d = refine._cache_index()[key]
    return phonopy.load(str(d / "phonopy_params.yaml"), produce_fc=False, log_level=0), raw


def _atoms(cell):
    from ase import Atoms

    return Atoms(cell.symbols, cell=cell.cell, scaled_positions=cell.scaled_positions, pbc=True)


def _free(ph, atoms):
    from isoshift import phonons as P

    mesh = tuple(int(min(16, max(4, 2 * round(60.0 / l / 2)))) for l in atoms.cell.lengths())
    out = {}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        mf = P.mesh_frequencies(ph, P.make_masses(atoms, sub, default="light"), mesh, is_gamma_center=False)
        ab = P.MeshFreqs(np.abs(mf.freqs), mf.weights, mf.n_atoms)
        out[f"F_{iso}_meV_atom"] = (np.asarray(ab.helmholtz_free_energy(list(TEMPS))) * 1000 / len(atoms)).tolist()
        out["min_freq_THz"] = min(out.get("min_freq_THz", 1e9), float(mf.min_freq))
        out["imag_fraction"] = max(out.get("imag_fraction", 0.0), float(mf.imaginary_fraction))
    return out


def stabilize(model, sid, calc):
    from ase.build import make_supercell
    from pymatgen.analysis.structure_matcher import StructureMatcher
    from pymatgen.io.ase import AseAtomsAdaptor as AA

    from isoshift import phonons as P
    from isoshift.calculators import calculator_info
    from isoshift.relax import relax

    ph0, raw = _cached(model, sid)
    a0 = _atoms(ph0.unitcell)
    n = len(a0)
    mult = np.array([2 if n * 8 <= 160 else 1, 2 if n * 4 <= 160 else 1, 2 if n * 2 <= 160 else 1])
    qs = np.array([[i / mult[0], j / mult[1], k / mult[2]]
                   for i in range(mult[0]) for j in range(mult[1]) for k in range(mult[2])])
    ph0.run_qpoints(qs, with_eigenvectors=True)
    f, ev = ph0.qpoints.frequencies, ph0.qpoints.eigenvectors
    i, j = np.unravel_index(np.argmin(f), f.shape)
    res = {"model": model, "struct_id": sid, "n_atoms": n, "softest_q": qs[i].tolist(), "softest_THz": float(f[i, j]),
           "E0_eV_atom": raw["relax"]["energy"] / n}
    if f[i, j] > -0.3:
        res.update(status="stable_at_commensurate_q", dE_meV_atom=0.0, same_polymorph=True, **_free(ph0, a0))
        return res
    sup = make_supercell(a0, np.diag(mult))
    m = a0.get_masses()
    e = ev[i][:, j].reshape(-1, 3)
    cells = np.floor(sup.get_scaled_positions() @ np.diag(mult) + 1e-6)
    disp = np.array([np.real(e[k % n] * np.exp(2j * np.pi * qs[i] @ cells[k])) / np.sqrt(m[k % n]) for k in range(len(sup))])
    disp *= AMP / np.abs(disp).max()
    b = sup.copy()
    b.set_positions(sup.get_positions() + disp)
    r, info = relax(b, calc, fmax=2e-3, steps=3000, symmetrize=False)
    s_new = AA.get_structure(r).get_primitive_structure(tolerance=0.01)
    a1 = AA.get_atoms(s_new)
    a1, info1 = relax(a1, calc, fmax=2e-3, steps=2000, symmetrize=False)
    dE = (info1["energy"] / len(a1) - res["E0_eV_atom"]) * 1000
    cid = "{name}-{model}".format(**calculator_info(calc))
    ph1, _, _ = P.get_force_constants(a1, calc, cid + "-stab", min_length=9.5, max_atoms=160)
    sm = StructureMatcher(ltol=0.3, stol=0.4, angle_tol=8, attempt_supercell=True)
    same = bool(sm.fit(AA.get_structure(a0), AA.get_structure(a1)))
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    res.update(status="relaxed_along_mode", dE_meV_atom=dE, same_polymorph=same, n_atoms_new=len(a1),
               spg_new=SpacegroupAnalyzer(AA.get_structure(a1), symprec=0.05).get_space_group_number(),
               V_A3_atom=float(a1.get_volume() / len(a1)), E_eV_atom=info1["energy"] / len(a1), **_free(ph1, a1))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--models", default="mace,orb")
    args = ap.parse_args(argv)
    from isoshift.calculators import get_calculator

    import pandas as pd

    pairs = pd.read_csv(ROOT / "data" / "isoshift" / "pairs.csv").set_index("pair_id").loc[args.pairs.split(",")]
    rows = []
    for model in args.models.split(","):
        calc = get_calculator(model, "cuda")
        done = {}
        for pid, p in pairs.iterrows():
            for sid in (p.struct_a, p.struct_b):
                path = OUT / model / f"{sid}.json"
                if sid not in done:
                    if path.exists():
                        done[sid] = json.loads(path.read_text())
                    else:
                        try:
                            done[sid] = stabilize(model, sid, calc)
                        except Exception as exc:  # recorded, never silently dropped
                            done[sid] = {"model": model, "struct_id": sid, "status": f"error: {exc}"}
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(json.dumps(done[sid]))
                    print(model, sid, done[sid].get("status"), round(done[sid].get("dE_meV_atom", float("nan")), 3),
                          done[sid].get("same_polymorph"), flush=True)
            ra, rb = done[p.struct_a], done[p.struct_b]
            row = {"pair_id": pid, "model": model, "a_status": ra.get("status"), "b_status": rb.get("status"),
                   "a_same": ra.get("same_polymorph"), "b_same": rb.get("same_polymorph"),
                   "a_dE_meV_atom": ra.get("dE_meV_atom"), "b_dE_meV_atom": rb.get("dE_meV_atom")}
            if "F_H_meV_atom" in ra and "F_H_meV_atom" in rb:
                for k, t in enumerate(TEMPS):
                    row[f"ddF_stab_{int(t)}K"] = ((rb["F_D_meV_atom"][k] - rb["F_H_meV_atom"][k])
                                                 - (ra["F_D_meV_atom"][k] - ra["F_H_meV_atom"][k]))
            rows.append(row)
    path = ROOT / "results" / "stabilized_pairs.csv"
    old = list(csv.DictReader(open(path, newline=""))) if path.exists() else []
    keep = [r for r in old if (r["pair_id"], r["model"]) not in {(x["pair_id"], x["model"]) for x in rows}]
    fields = sorted({k for r in keep + rows for k in r}, key=lambda k: (k not in ("pair_id", "model"), k))
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, restval="")
        w.writeheader()
        w.writerows(keep + rows)


if __name__ == "__main__":
    main()
