"""Decision 18 control C2: float64 re-evaluation of the float32 production snapshots of one run.

For each GL point, the dumped ring-polymer snapshots are evaluated with float32 and float64 MACE. Per snapshot the
centroid-virial K_H (meV per H) is computed with both, and the ring-polymer weight change
w = exp(-beta/P sum_k [E64_k - E32_k]). The shift of <K_H> at a point is the reweighted float64 mean minus the
float32 mean; it is propagated through the TI weights like dF. sigma from a bootstrap over snapshots.
Pass if |shift| + 2 sigma < 0.05 meV/H; s_f32 = max(0.02, |shift| + 2 sigma). Above 0.1 meV/H: stop and reconvene.
Usage: c2_float64.py <run.json> <out.json>"""
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
import torch
from ase import Atoms

from src.isoshift_event import pimd as M

torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
run = json.loads(Path(sys.argv[1]).read_text())
rng = np.random.default_rng(2)
calcs = {}
per_point, shifts, g_list, w_list = [], [], [], []
for j, pt in enumerate(run["points"]):
    z = np.load(pt["snapshots"]["path"], allow_pickle=False)
    q, mask, P, T = z["q"], z["mask_h"], int(z["P"]), float(z["T_K"])
    if not calcs:
        atoms = Atoms(numbers=z["atomic_numbers"], positions=z["x0_A"], cell=z["cell_A"], pbc=True)
        calcs = {"float32": M.MaceForces(atoms, bead_chunk=4, dtype="float32"),
                 "float64": M.MaceForces(atoms, bead_chunk=2, dtype="float64")}
    n_h = int(mask.sum())
    beta = 1 / (M.KB_EV * T)
    K, E = {"float32": [], "float64": []}, {"float32": [], "float64": []}
    for qs in q:
        qc = qs.mean(axis=0)
        for dt, mf in calcs.items():
            f, e = mf(qs)
            vir = np.einsum("pna,pna->", (qs - qc)[:, mask], -f[:, mask])
            K[dt].append((1.5 * n_h * M.KB_EV * T + vir / (2 * P)) * 1e3 / n_h)
            E[dt].append(e.sum() / P)
    k32, k64 = np.array(K["float32"]), np.array(K["float64"])
    dv = np.array(E["float64"]) - np.array(E["float32"])

    def shift(idx):
        lw = -beta * (dv[idx] - dv[idx].mean())
        w = np.exp(lw - lw.max())
        w /= w.sum()
        return float(np.sum(w * k64[idx]) - k32[idx].mean()), float(1 / np.sum(w ** 2))

    s, ess = shift(np.arange(len(q)))
    boot = [shift(rng.integers(0, len(q), len(q)))[0] for _ in range(2000)]
    per_point.append({"g": pt["g"], "n_snapshots": len(q), "paired_dK_mean_meV_H": float(np.mean(k64 - k32)),
                      "paired_dK_sem_meV_H": float(np.std(k64 - k32, ddof=1) / np.sqrt(len(q))),
                      "dV_std_eV_per_bead": float(np.std(dv)), "reweighted_shift_meV_H": s,
                      "shift_boot_sigma_meV_H": float(np.std(boot)), "ess": ess})
    shifts.append(np.array([s] + boot))
    g_list.append(pt["g"])
    w_list.append(pt["weight"])
    print(json.dumps(per_point[-1]), flush=True)
g, w = np.array(g_list), np.array(w_list)
dF = np.array([-np.sum(w * 2 * np.array([sh[i] for sh in shifts]) / g) for i in range(len(shifts[0]))])
total, sigma = float(dF[0]), float(np.std(dF[1:]))
bound = abs(total) + 2 * sigma
out = {"control": "C2 float64 re-evaluation of float32 snapshots", "run": run["struct_id"], "P": run["P"],
       "per_point": per_point, "dF_shift_meV_H": total, "dF_shift_sigma_meV_H": sigma, "bound_meV_H": bound,
       "pass": bool(bound < 0.05), "stop_and_reconvene": bool(bound > 0.1), "s_f32_meV_H": max(0.02, bound)}
print(json.dumps({k: v for k, v in out.items() if k != "per_point"}, indent=1))
Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
