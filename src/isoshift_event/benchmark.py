"""Benchmark universal MLIPs against Togo phonondb (PBEsol) on H/D isotope quantities.

    python -m src.isoshift_event.benchmark run --models mace,orb --device cuda [--limit N]
    python -m src.isoshift_event.benchmark collect

Force constants are mass independent, so H and D phonons come from one set of force constants by
swapping masses. Per H atom (meV in the CSVs): ZPE_H, ZPE_D, dZPE = ZPE_H - ZPE_D,
dF300 = F_H(300 K) - F_D(300 K), and the H-projected mean stretch frequency (modes with H
eigenvector weight > 0.5, weights = q weight * H weight, H masses, cm^-1).
Settings: "a_dftstruct" (MLIP force constants at the DFT structure) and "b_relaxed"
(MLIP-relaxed structure, fmax 1e-3, cell relaxed). DFT NAC is dropped (MLIPs have no Born charges).
Works under .venv (mace, orb) and .venv-sevenn (sevenn, mattersim); only stdlib csv/json + numpy.
"""
from __future__ import annotations

import argparse
import csv
import json
import lzma
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MDR = ROOT / "data" / "isoshift" / "dft_phonons" / "mdr_phonondb"
RAW = ROOT / "results" / "raw" / "benchmark"
OUT = ROOT / "results" / "benchmark"
SETTINGS = ("a_dftstruct", "b_relaxed")
THZ_TO_CM = 33.35640952
EV_TO_MEV = 1000.0
T_REF = 300.0
GAMMA_TOL_THZ = 0.1
IMAG_TOL_THZ = -0.1


# ---------------------------------------------------------------- DFT loading
def entries(limit: int | None = None, only: list[str] | None = None) -> list[str]:
    """phonondb entry ids (mp-xxxx) sorted by unit-cell size (from index.json), smallest first."""
    idx = json.loads((MDR / "index.json").read_text())
    have = {p.parent.name for p in MDR.glob("mp-*/phonopy_params.yaml.xz")}
    rows = [r for r in idx if r["mp_id"] in have]
    if only:
        rows = [r for r in rows if r["mp_id"] in only]
    rows.sort(key=lambda r: (r["nsites"], r["mp_id"]))
    ids = [r["mp_id"] for r in rows]
    return ids[:limit] if limit else ids


def load_dft(entry: str):
    """Load phonopy_params.yaml.xz -> Phonopy (NAC dropped, compact fc)."""
    import phonopy

    raw = lzma.open(MDR / entry / "phonopy_params.yaml.xz").read()
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "phonopy_params.yaml"
        f.write_bytes(raw)
        ph = phonopy.load(str(f), log_level=0, is_nac=False)
    return ph


def unitcell_atoms(ph):
    from ase import Atoms

    u = ph.unitcell
    return Atoms(symbols=list(u.symbols), cell=u.cell, scaled_positions=u.scaled_positions, pbc=True)


def full_force_constants(ph) -> np.ndarray:
    fc = np.asarray(ph.force_constants)
    if fc.shape[0] == fc.shape[1]:
        return fc
    from phonopy.harmonic.force_constants import compact_fc_to_full_fc

    return compact_fc_to_full_fc(ph.primitive, fc)


# ---------------------------------------------------------------- isotope quantities
def _phonopy(atoms, supercell, masses, fc):
    from isoshift.phonons import _pa
    from phonopy import Phonopy

    p = Phonopy(_pa(atoms.get_chemical_symbols(), atoms.cell.array, atoms.get_scaled_positions(), masses),
                supercell_matrix=np.array(supercell), primitive_matrix="P", symprec=1e-4, log_level=0)
    p.force_constants = np.array(fc)
    return p


