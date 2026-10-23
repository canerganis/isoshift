"""P12 path-integral check: full H to D substitution free energy from PIMD (docs/predictions/P12_pimd.md).

Per structure: ring-polymer MD (normal-mode propagation, PILE-L thermostat) on the fixed relaxed cell of
the screen with MACE medium-mpa-0 (float32 by default, decision 17), and mass thermodynamic integration over the H mass,
    F(m_D) - F(m_H) = int_1^{g_D} 2 <K_H(g)>/g dg,  g = sqrt(m_H/m),  Gauss-Legendre in g,
with K_H the centroid-virial kinetic energy of the H atoms. The same-cell harmonic reference uses the cached
MACE force constants on the q-points commensurate with the PIMD supercell, and
    delta_anh = [F_D - F_H]_PIMD,P - [F_D - F_H]_harm,same cell,P    (meV per H).
Pair assembly (ddF_corr) is not done here.

These are fixed-volume Helmholtz differences, not Gibbs differences. At fixed pressure define
ln beta_p^G = -[(G_D^p - G_H^p) - Delta_classical] / (n_H kT), with
G_X(T,p) = min_V [E_BO(V) + F_vib,X(V,T) + p V] separately for each isotope X.
The common classical term cancels between phases: n_H kT ln(beta_a^G/beta_b^G) = ddG.
Replacing G with F in beta defines a separate fixed-volume identity for ddF.
This NVT driver performs no isotope-dependent volume minimisation or pressure-boundary conversion.

Zero modes: the PIMD centroid includes the free translation of the whole supercell, which contributes the
mass-dependent term F_COM = -(3/2) kT ln M_tot (the free-particle path integral equals its classical value).
The harmonic reference removes exactly the three Gamma translations, identified by their projection on the
mass-weighted translation vectors and verified below GAMMA_TOL_THZ (classify_modes), keeps every other positive
mode, folds non-translation imaginary modes to |nu| (A9), and adds this F_COM term back explicitly.
The dropped reference and infinite-P subtraction remain diagnostics; non-translation zeros invalidate.

Checks that this module cannot settle inside one run are reported, not assumed (JSON "unverified"): the time
step and the bead number (compare_runs between two runs, bead_transfer_ok for structures other than the
pilot), the cell-size dependence of delta_anh, the Fourier interpolation of the cached force constants when the
PIMD q-points are not commensurate with the force-constant supercell (hessian check on the PIMD cell), and the
statistical error when the block curve has no plateau (stat_error). delta_anh_meV_H is null when the harmonic
reference is invalid or its interpolation is unverified.

Units: A, eV, u, fs, K. Internal mass unit is eV fs^2 / A^2 (1 u = AMU_EV).

    python -m src.isoshift_event.pimd --struct mp-23940 --beads 32 --steps 20000 --out results/pimd/mp-23940_P32.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from contextlib import contextmanager
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

@contextmanager
def force_precision():
    """Disable reduced precision even inside caller autocast; read back within the force context."""
    try:
        import torch
    except ImportError:
        yield {"torch_available": False, "tf32_matmul": None, "tf32_cudnn": None,
               "autocast_cpu": None, "autocast_cuda": None}
        return
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    with torch.autocast("cpu", enabled=False), torch.autocast("cuda", enabled=False):
        yield {"torch_available": True, "tf32_matmul": bool(torch.backends.cuda.matmul.allow_tf32),
               "tf32_cudnn": bool(torch.backends.cudnn.allow_tf32),
               "autocast_cpu": bool(torch.is_autocast_enabled("cpu")),
               "autocast_cuda": bool(torch.is_autocast_enabled("cuda"))}


class HarmonicForces:
    """V = 1/2 u.Phi.u, u = q - x0, on unwrapped coordinates. fc: (N, N, 3, 3) eV/A^2."""

    name = "harmonic"

    def __init__(self, fc, x0):
        fc = np.asarray(fc, dtype=float)
        n = fc.shape[0]
        self.phi = fc.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
        self.x0 = np.asarray(x0, dtype=float)
        self.sampling_stability = None
        with force_precision() as precision:
            self.precision = precision

    def validate_stability(self, masses_u):
        """Reject an inverted harmonic PES before propagation, independently of the A9 reference fold.

        No mode is exempt: a negative eigenvalue on a verified translation (broken acoustic sum rule within
        GAMMA_TOL_THZ) is still an inverted, unbounded direction of the sampled potential, so the reference
        tolerance on translations does not apply here. The eigenvalue tolerance covers float64 eigensolver
        roundoff (N_dof * eps * spectral scale), not soft physical imaginary modes or small ASR violations.
        The sign of the quadratic form is invariant under the positive TI mass changes.
        """
        if self.sampling_stability is not None:
            return self.sampling_stability
        sm = np.sqrt(np.repeat(masses_u, 3) * AMU_EV)
        dm = (self.phi + self.phi.T) / (2 * np.outer(sm, sm))
        ev, vec = np.linalg.eigh(dm)
        nu = np.sign(ev) * np.sqrt(np.abs(ev)) / (2 * np.pi * 1e-3)
        _, trans, info = classify_modes(nu[None], vec, masses_u)
        roundoff = len(ev) * np.finfo(np.float64).eps * np.max(np.abs(ev))
        negative = ev < -roundoff
        neg_trans = negative & trans[0]
        neg_other = negative & ~trans[0]
        if negative.any():
            raise ValueError(f"unstable harmonic potential: {int(neg_other.sum())} negative non-translation and "
                             f"{int(neg_trans.sum())} negative translation eigenvalues (minimum frequency "
                             f"{nu[negative].min():.6g} THz); folding the reference to |nu| does not stabilise the "
                             "sampled potential, and a negative translation is an inverted direction even within "
                             "the acoustic sum rule tolerance")
        self.sampling_stability = {"stable": True, "n_negative_nontranslation": 0, "n_negative_translation": 0,
                                   "eigenvalue_roundoff_tol_fs2": float(roundoff),
                                   "translations_exempted": False,
                                   "translations_verified": bool(info["translations_verified"]),
                                   "reference_folding_applied_to_forces": False}
        return self.sampling_stability

    def __call__(self, q):
        torch = sys.modules.get("torch")
        if torch is not None:
            # NumPy has no autocast path, but an enclosing torch context must also be disabled here.
            if (torch.is_autocast_enabled("cpu") or torch.is_autocast_enabled("cuda")
                    or torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32):
                with force_precision() as precision:
                    self.precision = precision
                    return self._evaluate(q)
        return self._evaluate(q)

    def _evaluate(self, q):
        q = np.asarray(q, dtype=np.float64)
        u = (q - self.x0).reshape(len(q), -1)
        g = u @ self.phi.T
        return -g.reshape(q.shape), 0.5 * np.einsum("pi,pi->p", u, g)

    def info(self):
        return {"backend": "harmonic", "dtype": "float64", "precision_scope": "numpy float64; torch state at setup",
                "sampling_stability": self.sampling_stability, **self.precision}


class MaceForces:
    """MACE medium-mpa-0, conservative forces, model dtype float32 (decision 17 A1: the cached force constants and
    the screen relaxations are float32) or float64. Positions, momenta and estimators stay float64 in the ring
    polymer; forces are returned as float64. All beads go through one batched forward pass, or through explicit
    chunks of bead_chunk beads (recorded in the output; never chosen silently)."""

    name = "mace"

    def __init__(self, atoms, device="cuda", bead_chunk=None, model="medium-mpa-0", dtype="float32"):
        import torch
        from mace import data as mace_data
        from mace.calculators import mace_mp

        if device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("CUDA not available; P12 production runs on the GPU")
        if dtype not in ("float32", "float64"):
            raise ValueError(dtype)
        self.dtype = dtype
        self.calc = mace_mp(model=model, device=device, default_dtype=dtype, dispersion=False)
        self.model = self.calc.models[0]
        dt = next(self.model.parameters()).dtype
        if dt != getattr(torch, dtype):
            raise RuntimeError(f"MACE model dtype is {dt}, requested {dtype}")
        self.keyspec = mace_data.KeySpecification(info_keys=self.calc.info_keys, arrays_keys=self.calc.arrays_keys)
        self.atoms = atoms.copy()
        self.device = device
        self.bead_chunk = bead_chunk
        self.model_name = model
        with force_precision() as precision:
            self.precision = precision

    def _batch(self, qs):
        from mace import data as mace_data
        from mace.tools import torch_geometric, torch_tools

        graphs = []
        with torch_tools.default_dtype(self.dtype):
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
        f, e = np.empty(q.shape, dtype=np.float64), np.empty(P, dtype=np.float64)
        for s in range(0, P, chunk):
            t = min(P, s + chunk)
            try:
                with force_precision() as precision:
                    self.precision = precision
                    out = self.model(self._batch(q[s:t]).to_dict(), compute_stress=False, training=False)
            except (torch.OutOfMemoryError, RuntimeError) as err:  # TorchScript raises a plain RuntimeError
                if "out of memory" not in str(err):
                    raise
                raise RuntimeError(f"GPU out of memory for a batch of {t - s} beads x {n} atoms in {self.dtype}; "
                                   f"rerun with an explicit smaller --bead-chunk") from err
            f[s:t] = out["forces"].detach().cpu().double().numpy().reshape(t - s, n, 3)
            e[s:t] = out["energy"].detach().cpu().double().numpy()
        return f, e

    def info(self):
        import importlib.metadata as md

        import torch

        return {"backend": "mace", "model": self.model_name, "dtype": self.dtype, "device": self.device,
                "mace_torch": md.version("mace-torch"), "torch": torch.__version__, "bead_chunk": self.bead_chunk,
                "precision_scope": "inside force call", **self.precision}


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

    def __init__(self, x0, masses_u, P, T, dt, tau0, forces, rng, splitting="baoab"):
        if splitting not in ("obabo", "baoab"):
            raise ValueError(splitting)
        self.splitting = splitting
        self.P, self.T, self.dt, self.tau0 = int(P), float(T), float(dt), float(tau0)
        self.forces, self.rng = forces, rng
        self.C = nm_matrix(self.P)
        self.wk = nm_freqs(self.P, self.T)
        self.x0 = np.asarray(x0, dtype=np.float64).copy()
        self.q = np.repeat(self.x0[None], self.P, axis=0)
        self.set_masses(masses_u)
        self.f, self.v = self.forces(self.q)

    def initialize_harmonic(self, phi):
        """Exact P-bead draw at light masses, including the classical centroid.

        Physical mode l, ring mode k: variance P kT / (omega_l^2 + omega_k^2).
        All k amplitudes of translations and nonpositive physical modes are zero.
        """
        sm = np.sqrt(np.repeat(self.m, 3))
        ev, vec = np.linalg.eigh(np.asarray(phi, dtype=np.float64) / np.outer(sm, sm))
        nu = np.sign(ev) * np.sqrt(np.abs(ev)) / (2 * np.pi * 1e-3)
        keep, _, _ = classify_modes(nu[None], vec, self.m / AMU_EV)
        good = keep[0]
        amp = np.zeros((self.P, len(ev)), dtype=np.float64)
        amp[:, good] = (self.rng.standard_normal((self.P, int(good.sum())))
                       * np.sqrt(self.P * KB_EV * self.T / (ev[good] + self.wk[:, None] ** 2)))
        self.q = self.x0 + (self.C @ (amp @ vec.T / sm)).reshape(self.q.shape)
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
        if isinstance(self.forces, HarmonicForces):
            self.forces.validate_stability(self.m / AMU_EV)
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


def step_spectral_radius(P, T, dt, nu_phys_thz, tau0=100.0, splitting="baoab"):
    """Largest spectral radius over normal modes k of the mean (noise-free) one-step propagator of RingPolymer
    for a harmonic physical force of frequency nu_phys_thz (THz) on every bead. The physical Hessian is bead
    diagonal, so each normal mode is an independent 2x2 linear map on (q, p/m). A value above 1 means the
    exact free ring-polymer step resonates with the force step (Korol, Bou-Rabee, Miller, J. Chem. Phys. 151,
    124103 (2019); Korol et al., J. Chem. Phys. 152, 104102 (2020)) and the run has no stationary state.
    Returns (rho_max, k_max)."""
    wk = nm_freqs(P, T)
    gam = 2 * wk
    gam[0] = 1.0 / tau0
    to, ta = (0.5 * dt, dt) if splitting == "obabo" else (dt, 0.5 * dt)
    w2 = (2 * np.pi * 1e-3 * nu_phys_thz) ** 2
    B = np.array([[1.0, 0.0], [-0.5 * dt * w2, 1.0]])
    best = (0.0, 0)
    for k in range(P):
        w = wk[k]
        A = (np.array([[1.0, ta], [0.0, 1.0]]) if k == 0 else
             np.array([[np.cos(w * ta), np.sin(w * ta) / w], [-w * np.sin(w * ta), np.cos(w * ta)]]))
        O = np.diag([1.0, np.exp(-to * gam[k])])
        Mk = B @ A @ O @ A @ B if splitting == "baoab" else O @ B @ A @ B @ O
        r = float(np.abs(np.linalg.eigvals(Mk)).max())
        if r > best[0]:
            best = (r, k)
    return best


def check_step_stable(P, T, dt, nu_max_thz, tau0=100.0, splitting="baoab", margin=1.05, tol=1e-12):
    """Stability of P, T, dt for physical frequencies up to margin * nu_max_thz (scanned on a grid, since a
    resonance can sit between frequencies). Raises ValueError on an unstable combination; returns the scan."""
    grid = np.linspace(1.0, margin * nu_max_thz, 400)
    rho = [step_spectral_radius(P, T, dt, nu, tau0, splitting) for nu in grid]
    i = int(np.argmax([r[0] for r in rho]))
    out = {"nu_max_thz": float(nu_max_thz), "margin": margin, "rho_max": rho[i][0], "k": rho[i][1],
           "nu_at_rho_max_thz": float(grid[i]), "stable": bool(rho[i][0] <= 1 + tol)}
    if not out["stable"]:
        raise ValueError(f"unstable ring-polymer step: P={P}, T={T}, dt={dt} fs, {splitting}: spectral radius "
                         f"{rho[i][0]:.9f} at k={rho[i][1]}, nu={grid[i]:.1f} THz; lower dt or P")
    return out


# ---------------------------------------------------------------- statistics and quadrature

def block_error(x, min_blocks=16):
    """Standard error of the mean from blocks of size 1, 2, 4, ... while at least min_blocks blocks remain.
    Returns (err, curve) with err the maximum over the curve and curve [(size, n_blocks, err)]. This alone is
    not a converged error: see stat_error for the plateau and autocorrelation checks."""
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


def block_plateau(curve, n_levels=3, z=2.0):
    """Index of the first level of a plateau in a block curve, or None.

    The standard error of a block estimate e_l from n_l blocks is s_l = e_l / sqrt(2 (n_l - 1)) (Flyvbjerg and
    Petersen, J. Chem. Phys. 91, 461 (1989)). Level L starts a plateau if every larger block size l > L agrees
    with it, |e_l - e_L| <= z s_l, and at least n_levels levels (L included) remain. A curve that is still
    rising fails this, because the precise small-block levels drift by more than z s_l."""
    e = np.array([c[2] for c in curve])
    de = e / np.sqrt(2 * (np.array([c[1] for c in curve]) - 1))
    for s in range(len(curve) - n_levels + 1):
        if np.all(np.abs(e[s + 1:] - e[s]) <= z * de[s + 1:]):
            return s
    return None


def autocorr_time(x, c=5.0):
    """Integrated autocorrelation time tau (samples; statistical inefficiency is 2 tau) with Sokal's automatic
    window: the smallest M with M >= c tau(M). Returns (tau, M, window_found)."""
    x = np.asarray(x, dtype=float) - np.mean(x)
    n = len(x)
    if n < 4 or not np.any(x):
        return 0.5, 0, n >= 4
    f = np.fft.rfft(x, 2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:n]
    rho = acf / acf[0]
    tau = 0.5 + np.cumsum(rho[1:])
    for M in range(1, n - 1):
        if M >= c * tau[M - 1]:
            return float(max(tau[M - 1], 0.5)), M, True
    return float(max(tau[-1], 0.5)), n - 1, False


def stat_error(x, min_blocks=16, min_independent=50):
    """Error of the mean of a correlated series with two independent estimators.

    Block averaging must reach a plateau (block_plateau) with at least min_blocks blocks per level, and the
    Sokal autocorrelation estimate needs a window and at least min_independent effective samples
    n / (2 tau). converged is True only if both hold. err is the larger of the plateau value (maximum over the
    plateau levels with at least 2 min_blocks blocks) and the autocorrelation value; without a plateau it is
    the largest block value, and converged is False, so a short run is never reported as a resolved error."""
    x = np.asarray(x, dtype=float)
    _, curve = block_error(x, min_blocks)
    tau, M, window = autocorr_time(x)
    n_eff = len(x) / (2 * tau)
    err_acf = float(np.std(x, ddof=1) * np.sqrt(2 * tau / len(x))) if len(x) > 1 else float("nan")
    s = block_plateau(curve)
    if s is None:
        err_block = max((c[2] for c in curve), default=float("nan"))
    else:  # largest plateau value among levels with at least 2 min_blocks blocks (the tail is the noisiest)
        err_block = max([c[2] for c in curve[s:] if c[1] >= 2 * min_blocks] or [curve[s][2]])
    converged = bool(s is not None and window and n_eff >= min_independent)
    return {"err": float(max(err_block, err_acf)), "converged": converged, "err_block": float(err_block),
            "plateau_block_size": None if s is None else int(curve[s][0]),
            "plateau_n_blocks": None if s is None else int(curve[s][1]), "err_acf": err_acf,
            "tau_int_steps": tau, "acf_window": int(M), "acf_window_found": bool(window), "n_eff": float(n_eff),
            "curve": curve}


def ti_nodes(n=4, g_lo=G_D):
    """Gauss-Legendre nodes and weights on [g_lo, 1], nodes in descending g (H side first)."""
    x, w = np.polynomial.legendre.leggauss(n)
    g = 0.5 * (1 + g_lo) + 0.5 * (1 - g_lo) * x
    w = 0.5 * (1 - g_lo) * w
    o = np.argsort(-g)
    return g[o], w[o]


def stationarity(samples):
    """A6(ii): independent half-mean difference error sqrt(SE(first)^2 + SE(second)^2)."""
    x = np.asarray(samples, dtype=np.float64)
    a, b = x[:len(x) // 2], x[len(x) // 2:]
    if min(len(a), len(b)) < 2:
        return {"ok": False, "difference_meV_H": None, "sigma_half_meV_H": None,
                "definition": "sqrt(stat_error(first).err^2 + stat_error(second).err^2); threshold 3 sigma"}
    sa, sb = stat_error(a), stat_error(b)
    sigma = float(np.hypot(sa["err"], sb["err"]))
    diff = float(a.mean() - b.mean())
    return {"ok": bool(np.isfinite(sigma) and abs(diff) <= 3 * sigma),
            "difference_meV_H": diff * 1e3, "sigma_half_meV_H": sigma * 1e3,
            "halves_error_converged": bool(sa["converged"] and sb["converged"]),
            "definition": "sqrt(stat_error(first).err^2 + stat_error(second).err^2); threshold 3 sigma"}


class StructuralMonitor:
    """Compact sufficient statistics, sampled on kept steps only.

    Unwrapped displacement is aligned by subtracting the all-atom arithmetic translation (no rotation).
    Imaginary modes use Euclidean unit Cartesian vectors in that same gauge, so projections are in A.
    Fixed donor/acceptor O identities come from x0; an acceptor must have donor-O distance <= 3.5 A.
    Distances use the minimum image, with ASE's general algorithm for skew cells.
    A14 drift and coordination use the time-averaged aligned centroid. Instantaneous RMSD and donor
    flips are diagnostics: thermal motion and transient proton delocalisation alone do not fail a gate.
    """

    def __init__(self, x0, cell, numbers, imaginary_modes=None, state=None):
        self.x0, self.cell = np.asarray(x0, float), np.asarray(cell, float)
        self.invcell = np.linalg.inv(self.cell)
        self.orthogonal = np.allclose(self.cell @ self.cell.T, np.diag(np.diag(self.cell @ self.cell.T)))
        self.h = np.flatnonzero(np.asarray(numbers) == 1)
        self.o = np.flatnonzero(np.asarray(numbers) == 8)
        self.heavy = np.asarray(numbers) != 1
        self.modes = (np.empty((0, len(x0), 3)) if imaginary_modes is None else np.asarray(imaginary_modes))
        self.bins = np.linspace(-4., 4., 33)
        self.donors, self.acceptors = [], []
        for h in self.h:
            if not len(self.o):
                self.donors.append(-1)
                self.acceptors.append(-1)
                continue
            order = np.argsort(self.dist(self.x0[self.o] - self.x0[h]))
            donor = self.o[order[0]]
            others = [o for o in self.o[order[1:]] if self.dist(self.x0[o] - self.x0[donor]) <= 3.5]
            self.donors.append(int(donor))
            self.acceptors.append(int(others[0]) if others else -1)
        if state is not None and "centroid_displacement_sum_A" not in state:
            raise ValueError("missing centroid displacement accumulator; restart with a new output/state path")
        self.data = state if state is not None else {"samples": 0, "rmsd_sum": 0., "rmsd_max": 0.,
                              "centroid_displacement_sum_A": np.zeros_like(self.x0).tolist(),
                              "coord_changes": [0] * len(self.h), "projection_sum": [0.] * len(self.modes),
                              "projection_abs_sum": [0.] * len(self.modes),
                              "hist": np.zeros((len(self.h), 32), dtype=int).tolist(),
                              "undefined": [0] * len(self.h), "outside": [0] * len(self.h)}

    def dist(self, vectors):
        v = np.asarray(vectors)
        if self.orthogonal:
            f = v @ self.invcell
            return np.linalg.norm((f - np.rint(f)) @ self.cell, axis=-1)
        from ase.geometry import find_mic
        return find_mic(v.reshape(-1, 3), self.cell, pbc=True)[1].reshape(v.shape[:-1])

    def update(self, q):
        centroid = q.mean(axis=0)
        u = centroid - self.x0
        u -= u.mean(axis=0)
        rmsd = float(np.sqrt(np.mean(np.sum(u[self.heavy] ** 2, axis=1)))) if self.heavy.any() else 0.
        d = self.data
        d["samples"] += 1
        d["rmsd_sum"] += rmsd
        d["rmsd_max"] = max(d["rmsd_max"], rmsd)
        d["centroid_displacement_sum_A"] = (np.asarray(d["centroid_displacement_sum_A"]) + u).tolist()
        projection = np.einsum("ina,na->i", self.modes, u)
        d["projection_sum"] = (np.asarray(d["projection_sum"]) + projection).tolist()
        d["projection_abs_sum"] = (np.asarray(d["projection_abs_sum"]) + np.abs(projection)).tolist()
        if len(self.o):
            nearest = self.o[np.argmin(self.dist(centroid[self.h, None] - centroid[self.o]), axis=1)]
            d["coord_changes"] = (np.asarray(d["coord_changes"]) + (nearest != self.donors)).tolist()
        for j, (h, donor, acceptor) in enumerate(zip(self.h, self.donors, self.acceptors)):
            if acceptor < 0:
                d["undefined"][j] += len(q)
                continue
            delta = self.dist(q[:, h] - q[:, donor]) - self.dist(q[:, h] - q[:, acceptor])
            hist = np.histogram(delta, self.bins)[0]
            d["hist"][j] = (np.asarray(d["hist"][j]) + hist).tolist()
            d["outside"][j] += int(len(q) - hist.sum())

    def summary(self):
        d, n = self.data, self.data["samples"]
        proj = (np.asarray(d["projection_sum"]) / max(n, 1)).tolist()
        mean_u = np.asarray(d["centroid_displacement_sum_A"]) / max(n, 1)
        rmsd = float(np.sqrt(np.mean(np.sum(mean_u[self.heavy] ** 2, axis=1)))) if self.heavy.any() else 0.
        mean_centroid = self.x0 + mean_u
        nearest = (self.o[np.argmin(self.dist(mean_centroid[self.h, None] - mean_centroid[self.o]), axis=1)].tolist()
                   if len(self.o) else [-1] * len(self.h))
        coord_ok = bool(n and nearest == self.donors)
        return {"samples": n, "alignment": "subtract all-atom mean unwrapped displacement; no rotation",
                "centroid_displacement_sum_A": d["centroid_displacement_sum_A"],
                "heavy_rmsd_mean_A": d["rmsd_sum"] / max(n, 1), "heavy_rmsd_max_A": d["rmsd_max"],
                "heavy_rmsd_time_mean_A": rmsd, "heavy_rmsd_ok": bool(n and rmsd < .15),
                "heavy_rmsd_gate_definition": "RMSD of time-averaged aligned centroid from x0 < 0.15 A; "
                                              "instantaneous mean/max are diagnostics (A14 drift interpretation)",
                "coordination_defined": bool(len(self.o)), "coordination_unchanged": coord_ok,
                "donor_O_indices": self.donors, "coordination_changes_per_H": d["coord_changes"],
                "mean_centroid_donor_O_indices": nearest,
                "coordination_gate_definition": "nearest O of time-averaged aligned centroid, minimum image, "
                                                "compared with x0; per-sample flips are diagnostics",
                "imaginary_projection_mean_A": proj,
                "imaginary_projection_mean_abs_A": (np.asarray(d["projection_abs_sum"]) / max(n, 1)).tolist(),
                "projection_convention": "dot of aligned centroid-x0 with unit Cartesian real light-mass mode",
                "imaginary_retention_ok": bool(np.all(np.abs(proj) < .1)),
                "retention_ok": bool(n and coord_ok and np.all(np.abs(proj) < .1)),
                "transfer_histogram": {"bins_A": self.bins.tolist(), "counts": d["hist"],
                                       "H_indices": self.h.tolist(), "acceptor_O_indices": self.acceptors,
                                       "acceptor_max_OO_A": 3.5, "assignment": "fixed x0 nearest donor and next O within cutoff",
                                       "undefined_per_H": d["undefined"], "outside_bins_per_H": d["outside"]}}


def merge_monitors(points, monitor_factory):
    """Pool aligned vectors by kept sample count, and require both pooled and per-point gates.

    Opposite drifts at different GL points must not hide a point's sampling failure.
    Geometry comes from the factory, avoiding its duplication in each point's JSON.
    """
    rows = [p["monitors"] for p in points if p.get("monitors")]
    if not rows:
        return None
    mon = monitor_factory(None)
    d = mon.data
    d["samples"] = sum(r["samples"] for r in rows)
    for dest, source in (("rmsd_sum", "heavy_rmsd_mean_A"), ("projection_sum", "imaginary_projection_mean_A"),
                         ("projection_abs_sum", "imaginary_projection_mean_abs_A")):
        d[dest] = sum(np.asarray(r[source]) * r["samples"] for r in rows).tolist()
    d["rmsd_max"] = max(r["heavy_rmsd_max_A"] for r in rows)
    for dest, source in (("centroid_displacement_sum_A", "centroid_displacement_sum_A"),
                         ("coord_changes", "coordination_changes_per_H")):
        d[dest] = np.sum([r[source] for r in rows], axis=0).tolist()
    for dest, source in (("hist", "counts"), ("undefined", "undefined_per_H"), ("outside", "outside_bins_per_H")):
        d[dest] = np.sum([r["transfer_histogram"][source] for r in rows], axis=0).tolist()
    out = mon.summary()
    out["heavy_rmsd_pooled_ok"] = out["heavy_rmsd_ok"]
    out["coordination_pooled_unchanged"] = out["coordination_unchanged"]
    out["imaginary_retention_pooled_ok"] = out["imaginary_retention_ok"]
    for key in ("heavy_rmsd_ok", "coordination_unchanged", "imaginary_retention_ok", "retention_ok"):
        out[key] = out[key] and all(r[key] for r in rows)
    out["gate_scope"] = "every completed GL point and pooled kept samples must pass"
    return out


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
        # kT ln(2 sinh(E/2kT)) = E/2 + kT ln(1 - exp(-E/kT)); the direct sinh overflows for E/kT > ~1420.
        E = HBAR_EV_FS * w
        return E / 2 + kT * np.log(-np.expm1(-E / kT))
    wk = nm_freqs(P, T)
    return kT * np.sum(np.log(HBAR_EV_FS * np.sqrt(w[..., None] ** 2 + wk ** 2) / (P * kT)), axis=-1)


def com_free_energy(total_mass_u, T):
    """Mass-dependent part of the free translation of the whole cell, -(3/2) kT ln M (eV)."""
    return -1.5 * KB_EV * T * np.log(total_mass_u)


def commensurate_qpoints(sc):
    n = [int(x) for x in sc]
    return np.array([[i / n[0], j / n[1], k / n[2]] for i in range(n[0]) for j in range(n[1]) for k in range(n[2])])


def qpoints_commensurate_with(qpts, supercell_matrix, tol=1e-8):
    """True if every q (reduced, unit-cell reciprocal basis) is a commensurate point of the supercell, i.e.
    S^T q is integer. At such points the dynamical matrix built from that supercell's force constants is the
    supercell's own Hessian (no Fourier interpolation)."""
    x = np.asarray(qpts, dtype=float) @ np.asarray(supercell_matrix, dtype=float)
    return bool(np.all(np.abs(x - np.round(x)) < tol))


