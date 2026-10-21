"""Ice polymorph boundaries: blind prediction of the H2O -> D2O shift (P05, docs/predictions/P05_ice_boundary_blind.md).

Phases (ordered cells only, so harmonic phonons are defined):
    iceXI  Cmc2_1  mp-697111  proxy for ice Ih  (vibrational part only, see below)
    iceII  R-3     mp-24043   ice II is proton ordered, used as is
    iceIX  P4_12_12 mp-696735 proxy for ice III (secondary boundaries only)

Proxy assumption. Ice Ih (and III) are proton disordered. Their configurational (Pauling) entropy,
k_B ln(3/2) per H2O for Ih, does not depend on the hydrogen mass, so it cancels in the isotope double
difference ddG_iso = [G_D - G_H]_b - [G_D - G_H]_a to first order. The isotope shift of the Ih-II boundary
is then vibrational, and the vibrational part of Ih is approximated by its ordered counterpart XI.
Limits: (i) the phonon spectrum of a disordered Ih is not that of XI (librations and the O-H stretch are
broadened and slightly shifted); (ii) the Pauling term still enters dS, so for the temperature shift
dT = ddG/dS we add -k_B ln(3/2) to dS(II - Ih); (iii) partial ordering of ice III is not modelled and may itself
be isotope dependent, so boundaries with III (IX proxy) are secondary.

Method. One QHA volume scan per (phase, model) at 0 GPa (isoshift.qha via the pool, fixed supercells:
min_length 10 A, max_atoms 300, no OOM shrink). `collect` rebuilds Gamma-free F_vib per volume from the
cached force constants (3 smallest |w| at Gamma dropped, M01 (1)), with the four imaginary-mode treatments of
validate.py (omit, |w|, 2|w|, 3 THz), and fits G(T, P) = min_V [E0 + F_vib + P V] (phonopy QHA, vinet) on a
pressure grid. Per H2O, for a boundary a -> b (b denser):
    dG_X = G_b - G_a,  ddG_iso = [G_D - G_H]_b - [G_D - G_H]_a,  dV = V_b - V_a  (H values)
    dP_iso ~ -ddG_iso / dV  (M02, first order, at fixed T)
    dT_iso ~ ddG_iso / dS,  dS = -d(dG_H)/dT + dS_conf  (at fixed P)
    1000 ln alpha(a - b) = 1000 ddG_iso / (n_H k_B T), n_H = 2  (M02, full substitution)
evaluated at reference points of the boundary (fixed T and P grid). The model's own H boundary (root of dG_H,
with the Pauling term added to the disordered phase) and the exact root shift are reported as diagnostics.

    python -m src.isoshift_event.ice_boundary submit
    python -m src.isoshift_event.ice_boundary launch [mace orb ...]
    python -m src.isoshift_event.ice_boundary refc <model> [cpu]   # redo volumes whose supercell shrank after OOM
    python -m src.isoshift_event.ice_boundary collect      # CPU only -> results/ice_boundary.json, .csv
"""
from __future__ import annotations

import csv
import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "results" / "queue" / "ice"
RAW = ROOT / "results" / "raw" / "ice"
OUT_JSON = ROOT / "results" / "ice_boundary.json"
OUT_CSV = ROOT / "results" / "ice_boundary.csv"
SRC = ROOT / "data" / "isoshift" / "validation_structures"
PRIM = SRC / "prim"
PHASES = {"iceXI": "H2O_mp-697111_Cmc2_1.cif", "iceII": "H2O_mp-24043_R-3.cif", "iceIX": "H2O_mp-696735_P4_12_12.cif"}
MODELS = ("mace", "orb", "mattersim")
QHA_KW = {"n_vol": 11, "vol_range": [-0.08, 0.12], "min_length": 10.0, "max_atoms": 300,
          "temps": list(range(0, 321, 10)), "allow_shrink": False}
KB = 8.617333262145e-5  # eV/K
EV_GPA_A3 = 0.006241509074460763  # eV per (GPa A^3)
N_H = 2
S_PAULING = KB * np.log(1.5)  # eV/K per H2O, configurational entropy of Ih and of fully disordered phases
DS_GUARD = 3e-5  # eV/K per H2O, M01 (3) slope guard 0.01 meV/atom/K times 3 atoms
PRESSURES = np.round(np.arange(-0.2, 1.0001, 0.05), 3)
TREATMENTS = ("omit", "abs", "2abs", "fix3THz")
# boundary: (low-pressure phase a, high-pressure phase b, configurational entropy of a and b in units of S_PAULING,
#            reference temperatures K, reference pressures GPa, role)
BOUNDARIES = {
    "Ih-II": ("iceXI", "iceII", (1.0, 0.0), (150, 170, 190, 210, 230, 250), (0.0, 0.2, 0.4), "primary"),
    "Ih-III": ("iceXI", "iceIX", (1.0, None), (240, 250, 260), (0.2, 0.3), "secondary"),
    "II-III": ("iceII", "iceIX", (0.0, None), (240, 250, 260), (0.2, 0.3, 0.4), "secondary"),
}


