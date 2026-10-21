"""Evidence the ranking needs that the screen cannot produce (analysis.py PENDING_EVIDENCE).

From the cached MLIP force constants of every screened (structure, model):
  * relaxed structure -> per pair and model, are the two relaxed phases still distinct? (PLAN.md P5)
  * F_H, F_D recomputed on a denser, Gamma-free (shifted) q-mesh. The screen's Gamma-centred mesh
    drops the three acoustic Gamma modes, which leaves a mass-dependent term of order
    (3/2) w_Gamma kT ln(M_D/M_H) per cell (M01 review); the shifted mesh has no Gamma point.
    numerical_error_meV_atom = max over 0/300/600 K of |ddF_refined - ddF_screen| per atom.

    python -m src.isoshift_event.refine [--workers 6]
writes results/screen_pairs_refined.csv (screen_pairs.csv + identity_checked, numerical_error_meV_atom,
ddF_iso_*K_refined_meV_atom, refined flags) and results/refined_structures.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import lzma
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "raw" / "screen"
CACHE = ROOT / ".cache" / "isoshift"
TEMPS = (0.0, 300.0, 600.0, 2000.0)  # 2000 K only for the classical-limit check
DENSITY = 60.0  # q points per inverse length, screen used 40 (isoshift.phonons.choose_mesh)


def _cache_index():
    idx = {}
    for d in CACHE.iterdir():
        m = d / "meta.json"
        if not m.exists():
            continue
        meta = json.loads(m.read_text())
        calc = d.name.split("__")[1]
        idx[(calc, round(meta["energy_eV"], 6), round(meta["volume_A3"], 4))] = d
    return idx


def _refine_one(args):
    model, sid, raw_path, cache_dir = args
    import phonopy

    from isoshift import phonons as P

    ph = phonopy.load(str(Path(cache_dir) / "phonopy_params.yaml"), produce_fc=False, log_level=0)
    uc = ph.unitcell
    from ase import Atoms

    atoms = Atoms(uc.symbols, cell=uc.cell, scaled_positions=uc.scaled_positions, pbc=True)
    mesh = tuple(int(min(16, max(4, 2 * round(DENSITY / l / 2)))) for l in atoms.cell.lengths())  # even -> no Gamma
    out = {"model": model, "struct_id": sid, "mesh_refined": list(mesh), "n_atoms": len(atoms)}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        mf = P.mesh_frequencies(ph, P.make_masses(atoms, sub, default="light"), mesh, is_gamma_center=False)
        out[f"F_{iso}_meV_atom"] = (np.asarray(mf.helmholtz_free_energy(list(TEMPS))) * 1000 / len(atoms)).tolist()
        # |w| treatment of imaginary modes (decision 02): bracket for soft-mode structures; keeps the
        # classical kT ln(w_D/w_H) cancellation that omitting modes breaks
        ab = P.MeshFreqs(np.abs(mf.freqs), mf.weights, mf.n_atoms)
        out[f"Fabs_{iso}_meV_atom"] = (np.asarray(ab.helmholtz_free_energy(list(TEMPS))) * 1000 / len(atoms)).tolist()
    out["cell"] = np.asarray(uc.cell).tolist()
    out["frac"] = np.asarray(uc.scaled_positions).tolist()
    out["symbols"] = list(uc.symbols)
    return out


def _structure(r):
    from pymatgen.core import Lattice, Structure

    return Structure(Lattice(r["cell"]), r["symbols"], r["frac"])


def _same_phase(ra, rb):
    from pymatgen.analysis.structure_matcher import StructureMatcher
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    sa, sb = _structure(ra), _structure(rb)
    try:
        if SpacegroupAnalyzer(sa, symprec=0.05).get_space_group_number() != SpacegroupAnalyzer(sb, symprec=0.05).get_space_group_number():
            return False
    except Exception:
        pass
    m = StructureMatcher(ltol=0.2, stol=0.15, angle_tol=5, primitive_cell=True, scale=True, attempt_supercell=True)
    return bool(m.fit(sa, sb) or m.fit(sb, sa))


SOFT_MAX_FRACTION = 0.02  # decision 02: imaginary fraction allowed in the bracketed (secondary) tier


def _dd(ra, rb, key):
    return [(rb[f"{key}_D_meV_atom"][i] - rb[f"{key}_H_meV_atom"][i]) - (ra[f"{key}_D_meV_atom"][i] - ra[f"{key}_H_meV_atom"][i])
            for i in range(len(TEMPS))]


def _extended_structures():
    """screen_structures.csv with small soft-mode branches admitted as 'ok' (reason soft_mode_bracketed)."""
    rows = list(csv.DictReader(open(ROOT / "results" / "screen_structures.csv", newline="")))
    soft = set()
    for r in rows:
        try:
            fr = max(float(r["imag_fraction_H"]), float(r["imag_fraction_D"]))
        except (KeyError, ValueError):
            continue
        if r["status"] == "quarantined" and r["reason"].startswith("imaginary_modes") and fr <= SOFT_MAX_FRACTION:
            r["status"] = "ok"
            r["reason"] = r["reason"].replace("imaginary_modes", "soft_mode_bracketed")
            soft.add((r["struct_id"], r["model"]))
    with open(ROOT / "results" / "screen_structures_extended.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return soft


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--screen-pairs", type=Path, default=ROOT / "results" / "screen_pairs.csv")
    args = ap.parse_args(argv)
    idx = _cache_index()
    jobs, unmatched = [], []
    for model_dir in sorted(RAW.iterdir()):
        for f in sorted(model_dir.glob("*.json")):
            r = json.loads(f.read_text())
            if "fc_meta" not in r:
                continue
            calc = "{name}-{model}".format(**r["calc"])
            safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
            key = (safe, round(r["fc_meta"]["energy_eV"], 6), round(r["fc_meta"]["volume_A3"], 4))
            if key in idx:
                jobs.append((model_dir.name, f.stem, str(f), str(idx[key])))
            else:
                unmatched.append(f"{model_dir.name}/{f.stem}")
    with ProcessPoolExecutor(args.workers) as ex:
        refined = {(r["model"], r["struct_id"]): r for r in ex.map(_refine_one, jobs, chunksize=4)}
    with open(ROOT / "results" / "refined_structures.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["struct_id", "model", "mesh_refined", "F_H_300K_meV_atom", "F_D_300K_meV_atom"])
        for (m, s), r in sorted(refined.items()):
            w.writerow([s, m, "x".join(map(str, r["mesh_refined"])), r["F_H_meV_atom"][1], r["F_D_meV_atom"][1]])
    from . import screen

    soft = _extended_structures()
    rows = list(csv.DictReader(open(args.screen_pairs, newline="")))
    n_checked = n_same = n_soft = 0
    for row in rows:
        ra, rb = refined.get((row["model"], row["struct_a"])), refined.get((row["model"], row["struct_b"]))
        if ra is None or rb is None:
            row.update(identity_checked="", numerical_error_meV_atom="")
            continue
        members_soft = [(row[k], row["model"]) in soft for k in ("struct_a", "struct_b")]
        if row.get("ddF_iso_300K_meV_atom") in ("", None):
            if not any(members_soft):
                row.update(identity_checked="", numerical_error_meV_atom="")
                continue
            # pair skipped by the screen because a member was quarantined: compute it the screen's way
            try:
                raw = [json.loads((RAW / row["model"] / f"{row[k]}.json").read_text()) for k in ("struct_a", "struct_b")]
                q = screen.pair_quantities(*raw)
            except (OSError, ValueError, KeyError):
                row.update(identity_checked="", numerical_error_meV_atom="")
                continue
            keep = [f for f in row.get("flags", "").split(";") if f and "missing" not in f and "quarantined" not in f]
            row.update({k: (f"{v:.10g}" if isinstance(v, float) else v) for k, v in q.items() if k != "flags"})
            row["flags"] = ";".join(dict.fromkeys(keep + q["flags"].split(";")))
        same = _same_phase(ra, rb)
        n_checked += 1
        n_same += same
        dd, dda = _dd(ra, rb, "F"), _dd(ra, rb, "Fabs")
        err = max(abs(dd[i] - float(row[f"ddF_iso_{int(t)}K_meV_atom"])) for i, t in enumerate(TEMPS[:3]))
        bracket = max(abs(dda[i] - dd[i]) for i in range(3))
        err = max(err, bracket)
        flags = [f for f in row.get("flags", "").split(";") if f and "identity_unchecked" not in f]
        if same:
            flags.append("same_relaxed_structure")
        if any(members_soft):
            n_soft += 1
            flags.append("soft_mode_bracketed")
            dd = dda  # classical check on the |w| treatment (omitting modes breaks it by construction)
        # ddF must decay as 1/T in the classical limit (M01); growth means omitted (imaginary) modes
        # leave an uncancelled kT ln(w_D/w_H) term, as seen for ORB MgH2 at a larger supercell (G4/F3).
        if abs(dd[3]) > abs(dd[2]) and abs(dd[3]) > 0.01:
            flags.append("classical_limit_violation")
        row.update(identity_checked="true", numerical_error_meV_atom=f"{err:.6g}", flags=";".join(flags),
                   imag_bracket_meV_atom=f"{bracket:.6g}",
                   **{f"ddF_iso_{int(t)}K_refined_meV_atom": f"{dd[i]:.6g}" for i, t in enumerate(TEMPS)})
    fields = list(rows[0].keys())
    for extra in ("identity_checked", "numerical_error_meV_atom", "imag_bracket_meV_atom",
                  *(f"ddF_iso_{int(t)}K_refined_meV_atom" for t in TEMPS)):
        if extra not in fields:
            fields.append(extra)
    with open(ROOT / "results" / "screen_pairs_refined.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, restval="")
        w.writeheader()
        w.writerows(rows)
    print(f"refined {len(refined)} structure-model results ({len(unmatched)} without cache match); "
          f"pairs checked {n_checked} ({n_soft} with a soft-mode member), same relaxed phase {n_same}")


if __name__ == "__main__":
    main()