def classify_modes(nu, evec_gamma, masses_u, i_gamma=0, tol=Ph.GAMMA_TOL_THZ, min_overlap=0.99):
    """Pick the three translations at Gamma by their eigenvectors, not by the smallest |nu|.

    nu: (nq, nb) THz (phonopy sign convention, negative = imaginary); evec_gamma: (nb, nb) eigenvectors of the
    mass-weighted dynamical matrix at q index i_gamma, columns = modes. The mass-weighted translations
    t_a = sqrt(m_i) e_a (normalised) span the exact zero-mode subspace of a translation-invariant potential. The
    three modes with the largest projection on that subspace are the translations; they are verified only if
    each projection exceeds min_overlap and each |nu| is below tol (acoustic sum rule satisfied to tol). A soft
    optical mode below a shifted translation is therefore kept, not dropped. Every other mode with nu > 0
    enters the dropped free energy however small. Imaginary modes are classified separately for A9 folding.
    Returns (keep mask (nq, nb), translation mask, info)."""
    nu = np.atleast_2d(np.asarray(nu, dtype=float))
    nb = nu.shape[1]
    m = np.asarray(masses_u, dtype=float)
    t = np.zeros((nb, 3))
    for a in range(3):
        t[a::3, a] = np.sqrt(m)
    t /= np.linalg.norm(t, axis=0)
    ov = np.sum(np.abs(t.T @ np.asarray(evec_gamma)) ** 2, axis=0)
    idx = np.argsort(-ov)[:3]
    trans = np.zeros(nu.shape, dtype=bool)
    trans[i_gamma, idx] = True
    rest = ~trans
    keep = rest & (nu > 0)
    nonpos = rest & (nu <= 0)
    info = {"translation_overlap_min": float(ov[idx].min()),
            "translation_overlap_4th": float(np.sort(ov)[-4]) if nb > 3 else 0.0,
            "translation_max_abs_THz": float(np.abs(nu[i_gamma, idx]).max()),
            "n_nonpositive_nontranslation": int(nonpos.sum()),
            "n_imag": int((rest & (nu < 0)).sum()),
            "n_zero_nontranslation": int((rest & (nu == 0)).sum()),
            "n_soft_kept": int((keep & (nu < tol)).sum()),
            "min_freq_THz_nontranslation": float(nu[rest].min()) if rest.any() else None}
    info["translations_verified"] = bool(info["translation_overlap_min"] > min_overlap
                                         and info["translation_max_abs_THz"] < tol)
    return keep, trans, info


