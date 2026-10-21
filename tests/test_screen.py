"""CPU-only contract tests; synthetic worker results use eV per input cell."""
import copy
import json
import os

import numpy as np
import pytest
from ase import Atoms
from ase.io import read, write

from src.isoshift_event import screen


@pytest.fixture
def sample(tmp_path):
    structures = []
    for sid, repeat in (("a", 1), ("b", 2)):
        atoms = Atoms("LiH", positions=[[0, 0, 0], [2, 2, 2]], cell=[5, 5, 5], pbc=True)
        atoms = atoms.repeat((repeat, 1, 1))
        path = tmp_path / f"{sid}.cif"
        write(path, atoms)
        structures.append(dict(struct_id=sid, cif=str(path), nsites=len(atoms)))
    pairs = [dict(pair_id="ab", struct_a="a", struct_b="b", tier="16", flags="source_flag")]
    plan = screen.prepare(structures, pairs, ["mace", "orb"], tmp_path / "raw")
    return plan, pairs, tmp_path / "queue", tmp_path / "tables"


def result(entry, h=0.1, d=0.08, imaginary=False):
    n = entry["n_atoms"]
    return dict(calc=dict(name=entry["model"], model=screen.DEFAULT_MODELS[entry["model"]], version="test"),
                n_atoms=n, formula="LiH" if n == 2 else "H2Li2", temps=list(screen.TEMPS),
                mesh=entry["kw"]["mesh"],
                relax=dict(energy=-n, volume=20*n, converged=True, fmax_final=0.00001),
                fc_meta=dict(supercell=np.diag(entry["kw"]["supercell"]).tolist(), natoms_supercell=entry["supercell_atoms"]),
                variants={iso: dict(zpe_eV_cell=f*n,
                          F_eV_cell=[n*(f-1e-7*t*t) for t in screen.TEMPS],
                          imag=dict(min_freq_THz=-1.0 if imaginary else -0.01,
                                    has_imaginary=imaginary, n_imag_modes=int(imaginary),
                                    imag_fraction=0.01 if imaginary else 0.0))
                          for iso, f in (("H", h), ("D", d))},
                pool=dict(worker="test-worker", wall_s=1.25, model_load_s=2.0))


def publish(entry, **kwargs):
    path = entry["out"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result(entry, **kwargs)), encoding="utf-8")


def test_idempotent_pending_running_and_existing_result(sample):
    plan, _, queue, _ = sample
    screen.submit_jobs(plan, queue)
    pending = sorted((queue / "pending").glob("*.json"))
    assert len(pending) == 4
    original = pending[0].read_bytes()
    screen.submit_jobs(plan, queue)
    assert pending[0].read_bytes() == original
    pending[0].rename(queue / "running" / (pending[0].stem + "__worker.json"))
    screen.submit_jobs(plan, queue)
    assert len(list((queue / "pending").glob("*.json"))) == 3
    publish(plan[0])
    assert screen.submit_jobs(plan, queue)["existing"] == 1


def test_shared_supercell_mesh_and_explicit_no_shrink(sample):
    plan, _, queue, _ = sample
    screen.submit_jobs(plan, queue)
    for sid in ("a", "b"):
        entries = [p for p in plan if p["struct_id"] == sid]
        assert entries[0]["kw"] == entries[1]["kw"]
        assert entries[0]["supercell_atoms"] <= 160
    for path in (queue / "pending").glob("*.json"):
        job = json.loads(path.read_text())
        assert job["allow_shrink"] is False
        assert job["kw"]["fmax"] == 1e-4
        assert os.path.isabs(job["cif"])


def test_retry_budget_survives_repeated_submit(sample):
    plan, pairs, queue, output = sample
    plan = plan[:1]
    for attempt in range(3):
        screen.submit_jobs(plan, queue)
        jobs = list((queue / "pending").glob("*.json"))
        assert len(jobs) == 1
        job = json.loads(jobs[0].read_text())
        job["error"] = "synthetic failure"
        jobs[0].unlink()
        (queue / "failed" / f'{job["id"]}.json').write_text(json.dumps(job))
    for _ in range(3):
        screen.submit_jobs(plan, queue)
    assert not list((queue / "pending").glob("*.json"))
    rows, _ = screen.collect(plan, [], queue, output)
    assert rows[0]["status"] == "quarantined"
    assert "retry" in rows[0]["reason"]