def isotope_quantities(atoms, supercell, fc, mesh, T: float = T_REF, sub_h="D") -> dict:
    """ZPE/F/stretch per H atom from full force constants `fc` on `atoms` (unit cell) and q-mesh.

    `sub_h` is the mass label for the 'D' side; pass "H" for an identical-mass control
    (the difference is then exactly zero)."""
    from isoshift.phonons import MeshFreqs, make_masses

    syms = np.array(atoms.get_chemical_symbols())
    is_h = syms == "H"
    n_h = int(is_h.sum())
    if n_h == 0:
        raise ValueError("no H in structure")
    mH = make_masses(atoms, {"H": "H"}, default="light")
    mD = make_masses(atoms, {"H": sub_h}, default="light")

    def run(masses, eig):
        p = _phonopy(atoms, supercell, masses, fc)
        p.run_mesh(list(mesh), with_eigenvectors=eig, is_mesh_symmetry=True, is_gamma_center=True)
        m = p.mesh
        mf = MeshFreqs(np.array(m.frequencies), np.array(m.weights, dtype=float), len(p.unitcell))
        return mf, (np.array(m.eigenvectors) if eig else None)

    fH, ev = run(mH, True)
    fD, _ = run(mD, False)
    # H weight of each mode: sum over H atoms of |e_i|^2 (phonopy eigenvectors: columns are modes)
    nb = fH.freqs.shape[1]
    w_atom = (np.abs(ev) ** 2).reshape(ev.shape[0], len(atoms), 3, nb).sum(axis=2)  # (nq, N, nb)
    hw = w_atom[:, is_h, :].sum(axis=1)  # (nq, nb)
    sel = (hw > 0.5) & (fH.freqs > GAMMA_TOL_THZ)
    wt = fH.weights[:, None] * hw * sel
    stretch = float((wt * fH.freqs).sum() / wt.sum() * THZ_TO_CM) if wt.sum() > 0 else float("nan")
    zH, zD = fH.zpe(), fD.zpe()
    FH, FD = float(fH.helmholtz_free_energy(T)[0]), float(fD.helmholtz_free_energy(T)[0])
    return {
        "n_H": n_h,
        "zpe_H_meV": zH / n_h * EV_TO_MEV, "zpe_D_meV": zD / n_h * EV_TO_MEV,
        "dzpe_meV": (zH - zD) / n_h * EV_TO_MEV,
        "dF300_meV": (FH - FD) / n_h * EV_TO_MEV,
        "stretch_cm1": stretch, "stretch_mode_frac": float(sel.sum() / sel.size),
        "min_freq_THz": fH.min_freq, "has_imaginary": bool(fH.freqs.min() < IMAG_TOL_THZ),
    }


def dft_record(entry: str, mesh=None) -> tuple[dict, dict]:
    ph = load_dft(entry)
    atoms = unitcell_atoms(ph)
    sc = np.array(ph.supercell_matrix)
    if mesh is None:
        from isoshift.phonons import choose_mesh

        mesh = choose_mesh(atoms, density=30.0)
    fc = full_force_constants(ph)
    q = isotope_quantities(atoms, sc, fc, mesh)
    ctx = {"atoms": atoms, "supercell": sc, "mesh": tuple(int(x) for x in mesh), "ph": ph}
    return q, ctx


# ---------------------------------------------------------------- MLIP run
def mlip_quantities(atoms, calc, calc_id, supercell, mesh) -> tuple[dict, dict]:
    from isoshift.phonons import get_force_constants

    ph, meta, _ = get_force_constants(atoms, calc, calc_id, supercell=supercell, use_cache=False)
    fc = np.array(ph.force_constants)
    if fc.shape[0] != fc.shape[1]:
        fc = full_force_constants(ph)
    return isotope_quantities(atoms, supercell, fc, mesh), meta


def raw_path(entry, model, setting) -> Path:
    return RAW / f"{entry}__{model}__{setting}.json"


def run_one(entry, model, setting, calc, dft_q, ctx, device) -> dict:
    from isoshift.relax import relax

    atoms, sc = ctx["atoms"], ctx["supercell"]
    diag = np.count_nonzero(sc - np.diag(np.diag(sc))) == 0
    rec = {"entry": entry, "model": model, "setting": setting, "formula": atoms.get_chemical_formula(),
           "n_atoms_cell": len(atoms), "supercell": np.diag(sc).tolist() if diag else sc.tolist(),
           "mesh": list(ctx["mesh"]), "device": device, "dft": dft_q}
    if setting == "b_relaxed":
        a, info = relax(atoms, calc, fmax=1e-3, steps=500, relax_cell=True)
        rec["relax"] = info
        rec["volume_ratio"] = float(a.get_volume() / atoms.get_volume())
    else:
        a = atoms
    q, meta = mlip_quantities(a, calc, f"bench-{model}-{setting}", sc, ctx["mesh"])
    rec["mlip"] = q
    rec["n_displacements"] = meta.get("n_displacements")
    return rec


def run(models, device, limit=None, only=None):
    from isoshift.calculators import get_calculator

    RAW.mkdir(parents=True, exist_ok=True)
    ids = entries(limit, only)
    for model in models:
        calc = None
        for entry in ids:
            todo = [s for s in SETTINGS if not raw_path(entry, model, s).exists()]
            if not todo:
                continue
            try:
                dft_q, ctx = dft_record(entry)
                if calc is None:
                    calc = get_calculator(model, device)
                for s in todo:
                    rec = run_one(entry, model, s, calc, dft_q, ctx, device)
                    tmp = raw_path(entry, model, s).with_suffix(".tmp")
                    tmp.write_text(json.dumps(rec, indent=1))
                    tmp.replace(raw_path(entry, model, s))
                    print(f"{entry} {model} {s}: dZPE/H dft {dft_q['dzpe_meV']:.2f} mlip {rec['mlip']['dzpe_meV']:.2f} meV; "
                          f"stretch dft {dft_q['stretch_cm1']:.0f} mlip {rec['mlip']['stretch_cm1']:.0f} cm-1", flush=True)
            except Exception as e:  # keep going; failed runs are retried on the next invocation
                err = RAW / f"{entry}__{model}__error.json"
                err.write_text(json.dumps({"entry": entry, "model": model, "error": repr(e),
                                           "trace": traceback.format_exc()}, indent=1))
                print(f"{entry} {model}: ERROR {e!r}", flush=True)


