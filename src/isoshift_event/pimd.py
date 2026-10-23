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
The harmonic reference removes exactly the three Gamma translations, identified by their projection on the
mass-weighted translation vectors and verified below GAMMA_TOL_THZ (classify_modes), keeps every other positive
mode, and adds this F_COM term back explicitly, so both sides count the same 3N degrees of freedom.

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
    enters the free energy however small; a non-translation mode with nu <= 0 is counted, never made positive.
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
            "n_imag": int((rest & (nu < Ph.IMAG_TOL_THZ)).sum()),
            "n_soft_kept": int((keep & (nu < tol)).sum()),
            "min_freq_THz_nontranslation": float(nu[rest].min()) if rest.any() else None}
    info["translations_verified"] = bool(info["translation_overlap_min"] > min_overlap
                                         and info["translation_max_abs_THz"] < tol)
    return keep, trans, info


def _isotope_free_energy(nu, keep, total_mass_u, T, P=None):
    """Harmonic F (eV) of the kept modes plus the free translation of the whole cell."""
    return float(_osc_free_energy(nu[keep], T, P).sum()) + com_free_energy(total_mass_u, T)


def _assemble(per_iso, T, P):
    """per_iso: {iso: (nu, keep, info, total_mass_u)} -> dF dict with validity flags."""
    out = {}
    F, Fp = {}, {}
    for iso, (nu, keep, info, mtot) in per_iso.items():
        out.update({f"{k}_{iso}": v for k, v in info.items()})
        F[iso] = _isotope_free_energy(nu, keep, mtot, T)
        if P is not None:
            Fp[iso] = _isotope_free_energy(nu, keep, mtot, T, P)
    out["dF_eV"] = float(F["D"] - F["H"])
    out["dF_com_eV"] = float(com_free_energy(per_iso["D"][3], T) - com_free_energy(per_iso["H"][3], T))
    if P is not None:
        out["dF_P_eV"] = float(Fp["D"] - Fp["H"])
    out["has_imaginary"] = bool(out["n_imag_H"] > 0 or out["n_imag_D"] > 0)
    out["translations_verified"] = bool(out["translations_verified_H"] and out["translations_verified_D"])
    out["valid"] = bool(out["translations_verified"] and out["n_nonpositive_nontranslation_H"] == 0
                        and out["n_nonpositive_nontranslation_D"] == 0)
    return out


def _fc_asr_max(fc):
    """max over atoms i of |sum_j Phi_ij| (eV/A^2), compact or full force constants."""
    return float(np.abs(np.asarray(fc).sum(axis=1)).max())