def test_collect_partial_quarantine_and_cell_normalization(sample):
    plan, pairs, queue, output = sample
    publish(plan[0])
    publish(plan[1], imaginary=True)
    rows, pair_rows = screen.collect(plan, pairs, queue, output)
    assert len(rows) == 4 and len(pair_rows) == 2
    statuses = {(r["struct_id"], r["model"]): r["status"] for r in rows}
    assert statuses[("a", "mace")] == "ok"
    assert statuses[("a", "orb")] == "quarantined"
    assert statuses[("b", "mace")] == "missing"
    assert rows[0]["ZPE_H_meV_atom"] == pytest.approx(100)
    assert rows[0]["S_H_300K_meV_atom_K"] == pytest.approx(0.06)
    assert rows[0]["E_eV_atom"] == -1
    assert rows[0]["V_A3_atom"] == 20
    assert all(r["ddF_iso_300K_meV_atom"] == "" for r in pair_rows)
    assert "quarantined" in pair_rows[1]["flags"]
    assert (output / "screen_structures.csv").exists()


def test_p13_sign_swap_equal_masses_and_unequal_cells(sample):
    plan, _, _, _ = sample
    a, b = result(plan[0], h=0.1, d=0.08), result(plan[2], h=0.12, d=0.09)
    actual = screen.pair_quantities(a, b)
    assert actual["ddF_iso_300K_meV_atom"] == pytest.approx(-10)
    assert actual["ddF_iso_300K_meV_H"] == pytest.approx(-20)
    for r in (a, b):
        r["variants"]["H"], r["variants"]["D"] = r["variants"]["D"], r["variants"]["H"]
    assert screen.pair_quantities(a, b)["ddF_iso_300K_meV_atom"] == pytest.approx(10)
    for r in (a, b):
        r["variants"]["D"] = copy.deepcopy(r["variants"]["H"])
    assert screen.pair_quantities(a, b)["ddF_iso_600K_meV_atom"] == 0


@pytest.mark.parametrize("field", ["temps", "mesh", "supercell", "model", "nan"])
def test_incompatible_or_nonfinite_results_are_quarantined(sample, field):
    plan, pairs, queue, output = sample
    r = result(plan[0])
    if field == "supercell":
        r["fc_meta"]["supercell"] = [9, 9, 9]
    elif field == "model":
        r["calc"]["model"] = "old-checkpoint"
    elif field == "nan":
        r["variants"]["H"]["F_eV_cell"][0] = float("nan")
    else:
        r[field] = [999]
    plan[0]["out"].parent.mkdir(parents=True)
    plan[0]["out"].write_text(json.dumps(r))
    rows, _ = screen.collect(plan, pairs, queue, output)
    assert rows[0]["status"] == "quarantined"


def test_watchdog_reserves_loading_workers_and_separates_sevenn(sample, monkeypatch):
    plan, _, queue, _ = sample
    screen.submit_jobs(plan, queue)
    launched = []
    def launch(model, queue_dir, **kwargs):
        launched.append((model, kwargs))
        return os.getpid()
    monkeypatch.setattr(screen.pool, "launch", launch)
    control = queue.parent / "gpu-control"
    screen.run(queue, control_dir=control)
    screen.run(queue, control_dir=control)
    assert [m for m, _ in launched] == ["mace", "orb"]
    assert all(k["mem_fraction"] == 0.45 for _, k in launched)
    # Another queue cannot start SevenNet while these processes are alive.
    other = queue.parent / "other"
    screen.pool.submit(other, "harmonic", plan[0]["cif"], "sevenn", other / "out.json")
    screen.run(other, control_dir=control)
    assert len(launched) == 2


