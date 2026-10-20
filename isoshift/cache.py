"""Disk cache of phonopy force constants keyed by structure hash + calculator + supercell."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

CACHE_ROOT = Path(__file__).resolve().parent.parent / ".cache" / "isoshift"


def structure_hash(atoms, decimals: int = 5) -> str:
    """Hash of species, cell and scaled positions (invariant to tiny numerical noise)."""
    h = hashlib.sha256()
    h.update(",".join(atoms.get_chemical_symbols()).encode())
    h.update(np.round(atoms.cell.array, decimals).tobytes())
    h.update(np.round(atoms.get_scaled_positions(wrap=True) % 1.0 % 0.99999999, decimals).tobytes())
    return h.hexdigest()[:20]


def cache_key(atoms, calc_id: str, supercell, displacement: float = 0.01) -> str:
    sc = "x".join(str(int(x)) for x in np.diag(np.array(supercell)))
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc_id)
    return f"{structure_hash(atoms)}__{safe}__sc{sc}__d{displacement:g}__sym"


def cache_dir(key: str, root: Path | None = None) -> Path:
    return Path(root or CACHE_ROOT) / key


def save_fc(ph, key: str, meta: dict | None = None, root: Path | None = None) -> Path:
    d = cache_dir(key, root)
    d.mkdir(parents=True, exist_ok=True)
    ph.save(str(d / "phonopy_params.yaml"), settings={"force_constants": True})
    (d / "meta.json").write_text(json.dumps(meta or {}, indent=1, default=float))
    return d


def has_fc(key: str, root: Path | None = None) -> bool:
    return (cache_dir(key, root) / "phonopy_params.yaml").exists()


def load_fc(key: str, root: Path | None = None):
    """Return (Phonopy with force constants, meta dict) or None."""
    d = cache_dir(key, root)
    f = d / "phonopy_params.yaml"
    if not f.exists():
        return None
    import phonopy

    ph = phonopy.load(str(f), produce_fc=False, log_level=0)
    meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
    return ph, meta