def harmonic_samecell(ph, sc, T, P=None):
    """Same-cell harmonic F_D - F_H for the supercell sc (diagonal ints) from the force constants of ph.

    Zero modes: exactly the three translations at Gamma, identified and verified by classify_modes, are removed
    and replaced by the free translation -(3/2) kT ln M_tot of the whole supercell (M_tot = sum of the masses of
    the PIMD cell), which the PIMD centroid contains. Imaginary or zero non-translation modes make the result
    invalid (valid = False) and are excluded from the sum, never folded to positive values.

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
        ev = np.array(p.qpoints.eigenvectors)[i_gamma]
        keep, _, info = classify_modes(nu, ev, masses, i_gamma=i_gamma)
        per_iso[iso] = (nu, keep, info, float(masses.sum()) * len(qpts))
    out = {"n_qpoints": len(qpts), "source": "cached force constants, commensurate q of the PIMD supercell",
           "qpoints_exact": qpoints_commensurate_with(qpts, ph.supercell_matrix),
           "fc_asr_max_eV_A2": _fc_asr_max(ph.force_constants), "nu_max_thz": float(per_iso["H"][0].max())}
    out.update(_assemble(per_iso, T, P))
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
        keep, _, info = classify_modes(nu, vec, m)
        per_iso[iso] = (nu, keep, info, float(m.sum()))
    out = {"n_qpoints": 1, "source": "finite-difference Hessian of the PIMD supercell"}
    out.update(_assemble(per_iso, T, P))
    return out


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
        se = stat_error(ks)
        results.append({"g": float(g), "mass_H_u": float(M_H / g ** 2),
                        "weight": None if weights is None else float(weights[i]), "K_H_meV": float(ks.mean() * 1e3),
                        "K_H_err_meV": se["err"] * 1e3, "error_converged": se["converged"],
                        "K_H_err_block_meV": se["err_block"] * 1e3, "K_H_err_acf_meV": se["err_acf"] * 1e3,
                        "plateau_block_size": se["plateau_block_size"], "plateau_n_blocks": se["plateau_n_blocks"],
                        "tau_int_steps": se["tau_int_steps"], "n_eff": se["n_eff"],
                        "steps": steps, "steps_equil": n_eq, "steps_used": len(ks),
                        "block_curve_meV": [[b, nb, e * 1e3] for b, nb, e in se["curve"]],
                        "wall_s": wall, "steps_per_s": steps / wall})
        if on_point:
            on_point(results)
    return results


def _summarize(points, w):
    g = [p["g"] for p in points]
    df, err = ti_integrate(g, w[: len(points)], [p["K_H_meV"] for p in points], [p["K_H_err_meV"] for p in points])
    return df, err


# ---------------------------------------------------------------- systematic checks between runs

COMPARE_TOL_MEV = 0.3  # P12 section 2: P vs 2P, and the per-structure error target
HESSIAN_TOL_MEV = 0.1  # interpolated vs PIMD-cell Hessian, meV per H (a third of the 0.3 meV target)


def compare_runs(a, b, tol=COMPARE_TOL_MEV, z=2.0):
    """Systematic check between two completed run JSONs of one structure that differ in P or dt only.

    diff = dF_PIMD(b) - dF_PIMD(a) per H, err = combined statistical error (independent runs). converged needs
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
    lo, hi = sorted((ra[varied[0]], rb[varied[0]]))
    if not np.isclose(hi, 2 * lo, rtol=1e-9):
        raise ValueError(f"{varied[0]}: {lo} vs {hi}; the convergence check needs exactly a factor 2 (P vs 2P, dt vs dt/2)")
    diff = b["dF_PIMD_meV_H"] - a["dF_PIMD_meV_H"]
    err = float(np.hypot(a["dF_PIMD_err_meV_H"], b["dF_PIMD_err_meV_H"]))
    upper = abs(diff) + z * err
    errs_ok = bool(a.get("error_converged") and b.get("error_converged"))
    out = {"struct_id": a["struct_id"], "varied": varied[0], "a": ra[varied[0]], "b": rb[varied[0]],
           "diff_meV_H": diff, "diff_err_meV_H": err, "z": z, "upper_bound_meV_H": upper, "tol_meV_H": tol,
           "errors_converged": errs_ok, "converged": bool(errs_ok and upper < tol)}
    if varied == ["beads"]:
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
    harm_P_meV = harm["dF_P_eV"] * 1e3 / n_h
    # stop before any force call on an unstable P, T, dt (highest frequency is at the H mass, g = 1)
    stability = check_step_stable(a.beads, a.T, a.dt, harm["nu_max_thz"], a.tau0, a.splitting)

    out_path = a.out if a.out.is_absolute() else ROOT / a.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_args = {k: getattr(a, k) for k in ("beads", "steps", "dt", "T", "tau0", "masses_points", "equil", "seed",
                                           "backend", "bead_chunk", "splitting")}
    done, prev = [], {}
    if out_path.exists():
        prev = json.loads(out_path.read_text())
        if prev.get("run_args") != run_args:
            raise ValueError(f"{out_path} exists with different arguments {prev.get('run_args')}; refusing to mix runs")
        done = prev.get("points", [])
    state = Path(a.state_root) / f"{out_path.stem}.npz"

    # Interpolation check of the same-cell reference: the PIMD cell's own Hessian with the run's backend.
    hess = prev.get("hessian_check") if done else None
    want_hess = a.hessian_check == "on" or (a.hessian_check == "auto" and not harm["qpoints_exact"])
    if want_hess and hess is None:
        t0 = time.time()
        direct = hessian_samecell(fd_hessian(forces, atoms.positions, delta=0.01, chunk=a.bead_chunk or a.beads),
                                  base, mask_h, a.T)
        d_meV = direct["dF_eV"] * 1e3 / n_h
        hess = {"dF_direct_meV_H": d_meV, "dF_interp_meV_H": harm_meV, "diff_meV_H": d_meV - harm_meV,
                "tol_meV_H": HESSIAN_TOL_MEV, "passed": bool(direct["valid"] and abs(d_meV - harm_meV) < HESSIAN_TOL_MEV),
                "direct_valid": direct["valid"], "direct_translations_verified": direct["translations_verified"],
                "direct_n_nonpositive": direct["n_nonpositive_nontranslation_H"], "delta_A": 0.01,
                "wall_s": time.time() - t0}
    # a check that ran decides, also when the q-points are exact (a failed direct Hessian is a real disagreement)
    fc_ok = bool(hess["passed"]) if hess is not None else bool(harm["qpoints_exact"])

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
               "dF_harm_samecell_meV_H": harm_meV, "dF_harm_samecell_P_meV_H": harm_P_meV,
               "harmonic_bead_error_meV_H": harm_P_meV - harm_meV,
               "harmonic_valid": harm["valid"], "step_stability": stability, "hessian_check": hess, "fc_interpolation_verified": fc_ok,
               "zero_modes": "the three Gamma translations, identified by projection on the mass-weighted "
                             "translations and verified below GAMMA_TOL_THZ, are removed from the harmonic "
                             "reference and -(3/2) kT ln M_tot of the PIMD supercell is added (free translation, "
                             "present in the PIMD centroid); all other positive modes are kept",
               "finite_size": "delta_anh is the anharmonic correction in this supercell; the same-cell "
                              "subtraction removes only the harmonic finite-size term, the cell-size dependence "
                              "of delta_anh itself is not bounded by this run"}
        unverified = ["time_step (needs compare_runs at dt/2)", "beads (needs compare_runs P vs 2P, "
                      "bead_transfer_ok)", "finite_size_anharmonic"]
        if not fc_ok:
            unverified.append("fc_interpolation (PIMD q-points interpolated, Hessian check missing or failed)")
        if not harm["valid"]:
            unverified.append("harmonic_reference (translations unverified or imaginary/zero modes)")
        err_conv = bool(points) and all(p["error_converged"] for p in points)
        if not err_conv:
            unverified.append("statistical_error (no block plateau or too few independent samples)")
        doc["error_converged"] = err_conv
        doc["unverified"] = unverified
        if len(points) == a.masses_points:
            df, err = _summarize(points, w)
            ok = bool(harm["valid"] and fc_ok)
            doc.update({"dF_PIMD_meV_H": df, "dF_PIMD_err_meV_H": err,
                        "delta_anh_meV_H": df - harm_meV if ok else None, "delta_anh_err_meV_H": err,
                        "delta_anh_unchecked_meV_H": df - harm_meV,
                        "delta_anh_beadcorr_meV_H": df - harm_P_meV})
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
