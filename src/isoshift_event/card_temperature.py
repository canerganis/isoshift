"""Temperature dependence of the isotope shift of the AlOOH and FeOOH transition pressures (CPU only).

Rebuilds Gamma-free QHA (3 smallest |w| at Gamma dropped, imaginary non-acoustic modes omitted) from the cached
force constants of results/raw/qha_pressure/<model>/<sid>_P<P>.json, on a wider T grid than the stored 0 to 400 K.
G(T, P) = min_V [E0(V) + F_vib(V, T) + P V] (phonopy QHA, vinet), per isotope. P_t(T) per isotope is the root of
a linear fit of dG = G_high - G_low through all pressures run (same estimator as card_alooh.py), dP_iso = P_t^D - P_t^H.

    python -m src.isoshift_event.card_temperature
writes results/card_alooh_temperature.json
"""
from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "raw" / "qha_pressure"
STRUCTS = ROOT / "data" / "isoshift" / "structs"
OUT = ROOT / "results" / "card_alooh_temperature.json"
TEMPS = np.arange(0.0, 1601.0, 50.0)  # phonopy QHA drops the last T, so 1500 K needs 1550+
REPORT_T = (300, 600, 1000, 1500)
CARDS = {
    "AlOOH": {"low": "mp-625152", "high": "mp-23807", "P": (10, 15, 20)},
    "FeOOH": {"low": "mp-605437", "high": "JVASP-92228", "P": (3, 6, 9)},
}


def _qha_one(args):
    """Gamma-free, 'omit' QHA for one raw file: G (eV/atom) and V(T) per isotope, plus spectrum diagnostics."""
    model, sid, P = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    from phonopy import PhonopyQHA

    from ase import Atoms

    from isoshift import phonons as PH
    from src.isoshift_event import validate as V

    V.PRIM = STRUCTS  # _qha_fcs reads PRIM/<name>.cif
    V.V_TOL = 1e-3  # pressure runs after the first reuse cached FCs of volumes that differ by <= 1.1e-4 A^3 (1e-6 relative)
    r = json.loads((RAW / model / f"{sid}_P{P}.json").read_text())
    vols, e0 = np.array(r["volumes"]), np.array(r["E0"])
    fcs = V._qha_fcs(sid, r)
    uc0 = fcs[int(np.argmin(np.abs(vols - r["V0_relaxed"])))][0].unitcell
    a0 = Atoms(uc0.symbols, cell=uc0.cell, scaled_positions=uc0.scaled_positions, pbc=True)
    mesh = PH.choose_mesh(a0)
    res = {"n_atoms_cell": r["n_atoms_cell"], "vol_min": float(vols.min()), "vol_max": float(vols.max()), "variants": {}}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        masses = PH.make_masses(a0, sub, default="light")
        spec = [V._spectrum(ph, masses, mesh) for ph, _m in fcs]
        th = [V._thermo(f, w, k, "omit", TEMPS) for f, w, k, _a in spec]
        fe, se, cv = (np.array(x).T for x in zip(*th))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            q = PhonopyQHA(volumes=vols, electronic_energies=e0, temperatures=TEMPS, free_energy=fe, cv=cv, entropy=se,
                           eos="vinet", pressure=float(P), t_max=float(TEMPS[-1]))
        g, v = np.array(q.gibbs_temperature), np.array(q.volume_temperature)
        n = len(g)
        d = {"T": TEMPS[:n].tolist(), "G_eV_atom": (g / r["n_atoms_cell"]).tolist(), "V_A3": v.tolist(),
             "in_range": ((v >= vols.min() - 1e-9) & (v <= vols.max() + 1e-9)).tolist()}
        if iso == "H":
            d["imag_frac_pct_per_volume"] = [round(100 * float((((f < PH.IMAG_TOL_THZ) & k) * w[:, None]).sum() / f.shape[1]), 4)
                                             for f, w, k, _a in spec]
        res["variants"][iso] = d
    return (model, sid, P), res


def _root(x, y):
    ok = np.isfinite(y)
    if ok.sum() < 2:
        return None, None
    k, b = np.polyfit(np.asarray(x, float)[ok], np.asarray(y)[ok], 1)
    return float(-b / k), bool(not (min(np.asarray(x)[ok]) <= -b / k <= max(np.asarray(x)[ok])))


def main(workers: int = 2):
    from concurrent.futures import ProcessPoolExecutor

    models = sorted(p.name for p in RAW.iterdir())
    jobs = []
    for card in CARDS.values():
        for model in models:
            for sid in (card["low"], card["high"]):
                for P in card["P"]:
                    if (RAW / model / f"{sid}_P{P}.json").exists():
                        jobs.append((model, sid, P))
    with ProcessPoolExecutor(workers) as ex:
        done = {}
        for key, res in ex.map(_qha_one, jobs):
            done[key] = res
            print("done", key, flush=True)
    out = {}
    for cname, card in CARDS.items():
        for model in models:
            if not all((model, s, P) in done for s in (card["low"], card["high"]) for P in card["P"]):
                continue
            entry = {"card": cname, "pressures_GPa": list(card["P"]), "treatment": "Gamma-free, omit imaginary", "T": {}}
            imag = {s: max(max(done[(model, s, P)]["variants"]["H"]["imag_frac_pct_per_volume"]) for P in card["P"])
                    for s in (card["low"], card["high"])}
            entry["imag_frac_pct_max_over_volumes_pressures"] = imag
            for T in REPORT_T:
                it = int(np.argmin(np.abs(TEMPS - T)))
                row = {}
                for iso in ("H", "D"):
                    dg, rng = [], True
                    for P in card["P"]:
                        lo = done[(model, card["low"], P)]["variants"][iso]
                        hi = done[(model, card["high"], P)]["variants"][iso]
                        if it >= len(lo["T"]) or it >= len(hi["T"]):
                            dg.append(np.nan)
                            continue
                        dg.append((hi["G_eV_atom"][it] - lo["G_eV_atom"][it]) * 1000)
                        rng &= lo["in_range"][it] and hi["in_range"][it]
                    root, extrap = _root(card["P"], np.array(dg))
                    row[f"dG_meV_atom_{iso}"] = [round(x, 4) for x in dg]
                    row[f"Pt_{iso}_GPa"] = None if root is None else round(root, 3)
                    row[f"Pt_{iso}_extrapolated"] = extrap
                    row[f"in_range_{iso}"] = bool(rng)
                if row["Pt_H_GPa"] is not None and row["Pt_D_GPa"] is not None:
                    row["dP_iso_GPa"] = round(row["Pt_D_GPa"] - row["Pt_H_GPa"], 3)
                entry["T"][str(T)] = row
                print(cname, model, T, json.dumps(row), flush=True)
            out[f"{cname}/{model}"] = entry
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
