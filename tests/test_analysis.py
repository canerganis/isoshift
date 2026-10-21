"""CPU-only analysis tests: synthetic values, no MLIP loading or downloads."""
import copy
import csv
import importlib
import importlib.util
import json
import subprocess
import sys

import pytest


@pytest.fixture
def analysis():
    # A missing implementation is an explicit assertion failure during the red run.
    assert importlib.util.find_spec("src.isoshift_event.analysis") is not None
    return importlib.import_module("src.isoshift_event.analysis")


def inputs(signals=(1.0, 1.2), pair_id="ab"):
    pairs, structures = [], []
    for model, signal in zip(("mace", "orb", "sevenn", "mattersim"), signals):
        pairs.append(dict(pair_id=pair_id, struct_a="a", struct_b="b", model=model,
                          flags="", identity_checked=True, numerical_error_meV_atom=0.01,
                          dE_static_meV_atom=2.0,
                          **{f"ddF_iso_{t}K_meV_atom": signal for t in (0, 300, 600)},
                          **{f"ddF_iso_{t}K_meV_H": 2*signal for t in (0, 300, 600)}))
        for sid, n, h, fh, fd, energy, volume in (
            ("a", 2, 1, 50., 40., -1., 10.),
            ("b", 4, 2, 60., 50.+signal, -0.998, 10.5),
        ):
            structures.append(dict(struct_id=sid, model=model, status="ok", reason="", formula="LiH",
                n_atoms=n, H_count=h, relax_converged=True, min_freq_THz=-0.01,
                has_imaginary_H=False, has_imaginary_D=False,
                min_freq_THz_H=-0.01, min_freq_THz_D=-0.01,
                E_eV_atom=energy, V_A3_atom=volume, supercell="[2, 2, 2]",
                input_sha256=sid, temps_K_json="[0, 300, 600]",
                F_H_meV_atom_json=json.dumps([fh, fh-3, fh-12]),
                F_D_meV_atom_json=json.dumps([fd, fd-3, fd-12])))
    return pairs, structures


def write_csv(path, rows, fields=None):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_signal_spread_units_pressure_and_no_invented_transition(analysis):
    row, = analysis.analyze(*inputs())
    assert row["eligible"] and row["rank"] == 1
    assert row["n_models_valid"] == 2
    assert row["ddF_iso_300K_median_meV_atom"] == pytest.approx(1.1)
    assert row["ddF_iso_300K_model_spread_meV_atom"] == pytest.approx(0.2)
    assert row["ddF_iso_300K_median_meV_H"] == pytest.approx(2.2)
    assert row["dP_iso_300K_median_GPa"] == pytest.approx(-0.35247885948)
    assert row["dT_iso_K"] is None
    assert "mass_path_unavailable" in row["flags"]
    assert "shared_bias" in row["limitations"]


@pytest.mark.parametrize("signals,reason", [
    ((1., -1.), "sign_disagreement"), ((0., 0.), "signal_below_threshold"),
    ((0.1, 0.1), "signal_below_threshold"), ((0.2, 1.), "signal_below_threshold"),
    ((1.,), "insufficient_models"),
])
def test_rank_gates(analysis, signals, reason):
    row, = analysis.analyze(*inputs(signals))
    assert not row["eligible"] and row["rank"] is None
    assert reason in row["rejection_reasons"]


def test_equal_mass_and_isotope_swap(analysis):
    pairs, structures = inputs()
    for r in structures:
        r["F_H_meV_atom_json"], r["F_D_meV_atom_json"] = r["F_D_meV_atom_json"], r["F_H_meV_atom_json"]
    for r in pairs:
        for t in (0, 300, 600):
            for unit in ("atom", "H"):
                r[f"ddF_iso_{t}K_meV_{unit}"] *= -1
    row, = analysis.analyze(pairs, structures)
    assert row["ddF_iso_300K_median_meV_atom"] == pytest.approx(-1.1)
    assert row["eligible"]
    for r in structures:
        r["F_D_meV_atom_json"] = r["F_H_meV_atom_json"]
    for r in pairs:
        for t in (0, 300, 600):
            for unit in ("atom", "H"):
                r[f"ddF_iso_{t}K_meV_{unit}"] = 0
    row, = analysis.analyze(pairs, structures)
    assert row["ddF_iso_300K_median_meV_atom"] == 0
    assert not row["eligible"]


