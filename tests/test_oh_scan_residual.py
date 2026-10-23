"""A4b checks: deterministic CPU calculations, no model downloads or GPU."""
import functools
import json
from types import SimpleNamespace

import numpy as np
import pytest
from ase import Atoms
from ase.calculators.calculator import Calculator, all_changes

from src.isoshift_event import oh_scan_residual as M
from src.isoshift_event.pimd import _osc_free_energy


def morse(depth=4.6):
    mu = M.mass_variants()["reduced"]["H"]
    omega = 2 * np.pi * 3600 * M.CM_TO_THZ * 1e-3
    curvature = mu * M.AMU_EV * omega**2
    alpha = np.sqrt(curvature / (2 * depth))
    return lambda x: depth * np.expm1(-alpha * x)**2, curvature


@pytest.fixture(scope="module")
def morse_result():
    potential, curvature = morse()
    return M.analyze_potential(potential, curvature, 0.0)


def test_morse_decision17(morse_result):
    result = morse_result["mass_variants"]["reduced"]
    delta = result["delta_anh_meV"]
    assert delta["16"] == pytest.approx(1.222, abs=0.005)
    assert delta["inf"] == pytest.approx(1.272, abs=0.005)
    assert result["residual_meV"] == pytest.approx(-0.053, abs=0.005)
    assert result["residual_meV"] == pytest.approx(delta["16"] - delta["128"])
    assert morse_result["numerics"]["harmonic_max_error_meV"] < 1e-4
    assert morse_result["numerics"]["edge_probability_max"] < 1e-10
    assert morse_result["numerics"]["converged"]


def test_morse_decision18_not_the_4p6_ev_parameter_set():
    quantum = M.HBAR_EV_FS * 2 * np.pi * M.CM_TO_THZ * 1e-3
    depth = quantum * 3600**2 / (4 * 82)
    potential, curvature = morse(depth)
    result = M.analyze_potential(potential, curvature, 0.0, beads=(16, 96, 128))
    delta = result["mass_variants"]["reduced"]["delta_anh_meV"]
    assert delta["16"] - delta["96"] == pytest.approx(-0.051, abs=0.005)
    assert delta["inf"] == pytest.approx(1.195, abs=0.005)


def test_harmonic_cancels_and_matches_analytic_for_both_mass_variants():
    curvature = morse()[1]
    result = M.analyze_potential(lambda x: 0.5 * curvature * x**2, curvature, 0.0)
    for name, masses in M.mass_variants().items():
        r = result["mass_variants"][name]
        for p in (16, 128, None):
            key = "inf" if p is None else str(p)
            assert abs(r["delta_anh_meV"][key]) < 1e-6
            freqs = {iso: np.sqrt(curvature / (mass * M.AMU_EV)) / (2 * np.pi) * 1000
                     for iso, mass in masses.items()}
            expected = 1000 * (_osc_free_energy(freqs["D"], 300, p)
                               - _osc_free_energy(freqs["H"], 300, p))
            assert r["dF_fit_meV"][key] == pytest.approx(expected, abs=1e-4)
            assert r["harmonic_frequency"]["H"]["THz"] == pytest.approx(freqs["H"])


def test_fit_morse_and_float32_noise_stability():
    x = M.SCAN_DISPLACEMENTS
    potential, _ = morse()
    # Float32 quantisation at the total energies of a production supercell.
    energies = (potential(x) - 800).astype(np.float32).astype(float) + 800
    result = M.analyze_scan(x, energies)
    assert result["status"] == "complete"
    assert abs(result["fit_diagnostics"]["minimum_offset_A"]) < 0.005
    assert result["fit_diagnostics"]["repulsive_branch_monotonic"]
    stability = result["fit_diagnostics"]["stability"]
    assert stability["comparison_degree"] == 8
    assert stability["max_residual_change_meV"] < 0.02
    assert stability["max_frequency_relative_change"] < 0.01
    assert result["mass_variants"]["reduced"]["delta_anh_meV"]["inf"] == pytest.approx(1.272, abs=0.02)