def _isotope_free_energy(nu, keep, total_mass_u, T, P=None):
    """Harmonic F (eV) of the kept modes plus the free translation of the whole cell."""
    return float(_osc_free_energy(nu[keep], T, P).sum()) + com_free_energy(total_mass_u, T)


def _assemble(per_iso, T, P, n_h=1):
    """per_iso: {iso: (nu, keep, info, total_mass_u)} -> dF dict with validity flags."""
    out = {}
    F, Fp, folded, folded_p = {}, {}, {}, {}
    for iso, (nu, keep, info, mtot) in per_iso.items():
        out.update({f"{k}_{iso}": v for k, v in info.items()})
        F[iso] = _isotope_free_energy(nu, keep, mtot, T)
        imag_nu = np.array([m["frequency_THz"] for m in info["imaginary_modes"]])
        folded[iso] = F[iso] + float(_osc_free_energy(np.abs(imag_nu), T).sum())
        if P is not None:
            Fp[iso] = _isotope_free_energy(nu, keep, mtot, T, P)
            folded_p[iso] = Fp[iso] + float(_osc_free_energy(np.abs(imag_nu), T, P).sum())
    out["dF_dropped_eV"] = float(F["D"] - F["H"])
    out["dF_folded_eV"] = float(folded["D"] - folded["H"])
    out["dF_eV"] = out["dF_folded_eV"]
    out["dF_com_eV"] = float(com_free_energy(per_iso["D"][3], T) - com_free_energy(per_iso["H"][3], T))
    if P is not None:
        out["dF_dropped_P_eV"] = float(Fp["D"] - Fp["H"])
        out["dF_folded_P_eV"] = float(folded_p["D"] - folded_p["H"])
        out["dF_P_eV"] = out["dF_folded_P_eV"]
    out["has_imaginary"] = bool(out["n_imag_H"] > 0 or out["n_imag_D"] > 0)
    out["translations_verified"] = bool(out["translations_verified_H"] and out["translations_verified_D"])
    out["valid"] = bool(out["translations_verified"] and out["n_zero_nontranslation_H"] == 0
                        and out["n_zero_nontranslation_D"] == 0)
    out["folded"] = out["has_imaginary"]
    out["n_imag"] = max(out["n_imag_H"], out["n_imag_D"])
    out["s_imag_inf_meV_H"] = abs(out["dF_folded_eV"] - out["dF_dropped_eV"]) * 1e3 / n_h
    out["s_imag_meV_H"] = (abs(out["dF_folded_P_eV"] - out["dF_dropped_P_eV"]) * 1e3 / n_h
                            if P is not None else out["s_imag_inf_meV_H"])
    return out


