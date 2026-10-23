"""P12 path-integral check: full H to D substitution free energy from PIMD (docs/predictions/P12_pimd.md).

Per structure: ring-polymer MD (normal-mode propagation, PILE-L thermostat) on the fixed relaxed cell of
the screen with MACE medium-mpa-0 in float64, and mass thermodynamic integration over the H mass,
    F(m_D) - F(m_H) = int_1^{g_D} 2 <K_H(g)>/g dg,  g = sqrt(m_H/m),  Gauss-Legendre in g,
with K_H the centroid-virial kinetic energy of the H atoms. The same-cell harmonic reference uses the cached
MACE force constants on the q-points commensurate with the PIMD supercell, and
    delta_anh = [F_D - F_H]_PIMD - [F_D - F_H]_harm,same cell        (meV per H).
Pair assembly (ddF_corr) is not done here.

Zero modes: the PIMD centroid includes the free translation of the whole supercell, which contributes the
mass-dependent term F_COM = -(3/2) kT ln M_tot (the free-particle path integral equals its classical value).
The harmonic reference drops the three Gamma acoustic modes (MeshFreqs convention, |nu| < GAMMA_TOL_THZ) and
adds this F_COM term back explicitly, so both sides count the same 3N degrees of freedom.

Units: A, eV, u, fs, K. Internal mass unit is eV fs^2 / A^2 (1 u = AMU_EV).

    python -m src.isoshift_event.pimd --struct mp-23940 --beads 32 --steps 20000 --out results/pimd/mp-23940_P32.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from isoshift import phonons as Ph

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "raw" / "screen" / "mace"
CACHE = ROOT / ".cache" / "isoshift"
STATE = ROOT / ".cache" / "pimd"
CALC_ID = "mace-medium-mpa-0"

HBAR_EV_FS = 0.6582119569  # eV fs
AMU_EV = 103.642697  # 1 u in eV fs^2 / A^2
KB_EV = Ph.KB_EV
M_H = Ph.MASS_MAP["H"]
M_D = Ph.MASS_MAP["D"]
G_D = float(np.sqrt(M_H / M_D))
MIN_LENGTH, MAX_ATOMS = 8.0, 128  # P12 supercell rule


# ---------------------------------------------------------------- force backends

class HarmonicForces:
    """V = 1/2 u.Phi.u, u = q - x0, on unwrapped coordinates. fc: (N, N, 3, 3) eV/A^2."""

    name = "harmonic"

    def __init__(self, fc, x0):
        fc = np.asarray(fc, dtype=float)
        n = fc.shape[0]
        self.phi = fc.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
        self.x0 = np.asarray(x0, dtype=float)

    def __call__(self, q):
        u = (q - self.x0).reshape(len(q), -1)
        g = u @ self.phi.T
        return -g.reshape(q.shape), 0.5 * np.einsum("pi,pi->p", u, g)

    def info(self):
        return {"backend": "harmonic"}


class MaceForces:
    """MACE medium-mpa-0, float64, conservative forces. All beads go through one batched forward pass, or
    through explicit chunks of bead_chunk beads (recorded in the output; never chosen silently)."""

    name = "mace"

    def __init__(self, atoms, device="cuda", bead_chunk=None, model="medium-mpa-0"):
        import torch
        from mace import data as mace_data
        from mace.calculators import mace_mp

        if device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("CUDA not available; P12 production runs on the GPU")
        self.calc = mace_mp(model=model, device=device, default_dtype="float64", dispersion=False)
        self.model = self.calc.models[0]
        dt = next(self.model.parameters()).dtype
        if dt != torch.float64:
            raise RuntimeError(f"MACE model dtype is {dt}, P12 needs float64")
        self.keyspec = mace_data.KeySpecification(info_keys=self.calc.info_keys, arrays_keys=self.calc.arrays_keys)
        self.atoms = atoms.copy()
        self.device = device
        self.bead_chunk = bead_chunk
        self.model_name = model

    def _batch(self, qs):
        from mace import data as mace_data
        from mace.tools import torch_geometric, torch_tools

        graphs = []
        with torch_tools.default_dtype("float64"):
            for q in qs:
                a = self.atoms.copy()
                a.positions = q
                a.wrap()  # only for the force call; the ring polymer itself stays unwrapped
                cfg = mace_data.config_from_atoms(a, key_specification=self.keyspec, head_name=self.calc.head)
                graphs.append(mace_data.AtomicData.from_config(cfg, z_table=self.calc.z_table, cutoff=self.calc.r_max,
                                                               heads=self.calc.available_heads))
        return torch_geometric.Batch.from_data_list(graphs).to(self.device)

    def __call__(self, q):
        import torch

        P, n = q.shape[:2]
        chunk = self.bead_chunk or P
        f, e = np.empty_like(q), np.empty(P)
        for s in range(0, P, chunk):
            t = min(P, s + chunk)
            try:
                out = self.model(self._batch(q[s:t]).to_dict(), compute_stress=False, training=False)
            except (torch.OutOfMemoryError, RuntimeError) as err:  # TorchScript raises a plain RuntimeError
                if "out of memory" not in str(err):
                    raise
                raise RuntimeError(f"GPU out of memory for a batch of {t - s} beads x {n} atoms in float64; "
                                   f"rerun with an explicit smaller --bead-chunk") from err
            f[s:t] = out["forces"].detach().cpu().numpy().reshape(t - s, n, 3)
            e[s:t] = out["energy"].detach().cpu().numpy()
        return f, e

    def info(self):
        import importlib.metadata as md

        import torch

        return {"backend": "mace", "model": self.model_name, "dtype": "float64", "device": self.device,
                "mace_torch": md.version("mace-torch"), "torch": torch.__version__, "bead_chunk": self.bead_chunk}


# ---------------------------------------------------------------- ring polymer

def nm_matrix(P):
    """Orthonormal real normal-mode matrix C (P, P): q_nm[k] = sum_j C[j, k] q[j]. Column 0 is the centroid
    (times sqrt(P)); frequencies omega_k = 2 omega_P sin(k pi / P)."""
    j = np.arange(P)[:, None]
    C = np.empty((P, P))
    for k in range(P):
        if k == 0:
            C[:, k] = 1.0
        elif 2 * k < P:
            C[:, k] = np.sqrt(2.0) * np.cos(2 * np.pi * j[:, 0] * k / P)
        elif 2 * k == P:
            C[:, k] = (-1.0) ** j[:, 0]
        else:
            C[:, k] = np.sqrt(2.0) * np.sin(2 * np.pi * j[:, 0] * k / P)
    return C / np.sqrt(P)


def nm_freqs(P, T):
    wP = P * KB_EV * T / HBAR_EV_FS
    return 2 * wP * np.sin(np.arange(P) * np.pi / P)


class RingPolymer:
    """P beads x N atoms, fixed cell, unwrapped coordinates. PILE-L (Ceriotti et al. 2010): centroid Langevin
    with tau0, internal modes critically damped (gamma_k = 2 omega_k), exact free ring-polymer step.
    Splitting "obabo" (Ceriotti 2010): O(dt/2) B(dt/2) A(dt) B(dt/2) O(dt/2). Splitting "baoab" (the "middle"
    scheme of Liu, Li and Liu, J. Chem. Phys. 145, 024103 (2016)): B(dt/2) A(dt/2) O(dt) A(dt/2) B(dt/2), same
    thermostat, much smaller time-step error in configurational averages such as the centroid-virial K."""

    def __init__(self, x0, masses_u, P, T, dt, tau0, forces, rng, splitting="obabo"):
        if splitting not in ("obabo", "baoab"):
            raise ValueError(splitting)
        self.splitting = splitting
        self.P, self.T, self.dt, self.tau0 = int(P), float(T), float(dt), float(tau0)
        self.forces, self.rng = forces, rng
        self.C = nm_matrix(self.P)
        self.wk = nm_freqs(self.P, self.T)
        self.q = np.repeat(np.asarray(x0, dtype=float)[None], self.P, axis=0)
        self.set_masses(masses_u)
        self.f, self.v = self.forces(self.q)

    def set_masses(self, masses_u, resample=True):
        """New per-atom masses (u). Momenta are redrawn from the bead Maxwell-Boltzmann distribution at the
        new masses, so they are consistent with the new mass from the first step."""
        self.m = np.asarray(masses_u, dtype=float) * AMU_EV  # (N,)
        dt, w = self.dt, self.wk
        gam = 2 * w
        gam[0] = 1.0 / self.tau0
        to, ta = (0.5 * dt, dt) if self.splitting == "obabo" else (dt, 0.5 * dt)  # O and A step lengths
        self.c1 = np.exp(-to * gam)[:, None, None]
        self.c2 = np.sqrt(1 - self.c1 ** 2)
        self.ta = ta
        self.cos = np.cos(w * ta)[:, None, None]
        self.sin = np.sin(w * ta)[:, None, None]
        if resample:
            self.p = self._to_beads(np.sqrt(self.m[None, :, None] * self.P * KB_EV * self.T)
                                    * self.rng.standard_normal(self.q.shape))

    def _to_nm(self, x):
        return (self.C.T @ x.reshape(self.P, -1)).reshape(x.shape)

    def _to_beads(self, x):
        return (self.C @ x.reshape(self.P, -1)).reshape(x.shape)

    def _thermo(self):
        pn = self._to_nm(self.p)
        s = np.sqrt(self.m[None, :, None] * self.P * KB_EV * self.T)
        pn = self.c1 * pn + self.c2 * s * self.rng.standard_normal(pn.shape)
        self.p = self._to_beads(pn)

    def _free(self):
        qn, pn = self._to_nm(self.q), self._to_nm(self.p)
        m = self.m[None, :, None]
        mw = m * self.wk[1:, None, None]
        q0 = qn[0] + pn[0] / m[0] * self.ta
        q1 = qn[1:] * self.cos[1:] + pn[1:] / mw * self.sin[1:]
        p1 = pn[1:] * self.cos[1:] - mw * qn[1:] * self.sin[1:]
        qn[0], qn[1:], pn[1:] = q0, q1, p1
        self.q, self.p = self._to_beads(qn), self._to_beads(pn)

    def step(self):
        if self.splitting == "obabo":
            self._thermo()
            self.p += 0.5 * self.dt * self.f
            self._free()
            self.f, self.v = self.forces(self.q)
            self.p += 0.5 * self.dt * self.f
            self._thermo()
        else:
            self.p += 0.5 * self.dt * self.f
            self._free()
            self._thermo()
            self._free()
            self.f, self.v = self.forces(self.q)
            self.p += 0.5 * self.dt * self.f

    def kinetic_cv(self, mask):
        """Centroid-virial kinetic energy (eV) of the atoms in mask."""
        qc = self.q.mean(axis=0)
        vir = np.einsum("pna,pna->", (self.q - qc)[:, mask], -self.f[:, mask])
        return 1.5 * int(np.sum(mask)) * KB_EV * self.T + vir / (2 * self.P)


# ---------------------------------------------------------------- statistics and quadrature

def block_error(x, min_blocks=16):
    """Standard error of the mean from blocks of size 1, 2, 4, ... while at least min_blocks blocks remain.
    Returns (err, curve) with err the maximum over the curve (conservative) and curve [(size, n_blocks, err)]."""
    x = np.asarray(x, dtype=float)
    curve, b = [], 1
    while len(x) // b >= min_blocks:
        nb = len(x) // b
        m = x[: nb * b].reshape(nb, b).mean(axis=1)
        curve.append((b, nb, float(m.std(ddof=1) / np.sqrt(nb))))
        b *= 2
    if not curve:
        return float("nan"), curve
    return max(c[2] for c in curve), curve


def ti_nodes(n=4, g_lo=G_D):
    """Gauss-Legendre nodes and weights on [g_lo, 1], nodes in descending g (H side first)."""
    x, w = np.polynomial.legendre.leggauss(n)
    g = 0.5 * (1 + g_lo) + 0.5 * (1 - g_lo) * x
    w = 0.5 * (1 - g_lo) * w
    o = np.argsort(-g)
    return g[o], w[o]


def ti_integrate(g, w, k, k_err=None):
    """F(m_D) - F(m_H) = -sum w 2 K(g)/g (integral from 1 down to g_D), with propagated error."""
    g, w, k = map(np.asarray, (g, w, k))
    df = -float(np.sum(w * 2 * k / g))
    if k_err is None:
        return df
    return df, float(np.sqrt(np.sum((w * 2 * np.asarray(k_err) / g) ** 2)))


# ---------------------------------------------------------------- harmonic references

def _osc_free_energy(nu_thz, T, P=None):
    """Quantum (P=None) or P-bead discretized harmonic free energy, eV, for frequencies in THz."""
    kT = KB_EV * T
    w = 2 * np.pi * np.asarray(nu_thz, dtype=float) * 1e-3  # rad/fs
    if P is None:
        return kT * np.log(2 * np.sinh(HBAR_EV_FS * w / (2 * kT)))
    wk = nm_freqs(P, T)
    return kT * np.sum(np.log(HBAR_EV_FS * np.sqrt(w[..., None] ** 2 + wk ** 2) / (P * kT)), axis=-1)


def com_free_energy(total_mass_u, T):
    """Mass-dependent part of the free translation of the whole cell, -(3/2) kT ln M (eV)."""
    return -1.5 * KB_EV * T * np.log(total_mass_u)


def commensurate_qpoints(sc):
    n = [int(x) for x in sc]
    return np.array([[i / n[0], j / n[1], k / n[2]] for i in range(n[0]) for j in range(n[1]) for k in range(n[2])])


def harmonic_samecell(ph, sc, T, P=None):
    """Same-cell harmonic F_D - F_H for the supercell sc (diagonal ints) from the force constants of ph.

    Returns a dict with dF per supercell (eV), the Gamma zero modes dropped, imaginary-mode flags and, if P is
    given, the P-bead discretized value as a diagnostic."""
    from ase import Atoms

    uc = ph.unitcell
    atoms = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    qpts = commensurate_qpoints(sc)
    out = {"n_qpoints": len(qpts)}
    F, Fp, tot_m = {}, {}, {}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        masses = Ph.make_masses(atoms, sub, default="light")
        p = Ph.phonopy_with_masses(ph, masses)
        p.run_qpoints(qpts)
        nu = np.array(p.qpoints.frequencies)  # (nq, 3n) THz
        keep = nu > Ph.GAMMA_TOL_THZ
        out[f"n_dropped_{iso}"] = int((~keep).sum())
        out[f"n_imag_{iso}"] = int((nu < Ph.IMAG_TOL_THZ).sum())
        out[f"min_freq_THz_{iso}"] = float(nu.min())
        tot_m[iso] = float(masses.sum()) * len(qpts)
        F[iso] = float(_osc_free_energy(nu[keep], T).sum()) + com_free_energy(tot_m[iso], T)
        if P is not None:
            Fp[iso] = float(_osc_free_energy(nu[keep], T, P).sum()) + com_free_energy(tot_m[iso], T)
    out["dF_eV"] = F["D"] - F["H"]
    out["dF_com_eV"] = com_free_energy(tot_m["D"], T) - com_free_energy(tot_m["H"], T)
    if P is not None:
        out["dF_P_eV"] = Fp["D"] - Fp["H"]
    out["has_imaginary"] = out["n_imag_H"] > 0 or out["n_imag_D"] > 0
    return out


# ---------------------------------------------------------------- cache matching

def find_cache(struct_id, raw_root=RAW, cache_root=CACHE):
    """The one cache dir whose meta matches the raw screen fc_meta: energy within 1e-6 eV, equal natoms_cell,
    equal supercell. Zero or several matches raise."""
    raw = json.loads((Path(raw_root) / f"{struct_id}.json").read_text())
    fm = raw["fc_meta"]
    hits = []
    for d in sorted(Path(cache_root).glob(f"*__{CALC_ID}__*")):
        m = d / "meta.json"
        if not m.exists():
            continue
        meta = json.loads(m.read_text())
        if (abs(meta.get("energy_eV", np.inf) - fm["energy_eV"]) < 1e-6 and meta.get("natoms_cell") == fm["natoms_cell"]
                and list(meta.get("supercell", [])) == list(fm["supercell"])):
            hits.append(d)
    if len(hits) != 1:
        raise LookupError(f"{struct_id}: {len(hits)} cache matches for fc_meta {fm} ({[h.name for h in hits]})")
    return hits[0]


# ---------------------------------------------------------------- driver

def _git_hash():
    try:
        h = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "src/isoshift_event/pimd.py"], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
        return h + ("-dirty" if dirty else "")
    except OSError:
        return "unknown"


def run_points(rp, mask_h, g_nodes, steps, equil_frac, base_masses, on_point=None, done=None, log_every=0,
               weights=None):
    """Run the TI mass points in order. done: list of already completed point dicts (resume)."""
    results = list(done or [])
    n_h = int(mask_h.sum())
    for i, g in enumerate(g_nodes):
        if i < len(results):
            continue
        m = base_masses.copy()
        m[mask_h] = M_H / g ** 2
        rp.set_masses(m)
        n_eq = int(round(equil_frac * steps))
        t0 = time.time()
        ks = np.empty(steps - n_eq)
        for s in range(steps):
            rp.step()
            if s >= n_eq:
                ks[s - n_eq] = rp.kinetic_cv(mask_h) / n_h
            if log_every and (s + 1) % log_every == 0:
                print(f"  g={g:.5f} step {s + 1}/{steps} {(s + 1) / (time.time() - t0):.2f} steps/s", flush=True)
        wall = time.time() - t0
        err, curve = block_error(ks)
        results.append({"g": float(g), "mass_H_u": float(M_H / g ** 2),
                        "weight": None if weights is None else float(weights[i]), "K_H_meV": float(ks.mean() * 1e3),
                        "K_H_err_meV": err * 1e3, "steps": steps, "steps_equil": n_eq, "steps_used": len(ks),
                        "block_curve_meV": [[b, nb, e * 1e3] for b, nb, e in curve],
                        "wall_s": wall, "steps_per_s": steps / wall})
        if on_point:
            on_point(results)
    return results


def _summarize(points, w):
    g = [p["g"] for p in points]
    df, err = ti_integrate(g, w[: len(points)], [p["K_H_meV"] for p in points], [p["K_H_err_meV"] for p in points])
    return df, err


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--struct", required=True)
    ap.add_argument("--beads", type=int, required=True)
    ap.add_argument("--steps", type=int, required=True, help="MD steps per mass point (incl. equilibration)")
    ap.add_argument("--dt", type=float, default=0.25, help="fs")
    ap.add_argument("--T", type=float, default=300.0)
    ap.add_argument("--tau0", type=float, default=100.0, help="centroid Langevin time constant, fs")
    ap.add_argument("--masses-points", type=int, default=4)
    ap.add_argument("--equil", type=float, default=0.2, help="equilibration fraction per mass point")
    ap.add_argument("--seed", type=int, default=12)
    ap.add_argument("--splitting", choices=("baoab", "obabo"), default="baoab")
    ap.add_argument("--backend", choices=("mace", "harmonic"), default="mace")
    ap.add_argument("--bead-chunk", type=int, default=None, help="beads per MACE forward pass (default all P)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, default=RAW)
    ap.add_argument("--cache-root", type=Path, default=CACHE)
    ap.add_argument("--state-root", type=Path, default=STATE)
    ap.add_argument("--log-every", type=int, default=0)
    ap.add_argument("--stop-after", type=int, default=None, help=argparse.SUPPRESS)  # tests: simulate interruption
    a = ap.parse_args(argv)

    from ase import Atoms

    from isoshift import cache

    cdir = find_cache(a.struct, a.raw_root, a.cache_root)
    ph, meta = cache.load_fc(cdir.name, root=cdir.parent)
    uc = ph.unitcell
    cell_atoms = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    sc = [int(x) for x in np.diag(Ph.supercell_for_min_length(cell_atoms, MIN_LENGTH, MAX_ATOMS))]

    if a.backend == "harmonic":
        if sc != [int(x) for x in np.diag(ph.supercell_matrix)]:
            raise ValueError(f"harmonic backend needs the PIMD supercell {sc} to equal the force-constant supercell")
        from phonopy.harmonic.force_constants import compact_fc_to_full_fc

        fc = ph.force_constants
        if fc.shape[0] != fc.shape[1]:
            fc = compact_fc_to_full_fc(ph.primitive, fc)
        s = ph.supercell
        atoms = Atoms(s.symbols, cell=s.cell, scaled_positions=s.scaled_positions, pbc=True)
        forces = HarmonicForces(fc, atoms.positions)
    else:
        atoms = cell_atoms * tuple(sc)
        forces = MaceForces(atoms, device=a.device, bead_chunk=a.bead_chunk)

    mask_h = np.array([s == "H" for s in atoms.get_chemical_symbols()])
    n_h = int(mask_h.sum())
    if n_h == 0:
        raise ValueError(f"{a.struct}: no H atoms")
    base = Ph.make_masses(atoms, {}, default="light")
    g_nodes, w = ti_nodes(a.masses_points)

    harm = harmonic_samecell(ph, sc, a.T, P=a.beads)
    harm_meV = harm["dF_eV"] * 1e3 / n_h

    out_path = a.out if a.out.is_absolute() else ROOT / a.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_args = {k: getattr(a, k) for k in ("beads", "steps", "dt", "T", "tau0", "masses_points", "equil", "seed",
                                           "backend", "bead_chunk", "splitting")}
    done = []
    if out_path.exists():
        prev = json.loads(out_path.read_text())
        if prev.get("run_args") != run_args:
            raise ValueError(f"{out_path} exists with different arguments {prev.get('run_args')}; refusing to mix runs")
        done = prev.get("points", [])
    state = Path(a.state_root) / f"{out_path.stem}.npz"

    rng = np.random.default_rng(a.seed)
    gpu_peak = None
    try:
        import torch

        if a.backend == "mace":
            torch.cuda.reset_peak_memory_stats()
    except ImportError:
        torch = None
    rp = RingPolymer(atoms.positions, base, a.beads, a.T, a.dt, a.tau0, forces, rng, splitting=a.splitting)
    f0_max = float(np.abs(rp.f[0]).max())
    if done:
        st = np.load(state, allow_pickle=False)
        if int(st["n_points"]) != len(done):
            raise ValueError(f"restart state {state} has {int(st['n_points'])} points, JSON has {len(done)}")
        rp.q = st["q"]
        rp.f, rp.v = rp.forces(rp.q)
        rng.bit_generator.state = json.loads(str(st["rng"]))

    def record(points, status):
        nonlocal gpu_peak
        if torch is not None and a.backend == "mace":
            gpu_peak = max(gpu_peak or 0.0, torch.cuda.max_memory_allocated() / 1e9)
        doc = {"struct_id": a.struct, "status": status, "run_args": run_args, "cache_key": cdir.name,
               "fc_supercell": [int(x) for x in np.diag(ph.supercell_matrix)], "supercell": sc,
               "natoms": len(atoms), "n_H": n_h, "P": a.beads, "dt_fs": a.dt, "T_K": a.T, "tau0_fs": a.tau0,
               "splitting": a.splitting, "seed": a.seed, "model": forces.info(), "git": _git_hash(), "initial_max_abs_F_eV_A": f0_max,
               "gpu_peak_GB": gpu_peak, "points": points,
               "harmonic_samecell": {k: v for k, v in harm.items()},
               "dF_harm_samecell_meV_H": harm_meV, "dF_harm_samecell_P_meV_H": harm["dF_P_eV"] * 1e3 / n_h,
               "zero_modes": "Gamma acoustic modes dropped in the harmonic reference; -(3/2) kT ln M_tot added "
                             "(free translation, present in PIMD)"}
        if len(points) == a.masses_points:
            df, err = _summarize(points, w)
            doc.update({"dF_PIMD_meV_H": df, "dF_PIMD_err_meV_H": err, "delta_anh_meV_H": df - harm_meV,
                        "delta_anh_err_meV_H": err})
        tmp = out_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, indent=1))
        tmp.replace(out_path)

    def on_point(points):
        state.parent.mkdir(parents=True, exist_ok=True)
        np.savez(state, q=rp.q, n_points=len(points), rng=json.dumps(rp.rng.bit_generator.state))
        record(points, "complete" if len(points) == a.masses_points else "partial")
        print(f"{a.struct} point {len(points)}/{a.masses_points}: g={points[-1]['g']:.5f} "
              f"<K_H>={points[-1]['K_H_meV']:.2f}+-{points[-1]['K_H_err_meV']:.2f} meV/H, "
              f"{points[-1]['steps_per_s']:.3f} steps/s", flush=True)

    todo = g_nodes if a.stop_after is None else g_nodes[: len(done) + a.stop_after]
    pts = run_points(rp, mask_h, todo, a.steps, a.equil, base, on_point=on_point, done=done, log_every=a.log_every,
                     weights=w)
    if len(pts) == len(done):
        record(pts, "complete" if len(pts) == a.masses_points else "partial")
    return json.loads(out_path.read_text())


if __name__ == "__main__":
    main()