def test_fallback_has_three_distinct_composition_matched_pairs(tmp_path):
    structures, pairs = screen.validation_pairs(3)
    assert len(pairs) == 3
    assert len(structures) == 6
    assert all(p["struct_a"] != p["struct_b"] for p in pairs)
    plan = screen.prepare(structures, pairs, ["mace", "orb"], tmp_path / "raw")
    assert len(plan) == 12
    invalid = {(e["struct_id"], e["model"]): e["skip_reason"] for e in plan
               if e["skip_reason"].startswith("invalid_input")}
    assert not invalid
    atoms = {s["struct_id"]: read(s["cif"]) for s in structures}
    assert all(s["nsites"] == len(atoms[s["struct_id"]]) for s in structures)
    for pair in pairs:
        a, b = (atoms[pair[key]] for key in ("struct_a", "struct_b"))
        assert a.get_chemical_formula(empirical=True) == b.get_chemical_formula(empirical=True)
    assert all(not e["skip_reason"] for e in plan)


def test_entropy_grid_accuracy_for_soft_harmonic_mode():
    from isoshift.phonons import MeshFreqs, KB_EV, H_EV_THZ
    mf = MeshFreqs(np.array([[0.2, 1., 20.]]), np.array([1.]), 1)
    f = mf.helmholtz_free_energy(screen.TEMPS) * 1000
    numerical = screen.entropy_300(f)
    x = H_EV_THZ * np.array([0.2, 1., 20.]) / (KB_EV * 300)
    exact = 1000 * KB_EV * np.sum(x / np.expm1(x) - np.log1p(-np.exp(-x)))
    assert abs(numerical - exact) < 1e-5


def test_sevenn_cap_skips_instead_of_changing_supercell(tmp_path):
    atoms = Atoms("LiH", positions=[[0, 0, 0], [1.5, 1.5, 1.5]], cell=[3, 3, 3], pbc=True)
    path = tmp_path / "small.cif"
    write(path, atoms)
    structures = [dict(struct_id="a", cif=str(path), nsites=2)]
    pairs = [dict(pair_id="self", struct_a="a", struct_b="a", tier="16")]
    plan = screen.prepare(structures, pairs, ["mace", "sevenn"], tmp_path / "raw")
    assert plan[0]["supercell_atoms"] == 128
    assert plan[0]["kw"]["supercell"] == plan[1]["kw"]["supercell"]
    queue = tmp_path / "queue"
    screen.submit_jobs(plan, queue)
    assert len(list((queue / "pending").glob("*.json"))) == 1
    rows, _ = screen.collect(plan, pairs, queue, tmp_path / "tables")
    assert rows[1]["status"] == "quarantined"
    assert "skipped_model_cap_100" in rows[1]["reason"]


def test_crossings_static_energy_slope_guard_and_high_temperature(sample):
    plan, _, _, _ = sample
    a, b = result(plan[0]), result(plan[2])
    # Delta G_H = 40 - 0.05 T, delta G_D = 30 - 0.05 T (meV/atom).
    b["relax"]["energy"] = -0.96 * b["n_atoms"]
    for isotope, offset in (("H", 0), ("D", -0.01)):
        b["variants"][isotope]["F_eV_cell"] = [
            b["n_atoms"] * (fa / a["n_atoms"] + offset - 0.00005*t)
            for fa, t in zip(a["variants"][isotope]["F_eV_cell"], screen.TEMPS)]
    quantities = screen.pair_quantities(a, b)
    assert quantities["dE_static_meV_atom"] == pytest.approx(40)
    assert float(quantities["crossings_H_K"]) == pytest.approx(800)
    assert float(quantities["crossings_D_K"]) == pytest.approx(600)
    assert "crossing_H_above_600K" in quantities["flags"]
    assert "static_gap_gt_25_meV_atom" in quantities["flags"]
    b["relax"]["energy"] = -1 * b["n_atoms"]
    for isotope in ("H", "D"):
        b["variants"][isotope]["F_eV_cell"] = [
            b["n_atoms"] * (fa/a["n_atoms"] + 0.000001*(300-t))
            for fa, t in zip(a["variants"][isotope]["F_eV_cell"], screen.TEMPS)]
    guarded = screen.pair_quantities(a, b)
    # Small slope keeps the real root (M01: exact roots are primary) and flags it.
    assert float(guarded["crossings_H_K"]) == pytest.approx(300)
    assert float(guarded["crossings_D_K"]) == pytest.approx(300)
    assert "crossing_H_small_slope_guard" in guarded["flags"]
    assert "crossing_D_small_slope_guard" in guarded["flags"]
    assert "linear_dT_blocked_slope_guard" in guarded["flags"]


