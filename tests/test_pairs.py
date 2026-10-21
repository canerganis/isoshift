"""CPU-only pair curation tests; all data and output paths are synthetic."""

import json
from collections import Counter
from itertools import combinations

import numpy as np
import pandas as pd
import pytest
from ase.io import read
from pymatgen.core import Lattice, Structure

from src.isoshift_event import pairs


def phase(kind=0):
    # Rocksalt and CsCl coordination cannot be related by a setting change.
    if kind == 0:
        return Structure.from_spacegroup(
            225, Lattice.cubic(4.8), ["Li", "H"], [[0, 0, 0], [0.5, 0.5, 0.5]]
        )
    return Structure(Lattice.cubic(3.2), ["Li", "H"], [[0, 0, 0], [0.5, 0.5, 0.5]])


def mp(sid, structure, energy=0.0, raw=-10.0, **extra):
    return dict(
        mp_id=sid,
        structure=structure.as_dict(),
        e_hull_eV=energy,
        e_form_eV=-1.0 + energy,
        e_per_atom_eV=raw,
        theoretical=False,
        **extra,
    )


def jarvis(sid, structure, energy=-1.0, func="OptB88vdW", cartesian=False):
    return {
        "jid": sid,
        "formation_energy_peratom": energy,
        "func": func,
        "atoms": {
            "lattice_mat": structure.lattice.matrix.tolist(),
            "coords": (
                structure.cart_coords if cartesian else structure.frac_coords
            ).tolist(),
            "elements": [s.specie.symbol for s in structure],
            "cartesian": cartesian,
        },
    }


def test_cell_and_setting_duplicates_merge_but_polymorph_survives():
    original = phase()
    supercell = original * [2, 1, 1]
    supercell.translate_sites(range(len(supercell)), [0.13, 0.27, 0.31])
    result = pairs.build_pairs(
        [mp("mp-1", original), mp("mp-2", supercell), mp("mp-3", phase(1), 0.01)], []
    )
    assert len(result.pairs) == 1
    assert {r["struct_id"] for r in result.structures} == {"mp-1", "mp-3"}
    assert result.aliases["mp-2"] == "mp-1"
    assert {r["nsites"] for r in result.structures} == {2}
    assert result.pairs[0]["dE_meV_atom"] == pytest.approx(10.0)


def test_cross_source_merge_prefers_mp_but_keeps_jarvis_energy_provenance():
    result = pairs.build_pairs(
        [mp("mp-1", phase(), raw=-100.0)],
        [jarvis("JVASP-1", phase(), -2.0), jarvis("JVASP-2", phase(1), -1.98)],
    )
    pair = result.pairs[0]
    assert (pair["struct_a"], pair["struct_b"], pair["source"]) == (
        "mp-1",
        "JVASP-2",
        "jarvis",
    )
    assert (pair["energy_id_a"], pair["energy_id_b"]) == ("JVASP-1", "JVASP-2")
    assert pair["dE_meV_atom"] == pytest.approx(20.0)
    assert pair["energy_a_eV_atom"] == -2.0
    assert result.aliases["JVASP-1"] == "mp-1"


def test_cross_database_only_composition_does_not_create_energy_pair():
    result = pairs.build_pairs([mp("mp-1", phase())], [jarvis("JVASP-2", phase(1))])
    assert result.pairs == []
    assert result.structures == []


def test_pair_found_in_both_sources_prefers_mp_even_if_jarvis_gap_is_smaller():
    result = pairs.build_pairs(
        [mp("mp-1", phase()), mp("mp-2", phase(1), 0.02)],
        [jarvis("JVASP-1", phase()), jarvis("JVASP-2", phase(1), -0.99)],
    )
    assert len(result.pairs) == 1
    assert result.pairs[0]["source"] == "mp"
    assert result.pairs[0]["dE_meV_atom"] == pytest.approx(20.0)
    assert result.counts["pair_source_duplicates"] == 1


def test_mp_corrected_thermodynamic_energy_not_raw_total_is_used():
    result = pairs.build_pairs(
        [mp("mp-1", phase(), 0.02, raw=-200.0), mp("mp-2", phase(1), 0.0, raw=-10.0)],
        [],
    )
    pair = result.pairs[0]
    assert (pair["struct_a"], pair["struct_b"]) == ("mp-2", "mp-1")
    assert pair["dE_meV_atom"] == pytest.approx(20.0)
    assert pair["energy_kind"] == "mp_corrected_formation"


