"""Independent CPU-only F01 replication; no event-analysis imports.

Run from the repository root with .venv/Scripts/python.exe -B
src/isoshift_event/replicate_f01.py. Only results/replicate_f01.json is written.
The reference CSV is first opened after all independent calculations pass.
"""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""
for _variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_variable] = "1"

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/replicate_f01.json"
MH, MD = 1.00782503, 2.01410178
KB, PLANCK = 8.617333262e-5, 4.135667696e-3
TEMPERATURE = 300.0


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_result(result):
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                      encoding="utf-8")


def index_cache():
    entries = []
    for path in sorted((ROOT / ".cache/isoshift").glob("*/meta.json")):
        if (path.parent / "phonopy_params.yaml").is_file():
            entries.append((path.parent, read_json(path)))
    return entries


def match_cache(raw, entries):
    calc, meta = raw["calc"], raw["fc_meta"]
    calc_id = re.sub(r"[^a-zA-Z0-9_.-]", "_", calc["name"] + "-" + calc["model"])
    matches = []
    for directory, cached in entries:
        if "__" + calc_id + "__" not in directory.name:
            continue
        if (abs(cached.get("energy_eV", math.inf) - meta["energy_eV"]) < 1e-7
                and abs(cached.get("volume_A3", math.inf) - meta["volume_A3"]) < 1e-6
                and cached.get("supercell") == meta.get("supercell")
                and abs(cached.get("displacement", math.inf)
                        - meta["displacement"]) < 1e-10):
            matches.append(directory)
    if len(matches) != 1:
        raise ValueError(f"Expected unique cache match; got {len(matches)}: {calc_id}")
    return matches[0]


