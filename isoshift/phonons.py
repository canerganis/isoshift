"""Phonopy finite-displacement force constants and mass-override harmonic thermodynamics.

Force constants are mass independent (Born-Oppenheimer). They are computed once per structure;
any isotope assignment is then evaluated by re-diagonalizing the dynamical matrix with new masses.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from ase.data import atomic_masses, atomic_numbers

from . import cache as _cache

KB_EV = 8.617333262e-5
H_EV_THZ = 4.135667696e-3  # eV per THz (h*nu)
IMAG_TOL_THZ = -0.1
GAMMA_TOL_THZ = 0.1  # freq below this is treated as a translational/zero mode and excluded

# isotope label -> mass (u)
MASS_MAP = {
    "H": 1.00782503, "D": 2.01410178, "T": 3.01604928,
    "6Li": 6.0151228, "7Li": 7.0160034,
    "10B": 10.0129370, "11B": 11.0093054,
    "14N": 14.0030740, "15N": 15.0001089,
    "16O": 15.9949146, "18O": 17.9991610,
    "12C": 12.0, "13C": 13.0033548,
}


def _mass_of(label: str) -> float:
    if label in MASS_MAP:
        return MASS_MAP[label]
    return float(atomic_masses[atomic_numbers[label]])


def make_masses(atoms, substitution: dict | None = None, default: str = "natural") -> np.ndarray:
    """Per-atom mass array.

    substitution maps element symbol -> isotope label or float mass, e.g. {"H": "D"},
    {"Li": "6Li"}, {"H": 2.014}. Unlisted elements use the natural-abundance mass, except
    H when default == "light" (1.00783).
    """
    substitution = substitution or {}
    out = []
    for s in atoms.get_chemical_symbols():
        if s in substitution:
            v = substitution[s]
            out.append(float(v) if not isinstance(v, str) else _mass_of(v))
        elif default == "light" and s == "H":
            out.append(MASS_MAP["H"])
        else:
            out.append(float(atomic_masses[atomic_numbers[s]]))
    return np.array(out)


def supercell_for_min_length(atoms, min_length: float = 10.0, max_atoms: int | None = None,
                             floor_length: float = 6.0) -> np.ndarray:
    """Diagonal supercell matrix so every perpendicular cell height is >= min_length (A).

    If max_atoms is given and the supercell would exceed it, min_length is reduced in 0.5 A steps
    (not below floor_length) until it fits.
    """
    cell = atoms.cell.array
    vol = abs(np.linalg.det(cell))
    heights = [vol / np.linalg.norm(np.cross(cell[(i + 1) % 3], cell[(i + 2) % 3])) for i in range(3)]
    L = min_length
    while True:
        n = [max(1, int(np.ceil(L / h - 1e-8))) for h in heights]
        if max_atoms is None or int(np.prod(n)) * len(atoms) <= max_atoms or L <= floor_length:
            return np.diag(n)
        L -= 0.5


def _pa(symbols, cell, spos, masses=None):
    from phonopy.structure.atoms import PhonopyAtoms

    return PhonopyAtoms(symbols=list(symbols), cell=np.array(cell), scaled_positions=np.array(spos),
                        masses=None if masses is None else np.asarray(masses, dtype=float))


def compute_force_constants(atoms, calc, supercell=None, min_length: float = 10.0,
                            displacement: float = 0.01, symprec: float = 1e-4, symmetrize: bool = True):
    """Finite displacement force constants. `atoms` must already be relaxed with `calc`.
    Returns (Phonopy object with force constants, meta dict)."""
    from ase import Atoms
    from phonopy import Phonopy

    sc = supercell_for_min_length(atoms, min_length) if supercell is None else np.array(supercell)
    ph = Phonopy(_pa(atoms.get_chemical_symbols(), atoms.cell.array, atoms.get_scaled_positions()),
                 supercell_matrix=sc, primitive_matrix="P", symprec=symprec, log_level=0)
    ph.generate_displacements(distance=displacement)
    forces = []
    for s in ph.supercells_with_displacements:
        a = Atoms(symbols=s.symbols, cell=s.cell, scaled_positions=s.scaled_positions, pbc=True)
        a.calc = calc
        forces.append(a.get_forces())
    ph.forces = np.array(forces)
    ph.produce_force_constants()
    if symmetrize:  # enforce translational (acoustic sum rule) and index-permutation symmetry
        ph.symmetrize_force_constants()
    a0 = atoms.copy()
    a0.calc = calc
    meta = {"supercell": np.diag(sc).tolist(), "n_displacements": len(forces),
            "displacement": displacement, "natoms_cell": len(atoms),
            "natoms_supercell": len(ph.supercell),
            "energy_eV": float(a0.get_potential_energy()), "volume_A3": float(atoms.get_volume())}
    return ph, meta


def get_force_constants(atoms, calc, calc_id: str, min_length: float = 10.0, supercell=None,
                        max_atoms: int | None = 400, displacement: float = 0.01, use_cache: bool = True, cache_root=None):
    """Cached wrapper around compute_force_constants. Returns (Phonopy, meta, from_cache)."""
    sc = supercell_for_min_length(atoms, min_length, max_atoms) if supercell is None else np.array(supercell)
    while True:
        key = _cache.cache_key(atoms, calc_id, sc, displacement)
        if use_cache:
            hit = _cache.load_fc(key, cache_root)
            if hit is not None:
                return hit[0], hit[1], True
        try:
            ph, meta = compute_force_constants(atoms, calc, supercell=sc, displacement=displacement)
            break
        except RuntimeError as e:  # CUDA OOM: retry with a smaller supercell
            if "out of memory" not in str(e) or supercell is not None:
                raise
            import torch

            torch.cuda.empty_cache()
            min_length -= 1.0
            if min_length < 5.0:
                raise
            sc = supercell_for_min_length(atoms, min_length)
    if use_cache:
        _cache.save_fc(ph, key, meta, cache_root)
    return ph, meta, False


def phonopy_with_masses(ph, masses):
    """New Phonopy object sharing ph's force constants but with the given per-atom masses.
    No forces are recomputed."""
    from phonopy import Phonopy

    uc = ph.unitcell
    new = Phonopy(_pa(uc.symbols, uc.cell, uc.scaled_positions, masses),
                  supercell_matrix=ph.supercell_matrix, primitive_matrix="P",
                  symprec=ph.symmetry.tolerance, log_level=0)
    new.force_constants = np.array(ph.force_constants)
    return new


@dataclass
class MeshFreqs:
    freqs: np.ndarray  # (nq, nbands) THz
    weights: np.ndarray  # (nq,)
    n_atoms: int

    @property
    def min_freq(self) -> float:
        return float(self.freqs.min())

    @property
    def n_imaginary(self) -> int:
        """Imaginary band count over the full mesh (q multiplicity weighted)."""
        return int(round(float(((self.freqs < IMAG_TOL_THZ) * self.weights[:, None]).sum())))

    @property
    def imaginary_fraction(self) -> float:
        tot = self.weights.sum() * self.freqs.shape[1]
        return float(((self.freqs < IMAG_TOL_THZ) * self.weights[:, None]).sum() / tot)

    def has_imaginary(self, tol: float = IMAG_TOL_THZ) -> bool:
        return bool((self.freqs < tol).any())

    def zpe(self) -> float:
        """Zero point energy, eV per unit cell."""
        e = 0.5 * H_EV_THZ * np.where(self.freqs > GAMMA_TOL_THZ, self.freqs, 0.0)
        return float((e * self.weights[:, None]).sum() / self.weights.sum())

    def helmholtz_free_energy(self, T) -> np.ndarray:
        """Vibrational Helmholtz free energy F_vib(T), eV per unit cell, T array in K."""
        T = np.atleast_1d(np.asarray(T, dtype=float))
        good = self.freqs > GAMMA_TOL_THZ
        e = np.where(good, H_EV_THZ * self.freqs, 1.0)
        w = self.weights[:, None]
        out = np.empty_like(T)
        for i, t in enumerate(T):
            term = 0.5 * e
            if t > 0:
                term = term + KB_EV * t * np.log1p(-np.exp(-e / (KB_EV * t)))
            out[i] = (np.where(good, term, 0.0) * w).sum() / self.weights.sum()
        return out


def mesh_frequencies(ph, masses=None, mesh=(8, 8, 8), is_gamma_center: bool = True) -> MeshFreqs:
    """Mesh frequencies for an arbitrary mass assignment, reusing ph's force constants."""
    p = ph if masses is None else phonopy_with_masses(ph, masses)
    p.run_mesh(list(mesh), with_eigenvectors=False, is_mesh_symmetry=True, is_gamma_center=is_gamma_center)
    m = p.mesh
    return MeshFreqs(np.array(m.frequencies), np.array(m.weights, dtype=float), len(p.unitcell))


def zpe(ph, masses, mesh=(8, 8, 8)) -> float:
    return mesh_frequencies(ph, masses, mesh).zpe()


def helmholtz_free_energy(ph, T_array, masses, mesh=(8, 8, 8)) -> np.ndarray:
    return mesh_frequencies(ph, masses, mesh).helmholtz_free_energy(T_array)


def imaginary_report(mf: MeshFreqs) -> dict:
    return {"min_freq_THz": mf.min_freq, "has_imaginary": mf.has_imaginary(),
            "n_imag_modes": mf.n_imaginary, "imag_fraction": mf.imaginary_fraction}


def choose_mesh(atoms, density: float = 40.0) -> tuple:
    """q mesh with about density/length points per axis, clipped to [4, 12]."""
    return tuple(int(min(12, max(4, round(density / l)))) for l in atoms.cell.lengths())