def test_mp_inconsistent_hull_reference_is_counted_and_not_compared():
    a, b = mp("mp-1", phase()), mp("mp-2", phase(1), 0.01)
    b["e_form_eV"] = -2.0
    result = pairs.build_pairs([a, b], [])
    assert result.pairs == []
    assert result.counts["mp_inconsistent_reference_compositions"] == 1


@pytest.mark.parametrize(
    "gap, kept", [(0.0, True), (0.025, True), (0.025001, False), (0.05, False)]
)
def test_gap_cut_sign_and_tie_break(gap, kept):
    result = pairs.build_pairs([mp("mp-2", phase(1), gap), mp("mp-1", phase())], [])
    assert len(result.pairs) == int(kept)
    if kept:
        assert result.pairs[0]["struct_a"] == "mp-1"
        assert result.pairs[0]["dE_meV_atom"] == pytest.approx(gap * 1000)
    else:
        assert result.counts["pairs_25_to_50_meV"] == 1


def test_partial_occupancy_and_h_no_carbon_filters_are_counted():
    disordered = Structure(Lattice.cubic(4), ["Li", {"H": 0.5}], [[0, 0, 0], [0.5] * 3])
    result = pairs.build_pairs(
        [
            mp("mp-1", phase()),
            mp("mp-2", phase(1), 0.01),
            mp("mp-3", disordered),
            mp("mp-4", Structure(Lattice.cubic(4), ["C", "H"], [[0, 0, 0], [0.5] * 3])),
            mp("mp-5", Structure(Lattice.cubic(4), ["Li"], [[0, 0, 0]])),
        ],
        [],
    )
    assert result.counts["mp_read"] == 5
    assert result.counts["mp_h_no_c"] == 3
    assert result.counts["mp_ordered"] == 2
    assert result.counts["mp_partial_occupancy"] == 1
    assert len(result.pairs) == 1


@pytest.mark.parametrize(
    "a,b,want",
    [(16, 16, 16), (16, 17, 32), (32, 32, 32), (33, 16, None), (32, 33, None)],
)
def test_tier_boundaries(a, b, want):
    assert pairs.pair_tier(a, b) == want


def test_tier_uses_primitive_not_stored_cell():
    result = pairs.build_pairs(
        [mp("mp-1", phase() * [3, 2, 1]), mp("mp-2", phase(1) * [4, 3, 1], 0.01)], []
    )
    assert result.pairs[0]["tier"] == 16
    assert result.pairs[0]["nsites_a"] == result.pairs[0]["nsites_b"] == 2


def test_unknown_or_mixed_jarvis_functionals_never_produce_a_gap():
    for functional in ("PBE", None, "na"):
        result = pairs.build_pairs(
            [],
            [
                jarvis("JVASP-1", phase()),
                jarvis("JVASP-2", phase(1), -0.99, functional),
            ],
        )
        assert result.pairs == []
        assert result.counts["jarvis_untrusted_functional"] == 1


def test_missing_energy_never_defaults_to_zero():
    a = mp("mp-1", phase())
    a["e_form_eV"] = float("nan")
    result = pairs.build_pairs([a, mp("mp-2", phase(1))], [])
    assert not result.pairs
    assert result.counts["mp_missing_energy"] == 1


def test_cartesian_jarvis_coordinates_merge_with_fractional_mp():
    result = pairs.build_pairs(
        [mp("mp-1", phase())],
        [
            jarvis("JVASP-1", phase(), cartesian=True),
            jarvis("JVASP-2", phase(1), -0.99),
        ],
    )
    assert result.aliases["JVASP-1"] == "mp-1"
    assert len(result.structures) == 2


def test_harmonic_validity_flags():
    molecular = Structure(Lattice.cubic(6), ["H", "H"], [[0, 0, 0], [0.74 / 6, 0, 0]])
    assert "molecular_h2" in pairs.structure_flags(molecular)
    bridge = Structure(
        Lattice.cubic(8), ["O", "H", "O"], [[0, 0, 0], [1.2 / 8, 0, 0], [2.4 / 8, 0, 0]]
    )
    assert "proton_transfer" in pairs.structure_flags(bridge)
    for species, flag in [
        (["O", "H", "H"], "hbond_disordered"),
        (["K", "O", "H"], "hbond_disordered"),
        (["N", "H", "H", "H", "H", "Cl"], "hbond_disordered"),
        (["Al", "O", "O", "H"], "proton_transfer"),
        (["K", "P", "O", "O", "O", "O", "H", "H"], "proton_transfer"),
    ]:
        s = Structure(
            Lattice.cubic(10),
            species,
            [[i / len(species), 0, 0] for i in range(len(species))],
        )
        assert flag in pairs.structure_flags(s)