def test_symmetric_double_well_reports_both_wells_and_barrier():
    x = M.SCAN_DISPLACEMENTS
    result = M.analyze_scan(x, 12 * ((x - 0.2)**2 - 0.2**2)**2)
    assert result["status"] == "complete"
    diag = result["fit_diagnostics"]
    assert diag["well_positions_A"] == pytest.approx([0.0, 0.4], abs=1e-6)
    assert diag["barrier_height_eV"] == pytest.approx(12 * 0.2**4, abs=1e-6)
    assert diag["minimum_offset_A"] == pytest.approx(0.0, abs=1e-6)
    assert all(np.isfinite(v["residual_meV"]) for v in result["mass_variants"].values())


def test_shifted_minimum_and_bad_repulsive_branch_are_visible():
    x = M.SCAN_DISPLACEMENTS
    fit = M.fit_potential(x, 20 * (x - 0.08)**2)
    assert fit.minimum == pytest.approx(0.08, abs=1e-7)
    assert "large_minimum_offset" in fit.diagnostics["flags"]
    values = 20 * x**2
    values[0] = values[1] - 0.5
    result = M.analyze_scan(x, values)
    assert not result["fit_diagnostics"]["repulsive_branch_monotonic"]
    assert "nonmonotonic_repulsive_branch" in result["fit_diagnostics"]["flags"]


def test_confining_extension_has_no_extra_well_and_is_c2():
    potential, _ = morse()
    fit = M.fit_potential(M.SCAN_DISPLACEMENTS, potential(M.SCAN_DISPLACEMENTS))
    a, b = fit.diagnostics["fit_range_A"]  # the well window, inside the scan
    assert -0.4 <= a < -0.15 and 0.3 < b <= 0.8
    left = np.linspace(a - 0.8, a, 200)
    right = np.linspace(b, b + 1.2, 200)
    assert np.all(np.diff(fit(left)) < 0)
    assert np.all(np.diff(fit(right)) > 0)
    for endpoint in (a, b):
        eps = 1e-5
        numerical = (fit(endpoint + eps) - fit(endpoint - eps)) / (2 * eps)
        assert numerical == pytest.approx(fit.polynomial.deriv()(endpoint), abs=1e-3)
        curvature = (fit(endpoint + eps) - 2 * fit(endpoint) + fit(endpoint - eps)) / eps**2
        assert curvature == pytest.approx(fit.polynomial.deriv(2)(endpoint), abs=0.03)
    with pytest.raises(ValueError):
        M.fit_potential(M.SCAN_DISPLACEMENTS, -M.SCAN_DISPLACEMENTS)


def test_reference_stays_in_occupied_well_when_other_well_is_deeper():
    x = M.SCAN_DISPLACEMENTS
    # Two wells separated by a maximum near +0.2; the right well is deeper.
    fit = M.fit_potential(x, 12 * ((x - 0.2)**2 - 0.2**2)**2 - 0.01 * x)
    assert len(fit.diagnostics["well_positions_A"]) == 2
    assert fit.minimum < 0.1
    assert fit.diagnostics["well_energies_eV"][1] < fit.diagnostics["well_energies_eV"][0]


def _scan_with_far_well(depth):
    """Donor Morse plus a Gaussian second well centred beyond the +0.8 A endpoint."""
    potential, _ = morse()
    x = M.SCAN_DISPLACEMENTS
    def total(y):
        return potential(y) - depth * np.exp(-((y - 1.1) / 0.25)**2)
    return x, total(x) - total(0.0)


