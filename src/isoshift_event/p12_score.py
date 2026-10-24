"""CPU-only P12 scoring, frozen by P12 A1--A15 and decisions 18/19.

python -m src.isoshift_event.p12_score pilot
python -m src.isoshift_event.p12_score score --no-write

The public ``score`` function is read-only. Only the CLI writes the requested
report. Partial runs and unavailable controls are evidence gaps, never passes.
All energies and uncertainties below are meV per H unless explicitly labelled.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
# A12: first label member is b, second is a. Do not infer from the label header.
PAIRS = (
    ("mp-23807", "mp-625054", 5.03, 1.85),
    ("JVASP-54682", "JVASP-92228", 6.00, 3.62),
    ("mp-23807", "mp-625152", 3.07, .84),
    ("mp-626497", "mp-985293", 1.50, -.74),
    ("mp-23940", "mp-626000", 5.80, -.32),
)
INTERPOLATED = {"mp-625054", "JVASP-54682", "JVASP-92228"}
CATEGORIES = ("not run", "invalid reference", "inconclusive", "supported", "challenged", "unresolved")
RULE_TEXTS = {
    "orientation": "A12: ddF_harm = ddF_total/H_per_atom (mace), b first, a second; ddF_corr = ddF_harm + Delta_b - Delta_a.",
    "F": "A4: branch F iff abs(d) > 0.3 and abs(d) > 1.96*sigma_d; d = Delta_32 - Delta_16 on mp-625152, independent seeds.",
    "T": "A6: branch T iff first GL point tau_int of mp-625152 P16 > 24 steps; 4000 rather than 3000 steps per point.",
    "rate": "f = seconds_per_ring_step / (1.23 seconds * P/16), chunk-4 mp-625152 smoke-test reference.",
    "selection": "Main/T: pairs 1,3,4,5 at P16; pair 2 at preselected P32 or P24 (default P32, decision 19). F: pairs 1,2,3 at P32; pairs 4,5 not run. Fe P16 is diagnostic only.",
    "s_P16": "max(0.05, A_i(16), max(0, abs(d)-sigma_d))",
    "s_P32_main": "max(0.05, A_i(32), max(0, abs(d)-sigma_d)/2, max(0, abs(d_Fe)-sigma_dFe)/2); Fe term only for pair 2 if row 8 ran.",
    "s_P24": "max(0.05, A_i(24), max(0, abs(d)-sigma_d))",
    "s_P_F": "max(0.05, A_i(32), abs(d)/2)",
    "C1": "C1 at the pair's P: C1_by_P[P] present, non-empty, every entry pass; pair 2 also needs its two FeOOH entries.",
    "s_hess": "For mp-625054, JVASP-54682, JVASP-92228: max(abs(diff_meV_H), abs(diff_P_meV_H)), matching the pimd Hessian gate; otherwise 0.",
    "error": "sigma_pair = hypot(sigma_a,sigma_b); B_pair = s_dt+s_f32+s_quad+s_P,a+s_P,b+s_hess,a+s_hess,b+s_imag,a+s_imag,b; E_pair = 1.96*sigma_pair+B_pair. Shared allowances counted once per pair.",
    "category": "Missing/partial: not run; A13 invalid or force > 1e-3 eV/A: invalid reference; failed/missing gate or E_pair > 1: inconclusive; abs(ddF_corr) > E_pair: supported if harmonic sign, challenged otherwise; else unresolved.",
    "H1": "Pairs 1-3, denominator 3: all supported => supported; any challenged => challenged; otherwise undecided, with counts.",
    "H2": "Pairs 1-3: abs(correction)+E_pair < (2.515,3.000,1.535) => supported; abs(correction)-E_pair > half => exceeded; else unresolved. Unscoreable pairs: not assessed.",
    "H3_H4": "Exploratory: report correction sign and resolution separately from corrected ddF sign; pair 4 rule sign is negative. Pair 5: correction size/sign or absence reason.",
    "sensitivity": "Replace only A_i(P) by plateau sensitivity; never change primary eligibility. The 0.19 planning line and bead_transfer_ok are not gates.",
    "expectations": "Decision 17 corrections (+1.85,+3.62,+0.84,-0.74,-0.32) and decision 19 pair 2 [+3.51,+3.81] are comparisons only, never rule inputs.",
}


T_K = 300.0


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _nonnegative(value):
    return _number(value) and value >= 0


def _json_number(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"JSON requires finite numbers, found {text}")
    return value


class _Inputs:
    """Hash the exact bytes parsed, including absent inputs in the manifest."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.manifest = {}

    def read(self, relative, *, raw=False):
        path = self.root / relative
        key = str(path)
        if not path.exists():
            self.manifest[key] = {"path": key, "sha256": None, "status": "missing"}
            return None
        data = path.read_bytes()
        self.manifest[key] = {"path": key, "sha256": hashlib.sha256(data).hexdigest(), "status": "present"}
        text = data.decode("utf-8-sig")
        return text if raw else json.loads(text, parse_float=_json_number, parse_constant=_json_number)