@pytest.mark.parametrize("change,reason", [
    ({"status": "quarantined", "reason": "imaginary_modes"}, "quarantined"),
    ({"status": "failed", "reason": "CUDA out of memory"}, "failed"),
    ({"has_imaginary_D": "True"}, "imaginary_modes"),
    ({"min_freq_THz_D": -0.11}, "imaginary_modes"),
    ({"relax_converged": "False"}, "relax_not_converged"),
    ({"F_H_meV_atom_json": "[1, NaN, 3]"}, "invalid_thermodynamics"),
    ({"F_H_meV_atom_json": "[1, 2]"}, "invalid_thermodynamics"),
    ({"temps_K_json": "[0, 300, 300]"}, "invalid_thermodynamics"),
    ({"H_count": 0}, "invalid_composition"),
])
def test_bad_member_blocks_ranking_without_losing_pair(analysis, change, reason):
    pairs, structures = inputs((1., 1.1, 1.2))
    structures[-1].update(change)
    row, = analysis.analyze(pairs, structures)
    assert row["n_models_valid"] == 2
    assert not row["eligible"]
    assert reason in row["rejection_reasons"]
    assert row["pair_id"] == "ab"


def test_composition_must_match_in_every_element(analysis):
    # LiH vs NaH share H_count/n_atoms but are not polymorphs.
    pairs, structures = inputs()
    for r in structures:
        if r["struct_id"] == "b":
            r["formula"] = "NaH"
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"] and row["provisional_rank"] is None
    assert "composition_mismatch" in row["rejection_reasons"]
    # No composition evidence at all fails closed.
    pairs, structures = inputs()
    for r in structures:
        r.pop("formula")
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"] and "composition_unchecked" in row["rejection_reasons"]
    # The structure manifest is accepted as evidence, and it must agree with the rows.
    manifest = [dict(struct_id="a", formula="LiH"), dict(struct_id="b", formula="Li2H2")]
    row, = analysis.analyze(pairs, structures, structures_manifest=manifest)
    assert row["eligible"] and row["formula"] == "LiH"
    manifest[1]["formula"] = "NaH"
    row, = analysis.analyze(pairs, structures, structures_manifest=manifest)
    assert "composition_mismatch" in row["rejection_reasons"]
    pairs, structures = inputs()
    row, = analysis.analyze(pairs, structures, structures_manifest=[dict(struct_id="b", formula="NaH")])
    assert "composition_evidence_conflict" in row["rejection_reasons"]
    # Cell counts that do not fit the formula invalidate the model.
    pairs, structures = inputs()
    for r in structures:
        r["formula"] = "LiH2"
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"] and "composition_count_mismatch" in row["rejection_reasons"]


def test_reported_temperatures_must_be_grid_points(analysis):
    pairs, structures = inputs()
    for r in structures:
        r["temps_K_json"] = "[0, 600, 1200]"
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"] and row["n_models_valid"] == 0
    assert "reported_temperature_not_on_grid" in row["rejection_reasons"]
    assert row["ddF_iso_300K_median_meV_atom"] is None
    # Values are read at the grid point, not interpolated from neighbours.
    pairs, structures = inputs()
    for r in structures:
        f_h, f_d = json.loads(r["F_H_meV_atom_json"]), json.loads(r["F_D_meV_atom_json"])
        r["temps_K_json"] = "[0, 150, 300, 600]"
        r["F_H_meV_atom_json"] = json.dumps([f_h[0], f_h[0], *f_h[1:]])
        r["F_D_meV_atom_json"] = json.dumps([f_d[0], f_d[0] + 7., *f_d[1:]])
    row, = analysis.analyze(pairs, structures)
    assert row["eligible"]
    assert row["ddF_iso_300K_median_meV_atom"] == pytest.approx(1.1)