def test_far_high_well_beyond_the_window_is_excluded_not_invalid():
    """A far well behind a barrier more than FIT_WINDOW_EV above the occupied well is outside the fitted window:
    the scan stays usable and the Morse residual is unchanged."""
    x, energies = _scan_with_far_well(3.0)
    assert energies[-1] < energies[-2]
    result = M.analyze_scan(x, energies)
    assert result["status"] == "complete"
    diag = result["fit_diagnostics"]
    assert diag["fit_range_A"][1] < 0.8
    assert result["mass_variants"]["reduced"]["residual_meV"] == pytest.approx(-0.053, abs=0.01)


def test_inward_endpoint_with_accessible_region_stays_invalid():
    potential, _ = morse()
    x = M.SCAN_DISPLACEMENTS
    # Donor plus acceptor Morse at O...O = 3.1 A: the hidden acceptor well past
    # +0.8 A is as deep as the occupied one, so a wall would hide real population.
    def pair(y):
        return potential(y) + potential(3.1 - 2 * 0.97 - y)
    result = M.analyze_scan(x, pair(x) - pair(0.0))
    assert result["status"] == "invalid"
    assert "thermally accessible" in result["error"]
    assert "nonconfining_scan_endpoint" in result["fit_diagnostics"]["flags"]
    assert result["fit_diagnostics"]["truncations"][0]["extrapolated_min_energy_above_well_eV"] < 0.3


def test_underresolved_grid_is_rejected():
    potential, curvature = morse()
    with pytest.raises(ValueError, match="did not converge"):
        M.analyze_potential(potential, curvature, max_grid=20)


def test_cache_loader_preserves_geometry_and_never_guesses(tmp_path, monkeypatch):
    atoms = Atoms("OH", positions=[[0.123, 1.234, 2.345], [1.12, 1.25, 2.38]],
                  cell=[[10, 0, 0], [1, 11, 0], [0.2, 0.3, 12]], pbc=True)
    directory = tmp_path / "unique-cache"
    # Preserve the cached representation: wrapping here moves O by one a vector.
    unit = SimpleNamespace(symbols=atoms.get_chemical_symbols(), cell=atoms.cell.array,
                           scaled_positions=atoms.get_scaled_positions(wrap=False))
    monkeypatch.setattr(M, "find_cache", lambda s: directory)
    def load(key, root):
        assert key == directory.name and root == directory.parent
        return SimpleNamespace(unitcell=unit), {}
    monkeypatch.setattr(M, "load_fc", load)
    actual, name = M.load_structure("mp-23807")
    assert name == directory.name
    np.testing.assert_allclose(actual.positions, atoms.positions, atol=1e-14)
    np.testing.assert_array_equal(actual.cell, atoms.cell)
    def ambiguous(s):
        raise LookupError("2 cache matches")
    monkeypatch.setattr(M, "find_cache", ambiguous)
    with pytest.raises(LookupError, match="2 cache matches"):
        M.load_structure("mp-23807")


def test_symmetry_multiplicities_minimum_image_and_no_acceptor():
    water = Atoms("OH2", positions=[[0, 0, 0], [0.8, 0.6, 0], [-0.8, 0.6, 0]],
                  cell=[12, 12, 12], pbc=True)
    groups = M.distinct_hydrogens(water)
    assert len(groups) == 1 and groups[0]["multiplicity"] == 2
    # An isolated molecule has no second O image; a periodic one does.
    water.pbc = False
    bond = M.assign_bond(water, 1)
    assert bond["donor_O_index"] == 0
    assert bond["acceptor_O_index"] is None
    assert bond["acceptor_O_image_shift"] is None
    assert bond["H_acceptor_A"] is None and bond["angle_deg"] is None
    assert bond["OH_A"] == pytest.approx(1)
    periodic = Atoms("OHO", positions=[[11.5, 1, 1], [0.5, 1, 1], [2, 1, 1]],
                     cell=[12, 12, 12], pbc=True)
    bond = M.assign_bond(periodic, 1)
    assert bond["OO_A"] == pytest.approx(2.5)
    assert bond["angle_deg"] == pytest.approx(180)


