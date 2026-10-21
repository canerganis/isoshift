"""Deterministic, source-traceable H/D polymorph candidates (CPU only).

Run from the repository root with ``python -m src.isoshift_event.pairs``.
Inputs are local snapshots; no API, credentials, MLIP, or network is used.
``--output-dir`` supports isolated validation without touching production CIFs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from importlib.metadata import version
from itertools import combinations
from pathlib import Path

import numpy as np
from ase.io import read as ase_read
from pymatgen.analysis.structure_matcher import ElementComparator, StructureMatcher
from pymatgen.core import Composition, Structure
from pymatgen.io.cif import CifWriter
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "isoshift"
PRIMITIVE_TOL = 0.01  # Angstrom; 0.1 folded real superstructures (0.04 to 0.1 A distortions) into averaged cells
MATCH_SETTINGS = {
    "ltol": 0.2,
    "stol": 0.15,  # pymatgen default 0.3 merged distinct H-ordering polymorphs
    "angle_tol": 5.0,
    "primitive_cell": False,
    "scale": True,
    "attempt_supercell": False,
    "allow_subset": False,
}
HULL_REFERENCE_TOL = 1e-5  # eV/atom
CUT_MEV = 25.0
CUT_EPS = 1e-8  # meV/atom; only absorbs floating-point subtraction noise
PRE_EVENT_IDS = frozenset(
    {
        "JVASP-12557",
        "JVASP-2002",
        "JVASP-29869",
        "JVASP-3687",
        "JVASP-4119",
        "JVASP-54676",
        "JVASP-54695",
    }
)
STRUCTURE_FIELDS = (
    "struct_id",
    "source",
    "formula",
    "spg",
    "nsites",
    "cif",
    "e_source_eV_atom",
    "e_kind",
)
PAIR_FIELDS = (
    "pair_id",
    "formula",
    "struct_a",
    "struct_b",
    "source",
    "dE_meV_atom",
    "nsites_a",
    "nsites_b",
    "tier",
    "flags",
    "energy_id_a",
    "energy_id_b",
    "energy_a_eV_atom",
    "energy_b_eV_atom",
    "energy_kind",
    "functional",
)


def make_matcher() -> StructureMatcher:
    """Use on primitive, element-only structures, as returned in BuildResult."""
    return StructureMatcher(comparator=ElementComparator(), **MATCH_SETTINGS)


MERGE_SYMPREC = 0.05  # Angstrom; structures with different space groups at this precision are never merged
_SPG_CACHE: dict[int, int] = {}


def _spg(crystal: Structure) -> int:
    key = id(crystal)
    if key not in _SPG_CACHE:
        try:
            _SPG_CACHE[key] = SpacegroupAnalyzer(crystal, symprec=MERGE_SYMPREC).get_space_group_number()
        except Exception:
            _SPG_CACHE[key] = 0
    return _SPG_CACHE[key]


def _matches(matcher: StructureMatcher, a: Structure, b: Structure) -> bool:
    # Symmetry-distinct H orderings (e.g. delta-AlOOH Pnnm vs P2_1nm) are different phases for
    # isotope physics even when StructureMatcher would fit them, so a space-group mismatch blocks a merge.
    if _spg(a) != _spg(b):
        return False
    # fit() can be asymmetric near a tolerance boundary. Merging on either
    # direction ensures no surviving representatives match in either order.
    return matcher.fit(a, b) or matcher.fit(b, a)


def pair_tier(nsites_a: int, nsites_b: int) -> int | None:
    largest = max(nsites_a, nsites_b)
    return 16 if largest <= 16 else 32 if largest <= 32 else None


def _id_key(sid: str) -> tuple:
    return (0 if sid.startswith("mp-") else 1, int(sid.rsplit("-", 1)[1]))


def _finite(value) -> float | None:
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _formula(structure: Structure) -> str:
    # Neither source's pretty formula is used for equality or grouping.
    return structure.composition.element_composition.reduced_formula


@dataclass
class Entry:
    sid: str
    source: str
    crystal: Structure
    energy: float
    provenance_energy: float
    hull: float | None
    functional: str
    theoretical: bool = False

    @property
    def formula(self) -> str:
        return _formula(self.crystal)


@dataclass
class BuildResult:
    structures: list[dict] = field(default_factory=list)
    pairs: list[dict] = field(default_factory=list)
    crystals: dict[str, Structure] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)
    counts: Counter = field(default_factory=Counter)
    examples: dict[str, list[str]] = field(default_factory=dict)
    functionals: Counter = field(default_factory=Counter)
    validation: dict[str, dict] = field(default_factory=dict)
    input_hashes: dict[str, str] = field(default_factory=dict)
    cache_hits: int = 0  # Deliberately omitted from deterministic reports.

    def example(self, reason: str, text: str) -> None:
        examples = self.examples.setdefault(reason, [])
        if len(examples) < 5:
            examples.append(text)


def _load_entries(mp_rows, jarvis_rows, result: BuildResult) -> list[Entry]:
    entries = []
    seen = set()
    for source, rows in (("mp", mp_rows), ("jarvis", jarvis_rows)):
        id_field = "mp_id" if source == "mp" else "jid"
        for row in sorted(rows, key=lambda r: _id_key(str(r[id_field]))):
            result.counts[f"{source}_read"] += 1
            sid = str(row[id_field])
            pattern = r"mp-\d+" if source == "mp" else r"JVASP-\d+"
            if not re.fullmatch(pattern, sid) or sid in seen:
                raise ValueError(f"Invalid or repeated source ID: {sid!r}")
            seen.add(sid)
            passed_composition = False
            try:
                if source == "mp":
                    crystal = Structure.from_dict(row["structure"])
                    elements = {e.symbol for e in crystal.composition.elements}
                else:
                    atoms = row["atoms"]
                    elements = set(atoms["elements"])
                if "H" not in elements or "C" in elements:
                    result.counts[f"{source}_excluded_composition"] += 1
                    continue
                result.counts[f"{source}_h_no_c"] += 1
                passed_composition = True
                if source == "jarvis":
                    cartesian = atoms["cartesian"]
                    if not isinstance(cartesian, (bool, np.bool_)):
                        raise ValueError("cartesian must be a boolean")
                    crystal = Structure(
                        atoms["lattice_mat"],
                        atoms["elements"],
                        atoms["coords"],
                        coords_are_cartesian=bool(cartesian),
                    )
                if not crystal.is_ordered:
                    result.counts[f"{source}_partial_occupancy"] += 1
                    result.example("partial occupancy", sid)
                    continue
                if (
                    not len(crystal)
                    or not np.isfinite(crystal.frac_coords).all()
                    or not (math.isfinite(crystal.volume) and crystal.volume > 0)
                ):
                    raise ValueError("empty or nonfinite crystal")
            except (ValueError, TypeError, KeyError) as exc:
                # Data defects are counted; matcher/symmetry failures later are fatal.
                result.counts[f"{source}_invalid_structure"] += 1
                stage = "after" if passed_composition else "before"
                result.counts[f"{source}_invalid_{stage}_composition"] += 1
                result.example("invalid structure", f"{sid}: {exc}")
                continue
            result.counts[f"{source}_ordered"] += 1
            crystal.remove_oxidation_states()
            # Magnetic moments/site metadata are not crystallographic identities.
            crystal = Structure(
                crystal.lattice,
                [s.specie.symbol for s in crystal],
                crystal.frac_coords,
                to_unit_cell=True,
            )
            if source == "mp":
                energy = _finite(row.get("e_form_eV"))
                provenance = _finite(row.get("e_per_atom_eV"))
                hull = _finite(row.get("e_hull_eV"))
                functional = "MP corrected mixed thermodynamics"
            else:
                functional = str(row.get("func", "missing"))
                result.functionals[functional] += 1
                # The cached formation-energy column is specifically OptB88vdW.
                if re.sub(r"[^a-z0-9]", "", functional.lower()) != "optb88vdw":
                    result.counts["jarvis_untrusted_functional"] += 1
                    result.example(
                        "untrusted JARVIS functional", f"{sid}: {functional}"
                    )
                    continue
                functional = "OptB88vdW"
                energy = provenance = _finite(row.get("formation_energy_peratom"))
                hull = None
            if (
                energy is None
                or provenance is None
                or (source == "mp" and hull is None)
            ):
                result.counts[f"{source}_missing_energy"] += 1
                result.example("missing/nonfinite energy", sid)
                continue
            entries.append(
                Entry(
                    sid,
                    source,
                    crystal,
                    energy,
                    provenance,
                    hull,
                    functional,
                    source == "mp" and row.get("theoretical") is True,
                )
            )
            result.counts[f"{source}_energy_eligible"] += 1
    return entries


def _primitive(crystal: Structure) -> Structure:
    primitive = crystal.get_primitive_structure(tolerance=PRIMITIVE_TOL)
    primitive = primitive.get_reduced_structure().get_sorted_structure()
    return Structure(
        primitive.lattice,
        [s.specie.symbol for s in primitive],
        primitive.frac_coords,
        to_unit_cell=True,
    )


def _json_bytes(value) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == content:
        return
    # Each interrupted run leaves all completed composition caches usable.
    fd, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _cache_salt() -> str:
    versions = "|".join(
        f"{name}={version(name)}" for name in ("pymatgen", "spglib", "numpy")
    )
    return hashlib.sha256(Path(__file__).read_bytes() + versions.encode()).hexdigest()


def _deduplicate_group(entries: list[Entry], cache_dir: Path | None, salt: str):
    """Greedy representatives; never group by space group or database formula.

    Compare only equal primitive atom counts: with primitive_cell=False and
    attempt_supercell=False the matcher cannot fit unequal counts. Representatives
    are selected by source, then source energy, then numeric ID. This deliberately
    avoids transitive chains of approximate matches merging distant structures.
    """
    cache_path = None
    if cache_dir is not None:
        payload = [
            {
                "sid": e.sid,
                "source": e.source,
                "energy": e.energy,
                "crystal": e.crystal.as_dict(),
            }
            for e in sorted(entries, key=lambda e: _id_key(e.sid))
        ]
        key = hashlib.sha256(salt.encode() + _json_bytes(payload)).hexdigest()
        cache_path = cache_dir / (key + ".json")
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached["key"] != key or set(cached["aliases"]) != {
                e.sid for e in entries
            }:
                raise ValueError("stale cache")
            crystals = {
                sid: Structure.from_dict(s) for sid, s in cached["crystals"].items()
            }
            if set(crystals) != {e.sid for e in entries}:
                raise ValueError("incomplete cache")
            return crystals, cached["aliases"], cached["within"], cached["counts"], True
        except (OSError, ValueError, KeyError, TypeError):
            pass
    crystals = {e.sid: _primitive(e.crystal) for e in entries}
    matcher = make_matcher()
    within, aliases, counts = {}, {}, {}
    representatives = {}
    for source in ("mp", "jarvis"):
        buckets = defaultdict(list)
        representatives[source] = []
        for entry in sorted(
            (e for e in entries if e.source == source),
            key=lambda e: (e.energy, _id_key(e.sid)),
        ):
            crystal = crystals[entry.sid]
            match = next(
                (
                    sid
                    for sid in buckets[len(crystal)]
                    if _matches(matcher, crystal, crystals[sid])
                ),
                None,
            )
            if match is None:
                match = entry.sid
                buckets[len(crystal)].append(match)
                representatives[source].append(match)
            within[entry.sid] = match
        counts[source] = len(representatives[source])
    mp_buckets = defaultdict(list)
    for sid in representatives["mp"]:
        mp_buckets[len(crystals[sid])].append(sid)
        aliases[sid] = sid
    for sid in representatives["jarvis"]:
        matches = (
            mp_sid
            for mp_sid in mp_buckets[len(crystals[sid])]
            if _matches(matcher, crystals[sid], crystals[mp_sid])
        )
        aliases[sid] = next(matches, sid)
    aliases = {sid: aliases[representative] for sid, representative in within.items()}
    if cache_path is not None:
        _atomic_write(
            cache_path,
            _json_bytes(
                {
                    "key": key,
                    "aliases": aliases,
                    "within": within,
                    "counts": counts,
                    "crystals": {sid: s.as_dict() for sid, s in crystals.items()},
                }
            ),
        )
    return crystals, aliases, within, counts, False


def structure_flags(crystal: Structure) -> set[str]:
    """Conservative screening labels, not a determination of proton dynamics."""
    reduced = crystal.composition.element_composition.reduced_composition
    elements = {e.symbol for e in reduced.elements}
    flags = set()
    if (
        reduced == Composition("H2O").reduced_composition
        or any(
            reduced == Composition(f"{metal}OH").reduced_composition
            for metal in ("Li", "Na", "K", "Rb", "Cs")
        )
        or (
            "N" in elements
            and reduced["H"] >= 4 * reduced["N"]
            and bool(elements & {"F", "Cl", "Br", "I"})
        )
    ):
        flags.add("hbond_disordered")
    if ("H" in elements and "O" in elements and bool(elements & {"P", "S"})) or any(
        reduced == Composition(f"{metal}HO2").reduced_composition
        for metal in ("Al", "Ga", "In", "Fe")
    ):
        flags.add("proton_transfer")
    for site in crystal:
        if site.specie.symbol != "H":
            continue
        neighbors = crystal.get_neighbors(site, 1.6)
        if any(
            n.specie.symbol == "H" and 0.55 <= n.nn_distance <= 1.0 for n in neighbors
        ):
            flags.add("molecular_h2")
        donors = sorted(
            (
                n
                for n in neighbors
                if n.specie.symbol in {"O", "N", "F"} and n.nn_distance > 0.1
            ),
            key=lambda n: n.nn_distance,
        )
        if len(donors) >= 2:
            v1, v2 = (donors[i].coords - site.coords for i in (0, 1))
            cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            if cosine <= math.cos(math.radians(150)):
                flags.add("proton_transfer")
    return flags


def build_pairs(
    mp_rows, jarvis_rows, *, cache_dir: Path | None = None, baseline_rows=None
) -> BuildResult:
    """Curate already-loaded rows; no output files except optional .cache entries.

    MP summary formation energies are corrected thermodynamic quantities. At a
    fixed composition, E_form - E_hull must give one common hull reference. Reject
    comparisons for a composition if this consistency check fails; never fall
    back to uncorrected raw totals or JARVIS ehull.
    """
    result = BuildResult()
    entries = _load_entries(mp_rows, jarvis_rows, result)
    by_id = {entry.sid: entry for entry in entries}
    by_formula = defaultdict(list)
    for entry in entries:
        by_formula[entry.formula].append(entry)
    crystals = {}
    salt = _cache_salt() if cache_dir is not None else ""
    cache_dir = Path(cache_dir) if cache_dir is not None else None
    if cache_dir is not None and ".cache" not in cache_dir.parts:
        raise ValueError("Intermediate caches must be under a .cache directory")
    eligible_pairs = []
    for formula, group in sorted(by_formula.items()):
        prims, aliases, within, counts, hit = _deduplicate_group(group, cache_dir, salt)
        result.cache_hits += int(hit)
        crystals.update(prims)
        result.aliases.update(aliases)
        for source in ("mp", "jarvis"):
            result.counts[f"{source}_within_unique"] += counts[source]
            duplicates = [
                e for e in group if e.source == source and within[e.sid] != e.sid
            ]
            result.counts[f"{source}_within_duplicates"] += len(duplicates)
            for entry in duplicates:
                result.example(
                    "within-source duplicate",
                    f"{entry.sid} -> {within[entry.sid]} ({formula})",
                )
        unique = set(aliases.values())
        result.counts["cross_unique"] += len(unique)
        result.counts["cross_merges"] += sum(counts.values()) - len(unique)
        result.counts["compositions"] += 1
        result.counts["multi_structure_compositions"] += int(len(unique) >= 2)
        for sid in sorted(set(within.values()), key=_id_key):
            if aliases[sid] != sid:
                result.example(
                    "cross-source duplicate", f"{sid} -> {aliases[sid]} ({formula})"
                )
        mp_group = [e for e in group if e.source == "mp"]
        references = [e.energy - e.hull for e in mp_group]
        consistent = (
            not references or max(references) - min(references) <= HULL_REFERENCE_TOL
        )
        if not consistent:
            result.counts["mp_inconsistent_reference_compositions"] += 1
            result.example(
                "inconsistent MP hull reference",
                f"{formula}: spread "
                f"{1000 * (max(references) - min(references)):.6g} meV/atom; "
                + ", ".join(e.sid for e in mp_group),
            )
        group_stats = Counter()
        for source in ("mp", "jarvis"):
            # One energy per phase per database. Lowest source energy wins;
            # duplicate calculations must not create alternative near-cut gaps.
            phase_entries = {}
            for entry in sorted(
                (e for e in group if e.source == source),
                key=lambda e: (e.energy, _id_key(e.sid)),
            ):
                phase_entries.setdefault(aliases[entry.sid], entry)
            result.counts[f"{source}_phase_representatives"] += len(phase_entries)
            for (sid_a, a), (sid_b, b) in combinations(phase_entries.items(), 2):
                result.counts["candidate_pairs"] += 1
                result.counts[f"{source}_candidate_pairs"] += 1
                group_stats["candidate_pairs"] += 1
                if source == "mp" and not consistent:
                    result.counts["pairs_untrusted_mp_reference"] += 1
                    group_stats["untrusted_reference"] += 1
                    continue
                gap = (b.energy - a.energy) * 1000
                if gap > CUT_MEV + CUT_EPS:
                    result.counts["pairs_above_25_meV"] += 1
                    band = (
                        "pairs_25_to_50_meV"
                        if gap <= 50 + CUT_EPS
                        else "pairs_above_50_meV"
                    )
                    result.counts[band] += 1
                    group_stats[band] += 1
                    result.example(
                        "energy cut",
                        f"{a.sid} / {b.sid} ({formula}): {gap:.9g} meV/atom",
                    )
                    continue
                result.counts["pairs_after_energy_cut"] += 1
                result.counts[f"{source}_pairs_after_energy_cut"] += 1
                group_stats["after_energy_cut"] += 1
                tier = pair_tier(len(prims[sid_a]), len(prims[sid_b]))
                if tier is None:
                    result.counts["pairs_oversized"] += 1
                    group_stats["oversized"] += 1
                    result.example(
                        "primitive cell >32 atoms",
                        f"{sid_a} / {sid_b} ({formula}): "
                        f"{len(prims[sid_a])}, {len(prims[sid_b])}",
                    )
                    continue
                result.counts["pairs_after_size_cut"] += 1
                # Sorting phase_entries above makes a lower-energy; tie by source ID.
                pair_id = "__".join(sorted((sid_a, sid_b), key=_id_key))
                eligible_pairs.append(
                    {
                        "pair_id": pair_id,
                        "formula": formula,
                        "struct_a": sid_a,
                        "struct_b": sid_b,
                        "source": source,
                        "dE_meV_atom": min(CUT_MEV, max(0.0, gap)),
                        "nsites_a": len(prims[sid_a]),
                        "nsites_b": len(prims[sid_b]),
                        "tier": tier,
                        "flags": "",
                        "energy_id_a": a.sid,
                        "energy_id_b": b.sid,
                        "energy_a_eV_atom": a.energy,
                        "energy_b_eV_atom": b.energy,
                        "energy_kind": "mp_corrected_formation"
                        if source == "mp"
                        else "jarvis_formation",
                        "functional": a.functional,
                    }
                )
        if formula in {_formula_from_text("MgH2"), _formula_from_text("AlHO2")}:
            result.validation[formula] = {
                "inputs": [
                    {
                        "id": e.sid,
                        "spg": SpacegroupAnalyzer(
                            prims[e.sid], symprec=0.1
                        ).get_space_group_number(),
                        "nsites": len(prims[e.sid]),
                        "energy": e.energy,
                        "canonical": aliases[e.sid],
                    }
                    for e in group
                ],
                "counts": dict(group_stats),
            }
    # A pair discovered in both databases is one experiment, with MP priority
    # among candidates that actually passed both filters. Do not average gaps.
    selected = {}
    for pair in sorted(
        eligible_pairs, key=lambda p: (p["source"] != "mp", p["pair_id"])
    ):
        if pair["pair_id"] in selected:
            result.counts["pair_source_duplicates"] += 1
            result.example("pair also found in other source", pair["pair_id"])
        else:
            selected[pair["pair_id"]] = pair
    result.pairs = sorted(selected.values(), key=lambda p: (p["formula"], p["pair_id"]))
    used = {p[side] for p in result.pairs for side in ("struct_a", "struct_b")}
    flags_by_phase = defaultdict(set)
    for sid, canonical in sorted(
        result.aliases.items(), key=lambda item: _id_key(item[0])
    ):
        if canonical in used:
            flags_by_phase[canonical].update(structure_flags(crystals[sid]))
            if by_id[sid].theoretical:
                flags_by_phase[canonical].add("theoretical")
    for pair in result.pairs:
        flags = flags_by_phase[pair["struct_a"]] | flags_by_phase[pair["struct_b"]]
        if (
            by_id[pair["struct_a"]].source == "jarvis"
            or by_id[pair["struct_b"]].source == "jarvis"
        ):
            flags = flags | {"jarvis_only"}
        pair["flags"] = ";".join(sorted(flags))
        for flag in flags:
            result.counts[f"flag_{flag}"] += 1
        result.counts[f"tier_{pair['tier']}"] += 1
    for sid in sorted(used, key=lambda s: (by_id[s].formula, _id_key(s))):
        entry, crystal = by_id[sid], crystals[sid]
        result.crystals[sid] = crystal
        result.structures.append(
            {
                "struct_id": sid,
                "source": entry.source,
                "formula": entry.formula,
                "spg": SpacegroupAnalyzer(
                    crystal, symprec=0.1
                ).get_space_group_number(),
                "nsites": len(crystal),
                "cif": f"data/isoshift/structs/{sid}.cif",
                "e_source_eV_atom": entry.provenance_energy,
                "e_kind": "mp_total_r2scan_or_gga"
                if entry.source == "mp"
                else "jarvis_formation",
            }
        )
    result.counts["final_structures"] = len(result.structures)
    result.counts["final_pairs"] = len(result.pairs)
    result.counts["unused_unique_structures"] = result.counts["cross_unique"] - len(
        used
    )
    _cross_check_baseline(baseline_rows, result)
    return result


def _formula_from_text(text: str) -> str:
    return Composition(text).reduced_formula


def _cross_check_baseline(rows, result: BuildResult) -> None:
    if rows is None:
        return
    result.counts["baseline_provided"] = 1
    selected = {p["pair_id"] for p in result.pairs}
    seen = set()
    for row in rows:
        result.counts["baseline_rows"] += 1
        a, b = str(row["jid_a"]), str(row["jid_b"])
        key = tuple(sorted((a, b), key=_id_key))
        if key in seen:
            result.counts["baseline_repeated_rows"] += 1
            continue
        seen.add(key)
        if a not in result.aliases or b not in result.aliases:
            result.counts["baseline_ineligible_entry"] += 1
            continue
        a, b = result.aliases[a], result.aliases[b]
        if a == b:
            result.counts["baseline_same_phase"] += 1
        elif "__".join(sorted((a, b), key=_id_key)) in selected:
            result.counts["baseline_retained"] += 1
        else:
            result.counts["baseline_not_selected"] += 1
    result.counts["baseline_unique_pairs"] = len(seen)


def report_markdown(result: BuildResult) -> str:
    """Every data-dependent count is generated, never copied from feasibility."""
    c = result.counts
    lines = [
        "# IsoShift polymorph pair provenance",
        "",
        "## Method and energy provenance",
        "",
        "Inputs: local `mp_h.json`, `dft_3d.pkl` and (cross-check only) `jarvis_h_pairs.csv`; no refetch.",
        "Formula equality uses pymatgen elemental reduced composition, not source formula strings.",
        (
            "MP pair energies are `e_form_eV`, the summary's corrected formation energies. At fixed composition, "
            "the hull reference `e_form_eV - e_hull_eV` must agree within 1e-5 eV/atom; otherwise all MP "
            "comparisons of that composition are excluded and counted. This checks snapshot consistency, "
            "not the underlying DFT accuracy. The snapshot has no per-entry thermo-type identifiers, "
            "so a common corrected summary thermodynamic scale is an explicit assumption, not independent verification."
        ),
        (
            "MP raw `e_per_atom_eV` is retained only in structures.csv as `e_source_eV_atom`, with contract "
            "`e_kind=mp_total_r2scan_or_gga`; it is NEVER subtracted. Pairs instead record "
            "`energy_kind=mp_corrected_formation`, both comparison energies and both original energy IDs."
        ),
        (
            "JARVIS uses only finite `formation_energy_peratom` and verified `func=OptB88vdW` "
            "(case/punctuation normalized); other or missing functionals are excluded and counted. "
            "`ehull` and raw JARVIS total energies are not used. MP and JARVIS energies are never mixed."
        ),
        (
            "Background: [MP energy corrections](https://docs.materialsproject.org/methodology/materials-methodology/"
            "thermodynamic-stability/thermodynamic-stability) and "
            "[MP phase diagrams](https://docs.materialsproject.org/methodology/materials-methodology/"
            "thermodynamic-stability/phase-diagrams-pds)."
        ),
        "",
        "## Structural identity and output",
        "",
        (
            "Remove oxidation states/site properties; reduce primitive cells with pymatgen "
            "`get_primitive_structure(tolerance=0.01 Angstrom)`, Niggli-reduce and sort sites. "
            "This is numerical primitive-cell recognition, not a relaxation."
        ),
        (
            "StructureMatcher: ElementComparator, ltol=0.2, stol=0.15 (fraction of mean free length per atom), "
            "angle_tol=5 degrees, scale=True, primitive_cell=False (already reduced), "
            "attempt_supercell=False, allow_subset=False. Only equal primitive atom counts can match. "
            "A fit in either direction counts as identity (fit can be asymmetric near a tolerance boundary). "
            "Different space groups at symprec=0.05 Angstrom block a merge; reported space groups use symprec=0.1 Angstrom."
        ),
        (
            "Within each source choose deterministic representatives by lowest comparison energy, then numeric ID; "
            "greedily match to representatives (no transitive closure of approximate matches). Then match JARVIS "
            "representatives to MP representatives, always preferring MP. Members inherit their representative's "
            "mapping. Only one lowest-energy entry per source and canonical phase supplies comparisons."
        ),
        (
            "A JARVIS-energy pair may therefore reference an MP structure. `energy_id_a/b`, "
            "`energy_a/b_eV_atom`, `energy_kind`, and `functional` preserve the actual subtraction. "
            "If both databases produce an eligible unordered pair, keep MP's gap; otherwise keep the eligible "
            "source. Do not average gaps. Stable pair IDs are the two canonical IDs in deterministic order. "
            "`a` has the lower comparison energy; exact ties use numeric energy-entry ID."
        ),
        (
            "Keep gaps <=25 meV/atom (1e-8 meV floating-point tolerance), then primitive cells <=32 atoms. "
            "Tier 16 means both <=16; tier 32 is the remainder. Counts of 25<gap<=50 are before size filtering. "
            "These are source-energy prefilters: MLIP relaxation must reapply energy and structural-identity "
            "cuts. No claim of isotope switching or harmonic validity is made here."
        ),
        (
            "structures.csv contains exactly the structures referenced by pairs.csv. CIFs are written as P1 "
            "without symmetry expansion and verified with ASE for species and atom count. Seven pre-event "
            "CIFs are never overwritten: reuse only if ASE verifies the same primitive atom count and "
            "StructureMatcher verifies the phase; otherwise fail before writing any output. Unreferenced "
            "existing CIFs are left on disk but are not included in structures.csv."
        ),
        (
            "Per-composition caches live under `.cache/`, keyed by structure/energy inputs, implementation "
            "hash and pymatgen/spglib/numpy versions. Interrupted runs retain completed groups; stale or "
            "unreadable caches are recomputed. CSV/CIF/report content has no timestamps or cache-hit counts."
        ),
        "",
        "## Filter accounting",
        "",
        (
            "Counts of candidate pairs are per source until source "
            "duplicates are resolved. Duplicate rejection examples below are a sample of at most five per "
            "reason; no entry or pair processing is capped."
        ),
        "",
        "| Entry stage | MP | JARVIS |",
        "|---|---:|---:|",
    ]
    stages = [
        ("read", "Entries read"),
        ("excluded_composition", "Excluded: no H or contains C"),
        ("invalid_before_composition", "Malformed before composition established"),
        ("h_no_c", "After H/no-C filter"),
        ("invalid_after_composition", "Malformed after composition established"),
        ("partial_occupancy", "Dropped partial occupancy"),
        ("ordered", "After occupancy/geometry check"),
        ("missing_energy", "Dropped missing/nonfinite energy"),
        ("untrusted_functional", "Dropped untrusted functional"),
        ("energy_eligible", "Energy-eligible entries"),
        ("within_duplicates", "Within-source duplicates"),
        ("within_unique", "Unique after within-source dedup"),
        (
            "phase_representatives",
            "Source phase representatives after cross-source dedup",
        ),
        ("candidate_pairs", "Candidate distinct-phase pairs"),
        ("pairs_after_energy_cut", "Pairs after energy cut"),
    ]
    lines += [
        f"| {label} | {c['mp_' + key]} | {c['jarvis_' + key]} |"
        for key, label in stages
    ]
    lines += [
        "",
        (
            "Entry identities: read = excluded-composition + malformed-before + H/no-C; "
            "H/no-C = malformed-after + partial-occupancy + ordered; ordered = missing-energy + "
            "untrusted-functional + energy-eligible; energy-eligible = within-duplicates + within-unique."
        ),
        "",
        "| Combined stage | Count |",
        "|---|---:|",
    ]
    combined = [
        ("cross_merges", "Cross-source representative merges"),
        ("cross_unique", "Unique structures after cross-source dedup"),
        ("compositions", "Compositions"),
        ("multi_structure_compositions", "Compositions with >=2 structures"),
        (
            "mp_inconsistent_reference_compositions",
            "MP compositions with inconsistent hull reference",
        ),
        ("candidate_pairs", "Candidate pairs before energy eligibility/cuts"),
        ("pairs_untrusted_mp_reference", "Excluded MP pairs: inconsistent reference"),
        ("pairs_above_25_meV", "Pairs excluded above 25 meV/atom"),
        ("pairs_25_to_50_meV", "Of those: 25<gap<=50 meV/atom"),
        ("pairs_above_50_meV", "Of those: gap>50 meV/atom"),
        ("pairs_after_energy_cut", "Pairs after energy cut"),
        ("pairs_oversized", "Excluded: cell >32 atoms"),
        ("pairs_after_size_cut", "Pairs after cell-size cut"),
        ("pair_source_duplicates", "Duplicate pairs found in both sources"),
        ("tier_16", "Final tier 16 pairs"),
        ("tier_32", "Final tier 32 pairs"),
        ("final_pairs", "Final pairs"),
        ("final_structures", "Final referenced structures"),
        (
            "unused_unique_structures",
            "Unique structures not referenced by a selected pair",
        ),
    ]
    lines += [f"| {label} | {c[key]} |" for key, label in combined]
    lines += [
        "",
        (
            "Accounting identities: candidates = untrusted-reference + above-cut + after-energy; "
            "after-energy = oversized + after-size; after-size = source-duplicate-pairs + final-pairs; "
            "final-pairs = tier16 + tier32. Within-source unique sum = cross-merges + cross-unique. "
            "Cross-unique = final-structures + unused-unique."
        ),
        "",
        "## Flags (pair counts)",
        "",
    ]
    rules = {
        "proton_transfer": "Any H with two O/N/F neighbors <=1.6 Angstrom and X-H-X angle >=150 degrees; "
        "or H/O/P or H/O/S compounds (conservative acid-salt family); or MOOH with M=Al/Ga/In/Fe.",
        "hbond_disordered": "H2O, alkali hydroxides Li/Na/K/Rb/Cs OH, or N-containing halides with H:N>=4. "
        "Flags the family even if this particular ordered snapshot has no occupational disorder.",
        "molecular_h2": "At least one periodic H-H separation in [0.55, 1.0] Angstrom.",
        "jarvis_only": "At least one canonical member has no matched MP representative.",
        "theoretical": "At least one input MP entry merged into either phase has theoretical=True.",
    }
    for name, rule in rules.items():
        lines.append(f"- `{name}`: {c['flag_' + name]} pairs. {rule}")
    lines += [
        "",
        (
            "Flags are unioned over merged phase members; they overlap and are not exclusions. "
            "Geometric/composition heuristics are review prompts, not evidence of proton transfer "
            "or actual disorder. Partial occupancy is dropped, so no retained pair is labeled "
            "`partial_occ_dropped`."
        ),
        "",
        "## JARVIS functional audit",
        "",
    ]
    lines += [
        f"- `{name}`: {count} ordered H/no-C entries."
        for name, count in sorted(result.functionals.items())
    ]
    lines += [
        "",
        "## Pre-event candidate cross-check",
        "",
        (
            "The old formula/space-group list cannot create or override a pair. Its unique ID pairs "
            "are mapped through the new aliases and partitioned into the categories below. "
            "Different source IDs may map to one final pair; these are baseline ID-pair counts."
        ),
        "",
    ]
    for key in (
        "baseline_provided",
        "baseline_rows",
        "baseline_repeated_rows",
        "baseline_unique_pairs",
        "baseline_ineligible_entry",
        "baseline_same_phase",
        "baseline_retained",
        "baseline_not_selected",
    ):
        lines.append(f"- {key}: {c[key]}")
    lines += ["", "## Validation compositions", ""]
    for formula in (_formula_from_text("MgH2"), _formula_from_text("AlHO2")):
        detail = result.validation.get(formula)
        lines.append(f"### {formula}")
        lines.append("")
        if detail is None:
            lines.append(
                "No energy-eligible input entries; see entry rejection counts/examples."
            )
        else:
            lines += [
                "| Input ID | Primitive atoms | Space group | Source comparison eV/atom | Canonical ID |",
                "|---|---:|---:|---:|---|",
            ]
            for row in detail["inputs"]:
                lines.append(
                    f"| {row['id']} | {row['nsites']} | {row['spg']} | {row['energy']:.12g} | {row['canonical']} |"
                )
            lines.append("")
            lines.append(
                "Source-level filter accounting: "
                + json.dumps(detail["counts"], sort_keys=True)
            )
            kept = [p for p in result.pairs if p["formula"] == formula]
            lines.append(
                "Retained pairs: "
                + (
                    ", ".join(
                        f"{p['pair_id']} ({p['dE_meV_atom']:.6g} meV/atom)"
                        for p in kept
                    )
                    or "none"
                )
            )
            lines.append(
                "Space groups and source IDs permit the rutile/gamma MgH2 and AlOOH variants to be "
                "audited without inferring phase names solely from space group. Missing comparisons "
                "are accounted for by structural merges, energy eligibility, gap or cell-size cuts above."
            )
        lines.append("")
    lines += ["## Rejection/merge audit examples", ""]
    for reason, examples in sorted(result.examples.items()):
        lines.append(f"- {reason}: " + "; ".join(examples))
    lines += [
        "",
        "## Reproduction",
        "",
        "```powershell",
        ".venv/Scripts/python.exe -m pytest -q tests/test_pairs.py",
        ".venv/Scripts/python.exe -m src.isoshift_event.pairs",
        "```",
        "",
        (
            "Curation and ASE round-trip checks complete when the module exits successfully. "
            "Unit tests are a separate command; this generated report does not assert their result."
        ),
    ]
    if result.input_hashes:
        lines += ["", "Input SHA-256:"]
        lines += [
            f"- `{name}`: `{digest}`"
            for name, digest in sorted(result.input_hashes.items())
        ]
    return "\n".join(lines) + "\n"


def _csv_bytes(rows: list[dict], fields: tuple[str, ...]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                key: format(value, ".15g") if isinstance(value, float) else value
                for key, value in row.items()
            }
        )
    return stream.getvalue().encode("utf-8")


def _verify_cif(content: bytes, crystal: Structure) -> None:
    atoms = ase_read(io.BytesIO(content), format="cif")
    expected = Counter(site.specie.symbol for site in crystal)
    if len(atoms) != len(crystal) or Counter(atoms.get_chemical_symbols()) != expected:
        raise ValueError("CIF round-trip changed species or primitive atom count")
    restored = Structure(
        atoms.cell.array, atoms.get_chemical_symbols(), atoms.get_scaled_positions()
    )
    if not make_matcher().fit(crystal, restored):
        raise ValueError("CIF round-trip changed the crystal structure")


def write_outputs(result: BuildResult, output_dir: Path = DATA) -> None:
    """Preflight every CIF before publishing CSVs; never overwrite baseline CIFs."""
    output_dir = Path(output_dir)
    pending = {}
    for row in result.structures:
        sid = row["struct_id"]
        path = output_dir / "structs" / f"{sid}.cif"
        crystal = result.crystals[sid]
        if sid in PRE_EVENT_IDS and path.exists():
            try:
                _verify_cif(path.read_bytes(), crystal)
            except Exception as exc:
                raise FileExistsError(
                    f"Incompatible pre-event CIF must be preserved: {path}"
                ) from exc
            continue
        content = str(CifWriter(crystal, symprec=None, significant_figures=10)).encode(
            "utf-8"
        )
        _verify_cif(content, crystal)
        pending[path] = content
    for path, content in pending.items():
        _atomic_write(path, content)
    _atomic_write(
        output_dir / "structures.csv", _csv_bytes(result.structures, STRUCTURE_FIELDS)
    )
    _atomic_write(output_dir / "pairs.csv", _csv_bytes(result.pairs, PAIR_FIELDS))
    _atomic_write(output_dir / "PAIRS.md", report_markdown(result).encode("utf-8"))


def main(argv=None) -> None:
    import pandas as pd

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DATA)
    parser.add_argument("--output-dir", type=Path, default=DATA)
    parser.add_argument(
        "--cache-dir", type=Path, default=ROOT / ".cache" / "isoshift_pairs"
    )
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args(argv)
    mp_path = args.input_dir / "mp_h.json"
    jarvis_path = args.input_dir / "dft_3d.pkl"
    baseline_path = args.input_dir / "jarvis_h_pairs.csv"
    mp_rows = json.loads(mp_path.read_text(encoding="utf-8"))
    # Trusted, already-present local snapshot only; never load remote pickles.
    jarvis_rows = pd.read_pickle(jarvis_path).to_dict("records")
    baseline = None
    if baseline_path.exists():
        with baseline_path.open(encoding="utf-8", newline="") as stream:
            baseline = list(csv.DictReader(stream))
    result = build_pairs(
        mp_rows,
        jarvis_rows,
        cache_dir=None if args.no_cache else args.cache_dir,
        baseline_rows=baseline,
    )
    for path in (mp_path, jarvis_path, baseline_path):
        if path.exists():
            with path.open("rb") as stream:
                result.input_hashes[path.name] = hashlib.file_digest(
                    stream, "sha256"
                ).hexdigest()
    write_outputs(result, args.output_dir)
    print(
        f"structures={len(result.structures)} pairs={len(result.pairs)} "
        f"tier16={result.counts['tier_16']} tier32={result.counts['tier_32']} "
        f"composition_cache_hits={result.cache_hits}"
    )


if __name__ == "__main__":
    main()