def test_model_cap_skip_is_not_a_dissenting_model(analysis):
    pairs, structures = inputs((1., 1.1, 1.2))
    for r in pairs[2:]:
        for k in list(r):
            if k.startswith("ddF_") or k == "dE_static_meV_atom":
                r[k] = ""
    for r in structures:
        if r["model"] == "sevenn" and r["struct_id"] == "b":
            r.update(status="quarantined", reason="skipped_model_cap_100_shared_supercell_128")
        elif r["model"] == "sevenn":
            r.update(status="missing", reason="no_result")
    row, = analysis.analyze(pairs, structures)
    assert row["eligible"] and row["rank"] == 1
    assert row["n_models_valid"] == 2 and row["n_models_expected"] == 2
    assert row["coverage"] == "partial"
    assert "sevenn:not_applicable:b_quarantined:skipped_model_cap_100" in row["flags"]
    assert json.loads(row["model_results_json"])["sevenn"]["status"] == "not_applicable"
    # A real failure on the other member of the capped model stays fail-closed.
    for r in structures:
        if r["model"] == "sevenn" and r["struct_id"] == "a":
            r.update(status="quarantined", reason="imaginary_modes")
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"] and "sevenn:a_quarantined:imaginary_modes" in row["rejection_reasons"]
    # A stale finite summary next to a cap skip is not silently ignored.
    pairs, structures = inputs((1., 1.1, 1.2))
    for r in structures:
        if r["model"] == "sevenn" and r["struct_id"] == "b":
            r.update(status="quarantined", reason="skipped_model_cap_100_shared_supercell_128")
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"] and row["n_models_expected"] == 3


def test_provisional_shortlist_only_waives_pending_evidence(analysis):
    pairs, structures = inputs()
    twin, _ = inputs(pair_id="yy")
    stale, _ = inputs(pair_id="stale")
    for r in stale:
        r["ddF_iso_300K_meV_atom"] = 99
    pairs += twin + stale
    for r in pairs:
        r.pop("identity_checked")
        r.pop("numerical_error_meV_atom")
        r["flags"] = "relaxed_identity_unchecked_worker_has_no_coordinates"
    rows = {r["pair_id"]: r for r in analysis.analyze(pairs, structures)}
    assert not any(r["eligible"] or r["rank"] for r in rows.values())
    assert [rows[p]["provisional_rank"] for p in ("ab", "yy", "stale")] == [1, 2, None]
    assert rows["ab"]["pending_evidence"] == "identity_unchecked;numerical_error_unknown"
    assert "pair_summary_mismatch" in rows["stale"]["rejection_reasons"]
    # Below-threshold signals are real rejections even with evidence pending.
    pairs, structures = inputs((0.05, 0.06))
    for r in pairs:
        r.pop("identity_checked")
    row, = analysis.analyze(pairs, structures)
    assert row["provisional_rank"] is None and "signal_below_threshold" in row["rejection_reasons"]


def test_missing_structure_and_pending_model_stay_visible(analysis):
    pairs, structures = inputs((1., 1.1, 1.2))
    structures = [r for r in structures if r["model"] != "sevenn"]
    for k in list(pairs[-1]):
        if k.startswith("ddF_") or k == "dE_static_meV_atom":
            pairs[-1][k] = ""
    row, = analysis.analyze(pairs, structures)
    assert row["n_models_valid"] == 2 and row["n_models_expected"] == 3
    assert row["coverage"] == "partial"
    assert "missing" in row["flags"]
    # A partial two-model result is not a four-model validation claim.
    assert json.loads(row["model_results_json"])["sevenn"]["status"] == "missing"


def test_identity_and_numerical_error_must_be_evidenced(analysis):
    pairs, structures = inputs()
    for r in pairs:
        r.pop("identity_checked")
        r.pop("numerical_error_meV_atom")
        r["flags"] = "relaxed_identity_unchecked_worker_has_no_coordinates"
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"]
    assert "identity_unchecked" in row["rejection_reasons"]
    assert "numerical_error_unknown" in row["rejection_reasons"]
    assert row["numerical_error_meV_atom"] is None
    assert row["ddF_iso_300K_median_meV_atom"] == pytest.approx(1.1)