def _imaginary_modes(nu, trans, vecs, T, qpts=None):
    """Columns of mass-weighted eigenvectors; complex Bloch modes retain both components."""
    modes = []
    for q, b in np.argwhere((nu < 0) & ~trans):
        v = vecs[q, :, b]
        modes.append({"frequency_THz": float(nu[q, b]),
                      "beta_hbar_abs_omega": float(HBAR_EV_FS * 2 * np.pi * abs(nu[q, b]) * 1e-3 / (KB_EV * T)),
                      "q": [0., 0., 0.] if qpts is None else qpts[q].tolist(),
                      "eigenvector_real": v.real.tolist(), "eigenvector_imag": v.imag.tolist()})
    return modes


def _fc_asr_max(fc):
    """max over atoms i of |sum_j Phi_ij| (eV/A^2), compact or full force constants."""
    return float(np.abs(np.asarray(fc).sum(axis=1)).max())


def harmonic_samecell(ph, sc, T, P=None):
    """Same-cell harmonic F_D - F_H for the supercell sc (diagonal ints) from the force constants of ph.

    Zero modes: exactly the three translations at Gamma, identified and verified by classify_modes, are removed
    and replaced by the free translation -(3/2) kT ln M_tot of the whole supercell (M_tot = sum of the masses of
    the PIMD cell), which the PIMD centroid contains. Imaginary or zero non-translation modes make the result
    invalid only for zero modes. A9 folds non-translation imaginary modes to |nu| and also stores the dropped sum.

    qpoints_exact says whether all commensurate q of sc are commensurate with the force-constant supercell; if
    not, the dynamical matrices there are Fourier interpolated and need hessian_samecell to be checked.

    Returns a dict with dF per supercell (eV) and, if P is given, the P-bead discretized value dF_P_eV."""
    from ase import Atoms

    uc = ph.unitcell
    atoms = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    qpts = commensurate_qpoints(sc)
    i_gamma = int(np.flatnonzero(np.all(np.abs(qpts) < 1e-12, axis=1))[0])
    per_iso = {}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        masses = Ph.make_masses(atoms, sub, default="light")
        p = Ph.phonopy_with_masses(ph, masses)
        p.run_qpoints(qpts, with_eigenvectors=True)
        nu = np.array(p.qpoints.frequencies)  # (nq, 3n) THz
        vecs = np.array(p.qpoints.eigenvectors)
        keep, trans, info = classify_modes(nu, vecs[i_gamma], masses, i_gamma=i_gamma)
        info["imaginary_modes"] = _imaginary_modes(nu, trans, vecs, T, qpts)
        per_iso[iso] = (nu, keep, info, float(masses.sum()) * len(qpts))
    out = {"n_qpoints": len(qpts), "source": "cached force constants, commensurate q of the PIMD supercell",
           "qpoints_exact": qpoints_commensurate_with(qpts, ph.supercell_matrix),
           "fc_asr_max_eV_A2": _fc_asr_max(ph.force_constants), "nu_max_thz": float(per_iso["H"][0].max())}
    n_h = int(np.sum(atoms.numbers == 1)) * len(qpts)
    out.update(_assemble(per_iso, T, P, n_h))
    return out