def _harmonics(text):
    rows = [r for r in csv.DictReader(io.StringIO(text)) if r["model"] == "mace"]
    result = {}
    for n, (b, a, expected, _) in enumerate(PAIRS, 1):
        matches = [r for r in rows if r["pair_id"] == f"{b}__{a}"]
        if len(matches) != 1:
            raise ValueError(f"A12: need exactly one mace row for {b}__{a}, b first")
        row = matches[0]
        # Some exports also carry struct_a/b; reject an inconsistent orientation.
        if row.get("struct_a", a) != a or row.get("struct_b", b) != b:
            raise ValueError(f"A12: swapped orientation for pair {n}")
        h = float(row["H_per_atom"])
        if not _number(h) or h <= 0:
            raise ValueError(f"A12: invalid H_per_atom for pair {n}")
        value = float(row["ddF_total"]) / h
        if not _number(value) or abs(value - expected) > .01:
            raise ValueError(f"A12: pair {n} has ddF_harm(b-a)={value}, expected {expected} within 0.01")
        result[n] = value
    return result


def harmonic_values(path):
    """Assert the five registered A12 values against the decomposition CSV."""
    return _harmonics(Path(path).read_text(encoding="utf-8-sig"))


def bead_allowance(P, A, d, sigma_d, *, branch_f=False, d_fe=None, sigma_d_fe=None):
    """Decision 19 rule 4, with all candidates and all tied maxima retained."""
    if P not in (16, 24, 32) or (branch_f and P != 32):
        raise ValueError("s_P requires P16/24/32, and P32 on branch F")
    if not (_nonnegative(A) and _number(d) and _nonnegative(sigma_d)):
        raise ValueError("s_P requires finite A_i, d and nonnegative sigma_d")
    terms = {"floor": .05, "A4b": A}
    if branch_f:
        terms["branch_F_pilot"] = abs(d) / 2
    else:
        terms["pilot"] = max(0., abs(d) - sigma_d) / (2 if P == 32 else 1)
        if P == 32 and d_fe is not None:
            if not (_number(d_fe) and _nonnegative(sigma_d_fe)):
                raise ValueError("Fe pilot requires finite d_Fe and nonnegative sigma_dFe")
            terms["Fe_pilot"] = max(0., abs(d_fe) - sigma_d_fe) / 2
    value = max(terms.values())
    return {"value_meV_H": value, "terms_meV_H": terms,
            "setting_terms": [k for k, v in terms.items() if v == value]}


# run_args that change the sampled physics: they must match exactly between the two pilot runs.
PHYSICS_RUN_ARGS = ("dt", "T", "tau0", "masses_points", "equil", "splitting", "dtype", "init", "pre_equil",
                    "stationarity_extension", "backend", "monitor_schema")
# run_args that only set output, storage, device or batching (run_pilot.sh dumps at P16 for C2, not at P32).
# compare_runs would refuse any difference in them, so they are removed from the copies it sees. Any other
# differing key still reaches compare_runs and is refused there.
DIAGNOSTIC_RUN_ARGS = ("dump_every", "state_root", "bead_chunk", "device", "log_every")