@pytest.mark.parametrize("oxygen_x, donor_shift, acceptor_shift", [
    (0.0, [0, 0, 0], [1, 0, 0]),
    (10.0, [-4, 0, 0], [-3, 0, 0]),
])
def test_acceptor_can_be_another_image_of_donor(oxygen_x, donor_shift, acceptor_shift):
    atoms = Atoms("OH", positions=[[oxygen_x, 0, 0], [1, 0, 0]],
                  cell=[[2.5, 0, 0], [1, 12, 0], [0, 0, 12]], pbc=True)
    original = atoms.positions.copy()
    bond = M.assign_bond(atoms, 1)
    assert bond["acceptor_O_index"] == bond["donor_O_index"] == 0
    assert bond["donor_O_image_shift"] == donor_shift
    assert bond["acceptor_O_image_shift"] == acceptor_shift
    assert bond["OH_A"] == pytest.approx(1.0)
    assert bond["H_acceptor_A"] == pytest.approx(1.5)
    assert bond["OO_A"] == pytest.approx(2.5)
    assert bond["angle_deg"] == pytest.approx(180)
    np.testing.assert_allclose(bond["stretch_direction"], [1, 0, 0])
    np.testing.assert_allclose(bond["transfer_direction"], [1, 0, 0])
    np.testing.assert_array_equal(atoms.positions, original)


def test_equidistant_oxygen_images_use_index_then_translation():
    atoms = Atoms("OHO", positions=[[0, 0, 0], [1, 0, 0], [2, 0, 0]],
                  cell=[12, 12, 12], pbc=True)
    bond = M.assign_bond(atoms, 1)
    assert bond["donor_O_index"] == 0 and bond["acceptor_O_index"] == 2
    atoms = Atoms("OH", positions=[[0, 0, 0], [1.25, 0, 0]],
                  cell=[2.5, 12, 12], pbc=True)
    bond = M.assign_bond(atoms, 1)
    assert bond["donor_O_image_shift"] == [0, 0, 0]
    assert bond["acceptor_O_image_shift"] == [1, 0, 0]


def test_scan_cell_enlarges_beyond_cap_and_handles_skew():
    atoms = Atoms("H64", scaled_positions=np.random.default_rng(1).random((64, 3)),
                  cell=[7.32, 7.32, 7.32], pbc=True)
    cell, matrix, distance = M.make_scan_cell(atoms)
    assert len(cell) > 128
    assert distance >= 8
    assert np.array_equal(matrix, np.diag([2, 2, 2]))
    skew = Atoms("OH", positions=[[0, 0, 0], [0, 0, 1]],
                 cell=[[10, 0, 0], [9, 2, 0], [0, 0, 10]], pbc=True)
    cell, _, distance = M.make_scan_cell(skew)
    assert distance >= 8 and M.minimum_image_distance(cell.cell) >= 8


def test_weighting_uses_max_per_h_not_sum_of_overlapping_scans():
    def scan(a, b):
        return {"status": "complete", "mass_variants": {
            "reduced": {"residual_meV": a}, "bare": {"residual_meV": b}}}
    sites = [{"multiplicity": 2, "scans": [scan(-0.1, 0.2), scan(-0.3, 0.1)]},
             {"multiplicity": 1, "scans": [scan(0.6, -0.4)]}]
    weighted = M.aggregate_sites(sites, 3)
    assert weighted["a4b_residual_meV_H"] == pytest.approx(0.4)
    assert weighted["max_abs_residual_meV"] == pytest.approx(0.6)
    assert sites[0]["signed_residuals_meV"] == [-0.1, 0.2, -0.3, 0.1]
    with pytest.raises(AssertionError):
        M.aggregate_sites(sites, 4)
    structures = {s: {"a4b_residual_meV_H": i / 10} for i, s in enumerate(M.SECOND_CHECK_IDS)}
    structures["mp-625152"] = {"a4b_residual_meV_H": 999}
    selected = M.select_second_check(structures)
    assert selected["second_P32_check"] == "JVASP-92228"
    assert set(selected["second_P32_candidates_meV_H"]) == set(M.SECOND_CHECK_IDS)
    del structures["mp-23807"]
    assert M.select_second_check(structures)["second_P32_check"] is None