def hessian_samecell(phi, masses_light_u, mask_h, T, P=None):
    """Harmonic F_D - F_H of the PIMD supercell from its own Hessian phi (3N, 3N, eV/A^2): only q = 0 of the
    supercell, i.e. exactly the commensurate set of harmonic_samecell, without any interpolation. Same zero-mode
    treatment as harmonic_samecell."""
    phi = 0.5 * (np.asarray(phi, dtype=float) + np.asarray(phi, dtype=float).T)
    per_iso = {}
    for iso, mh in (("H", M_H), ("D", M_D)):
        m = np.asarray(masses_light_u, dtype=float).copy()
        m[mask_h] = mh
        isq = 1 / np.sqrt(np.repeat(m, 3) * AMU_EV)
        ev, vec = np.linalg.eigh(isq[:, None] * phi * isq[None, :])
        nu = (np.sign(ev) * np.sqrt(np.abs(ev)) / (2 * np.pi * 1e-3))[None]  # signed THz, imaginary < 0
        keep, trans, info = classify_modes(nu, vec, m)
        info["imaginary_modes"] = _imaginary_modes(nu, trans, vec[None], T)
        per_iso[iso] = (nu, keep, info, float(m.sum()))
    out = {"n_qpoints": 1, "source": "finite-difference Hessian of the PIMD supercell"}
    out.update(_assemble(per_iso, T, P, int(np.sum(mask_h))))
    return out


def cached_hessian(ph, sc, atoms):
    """Inverse Bloch transform on the commensurate grid, in the supplied atoms' order.

    Phonopy includes the basis displacement in exp(+2 pi i q.(r_j-r_i)). Undo that phase,
    including the basis, rather than Fourier transforming cell indices alone. Dynamical matrices
    here are in eV/A^2/u; unweighting masses returns force constants without a frequency conversion.
    """
    from ase import Atoms

    uc = ph.unitcell
    base = Atoms(uc.symbols, positions=uc.positions, cell=uc.cell, pbc=True)
    p = Ph.phonopy_with_masses(ph, Ph.make_masses(base, {}, default="light"))
    frac = atoms.positions @ np.linalg.inv(uc.cell)
    basis = np.asarray(p.primitive.scaled_positions)
    mapping = []
    for s, r in zip(atoms.get_chemical_symbols(), frac):
        delta = r - basis
        hits = [j for j in range(len(basis)) if p.primitive.symbols[j] == s
                and np.max(np.abs(delta[j] - np.round(delta[j]))) < 1e-7]
        if len(hits) != 1:
            raise ValueError("cannot uniquely map PIMD atoms to the phonopy basis")
        mapping.append(hits[0])
    dofs = (3 * np.asarray(mapping)[:, None] + np.arange(3)).ravel()
    qpts = commensurate_qpoints(sc)
    mat = np.zeros((3 * len(atoms), 3 * len(atoms)), dtype=complex)
    for q in qpts:
        p.dynamical_matrix.run(q)
        dm = p.dynamical_matrix.dynamical_matrix[np.ix_(dofs, dofs)]
        phase = np.repeat(np.exp(2j * np.pi * (frac @ q)), 3)
        mat += phase[:, None] * dm * phase.conj()[None, :] / len(qpts)
    sm = np.sqrt(np.repeat(Ph.make_masses(atoms, {}, default="light"), 3))
    mat *= np.outer(sm, sm)
    if np.max(np.abs(mat.imag)) > 1e-7:
        raise ValueError("commensurate Bloch transform did not produce a real Hessian")
    return (mat.real + mat.real.T) / 2


def imaginary_cartesian_modes(phi, masses):
    """Real light-mass supercell modes for retention, Euclidean-normalised after translation removal."""
    sm = np.sqrt(np.repeat(masses, 3) * AMU_EV)
    ev, vec = np.linalg.eigh(phi / np.outer(sm, sm))
    nu = np.sign(ev) * np.sqrt(np.abs(ev)) / (2 * np.pi * 1e-3)
    _, trans, _ = classify_modes(nu[None], vec, masses)
    v = (vec[:, (nu < 0) & ~trans[0]].T / sm).reshape(-1, len(masses), 3)
    v -= v.mean(axis=1, keepdims=True)
    if len(v):
        v /= np.linalg.norm(v.reshape(len(v), -1), axis=1)[:, None, None]
    return v


def fd_hessian(forces, x0, delta=0.01, chunk=None):
    """Central finite-difference Hessian (3N, 3N) of a force backend at x0, all 6N displaced configurations in
    batches of chunk (default: all at once; the MACE backend applies its own bead_chunk). Symmetrised."""
    x0 = np.asarray(x0, dtype=float)
    n = len(x0)
    disp = np.repeat(x0[None], 6 * n, axis=0)
    for d in range(3 * n):
        i, a = divmod(d, 3)
        disp[2 * d, i, a] += delta
        disp[2 * d + 1, i, a] -= delta
    chunk = chunk or len(disp)
    f = np.concatenate([forces(disp[s:s + chunk])[0] for s in range(0, len(disp), chunk)])
    f = f.reshape(3 * n, 2, 3 * n)
    phi = -(f[:, 0] - f[:, 1]) / (2 * delta)
    return 0.5 * (phi + phi.T)


# ---------------------------------------------------------------- cache matching