def _compare(lo, hi, struct):
    # Lazy import: score-module import itself needs neither NumPy nor torch/MACE.
    from .pimd import compare_runs

    for doc, P in ((lo, 16), (hi, 32)):
        if doc.get("struct_id") != struct or doc.get("P") != P or doc.get("run_args", {}).get("beads") != P:
            raise ValueError(f"pilot requires {struct} P16 and P32, consistent with run_args")
        sigma = doc.get("delta_anh_err_meV_H")
        if not _nonnegative(sigma) or sigma != doc.get("dF_PIMD_err_meV_H"):
            raise ValueError("pilot sigma must match the run's same-P Delta_anh error")
        if not _number(doc.get("delta_anh_meV_H")):
            raise ValueError("pilot needs finite, verified Delta_anh")
    ra, rb = lo.get("run_args") or {}, hi.get("run_args") or {}
    physics = [k for k in PHYSICS_RUN_ARGS if ra.get(k) != rb.get(k)]
    if physics:
        raise ValueError(f"{struct} pilot runs differ in physics run_args {physics}; compare P only")
    stripped = [{**doc, "run_args": {k: v for k, v in (doc.get("run_args") or {}).items()
                                     if k not in DIAGNOSTIC_RUN_ARGS}} for doc in (lo, hi)]
    out = compare_runs(*stripped, z=1.96)
    out["ignored_diagnostic_run_args"] = {k: [ra.get(k), rb.get(k)] for k in DIAGNOSTIC_RUN_ARGS
                                          if ra.get(k) != rb.get(k)}
    return out


def _c2_summary(documents):
    # C2 is a common precision control, including P16's control for P32 pairs.
    # If several exist, preserve failures and use the largest allowance.
    docs = list(documents)
    values = [d.get("s_f32_meV_H") for d in docs]
    return {"pass": bool(docs) and all(d.get("pass") is True for d in docs)
            and all(_nonnegative(v) for v in values),
            "stop_and_reconvene": any(d.get("stop_and_reconvene") is True for d in docs),
            "s_f32_meV_H": max(values) if values and all(_nonnegative(v) for v in values) else None,
            "controls": [{k: d.get(k) for k in ("P", "pass", "stop_and_reconvene", "s_f32_meV_H")} for d in docs]}


def _add_fe_comparison(pilot, fe16, fe32):
    pilot.update(d_Fe_meV_H=None, sigma_dFe_meV_H=None)
    if pilot["branch_F"] or not all(d and d.get("status") == "complete" for d in (fe16, fe32)):
        return
    if not all(_number(d.get("delta_anh_meV_H")) for d in (fe16, fe32)):
        pilot["Fe_comparison_unavailable"] = "completed Fe runs lack verified Delta_anh; unchecked values are excluded"
        return
    fe = _compare(fe16, fe32, "JVASP-54682")
    pilot.update(d_Fe_meV_H=fe["d_meV_H"], sigma_dFe_meV_H=fe["sigma_d_meV_H"], Fe_comparison=fe)


def pilot_decision(p16, p32, c2=None, fe16=None, fe32=None):
    """Decide F and T independently, reusing compare_runs' seed/factor-2 checks."""
    comparison = _compare(p16, p32, "mp-625152")
    tau = p16.get("points", [{}])[0].get("tau_int_steps") if p16.get("points") else None
    if not _nonnegative(tau):
        raise ValueError("pilot needs first GL point tau_int_steps")
    F, T = comparison["pilot_reject_P"], tau > 24
    precision = _c2_summary([] if c2 is None else (c2 if isinstance(c2, list) else [c2]))
    rates = {}
    for doc in (p16, p32):
        rate = doc.get("seconds_per_ring_step")
        rates[str(doc["P"])] = {"seconds_per_ring_step": rate,
                                "rate_factor": rate / (1.23 * doc["P"] / 16) if _nonnegative(rate) else None}
    out = {"status": "complete", "branch": "F" if F else ("T" if T else "main"),
           "branch_F": F, "branch_T": T, "tau_int_steps": tau,
           "steps_per_point": 4000 if T else 3000,
           "d_meV_H": comparison["d_meV_H"], "sigma_d_meV_H": comparison["sigma_d_meV_H"],
           "comparison": comparison, "rates": rates, "C2": precision,
           "s_f32_meV_H": precision["s_f32_meV_H"],
           "stop_and_reconvene": precision["stop_and_reconvene"],
           "action": "STOP AND RECONVENE" if precision["stop_and_reconvene"] else
                     ("C2 missing or failed; production not cleared" if not precision["pass"] else "pilot decision recorded"),
           "d_Fe_meV_H": None, "sigma_dFe_meV_H": None, "rule_texts": RULE_TEXTS}
    _add_fe_comparison(out, fe16, fe32)
    return out


