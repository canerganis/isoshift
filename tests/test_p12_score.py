"""CPU-only P12 verdicts against hand-computed, independent synthetic runs."""
import csv
import hashlib
import json
from pathlib import Path

import pytest

from src.isoshift_event import p12_score as S


REPO = Path(__file__).resolve().parents[1]
PAIRS = [
    ("mp-23807", "mp-625054", 5.03),
    ("JVASP-54682", "JVASP-92228", 6.00),
    ("mp-23807", "mp-625152", 3.07),
    ("mp-626497", "mp-985293", 1.50),
    ("mp-23940", "mp-626000", 5.80),
]
INTERPOLATED = {"mp-625054", "JVASP-54682", "JVASP-92228"}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")


def run(struct, beads, delta=0.0, sigma=0.1, seed=None):
    monitors = {key: True for key in (
        "heavy_rmsd_ok", "coordination_unchanged", "retention_ok",
        "imaginary_retention_ok", "heavy_rmsd_pooled_ok",
        "coordination_pooled_unchanged", "imaginary_retention_pooled_ok")}
    return {
        "struct_id": struct, "P": beads, "status": "complete",
        "delta_anh_meV_H": delta, "delta_anh_err_meV_H": sigma,
        "dF_PIMD_meV_H": delta - 80, "dF_PIMD_err_meV_H": sigma,
        "harmonic_bead_error_meV_H": 2.0, "error_converged": True,
        "stationarity_ok": True, "fc_interpolation_verified": True,
        "invalid_reference": False, "initial_max_abs_F_eV_A": 0.0001,
        "s_imag_meV_H": 0.0, "seconds_per_ring_step": 1.23 * beads / 16,
        # real run_args keys (pimd.py document()); run_pilot.sh dumps at P16 for C2 and not at P32
        "run_args": {"beads": beads, "steps": 3000, "dt": 0.25, "T": 300.0, "tau0": 100.0,
                     "masses_points": 4, "equil": 0.2, "seed": beads if seed is None else seed,
                     "backend": "mace", "bead_chunk": 4, "splitting": "baoab", "dtype": "float32",
                     "device": "cuda", "init": "harmonic", "pre_equil": 1000,
                     "stationarity_extension": 3000, "dump_every": 30 if beads == 16 else 0,
                     "allow_invalid_reference": False, "hessian_check": "auto",
                     "state_root": "C:\\cache\\pimd", "monitor_schema": "time-averaged-centroid-v2"},
        "hessian_check": ({"diff_meV_H": -0.01, "diff_P_meV_H": 0.02,
                           "passed": True} if struct in INTERPOLATED else None),
        "monitors": monitors,
        "points": [{"tau_int_steps": 24, "stationarity_ok": True,
                    "error_converged": True, "monitors": dict(monitors)} for _ in range(4)],
    }


@pytest.fixture
def tree(tmp_path):
    results = tmp_path / "results"
    pimd = results / "pimd"
    pimd.mkdir(parents=True)
    with (results / "decompose_pairs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pair_id", "model", "ddF_total", "H_per_atom"])
        writer.writeheader()
        for b, a, harmonic in PAIRS:
            writer.writerow(dict(pair_id=f"{b}__{a}", model="mace",
                                 ddF_total=harmonic / 4, H_per_atom=0.25))
    ids = {s for b, a, _ in PAIRS for s in (b, a)}
    controls = {
        "pass": True, "s_quad_meV_H": 0.01,
        "s_dt_meV_H_by_P": {str(p): 0.06 for p in (16, 24, 32)},
        # schema of the real controls_cpu.json: C1 on mp-23807 and mp-625152, plus FeOOH at P24/P32
        "C1_by_P": {str(p): {s: {"pass": True} for s in ("mp-23807", "mp-625152")
                             + (("JVASP-54682", "JVASP-92228") if p > 16 else ())} for p in (16, 24, 32)},
        "C4_by_P": {str(p): {"pass": True} for p in (16, 24, 32)},
    }
    write(pimd / "controls_cpu.json", controls)
    write(pimd / "c2_mp-625152_P16.json",
          {"P": 16, "pass": True, "stop_and_reconvene": False, "s_f32_meV_H": 0.02})
    write(pimd / "a4b_scan_residual.json", {"structures": {
        s: {"a4b_bound_meV_H": {str(p): 0.05 for p in (16, 24, 32)},
            "a4b_plateau_sensitivity_meV_H": {str(p): 0.04 for p in (16, 24, 32)}}
        for s in ids}})
    for s in ids:
        for p in (16, 24, 32):
            write(pimd / f"{s}_P{p}.json", run(s, p))
    write(pimd / "pair2_beads.json", {"P": 32})
    return tmp_path


