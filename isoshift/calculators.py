"""ASE calculator factory for universal MLIPs (MACE, ORB, SevenNet, MatterSim).

Only conservative (energy-derived force) models are used, as recommended for phonons.
MACE and ORB run in .venv; SevenNet and MatterSim need e3nn>=0.5 and run in .venv-sevenn
(see isoshift.worker.run_job, which dispatches automatically).
"""
from __future__ import annotations

import importlib.metadata as md
import os
import warnings

DEFAULT_MODELS = {
    "mace": "medium-mpa-0",
    "orb": "orb_v3_conservative_inf_mpa",
    "sevenn": "7net-mf-ompa",
    "mattersim": "MatterSim-v1.0.0-5M.pth",
}
SEVENN_MODAL = "mpa"
# supercell atom caps that fit an 8 GB GPU (SevenNet-MF-ompa is the memory hungry one)
MAX_ATOMS = {"mace": 400, "orb": 400, "sevenn": 100, "mattersim": 300}
_PKG = {"mace": "mace-torch", "orb": "orb-models", "sevenn": "sevenn", "mattersim": "mattersim"}

_cache: dict = {}


def _device(device: str) -> str:
    import torch

    if device.startswith("cuda") and not torch.cuda.is_available():
        warnings.warn("CUDA not available, using cpu")
        return "cpu"
    return device


def get_calculator(name: str, device: str = "cuda", model: str | None = None):
    """Return an ASE calculator. Cached per (name, model, device).

    The calculator carries `.isoshift_info` (dict: name, model, package version, device).
    """
    name = name.lower()
    if name not in DEFAULT_MODELS:
        raise ValueError(f"unknown calculator {name!r}, choose from {list(DEFAULT_MODELS)}")
    model = model or DEFAULT_MODELS[name]
    device = _device(device)
    key = (name, model, device)
    if key in _cache:
        return _cache[key]
    if name == "mace":
        from mace.calculators import mace_mp

        calc = mace_mp(model=model, device=device, default_dtype="float32", dispersion=False)
    elif name == "orb":
        from orb_models.forcefield import pretrained
        from orb_models.forcefield.calculator import ORBCalculator

        orbff = getattr(pretrained, model)(device=device, precision="float32-high", compile=False)
        calc = ORBCalculator(orbff, device=device)
    elif name == "mattersim":
        from mattersim.forcefield import MatterSimCalculator

        calc = MatterSimCalculator(load_path=model, device=device)
    else:
        from sevenn.calculator import SevenNetCalculator

        modal = SEVENN_MODAL if "mf" in model else None
        calc = SevenNetCalculator(model, modal=modal, device=device)
    calc.isoshift_info = {
        "name": name,
        "model": model,
        "package": _PKG[name],
        "version": md.version(_PKG[name]),
        "device": device,
    }
    _cache[key] = calc
    return calc


def calculator_info(calc) -> dict:
    return dict(getattr(calc, "isoshift_info", {}))


def available_calculators() -> list[str]:
    return list(DEFAULT_MODELS)


if __name__ == "__main__":
    for n in DEFAULT_MODELS:
        print(calculator_info(get_calculator(n, os.environ.get("DEVICE", "cuda"))))