class AnalyticCalculator(Calculator):
    implemented_properties = ["energy"]

    def __init__(self):
        super().__init__()
        self.isoshift_info = {"name": "fake", "model": "analytic", "version": "1", "device": "cpu"}
        self.origins = {}
        self.moves = []

    def calculate(self, atoms=None, properties=None, system_changes=all_changes):
        super().calculate(atoms, properties, system_changes)
        key = tuple(atoms.numbers)
        initial = self.origins.setdefault(key, atoms.positions.copy())
        displacement = atoms.positions - initial
        moved = np.flatnonzero(np.linalg.norm(displacement, axis=1) > 1e-9)
        assert len(moved) <= 1
        assert all(atoms.numbers[i] == 1 for i in moved)
        self.moves.append(displacement.copy())
        self.results["energy"] = -800 + 20 * float(np.sum(displacement**2))


def test_full_cli_pipeline_and_safe_reuse(tmp_path, monkeypatch):
    short = Atoms("OHO", positions=[[2, 2, 2], [3, 2, 2], [4.5, 2, 2]],
                  cell=[12, 12, 12], pbc=True)
    distant_acceptor = Atoms("OH2", positions=[[2, 2, 2], [2.8, 2.6, 2], [1.2, 2.6, 2]],
                        cell=[12, 12, 12], pbc=True)
    originals = {s: (short if i % 2 == 0 else distant_acceptor).copy() for i, s in enumerate(M.SECOND_CHECK_IDS)}
    calculator = AnalyticCalculator()
    monkeypatch.setattr(M, "load_structure", lambda s: (originals[s].copy(), "synthetic-" + s))
    monkeypatch.setattr(M, "get_calculator", lambda *a, **kw: calculator)
    out = tmp_path / "nested" / "a4b.json"
    args = ["--out", str(out), "--structs", *M.SECOND_CHECK_IDS, "--device", "cpu"]
    assert M.main(args) == 0
    data = json.loads(out.read_text())
    assert data["T_K"] == 300 and data["P"] == [16, 128, "inf"]
    assert data["calculator_info"]["model"] == "analytic"
    assert data["masses_u"]["O"] == 15.999
    assert data["points_evaluated"] == 4 + 2 * 82 + 2 * 41
    assert "stretch-bend" in data["limitations"]
    assert data["second_P32_check"] in M.SECOND_CHECK_IDS
    assert data["git_hash"] and data["wall_time_s"] > 0
    for struct_id, structure in data["structures"].items():
        assert structure["cache_dir_name"] == "synthetic-" + struct_id
        assert structure["min_image_distance_A"] >= 8
        assert structure["n_H"] == sum(h["multiplicity"] for h in structure["distinct_H"])
        assert abs(structure["a4b_residual_meV_H"]) < 1e-5
        for site in structure["distinct_H"]:
            assert {s["type"] for s in site["scans"]} == (
                {"stretch", "transfer"} if site["OO_A"] is not None and site["OO_A"] < 2.7
                else {"stretch"})
            for scan in site["scans"]:
                assert len(scan["raw_energies_eV"]) == 41
                assert scan["displacements_A"] == pytest.approx(np.linspace(-0.4, 0.8, 41))
                assert scan["raw_energies_eV"] == pytest.approx(20 * M.SCAN_DISPLACEMENTS**2, abs=1e-10)
                assert set(scan["mass_variants"]) == {"bare", "reduced"}
    calls = len(calculator.moves)
    assert M.main(args) == 0
    assert len(calculator.moves) == calls
    assert json.loads(out.read_text())["points_evaluated"] == 0
    # A changed cell invalidates reuse even though the cached name is unchanged.
    originals[M.SECOND_CHECK_IDS[0]].cell[2, 2] += 0.1
    assert M.main(args) == 0
    assert len(calculator.moves) == calls + 83
    calls = len(calculator.moves)
    calculator.isoshift_info["version"] = "2"
    assert M.main(args) == 0
    assert len(calculator.moves) == calls + 250


