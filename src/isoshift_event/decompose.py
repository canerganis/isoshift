"""Mode-resolved isotope free energy (M01 section 6): which H motions carry ddF_iso?

F_D - F_H = - integral_{ln m_H}^{ln m_D} sum_{q,nu} w_q K_nu(m) [w_str + w_perp] d ln m,
K_nu = (E/4) coth(E / 2kT), w_str = sum_{i in H} |b_i . e_i|^2 (b_i: unit vector to the nearest
non-H neighbour), w_perp = w_H - w_str. Six-point Gauss-Legendre in ln m, force constants re-used at
each H mass (mass independent), Gamma-free shifted mesh. The quadrature total is checked against the
direct F_D - F_H.

Covalent X-H (nearest non-H neighbour closer than 1.3 A: O, N, B, C ...) gets a stretch/perpendicular
split; hydridic H (metal neighbours) gets only the total, flagged.

    python -m src.isoshift_event.decompose [--workers 8] [--T 300] [--out-dir results]
writes decompose_structures.csv and decompose_pairs.csv (per pair and model) into --out-dir at temperature --T.
Defaults (300 K, results/) reproduce the frozen files. At T = 0 the mode weight is the T -> 0 limit E/4.
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
KB = 8.617333262e-5  # eV/K
THZ_EV = 4.135667696e-3
T = 300.0
M_H, M_D = 1.00782503, 2.01410178
COVALENT_CUT = 1.3  # A


def _one(args):
    model, sid, cache_dir, *rest = args
    t = float(rest[0]) if rest else T
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import phonopy

    from isoshift import phonons as P

    ph = phonopy.load(str(Path(cache_dir) / "phonopy_params.yaml"), produce_fc=False, log_level=0)
    uc = ph.unitcell
    sym = np.array(uc.symbols)
    H = np.flatnonzero(sym == "H")
    cell = np.asarray(uc.cell)
    frac = np.asarray(uc.scaled_positions)
    heavy = np.flatnonzero(sym != "H")
    if len(heavy) == 0 or len(H) == 0:
        return None  # pure H (solid H2) or H-free cells: nothing to decompose
    bonds, dists = np.zeros((len(sym), 3)), []
    for i in H:
        d = frac[heavy] - frac[i]
        d -= np.round(d)
        cart = d @ cell
        k = int(np.argmin(np.linalg.norm(cart, axis=1)))
        dists.append(float(np.linalg.norm(cart[k])))
        bonds[i] = cart[k] / dists[-1]
    covalent = bool(dists) and max(dists) < COVALENT_CUT
    mesh = [int(min(12, max(4, 2 * round(40.0 / l / 2)))) for l in np.linalg.norm(cell, axis=1)]
    base = P.make_masses(_atoms(uc), {}, default="light")
    xs, ws = np.polynomial.legendre.leggauss(6)
    lo, hi = np.log(M_H), np.log(M_D)
    I_str = I_perp = 0.0
    for x, wgl in zip(xs, ws):
        lm = 0.5 * (hi - lo) * x + 0.5 * (hi + lo)
        masses = base.copy()
        masses[H] = np.exp(lm)
        p = P.phonopy_with_masses(ph, masses)
        p.run_mesh(mesh, with_eigenvectors=True, is_mesh_symmetry=False, is_gamma_center=False)
        f = np.array(p.mesh.frequencies)
        ev = np.array(p.mesh.eigenvectors)  # (nq, 3n, nb), mass-weighted
        wq = np.array(p.mesh.weights, float)
        wq /= wq.sum()
        E = np.abs(f) * THZ_EV
        if t > 0:
            K = np.where(E > 1e-6, 0.25 * E / np.tanh(np.maximum(E, 1e-12) / (2 * KB * t)), 0.0)
        else:
            K = np.where(E > 1e-6, 0.25 * E, 0.0)
        e3 = ev.reshape(ev.shape[0], len(sym), 3, ev.shape[2])
        wH = (np.abs(e3[:, H]) ** 2).sum(axis=(1, 2))
        proj = np.einsum("qiab,ia->qib", e3[:, H], bonds[H])
        wstr = (np.abs(proj) ** 2).sum(axis=1)
        jac = 0.5 * (hi - lo) * wgl
        I_str += jac * float((wq[:, None] * K * wstr).sum())
        I_perp += jac * float((wq[:, None] * K * (wH - wstr)).sum())
    n = len(sym)
    dF_quad = -(I_str + I_perp) * 1000 / n  # meV/atom
    mf = {iso: P.mesh_frequencies(ph, P.make_masses(_atoms(uc), sub, default="light"), mesh, is_gamma_center=False)
          for iso, sub in (("H", {}), ("D", {"H": "D"}))}
    dF_direct = float(mf["D"].helmholtz_free_energy([t])[0] - mf["H"].helmholtz_free_energy([t])[0]) * 1000 / n
    return {"model": model, "struct_id": sid, "n_atoms": n, "n_H": int(len(H)), "covalent_XH": covalent,
            "XH_max_A": round(max(dists), 4) if dists else "", "XH_mean_A": round(float(np.mean(dists)), 5) if dists else "", "dF_str_meV_atom": -I_str * 1000 / n,
            "dF_perp_meV_atom": -I_perp * 1000 / n, "dF_quad_meV_atom": dF_quad, "dF_direct_meV_atom": dF_direct}


def _atoms(uc):
    from ase import Atoms

    return Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--models", default="mace,orb")
    ap.add_argument("--T", type=float, default=T, help="temperature in K (default 300)")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "results", help="output directory (default results/)")
    args = ap.parse_args(argv)
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    from . import refine

    idx = refine._cache_index()
    models = args.models.split(",")
    pairs = list(csv.DictReader(open(ROOT / "results" / "screen_pairs_refined.csv", newline="")))
    pairs = [p for p in pairs if p["model"] in models and p.get("identity_checked") == "true"
             and "same_relaxed_structure" not in p.get("flags", "")]
    need = {(p["model"], s) for p in pairs for s in (p["struct_a"], p["struct_b"])}
    jobs = []
    for model, sid in sorted(need):
        f = refine.RAW / model / f"{sid}.json"
        r = json.loads(f.read_text())
        calc = "{name}-{model}".format(**r["calc"])
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
        key = (safe, round(r["fc_meta"]["energy_eV"], 6), round(r["fc_meta"]["volume_A3"], 4))
        if key in idx:
            jobs.append((model, sid, str(idx[key]), args.T))
    with ProcessPoolExecutor(args.workers) as ex:
        res = {(r["model"], r["struct_id"]): r for r in ex.map(_one, jobs, chunksize=2) if r}
    with open(out_dir / "decompose_structures.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(next(iter(res.values()))))
        w.writeheader()
        w.writerows(res.values())
    out = []
    for p in pairs:
        a, b = res.get((p["model"], p["struct_a"])), res.get((p["model"], p["struct_b"]))
        if not a or not b:
            continue
        out.append({"pair_id": p["pair_id"], "model": p["model"], "formula": p.get("formula", "") or a.get("formula", ""),
                    "covalent_XH": a["covalent_XH"] and b["covalent_XH"],
                    "ddF_str": b["dF_str_meV_atom"] - a["dF_str_meV_atom"],
                    "ddF_perp": b["dF_perp_meV_atom"] - a["dF_perp_meV_atom"],
                    "ddF_total": b["dF_quad_meV_atom"] - a["dF_quad_meV_atom"],
                    "ddF_direct": b["dF_direct_meV_atom"] - a["dF_direct_meV_atom"],
                    "dXH_A": (b["XH_max_A"] - a["XH_max_A"]) if a["covalent_XH"] and b["covalent_XH"] else "",
                    "dXH_mean_A": (b["XH_mean_A"] - a["XH_mean_A"]) if a["covalent_XH"] and b["covalent_XH"] else "",
                    "H_per_atom": a["n_H"] / a["n_atoms"],
                    "clean": abs(a["dF_quad_meV_atom"] - a["dF_direct_meV_atom"]) < 0.01
                             and abs(b["dF_quad_meV_atom"] - b["dF_direct_meV_atom"]) < 0.01})
    with open(out_dir / "decompose_pairs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(out[0]))
        w.writeheader()
        w.writerows(out)
    err = max(abs(r["dF_quad_meV_atom"] - r["dF_direct_meV_atom"]) for r in res.values())
    print(f"T = {args.T:g} K, {len(res)} structures, {len(out)} pair rows; max |quadrature - direct| = {err:.2e} meV/atom")


if __name__ == "__main__":
    main()
