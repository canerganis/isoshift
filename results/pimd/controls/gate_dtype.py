"""Decision 17 A1 gate: centroid-virial K_H from float32 vs float64 MACE forces on 20 harmonic-backend
ring-polymer configurations of mp-23807 (P = 16, 300 K). No MACE sampling."""
import json
import sys
import time

import numpy as np

sys.path.insert(0, r"C:\Users\can02\Projects\osi-hackathon-2026")
from ase import Atoms
from phonopy.harmonic.force_constants import compact_fc_to_full_fc

from isoshift import cache
from isoshift import phonons as Ph
from src.isoshift_event import pimd as M

sid, P = "mp-23807", 16
cdir = M.find_cache(sid)
ph, _ = cache.load_fc(cdir.name, root=cdir.parent)
fc = ph.force_constants
if fc.shape[0] != fc.shape[1]:
    fc = compact_fc_to_full_fc(ph.primitive, fc)
s = ph.supercell
atoms = Atoms(s.symbols, cell=s.cell, scaled_positions=s.scaled_positions, pbc=True)
mask = np.array([x == "H" for x in atoms.get_chemical_symbols()])
n_h = int(mask.sum())
masses = Ph.make_masses(atoms, {}, default="light")
rp = M.RingPolymer(atoms.positions, masses, P, 300.0, 0.25, 100.0, M.HarmonicForces(fc, atoms.positions),
                   np.random.default_rng(17), splitting="baoab")
for _ in range(2000):
    rp.step()
confs = []
for i in range(20):
    for _ in range(200):
        rp.step()
    confs.append(rp.q.copy())


def kcv(q, f):
    qc = q.mean(axis=0)
    vir = np.einsum("pna,pna->", (q - qc)[:, mask], -f[:, mask])
    return (1.5 * n_h * M.KB_EV * 300.0 + vir / (2 * P)) * 1e3 / n_h


res = {}
for dt in ("float32", "float64"):
    mf = M.MaceForces(atoms, bead_chunk=2 if dt == "float64" else 4, dtype=dt)
    t0 = time.time()
    res[dt] = [kcv(q, mf(q)[0]) for q in confs]
    res[dt + "_s"] = time.time() - t0
    del mf
    import gc, torch; gc.collect(); torch.cuda.empty_cache()
d = np.array(res["float32"]) - np.array(res["float64"])
out = {"gate": "A1 float32 vs float64 centroid-virial K_H", "struct_id": sid, "cache_key": cdir.name, "P": P,
       "n_configs": 20, "n_H": n_h, "K_H_float64_meV_H": res["float64"], "diff_meV_H": d.tolist(),
       "max_abs_diff_meV_H": float(np.abs(d).max()), "mean_diff_meV_H": float(d.mean()), "tol_meV_H": 0.05,
       "passed": bool(np.abs(d).max() <= 0.05), "wall_s": {k: res[k + "_s"] for k in ("float32", "float64")}}
print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}, indent=1))
json.dump(out, open(sys.argv[1], "w"), indent=1)