def change(tree, name, update):
    path = tree / "results" / "pimd" / name
    obj = json.loads(path.read_text())
    update(obj)
    write(path, obj)


def pair(tree, number=1):
    return S.score(tree)["pairs"][number - 1]


@pytest.mark.parametrize("delta,category", [(0, "supported"), (-6, "challenged"), (-5.03, "unresolved")])
def test_orientation_and_resolved_categories(tree, delta, category):
    change(tree, "mp-23807_P16.json", lambda d: d.update(delta_anh_meV_H=delta))
    p = pair(tree)
    assert p["category"] == category
    assert p["correction_meV_H"] == delta
    assert p["ddF_corr_meV_H"] == pytest.approx(5.03 + delta)
    assert p["B_pair_meV_H"] == pytest.approx(0.21)
    assert p["E_pair_meV_H"] == pytest.approx(0.4871858582251267)
    assert p["structures"]["a"]["s_hess_meV_H"] == 0.02


@pytest.mark.parametrize("P,F,A,d,sd,fe,sfe,want,term", [
    (16, False, .1, .4, .1, None, None, .3, "pilot"),
    (16, False, .01, .01, .1, None, None, .05, "floor"),
    (32, False, .1, .4, .1, None, None, .15, "pilot"),
    (32, False, .1, .4, .1, .8, .2, .3, "Fe_pilot"),
    (24, False, .1, .4, .1, .8, .2, .3, "pilot"),
    (32, True, .1, .8, .3, 9, .1, .4, "branch_F_pilot"),
    (16, False, .6, .4, .1, None, None, .6, "A4b"),
])
def test_s_p_registered_formulas(P, F, A, d, sd, fe, sfe, want, term):
    out = S.bead_allowance(P, A, d, sd, branch_f=F, d_fe=fe, sigma_d_fe=sfe)
    assert out["value_meV_H"] == pytest.approx(want)
    assert term in out["setting_terms"]


@pytest.mark.parametrize("d,sigma,F", [(.299, .01, False), (.3, .01, False),
    (.301, .01, True), (.39, .2, False), (.392, .2, False), (.393, .2, True), (-.4, .1, True)])
def test_pilot_strict_thresholds(d, sigma, F):
    lo, hi = run("mp-625152", 16, sigma=0), run("mp-625152", 32, delta=d, sigma=sigma)
    out = S.pilot_decision(lo, hi)
    assert out["branch_F"] is F
    assert out["sigma_d_meV_H"] == sigma
    assert out["rates"]["32"]["rate_factor"] == 1


@pytest.mark.parametrize("tau,T", [(24, False), (25, True)])
def test_pilot_tau_threshold(tau, T):
    lo = run("mp-625152", 16)
    lo["points"][0]["tau_int_steps"] = tau
    assert S.pilot_decision(lo, run("mp-625152", 32))["branch_T"] is T


def test_pilot_refuses_shared_seed_and_nonfactor_two():
    with pytest.raises(ValueError, match="seed"):
        S.pilot_decision(run("mp-625152", 16, seed=7), run("mp-625152", 32, seed=7))
    with pytest.raises(ValueError):
        S.pilot_decision(run("mp-625152", 16), run("mp-625152", 24))