def _identity(doc, struct, P):
    if doc is not None and (doc.get("struct_id") != struct or doc.get("P") != P):
        raise ValueError(f"run identity/P mismatch: expected {struct} P{P}")
    if doc and "beads" in doc.get("run_args", {}) and doc["run_args"]["beads"] != P:
        raise ValueError(f"run_args P mismatch for {struct}")
    if doc is not None:
        # every PIMD value is added to the 300 K harmonic double difference (P12 section 2); a run at another or an
        # unrecorded temperature is never combined with it (review, 24 Oct)
        temps = [t for t in (doc.get("T_K"), doc.get("run_args", {}).get("T")) if t is not None]
        if not temps or any(not _number(t) or abs(t - T_K) > 1e-9 for t in temps):
            raise ValueError(f"{struct} P{P}: temperature {temps or 'missing'} is not {T_K} K")


def _structure(doc, struct, P, scan, pilot, *, fe=False):
    reasons = []
    out = {"struct_id": struct, "P": P, "status": doc.get("status") if doc else "missing",
           "delta_anh_meV_H": None, "sigma_meV_H": None, "s_P": None,
           "s_P_plateau": None, "s_hess_meV_H": None, "s_imag_meV_H": None,
           "invalid_reference": False, "reasons": reasons}
    if not doc or doc.get("status") != "complete":
        return out
    for source, target in (("delta_anh_meV_H", "delta_anh_meV_H"),
                           ("delta_anh_err_meV_H", "sigma_meV_H"), ("s_imag_meV_H", "s_imag_meV_H")):
        value = doc.get(source)
        if _number(value) and (source == "delta_anh_meV_H" or value >= 0):
            out[target] = value
        else:
            reasons.append(f"{struct}: missing/invalid {'Delta_anh' if source == 'delta_anh_meV_H' else source}")
    force = doc.get("initial_max_abs_F_eV_A")
    out["initial_max_abs_F_eV_A"] = force
    out["invalid_reference"] = doc.get("invalid_reference") is True or (_number(force) and force > .001)
    if out["invalid_reference"]:
        reasons.append(f"{struct}: A13 invalid reference or residual force > 0.001 eV/A")
    if not _nonnegative(force) or "invalid_reference" not in doc:
        reasons.append(f"{struct}: missing A13 reference validation")
    for key, label in (("stationarity_ok", "stationarity"), ("error_converged", "statistical error unconverged"),
                       ("fc_interpolation_verified", "FC interpolation unverified")):
        if doc.get(key) is not True:
            reasons.append(f"{struct}: {label}")
    points = doc.get("points") or []
    if not points:
        reasons.append(f"{struct}: missing per-point stationarity/monitors")
    for index, point in enumerate(points):
        if point.get("stationarity_ok") is not True:
            reasons.append(f"{struct}: point {index} stationarity")
        if point.get("error_converged") is not True:
            reasons.append(f"{struct}: point {index} statistical error unconverged")
    monitors = [("run", doc.get("monitors") or {})] + [
        (f"point {i}", p.get("monitors") or {}) for i, p in enumerate(points)]
    for scope, mon in monitors:
        for key in ("heavy_rmsd_ok", "coordination_unchanged", "retention_ok"):
            if mon.get(key) is not True:
                reasons.append(f"{struct}: {scope} {key} failed or missing")
        for key in ("imaginary_retention_ok", "heavy_rmsd_pooled_ok", "coordination_pooled_unchanged",
                    "imaginary_retention_pooled_ok", "retention_pooled_ok"):
            if key in mon and mon[key] is not True:
                reasons.append(f"{struct}: {scope} {key} failed")
    hess = doc.get("hessian_check")
    out["hessian_check"] = hess
    out["s_hess_choice"] = RULE_TEXTS["s_hess"]
    if struct in INTERPOLATED or hess is not None:
        from .pimd import HESSIAN_TOL_MEV

        diffs = [hess.get(k) for k in ("diff_meV_H", "diff_P_meV_H")] if hess else []
        measured = max(abs(x) for x in diffs) if len(diffs) == 2 and all(_number(x) for x in diffs) else None
        if not hess or hess.get("passed") is not True or measured is None or measured >= HESSIAN_TOL_MEV:
            reasons.append(f"{struct}: Hessian check failed or missing")
        out["s_hess_meV_H"] = measured if struct in INTERPOLATED else 0.
    else:
        out["s_hess_meV_H"] = 0.
    for field, target in (("a4b_bound_meV_H", "s_P"), ("a4b_plateau_sensitivity_meV_H", "s_P_plateau")):
        A = (scan.get(field) or {}).get(str(P))
        if not _nonnegative(A) or not _number(pilot.get("d_meV_H")) or not _nonnegative(pilot.get("sigma_d_meV_H")):
            if target == "s_P":
                reasons.append(f"{struct}: missing A4b bound or completed pilot")
            continue
        out[target] = bead_allowance(P, A, pilot["d_meV_H"], pilot["sigma_d_meV_H"],
                                    branch_f=pilot.get("branch_F", False),
                                    d_fe=pilot.get("d_Fe_meV_H") if fe else None,
                                    sigma_d_fe=pilot.get("sigma_dFe_meV_H") if fe else None)
    return out