def _prim_path(name):
    return PRIM / f"{name}.cif"


def submit(models=MODELS):
    from pymatgen.core import Structure

    from isoshift import pool

    PRIM.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, cif in PHASES.items():
        prim = _prim_path(name)
        if not prim.exists():
            Structure.from_file(SRC / cif).get_primitive_structure().to(filename=str(prim))
        for m in models:
            jid = pool.submit(QUEUE, "qha", str(prim), m, str(RAW / m / f"{name}.json"), **QHA_KW)
            n += jid is not None
            print(name, m, jid)
    print(f"queued {n} jobs in {QUEUE}")


def launch(models=("mace", "orb"), mem_fraction=0.3):
    from isoshift import pool

    os.environ["OMP_NUM_THREADS"] = "3"
    for m in models:
        print(m, pool.launch(m, QUEUE, idle_exit_s=900.0, mem_fraction=mem_fraction))


def _configure_validate():
    from src.isoshift_event import validate as V

    V.PRIM = PRIM
    V.QHA_KW = dict(QHA_KW)
    V.SC_MAX_ATOMS = QHA_KW["max_atoms"]
    V.V_TOL = 1e-3
    V.E_TOL = 2e-2  # eV per cell: refc FCs are recomputed on the CPU, orb CPU vs GPU energies differ by ~4e-3 eV/cell
    return V


def refc(model, device="cpu", mem_fraction=0.3):
    """Recompute force constants at the fixed supercell where qha_gibbs fell back to a smaller one.

    isoshift.phonons.get_force_constants silently lowers min_length after a CUDA OOM (shared GPU), so some
    volumes of one scan can carry a smaller supercell than the others. Here the relaxed cell of each such
    volume (the unit cell stored with its cached FC) is redone with the explicit supercell that
    supercell_for_min_length(min_length 10, max_atoms 300) gives; an explicit supercell never shrinks, it fails.
    Default device is the CPU: the 288-atom ice II / IX supercells need more than the 0.3 GPU memory share.
    The new FC goes into the same cache, where validate._qha_fcs prefers it."""
    import torch
    from ase import Atoms

    from isoshift import phonons as PH
    from isoshift.calculators import get_calculator

    V = _configure_validate()
    if device.startswith("cuda") and torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(mem_fraction, device="cuda:0")
    calc = get_calculator(model, device)
    for name in PHASES:
        path = RAW / model / f"{name}.json"
        if not path.exists():
            continue
        r = json.loads(path.read_text())
        items = list(enumerate(V._qha_fcs(name, r)))
        if os.environ.get("ICE_REFC_REVERSE"):  # a second process can work from the other end of the volume grid
            items = items[::-1]
        for i, (ph, meta) in items:
            if os.environ.get("ICE_REFC_REVERSE") and list(meta["supercell"]) != np.diag(
                    PH.supercell_for_min_length(Atoms(ph.unitcell.symbols, cell=ph.unitcell.cell,
                                                      scaled_positions=ph.unitcell.scaled_positions, pbc=True),
                                                QHA_KW["min_length"], QHA_KW["max_atoms"])).tolist():
                fresh = V._qha_fcs(name, r)[i][1]  # skip volumes the forward process has finished meanwhile
                if list(fresh["supercell"]) != list(meta["supercell"]):
                    continue
            uc = ph.unitcell
            at = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
            exp = PH.supercell_for_min_length(at, QHA_KW["min_length"], QHA_KW["max_atoms"])
            if list(meta["supercell"]) == np.diag(exp).tolist():
                continue
            _ph, m2, hit = PH.get_force_constants(at, calc, r["calc_id"], supercell=exp, max_atoms=None)
            print(f"refc {model} {name} vol {i} {meta['supercell']} -> {m2['supercell']} cached={hit} "
                  f"dE={m2['energy_eV'] - r['E0'][i]:+.2e} dV={m2['volume_A3'] - r['volumes'][i]:+.2e}", flush=True)


BAND_T = 200.0