def test_subset_rerun_keeps_every_other_structure(tmp_path, monkeypatch):
    short = Atoms("OHO", positions=[[2, 2, 2], [3, 2, 2], [4.5, 2, 2]],
                  cell=[12, 12, 12], pbc=True)
    distant_acceptor = Atoms("OH2", positions=[[2, 2, 2], [2.8, 2.6, 2], [1.2, 2.6, 2]],
                             cell=[12, 12, 12], pbc=True)
    originals = {s: (short if i % 2 == 0 else distant_acceptor).copy() for i, s in enumerate(M.SECOND_CHECK_IDS)}
    calculator = AnalyticCalculator()
    monkeypatch.setattr(M, "load_structure", lambda s: (originals[s].copy(), "synthetic-" + s))
    monkeypatch.setattr(M, "get_calculator", lambda *a, **kw: calculator)
    out = tmp_path / "a4b.json"
    assert M.main(["--out", str(out), "--structs", *M.SECOND_CHECK_IDS, "--device", "cpu"]) == 0
    full = json.loads(out.read_text())
    calls = len(calculator.moves)
    retry = M.SECOND_CHECK_IDS[2]

    assert M.main(["--out", str(out), "--structs", retry, "--device", "cpu"]) == 0
    data = json.loads(out.read_text())
    assert len(calculator.moves) == calls
    assert list(data["structures"]) == list(M.SECOND_CHECK_IDS)
    assert data["second_P32_check"] == full["second_P32_check"] is not None
    assert data["second_P32_candidates_meV_H"] == full["second_P32_candidates_meV_H"]
    assert data["requested_structures"] == [retry] and len(data["run_history"]) == 2
    for struct_id, structure in data["structures"].items():
        assert structure["status"] == "complete"
        assert structure.get("carried_over", False) == (struct_id != retry)
        assert ([scan["raw_energies_eV"] for h in structure["distinct_H"] for scan in h["scans"]]
                == [scan["raw_energies_eV"] for h in full["structures"][struct_id]["distinct_H"]
                    for scan in h["scans"]])

    # A carried structure whose geometry changed keeps its raw data but loses its value.
    moved = M.SECOND_CHECK_IDS[0]
    originals[moved].cell[2, 2] += 0.1
    assert M.main(["--out", str(out), "--structs", retry, "--device", "cpu"]) == 1
    data = json.loads(out.read_text())
    assert len(calculator.moves) == calls
    stale = data["structures"][moved]
    assert stale["status"] == "stale" and stale["a4b_residual_meV_H"] is None
    assert stale["previous_status"] == "complete"
    assert stale["distinct_H"][0]["scans"][0]["raw_energies_eV"] == pytest.approx(20 * M.SCAN_DISPLACEMENTS**2)
    assert data["second_P32_check"] is None and len(data["structures"]) == 4

    # A budget stop on a rescan keeps the saved raw energies of that structure too.
    monkeypatch.setattr(M, "ScanBudget", functools.partial(M.ScanBudget, limit_s=0.0))
    assert M.main(["--out", str(out), "--structs", moved, "--device", "cpu"]) == 1
    data = json.loads(out.read_text())
    assert data["status"] == "budget_exhausted" and len(data["structures"]) == 4
    assert data["structures"][moved]["status"] == "budget_exhausted"
    assert data["structures"][moved]["distinct_H"][0]["scans"][0]["raw_energies_eV"]
    assert data["structures"][retry]["status"] == "complete"


