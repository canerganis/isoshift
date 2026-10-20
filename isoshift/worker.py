"""Run a calculator-dependent job, in-process or in the secondary env (.venv-sevenn).

MACE and ORB run in .venv (e3nn 0.4.4). SevenNet and MatterSim need e3nn >= 0.5 and live in
.venv-sevenn. Results are exchanged as JSON; force constants through the shared disk cache.

CLI: python -m isoshift.worker harmonic|qha --calc sevenn --cif FILE --out FILE.json [opts]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SECONDARY_PY = ROOT / ".venv-sevenn" / "Scripts" / "python.exe"
SECONDARY_CALCS = {"sevenn", "mattersim"}


def _read(cif):
    from ase.io import read

    return read(cif)


def harmonic_job(cif: str, calc_name: str, device="cuda", min_length=10.0, max_atoms=None, fmax=0.001, relax_cell=True,
                 mesh=None, temps=(300.0,), subs=None, supercell=None, steps=500) -> dict:
    """Relax, force constants (cached), harmonic ZPE and F(T) for each mass variant."""
    from . import phonons as P
    from .calculators import MAX_ATOMS, calculator_info, get_calculator
    from .relax import relax

    max_atoms = max_atoms or MAX_ATOMS[calc_name]

    subs = subs or {"H": {}, "D": {"H": "D"}}
    calc = get_calculator(calc_name, device)
    info = calculator_info(calc)
    cid = f"{info['name']}-{info['model']}"
    atoms = _read(cif)
    t = time.time()
    a, rinfo = relax(atoms, calc, fmax=fmax, relax_cell=relax_cell, steps=steps)
    t_relax = time.time() - t
    t = time.time()
    ph, meta, hit = P.get_force_constants(a, calc, cid, min_length=min_length, supercell=supercell, max_atoms=max_atoms)
    t_fc = time.time() - t
    mesh = tuple(mesh) if mesh else P.choose_mesh(a)
    out = {"calc": info, "relax": rinfo, "fc_meta": meta, "fc_cached": hit, "mesh": list(mesh),
           "timing": {"relax_s": t_relax, "fc_s": t_fc}, "n_atoms": len(a), "formula": a.get_chemical_formula(),
           "variants": {}}
    if device.startswith("cuda"):
        import torch

        out["gpu_peak_mem_MB"] = torch.cuda.max_memory_allocated() / 2**20
    for name, sub in subs.items():
        mf = P.mesh_frequencies(ph, P.make_masses(a, sub, default="light"), mesh)
        out["variants"][name] = {"zpe_eV_cell": mf.zpe(), "F_eV_cell": mf.helmholtz_free_energy(list(temps)).tolist(),
                                 "imag": P.imaginary_report(mf)}
    out["temps"] = list(temps)
    return out


def qha_job(cif: str, calc_name: str, device="cuda", **kw) -> dict:
    from .calculators import MAX_ATOMS, calculator_info, get_calculator
    from .qha import qha_gibbs

    kw.setdefault("max_atoms", MAX_ATOMS[calc_name])

    calc = get_calculator(calc_name, device)
    info = calculator_info(calc)
    variants = kw.pop("variants", None) or {"H": {}, "D": {"H": "D"}}
    return qha_gibbs(_read(cif), calc, f"{info['name']}-{info['model']}", variants, **kw)


def run_job(kind: str, cif: str, calc_name: str, **kw) -> dict:
    """Dispatch to the right environment automatically. kw must be JSON serialisable."""
    if calc_name in SECONDARY_CALCS and Path(sys.executable).resolve() != SECONDARY_PY.resolve():
        return _subprocess(kind, cif, calc_name, kw)
    return {"harmonic": harmonic_job, "qha": qha_job}[kind](cif, calc_name, **kw)


def _subprocess(kind, cif, calc_name, kw):
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        cmd = [str(SECONDARY_PY), "-m", "isoshift.worker", kind, "--calc", calc_name, "--cif", str(cif),
               "--out", str(out), "--kw", json.dumps(kw)]
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode != 0 or not out.exists():
            raise RuntimeError(f"worker failed:\n{r.stderr[-3000:]}")
        return json.loads(out.read_text())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["harmonic", "qha"])
    ap.add_argument("--calc", required=True)
    ap.add_argument("--cif", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--kw", default="{}")
    a = ap.parse_args(argv)
    res = {"harmonic": harmonic_job, "qha": qha_job}[a.kind](a.cif, a.calc, **json.loads(a.kw))
    Path(a.out).write_text(json.dumps(res, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)))


if __name__ == "__main__":
    main()