def _band_F(f, w, keep, nfu):
    """Harmonic F_vib at BAND_T (eV per H2O) split by mode rank at each q: per H2O the 3 lowest modes are
    translational, the next 3 librational, then 1 bend and 2 stretches. Imaginary modes are omitted. A diagnostic
    for which band carries ddG_iso (rank assignment, not an eigenvector projection)."""
    from isoshift import phonons as PH

    n = int(round(nfu))
    edges = {"trans": (0, 3 * n), "lib": (3 * n, 6 * n), "bend": (6 * n, 7 * n), "stretch": (7 * n, 9 * n)}
    order = np.argsort(f, axis=1)
    fs = np.take_along_axis(f, order, axis=1)
    ks = np.take_along_axis(keep, order, axis=1) & (fs > 0)
    e = PH.H_EV_THZ * np.where(ks, fs, 1.0)
    x = e / (PH.KB_EV * BAND_T)
    term = np.where(ks, 0.5 * e + PH.KB_EV * BAND_T * np.log1p(-np.exp(-x)), 0.0) * w[:, None]
    return {b: float(term[:, lo:hi].sum() / nfu) for b, (lo, hi) in edges.items()}


def _qha_phase(args):
    """Gamma-free G(T, P), V(T, P), S(T, P) per isotope and treatment for one (phase, model). eV, A^3 per H2O."""
    name, model = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    from ase import Atoms
    from phonopy import PhonopyQHA

    from isoshift import phonons as PH

    V = _configure_validate()
    r = json.loads((RAW / model / f"{name}.json").read_text())
    vols, e0, temps = np.array(r["volumes"]), np.array(r["E0"]), np.array(r["temperatures"], float)
    nfu = r["n_atoms_cell"] / 3
    fcs = V._qha_fcs(name, r)
    uc0 = fcs[int(np.argmin(np.abs(vols - r["V0_relaxed"])))][0].unitcell
    a0 = Atoms(uc0.symbols, cell=uc0.cell, scaled_positions=uc0.scaled_positions, pbc=True)
    mesh = PH.choose_mesh(a0)
    res = {"n_fu": nfu, "volumes_A3_fu": (vols / nfu).tolist(), "E0_eV_fu": (e0 / nfu).tolist(), "T": temps.tolist(),
           "P": PRESSURES.tolist(), "mesh": list(mesh), "n_sc": sorted({m["natoms_supercell"] for _p, m in fcs}),
           "relax": {"fmax_V0": None}, "iso": {}}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        masses = PH.make_masses(a0, sub, default="light")
        spec = [V._spectrum(ph, masses, mesh) for ph, _m in fcs]
        if iso == "H":
            res["imag_frac_pct"] = [round(100 * float((((f < PH.IMAG_TOL_THZ) & k) * w[:, None]).sum() / f.shape[1]), 4)
                                    for f, w, k, _a in spec]
            res["min_freq_THz"] = [round(float(f[k].min()), 3) for f, w, k, _a in spec]
            res["gamma_acoustic_max_THz"] = max(a for *_x, a in spec)
        res.setdefault("bands", {})[iso] = [_band_F(f, w, k, nfu) for f, w, k, _a in spec]
        out = {}
        for t in TREATMENTS:
            th = [V._thermo(f, w, k, t, temps) for f, w, k, _a in spec]
            fe, se, cv = (np.array(x).T for x in zip(*th))
            G = np.full((len(PRESSURES), len(temps)), np.nan)
            Vt = np.full_like(G, np.nan)
            for ip, P in enumerate(PRESSURES):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    q = PhonopyQHA(volumes=vols, electronic_energies=e0, temperatures=temps, free_energy=fe, cv=cv,
                                   entropy=se, eos="vinet", pressure=float(P), t_max=float(temps[-1]))
                g, v = np.array(q.gibbs_temperature), np.array(q.volume_temperature)
                G[ip, :len(g)] = g / nfu
                Vt[ip, :len(v)] = v / nfu
            out[t] = {"G_eV_fu": G.tolist(), "V_A3_fu": Vt.tolist()}
        res["iso"][iso] = out
    return (name, model), res


def _interp_T(arr, temps, T):
    return float(np.interp(T, temps, arr))