def _score_pair(n, P, harmonic, docs, scans, pilot, controls, c2):
    b, a, _, expectation = PAIRS[n - 1]
    reasons = []
    row = {"pair": n, "pair_id": f"{b}__{a}", "a": a, "b": b, "P": P,
           "ddF_harm_meV_H": harmonic, "correction_meV_H": None, "ddF_corr_meV_H": None,
           "sigma_pair_meV_H": None, "B_pair_meV_H": None, "E_pair_meV_H": None,
           "E_pair_plateau_meV_H": None, "inconclusive_only_fit_allowance": False,
           "category": "not run", "reasons": reasons, "scoreable": False,
           "registered_expectation_meV_H": expectation,
           "registered_expectation_range_meV_H": [3.51, 3.81] if n == 2 else None,
           "structures": {}, "allowances_meV_H": {}}
    if P is None:
        reasons.append("not run: branch F excludes pairs 4/5, or pair 2 omitted by predeclared cap choice")
        return row
    for struct, doc in zip((b, a), docs):
        _identity(doc, struct, P)
    structures = {role: _structure(doc, struct, P, scans.get(struct, {}), pilot, fe=n == 2 and P == 32)
                  for role, struct, doc in zip(("b", "a"), (b, a), docs)}
    row["structures"] = structures
    for s in structures.values():
        reasons.extend(s["reasons"])
    if any(s["status"] != "complete" for s in structures.values()):
        reasons.extend(f"{s['struct_id']}: {s['status']} (not run)" for s in structures.values() if s["status"] != "complete")
        return row
    if any(s["invalid_reference"] for s in structures.values()):
        row["category"] = "invalid reference"
        return row
    if controls.get("pass") is not True:
        reasons.append("controls_cpu overall pass missing or failed")
    # C1 is an integrator control at the pair's P (decision 18 action 4, decision 19 action 3), registered on
    # mp-23807 and mp-625152 at every P and on the FeOOH FCs at P24/P32. It gates the pair through its P, not
    # through per-structure entries for structures it was never registered on.
    c1 = (controls.get("C1_by_P") or {}).get(str(P)) or {}
    if not c1:
        reasons.append(f"C1 P{P} missing")
    for struct, entry in sorted(c1.items()):
        if (entry or {}).get("pass") is not True:
            reasons.append(f"C1 P{P} {struct} failed")
    if n == 2:
        for struct in (b, a):
            if struct not in c1:
                reasons.append(f"C1 P{P} {struct} (own FC cell) missing")
    if ((controls.get("C4_by_P") or {}).get(str(P)) or {}).get("pass") is not True:
        reasons.append(f"C4 P{P} missing or failed")
    if c2["pass"] is not True:
        reasons.append("C2 missing or failed")
    if c2["stop_and_reconvene"]:
        reasons.append("C2 STOP AND RECONVENE")
    if n == 2 and P == 32 and not pilot["branch_F"] and pilot.get("Fe_comparison_unavailable"):
        reasons.append(pilot["Fe_comparison_unavailable"])
    terms = {"s_dt": (controls.get("s_dt_meV_H_by_P") or {}).get(str(P)),
             "s_f32": c2["s_f32_meV_H"], "s_quad": controls.get("s_quad_meV_H")}
    for role, s in structures.items():
        terms[f"s_P_{role}"] = s["s_P"]["value_meV_H"] if s["s_P"] else None
        terms[f"s_hess_{role}"] = s["s_hess_meV_H"]
        terms[f"s_imag_{role}"] = s["s_imag_meV_H"]
    row["allowances_meV_H"] = terms
    for key, value in terms.items():
        if not _nonnegative(value):
            reasons.append(f"missing/invalid allowance {key}")
    sa, sb = structures["a"], structures["b"]
    if all(_number(s["delta_anh_meV_H"]) for s in (sa, sb)):
        row["correction_meV_H"] = sb["delta_anh_meV_H"] - sa["delta_anh_meV_H"]
        row["ddF_corr_meV_H"] = harmonic + row["correction_meV_H"]
    if all(_nonnegative(s["sigma_meV_H"]) for s in (sa, sb)):
        row["sigma_pair_meV_H"] = math.hypot(sa["sigma_meV_H"], sb["sigma_meV_H"])
        if all(_nonnegative(v) for v in terms.values()):
            row["B_pair_meV_H"] = sum(terms.values())
            row["E_pair_meV_H"] = 1.96 * row["sigma_pair_meV_H"] + row["B_pair_meV_H"]
            if all(s["s_P_plateau"] is not None for s in (sa, sb)):
                plateau_terms = dict(terms)
                for role, s in structures.items():
                    plateau_terms[f"s_P_{role}"] = s["s_P_plateau"]["value_meV_H"]
                row["E_pair_plateau_meV_H"] = 1.96 * row["sigma_pair_meV_H"] + sum(plateau_terms.values())
    E = row["E_pair_meV_H"]
    if E is not None and E > 1:
        row["inconclusive_only_fit_allowance"] = not reasons and row["E_pair_plateau_meV_H"] is not None and row["E_pair_plateau_meV_H"] <= 1
        reasons.append("E_pair > 1 meV/H")
    if reasons or E is None or row["ddF_corr_meV_H"] is None:
        row["category"] = "inconclusive"
    else:
        row["scoreable"] = True
        corr = row["ddF_corr_meV_H"]
        row["category"] = ("supported" if corr * harmonic > 0 else "challenged") if abs(corr) > E else "unresolved"
    return row