def test_small_slope_root_kept_m01_toy(sample):
    """M01 toy: T_c^H = 108.2738654918 K with |dS_H| ~ 0.00605 meV/atom/K, no D root."""
    plan, _, _, _ = sample
    a, b = result(plan[0]), result(plan[2])
    tc, ds = 108.2738654918, 0.00605497
    b["relax"]["energy"] = -1 * b["n_atoms"]
    # Delta G_H = ds (T - tc), Delta G_D = Delta G_H + 1.5 meV/atom (> 0 everywhere).
    for isotope, offset in (("H", 0.0), ("D", 1.5)):
        b["variants"][isotope]["F_eV_cell"] = [
            b["n_atoms"] * (fa/a["n_atoms"] + 1e-3*(offset + ds*(t - tc)))
            for fa, t in zip(a["variants"][isotope]["F_eV_cell"], screen.TEMPS)]
    quantities = screen.pair_quantities(a, b)
    assert quantities["dE_static_meV_atom"] == pytest.approx(0, abs=1e-9)
    assert float(quantities["crossings_H_K"]) == pytest.approx(tc, abs=1e-4)  # CSV keeps 8 significant digits
    assert quantities["crossings_D_K"] == ""
    assert "crossing_H_small_slope_guard" in quantities["flags"]
    assert "linear_dT_blocked_slope_guard" in quantities["flags"]


def test_steep_crossing_has_no_slope_flag(sample):
    plan, _, _, _ = sample
    a, b = result(plan[0]), result(plan[2])
    b["relax"]["energy"] = -1 * b["n_atoms"]
    for isotope in ("H", "D"):
        b["variants"][isotope]["F_eV_cell"] = [
            b["n_atoms"] * (fa/a["n_atoms"] + 0.00005*(t - 200))
            for fa, t in zip(a["variants"][isotope]["F_eV_cell"], screen.TEMPS)]
    quantities = screen.pair_quantities(a, b)
    assert float(quantities["crossings_H_K"]) == pytest.approx(200)
    assert "slope_guard" not in quantities["flags"]


def test_changed_input_hash_is_not_silently_reused(sample):
    plan, pairs, queue, output = sample
    screen.submit_jobs(plan, queue)
    publish(plan[0])
    plan[0]["input_sha256"] = "changed-input"
    rows, _ = screen.collect(plan, pairs, queue, output)
    assert rows[0]["status"] == "quarantined"
    assert rows[0]["reason"] == "input_hash_mismatch"


def test_missing_tables_still_have_stable_schema(sample):
    plan, pairs, queue, output = sample
    rows, _ = screen.collect(plan, pairs, queue, output)
    assert all(r["status"] == "missing" for r in rows)
    assert "S_H_300K_meV_atom_K" in rows[0]
    assert "ZPE_D_meV_atom" in rows[0]
    assert rows[0]["ZPE_D_meV_atom"] == ""


def test_run_retries_failed_job_without_another_submit(sample, monkeypatch):
    plan, _, queue, _ = sample
    screen.submit_jobs(plan[:1], queue)
    pending = next((queue / "pending").glob("*.json"))
    job = json.loads(pending.read_text())
    pending.unlink()
    job["error"] = "failed once"
    (queue / "failed" / f'{job["id"]}.json').write_text(json.dumps(job))
    monkeypatch.setattr(screen.pool, "launch", lambda *a, **k: os.getpid())
    screen.run(queue, control_dir=queue.parent / "control")
    jobs = list((queue / "pending").glob("*.json"))
    assert len(jobs) == 1
    assert json.loads(jobs[0].read_text())["attempts"] == 1