def test_same_oxygen_image_triggers_transfer_scan():
    atoms = Atoms("OH", positions=[[0, 0, 0], [1, 0, 0]],
                  cell=[2.5, 12, 12], pbc=True)
    calculator = AnalyticCalculator()
    result = M.scan_structure(atoms, "synthetic", calculator, calculator.isoshift_info,
                              M.ScanBudget())
    assert result["status"] == "complete"
    site, = result["distinct_H"]
    assert site["donor_O_index"] == site["acceptor_O_index"] == 0
    assert site["OO_A"] == pytest.approx(2.5)
    assert [scan["type"] for scan in site["scans"]] == ["stretch", "transfer"]
    assert result["points_evaluated"] == 83
    assert abs(result["a4b_residual_meV_H"]) < 1e-5
    for scan in site["scans"]:
        assert len(scan["raw_energies_eV"]) == 41
        assert scan["raw_energies_eV"] == pytest.approx(20 * M.SCAN_DISPLACEMENTS**2, abs=1e-10)


def test_budget_stops_before_calculator_call():
    calculator = AnalyticCalculator()
    atoms = Atoms("H", positions=[[0, 0, 0]])
    atoms.calc = calculator
    budget = M.ScanBudget(limit_s=0)
    with pytest.raises(M.ScanBudgetExceeded):
        budget.energy(atoms)
    assert not calculator.moves


def test_invalid_scan_cannot_produce_selection_value():
    sites = [{"multiplicity": 1, "scans": [{"status": "invalid", "error": "bad branch"}]}]
    result = M.aggregate_sites(sites, 1)
    assert result["status"] == "invalid" and result["a4b_residual_meV_H"] is None


def test_invalid_cli_id_is_rejected_before_loading_model(monkeypatch):
    monkeypatch.setattr(M, "get_calculator", lambda *a, **k: pytest.fail("model should not load"))
    with pytest.raises(SystemExit):
        M.main(["--structs", "not-a-p12-id"])


@pytest.mark.parametrize("amplitude", [20.0, 50.0])
def test_steep_short_range_wall_does_not_corrupt_the_well(amplitude):
    """Review case (24 Oct): Morse plus a steep wall amplitude*exp(-(x+0.4)/0.06) at the scan edge. A global fit
    returned -0.064 (20 eV) and -2.59 meV (50 eV) against exact +0.27 and +0.50 and still said complete. The
    well-window fit must reproduce the exact residual, or refuse."""
    potential, curvature = morse()
    wall = lambda x: amplitude * np.exp(-(np.asarray(x) + 0.4) / 0.06)
    from scipy.optimize import minimize_scalar
    total = lambda x: potential(x) + wall(x)
    x_min = minimize_scalar(total, bounds=(-0.2, 0.2), method="bounded", options={"xatol": 1e-10}).x
    e = 1e-4
    k = (total(x_min + e) - 2 * total(x_min) + total(x_min - e)) / e**2
    exact = M.analyze_potential(lambda x: total(x) - total(x_min), k, x_min)
    x = M.SCAN_DISPLACEMENTS
    result = M.analyze_scan(x, potential(x) + wall(x))
    assert result["status"] == "complete"
    for name, v in result["mass_variants"].items():
        # the bound that enters s_P never understates the exact residual by more than 0.01 meV
        assert v["residual_bound_meV"] >= abs(exact["mass_variants"][name]["residual_meV"]) - 0.01
        assert v["residual_meV"] == pytest.approx(exact["mass_variants"][name]["residual_meV"], abs=0.05)


def test_unstable_fit_is_not_usable():
    rng = np.random.default_rng(3)
    potential, _ = morse()
    x = M.SCAN_DISPLACEMENTS
    result = M.analyze_scan(x, potential(x) + 5e-2 * rng.standard_normal(len(x)))  # 1000x float32 noise
    assert result["status"] != "complete"
    agg = M.aggregate_sites([{"multiplicity": 1, "scans": [result]}], 1)
    assert agg["status"] == "invalid" and agg["a4b_residual_meV_H"] is None
