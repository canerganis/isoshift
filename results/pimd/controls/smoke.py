"""Decision 18 row 0a: float32 MACE force throughput on mp-625152 PIMD cell, P = 16, bead chunk 4, 8, 16."""
import json
import sys
import time

import numpy as np

sys.path.insert(0, r"C:\Users\can02\Projects\osi-hackathon-2026")
import torch
from ase import Atoms

from isoshift import cache
from isoshift import phonons as Ph
from src.isoshift_event import pimd as M

torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
out = {}
for sid in sys.argv[2:]:
    cdir = M.find_cache(sid)
    ph, _ = cache.load_fc(cdir.name, root=cdir.parent)
    uc = ph.unitcell
    cell = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    sc = [int(x) for x in np.diag(Ph.supercell_for_min_length(cell, M.MIN_LENGTH, M.MAX_ATOMS))]
    atoms = cell * tuple(sc)
    rng = np.random.default_rng(0)
    q = atoms.positions[None] + 0.05 * rng.standard_normal((16, len(atoms), 3))
    res = {"supercell": sc, "natoms": len(atoms)}
    for chunk in (4, 8, 16):
        try:
            mf = M.MaceForces(atoms, bead_chunk=chunk, dtype="float32")
            torch.cuda.reset_peak_memory_stats()
            f0 = np.abs(mf(atoms.positions[None])[0]).max()
            mf(q)
            t0 = time.time()
            for _ in range(10):
                mf(q)
            res[f"chunk{chunk}"] = {"s_per_ring_step": (time.time() - t0) / 10,
                                    "peak_GB": torch.cuda.max_memory_allocated() / 1e9, "max_abs_F_x0": float(f0)}
        except RuntimeError as e:
            res[f"chunk{chunk}"] = {"error": str(e)[:120]}
        del mf
        import gc
        gc.collect()
        torch.cuda.empty_cache()
    out[sid] = res
    print(sid, json.dumps(res), flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
