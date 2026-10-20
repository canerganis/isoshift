"""Structure relaxation (positions + cell) with ASE."""
from __future__ import annotations

from ase.filters import FrechetCellFilter
from ase.optimize import BFGS, FIRE


def relax(atoms, calc, fmax: float = 0.001, steps: int = 500, optimizer: str = "FIRE",
          relax_cell: bool = True, constant_volume: bool = False, scalar_pressure: float = 0.0,
          symmetrize: bool = True, logfile=None):
    """Relax a copy of `atoms`. Returns (relaxed_atoms, info). scalar_pressure in eV/A^3.

    constant_volume keeps the cell volume fixed (shape and positions relax), for QHA scans.
    """
    a = atoms.copy()
    a.calc = calc
    if symmetrize:
        try:
            from ase.constraints import FixSymmetry

            a.set_constraint(FixSymmetry(a, symprec=1e-3))
        except Exception:
            pass
    target = FrechetCellFilter(a, constant_volume=constant_volume, scalar_pressure=scalar_pressure) if relax_cell else a
    opt = {"FIRE": FIRE, "BFGS": BFGS}[optimizer.upper()](target, logfile=logfile)
    converged = opt.run(fmax=fmax, steps=steps)
    a.set_constraint()
    info = {
        "converged": bool(converged),
        "steps": int(opt.get_number_of_steps()),
        "energy": float(a.get_potential_energy()),
        "volume": float(a.get_volume()),
        "fmax_final": float(abs(a.get_forces()).max()),
    }
    a.calc = None
    return a, info
