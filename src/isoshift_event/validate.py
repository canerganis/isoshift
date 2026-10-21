"""Gate validation runs (PLAN.md P1 tier B): QHA H/D for structures with measured isotope volume effects.

    python -m src.isoshift_event.validate submit      # write primitive CIFs, queue QHA jobs for 4 models
    python -m src.isoshift_event.validate run         # serve the queue one model at a time (blocking)
    python -m src.isoshift_event.validate collect     # results/validation/volume_isotope.csv (CPU only)

Uses the pre-event pool (isoshift.pool) and QHA (isoshift.qha) unchanged.

`collect` (gate G2, docs/decisions/01-gate.md) does not use the stored V(T) of qha_gibbs, whose phonopy
thermal sums kept the near-zero Gamma acoustic modes and silently dropped imaginary modes. It rebuilds
F_vib per QHA volume from that volume's cached force constants, drops the 3 Gamma acoustic modes as in
M01 (1), and repeats the EOS fit (PhonopyQHA, vinet) on the same volumes and E0 for four treatments of
the non-acoustic imaginary modes: omit, |w|, 2|w|, fixed 3 THz. The treatment spread is the error bar
for the imaginary branch (decision 00): a sensitivity bracket, not an anharmonic calculation.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "results" / "queue" / "validation"
RAW = ROOT / "results" / "raw" / "validation"
OUT = ROOT / "results" / "validation"
PRIM = ROOT / "data" / "isoshift" / "validation_structures" / "prim"
MODELS = ("mace", "orb", "mattersim", "sevenn")
# name -> (MP CIF in validation_structures, measured V_H/V_D - 1 in %, T of measurement K, note)
# Numbers trace to rows of data/isoshift/validation.csv (derived_isotope_effect_pct column).
CASES = {
    "brucite": ("MgOH2_mp-30247_P-3m1.cif", 0.31, 295,
                "Chakoumakos 2013 abstract, 10.2138/am.2013.4202; room T, 295 K from COD 1557014; sign also Horita 2010"),
    "portlandite": ("CaOH2_mp-23879_P-3m1.cif", None, 295,
                    "no clean experimental pair; null check per PLAN P12 (cross-lab +0.67% is not a target)"),
    "LiH": ("LiH_mp-23703_Fm-3m.cif", 0.81, 300,
            "Loubeyre 1998 a(300 K) via Dammak 2012 Table 2, 10.1088/0953-8984/24/43/435402; "
            "Smith-Leider 0.014 A shift in the same source gives +1.04% (inferred)"),
    "iceXI": ("H2O_mp-697111_Cmc2_1.cif", -0.075, 100,
              "reported only (P12); Pamuk 2012 Table I 100 K, 10.1103/PhysRevLett.108.193003: this work -0.075%, "
              "Rottger 1994 row -0.078%; ice Ih measurement vs ordered ice XI proxy"),
}
QHA_KW = {"n_vol": 9, "vol_range": [-0.04, 0.12], "min_length": 9.5, "max_atoms": 160,
          "temps": list(range(0, 401, 10))}


def submit():
    from pymatgen.core import Structure

    from isoshift import pool

    PRIM.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, (cif, *_rest) in CASES.items():
        prim = PRIM / f"{name}.cif"
        if not prim.exists():
            Structure.from_file(ROOT / "data" / "isoshift" / "validation_structures" / cif).get_primitive_structure().to(filename=str(prim))
        for m in MODELS:
            jid = pool.submit(QUEUE, "qha", str(prim), m, str(RAW / m / f"{name}.json"), **QHA_KW)
            n += jid is not None
    print(f"queued {n} jobs in {QUEUE}")


def run(idle_exit_s: float = 20.0):
    from isoshift import pool

    for m in MODELS:
        cmd = pool.launch_cmd(m, QUEUE, idle_exit_s=idle_exit_s, mem_fraction=0.5)
        print("serve", m, flush=True)
        subprocess.run(cmd, cwd=ROOT, check=False)


TREATMENTS = ("omit", "abs", "2abs", "fix3THz")  # imaginary non-acoustic modes: drop, |w|, 2|w|, 3 THz
FIX_THZ = 3.0
EV_KJMOL = 96.48533212
SC_MAX_ATOMS = QHA_KW["max_atoms"]
V_TOL, E_TOL = 1e-8, 1e-3  # A^3, eV: volume is bit-identical for the QHA entry; E0 (relax) vs meta (recomputed) up to 4e-4 eV for orb


def _safe_id(calc_id: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in calc_id)


def _qha_fcs(name: str, r: dict):
    """Cached force constants for every QHA volume of one raw result.

    Match: calc id in the cache key, natoms_cell, volume and energy against the 'volumes' / 'E0' arrays
    (the volume is written from the same relaxed Atoms and agrees bit for bit; other runs of the same
    structure sit 1e-6 to 1e-3 A^3 away and must not be picked), element multiset of the primitive CIF. If one volume
    still has several entries, prefer the supercell qha_gibbs would have hit first (supercell_for_min_length
    with QHA_KW), then the closest match, then the largest supercell within max_atoms."""
    import phonopy
    from ase import Atoms
    from ase.io import read

    from isoshift import cache as K
    from isoshift import phonons as P

    vols, e0 = np.array(r["volumes"]), np.array(r["E0"])
    want = sorted(read(PRIM / f"{name}.cif").get_chemical_symbols())
    tag = f"__{_safe_id(r['calc_id'])}__"
    cand = {}
    for d in K.CACHE_ROOT.iterdir():
        if tag not in d.name or not (d / "meta.json").exists():
            continue
        meta = json.loads((d / "meta.json").read_text())
        if meta.get("natoms_cell") != r["n_atoms_cell"] or meta.get("volume_A3") is None:
            continue
        i = int(np.argmin(np.abs(vols - meta["volume_A3"])))
        dv, de = abs(vols[i] - meta["volume_A3"]), abs(e0[i] - meta.get("energy_eV", np.inf))
        if dv > V_TOL or de > E_TOL:
            continue
        meta = dict(meta, _dist=(dv, de))
        if meta.get("natoms_supercell", 0) > SC_MAX_ATOMS:
            continue
        cand.setdefault(i, []).append((d, meta))
    out = []
    for i in range(len(vols)):
        if i not in cand:
            raise FileNotFoundError(f"{name} {r['calc_id']}: no cached FC for volume {vols[i]:.4f}")
        loaded = []
        for d, meta in cand[i]:
            ph = phonopy.load(str(d / "phonopy_params.yaml"), produce_fc=False, log_level=0)
            if sorted(ph.unitcell.symbols) == want:
                loaded.append((ph, meta))
        if not loaded:
            raise FileNotFoundError(f"{name} {r['calc_id']}: cached FC at volume {vols[i]:.4f} has other elements")
        uc = loaded[0][0].unitcell
        at = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
        exp_sc = np.diag(P.supercell_for_min_length(at, QHA_KW["min_length"], SC_MAX_ATOMS)).tolist()
        loaded.sort(key=lambda x: (list(x[1]["supercell"]) != exp_sc, x[1]["_dist"], -x[1]["natoms_supercell"]))
        out.append(loaded[0])
    return out


def _spectrum(ph, masses, mesh):
    """Gamma-centred mesh spectrum and the mask of modes kept per M01 (1): the 3 smallest |w| at Gamma out."""
    from isoshift import phonons as P

    p = P.phonopy_with_masses(ph, masses)
    p.run_mesh(list(mesh), with_eigenvectors=False, is_mesh_symmetry=True, is_gamma_center=True)
    f = np.array(p.mesh.frequencies, float)
    w = np.array(p.mesh.weights, float)
    q = np.array(p.mesh.qpoints, float)
    ig = np.flatnonzero(np.all(np.abs(q - np.round(q)) < 1e-8, axis=1))
    if len(ig) != 1:
        raise RuntimeError(f"expected one Gamma row in the mesh, found {len(ig)}")
    keep = np.ones(f.shape, bool)
    ac = np.argsort(np.abs(f[ig[0]]))[:3]
    keep[ig[0], ac] = False
    return f, w / w.sum(), keep, float(np.abs(f[ig[0], ac]).max())


def _thermo(f, w, keep, treatment, temps):
    """F (kJ/mol), S and Cv (J/K/mol) per cell (phonopy QHA units) for one imaginary-mode treatment.
    Imaginary = non-acoustic w < 0. Positive modes are kept however small (M01 (1)); exact zeros drop out."""
    from isoshift import phonons as P

    imag = keep & (f < 0)
    g = f.copy()
    use = keep.copy()
    if treatment == "omit":
        use &= ~imag
    elif treatment == "abs":
        g[imag] = -f[imag]
    elif treatment == "2abs":
        g[imag] = -2.0 * f[imag]
    elif treatment == "fix3THz":
        g[imag] = FIX_THZ
    else:
        raise ValueError(treatment)
    use &= g > 0
    e = np.where(use, P.H_EV_THZ * g, 1.0)[None]  # (1, nq, nb) eV
    W = (w[:, None] * use)[None]
    T = np.asarray(temps, float)[:, None, None]
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        x = np.where(T > 0, e / (P.KB_EV * np.where(T > 0, T, 1.0)), np.inf)
        ln1m = np.log1p(-np.exp(-x))
        fterm = 0.5 * e + np.where(T > 0, P.KB_EV * T * ln1m, 0.0)
        sterm = np.where(np.isfinite(x), P.KB_EV * (x / np.expm1(x) - ln1m), 0.0)
        cterm = np.where(np.isfinite(x) & (x < 700), P.KB_EV * x ** 2 * np.exp(np.minimum(x, 700)) / np.expm1(np.minimum(x, 700)) ** 2, 0.0)
    F = (np.nan_to_num(fterm) * W).sum(axis=(1, 2))
    S = (np.nan_to_num(sterm) * W).sum(axis=(1, 2))
    C = (np.nan_to_num(cterm) * W).sum(axis=(1, 2))
    return F * EV_KJMOL, S * EV_KJMOL * 1000, C * EV_KJMOL * 1000


def _qha_v(vols, e0, temps, thermo_per_vol):
    import warnings

    from phonopy import PhonopyQHA

    fe, se, cv = (np.array(x).T for x in zip(*thermo_per_vol))  # (nT, nV)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)  # same class qha.py uses (phonopy 4.8.3)
        q = PhonopyQHA(volumes=vols, electronic_energies=e0, temperatures=temps, free_energy=fe, cv=cv, entropy=se,
                       eos="vinet", pressure=0.0, t_max=float(temps[-1]))
    return np.array(q.volume_temperature)


def _vie_case(name: str, r: dict):
    """V_H(T), V_D(T) per treatment for one (case, model), plus diagnostics over the volume grid."""
    from ase import Atoms

    from isoshift import phonons as P

    vols, e0, temps = np.array(r["volumes"]), np.array(r["E0"]), np.array(r["temperatures"], float)
    fcs = _qha_fcs(name, r)
    uc0 = fcs[int(np.argmin(np.abs(vols - r["V0_relaxed"])))][0].unitcell
    a0 = Atoms(uc0.symbols, cell=uc0.cell, scaled_positions=uc0.scaled_positions, pbc=True)
    mesh = P.choose_mesh(a0)  # qha_gibbs uses one mesh for all volumes, chosen at the relaxed V0
    spec = {}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        masses = P.make_masses(a0, sub, default="light")
        spec[iso] = [_spectrum(ph, masses, mesh) for ph, _m in fcs]
    v = {}
    for t in TREATMENTS:
        for iso in ("H", "D"):
            v[(iso, t)] = _qha_v(vols, e0, temps, [_thermo(f, w, k, t, temps) for f, w, k, _a in spec[iso]])
    imag_frac = [float((((f < P.IMAG_TOL_THZ) & k) * w[:, None]).sum() / f.shape[1]) for f, w, k, _a in spec["H"]]
    diag = {"imag_frac": imag_frac, "min_freq": min(float(f[k].min()) for f, _w, k, _a in spec["H"]),
            "acoustic_max": max(a for s in spec.values() for *_x, a in s),
            "n_sc": sorted({m["natoms_supercell"] for _ph, m in fcs}), "mesh": mesh}
    return temps, vols, v, diag


def _vie_job(name: str, m: str):
    r = json.loads((RAW / m / f"{name}.json").read_text())
    return r, _vie_case(name, r)


def collect(workers: int | None = None):
    """Gate G2: Gamma-free QHA volume isotope effect with the imaginary-mode bracket (CPU, cached FCs).
    One process per (case, model); the time goes into parsing the force-constant YAMLs."""
    import os
    import time
    from concurrent.futures import ProcessPoolExecutor

    os.environ["CUDA_VISIBLE_DEVICES"] = ""  # CPU only; nothing here needs a model
    t_start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(name, m) for name in CASES for m in MODELS if (RAW / m / f"{name}.json").exists()]
    workers = workers or max(1, min(len(jobs), (os.cpu_count() or 2) // 2))
    with ProcessPoolExecutor(workers) as ex:
        done = dict(zip(jobs, ex.map(_vie_job, *zip(*jobs))))
    rows = []
    for name, (_cif, exp, T_exp, note) in CASES.items():
        for m in MODELS:
            if (name, m) not in done:
                continue
            r, (temps, vols, v, diag) = done[(name, m)]
            it_exp = int(np.argmin(np.abs(temps - T_exp)))  # first nearest grid point (295 -> 290)
            for it in (0, it_exp):
                stored = r["variants"]["H"]["V_A3"][it] / r["variants"]["D"]["V_A3"][it] - 1
                for t in TREATMENTS:
                    vh, vd = v[("H", t)][it], v[("D", t)][it]
                    ok = bool(vols.min() - 1e-9 <= min(vh, vd) and max(vh, vd) <= vols.max() + 1e-9)
                    rows.append({"case": name, "model": m, "T_K": int(temps[it]), "treatment": t,
                                 "VIE_pct": round((vh / vd - 1) * 100, 5), "in_range": ok,
                                 "exp_VIE_pct": "" if it != it_exp or exp is None else exp,
                                 "exp_note": note if it == it_exp else "",
                                 "imag_frac_min_pct": round(min(diag["imag_frac"]) * 100, 4),
                                 "imag_frac_max_pct": round(max(diag["imag_frac"]) * 100, 4),
                                 "min_freq_THz": round(diag["min_freq"], 3),
                                 "gamma_acoustic_max_THz": round(diag["acoustic_max"], 4),
                                 "n_atoms_supercell": "/".join(map(str, diag["n_sc"])),
                                 "VIE_stored_pct": round(stored * 100, 5)})
            print(f"{name:11s} {m:9s} mesh={diag['mesh']} sc={diag['n_sc']} imag {min(diag['imag_frac'])*100:.2f}"
                  f"-{max(diag['imag_frac'])*100:.2f}% min {diag['min_freq']:+.2f} THz "
                  f"Gamma acoustic max |w| {diag['acoustic_max']:.4f} THz", flush=True)
    with open(OUT / "volume_isotope.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print()
    for r in rows:
        print(f"{r['case']:11s} {r['model']:9s} T={r['T_K']:3d} {r['treatment']:7s} VIE={r['VIE_pct']:+.3f}% "
              f"(stored {r['VIE_stored_pct']:+.3f})  exp={r['exp_VIE_pct']}  in_range={r['in_range']}")
    # Gate pass rule (01-gate G2, PLAN P12): brucite and LiH sign right in >= 3 models under every treatment
    ok_all = True
    print()
    for name in ("brucite", "LiH"):
        exp = CASES[name][1]
        for t in TREATMENTS:
            sel = [x for x in rows if x["case"] == name and x["treatment"] == t and x["exp_VIE_pct"] != ""]
            good = [x["model"] for x in sel if x["in_range"] and np.sign(x["VIE_pct"]) == np.sign(exp)]
            ok = len(good) >= 3
            ok_all &= ok
            print(f"PASS-RULE {name:8s} {t:7s} sign right {len(good)}/{len(sel)} ({','.join(good)}) -> {'ok' if ok else 'FAIL'}")
    print(f"G2 pass rule (brucite and LiH sign right in >=3 models, every treatment): {'PASS' if ok_all else 'FAIL'}"
          f"   ({time.time() - t_start:.0f} s)")
    return ok_all


if __name__ == "__main__":
    commands = {"submit": submit, "run": run, "collect": collect}
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(__doc__)
        sys.exit(0 if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help") else 2)
    commands[sys.argv[1]]()
