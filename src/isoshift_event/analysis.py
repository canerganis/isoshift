"""CPU-only ensemble audit of screen CSVs (PLAN P3/P13/P14/P15, accepted M01).

Run ``python -m src.isoshift_event.analysis --top 10`` after screen collect.
Writes results/candidates.csv, INCLUDING rejected and missing pairs; --top only
limits the printed ranking. No workers, downloads, or raw results are modified.
Re-running recomputes from the current snapshot and atomically replaces the CSV.

Ranking is by descending absolute median ddF at 300 K (configurable), with pair
id breaking ties. At least two valid models must agree on a nonzero sign, and
the signal must strictly exceed max(max-min model spread, numerical error, 0.1
meV/atom). Failed/quarantined or inconsistent models cannot be silently omitted
to obtain consensus. Pending models are reported as partial coverage.

Extra pair/model evidence columns: identity_checked=True confirms that the two
relaxed structures remain distinct, and numerical_error_meV_atom supplies the
measured P13 convergence bound. The latter can alternatively be supplied with
--numerical-error-meV-atom, which must be a measured bound for the whole input.
Neither missing evidence nor an identity-unchecked flag is treated as a pass.
Identity cannot be inferred from energies.

Provisional shortlist: the current screen cannot yet produce identity or P13
numerical-error evidence. Pairs that pass every other gate (composition, sign
agreement, model spread and 0.1 meV/atom floor, imaginary modes, convergence,
consistency) get provisional_rank, with the missing evidence listed in
pending_evidence. It is a shortlist for the next checks (QHA, identity), NOT a
P14 ranking; rank stays empty and eligible False until the evidence exists.

Composition: both members must have the same reduced composition (all elements,
not only the H fraction). Evidence comes from a formula column on the screen
structure rows or from the structure manifest (--structures, default
data/isoshift/structures.csv). Missing, conflicting or unequal compositions
reject the pair, and each model's n_atoms/H_count must fit that formula.

Temperatures: 0, 300 and 600 K must be exact points of the free-energy grid.
Values are never interpolated, because harmonic F(T) is not linear in T.

Model capability skips (screen reasons skipped_model_cap_* and
shared_supercell_exceeds_160_atoms) make that model not_applicable for the pair:
it is excluded from n_models_expected and consensus, recorded in flags and
model_results_json, and coverage stays partial. Real failures stay fail-closed.

Per-atom arrays are already normalized by screen; NEVER divide by n_atoms again.
Per-H values divide by H_count/n_atoms, checked for equality between members.
ddF = (F_D - F_H)_b - (F_D - F_H)_a. Pressure sensitivity is
-0.1602176634 * ddF[meV/atom] / dV[A^3/atom], only for |dV| >= 0.1.
No dT is inferred by subtracting the first H and D roots: these CSVs have no mass
path for M01 root matching. Static-offset sensitivity, QHA, mode projections and
accessibility assessment remain unavailable and are explicitly labelled.
Model spread is not a confidence interval or independent experimental evidence.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
from statistics import median
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TEMPERATURES = (0, 300, 600)
DEFAULT_STRUCTURES = ROOT / "data/isoshift/structures.csv"
# Evidence the current screen cannot produce; lacking only these gives a provisional rank.
PENDING_EVIDENCE = frozenset({"identity_unchecked", "numerical_error_unknown"})
CAP_SKIP_PREFIXES = ("skipped_model_cap_", "shared_supercell_exceeds_160_atoms")
CONFLICT = "conflict"
LIMITATIONS = (
    "harmonic_screening_only;shared_bias_PBE_trained_models;"
    "model_spread_not_confidence_interval;mass_path_unavailable;"
    "static_offset_sweep_unavailable;QHA_unavailable;"
    "mode_projection_unavailable;accessibility_unchecked"
)
FIELDS = [
    "pair_id", "rank", "eligible", "rejection_reasons", "provisional_rank",
    "pending_evidence", "formula", "struct_a", "struct_b",
    "source", "tier", "ranking_temperature_K", "n_models_expected", "n_models_valid",
    "models_valid", "coverage", "sign_agreement", "numerical_error_meV_atom",
    "signal_threshold_meV_atom", "signal_abs_meV_atom", "dT_iso_K", "flags",
    "limitations", "model_results_json",
    *(f"ddF_iso_{t}K_{stat}_meV_{unit}" for t in TEMPERATURES for unit in ("atom", "H")
      for stat in ("median", "min", "max", "model_spread")),
    *(f"{prefix}_{stat}_{unit}" for prefix, unit in (("dE_static", "meV_atom"),
                                                   ("dP_iso_300K", "GPa"))
      for stat in ("median", "min", "max", "model_spread")),
]


def _true(value):
    return str(value).strip().lower() in ("true", "1")


def _false(value):
    return str(value).strip().lower() in ("false", "0")


def _number(value):
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ValueError("missing or invalid number") from None
    if not math.isfinite(result):
        raise ValueError("nonfinite number")
    return result


def _flags(row):
    return set(filter(None, str(row.get("flags", "")).split(";")))


def _parse_formula(text):
    """Normalized element fractions of a chemical formula (any multiple of it)."""
    from ase.formula import Formula
    try:
        counts = Formula(str(text).strip()).count()
    except Exception:
        raise ValueError("invalid formula") from None
    counts = {el: c for el, c in counts.items() if c}
    total = sum(counts.values())
    if not counts or total <= 0 or any(c < 0 for c in counts.values()):
        raise ValueError("invalid formula")
    return {el: c/total for el, c in counts.items()}


def _same_composition(x, y):
    return x.keys() == y.keys() and all(math.isclose(x[k], y[k], rel_tol=0, abs_tol=1e-9) for k in x)


def _compositions(screen_structures, manifest):
    """struct_id -> element fractions, or CONFLICT when the evidence disagrees."""
    result = {}
    for row in [*screen_structures, *manifest]:
        sid, text = str(row.get("struct_id", "")).strip(), str(row.get("formula") or "").strip()
        if not sid or not text:
            continue
        try:
            fractions = _parse_formula(text)
        except ValueError:
            result[sid] = CONFLICT
            continue
        known = result.get(sid)
        if known is None:
            result[sid] = fractions
        elif known is CONFLICT or not _same_composition(known, fractions):
            result[sid] = CONFLICT
    return result


def _check_counts(fractions, n, h):
    """A cell of n atoms with h H atoms must be an integer multiple of the formula."""
    if fractions is None or fractions is CONFLICT:
        return  # rejected at pair level
    if not math.isclose(fractions.get("H", 0.), h/n, rel_tol=0, abs_tol=1e-9):
        raise ValueError("composition_count_mismatch")
    if any(abs(f*n - round(f*n)) > 1e-6 for f in fractions.values()):
        raise ValueError("composition_count_mismatch")


def _cap_skip(row):
    return (row is not None and row.get("status") == "quarantined"
            and str(row.get("reason", "")).startswith(CAP_SKIP_PREFIXES))


def _index(rows, keys):
    indexed = {}
    for row in rows:
        key = tuple(str(row.get(k, "")).strip() for k in keys)
        if not all(key):
            raise ValueError(f"missing key: {','.join(keys)}")
        if key in indexed:
            raise ValueError(f"duplicate {','.join(keys)}: {key}")
        indexed[key] = row
    return indexed


def _structure(row):
    """Validate an ok screen row before allowing its arrays into an ensemble."""
    if not _true(row.get("relax_converged")):
        raise ValueError("relax_not_converged")
    for isotope in ("H", "D"):
        if _true(row.get(f"has_imaginary_{isotope}")):
            raise ValueError("imaginary_modes")
        if not _false(row.get(f"has_imaginary_{isotope}")):
            raise ValueError("imaginary_report_missing")
        try:
            frequency = _number(row.get(f"min_freq_THz_{isotope}"))
        except ValueError:
            raise ValueError("imaginary_report_missing") from None
        if frequency < -0.1:
            raise ValueError("imaginary_modes")
    try:
        n, h = _number(row.get("n_atoms")), _number(row.get("H_count"))
        if not (n.is_integer() and h.is_integer() and 0 < h <= n):
            raise ValueError
    except ValueError:
        raise ValueError("invalid_composition") from None
    try:
        temps = np.asarray(json.loads(row["temps_K_json"]), dtype=float)
        curves = {s: np.asarray(json.loads(row[f"F_{s}_meV_atom_json"]), dtype=float)
                  for s in ("H", "D")}
        if (temps.ndim != 1 or len(temps) < 2 or not np.isfinite(temps).all()
                or not (np.diff(temps) > 0).all()
                or any(f.shape != temps.shape or not np.isfinite(f).all()
                       for f in curves.values())):
            raise ValueError
        energy = _number(row.get("E_eV_atom"))
        volume = _number(row.get("V_A3_atom"))
        if volume <= 0:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise ValueError("invalid_thermodynamics") from None
    # Reported temperatures must be grid points: harmonic F(T) is not linear in T.
    indices = {}
    for t in TEMPERATURES:
        hits = np.flatnonzero(temps == t)
        if len(hits) != 1:
            raise ValueError("reported_temperature_not_on_grid")
        indices[t] = int(hits[0])
    return temps, curves, (int(n), int(h)), energy, volume, indices


def _model_result(pair, structures, compositions):
    members = [structures.get((str(pair[side]), str(pair["model"])))
               for side in ("struct_a", "struct_b")]
    reasons = []
    missing = False
    for side, row in zip(("a", "b"), members):
        status = "missing" if row is None else row.get("status", "missing")
        if status != "ok":
            missing |= status == "missing"
            reasons.append(f"{side}_{status}:{row.get('reason', '') if row else 'no_structure_row'}")
    if reasons:
        only_missing = all(row is None or row.get("status") in ("ok", "missing") for row in members)
        # A stale finite pair summary may not silently become a pending model.
        has_summary = any(pair.get(f"ddF_iso_{t}K_meV_atom") not in (None, "") for t in TEMPERATURES)
        # A model that cannot hold the shared supercell never runs this pair; it is
        # not a dissenting model. A real failure on the other member still counts.
        capped = (any(_cap_skip(row) for row in members) and not has_summary and
                  all(row is None or row.get("status") in ("ok", "missing") or _cap_skip(row)
                      for row in members))
        status = ("not_applicable" if capped else
                  "missing" if missing and only_missing and not has_summary else "invalid")
        return dict(status=status, reasons=reasons)
    try:
        ta, fa, (na, nha), ea, va, index = _structure(members[0])
        tb, fb, (nb, nhb), eb, vb, _ = _structure(members[1])
        if not np.array_equal(ta, tb):
            raise ValueError("temperature_grid_mismatch")
        _check_counts(compositions.get(str(pair["struct_a"])), na, nha)
        _check_counts(compositions.get(str(pair["struct_b"])), nb, nhb)
        ha, hb = nha/na, nhb/nb
        if not math.isclose(ha, hb, rel_tol=1e-10, abs_tol=1e-12):
            raise ValueError("invalid_composition")
        delta = (fb["D"] - fb["H"]) - (fa["D"] - fa["H"])
        values = {str(t): float(delta[index[t]]) for t in TEMPERATURES}
        de = 1000*(eb-ea)
        expected = {"dE_static_meV_atom": de}
        for t in TEMPERATURES:
            expected[f"ddF_iso_{t}K_meV_atom"] = values[str(t)]
            expected[f"ddF_iso_{t}K_meV_H"] = values[str(t)]/ha
        for field, value in expected.items():
            try:
                observed = _number(pair.get(field))
            except ValueError:
                raise ValueError("pair_summary_mismatch") from None
            if not math.isclose(value, observed, rel_tol=1e-7, abs_tol=1e-6):
                raise ValueError("pair_summary_mismatch")
        return dict(status="ok", ddF_meV_atom=values,
                    ddF_meV_H={t: v/ha for t, v in values.items()},
                    dE_static_meV_atom=de, dV_A3_atom=vb-va)
    except ValueError as exc:
        return dict(status="invalid", reasons=[str(exc)])


def _config(row):
    """Canonical supercell and temperature grid for cross-model comparisons."""
    try:
        sc = np.asarray(json.loads(row["supercell"]), dtype=float)
        if sc.shape == (3,):
            sc = np.diag(sc)
        if (sc.shape != (3, 3) or not np.isfinite(sc).all()
                or not np.equal(sc, np.round(sc)).all() or np.linalg.det(sc) <= 0):
            raise ValueError
        return (tuple(sc.ravel()), tuple(json.loads(row["temps_K_json"])),
                row.get("input_sha256", ""))
    except (KeyError, TypeError, ValueError):
        return None


def _statistics(row, prefix, unit, values):
    for name, function in (("median", median), ("min", min), ("max", max),
                           ("model_spread", lambda x: max(x)-min(x))):
        row[f"{prefix}_{name}_{unit}"] = float(function(values)) if values else None


def analyze(screen_pairs, screen_structures, *, pairs=None, structures_manifest=None,
            numerical_error_meV_atom=None, temperature=300):
    """Return deterministic audit rows, with rank=None for ineligible pairs.

    Inputs are iterables of dictionaries (csv.DictReader is supported). Optional
    pairs is the pair manifest, preserving pairs with no screen rows yet.
    Optional structures_manifest rows (struct_id, formula) give composition
    evidence. An explicit numerical-error bound is combined conservatively with
    row bounds.
    No inputs are mutated. Unknown evidence fails closed; empty queues are valid.
    """
    if temperature not in TEMPERATURES:
        raise ValueError("temperature must be 0, 300 or 600 K")
    if numerical_error_meV_atom is not None:
        numerical_error_meV_atom = _number(numerical_error_meV_atom)
        if numerical_error_meV_atom < 0:
            raise ValueError("numerical error must be nonnegative")
    screen_structures = list(screen_structures)
    structures_manifest = list(structures_manifest or [])
    observed = _index(screen_pairs, ("pair_id", "model"))
    structures = _index(screen_structures, ("struct_id", "model"))
    manifests = _index(pairs or [], ("pair_id",))
    _index(structures_manifest, ("struct_id",))  # duplicate ids are an input error
    compositions = _compositions(screen_structures, structures_manifest)
    formulas = {str(r.get("struct_id", "")).strip(): str(r.get("formula") or "").strip()
                for r in [*screen_structures, *structures_manifest] if r.get("formula")}
    grouped = {}
    for (pid, model), record in observed.items():
        if not record.get("struct_a") or not record.get("struct_b"):
            raise ValueError(f"missing pair members: {pid}")
        grouped.setdefault(pid, {})[model] = record
    output = []
    for pid in sorted(set(grouped) | {key[0] for key in manifests}):
        records = dict(grouped.get(pid, {}))
        meta = manifests.get((pid,), next(iter(records.values()), {}))
        # Include completed/failed jobs even if a partial/stale pair table omitted
        # their model row. Otherwise a dissenting third model could disappear.
        models = {model for sid, model in structures if sid in (meta.get("struct_a"), meta.get("struct_b"))}
        for model in sorted(models - records.keys()):
            records[model] = dict(pair_id=pid, model=model,
                                  struct_a=meta.get("struct_a"), struct_b=meta.get("struct_b"))
        row = {key: meta.get(key, "") for key in ("formula", "struct_a", "struct_b", "source", "tier")}
        row.update(pair_id=pid, rank=None, eligible=False, ranking_temperature_K=temperature,
                   provisional_rank=None, dT_iso_K=None, limitations=LIMITATIONS)
        flags = _flags(meta) | {"mass_path_unavailable", "accessibility_unchecked"}
        rejected = set()
        results = {}
        bounds = []
        for model, record in sorted(records.items()):
            flags |= _flags(record)
            if any(record.get(key) != meta.get(key) for key in ("struct_a", "struct_b")):
                results[model] = dict(status="invalid", reasons=["pair_members_mismatch"])
            else:
                results[model] = _model_result(record, structures, compositions)
            result = results[model]
            if result["status"] == "not_applicable":
                flags.update(f"{model}:not_applicable:{r}" for r in result["reasons"])
                continue
            if result["status"] != "ok":
                flags.update(f"{model}:{r}" for r in result["reasons"])
                if result["status"] != "missing":
                    rejected.update(f"{model}:{r}" for r in result["reasons"])
                continue
            if (not _true(record.get("identity_checked")) or
                    any("identity_unchecked" in flag for flag in _flags(record))):
                rejected.add("identity_unchecked")
            if any("same_" in flag and "structure" in flag for flag in _flags(record)):
                rejected.add("same_relaxed_structure")
            bound = numerical_error_meV_atom
            if record.get("numerical_error_meV_atom") not in (None, ""):
                try:
                    supplied = _number(record["numerical_error_meV_atom"])
                    if supplied < 0:
                        raise ValueError
                    bound = max(supplied, bound) if bound is not None else supplied
                except ValueError:
                    rejected.add("invalid_numerical_error")
            if bound is None:
                rejected.add("numerical_error_unknown")
            else:
                bounds.append(bound)
            if abs(result["dE_static_meV_atom"]) > 25:
                flags.add(f"{model}:static_gap_gt_25_meV_atom")
        if row["struct_a"] == row["struct_b"]:
            rejected.add("same_input_structure")
        comp_a, comp_b = (compositions.get(str(row[k])) for k in ("struct_a", "struct_b"))
        if comp_a is None or comp_b is None:
            rejected.add("composition_unchecked")
        elif comp_a is CONFLICT or comp_b is CONFLICT:
            rejected.add("composition_evidence_conflict")
        elif not _same_composition(comp_a, comp_b):
            rejected.add("composition_mismatch")
        elif not row["formula"]:
            row["formula"] = formulas.get(str(row["struct_a"]), "")
        row["n_models_expected"] = sum(r["status"] != "not_applicable" for r in results.values())
        valid = {m: r for m, r in results.items() if r["status"] == "ok"}
        row["n_models_valid"] = len(valid)
        row["models_valid"] = ";".join(sorted(valid))
        row["coverage"] = "complete" if records and len(valid) == len(records) else "partial" if valid else "missing"
        if not records:
            flags.add("missing_screen_results")
        if len(valid) < 2:
            rejected.add("insufficient_models")
        for sid in (row["struct_a"], row["struct_b"]):
            configs = [_config(structures[(sid, m)]) for m in valid]
            if configs and (None in configs or len(set(configs)) != 1):
                rejected.add("cross_model_config_mismatch")
        for t in TEMPERATURES:
            for unit in ("atom", "H"):
                values = [r[f"ddF_meV_{unit}"][str(t)] for r in valid.values()]
                _statistics(row, f"ddF_iso_{t}K", f"meV_{unit}", values)
        values = [r["ddF_meV_atom"][str(temperature)] for r in valid.values()]
        row["sign_agreement"] = bool(values) and (all(v > 0 for v in values) or all(v < 0 for v in values))
        if values and not row["sign_agreement"]:
            rejected.add("sign_disagreement")
        row["numerical_error_meV_atom"] = max(bounds) if bounds and len(bounds) == len(valid) else None
        spread = row[f"ddF_iso_{temperature}K_model_spread_meV_atom"]
        threshold = max(0.1, spread or 0., max(bounds, default=0.))
        row["signal_threshold_meV_atom"] = threshold if row["numerical_error_meV_atom"] is not None else None
        signal = abs(median(values)) if values else None
        row["signal_abs_meV_atom"] = signal
        if signal is not None and (signal <= threshold or math.isclose(signal, threshold, rel_tol=1e-12, abs_tol=1e-12)):
            rejected.add("signal_below_threshold")
        _statistics(row, "dE_static", "meV_atom", [r["dE_static_meV_atom"] for r in valid.values()])
        pressures = []
        for model, result in valid.items():
            dv = result["dV_A3_atom"]
            if abs(dv) < 0.1:
                flags.add(f"{model}:pressure_volume_guard")
            else:
                pressures.append(-0.1602176634*result["ddF_meV_atom"]["300"]/dv)
        # Do not publish an ensemble pressure computed from only its convenient members.
        _statistics(row, "dP_iso_300K", "GPa", pressures if len(pressures) == len(valid) else [])
        row["model_results_json"] = json.dumps(results, sort_keys=True, allow_nan=False, separators=(",", ":"))
        row["eligible"] = not rejected
        row["rejection_reasons"] = ";".join(sorted(rejected))
        row["pending_evidence"] = ";".join(sorted(rejected & PENDING_EVIDENCE))
        row["_provisional"] = not (rejected - PENDING_EVIDENCE)
        row["flags"] = ";".join(sorted(flags))
        output.append(row)
    output.sort(key=lambda r: (not r["eligible"], -(r["signal_abs_meV_atom"] or 0.), r["pair_id"]))
    for rank, row in enumerate((r for r in output if r["eligible"]), 1):
        row["rank"] = rank
    shortlist = sorted((r for r in output if r.pop("_provisional")),
                       key=lambda r: (-(r["signal_abs_meV_atom"] or 0.), r["pair_id"]))
    for rank, row in enumerate(shortlist, 1):
        row["provisional_rank"] = rank
    return output


def _read_csv(path, required):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(required).issubset(reader.fieldnames or []):
            raise ValueError(f"{Path(path).name}: missing required columns {', '.join(required)}")
        return list(reader)


def write_candidates(path, rows):
    """Atomic CSV replacement; a failed write leaves the previous output intact."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", delete=False,
                                         dir=path.parent, prefix=path.name+".tmp.") as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--screen-pairs", type=Path, default=ROOT / "results/screen_pairs.csv")
    parser.add_argument("--screen-structures", type=Path, default=ROOT / "results/screen_structures.csv")
    parser.add_argument("--pairs", type=Path, help="Optional pair manifest, also includes unscreened pairs")
    parser.add_argument("--structures", type=Path,
                        help="Structure manifest (struct_id, formula) for the composition check; "
                             "default data/isoshift/structures.csv when it exists")
    parser.add_argument("--output", type=Path, default=ROOT / "results/candidates.csv", help="Full audit CSV")
    parser.add_argument("--top", type=int, default=10, help="Maximum eligible rows printed; CSV is never truncated")
    parser.add_argument("--temperature", type=int, choices=TEMPERATURES, default=300)
    parser.add_argument("--numerical-error-meV-atom", type=float, help="Measured P13 bound applicable to all input pairs")
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error("--top must be positive")
    try:
        manifest = args.structures or (DEFAULT_STRUCTURES if DEFAULT_STRUCTURES.exists() else None)
        sources = ([args.screen_pairs, args.screen_structures] + ([args.pairs] if args.pairs else [])
                   + ([manifest] if manifest else []))
        if args.output.resolve() in [p.resolve() for p in sources]:
            raise ValueError("output must not overwrite an input CSV")
        rows = analyze(
            _read_csv(args.screen_pairs, ("pair_id", "model", "struct_a", "struct_b", "flags")),
            _read_csv(args.screen_structures, ("struct_id", "model", "status", "reason")),
            pairs=_read_csv(args.pairs, ("pair_id", "struct_a", "struct_b")) if args.pairs else None,
            structures_manifest=_read_csv(manifest, ("struct_id", "formula")) if manifest else None,
            numerical_error_meV_atom=args.numerical_error_meV_atom, temperature=args.temperature)
        write_candidates(args.output, rows)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"analysis: {exc}\n")
    eligible = [r for r in rows if r["eligible"]]
    print(f"{len(rows)} pairs; {len(eligible)} eligible; {len(rows)-len(eligible)} unranked. {args.output}")
    print("rank pair_id median_ddF_meV_atom model_spread_meV_atom valid/expected_models")
    for row in eligible[:args.top]:
        print(f"{row['rank']} {row['pair_id']} "
              f"{row[f'ddF_iso_{args.temperature}K_median_meV_atom']:.6g} "
              f"{row[f'ddF_iso_{args.temperature}K_model_spread_meV_atom']:.6g} "
              f"{row['n_models_valid']}/{row['n_models_expected']}")
    if not eligible:
        print("No eligible candidates; see rejection_reasons and flags in the full CSV.")
    if manifest is None:
        print("No structure manifest: every pair is rejected as composition_unchecked.")
    shortlist = sorted((r for r in rows if r["provisional_rank"] is not None),
                       key=lambda r: r["provisional_rank"])
    print(f"PROVISIONAL shortlist, {len(shortlist)} pairs: all gates pass except the listed "
          "pending evidence. Not a P14 ranking.")
    print("provisional_rank pair_id formula median_ddF_meV_atom model_spread_meV_atom "
          "valid/expected_models pending_evidence")
    for row in shortlist[:args.top]:
        print(f"{row['provisional_rank']} {row['pair_id']} {row['formula'] or '-'} "
              f"{row[f'ddF_iso_{args.temperature}K_median_meV_atom']:.6g} "
              f"{row[f'ddF_iso_{args.temperature}K_model_spread_meV_atom']:.6g} "
              f"{row['n_models_valid']}/{row['n_models_expected']} {row['pending_evidence'] or '-'}")
    print("Exploratory harmonic screening; model spread has shared bias and is not experimental validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