# ---------------------------------------------------------------- collect
ROW_FIELDS = ["entry", "formula", "model", "setting", "n_H", "n_atoms_cell", "supercell", "mesh",
              "zpe_H_dft_meV", "zpe_H_mlip_meV", "zpe_D_dft_meV", "zpe_D_mlip_meV",
              "dzpe_dft_meV", "dzpe_mlip_meV", "dzpe_err_meV",
              "dF300_dft_meV", "dF300_mlip_meV", "dF300_err_meV",
              "stretch_dft_cm1", "stretch_mlip_cm1", "stretch_err_cm1",
              "min_freq_dft_THz", "min_freq_mlip_THz", "imag_dft", "imag_mlip", "volume_ratio", "relax_converged"]


def _row(r: dict) -> dict:
    d, m = r["dft"], r["mlip"]
    return {
        "entry": r["entry"], "formula": r.get("formula"), "model": r["model"], "setting": r["setting"],
        "n_H": d["n_H"], "n_atoms_cell": r.get("n_atoms_cell"),
        "supercell": "x".join(map(str, np.ravel(r["supercell"]))), "mesh": "x".join(map(str, r["mesh"])),
        "zpe_H_dft_meV": d["zpe_H_meV"], "zpe_H_mlip_meV": m["zpe_H_meV"],
        "zpe_D_dft_meV": d["zpe_D_meV"], "zpe_D_mlip_meV": m["zpe_D_meV"],
        "dzpe_dft_meV": d["dzpe_meV"], "dzpe_mlip_meV": m["dzpe_meV"], "dzpe_err_meV": m["dzpe_meV"] - d["dzpe_meV"],
        "dF300_dft_meV": d["dF300_meV"], "dF300_mlip_meV": m["dF300_meV"],
        "dF300_err_meV": m["dF300_meV"] - d["dF300_meV"],
        "stretch_dft_cm1": d["stretch_cm1"], "stretch_mlip_cm1": m["stretch_cm1"],
        "stretch_err_cm1": m["stretch_cm1"] - d["stretch_cm1"],
        "min_freq_dft_THz": d["min_freq_THz"], "min_freq_mlip_THz": m["min_freq_THz"],
        "imag_dft": d["has_imaginary"], "imag_mlip": m["has_imaginary"],
        "volume_ratio": r.get("volume_ratio", ""), "relax_converged": r.get("relax", {}).get("converged", ""),
    }


def _stats(vals):
    v = np.array([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    if v.size == 0:
        return float("nan"), float("nan")
    return float(np.abs(v).mean()), float(v.mean())


def collect(raw=RAW, out=OUT) -> Path:
    raw, out = Path(raw), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in sorted(raw.glob("*.json")):
        if f.name.endswith("__error.json"):
            continue
        rows.append(_row(json.loads(f.read_text())))
    with open(out / "isotope_benchmark.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ROW_FIELDS)
        w.writeheader()
        w.writerows(rows)
    groups: dict = {}
    for r in rows:
        groups.setdefault((r["model"], r["setting"]), []).append(r)
    cols = ["model", "setting", "n", "n_imag_mlip", "n_imag_dft", "dzpe_MAE_meV", "dzpe_bias_meV",
            "dF300_MAE_meV", "dF300_bias_meV", "stretch_MAE_cm1", "stretch_bias_cm1"]
    with open(out / "summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for (model, setting), g in sorted(groups.items()):
            a1, b1 = _stats([x["dzpe_err_meV"] for x in g])
            a2, b2 = _stats([x["dF300_err_meV"] for x in g])
            a3, b3 = _stats([x["stretch_err_cm1"] for x in g])
            w.writerow({"model": model, "setting": setting, "n": len(g),
                        "n_imag_mlip": sum(bool(x["imag_mlip"]) for x in g),
                        "n_imag_dft": sum(bool(x["imag_dft"]) for x in g),
                        "dzpe_MAE_meV": a1, "dzpe_bias_meV": b1, "dF300_MAE_meV": a2, "dF300_bias_meV": b2,
                        "stretch_MAE_cm1": a3, "stretch_bias_cm1": b3})
    return out / "summary.csv"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="benchmark")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--models", default="mace,orb,sevenn,mattersim")
    r.add_argument("--device", default="cuda")
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--entries", default=None, help="comma separated mp ids")
    sub.add_parser("collect")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run([m.strip() for m in a.models.split(",") if m.strip()], a.device, a.limit,
            a.entries.split(",") if a.entries else None)
    else:
        print(collect())


if __name__ == "__main__":
    main()
