"""Quasi-harmonic workflow: volume scan, constant-volume relax, phonons per volume, phonopy QHA.

H and D (any mass assignment) variants share the same force constants at each volume.
"""
from __future__ import annotations

import time

import numpy as np

from . import phonons as P
from .relax import relax

EV_PER_KJMOL = 1.0 / 96.48533212


def _thermal(ph, masses, mesh, temps):
    p = P.phonopy_with_masses(ph, masses)
    p.run_mesh(list(mesh), is_mesh_symmetry=True, is_gamma_center=True)
    p.run_thermal_properties(temperatures=temps)
    d = p.get_thermal_properties_dict()
    return d["free_energy"], d["entropy"], d["heat_capacity"]


def qha_gibbs(atoms, calc, calc_id: str, variants: dict, n_vol: int = 7, vol_range=(-0.03, 0.07),
              min_length: float = 10.0, max_atoms: int | None = 400, mesh=None, temps=None, pressure_GPa: float = 0.0,
              fmax: float = 0.001, relax_first: bool = True, use_cache: bool = True,
              eos: str = "vinet", verbose: bool = False):
    """Return dict with G(T) at pressure for each variant.

    variants: name -> substitution dict for P.make_masses, e.g. {"H": {}, "D": {"H": "D"}}
    G is in eV per cell of `atoms`. vol_range is the relative volume window around the relaxed static
    volume. It is asymmetric by default because zero point pressure expands light-H compounds by
    several percent; V(T) outside the scanned window is flagged (`in_range`) and must not be trusted.
    """
    from phonopy import PhonopyQHA

    temps = np.arange(0, 801, 10.0) if temps is None else np.asarray(temps, float)
    t0 = time.time()
    a0 = atoms
    info0 = None
    if relax_first:
        a0, info0 = relax(atoms, calc, fmax=fmax)
    V0 = a0.get_volume()
    mesh = mesh or P.choose_mesh(a0)
    vols, e0s, fcs, timing = [], [], [], {"relax_s": 0.0, "fc_s": 0.0, "fc_cached": 0}
    for f in np.linspace(1 + vol_range[0], 1 + vol_range[1], n_vol):
        a = a0.copy()
        a.set_cell(a0.cell.array * f ** (1 / 3), scale_atoms=True)
        tr = time.time()
        ar, inf = relax(a, calc, fmax=fmax, constant_volume=True)
        timing["relax_s"] += time.time() - tr
        tf = time.time()
        ph, meta, hit = P.get_force_constants(ar, calc, calc_id, min_length=min_length, max_atoms=max_atoms, use_cache=use_cache)
        timing["fc_s"] += time.time() - tf
        timing["fc_cached"] += int(hit)
        vols.append(ar.get_volume())
        e0s.append(inf["energy"])
        fcs.append(ph)
        if verbose:
            print(f"  V/V0={f:.4f} E={inf['energy']:.5f} relax steps={inf['steps']} cached={hit}")
    order = np.argsort(vols)
    vols = np.array(vols)[order]
    e0s = np.array(e0s)[order]
    fcs = [fcs[i] for i in order]
    out = {"calc_id": calc_id, "volumes": vols.tolist(), "E0": e0s.tolist(), "V0_relaxed": V0,
           "temperatures": temps.tolist(), "pressure_GPa": pressure_GPa, "variants": {}, "timing": timing,
           "n_atoms_cell": len(a0)}
    for name, sub in variants.items():
        masses = P.make_masses(a0, sub, default="light")
        fe, se, cv = [], [], []
        for ph in fcs:
            f_, s_, c_ = _thermal(ph, masses, mesh, temps)
            fe.append(f_)
            se.append(s_)
            cv.append(c_)
        fe, se, cv = (np.array(x).T for x in (fe, se, cv))  # (nT, nV)
        q = PhonopyQHA(volumes=vols, electronic_energies=e0s, temperatures=temps, free_energy=fe, cv=cv,
                       entropy=se, eos=eos, pressure=pressure_GPa, t_max=float(temps[-1]))
        g = np.array(q.gibbs_temperature)
        v = np.array(q.volume_temperature)
        n = len(g)
        in_range = ((v >= vols.min() - 1e-9) & (v <= vols.max() + 1e-9))
        out["variants"][name] = {"T": temps[:n].tolist(), "G_eV": g.tolist(), "V_A3": v.tolist(),
                                 "in_range": in_range.tolist(), "n_in_range": int(in_range.sum())}
    timing["total_s"] = time.time() - t0
    return out