def find_cache(struct_id, raw_root=RAW, cache_root=CACHE):
    """The one cache dir whose meta matches the raw screen fc_meta: energy within 1e-6 eV, volume within 1e-4 A^3
    (as refine._cache_index; relaxations of the same structure can share the energy to float32), equal
    natoms_cell, supercell and n_displacements. Zero or several matches raise."""
    raw = json.loads((Path(raw_root) / f"{struct_id}.json").read_text())
    fm = raw["fc_meta"]
    hits = []
    for d in sorted(Path(cache_root).glob(f"*__{CALC_ID}__*")):
        m = d / "meta.json"
        if not m.exists():
            continue
        meta = json.loads(m.read_text())
        if (abs(meta.get("energy_eV", np.inf) - fm["energy_eV"]) < 1e-6 and meta.get("natoms_cell") == fm["natoms_cell"]
                and list(meta.get("supercell", [])) == list(fm["supercell"])
                and abs(meta.get("volume_A3", np.inf) - fm["volume_A3"]) < 1e-4
                and meta.get("n_displacements") == fm.get("n_displacements")):
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
               weights=None, extension_steps=3000, monitor_factory=None, dump_every=0, dump_root=None,
               dump_stem="pimd", cell=None, atomic_numbers=None, active=None, on_progress=None):
    """TI points with one A6 extension and checkpointable, uncounted active-point samples.

    A checkpoint includes q, p and RNG for an active point; at a point boundary momenta are resampled.
    Snapshots are replaced atomically at completion, never appended to an interrupted file.
    """
    results = list(done or [])
    n_h = int(mask_h.sum())
    for i, g in enumerate(g_nodes):
        if i < len(results):
            continue
        m = base_masses.copy()
        m[mask_h] = M_H / g ** 2
        n_eq = int(round(equil_frac * steps))
        if active is not None:
            if active["point_index"] != i:
                raise ValueError("active checkpoint point does not follow completed points")
            rp.set_masses(m, resample=False)
            progress = active
            active = None
        else:
            rp.set_masses(m)
            progress = {"point_index": i, "step": 0, "target": steps, "extension_steps": 0,
                        "tests": [], "ks": [], "snapshot_q": [], "snapshot_steps": [],
                        "monitor_state": None, "wall_s": 0.}
        mon = monitor_factory(progress["monitor_state"]) if monitor_factory else None
        t0 = time.perf_counter()
        prior_wall = progress["wall_s"]

        def checkpoint():
            progress["wall_s"] = prior_wall + time.perf_counter() - t0
            progress["monitor_state"] = mon.data if mon else None
            if on_progress:
                on_progress(progress)

        try:
            while True:
                while progress["step"] < progress["target"]:
                    _checkpointable_step(rp)
                    progress["step"] += 1
                    s = progress["step"]
                    if s > n_eq:
                        progress["ks"].append(rp.kinetic_cv(mask_h) / n_h)
                        if mon:
                            mon.update(rp.q)
                        kept = len(progress["ks"])
                        if dump_every and kept % dump_every == 0:
                            progress["snapshot_q"].append(rp.q.copy())
                            progress["snapshot_steps"].append(kept)
                    if on_progress and s % 100 == 0:
                        checkpoint()
                    if log_every and s % log_every == 0:
                        print(f"  g={g:.5f} step {s}/{progress['target']}", flush=True)
                # Persist the decision as well as the data so an extension cannot fire twice on resume.
                required_tests = 2 if progress["extension_steps"] else 1
                if len(progress["tests"]) < required_tests:
                    progress["tests"].append(stationarity(progress["ks"]))
                if (not progress["tests"][-1]["ok"] and not progress["extension_steps"] and extension_steps):
                    progress["extension_steps"] = extension_steps
                    progress["target"] += extension_steps
                    checkpoint()
                    continue
                break
        except BaseException:
            checkpoint()
            raise
        wall = prior_wall + time.perf_counter() - t0
        ks = np.asarray(progress["ks"], dtype=np.float64)
        se = stat_error(ks)
        snapshots = {"path": None, "count": 0}
        if dump_every:
            path = Path(dump_root) / f"{dump_stem}_g{i}.npz"
            _atomic_npz(path, schema="isoshift-pimd-snapshots-v1", q=np.asarray(progress["snapshot_q"], dtype=np.float64)
                        .reshape(-1, *rp.q.shape), g=float(g), masses_u=m, mask_h=mask_h, cell_A=cell,
                        atomic_numbers=atomic_numbers, T_K=rp.T,
                        P=rp.P, kB_eV_K=KB_EV, model_info=json.dumps(rp.forces.info()),
                        x0_A=rp.x0, harmonic_phi_eV_A2=getattr(rp.forces, "phi", np.empty((0, 0))),
                        kept_steps=np.asarray(progress["snapshot_steps"], dtype=np.int64),
                        step_indices=np.asarray(progress["snapshot_steps"], dtype=np.int64) + n_eq,
                        coordinates="unwrapped Angstrom; all P beads", force_convention="physical forces eV/Angstrom",
                        kinetic_estimator="K_H=1.5*n_H*kB*T-sum((q-mean_beads(q))*F_H)/(2*P)")
            snapshots = {"path": str(path.resolve()), "count": len(progress["snapshot_steps"])}
        results.append({"g": float(g), "mass_H_u": float(M_H / g ** 2),
                        "weight": None if weights is None else float(weights[i]), "K_H_meV": float(ks.mean() * 1e3),
                        "K_H_err_meV": se["err"] * 1e3, "error_converged": se["converged"],
                        "K_H_err_block_meV": se["err_block"] * 1e3, "K_H_err_acf_meV": se["err_acf"] * 1e3,
                        "plateau_block_size": se["plateau_block_size"], "plateau_n_blocks": se["plateau_n_blocks"],
                        "tau_int_steps": se["tau_int_steps"], "n_eff": se["n_eff"],
                        "steps": progress["step"], "steps_planned": steps, "steps_equil": n_eq, "steps_used": len(ks),
                        "extension_steps": progress["extension_steps"], "stationarity_tests": progress["tests"],
                        "stationarity_ok": progress["tests"][-1]["ok"],
                        "monitors": mon.summary() if mon else None, "snapshots": snapshots,
                        "block_curve_meV": [[b, nb, e * 1e3] for b, nb, e in se["curve"]],
                        "wall_s": wall, "steps_per_s": progress["step"] / wall,
                        "seconds_per_ring_step": wall / progress["step"]})
        if on_point:
            on_point(results)
    return results