@pytest.mark.parametrize("field,value,reason", [
    ("stationarity_ok", False, "stationarity"),
    ("error_converged", False, "statistical error"),
    ("fc_interpolation_verified", False, "interpolation"),
    ("hessian_check", None, "Hessian"),
    ("hessian_check", {"passed": False, "diff_meV_H": .01, "diff_P_meV_H": .02}, "Hessian"),
    ("hessian_check", {"passed": True, "diff_meV_H": -.1, "diff_P_meV_H": .02}, "Hessian"),
    ("delta_anh_meV_H", None, "Delta_anh"),
])
def test_run_gates(tree, field, value, reason):
    change(tree, "mp-625054_P16.json", lambda d: d.update({field: value, "delta_anh_unchecked_meV_H": 100}))
    p = pair(tree)
    assert p["category"] == "inconclusive"
    assert any(reason in r for r in p["reasons"])
    if field == "delta_anh_meV_H":
        assert p["ddF_corr_meV_H"] is None
    assert S.score(tree)["H2"]["1"]["category"] == "not assessed"


@pytest.mark.parametrize("scope,key", [
    ("monitors", "heavy_rmsd_ok"), ("monitors", "coordination_unchanged"),
    ("monitors", "retention_ok"), ("monitors", "heavy_rmsd_pooled_ok"),
    ("monitors", "coordination_pooled_unchanged"), ("monitors", "imaginary_retention_pooled_ok"),
    ("point", "stationarity_ok"), ("point", "error_converged"),
    ("point_monitor", "retention_ok"), ("point_monitor", "heavy_rmsd_ok"),
])
def test_per_point_and_pooled_failures_cannot_be_hidden(tree, scope, key):
    def fail(d):
        target = d["monitors"] if scope == "monitors" else d["points"][0]
        if scope == "point_monitor":
            target = target["monitors"]
        target[key] = False
    change(tree, "mp-625054_P16.json", fail)
    assert pair(tree)["category"] == "inconclusive"


@pytest.mark.parametrize("gate,missing", [("C1", False), ("C1", True), ("C4", False), ("C4", True),
                                          ("C2", False), ("C2", True), ("controls", False)])
def test_controls_required_at_selected_p(tree, gate, missing):
    if gate == "C2":
        path = tree / "results/pimd/c2_mp-625152_P16.json"
        if missing:
            path.unlink()
        else:
            change(tree, path.name, lambda d: d.update({"pass": False}))
    else:
        def fail(d):
            if gate == "controls":
                d["pass"] = False
            elif missing:
                d[f"{gate}_by_P"].pop("16")
            elif gate == "C1":
                d["C1_by_P"]["16"]["mp-625152"]["pass"] = False
            else:
                d["C4_by_P"]["16"]["pass"] = False
        change(tree, "controls_cpu.json", fail)
    assert pair(tree)["category"] == "inconclusive"


def test_stop_and_reconvene_overrides_c2_pass(tree):
    change(tree, "c2_mp-625152_P16.json", lambda d: d.update(stop_and_reconvene=True))
    out = S.score(tree)
    assert out["stop_and_reconvene"] is True
    assert out["pairs"][0]["category"] == "inconclusive"


@pytest.mark.parametrize("missing", [True, False])
def test_not_run_for_missing_or_partial(tree, missing):
    if missing:
        (tree / "results/pimd/mp-625054_P16.json").unlink()
    else:
        change(tree, "mp-625054_P16.json", lambda d: d.update(status="partial"))
    assert pair(tree)["category"] == "not run"


@pytest.mark.parametrize("field,value", [("invalid_reference", True), ("initial_max_abs_F_eV_A", .00101)])
def test_invalid_reference_has_own_category(tree, field, value):
    change(tree, "mp-23940_P16.json", lambda d: d.update({field: value, "delta_anh_meV_H": None}))
    assert pair(tree, 5)["category"] == "invalid reference"
    assert S.score(tree)["H4"]["reason"]


def test_mixed_p_raises(tree):
    change(tree, "mp-625054_P16.json", lambda d: d.update(P=32))
    with pytest.raises(ValueError, match="P"):
        S.score(tree)