def _sign(value, E):
    return {"value_meV_H": value, "sign": "positive" if value > 0 else "negative" if value < 0 else "zero",
            "resolved": abs(value) > E}


def _hypotheses(rows):
    counts = {c: sum(r["category"] == c for r in rows[:3]) for c in CATEGORIES}
    H1 = {"denominator": 3, "counts": counts,
          "category": "challenged" if counts["challenged"] else "supported" if counts["supported"] == 3 else "undecided"}
    H2 = {}
    for r, half in zip(rows, (2.515, 3., 1.535)):
        verdict = "not assessed"
        if r["scoreable"]:
            size, E = abs(r["correction_meV_H"]), r["E_pair_meV_H"]
            verdict = "supported" if size + E < half else "exceeded" if size - E > half else "unresolved"
        H2[str(r["pair"])] = {"category": verdict, "half_threshold_meV_H": half,
                              "reasons": r["reasons"] if not r["scoreable"] else []}
    exploratory = {}
    for key, r in zip(("H3", "H4"), rows[3:]):
        observation = {"category": "exploratory" if r["scoreable"] else "not assessed",
                       "reason": None if r["scoreable"] else "; ".join(r["reasons"]),
                       "correction": None, "ddF_corr": None}
        # Keep valid measurements visible even when a gate prevents inference.
        if r["correction_meV_H"] is not None:
            for name, field in (("correction", "correction_meV_H"), ("ddF_corr", "ddF_corr_meV_H")):
                observation[name] = _sign(r[field], r["E_pair_meV_H"] or 0.)
                if not r["scoreable"]:
                    observation[name]["resolved"] = False
            observation["correction_magnitude_meV_H"] = abs(r["correction_meV_H"])
            if key == "H3":
                observation["toward_rule_negative"] = r["correction_meV_H"] < 0
        exploratory[key] = observation
    return {"H1": H1, "H2": H2, **exploratory}