def test_stale_running_attempts_count_toward_retry_limit(sample, monkeypatch):
    plan, _, queue, output = sample
    screen.submit_jobs(plan[:1], queue)
    pending = next((queue / "pending").glob("*.json"))
    job = json.loads(pending.read_text())
    job["attempts"] = 2
    pending.unlink()
    (queue / "running" / f'{job["id"]}__dead.json').write_text(json.dumps(job))
    monkeypatch.setattr(screen.pool, "launch", lambda *a, **k: pytest.fail("exhausted job launched"))
    screen.run(queue, control_dir=queue.parent / "control")
    rows, _ = screen.collect(plan[:1], [], queue, output)
    assert rows[0]["status"] == "quarantined"
    assert not list((queue / "pending").glob("*.json"))


def test_tier_filter_only_schedules_referenced_unique_structures(sample):
    plan, pairs, _, _ = sample
    structures = [dict(struct_id=e["struct_id"], cif=e["cif"], nsites=e["n_atoms"])
                  for e in plan if e["model"] == "mace"]
    extra = dict(pair_id="high", struct_a="b", struct_b="b", tier="32")
    low = dict(pair_id="low", struct_a="a", struct_b="a", tier="16")
    selected = screen.prepare(structures, [low, extra, low], ["mace"], plan[0]["out"].parent, tier=16)
    assert len(selected) == 1
    assert selected[0]["struct_id"] == "a"


def test_invalid_raw_json_is_retained_as_quarantine(sample):
    plan, pairs, queue, output = sample
    plan[0]["out"].parent.mkdir(parents=True)
    plan[0]["out"].write_text('{"partial":')
    rows, pairs_out = screen.collect(plan, pairs, queue, output)
    assert rows[0]["status"] == "quarantined"
    assert "invalid_result" in rows[0]["reason"]
    assert pairs_out[0]["ddF_iso_300K_meV_atom"] == ""


def test_other_failed_queue_does_not_get_mutated_by_dryrun(sample, monkeypatch):
    plan, _, queue, _ = sample
    screen.submit_jobs(plan[:1], queue)
    pending = next((queue / "pending").glob("*.json"))
    job = json.loads(pending.read_text())
    pending.rename(queue / "failed" / pending.name)
    control = queue.parent / "control"
    control.mkdir()
    (control / "workers.json").write_text(json.dumps([
        dict(queue=str(queue.resolve()), calc="sevenn", pid=os.getpid(), started_at=0)]))
    isolated = queue.parent / "dryrun"
    monkeypatch.setattr(screen.pool, "launch", lambda *a, **k: pytest.fail("GPU occupied"))
    screen.run(isolated, control_dir=control)
    assert (queue / "failed" / f'{job["id"]}.json').exists()
    assert not list((queue / "pending").glob("*.json"))


def test_new_configuration_does_not_duplicate_active_output(sample):
    plan, _, queue, _ = sample
    screen.submit_jobs(plan[:1], queue)
    changed = copy.deepcopy(plan[:1])
    changed[0]["kw"]["steps"] = 900
    summary = screen.submit_jobs(changed, queue)
    assert summary["active"] == 1
    assert len(list((queue / "pending").glob("*.json"))) == 1


def test_degenerate_identical_structures_report_no_crossings():
    from src.isoshift_event import screen

    temps = list(screen.TEMPS)
    f = [0.01 * t for t in temps]
    r = {"temps": temps, "relax": {"energy": -10.0},
         "variants": {"H": {"F_eV_cell": f}, "D": {"F_eV_cell": [x * 0.9 for x in f]}}}
    import copy
    a, b = copy.deepcopy(r), copy.deepcopy(r)
    a.update(formula="H2O", n_atoms=3); b.update(formula="H2O", n_atoms=3)
    out = screen.pair_quantities(a, b)
    assert out["crossings_H_K"] == "" and out["crossings_D_K"] == ""
    assert "degenerate_H" in out["flags"] and "degenerate_D" in out["flags"]