def _boundary(pa, pb, conf, T_ref, P_ref, temps, Pgrid, treatment):
    """Isotope quantities for one boundary, one model, one treatment."""
    sa, sb = conf
    out = {"ref": [], "model_boundary": []}
    g = {(ph, iso): np.array(d["iso"][iso][treatment]["G_eV_fu"]) for ph, d in (("a", pa), ("b", pb)) for iso in "HD"}
    v = {(ph, iso): np.array(d["iso"][iso][treatment]["V_A3_fu"]) for ph, d in (("a", pa), ("b", pb)) for iso in "HD"}
    vr = {"a": (min(pa["volumes_A3_fu"]), max(pa["volumes_A3_fu"])), "b": (min(pb["volumes_A3_fu"]), max(pb["volumes_A3_fu"]))}
    dG = {iso: g[("b", iso)] - g[("a", iso)] for iso in "HD"}  # (nP, nT), vibrational + static only
    ddG = dG["D"] - dG["H"]
    dV = v[("b", "H")] - v[("a", "H")]
    inr = np.ones_like(dV, bool)
    for ph in "ab":
        for iso in "HD":
            inr &= (v[(ph, iso)] >= vr[ph][0] - 1e-9) & (v[(ph, iso)] <= vr[ph][1] + 1e-9)
    dGdT = np.gradient(dG["H"], temps, axis=1)
    dS_vib = -dGdT
    dS_conf = None if (sa is None or sb is None) else (sb - sa) * S_PAULING
    for P in P_ref:
        ip = int(np.argmin(np.abs(Pgrid - P)))
        for T in T_ref:
            it = int(np.argmin(np.abs(temps - T)))
            dd, dv = float(ddG[ip, it]), float(dV[ip, it])
            row = {"T_K": float(temps[it]), "P_GPa": float(Pgrid[ip]), "ddG_meV_fu": 1000 * dd, "dV_A3_fu": dv,
                   "dP_iso_GPa": -dd / (EV_GPA_A3 * dv), "L_permil_a_minus_b": 1000 * dd / (N_H * KB * temps[it]),
                   "dS_vib_kB_fu": float(dS_vib[ip, it]) / KB, "in_range": bool(inr[ip, it]),
                   "dG_H_meV_fu_vib_static": 1000 * float(dG["H"][ip, it])}
            # M01 (3) slope guard: |dS| >= 0.01 meV/atom/K = 3e-5 eV/K per H2O, else the linear dT is not reported
            row["dT_iso_K_vib_only"] = dd / float(dS_vib[ip, it]) if abs(dS_vib[ip, it]) >= DS_GUARD else None
            if dS_conf is not None:
                dS = float(dS_vib[ip, it]) + dS_conf
                row["dS_total_kB_fu"] = dS / KB
                row["dT_iso_K"] = dd / dS if abs(dS) >= DS_GUARD else None
                row["dT_guard_failed"] = abs(dS) < DS_GUARD
            # model's own H-boundary location, first order from this reference point (static energies included)
            row["Pt_H_model_linear_GPa"] = float(Pgrid[ip]) - (float(dG["H"][ip, it]) - temps[it] * (dS_conf or 0.0)) / (EV_GPA_A3 * dv)
            out["ref"].append(row)
    # model's own H boundary at each T (root in P of dG_H - T dS_conf), and exact D root
    if dS_conf is not None:
        for it, T in enumerate(temps):
            if T < 100:
                continue
            roots = {}
            for iso in "HD":
                y = dG[iso][:, it] - T * dS_conf
                ok = np.isfinite(y)
                s = np.flatnonzero(np.diff(np.sign(y[ok])) != 0)
                if len(s) != 1:
                    roots[iso] = None
                    continue
                x = Pgrid[ok]
                i = s[0]
                roots[iso] = float(x[i] - y[ok][i] * (x[i + 1] - x[i]) / (y[ok][i + 1] - y[ok][i]))
            row = {"T_K": float(T), "Pt_H_GPa": roots["H"], "Pt_D_GPa": roots["D"]}
            if roots["H"] is not None and roots["D"] is not None:
                row["dP_exact_GPa"] = roots["D"] - roots["H"]
            out["model_boundary"].append(row)
    return out