def select_rows(count, entries, result):
    """Select without reading reference: smallest eligible cells, balanced models."""
    candidates = {"mace": [], "orb": []}
    sources = {}
    with (ROOT / "results/screen_pairs_refined.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rejected = {}
    for row in rows:
        model = row["model"]
        if model not in candidates or any(flag in row["flags"] for flag in
                                          ("same_relaxed_structure", "soft_mode")):
            continue
        loaded = []
        try:
            for side in ("a", "b"):
                sid = row["struct_" + side]
                key = (model, sid)
                if key not in sources:
                    rawpath = ROOT / f"results/raw/screen/{model}/{sid}.json"
                    raw = read_json(rawpath)
                    directory = match_cache(raw, entries)
                    sources[key] = (raw, directory, rawpath)
                loaded.append(sources[key])
        except (OSError, ValueError, KeyError) as exc:
            rejected[str(exc)] = rejected.get(str(exc), 0) + 1
            continue
        elements = [set(re.findall(r"[A-Z][a-z]?", item[0]["formula"])) for item in loaded]
        if not any({"H", "O"} <= symbols for symbols in elements):
            continue
        size = sum(item[0]["n_atoms"] for item in loaded)
        candidates[model].append((size, row["pair_id"], row))
    result["selection"] = {
        "policy": "ascending combined atom count within each model; alternate mace/orb",
        "eligible_available_by_model": {k: len(v) for k, v in candidates.items()},
        "input_rejection_reasons": rejected,
    }
    for values in candidates.values():
        values.sort(key=lambda item: item[:2])
    selected = []
    for i in range(count):
        model = ("mace", "orb")[i % 2]
        if not candidates[model]:
            raise RuntimeError(f"Insufficient matched eligible rows for balanced selection: {model}")
        selected.append(candidates[model].pop(0)[2])
    return selected, sources


def geometry(ph, np):
    from pymatgen.core import Lattice

    primitive = ph.primitive
    symbols = primitive.symbols
    hydrogens = [i for i, s in enumerate(symbols) if s == "H"]
    heavy = [i for i, s in enumerate(symbols) if s != "H"]
    if hydrogens and not heavy:
        raise ValueError("No non-H atom for stretch definition")
    lattice = Lattice(primitive.cell)
    positions = primitive.scaled_positions
    directions, neighbors = [], []
    for h in hydrogens:
        choices = []
        for j in heavy:
            distance, image = lattice.get_distance_and_image(positions[h], positions[j])
            vector = (positions[j] + image - positions[h]) @ primitive.cell
            choices.append((float(distance), j, vector))
        choices.sort(key=lambda item: (item[0], item[1]))
        distance, j, vector = choices[0]
        if distance < 1e-8:
            raise ValueError("Coincident H and heavy atom")
        directions.append(vector / distance)
        neighbors.append({"H_index": h, "neighbor_index": j, "element": symbols[j],
                          "distance_A": distance, "direction": (vector / distance).tolist(),
                          "next_nearest_gap_A": (choices[1][0] - distance
                                                if len(choices) > 1 else None)})
    return hydrogens, np.asarray(directions).reshape((-1, 3)), neighbors


def mesh_for(cell, density, np):
    # Reciprocal-vector norms handle oblique cells; even midpoint grids omit Gamma.
    inverse = np.linalg.inv(cell).T
    return tuple(max(4, 2 * int(math.ceil(density * length / 2)))
                 for length in np.linalg.norm(inverse, axis=1))


def evaluate_mesh(ph, hydrogens, directions, mesh, np):
    axes = [(np.arange(n) + 0.5) / n - 0.5 for n in mesh]
    q = np.array(np.meshgrid(*axes, indexing="ij")).reshape(3, -1).T
    assert np.all(np.linalg.norm(q, axis=1) > 0)
    ph.run_qpoints(q, with_dynamical_matrices=True)
    base = np.asarray(ph.qpoints.dynamical_matrices)
    conversion = float(ph.unit_conversion_factor)
    n = len(ph.primitive)
    h_dof = np.array([3 * h + k for h in hydrogens for k in range(3)], dtype=int)
    log_ratio = math.log(MD / MH)

    def diagonalize(t):
        scale = np.ones(3 * n)
        scale[h_dof] = math.exp(-t / 2)
        dm = base * scale[None, :, None] * scale[None, None, :]
        eigenvalues, vectors = np.linalg.eigh(dm)
        frequencies = np.sqrt(np.abs(eigenvalues)) * conversion * np.sign(eigenvalues)
        return frequencies, vectors

    # Positive-definite mass congruence preserves inertia. Use a fixed sorted-band
    # mask for both endpoints and all integration nodes; no isotope cutoff jumps.
    light, _ = diagonalize(0.0)
    heavy, _ = diagonalize(log_ratio)
    common = (light > 1e-7) & (heavy > 1e-7)
    if np.any((light > 1e-7) != (heavy > 1e-7)):
        raise RuntimeError("Near-zero branch crosses the numerical threshold")

    def free_energy(freq):
        energy = PLANCK * np.where(common, freq, 1.0)
        terms = energy / 2 + KB * TEMPERATURE * np.log(-np.expm1(-energy / (KB * TEMPERATURE)))
        return float(np.where(common, terms, 0).sum() / len(q) / n * 1000)

    def integral(order):
        nodes, weights = np.polynomial.legendre.leggauss(order)
        answer = np.zeros(2)
        for node, weight in zip(nodes, weights):
            freq, vec = diagonalize((node + 1) * log_ratio / 2)
            if np.any(common & (freq <= 0)):
                raise RuntimeError("Positive branch lost inside mass integration")
            hv = vec[:, h_dof, :].reshape(len(q), len(hydrogens), 3, 3 * n)
            parallel = np.einsum("qhcj,hc->qhj", hv, directions)
            pstr = (np.abs(parallel) ** 2).sum(axis=1)
            phydrogen = (np.abs(hv) ** 2).sum(axis=(1, 2))
            pperp = phydrogen - pstr
            if pperp.min(initial=0) < -1e-10:
                raise RuntimeError("Projection positivity check failed")
            energy = PLANCK * np.where(common, freq, 1.0)
            # dF/dln(m_H) = -1/2 E(n_B+1/2) times H participation.
            kernel = -0.25 * energy / np.tanh(energy / (2 * KB * TEMPERATURE))
            kernel = np.where(common, kernel, 0)
            answer += weight * np.array([(kernel * pstr).sum(), (kernel * pperp).sum()])
        return answer * log_ratio / 2 / len(q) / n * 1000

    coarse, fine = integral(4), integral(8)
    quadrature_error = float(np.max(np.abs(fine - coarse)))
    order = 8
    if quadrature_error > 0.0005:
        refined = integral(16)
        quadrature_error = float(np.max(np.abs(refined - fine)))
        fine, order = refined, 16
    fh, fd = free_energy(light), free_energy(heavy)
    direct = fd - fh
    closure = abs(float(fine.sum()) - direct)
    if max(quadrature_error, closure) > 0.001:
        raise RuntimeError(f"Mass integral not converged: quadrature={quadrature_error}, closure={closure}")
    return {"mesh": list(mesh), "nq": len(q), "F_H_meV_atom": fh, "F_D_meV_atom": fd,
            "dF_direct": direct, "dF_str": float(fine[0]), "dF_perp": float(fine[1]),
            "dF_total": float(fine.sum()), "quadrature_order": order,
            "quadrature_error_meV_atom": quadrature_error, "closure_error_meV_atom": closure,
            "excluded_modes": int((~common).sum()),
            "min_frequency_H_THz": float(light.min()),
            "min_frequency_D_THz": float(heavy.min())}


def calculate_structure(raw, directory, rawpath, tolerance, densities, np, phonopy):
    from ase.data import atomic_masses, atomic_numbers

    yaml = directory / "phonopy_params.yaml"
    ph = phonopy.load(str(yaml), produce_fc=False, log_level=0)
    # Explicit natural-abundance masses, never cached isotope assignments.
    ph.masses = [MH if s == "H" else atomic_masses[atomic_numbers[s]]
                 for s in ph.primitive.symbols]
    hydrogens, directions, neighbors = geometry(ph, np)
    history, stable_steps, previous = [], 0, None
    for density in densities:
        mesh = mesh_for(ph.primitive.cell, density, np)
        if history and list(mesh) == history[-1]["mesh"]:
            continue
        value = evaluate_mesh(ph, hydrogens, directions, mesh, np)
        value["density_A"] = density
        if previous is not None:
            change = max(abs(value[k] - previous[k]) for k in
                         ("dF_direct", "dF_str", "dF_perp", "dF_total"))
            value["mesh_change_meV_atom"] = change
            stable_steps = stable_steps + 1 if change <= tolerance else 0
        history.append(value)
        previous = value
        print(f"  {rawpath.stem}: {mesh}, dF={value['dF_direct']:.7f}, stable={stable_steps}", flush=True)
        # Two consecutive refinements; each structure <= half pair tolerance.
        if stable_steps >= 2:
            break
    if stable_steps < 2:
        raise RuntimeError(f"q convergence not established for {rawpath}: {history[-1]}")
    return {"raw_path": str(rawpath.relative_to(ROOT)), "raw_sha256": digest(rawpath),
            "cache_key": directory.name, "yaml_sha256": digest(yaml),
            "energy_eV": raw["fc_meta"]["energy_eV"],
            "volume_A3": raw["fc_meta"]["volume_A3"],
            "n_atoms_primitive": len(ph.primitive), "n_H": len(hydrogens),
            "nearest_nonH": neighbors, "mesh_history": history, "final": history[-1]}


def compare_at_end(result, np):
    """The sole reference-file access, called after independent phase succeeds."""
    path = ROOT / "results/decompose_pairs.csv"
    with path.open(newline="", encoding="utf-8") as f:
        reference = list(csv.DictReader(f))
    indexed = {}
    for item in reference:
        key = (item["pair_id"], item["model"])
        if key in indexed:
            raise ValueError(f"Duplicate reference row: {key}")
        indexed[key] = item
    fields = {"ddF_total": "ddF_direct", "ddF_str": "ddF_str", "ddF_perp": "ddF_perp"}
    differences, signs = {k: [] for k in fields}, {k: [] for k in fields}
    outliers = []
    for row in result["rows"]:
        ref = indexed.get((row["pair_id"], row["model"]))
        if ref is None:  # conductor patch: pair not in the reference table (excluded there as not clean)
            row["reference"] = None
            continue
        row["reference"] = {key: float(ref[key]) for key in fields.values()}
        row["absolute_difference_meV_atom"] = {}
        row["sign_agreement"] = {}
        for ours, theirs in fields.items():
            error = abs(row[ours] - float(ref[theirs]))
            agreement = bool(np.sign(row[ours]) == np.sign(float(ref[theirs])))
            differences[ours].append(error)
            signs[ours].append(agreement)
            row["absolute_difference_meV_atom"][ours] = error
            row["sign_agreement"][ours] = agreement
        row["absolute_difference_meV_atom"]["ddF_direct"] = abs(row["ddF_direct"] - float(ref["ddF_direct"]))
        if max(row["absolute_difference_meV_atom"].values()) > 0.05:
            structures = [result["structures"][row["model"] + "/" + row["struct_" + s]]
                          for s in ("a", "b")]
            issues = []
            if any(s["final"]["excluded_modes"] for s in structures):
                issues.append("Excluded nonpositive modes: compare imaginary/low-frequency cutoff policies.")
            if any(v["next_nearest_gap_A"] is not None and v["next_nearest_gap_A"] < 1e-4
                   for s in structures for v in s["nearest_nonH"]):
                issues.append("Nearly tied nearest non-H neighbors can change the stretch direction.")
            if row["absolute_difference_meV_atom"]["ddF_total"] <= 0.05:
                issues.append("Total agrees; split discrepancy may reflect endpoint projection versus mass-path integration.")
            else:
                issues.append("Total differs despite independent mesh, quadrature and closure checks; reference mesh/cutoff or cache matching needs investigation.")
            outliers.append({"pair_id": row["pair_id"], "model": row["model"],
                             "differences": row["absolute_difference_meV_atom"],
                             "diagnosis": issues, "diagnosis_status": "hypotheses; reference implementation not inspected"})
    summary = {k: {"max_abs_difference_meV_atom": float(np.max(v)),
                   "median_abs_difference_meV_atom": float(np.median(v)),
                   "sign_agreement_count": sum(signs[k]), "count": len(v),
                   "sign_agreement_fraction": sum(signs[k]) / len(v)}
               for k, v in differences.items()}
    direct = [r["absolute_difference_meV_atom"]["ddF_direct"] for r in result["rows"]]
    summary["ddF_direct"] = {"max_abs_difference_meV_atom": float(np.max(direct)),
                              "median_abs_difference_meV_atom": float(np.median(direct))}
    result["comparison"] = {"reference_sha256": digest(path), "statistics": summary,
                            "outliers_above_0_05_meV_atom": outliers,
                            "sign_policy": "strict sign, including zero; no tolerance relabeling"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=20)
    parser.add_argument("--pair-mesh-tolerance", type=float, default=0.01)
    parser.add_argument("--densities", type=float, nargs="+", default=[24, 36, 48, 64, 80, 104])
    args = parser.parse_args()
    if args.rows < 20 or args.pair_mesh_tolerance <= 0:
        parser.error("At least 20 rows and positive mesh tolerance required")
    if len(args.densities) < 3 or any(b <= a for a, b in zip(args.densities, args.densities[1:])):
        parser.error("Provide at least three strictly increasing mesh densities")
    result = {"status": "running", "started_utc": datetime.now(timezone.utc).isoformat(),
              "method": {"temperature_K": TEMPERATURE, "H_mass_u": MH, "D_mass_u": MD,
                         "other_masses": "ASE natural-abundance atomic_masses",
                         "route": "Gauss-Legendre integration of mass-weighted H parallel/perpendicular projections over ln(m_H)",
                         "derivative": "dF/dln(m_H)=-sum_modes[E*coth(E/(2kT))*P_H/4]",
                         "q_mesh": "full even midpoint grids, reciprocal-vector density, no Gamma, uniform weights",
                         "mesh_densities_A": args.densities,
                         "pair_mesh_tolerance_meV_atom": args.pair_mesh_tolerance,
                         "convergence": "two consecutive distinct refinements per structure, componentwise half pair tolerance",
                         "imaginary_policy": "same sorted-band mask f_H>1e-7 and f_D>1e-7 THz at every mass; exclude all other modes",
                         "stretch": "unit vector from H to nearest periodic non-H atom, fixed relaxed geometry",
                         "normalization": "primitive atom count, each structure separately",
                         "device": "CPU; no ML calculators imported"},
              "structures": {}, "rows": [], "comparison": None}
    write_result(result)
    try:
        import numpy as np
        import phonopy

        result["versions"] = {"numpy": np.__version__, "phonopy": phonopy.__version__,
                              "python": sys.version}
        selected, sources = select_rows(args.rows, index_cache(), result)
        result["selected_rows"] = [{k: r[k] for k in ("pair_id", "model", "struct_a", "struct_b", "flags")}
                                   for r in selected]
        write_result(result)
        for row in selected:
            for side in ("a", "b"):
                key = (row["model"], row["struct_" + side])
                label = "/".join(key)
                if label not in result["structures"]:
                    raw, directory, rawpath = sources[key]
                    result["structures"][label] = calculate_structure(
                        raw, directory, rawpath, args.pair_mesh_tolerance / 2,
                        args.densities, np, phonopy)
                    write_result(result)
            a, b = [result["structures"][row["model"] + "/" + row["struct_" + side]]["final"]
                    for side in ("a", "b")]
            answer = {k: row[k] for k in ("pair_id", "model", "struct_a", "struct_b", "flags")}
            for part in ("direct", "str", "perp", "total"):
                answer["ddF_" + part] = b["dF_" + part] - a["dF_" + part]
            answer["closure_error_meV_atom"] = abs(answer["ddF_total"] - answer["ddF_direct"])
            result["rows"].append(answer)
            print(json.dumps(answer), flush=True)
            write_result(result)
        result["independent_completed_utc"] = datetime.now(timezone.utc).isoformat()
        result["status"] = "independent_complete_before_reference"
        write_result(result)
        compare_at_end(result, np)
        result["status"] = "complete"
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_result(result)
        print(json.dumps(result["comparison"], indent=2), flush=True)
    except Exception as exc:
        result["status"] = "incomplete"
        result["error"] = f"{type(exc).__name__}: {exc}"
        write_result(result)
        raise


if __name__ == "__main__":
    main()