def test_outputs_deterministic_cached_and_ase_readable(tmp_path):
    rows = [mp("mp-1", phase()), mp("mp-2", phase(1), 0.01)]
    cache_dir = tmp_path / ".cache"
    result = pairs.build_pairs(rows, [], cache_dir=cache_dir)
    first, second = tmp_path / "first", tmp_path / "second"
    pairs.write_outputs(result, first)
    repeated = pairs.build_pairs(rows[::-1], [], cache_dir=cache_dir)
    pairs.write_outputs(repeated, second)
    snapshot = lambda root: {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    }
    assert snapshot(first) == snapshot(second)
    assert repeated.cache_hits > 0
    assert result.pairs[0]["pair_id"] == repeated.pairs[0]["pair_id"]
    for row in result.structures:
        atoms = read(first / "structs" / (row["struct_id"] + ".cif"))
        assert len(atoms) == row["nsites"] == 2
        assert Counter(atoms.get_chemical_symbols()) == {"Li": 1, "H": 1}
        assert row["cif"].startswith("data/isoshift/structs/")
    for a, b in combinations(result.crystals.values(), 2):
        assert not pairs.make_matcher().fit(a, b)
        assert not pairs.make_matcher().fit(b, a)
    rows[1]["e_form_eV"] = -0.98
    rows[1]["e_hull_eV"] = 0.02
    changed = pairs.build_pairs(rows, [], cache_dir=cache_dir)
    assert changed.pairs[0]["dE_meV_atom"] == pytest.approx(20.0)


def test_pre_event_cif_is_never_overwritten(tmp_path):
    result = pairs.build_pairs(
        [], [jarvis("JVASP-2002", phase()), jarvis("JVASP-2", phase(1), -0.99)]
    )
    target = tmp_path / "structs" / "JVASP-2002.cif"
    target.parent.mkdir()
    target.write_text("pre-event artifact\n")
    with pytest.raises(FileExistsError, match="pre-event"):
        pairs.write_outputs(result, tmp_path)
    assert target.read_text() == "pre-event artifact\n"


def test_baseline_is_cross_checked_but_does_not_create_pairs():
    result = pairs.build_pairs(
        [],
        [jarvis("JVASP-1", phase()), jarvis("JVASP-2", phase(), -0.99)],
        baseline_rows=[{"jid_a": "JVASP-1", "jid_b": "JVASP-2", "dEf_meV": 10.0}],
    )
    assert not result.pairs
    assert result.counts["baseline_same_phase"] == 1


def test_cache_corruption_is_recomputed(tmp_path):
    rows = [mp("mp-1", phase()), mp("mp-2", phase(1), 0.01)]
    cache_dir = tmp_path / ".cache"
    result = pairs.build_pairs(rows, [], cache_dir=cache_dir)
    for path in cache_dir.glob("*.json"):
        path.write_text("{broken")
    again = pairs.build_pairs(rows, [], cache_dir=cache_dir)
    assert again.pairs == result.pairs
    assert again.cache_hits == 0


@pytest.mark.parametrize("size,want_tier", [(16, 16), (17, 32), (32, 32), (33, None)])
def test_actual_primitive_size_cut(size, want_tier):
    # A generic low-symmetry H cell has no smaller translational repeat. Using
    # one element makes compositions equal despite different cell populations.
    def hydrogen(n, seed):
        rng = np.random.default_rng(seed)
        return Structure(
            Lattice.from_parameters(12, 13, 14, 81, 87, 76),
            ["H"] * n,
            rng.random((n, 3)),
        )

    result = pairs.build_pairs(
        [mp("mp-1", hydrogen(size, 3)), mp("mp-2", hydrogen(size, 9), 0.01)], []
    )
    if want_tier is None:
        assert not result.pairs
        assert result.counts["pairs_oversized"] == 1
    else:
        assert len(result.pairs) == 1
        assert result.pairs[0]["tier"] == want_tier
        assert result.pairs[0]["nsites_a"] == result.pairs[0]["nsites_b"] == size


def test_flags_propagate_without_excluding_pair():
    a = mp("mp-1", phase())
    a["theoretical"] = True
    result = pairs.build_pairs(
        [a], [jarvis("JVASP-1", phase()), jarvis("JVASP-2", phase(1), -0.99)]
    )
    assert len(result.pairs) == 1
    assert result.pairs[0]["flags"] == "jarvis_only;theoretical"
    assert result.counts["flag_jarvis_only"] == result.counts["flag_theoretical"] == 1