def test_explicit_error_bound_and_large_error(analysis):
    pairs, structures = inputs()
    for r in pairs:
        r.pop("numerical_error_meV_atom")
    assert analysis.analyze(pairs, structures, numerical_error_meV_atom=0.02)[0]["eligible"]
    row, = analysis.analyze(pairs, structures, numerical_error_meV_atom=2.)
    assert not row["eligible"]
    assert "signal_below_threshold" in row["rejection_reasons"]
    with pytest.raises(ValueError):
        analysis.analyze(pairs, structures, numerical_error_meV_atom=float("nan"))


@pytest.mark.parametrize("mutation,reason", [
    ("stale", "pair_summary_mismatch"), ("supercell", "cross_model_config_mismatch"),
    ("identity", "identity_unchecked"), ("same", "same_input_structure"),
])
def test_stale_and_incompatible_inputs_cannot_rank(analysis, mutation, reason):
    pairs, structures = inputs()
    if mutation == "stale":
        pairs[0]["ddF_iso_300K_meV_atom"] = 99
    elif mutation == "supercell":
        structures[-1]["supercell"] = "[3, 3, 3]"
    elif mutation == "identity":
        pairs[0]["flags"] = "relaxed_identity_unchecked_worker_has_no_coordinates"
    else:
        for r in pairs:
            r["struct_b"] = "a"
    row, = analysis.analyze(pairs, structures)
    assert not row["eligible"] and reason in row["rejection_reasons"]


def test_small_volume_difference_omits_pressure(analysis):
    pairs, structures = inputs()
    for r in structures:
        r["V_A3_atom"] = 10
    row, = analysis.analyze(pairs, structures)
    assert row["dP_iso_300K_median_GPa"] is None
    assert "pressure_volume_guard" in row["flags"]


def test_omitted_model_row_cannot_hide_a_disagreeing_completed_model(analysis):
    pairs, structures = inputs((1., 1.1, -2.))
    row, = analysis.analyze(pairs[:2], structures)
    assert row["n_models_expected"] == 3
    assert not row["eligible"]
    assert "pair_summary_mismatch" in row["rejection_reasons"]


def test_empty_output_still_has_usable_schema(analysis, tmp_path):
    output = tmp_path / "empty.csv"
    analysis.write_candidates(output, [])
    with output.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        assert "ddF_iso_300K_median_meV_atom" in reader.fieldnames
        assert "rejection_reasons" in reader.fieldnames
        assert list(reader) == []