def _context(root):
    inputs = _Inputs(root)
    base = Path("results/pimd")
    runs = {}

    def read_run(struct, P):
        key = (struct, P)
        if key not in runs:
            runs[key] = inputs.read(base / f"{struct}_P{P}.json")
            _identity(runs[key], struct, P)
        return runs[key]

    c2_paths = sorted((inputs.root / base).glob("c2_*.json"))
    c2 = [inputs.read(p.relative_to(inputs.root)) for p in c2_paths]
    if not c2_paths:
        inputs.read(base / "c2_mp-625152_P16.json")
    low, high = read_run("mp-625152", 16), read_run("mp-625152", 32)
    saved = inputs.read(base / "pilot_decision.json")
    fe16, fe32 = read_run("JVASP-54682", 16), read_run("JVASP-54682", 32)
    if all(d and d.get("status") == "complete" and _number(d.get("delta_anh_meV_H")) for d in (low, high)):
        pilot = pilot_decision(low, high, c2, fe16, fe32)
        if saved and saved.get("branch") != pilot["branch"]:
            raise ValueError("saved pilot branch disagrees with completed runs")
    elif (saved and _number(saved.get("d_meV_H")) and _nonnegative(saved.get("sigma_d_meV_H"))
          and _nonnegative(saved.get("tau_int_steps"))):
        pilot = dict(saved)
        F = abs(pilot["d_meV_H"]) > .3 and abs(pilot["d_meV_H"]) > 1.96 * pilot["sigma_d_meV_H"]
        T = _number(pilot.get("tau_int_steps")) and pilot["tau_int_steps"] > 24
        expected = "F" if F else "T" if T else "main"
        if pilot.get("branch") != expected:
            raise ValueError("saved pilot branch contradicts A4/A6 thresholds")
        precision = _c2_summary(c2)
        pilot.update(branch_F=F, branch_T=T, source="saved pilot; raw pilot unavailable",
                     C2=precision, s_f32_meV_H=precision["s_f32_meV_H"],
                     stop_and_reconvene=precision["stop_and_reconvene"])
        # Recompute any available Fe comparison; never silently omit a new row 8.
        if not F and all(d and d.get("status") == "complete" for d in (fe16, fe32)):
            _add_fe_comparison(pilot, fe16, fe32)
    else:
        pilot = {"status": "pending", "branch": "pending", "branch_F": False, "branch_T": False,
                 "d_meV_H": None, "sigma_d_meV_H": None,
                 "reason": "mp-625152 P16/P32 complete verified pilot unavailable"}
    diagnostics = []
    if not pilot["branch_F"] and fe16:
        diagnostics.append({"struct_id": "JVASP-54682", "P": 16, "diagnostic": True,
                            "status": fe16.get("status"), "used_in_ddF_corr": False,
                            "delta_anh_meV_H": fe16.get("delta_anh_meV_H") if fe16.get("status") == "complete" else None})
    return inputs, read_run, pilot, c2, diagnostics