def collect(workers: int | None = None, models=MODELS):
    from concurrent.futures import ProcessPoolExecutor

    jobs = [(n, m) for n in PHASES for m in models if (RAW / m / f"{n}.json").exists()]
    workers = workers or max(1, min(len(jobs), 3))
    with ProcessPoolExecutor(workers) as ex:
        done = dict(ex.map(_qha_phase, jobs))
    result = {"phases": {}, "boundaries": {}}
    for (n, m), d in done.items():
        result["phases"][f"{n}/{m}"] = {k: d[k] for k in ("n_fu", "n_sc", "mesh", "imag_frac_pct", "min_freq_THz",
                                                          "gamma_acoustic_max_THz", "volumes_A3_fu")}
        Pz = int(np.argmin(np.abs(PRESSURES)))
        result["phases"][f"{n}/{m}"]["V_H_0GPa_A3_fu"] = {str(int(T)): d["iso"]["H"]["omit"]["V_A3_fu"][Pz][i]
                                                          for i, T in enumerate(d["T"]) if T in (0, 100, 200, 250)}
        print(f"{n:6s} {m:9s} sc={d['n_sc']} mesh={d['mesh']} imag% max {max(d['imag_frac_pct']):.3f} "
              f"min w {min(d['min_freq_THz']):+.2f} THz V(0GPa,0K)={d['iso']['H']['omit']['V_A3_fu'][Pz][0]:.3f}", flush=True)
    rows = []
    for bname, (a, b, conf, T_ref, P_ref, role) in BOUNDARIES.items():
        for m in models:
            if (a, m) not in done or (b, m) not in done:
                continue
            pa, pb = done[(a, m)], done[(b, m)]
            temps = np.array(pa["T"], float)
            ent = {}
            for t in TREATMENTS:
                ent[t] = _boundary(pa, pb, conf, T_ref, P_ref, temps, PRESSURES, t)
                for r in ent[t]["ref"]:
                    rows.append({"boundary": bname, "role": role, "model": m, "treatment": t, **r})
            ent["imag_frac_pct_max"] = {a: max(pa["imag_frac_pct"]), b: max(pb["imag_frac_pct"])}
            ent["quarantine_gt2pct_imag"] = max(ent["imag_frac_pct_max"].values()) > 2.0  # decision 02 rule 4
            ent["single_supercell"] = len(pa["n_sc"]) == 1 and len(pb["n_sc"]) == 1
            summ = {}
            for r in ent["omit"]["ref"]:
                k = f"T{r['T_K']:.0f}_P{r['P_GPa']:.2f}"
                vals = [x["dP_iso_GPa"] for t in TREATMENTS for x in ent[t]["ref"]
                        if x["T_K"] == r["T_K"] and x["P_GPa"] == r["P_GPa"]]
                summ[k] = {"dP_iso_MPa_omit": 1000 * r["dP_iso_GPa"], "dP_iso_MPa_bracket": [1000 * min(vals), 1000 * max(vals)],
                           "ddG_meV_fu": r["ddG_meV_fu"], "L_permil": r["L_permil_a_minus_b"], "dT_iso_K": r.get("dT_iso_K"),
                           "in_range": r["in_range"]}
            ent["summary"] = summ
            # band split of the harmonic ddF at BAND_T, each phase at the scan volume nearest its V_H(BAND_T, 0.2 GPa)
            ip, it = int(np.argmin(np.abs(PRESSURES - 0.2))), int(np.argmin(np.abs(temps - BAND_T)))
            dd = {}
            for sign, d in ((-1, pa), (1, pb)):
                iv = int(np.argmin(np.abs(np.array(d["volumes_A3_fu"]) - d["iso"]["H"]["omit"]["V_A3_fu"][ip][it])))
                for band in d["bands"]["H"][iv]:
                    dd[band] = dd.get(band, 0.0) + sign * 1000 * (d["bands"]["D"][iv][band] - d["bands"]["H"][iv][band])
            ent["ddF_band_meV_fu_200K"] = dd
            result["boundaries"][f"{bname}/{m}"] = ent
    OUT_JSON.write_text(json.dumps(result, indent=1, default=float))
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    for r in rows:
        if r["treatment"] == "omit":
            print(f"{r['boundary']:6s} {r['model']:9s} T={r['T_K']:5.0f} P={r['P_GPa']:+.2f} ddG={r['ddG_meV_fu']:+.3f} meV/H2O "
                  f"dV={r['dV_A3_fu']:+.3f} dP_iso={r['dP_iso_GPa']*1000:+.1f} MPa dT={r.get('dT_iso_K')} "
                  f"dSvib={r['dS_vib_kB_fu']:+.3f} kB L={r['L_permil_a_minus_b']:+.2f} Pt_model={r['Pt_H_model_linear_GPa']:+.2f} "
                  f"in_range={r['in_range']}")
    for k, e in result["boundaries"].items():
        print(k, "imag% max", e["imag_frac_pct_max"], "quarantine", e["quarantine_gt2pct_imag"],
              "single_supercell", e["single_supercell"],
              "ddF bands 200K meV/H2O", {b: round(v, 3) for b, v in e["ddF_band_meV_fu_200K"].items()})
    return result


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "submit":
        submit(tuple(args) or MODELS)
    elif cmd == "launch":
        launch(tuple(args) or ("mace", "orb"))
    elif cmd == "refc":
        refc(args[0], *(args[1:2] or ["cpu"]))
    elif cmd == "collect":
        collect(models=tuple(args) or MODELS)
    else:
        raise SystemExit(__doc__)
