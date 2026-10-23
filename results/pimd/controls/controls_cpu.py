"""Decision 18 CPU controls. C4: 4 vs 8 GL points with exact finite-P harmonic K on the same-cell spectra of all 9.
C1: harmonic-backend PIMD on the real FCs of mp-23807 and mp-625152, P = 16, 0.25 fs, BAOAB, vs analytic dF_P.
Usage: controls_cpu.py c4 out.json | c1 out.json <struct> <steps_per_point> <seed>"""
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(r"C:\Users\can02\Projects\osi-hackathon-2026")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).parent / "snap"))
from ase import Atoms
from phonopy.harmonic.force_constants import compact_fc_to_full_fc

import pimd_head as M
from isoshift import cache
from isoshift import phonons as Ph

RAW, CACHE = REPO / "results/raw/screen/mace", REPO / ".cache/isoshift"
STRUCTS = ["mp-23807", "mp-625054", "JVASP-54682", "JVASP-92228", "mp-625152", "mp-626497", "mp-985293", "mp-23940",
           "mp-626000"]
T, P = 300.0, 16


def load(sid):
    cdir = M.find_cache(sid, RAW, CACHE)
    ph, _ = cache.load_fc(cdir.name, root=cdir.parent)
    uc = ph.unitcell
    cell = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    sc = [int(x) for x in np.diag(Ph.supercell_for_min_length(cell, M.MIN_LENGTH, M.MAX_ATOMS))]
    return cdir, ph, cell, sc


def f_harm(ph, cell, qpts, i_gamma, m_h, P):
    masses = Ph.make_masses(cell, {}, default="light").copy()
    masses[np.array(cell.get_chemical_symbols()) == "H"] = m_h
    p = Ph.phonopy_with_masses(ph, masses)
    p.run_qpoints(qpts, with_eigenvectors=True)
    nu = np.array(p.qpoints.frequencies)
    keep, _, _ = M.classify_modes(nu, np.array(p.qpoints.eigenvectors)[i_gamma], masses, i_gamma=i_gamma)
    return M._isotope_free_energy(nu, keep, float(masses.sum()) * len(qpts), T, P)


def c4():
    out = {}
    for sid in STRUCTS:
        cdir, ph, cell, sc = load(sid)
        qpts = M.commensurate_qpoints(sc)
        ig = int(np.flatnonzero(np.all(np.abs(qpts) < 1e-12, axis=1))[0])
        n_h = sum(s == "H" for s in cell.get_chemical_symbols()) * len(qpts)
        F = lambda g: f_harm(ph, cell, qpts, ig, M.M_H / g ** 2, P)
        exact = (F(M.G_D) - F(1.0)) * 1e3 / n_h
        res = {"exact_meV_H": exact}
        for n in (4, 8):
            g, w = M.ti_nodes(n)
            h = 1e-4
            dFdg = np.array([(F(x + h) - F(x - h)) / (2 * h) for x in g])
            # ti_nodes weights are positive on [g_D, 1]
            val = -float(np.sum(w * dFdg)) * 1e3 / n_h  # integral from 1 down to g_D
            res[f"GL{n}_meV_H"] = val
        res["GL4_minus_GL8"] = res["GL4_meV_H"] - res["GL8_meV_H"]
        res["GL4_minus_exact"] = res["GL4_meV_H"] - exact
        res["pass"] = bool(abs(res["GL4_minus_GL8"]) < 0.01)
        out[sid] = res
        print(sid, json.dumps(res), flush=True)
    return {"control": "C4 4 vs 8 GL points, exact finite-P (P = 16) same-cell harmonic K", "T": T, "P": P,
            "per_structure": out, "pass": all(r["pass"] for r in out.values())}


def c1(sid, steps, seed):
    cdir, ph, cell, sc = load(sid)
    if sc != [int(x) for x in np.diag(ph.supercell_matrix)]:
        raise ValueError("C1 needs PIMD sc == FC sc")
    fc = ph.force_constants
    if fc.shape[0] != fc.shape[1]:
        fc = compact_fc_to_full_fc(ph.primitive, fc)
    s = ph.supercell
    atoms = Atoms(s.symbols, cell=s.cell, scaled_positions=s.scaled_positions, pbc=True)
    mask = np.array([x == "H" for x in atoms.get_chemical_symbols()])
    base = Ph.make_masses(atoms, {}, default="light")
    harm = M.harmonic_samecell(ph, sc, T, P=P)
    n_h = int(mask.sum())
    rp = M.RingPolymer(atoms.positions, base, P, T, 0.25, 100.0, M.HarmonicForces(fc, atoms.positions),
                       np.random.default_rng(seed), splitting="baoab")
    for _ in range(2000):
        rp.step()
    g, w = M.ti_nodes(4)
    t0 = time.time()
    pts = M.run_points(rp, mask, g, steps, 0.2, base)
    df, err = M.ti_integrate(g, w, [p["K_H_meV"] for p in pts], [p["K_H_err_meV"] for p in pts])
    ref = harm["dF_P_eV"] * 1e3 / n_h
    return {"control": "C1 harmonic-backend PIMD vs analytic dF_P", "struct_id": sid, "cache_key": cdir.name, "P": P,
            "dt_fs": 0.25, "splitting": "baoab", "steps_per_point": steps, "seed": seed, "dF_PIMD_meV_H": df,
            "err_meV_H": err, "dF_P_analytic_meV_H": ref, "diff_meV_H": df - ref,
            "error_converged": all(p.get("error_converged", False) for p in pts), "wall_s": time.time() - t0,
            "pass": bool(abs(df - ref) < 0.10 + 2 * err)}


if __name__ == "__main__":
    mode, outp = sys.argv[1], sys.argv[2]
    res = c4() if mode == "c4" else c1(sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    print(json.dumps({k: v for k, v in res.items() if k != "per_structure"}, indent=1))
    json.dump(res, open(outp, "w"), indent=1)