def test_pre_event_compatible_cif_reused_byte_for_byte(tmp_path):
    result = pairs.build_pairs(
        [], [jarvis("JVASP-2002", phase()), jarvis("JVASP-2", phase(1), -0.99)]
    )
    pairs.write_outputs(result, tmp_path)
    target = tmp_path / "structs" / "JVASP-2002.cif"
    old = b"# preserved pre-event comment\n" + target.read_bytes()
    target.write_bytes(old)
    pairs.write_outputs(result, tmp_path)
    assert target.read_bytes() == old


def test_cli_reads_local_snapshots_and_writes_contract(tmp_path, capsys):
    inputs, output = tmp_path / "input", tmp_path / "output"
    inputs.mkdir()
    (inputs / "mp_h.json").write_text(json.dumps([mp("mp-1", phase())]))
    pd.DataFrame(
        [jarvis("JVASP-1", phase()), jarvis("JVASP-2", phase(1), -0.99)]
    ).to_pickle(inputs / "dft_3d.pkl")
    (inputs / "jarvis_h_pairs.csv").write_text(
        "jid_a,jid_b,dEf_meV\nJVASP-1,JVASP-2,10\n"
    )
    pairs.main(["--input-dir", str(inputs), "--output-dir", str(output), "--no-cache"])
    assert "structures=2 pairs=1 tier16=1" in capsys.readouterr().out
    structures = pd.read_csv(output / "structures.csv")
    candidates = pd.read_csv(output / "pairs.csv")
    assert set(structures.struct_id) == {"mp-1", "JVASP-2"}
    assert candidates.iloc[0].dE_meV_atom == pytest.approx(10.0)
    assert candidates.iloc[0].source == "jarvis"
    assert len(candidates) == 1
    assert (output / "PAIRS.md").is_file()


def test_all_filter_counts_reconcile():
    result = pairs.build_pairs(
        [mp("mp-1", phase()), mp("mp-2", phase(1), 0.04)],
        [
            jarvis("JVASP-1", phase()),
            jarvis("JVASP-2", phase(1), -0.99),
            jarvis("JVASP-3", phase(), func="unknown"),
        ],
    )
    c = result.counts
    for source in ("mp", "jarvis"):
        assert c[f"{source}_read"] == sum(
            c[f"{source}_{key}"]
            for key in ("excluded_composition", "invalid_before_composition", "h_no_c")
        )
        assert c[f"{source}_h_no_c"] == sum(
            c[f"{source}_{key}"]
            for key in ("invalid_after_composition", "partial_occupancy", "ordered")
        )
        assert c[f"{source}_ordered"] == sum(
            c[f"{source}_{key}"]
            for key in ("missing_energy", "untrusted_functional", "energy_eligible")
        )
        assert (
            c[f"{source}_energy_eligible"]
            == c[f"{source}_within_duplicates"] + c[f"{source}_within_unique"]
        )
    assert (
        c["candidate_pairs"]
        == c["pairs_untrusted_mp_reference"]
        + c["pairs_above_25_meV"]
        + c["pairs_after_energy_cut"]
    )
    assert (
        c["pairs_after_energy_cut"] == c["pairs_oversized"] + c["pairs_after_size_cut"]
    )
    assert c["pairs_after_size_cut"] == c["pair_source_duplicates"] + c["final_pairs"]
    assert c["final_pairs"] == c["tier_16"] + c["tier_32"]
    assert (
        c["mp_within_unique"] + c["jarvis_within_unique"]
        == c["cross_merges"] + c["cross_unique"]
    )
    assert c["cross_unique"] == c["final_structures"] + c["unused_unique_structures"]
    assert result.pairs[0]["source"] == "jarvis"  # MP failed the cut; JARVIS did not.


def test_symmetry_breaking_h_displacement_stays_distinct():
    from pymatgen.core import Lattice, Structure
    from src.isoshift_event import pairs

    lat = Lattice.orthorhombic(4.7, 4.2, 2.8)
    sym = Structure(lat, ["Al", "Al", "O", "O", "O", "O", "H", "H"],
                    [[0, 0, 0], [.5, .5, .5], [.35, .2, 0], [.65, .8, 0], [.15, .7, .5], [.85, .3, .5],
                     [.5, 0, 0], [0, .5, .5]])
    off = sym.copy()
    off.translate_sites([6], [0.03, 0, 0], frac_coords=True)  # H off the centre: lower symmetry
    pairs._SPG_CACHE.clear()
    assert pairs._spg(sym) != pairs._spg(off)
    assert not pairs._matches(pairs.make_matcher(), sym, off)