def test_main_branch_uses_p16_for_pair3_and_diagnostic_only_for_fe_allowance(tree):
    change(tree, "mp-625152_P32.json", lambda d: d.update(delta_anh_meV_H=.2))
    change(tree, "JVASP-54682_P16.json", lambda d: d.update(delta_anh_meV_H=-.8))
    out = S.score(tree)
    assert out["pairs"][2]["correction_meV_H"] == 0
    assert out["pairs"][1]["correction_meV_H"] == 0
    assert out["pairs"][1]["P"] == 32
    assert out["diagnostics"][0]["diagnostic"] is True
    assert out["pilot"]["d_Fe_meV_H"] == .8
    assert "Fe_pilot" in out["pairs"][1]["structures"]["a"]["s_P"]["setting_terms"]
    assert "Fe_pilot" not in out["pairs"][0]["structures"]["a"]["s_P"]["terms_meV_H"]


def test_branch_f_and_pair2_p24_selection(tree):
    change(tree, "pair2_beads.json", lambda d: d.update(P=24))
    assert pair(tree, 2)["P"] == 24
    change(tree, "mp-625152_P32.json", lambda d: d.update(delta_anh_meV_H=.5))
    out = S.score(tree)
    assert out["branch"] == "F"
    assert [p["P"] for p in out["pairs"][:3]] == [32, 32, 32]
    assert [p["category"] for p in out["pairs"][3:]] == ["not run", "not run"]
    assert out["pairs"][2]["correction_meV_H"] == -.5


def test_fit_sensitivity_never_rescues_primary_category(tree):
    def inflate(d):
        d["structures"]["mp-625054"]["a4b_bound_meV_H"]["16"] = .7
    change(tree, "a4b_scan_residual.json", inflate)
    p = pair(tree)
    assert p["E_pair_meV_H"] > 1
    assert p["E_pair_plateau_meV_H"] < 1
    assert p["category"] == "inconclusive"
    assert p["inconclusive_only_fit_allowance"] is True
    change(tree, "mp-625054_P16.json", lambda d: d.update(stationarity_ok=False))
    assert pair(tree)["inconclusive_only_fit_allowance"] is False


def test_h1_counts_covariance_and_exploratory_signs(tree):
    out = S.score(tree)
    assert out["H1"]["category"] == "supported"
    assert out["H1"]["counts"]["supported"] == out["H1"]["denominator"] == 3
    assert out["covariance"]["cov_meV_H_squared"] == pytest.approx(.01)
    assert out["covariance"]["correlation"] == pytest.approx(.5)
    change(tree, "mp-625054_P16.json", lambda d: d.update(status="partial"))
    out = S.score(tree)
    assert out["H1"]["category"] == "undecided"
    assert out["H1"]["counts"]["not run"] == 1
    change(tree, "mp-23807_P16.json", lambda d: d.update(delta_anh_meV_H=-6))
    assert S.score(tree)["H1"]["category"] == "challenged"
    change(tree, "mp-626497_P16.json", lambda d: d.update(delta_anh_meV_H=-.75))
    out = S.score(tree)
    assert out["H3"]["correction"]["sign"] == "negative"
    assert out["H3"]["correction"]["resolved"] is True
    assert out["H3"]["toward_rule_negative"] is True
    assert out["H3"]["ddF_corr"]["sign"] == "positive"


@pytest.mark.parametrize("correction,want", [(0, "supported"), (2.515, "unresolved"), (4, "exceeded")])
def test_h2_three_outcomes(tree, correction, want):
    change(tree, "mp-23807_P16.json", lambda d: d.update(delta_anh_meV_H=correction))
    assert S.score(tree)["H2"]["1"]["category"] == want


def test_real_a12_and_swapped_orientation(tree):
    assert list(S.harmonic_values(REPO / "results/decompose_pairs.csv").values()) == pytest.approx(
        [5.03, 6, 3.07, 1.5, 5.8], abs=.01)
    path = tree / "results/decompose_pairs.csv"
    path.write_text(path.read_text().replace("mp-23807__mp-625054", "mp-625054__mp-23807"))
    with pytest.raises(ValueError, match="A12"):
        S.harmonic_values(path)