def test_real_screen_collect_contract_on_partial_queue(analysis, tmp_path):
    from ase import Atoms
    from ase.io import write
    from src.isoshift_event import screen

    structures = []
    for sid, repeat in (("a", 1), ("b", 2)):
        path = tmp_path / f"{sid}.cif"
        atoms = Atoms("LiH", positions=[[0, 0, 0], [2, 2, 2]], cell=[5, 5, 5], pbc=True)
        atoms = atoms.repeat((repeat, 1, 1))
        write(path, atoms)
        structures.append(dict(struct_id=sid, cif=str(path), nsites=len(atoms)))
    pairs = [dict(pair_id="ab", struct_a="a", struct_b="b", tier="16", flags="")]
    plan = screen.prepare(structures, pairs, ["mace", "orb"], tmp_path / "raw")
    for entry in plan:
        if entry["model"] == "orb":
            continue  # one pending model, no hidden GPU job
        n = entry["n_atoms"]
        shifted = entry["struct_id"] == "b"
        data = dict(calc=dict(name=entry["model"], model=screen.DEFAULT_MODELS[entry["model"]], version="test"),
            n_atoms=n, formula="LiH" if n == 2 else "Li2H2", temps=list(screen.TEMPS),
            mesh=entry["kw"]["mesh"], relax=dict(energy=-n, volume=20*n, converged=True, fmax_final=1e-5),
            fc_meta=dict(supercell=entry["kw"]["supercell"], natoms_supercell=entry["supercell_atoms"]),
            variants={iso: dict(zpe_eV_cell=f*n, F_eV_cell=[n*(f-1e-7*t*t) for t in screen.TEMPS],
                imag=dict(min_freq_THz=-0.01, has_imaginary=False, n_imag_modes=0, imag_fraction=0.))
                for iso, f in (("H", 0.1), ("D", 0.081 if shifted else 0.08))})
        entry["out"].parent.mkdir(parents=True, exist_ok=True)
        entry["out"].write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "tables"
    screen.collect(plan, pairs, tmp_path / "queue", output)
    with (output / "screen_pairs.csv").open(newline="", encoding="utf-8") as stream:
        pair_rows = list(csv.DictReader(stream))
    with (output / "screen_structures.csv").open(newline="", encoding="utf-8") as stream:
        structure_rows = list(csv.DictReader(stream))
    row, = analysis.analyze(pair_rows, structure_rows)
    assert row["ddF_iso_300K_median_meV_atom"] == pytest.approx(1.)
    assert row["ddF_iso_300K_median_meV_H"] == pytest.approx(2.)
    assert row["n_models_valid"] == 1 and row["coverage"] == "partial"
    assert "identity_unchecked" in row["rejection_reasons"]
    assert not row["eligible"]
    assert analysis.main(["--screen-pairs", str(output / "screen_pairs.csv"),
                          "--screen-structures", str(output / "screen_structures.csv"),
                          "--output", str(output / "candidates.csv"), "--top", "10"]) == 0
    assert (output / "candidates.csv").exists()


def test_no_results_and_duplicate_rows(analysis):
    row, = analysis.analyze([], [], pairs=[dict(pair_id="ab", struct_a="a", struct_b="b")])
    assert row["coverage"] == "missing" and not row["eligible"]
    assert row["ddF_iso_300K_median_meV_atom"] is None
    pairs, structures = inputs()
    with pytest.raises(ValueError, match="duplicate"):
        analysis.analyze(pairs + pairs[:1], structures)
    with pytest.raises(ValueError, match="duplicate"):
        analysis.analyze(pairs, structures + structures[:1])


def test_reruns_are_deterministic_do_not_mutate_inputs_and_keep_rejections(analysis):
    pairs, structures = inputs()
    pairs2, _ = inputs(pair_id="zz")
    pairs += pairs2
    before = copy.deepcopy((pairs, structures))
    rows = analysis.analyze(pairs, structures)
    assert [r["pair_id"] for r in rows] == ["ab", "zz"]
    assert [r["rank"] for r in rows] == [1, 2]
    assert rows == analysis.analyze(list(reversed(pairs)), list(reversed(structures)))
    assert (pairs, structures) == before


def test_cli_writes_all_rows_atomically_top_only_limits_display(analysis, tmp_path):
    pairs, structures = inputs()
    other, _ = inputs(pair_id="zz")
    write_csv(tmp_path / "screen_pairs.csv", pairs + other)
    write_csv(tmp_path / "screen_structures.csv", structures)
    output = tmp_path / "candidates.csv"
    command = [sys.executable, "-B", "-m", "src.isoshift_event.analysis",
               "--screen-pairs", str(tmp_path / "screen_pairs.csv"),
               "--screen-structures", str(tmp_path / "screen_structures.csv"),
               "--output", str(output), "--top", "1"]
    first = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert first.returncode == 0, first.stderr
    assert "2 pairs" in first.stdout
    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2 and rows[0]["rank"] == "1"
    assert rows[0]["dT_iso_K"] == ""
    old = output.read_bytes()
    again = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert again.returncode == 0 and old == output.read_bytes()
    (tmp_path / "screen_pairs.csv").write_text("wrong,header\n", encoding="utf-8")
    failed = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert failed.returncode != 0 and output.read_bytes() == old
    assert not list(tmp_path.glob("*.tmp*"))