def _provenance(inputs):
    try:
        git = subprocess.run(["git", "-C", str(inputs.root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git = None
    return {"inputs": list(inputs.manifest.values()), "git_hash": git,
            "git_hash_status": "available" if git else "unavailable", "rule_texts": RULE_TEXTS}


def score(root=ROOT):
    """Read the current tree and return a strict-JSON report without writing."""
    inputs, read_run, pilot, c2_docs, diagnostics = _context(root)
    base = Path("results/pimd")
    text = inputs.read("results/decompose_pairs.csv", raw=True)
    if text is None:
        raise ValueError("A12: missing results/decompose_pairs.csv")
    harmonics = _harmonics(text)
    controls = inputs.read(base / "controls_cpu.json") or {}
    scans = (inputs.read(base / "a4b_scan_residual.json") or {}).get("structures", {})
    choice = inputs.read(base / "pair2_beads.json")
    pair2_P = 32 if choice is None else choice.get("P")
    if choice is not None and "P" not in choice:
        raise ValueError("pair2_beads.json requires P (24, 32, or null for omitted)")
    if pair2_P not in (None, 24, 32):
        raise ValueError("pair 2 requires preselected P24/P32 or null for omitted")
    c2 = _c2_summary(c2_docs)
    rows = []
    for n, (b, a, _, _) in enumerate(PAIRS, 1):
        P = (32 if n <= 3 else None) if pilot["branch_F"] else (pair2_P if n == 2 else 16)
        docs = (read_run(b, P), read_run(a, P)) if P is not None else (None, None)
        rows.append(_score_pair(n, P, harmonics[n], docs, scans, pilot, controls, c2))
    covariance = {"pairs": [1, 3], "shared_structure": "mp-23807", "coefficient_in_each": 1,
                  "cov_meV_H_squared": None, "correlation": None,
                  "statement": "cov = sigma_23807^2 (same positive sign); s_P(mp-23807) and per-pair systematics are shared, not independent errors."}
    p1, p3 = rows[0], rows[2]
    shared = p1["structures"].get("b", {}).get("sigma_meV_H")
    if _nonnegative(shared) and p1["sigma_pair_meV_H"] is not None and p3["sigma_pair_meV_H"] is not None:
        covariance["cov_meV_H_squared"] = shared ** 2
        denom = p1["sigma_pair_meV_H"] * p3["sigma_pair_meV_H"]
        covariance["correlation"] = shared ** 2 / denom if denom else None
    out = {"branch": pilot["branch"], "selection_provisional": pilot["branch"] == "pending",
           "pair2_choice_source": "decision 19 default P32" if choice is None else "pair2_beads.json",
           "pilot": pilot, "C2": c2, "stop_and_reconvene": c2["stop_and_reconvene"],
           "diagnostics": diagnostics, "pairs": rows, "covariance": covariance,
           **_hypotheses(rows), **_provenance(inputs)}
    # Reject non-finite input rather than letting NaN silently alter a verdict.
    json.dumps(out, allow_nan=False)
    return out


def _table(report):
    def fmt(value):
        return "--" if value is None else f"{value:.6g}"
    lines = ["| pair | P | ddF_harm | Delta b - a | ddF_corr | E_pair | category |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in report["pairs"]:
        cells = [str(r["pair"]), str(r["P"]) if r["P"] else "--"]
        cells += [fmt(r[k]) for k in ("ddF_harm_meV_H", "correction_meV_H", "ddF_corr_meV_H", "E_pair_meV_H")]
        lines.append("| " + " | ".join(cells + [r["category"]]) + " |")
    lines.append(f"H1: {report['H1']['category']}; denominator 3; counts {report['H1']['counts']}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", choices=("pilot", "score"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--no-write", action="store_true", help="evaluate and print without writing results")
    args = parser.parse_args(argv)
    if args.job == "score":
        report = score(args.root)
        default_name = "p12_scores.json"
    else:
        inputs, _, report, _, diagnostics = _context(args.root)
        if report.get("status") != "complete" or report.get("source") == "saved pilot; raw pilot unavailable":
            raise ValueError("pilot requires completed mp-625152 P16 and P32 runs")
        report = {**report, "diagnostics": diagnostics, **_provenance(inputs)}
        default_name = "pilot_decision.json"
    serialized = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if not args.no_write:
        out = args.out or args.root / "results" / "pimd" / default_name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")
    if report.get("stop_and_reconvene"):
        print("STOP AND RECONVENE: C2 requires production to stop.")
    print(_table(report) if args.job == "score" else serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