def test_cli_outputs_provenance_and_pilot(tree, capsys):
    out_path = tree / "scores.json"
    assert S.main(["score", "--root", str(tree), "--out", str(out_path)]) == 0
    out = json.loads(out_path.read_text())
    assert "| pair | P |" in capsys.readouterr().out
    harmonic = tree / "results/decompose_pairs.csv"
    assert any(i["sha256"] == hashlib.sha256(harmonic.read_bytes()).hexdigest() for i in out["inputs"])
    assert out["rule_texts"] and "git_hash" in out
    pilot_path = tree / "pilot.json"
    assert S.main(["pilot", "--root", str(tree), "--out", str(pilot_path)]) == 0
    assert json.loads(pilot_path.read_text())["branch"] == "main"


def test_current_tree_is_readable_without_writing_outputs(capsys):
    out = S.score(REPO)
    assert len(out["pairs"]) == 5
    json.dumps(out, allow_nan=False)
    assert S.main(["score", "--root", str(REPO), "--no-write"]) == 0
    assert "H1:" in capsys.readouterr().out


def test_error_budget_all_terms_and_matching_p_controls(tree):
    change(tree, "pair2_beads.json", lambda d: d.update(P=24))
    change(tree, "controls_cpu.json", lambda d: d["s_dt_meV_H_by_P"].update({"24": .08}))
    change(tree, "JVASP-54682_P24.json", lambda d: d.update(s_imag_meV_H=.03))
    change(tree, "JVASP-92228_P24.json", lambda d: d.update(s_imag_meV_H=.04))
    p = pair(tree, 2)
    # .08 + .02 + .01 + .05 + .05 + .02 + .02 + .03 + .04
    assert p["B_pair_meV_H"] == pytest.approx(.32)
    assert p["E_pair_meV_H"] == pytest.approx(.5971858582251267)
    change(tree, "controls_cpu.json", lambda d: d["C4_by_P"]["24"].update({"pass": False}))
    assert pair(tree, 2)["category"] == "inconclusive"


def test_missing_pilot_does_not_grant_support(tree):
    (tree / "results/pimd/mp-625152_P32.json").unlink()
    out = S.score(tree)
    assert out["branch"] == "pending"
    assert out["H1"]["counts"]["supported"] == 0


def test_saved_pilot_cannot_bypass_shared_seed_check(tree):
    write(tree / "results/pimd/pilot_decision.json", {
        "branch": "main", "d_meV_H": 0, "sigma_d_meV_H": .2, "tau_int_steps": 24})
    change(tree, "mp-625152_P32.json", lambda d: d["run_args"].update(seed=16))
    with pytest.raises(ValueError, match="seed"):
        S.score(tree)


def test_unavailable_diagnostic_does_not_prevent_pair2_score(tree):
    (tree / "results/pimd/JVASP-54682_P16.json").unlink()
    p = pair(tree, 2)
    assert p["category"] == "supported"
    assert "Fe_pilot" not in p["structures"]["b"]["s_P"]["terms_meV_H"]


def test_nonfinite_json_cannot_produce_support(tree):
    path = tree / "results/pimd/mp-23807_P16.json"
    doc = json.loads(path.read_text())
    doc["delta_anh_meV_H"] = float("nan")
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="finite|NaN"):
        S.score(tree)


def test_exploratory_measurement_remains_visible_when_inconclusive(tree):
    change(tree, "mp-626497_P16.json", lambda d: d.update(delta_anh_meV_H=-.75, stationarity_ok=False))
    out = S.score(tree)
    assert out["pairs"][3]["category"] == "inconclusive"
    assert out["H3"]["category"] == "not assessed"
    assert out["H3"]["correction"]["sign"] == "negative"
    assert out["H3"]["correction"]["resolved"] is False
    assert out["H3"]["reason"]


def test_cli_stop_banner_and_no_write(tree, capsys):
    change(tree, "c2_mp-625152_P16.json", lambda d: d.update(stop_and_reconvene=True))
    out = tree / "must_not_exist.json"
    S.main(["score", "--root", str(tree), "--no-write", "--out", str(out)])
    assert not out.exists()
    assert "STOP AND RECONVENE" in capsys.readouterr().out