def _atomic_npz(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("wb") as f:
        np.savez(f, **arrays)
    tmp.replace(path)


def _checkpointable_step(rp):
    """Do not persist a half BAOAB step if a force call or keyboard interrupt fails mid-step."""
    previous = rp.q.copy(), rp.p.copy(), rp.f, rp.v, rp.rng.bit_generator.state
    try:
        rp.step()
    except BaseException:
        rp.q, rp.p, rp.f, rp.v, rng_state = previous
        rp.rng.bit_generator.state = rng_state
        raise


def _summarize(points, w):
    g = [p["g"] for p in points]
    df, err = ti_integrate(g, w[: len(points)], [p["K_H_meV"] for p in points], [p["K_H_err_meV"] for p in points])
    return df, err


# ---------------------------------------------------------------- systematic checks between runs

COMPARE_TOL_MEV = 0.3  # P12 section 2: P vs 2P, and the per-structure error target
HESSIAN_TOL_MEV = 0.1  # interpolated vs PIMD-cell Hessian, meV per H (a third of the 0.3 meV target)


def compare_runs(a, b, tol=COMPARE_TOL_MEV, z=2.0):
    """Systematic check between two completed run JSONs of one structure that differ in P or dt only.

    diff = Delta_anh(larger P) - Delta_anh(smaller P), or Delta_anh(dt/2) - Delta_anh(dt).
    err = combined statistical error (independent runs). The diagnostic equivalence flag converged needs
    the upper bound |diff| + z err below tol, so an observed difference below tol with a large error does not
    pass. Both runs must have converged statistical errors. For a bead comparison the harmonic bead error
    |dF_harm,P - dF_harm| of each run is reported: transfer_reference_meV_H is that of the larger P, and a
    production structure at the same P whose harmonic bead error exceeds it is not covered by this pilot
    (bead_transfer_ok)."""
    for d in (a, b):
        if d.get("status") != "complete" or "dF_PIMD_meV_H" not in d:
            raise ValueError(f"{d.get('struct_id')}: run is not complete")
    if a["struct_id"] != b["struct_id"]:
        raise ValueError("compare_runs needs two runs of the same structure")
    ra, rb = dict(a["run_args"]), dict(b["run_args"])
    varied = sorted(k for k in set(ra) | set(rb) if ra.get(k) != rb.get(k) and k not in ("seed", "steps"))
    if varied not in (["beads"], ["dt"]):
        raise ValueError(f"runs differ in {varied}; compare P or dt only")
    if ra.get("seed") == rb.get("seed"):
        # the combined error below assumes independent runs; a shared seed shares thermostat noise (review, 24 Oct)
        raise ValueError(f"runs share seed {ra.get('seed')}; the P or dt comparison needs independent seeds")
    lo, hi = sorted((ra[varied[0]], rb[varied[0]]))
    if not np.isclose(hi, 2 * lo, rtol=1e-9):
        raise ValueError(f"{varied[0]}: {lo} vs {hi}; the convergence check needs exactly a factor 2 (P vs 2P, dt vs dt/2)")
    if any(d.get("delta_anh_meV_H") is None for d in (a, b)):
        raise ValueError("compare_runs needs verified, valid same-P Delta_anh values")
    small, big = sorted((a, b), key=lambda d: d["run_args"][varied[0]])
    diff = big["delta_anh_meV_H"] - small["delta_anh_meV_H"]
    if varied == ["dt"]:
        diff = -diff
    err = float(np.hypot(a["dF_PIMD_err_meV_H"], b["dF_PIMD_err_meV_H"]))
    upper = abs(diff) + z * err
    errs_ok = bool(a.get("error_converged") and b.get("error_converged"))
    out = {"struct_id": a["struct_id"], "varied": varied[0], "a": ra[varied[0]], "b": rb[varied[0]],
           "diff_meV_H": diff, "diff_err_meV_H": err, "z": z, "upper_bound_meV_H": upper, "tol_meV_H": tol,
           "errors_converged": errs_ok, "converged": bool(errs_ok and upper < tol)}
    if varied == ["beads"]:
        out["pilot_reject_P"] = bool(abs(diff) > 0.3 and abs(diff) > 1.96 * err)
        out["pilot_rule"] = "A4: reject only if abs(d)>0.3 meV/H and abs(d)>1.96*sigma_d; converged is diagnostic"
        out["d_meV_H"], out["sigma_d_meV_H"] = diff, err
        out["harmonic_bead_error_meV_H"] = {str(ra["beads"]): a["harmonic_bead_error_meV_H"],
                                            str(rb["beads"]): b["harmonic_bead_error_meV_H"]}
        big = a if ra["beads"] > rb["beads"] else b
        out["transfer_P"] = big["P"]
        out["transfer_reference_meV_H"] = abs(big["harmonic_bead_error_meV_H"])
    return out


def bead_transfer_ok(pilot, doc):
    """Harmonic prescreen only: True if doc (production, same P as the pilot's larger P) has a harmonic bead error
    no larger than the pilot's, i.e. its spectrum is not stiffer for the ring polymer. This does not bound the
    anharmonic bead error of doc; False means even the prescreen fails. Not a convergence proof."""
    return bool(pilot["converged"] and doc["P"] == pilot["transfer_P"]
                and abs(doc["harmonic_bead_error_meV_H"]) <= pilot["transfer_reference_meV_H"])


def _compare_main(argv):
    ap = argparse.ArgumentParser(description="P or dt convergence between two PIMD run JSONs")
    ap.add_argument("--compare", nargs=2, type=Path, required=True)
    ap.add_argument("--tol", type=float, default=COMPARE_TOL_MEV)
    ap.add_argument("--z", type=float, default=2.0)
    a = ap.parse_args(argv)
    res = compare_runs(*(json.loads(p.read_text()) for p in a.compare), tol=a.tol, z=a.z)
    print(json.dumps(res, indent=1))
    return res


def main(argv=None):
    import sys

    argv = sys.argv[1:] if argv is None else list(argv)
    if "--compare" in argv:
        return _compare_main(argv)
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
    ap.add_argument("--dtype", choices=("float32", "float64"), default="float32", help="MACE model dtype")
    ap.add_argument("--init", choices=("harmonic", "positions"), default="harmonic")
    ap.add_argument("--pre-equil", type=int, default=1000, help="discarded steps at light H, before GL points")
    ap.add_argument("--stationarity-extension", type=int, default=3000, help="one extension on a failed halves test")
    ap.add_argument("--dump-every", type=int, default=0, help="snapshot interval in kept steps; 0 disables")
    ap.add_argument("--allow-invalid-reference", action="store_true", help="diagnostic run despite residual force gate")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, default=RAW)
    ap.add_argument("--cache-root", type=Path, default=CACHE)
    ap.add_argument("--state-root", type=Path, default=STATE)
    ap.add_argument("--hessian-check", choices=("auto", "on", "off"), default="auto",
                    help="finite-difference Hessian of the PIMD cell with the run's own force backend, compared "
                         "with the interpolated same-cell reference; auto = only when the PIMD q-points are not "
                         "commensurate with the force-constant supercell")
    ap.add_argument("--log-every", type=int, default=0)
    ap.add_argument("--stop-after", type=int, default=None, help=argparse.SUPPRESS)  # tests: simulate interruption
    a = ap.parse_args(argv)

    if (a.beads < 1 or a.steps < 2 or not 0 <= a.equil < 1 or a.dt <= 0 or a.T <= 0 or a.tau0 <= 0
            or min(a.pre_equil, a.stationarity_extension, a.dump_every) < 0
            or a.masses_points < 1 or (a.bead_chunk is not None and a.bead_chunk < 1)):
        raise ValueError("invalid PIMD step counts, temperature, timestep or sampling options")

    from ase import Atoms

    from isoshift import cache

    cdir = find_cache(a.struct, a.raw_root, a.cache_root)
    ph, meta = cache.load_fc(cdir.name, root=cdir.parent)
    uc = ph.unitcell
    cell_atoms = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    sc = [int(x) for x in np.diag(Ph.supercell_for_min_length(cell_atoms, MIN_LENGTH, MAX_ATOMS))]
    out_path = a.out if a.out.is_absolute() else ROOT / a.out
    state = Path(a.state_root).resolve() / f"{out_path.stem}.npz"
    run_args = {k: getattr(a, k) for k in ("beads", "steps", "dt", "T", "tau0", "masses_points", "equil", "seed",
                                         "backend", "bead_chunk", "splitting", "dtype", "device", "init", "pre_equil",
                                         "stationarity_extension", "dump_every", "allow_invalid_reference", "hessian_check")}
    run_args["state_root"] = str(state.parent)
    # Old checkpoints lack the aligned vector sums; their gates cannot be recomputed faithfully.
    run_args["monitor_schema"] = "time-averaged-centroid-v2"
    prev = json.loads(out_path.read_text()) if out_path.exists() else {}
    saved = None
    if state.exists():
        with np.load(state, allow_pickle=False) as f:
            saved = {k: f[k].copy() for k in f.files}
        # The atomic NPZ is authoritative if interruption happened before its JSON mirror was written.
        checkpoint_doc = json.loads(str(saved["doc"]))
        if checkpoint_doc.get("output_path") != str(out_path.resolve()):
            raise ValueError("restart state belongs to another output path")
        prev = checkpoint_doc
    elif prev:
        raise ValueError(f"missing restart state {state}; refusing to mix runs")
    if prev and (prev.get("run_args") != run_args or prev.get("cache_key") != cdir.name
                 or prev.get("struct_id") != a.struct):
        raise ValueError(f"{out_path} exists with different arguments or cache; refusing to mix runs")
    done = prev.get("points", [])

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
        forces = MaceForces(atoms, device=a.device, bead_chunk=a.bead_chunk, dtype=a.dtype)

    mask_h = atoms.numbers == 1
    n_h = int(mask_h.sum())
    if not n_h:
        raise ValueError(f"{a.struct}: no H atoms")
    base = Ph.make_masses(atoms, {}, default="light")
    # Gate at x0 itself, before diagonalisation, FD Hessians, harmonic draws or ring propagation.
    f0, _ = forces(atoms.positions[None])
    f0_max = float(np.linalg.norm(f0[0], axis=1).max())
    invalid_reference = not np.isfinite(f0_max) or f0_max > 1e-3
    if invalid_reference and not a.allow_invalid_reference:
        raise ValueError(f"residual force at x0 {f0_max:.6g} eV/A exceeds 1e-3; invalid reference. "
                         "--allow-invalid-reference permits a diagnostic run with null primary Delta_anh")
    if a.backend == "harmonic":
        forces.validate_stability(base)
    g_nodes, w = ti_nodes(a.masses_points)
    harm = prev.get("harmonic_samecell") or harmonic_samecell(ph, sc, a.T, P=a.beads)
    harm_meV = harm["dF_eV"] * 1e3 / n_h
    harm_P_meV = harm["dF_P_eV"] * 1e3 / n_h
    stability = prev.get("step_stability") or check_step_stable(
        a.beads, a.T, a.dt, harm["nu_max_thz"], a.tau0, a.splitting)
    hess = prev.get("hessian_check")
    want_hess = a.hessian_check == "on" or (a.hessian_check == "auto" and not harm["qpoints_exact"])
    if saved is not None:
        phi = saved["phi"]
        init_source = prev["init_hessian_source"]
    elif want_hess:
        t0 = time.perf_counter()
        phi = fd_hessian(forces, atoms.positions, delta=.01, chunk=a.bead_chunk or a.beads)
        direct = hessian_samecell(phi, base, mask_h, a.T, P=a.beads)
        d_meV, dp_meV = direct["dF_eV"] * 1e3 / n_h, direct["dF_P_eV"] * 1e3 / n_h
        hess = {"dF_direct_meV_H": d_meV, "dF_interp_meV_H": harm_meV, "diff_meV_H": d_meV - harm_meV,
                "dF_direct_P_meV_H": dp_meV, "diff_P_meV_H": dp_meV - harm_P_meV,
                "tol_meV_H": HESSIAN_TOL_MEV,
                "passed": bool(direct["valid"] and max(abs(d_meV - harm_meV), abs(dp_meV - harm_P_meV)) < HESSIAN_TOL_MEV),
                "direct_valid": direct["valid"], "direct_translations_verified": direct["translations_verified"],
                "direct_n_nonpositive": direct["n_nonpositive_nontranslation_H"], "delta_A": .01,
                "wall_s": time.perf_counter() - t0}
        init_source = "finite-difference Hessian of PIMD cell with run force dtype"
    elif a.backend == "harmonic":
        phi = forces.phi.copy()
        init_source = "harmonic backend force constants in phonopy supercell order"
    else:
        phi = cached_hessian(ph, sc, atoms)
        init_source = "cached commensurate dynamical matrices, inverse Bloch transform in ASE order"
    fc_ok = bool(hess["passed"]) if hess is not None else bool(harm["qpoints_exact"])
    imaginary_modes = imaginary_cartesian_modes(phi, base)
    monitor_factory = lambda data: StructuralMonitor(atoms.positions, atoms.cell.array, atoms.numbers,
                                                       imaginary_modes, state=data)
    rng = np.random.default_rng(a.seed)
    git_provenance = _git_hash()
    gpu_peak = prev.get("gpu_peak_GB")
    use_cuda = a.backend == "mace" and a.device.startswith("cuda")
    if use_cuda:
        import torch
        gpu_device = torch.device(a.device)
        if gpu_device.index is None:
            gpu_device = torch.device("cuda", torch.cuda.current_device())
        torch.cuda.reset_peak_memory_stats(gpu_device)
    rp = RingPolymer(atoms.positions, base, a.beads, a.T, a.dt, a.tau0, forces, rng, splitting=a.splitting)
    active = None
    phase = "pre_equil"
    pre = prev.get("pre_equil", {"g": 1., "steps": 0, "target_steps": a.pre_equil, "wall_s": 0.,
                                "seconds_per_ring_step": None, "discarded": True})
    if saved is not None:
        rp.q, rp.p = saved["q"], saved["p"]
        rp.f, rp.v = rp.forces(rp.q)
        rng.bit_generator.state = json.loads(str(saved["rng"]))
        phase = str(saved["phase"])
        if str(saved["active"]) != "null":
            active = json.loads(str(saved["active"]))
            active["ks"] = saved["ks"].tolist()
            active["snapshot_q"] = list(saved["snapshot_q"])
    elif a.init == "harmonic":
        rp.initialize_harmonic(phi)

    def document(points):
        nonlocal gpu_peak
        if use_cuda:
            gpu_peak = max(gpu_peak or 0., torch.cuda.max_memory_allocated(gpu_device) / 1e9)
        wall = pre["wall_s"] + sum(p["wall_s"] for p in points)
        nsteps = pre["steps"] + sum(p["steps"] for p in points)
        doc = {"struct_id": a.struct, "status": "complete" if len(points) == a.masses_points else "partial",
               "output_path": str(out_path.resolve()), "run_args": run_args, "cache_key": cdir.name,
               "fc_supercell": [int(x) for x in np.diag(ph.supercell_matrix)], "supercell": sc,
               "natoms": len(atoms), "n_H": n_h, "P": a.beads, "dt_fs": a.dt, "T_K": a.T, "tau0_fs": a.tau0,
               "splitting": a.splitting, "seed": a.seed, "model": forces.info(), "git": git_provenance,
               "initial_max_abs_F_eV_A": f0_max, "residual_force_definition": "max atom Euclidean force norm at x0",
               "invalid_reference": invalid_reference, "gpu_peak_GB": gpu_peak, "points": points,
               "init": a.init, "init_hessian_source": init_source, "pre_equil": pre,
               "imaginary_modes_cartesian": imaginary_modes.tolist(), "monitors": merge_monitors(points, monitor_factory),
               "thermodynamic_ensemble": "NVT", "free_energy_potential": "Helmholtz F at fixed cell",
               "stationarity_ok": bool(points) and all(p["stationarity_ok"] for p in points),
               "wall_s": wall, "seconds_per_ring_step": wall / nsteps if nsteps else None,
               "harmonic_samecell": harm, "dF_harm_samecell_meV_H": harm_meV,
               "dF_harm_samecell_P_meV_H": harm_P_meV,
               "harmonic_bead_error_meV_H": harm_P_meV - harm_meV,
               "s_imag_meV_H": harm["s_imag_meV_H"], "harmonic_valid": harm["valid"],
               "step_stability": stability, "hessian_check": hess, "fc_interpolation_verified": fc_ok,
               "zero_modes": "three Gamma translations verified by mass-weighted projection are replaced by "
                             "-(3/2)kT ln M_tot; non-translation imaginary modes folded to |nu| (A9); zeros invalidate",
               "finite_size": "same-cell subtraction cancels only harmonic finite-size error; anharmonic size dependence unbounded"}
        unverified = ["time_step (C1 harmonic control required)", "beads (A4 pilot and A4b residual required)",
                      "finite_size_anharmonic"]
        if not fc_ok:
            unverified.append("fc_interpolation (Hessian check missing or failed)")
        if not harm["valid"]:
            unverified.append("harmonic_reference (translations unverified or non-translation zero modes)")
        if invalid_reference:
            unverified.append("residual_force (invalid reference override)")
        if not doc["stationarity_ok"]:
            unverified.append("stationarity (halves test failed or no completed points)")
        if doc["monitors"] and not doc["monitors"]["retention_ok"]:
            unverified.append("structural_retention (imaginary projection or O-H assignment)")
        if doc["monitors"] and not doc["monitors"]["heavy_rmsd_ok"]:
            unverified.append("heavy_atom_drift (time-averaged aligned centroid RMSD >= 0.15 A)")
        doc["error_converged"] = bool(points) and all(p["error_converged"] for p in points)
        if not doc["error_converged"]:
            unverified.append("statistical_error (no block plateau or too few independent samples)")
        doc["unverified"] = unverified
        if len(points) == a.masses_points:
            df, err = _summarize(points, w)
            ok = harm["valid"] and fc_ok and not invalid_reference
            doc.update({"dF_PIMD_meV_H": df, "dF_PIMD_err_meV_H": err,
                        "delta_anh_meV_H": df - harm_P_meV if ok else None, "delta_anh_err_meV_H": err,
                        "delta_anh_unchecked_meV_H": df - harm_P_meV,
                        "delta_anh_inf_meV_H": df - harm_meV,
                        "delta_anh_beadcorr_meV_H": df - harm_P_meV})
        return doc

    def save(points, progress=None, checkpoint_phase="points"):
        doc = document(points)
        meta_progress = None if progress is None else {k: v for k, v in progress.items() if k not in ("ks", "snapshot_q")}
        _atomic_npz(state, q=rp.q, p=rp.p, phi=phi, rng=json.dumps(rng.bit_generator.state),
                    phase=checkpoint_phase, doc=json.dumps(doc), active=json.dumps(meta_progress),
                    ks=np.asarray(progress["ks"] if progress else [], dtype=np.float64),
                    snapshot_q=np.asarray(progress["snapshot_q"] if progress else [], dtype=np.float64)
                    .reshape(-1, *rp.q.shape))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, separators=(",", ":")))
        tmp.replace(out_path)

    if phase == "pre_equil":
        # Persist the draw before the first MD step, then partial pre-equilibration and its momenta/RNG.
        save(done, checkpoint_phase="pre_equil")
        started, prior_wall = time.perf_counter(), pre["wall_s"]
        try:
            while pre["steps"] < a.pre_equil:
                _checkpointable_step(rp)
                pre["steps"] += 1
                if pre["steps"] % 100 == 0:
                    pre["wall_s"] = prior_wall + time.perf_counter() - started
                    pre["seconds_per_ring_step"] = pre["wall_s"] / pre["steps"]
                    save(done, checkpoint_phase="pre_equil")
        except BaseException:
            pre["wall_s"] = prior_wall + time.perf_counter() - started
            pre["seconds_per_ring_step"] = pre["wall_s"] / pre["steps"] if pre["steps"] else None
            save(done, checkpoint_phase="pre_equil")
            raise
        pre["wall_s"] = prior_wall + time.perf_counter() - started
        pre["seconds_per_ring_step"] = pre["wall_s"] / pre["steps"] if pre["steps"] else None
        save(done)

    completed = list(done)
    def on_point(points):
        completed[:] = points
        save(points)
        print(f"{a.struct} point {len(points)}/{a.masses_points}: g={points[-1]['g']:.5f} "
              f"<K_H>={points[-1]['K_H_meV']:.2f}+-{points[-1]['K_H_err_meV']:.2f} meV/H, "
              f"{points[-1]['steps_per_s']:.3f} steps/s", flush=True)

    todo = g_nodes if a.stop_after is None else g_nodes[:len(done) + a.stop_after]
    pts = run_points(rp, mask_h, todo, a.steps, a.equil, base, on_point=on_point, done=done, log_every=a.log_every,
                     weights=w, extension_steps=a.stationarity_extension, monitor_factory=monitor_factory,
                     dump_every=a.dump_every, dump_root=state.parent, dump_stem=out_path.stem,
                     cell=atoms.cell.array, atomic_numbers=atoms.numbers, active=active,
                     on_progress=lambda progress: save(completed, progress))
    if len(pts) == len(done):
        save(pts, active)
    return json.loads(out_path.read_text())


if __name__ == "__main__":
    main()