@pytest.mark.parametrize("P", [16, 32])
def test_invalid_fe_comparison_is_reported_without_using_unchecked_delta(tree, P):
    change(tree, f"JVASP-54682_P{P}.json", lambda d: d.update(
        delta_anh_meV_H=None, delta_anh_unchecked_meV_H=123, fc_interpolation_verified=False))
    out = S.score(tree)
    assert out["pairs"][1]["category"] == "inconclusive"
    assert out["pilot"]["d_Fe_meV_H"] is None
    assert out["pilot"]["Fe_comparison_unavailable"]


def test_invalid_pair2_p_is_not_silently_selected_from_available_runs(tree):
    change(tree, "pair2_beads.json", lambda d: d.update(P=16))
    with pytest.raises(ValueError, match="P24/P32"):
        S.score(tree)


def test_explicit_pair2_omission_is_not_run_even_with_existing_results(tree):
    change(tree, "pair2_beads.json", lambda d: d.update(P=None))
    p = pair(tree, 2)
    assert p["category"] == "not run"
    assert p["ddF_corr_meV_H"] is None


def test_c1_is_a_control_at_the_pairs_p_not_per_structure(tree):
    out = S.score(tree)
    # pairs 1, 4, 5 have no C1 entry of their own at P16 and are still scoreable
    assert [p["category"] for p in out["pairs"]] == ["supported"] * 5
    assert not any("C1" in r for p in out["pairs"] for r in p["reasons"])
    change(tree, "controls_cpu.json", lambda d: d["C1_by_P"]["32"].pop("JVASP-92228"))
    p = pair(tree, 2)
    assert p["category"] == "inconclusive"
    assert "C1 P32 JVASP-92228 (own FC cell) missing" in p["reasons"]
    change(tree, "controls_cpu.json", lambda d: d["C1_by_P"].update({"16": {}}))
    assert "C1 P16 missing" in pair(tree, 1)["reasons"]


def test_real_controls_file_lets_h1_pairs_score(tree):
    real = (REPO / "results/pimd/controls_cpu.json").read_text(encoding="utf-8")
    (tree / "results/pimd/controls_cpu.json").write_text(real, encoding="utf-8")
    out = S.score(tree)
    assert [p["category"] for p in out["pairs"]] == ["supported"] * 5
    assert out["H1"]["category"] == "supported"


def test_pilot_ignores_dump_every_but_not_physics_run_args():
    lo, hi = run("mp-625152", 16), run("mp-625152", 32)
    assert (lo["run_args"]["dump_every"], hi["run_args"]["dump_every"]) == (30, 0)
    hi["run_args"].update(bead_chunk=8, state_root="D:\\other")
    out = S.pilot_decision(lo, hi)
    assert out["branch"] == "main"
    assert out["comparison"]["ignored_diagnostic_run_args"]["dump_every"] == [30, 0]
    hi["run_args"]["dtype"] = "float64"
    with pytest.raises(ValueError, match="physics run_args"):
        S.pilot_decision(lo, hi)
    hi["run_args"]["dtype"] = "float32"
    hi["run_args"]["hessian_check"] = "off"
    with pytest.raises(ValueError, match="differ"):
        S.pilot_decision(lo, hi)


def test_score_runs_when_pilot_runs_differ_in_dump_every(tree):
    out = S.score(tree)
    assert out["pilot"]["status"] == "complete"
    assert out["pilot"]["comparison"]["ignored_diagnostic_run_args"] == {"dump_every": [30, 0]}
    assert out["pilot"]["Fe_comparison"]["ignored_diagnostic_run_args"] == {"dump_every": [30, 0]}


def test_run_at_another_temperature_is_rejected():
    with pytest.raises(ValueError, match="not 300.0 K"):
        S._identity({"struct_id": "mp-23807", "P": 16, "T_K": 600.0, "run_args": {"beads": 16, "T": 600.0}},
                    "mp-23807", 16)
    with pytest.raises(ValueError, match="missing"):
        S._identity({"struct_id": "mp-23807", "P": 16, "run_args": {"beads": 16}}, "mp-23807", 16)
    S._identity({"struct_id": "mp-23807", "P": 16, "T_K": 300.0, "run_args": {"beads": 16, "T": 300.0}}, "mp-23807", 16)
