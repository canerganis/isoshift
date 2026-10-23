"""P12 A4b: fixed-atom O-H scans and same-P anharmonic isotope residuals.

Only the scan stage needs MACE. ``analyze_scan`` can reanalyse the small raw
energy arrays in the JSON on a CPU. Finite P uses the symmetric primitive
free-particle transfer matrix; infinity uses sinc DVR, not a large-P proxy.
The harmonic reference uses the identical grid, quadrature and propagator.
No PIMD trajectories are read. No relaxation is performed.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import time

import numpy as np
from numpy.polynomial import Chebyshev
from scipy.linalg import eigh
from scipy.special import logsumexp

from isoshift.cache import load_fc
from isoshift.calculators import calculator_info, get_calculator
from isoshift.phonons import supercell_for_min_length
from .pimd import AMU_EV, HBAR_EV_FS, KB_EV, M_D, M_H, _osc_free_energy, find_cache

ROOT = Path(__file__).resolve().parents[2]
STRUCT_IDS = ("mp-23807", "mp-625054", "JVASP-54682", "JVASP-92228", "mp-625152",
              "mp-626497", "mp-985293", "mp-23940", "mp-626000")
SECOND_CHECK_IDS = STRUCT_IDS[:4]
M_O = 15.999
CM_TO_THZ = 0.0299792458
SCAN_DISPLACEMENTS = np.linspace(-0.4, 0.8, 41)
SELECTION_RULE = ("Largest multiplicity-weighted mean of per-H max absolute P16-P128 residuals "
                  "among mp-23807, mp-625054, JVASP-54682, JVASP-92228; mp-625152 excluded. "
                  "All four values are required; ties follow the listed order.")
LIMITATIONS = ("Fixed-atom 1D estimate covering O-H stretch and the 1D O...O transfer coordinate "
              "only, not stretch-bend coupling or other collective anharmonicity. Reduced and bare "
              "masses are alternative models of the same fixed-atom PES, not additional modes. "
              "Fit and grid diagnostics qualify this estimate; it is not a rigorous PIMD error bound. "
              "A scan whose endpoint slope points inward is cut at its outermost fitted maximum "
              "(flag truncated_at_endpoint); any well beyond the scanned range is not modelled.")
# An inward endpoint slope is cut only if the endpoint lies at least this far
# above the occupied well bottom (11.6 kT at 300 K) AND the estimated free-energy
# leak into the cut-off scanned region stays below TRUNCATION_MAX_LEAK_MEV. The
# leak is referenced to the converged free energy, so the H zero-point energy
# counts against the margin. Both checks also cover a Taylor extrapolation
# (endpoint slope, curvature clamped >= 0) up to TRUNCATION_EXTRAPOLATION_A past
# the endpoint: at +0.8 A a long-bond H is 1.0 to 1.2 A from the acceptor, so an
# unscanned acceptor-side well bottom can lie up to about 0.25 A further out.
TRUNCATION_MIN_ABOVE_WELL_EV = 0.3
TRUNCATION_MAX_LEAK_MEV = 1e-3
TRUNCATION_EXTRAPOLATION_A = 0.3
TRUNCATION_MAX_DENSITY = 1e-6  # max quantum probability within 0.1 A of a truncation cut
FIT_WINDOW_EV = 1.5  # fit only the contiguous scan points within this of the lowest point (well region)
FIT_MAX_RMS_NOISE = 10.0  # a fit with rms error above this many float32 noise units is not usable
STABILITY_MAX_RESIDUAL_CHANGE_MEV = 0.01
STABILITY_MAX_FREQUENCY_CHANGE = 0.01


def mass_variants():
    return {"reduced": {"H": M_H * M_O / (M_H + M_O), "D": M_D * M_O / (M_D + M_O)},
            "bare": {"H": M_H, "D": M_D}}


def _thread_limit():
    # Tiny dense eigensystems are slower with a large BLAS thread pool.
    try:
        from threadpoolctl import threadpool_limits
        return threadpool_limits(limits=1, user_api="blas")
    except ImportError:
        return nullcontext()


def _thermal_spectrum(matrix, beta, beads):
    """Return log Z and diagonal density; bound omitted states before truncating."""
    n = len(matrix)
    count = min(32, n)
    while True:
        subset = [0, count - 1] if beads is None else [n - count, n - 1]
        values, vectors = eigh(matrix, subset_by_index=subset, check_finite=False)
        if beads is None:
            logs = -beta * values
        else:
            if values[-1] <= 0:
                raise ValueError("Transfer matrix has no positive eigenvalue")
            logs = beads * np.log(np.maximum(values, np.finfo(float).tiny))
        log_z = float(logsumexp(logs))
        # All uncomputed Boltzmann weights are <= the smallest included weight.
        tail = float((n - count) * np.exp(np.min(logs) - log_z))
        if tail < 1e-13 or count == n:
            density = vectors**2 @ np.exp(logs - log_z)
            return log_z, density, tail
        count = min(2 * count, n)


def _free_energy(values, grid, mass, temperature, beads, monitor=None):
    """Uniform-grid primitive trace or sinc-DVR trace (eV)."""
    dx = float(grid[1] - grid[0])
    beta = 1 / (KB_EV * temperature)
    offset = float(np.min(values))
    v = values - offset
    n = len(grid)
    if beads is None:
        # Infinite-line sinc DVR: T_ii = hbar^2 pi^2/(6 m dx^2),
        # T_ij = hbar^2 (-1)^(i-j)/(m dx^2 (i-j)^2).
        d = np.arange(n)[:, None] - np.arange(n)[None, :]
        safe = np.where(d == 0, 1, d)
        matrix = (HBAR_EV_FS**2 / (mass * AMU_EV * dx**2)
                  * np.where(d % 2 == 0, 1.0, -1.0) / safe**2)
        np.fill_diagonal(matrix, HBAR_EV_FS**2 * np.pi**2 / (6 * mass * AMU_EV * dx**2) + v)
    else:
        tau = beta / beads
        variance = HBAR_EV_FS**2 * tau / (mass * AMU_EV)
        matrix = dx / np.sqrt(2 * np.pi * variance) * np.exp(
            -(grid[:, None] - grid[None, :])**2 / (2 * variance)
            - tau * (v[:, None] + v[None, :]) / 2)
    log_z, density, tail = _thermal_spectrum(matrix, beta, beads)
    edge_mask = (grid <= grid[0] + 0.06) | (grid >= grid[-1] - 0.06)
    watched = 0.0 if monitor is None else float(density[monitor].sum())
    return offset - log_z / beta, float(density[edge_mask].sum()), tail, watched


def _evaluate_grid(potential, curvature, minimum, grid, temperature, beads, monitor=()):
    fitted = np.asarray(potential(grid), dtype=float)
    mask = np.zeros(grid.shape, bool)
    for lo, hi in monitor:
        mask |= (grid >= lo) & (grid <= hi)
    harmonic = 0.5 * curvature * (grid - minimum)**2
    if fitted.shape != grid.shape or not np.all(np.isfinite(fitted)):
        raise ValueError("Potential must give one finite energy per grid point")
    results, max_error, max_edge, max_tail, max_watch = {}, 0.0, 0.0, 0.0, 0.0
    for variant, masses in mass_variants().items():
        frequencies = {}
        energies = {kind: {} for kind in ("fit", "harmonic")}
        errors = {}
        for iso, mass in masses.items():
            nu = float(np.sqrt(curvature / (mass * AMU_EV)) / (2 * np.pi) * 1000)
            frequencies[iso] = {"THz": nu, "cm^-1": nu / CM_TO_THZ}
            for kind, values in (("fit", fitted), ("harmonic", harmonic)):
                energies[kind][iso] = {}
                for p in (*beads, None):
                    key = "inf" if p is None else str(p)
                    f, edge, tail, watched = _free_energy(values, grid, mass, temperature, p,
                                                          mask if kind == "fit" else None)
                    energies[kind][iso][key] = f * 1000
                    max_edge, max_tail = max(max_edge, edge), max(max_tail, tail)
                    max_watch = max(max_watch, watched)
                    if kind == "harmonic":
                        err = abs(f - float(_osc_free_energy(nu, temperature, p))) * 1000
                        errors[f"{iso}_{key}"] = err
                        max_error = max(max_error, err)
        dfs = {kind: {p: energies[kind]["D"][p] - energies[kind]["H"][p]
                      for p in energies[kind]["H"]} for kind in energies}
        delta = {p: dfs["fit"][p] - dfs["harmonic"][p] for p in dfs["fit"]}
        results[variant] = {"masses_u": masses, "harmonic_frequency": frequencies,
                            "F_fit_meV": energies["fit"], "F_harmonic_meV": energies["harmonic"],
                            "dF_fit_meV": dfs["fit"], "dF_harmonic_meV": dfs["harmonic"],
                            "delta_anh_meV": delta, "residual_meV": delta["16"] - delta["128"],
                            "harmonic_errors_meV": errors}
    return results, max_error, max_edge, max_tail, max_watch


def analyze_potential(potential, curvature, minimum=0.0, *, temperature=300.0,
                      beads=(16, 128), bounds=(-0.7, 1.2), grid_step=0.012,
                      tolerance_meV=1e-4, max_grid=1800, monitor=()):
    """Converge space and resolution, including each isotope's harmonic check.

    The second grid is finer AND wider. All four individual free energies,
    isotope differences and Delta_anh values must converge. A failed check
    raises, rather than returning an apparently usable A4b estimate.
    """
    beads = tuple(sorted(set(beads)))
    if (not {16, 128}.issubset(beads) or any(not isinstance(p, (int, np.integer)) or p <= 0 for p in beads)
            or not np.isfinite(curvature) or curvature <= 0 or not np.isfinite(minimum)
            or not np.isfinite(temperature) or temperature <= 0 or grid_step <= 0
            or tolerance_meV <= 0 or not np.all(np.isfinite(bounds)) or bounds[0] >= bounds[1]):
        raise ValueError("Need positive curvature/T/grid step and bead integers including 16 and 128")
    light = mass_variants()["reduced"]["H"]
    omega = np.sqrt(curvature / (light * AMU_EV))
    sigma = np.sqrt(HBAR_EV_FS / (2 * light * AMU_EV * omega)
                    / np.tanh(HBAR_EV_FS * omega / (2 * KB_EV * temperature)))
    lo, hi = min(bounds[0], minimum - 10 * sigma), max(bounds[1], minimum + 10 * sigma)
    previous, history = None, []
    with _thread_limit():
        for refinement in range(5):
            n = int(np.ceil((hi - lo) / grid_step)) + 1
            if n > max_grid:
                break
            grid = np.linspace(lo, hi, n)
            result, error, edge, tail, watched = _evaluate_grid(potential, curvature, minimum, grid,
                                                                temperature, beads, monitor)
            flat = np.array([v for r in result.values() for kind in ("F_fit_meV", "F_harmonic_meV")
                             for iso in ("H", "D") for v in r[kind][iso].values()]
                            + [v for r in result.values() for v in r["delta_anh_meV"].values()])
            change = None if previous is None else float(np.max(np.abs(flat - previous)))
            history.append({"n_grid": n, "dx_A": float(grid[1] - grid[0]), "bounds_A": [lo, hi],
                            "max_change_meV": change, "harmonic_max_error_meV": error,
                            "edge_probability_max": edge})
            if change is not None and change < tolerance_meV and error < 1e-4 and edge < 1e-10:
                return {"mass_variants": result,
                        "numerics": {"converged": True, "method_P": "primitive symmetric transfer matrix",
                                     "method_inf": "sinc DVR", "grid_history": history,
                                     "harmonic_max_error_meV": error, "edge_probability_max": edge,
                                     "omitted_partition_weight_bound": tail,
                                     "monitor_intervals_A": [[float(v) if np.isfinite(v) else None for v in m]
                                                             for m in monitor],
                                     "monitor_probability_max": watched,
                                     "tolerance_meV": tolerance_meV}}
            previous = flat
            grid_step /= 2
            lo -= 0.12
            hi += 0.12
    raise ValueError(f"1D grid did not converge within {max_grid} points: {history}")


class FitError(ValueError):
    def __init__(self, message, diagnostics):
        super().__init__(message)
        self.diagnostics = diagnostics


@dataclass
class FittedPotential:
    polynomial: Chebyshev
    bounds: tuple
    minimum: float
    curvature: float
    extensions: tuple
    diagnostics: dict
    truncations: tuple = ()

    def monitor_intervals(self, width=0.1):
        """Bands next to each truncation wall where the density must vanish."""
        return tuple((t["cut_A"] - width, np.inf) if t["side"] == "right" else (-np.inf, t["cut_A"] + width)
                     for t in self.truncations)

    def __call__(self, x):
        x = np.asarray(x, dtype=float)
        # Do not evaluate a high-order polynomial outside its fitted interval.
        values = self.polynomial(np.clip(x, *self.bounds))
        for edge, sign, (v, slope, curv, quartic) in zip(self.bounds, (-1, 1), self.extensions):
            t = np.maximum(sign * (x - edge), 0)
            extension = v + slope * t + 0.5 * curv * t**2 + quartic * t**4
            values = np.where(t > 0, extension, values)
        return values


def fit_potential(displacements, energies, *, degree=10, noise_eV=5e-5):
    """Global Chebyshev smoothing and C2, monotonically confining tails.

    Never fix a nonphysical repulsive branch silently. An endpoint whose slope
    points inward is cut at the outermost fitted maximum with a C1 wall and
    flagged truncated_at_endpoint, but only when the endpoint and its short
    extrapolation stay TRUNCATION_MIN_ABOVE_WELL_EV above the occupied well;
    otherwise the scan is explicitly invalid. analyze_scan adds the leak check.
    """
    x, y = np.asarray(displacements, dtype=float), np.asarray(energies, dtype=float)
    if (x.ndim != 1 or y.shape != x.shape or len(x) < degree + 2
            or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or np.any(np.diff(x) <= 0)):
        raise ValueError("Need ordered finite scan points and matching energies")
    # Fit the well, not the short-range wall: keep the contiguous run of points around the scan point nearest
    # zero displacement whose energy is within FIT_WINDOW_EV of the lowest point of that run. A steep MLIP or
    # ZBL wall at -0.4 A otherwise pulls a global polynomial's error into the well (review, 24 Oct).
    i0 = int(np.argmin(np.abs(x)))
    ref = float(y[i0])
    lo = hi = i0
    while lo > 0 and y[lo - 1] - ref < FIT_WINDOW_EV:
        lo -= 1
    while hi < len(x) - 1 and y[hi + 1] - ref < FIT_WINDOW_EV:
        hi += 1
    full_x = x
    repulsive = bool(np.all(np.diff(y[x < -0.1]) <= 3 * noise_eV))  # on the whole scan, wall included
    x, y = x[lo:hi + 1], y[lo:hi + 1]
    if len(x) < degree + 2:
        raise ValueError(f"Only {len(x)} scan points within {FIT_WINDOW_EV} eV of the well for degree {degree}")
    polynomial = Chebyshev.fit(x, y, degree)
    first, second = polynomial.deriv(), polynomial.deriv(2)
    roots = sorted(float(r.real) for r in first.roots()
                   if abs(r.imag) < 1e-8 and x[0] < r.real < x[-1])
    wells = [r for r in roots if second(r) > 1e-8]
    maxima = [r for r in roots if second(r) < -1e-8]
    flags = [] if repulsive else ["nonmonotonic_repulsive_branch"]
    diagnostics = {"method": "Chebyshev least squares on the well window", "degree": degree,
                   "fit_window_eV": FIT_WINDOW_EV, "fit_range_A": [float(x[0]), float(x[-1])],
                   "n_points_fitted": int(len(x)), "n_points_scanned": int(len(full_x)),
                   "assumed_float32_noise_eV": noise_eV,
                   "rms_fit_error_eV": float(np.sqrt(np.mean((polynomial(x) - y)**2))),
                   "max_fit_error_eV": float(np.max(np.abs(polynomial(x) - y))),
                   "repulsive_branch_monotonic": repulsive, "well_positions_A": wells,
                   "barrier_height_eV": None, "flags": flags}
    if not wells:
        raise FitError("No stable fitted well in the scanned interval", diagnostics)
    # Select the basin occupied at displacement zero, not the globally deepest
    # well. Maxima delimit the basin even when the other well is lower/closer.
    left = max([r for r in maxima if r < 0] or [float(x[0])])
    right = min([r for r in maxima if r >= 0] or [float(x[-1])])
    occupied = [r for r in wells if left <= r <= right]
    minimum = min(occupied or wells, key=lambda r: (abs(r), r))
    curvature = float(second(minimum))
    barriers = []
    for a, b in zip(wells[:-1], wells[1:]):
        between = [r for r in maxima if a < r < b]
        if between:
            top = max(between, key=polynomial)
            barriers.append({"wells_A": [a, b], "position_A": top,
                             "height_from_left_eV": float(polynomial(top) - polynomial(a)),
                             "height_from_right_eV": float(polynomial(top) - polynomial(b))})
    if barriers:
        diagnostics["barrier_height_eV"] = max(max(b["height_from_left_eV"], b["height_from_right_eV"])
                                               for b in barriers)
    diagnostics.update({"barriers": barriers, "minimum_offset_A": minimum,
                        "curvature_eV_A2": curvature, "well_energies_eV": [float(polynomial(w)) for w in wells]})
    if abs(minimum) > 0.05:
        flags.append("large_minimum_offset")
    well_energy = float(polynomial(minimum))
    extensions, bounds, truncations = [], [], []
    for edge, sign, side in ((x[0], -1, "left"), (x[-1], 1, "right")):
        slope, curv = float(sign * first(edge)), float(second(edge))
        if slope < -1e-9 or (slope <= 1e-9 and curv < 0):
            # The energy falls outward at this endpoint (a further well beyond
            # the scan, e.g. the acceptor side of a long H-bond, or a short-range
            # MLIP hole). Cut at the outermost fitted maximum on this side and
            # confine there, but only if the endpoint is far above the occupied
            # well; analyze_scan also checks the quantum density at the cut.
            endpoint_above = float(polynomial(edge)) - well_energy
            outer = [r for r in maxima if (r > minimum if sign > 0 else r < minimum)]
            cut = (max(outer) if sign > 0 else min(outer)) if outer else float(edge)
            t = np.linspace(0, TRUNCATION_EXTRAPOLATION_A, 61)
            extrapolated = float(np.min(endpoint_above + slope * t + 0.5 * max(curv, 0.0) * t**2))
            record = {"side": side, "endpoint_A": float(edge), "cut_A": float(cut),
                      "endpoint_outward_slope_eV_A": slope, "endpoint_curvature_eV_A2": curv,
                      "endpoint_energy_above_well_eV": endpoint_above,
                      "cut_energy_above_well_eV": float(polynomial(cut)) - well_energy,
                      "extrapolation_A": TRUNCATION_EXTRAPOLATION_A,
                      "extrapolated_min_energy_above_well_eV": extrapolated,
                      "min_energy_above_well_eV": TRUNCATION_MIN_ABOVE_WELL_EV}
            diagnostics.setdefault("truncations", []).append(record)
            if min(endpoint_above, extrapolated) < TRUNCATION_MIN_ABOVE_WELL_EV:
                flags.append("nonconfining_scan_endpoint")
                raise FitError("Cannot extend an inward endpoint slope: the region beyond the "
                               f"{side} cut is thermally accessible (endpoint "
                               f"{endpoint_above:.3f} eV, extrapolated {extrapolated:.3f} eV "
                               "above the occupied well)", diagnostics)
            if "truncated_at_endpoint" not in flags:
                flags.append("truncated_at_endpoint")
            truncations.append(record)
            # C1 wall at the maximum: zero slope there, steep outward rise.
            extensions.append((float(polynomial(cut)), 0.0, max(curvature, 10.0), 1.0))
            bounds.append(float(cut))
            continue
        slope = max(slope, 0.0)
        # For c < 0, s+c*t+4*q*t^3 stays positive if q > |c|^3/(27*s^2).
        quartic = max(1.0, 2 * max(-curv, 0)**3 / (27 * max(slope, 1e-12)**2))
        extensions.append((float(polynomial(edge)), slope, curv, quartic))
        bounds.append(float(edge))
    diagnostics["extension"] = ("C2 quadratic plus quartic; outward derivative nonnegative"
                                + ("; C1 confining wall at the outermost maximum where the endpoint "
                                   "slope points inward" if truncations else ""))
    return FittedPotential(polynomial, tuple(bounds), minimum, curvature,
                           tuple(extensions), diagnostics, tuple(truncations))


def _check_truncation(result, fit, temperature=300.0):
    """Raise if the scanned region removed by a truncation wall is thermally accessible.

    Classical estimate of the missing partition weight relative to the converged
    free energy F of each isotope, mass variant and P:
    leak = kT * exp(beta F) * int_cut^end exp(-beta V(x)) dx / lambda_thermal.
    The integral covers the scanned part beyond the cut and the Taylor
    extrapolation past the endpoint; nothing further out is known.
    """
    diagnostics = fit.diagnostics
    if not fit.truncations:
        return
    beta = 1 / (KB_EV * temperature)
    diagnostics["truncation_density_max"] = result["numerics"]["monitor_probability_max"]
    if diagnostics["truncation_density_max"] is not None and diagnostics["truncation_density_max"] > TRUNCATION_MAX_DENSITY:
        diagnostics["flags"].append("quantum_density_at_cut")
        raise FitError(f"Quantum probability near a truncation cut is {diagnostics['truncation_density_max']:.2e} "
                       f"> {TRUNCATION_MAX_DENSITY:.0e}; widen the scan", diagnostics)
    worst = 0.0
    for record in fit.truncations:
        x = np.linspace(min(record["cut_A"], record["endpoint_A"]), max(record["cut_A"], record["endpoint_A"]), 401)
        v = fit.polynomial(x)
        t = np.linspace(0, record["extrapolation_A"], 201)
        v_out = (float(fit.polynomial(record["endpoint_A"])) + record["endpoint_outward_slope_eV_A"] * t
                 + 0.5 * max(record["endpoint_curvature_eV_A2"], 0.0) * t**2)
        leak = 0.0
        for variant in result["mass_variants"].values():
            for iso, mass in variant["masses_u"].items():
                wavelength = np.sqrt(2 * np.pi * HBAR_EV_FS**2 * beta / (mass * AMU_EV))
                for f_meV in variant["F_fit_meV"][iso].values():
                    f = f_meV / 1000
                    weight = (np.trapezoid(np.exp(-beta * (v - f)), x)
                              + np.trapezoid(np.exp(-beta * (v_out - f)), t)) / wavelength
                    leak = max(leak, float(weight / beta * 1000))
        record["leak_estimate_meV"] = leak
        record["max_leak_meV"] = TRUNCATION_MAX_LEAK_MEV
        worst = max(worst, leak)
    if worst > TRUNCATION_MAX_LEAK_MEV:
        diagnostics["flags"].append("nonconfining_scan_endpoint")
        raise FitError(f"Cannot extend an inward endpoint slope: the cut region is thermally "
                       f"accessible (leak estimate {worst:.2e} meV)", diagnostics)


def _spline_residuals(displacements, energies, fit):
    """A4b residual per mass variant with a not-a-knot cubic spline through the window points inside fit.bounds and
    fit's own confining extensions outside them."""
    from scipy.interpolate import CubicSpline
    from scipy.optimize import minimize_scalar

    x, y = np.asarray(displacements, dtype=float), np.asarray(energies, dtype=float)
    a, b = fit.bounds
    sel = (x >= a - 1e-12) & (x <= b + 1e-12)
    spline = CubicSpline(x[sel], y[sel])  # not-a-knot: exact for cubics, so a harmonic scan gives zero

    def potential(z):
        z = np.asarray(z, dtype=float)
        return np.where((z >= a) & (z <= b), spline(np.clip(z, a, b)), fit(z))

    m = minimize_scalar(lambda z: float(spline(z)), bounds=(max(a, fit.minimum - 0.1), min(b, fit.minimum + 0.1)),
                        method="bounded", options={"xatol": 1e-9}).x
    k = float(spline(m, 2))
    if not k > 0:
        raise ValueError("spline cross-check has no positive curvature at its minimum")
    res = analyze_potential(lambda z: potential(z) - float(spline(m)), k, m, monitor=fit.monitor_intervals())
    return {name: v["residual_meV"] for name, v in res["mass_variants"].items()}


def analyze_scan(displacements, energies):
    """Fit both degrees, quantify fit sensitivity, and report explicit failures."""
    diagnostics = {}
    try:
        fit = fit_potential(displacements, energies)
        diagnostics = fit.diagnostics
        result = analyze_potential(fit, fit.curvature, fit.minimum, monitor=fit.monitor_intervals())
        _check_truncation(result, fit)
        alternate = fit_potential(displacements, energies, degree=8)
        comparison = analyze_potential(alternate, alternate.curvature, alternate.minimum,
                                       monitor=alternate.monitor_intervals())
        _check_truncation(comparison, alternate)
        residual_changes, frequency_changes = {}, {}
        for name, r in result["mass_variants"].items():
            other = comparison["mass_variants"][name]
            residual_changes[name] = abs(r["residual_meV"] - other["residual_meV"])
            frequency_changes[name] = abs(r["harmonic_frequency"]["H"]["THz"]
                                          / other["harmonic_frequency"]["H"]["THz"] - 1)
        diagnostics["stability"] = {
            "comparison_degree": 8, "residual_changes_meV": residual_changes,
            "max_residual_change_meV": max(residual_changes.values()),
            "max_frequency_relative_change": max(frequency_changes.values()),
            "comparison_signed_residuals_meV": {k: v["residual_meV"]
                                                for k, v in comparison["mass_variants"].items()}}
        if alternate.diagnostics["flags"]:
            diagnostics["comparison_flags"] = alternate.diagnostics["flags"]
        # Independent cross-check: interpolating cubic spline through the same window points, same confining
        # tails. A polynomial that cannot follow a steep wall inside the window disagrees with it.
        spline_residual = _spline_residuals(displacements, energies, fit)
        spline_changes = {k: abs(result["mass_variants"][k]["residual_meV"] - v) for k, v in spline_residual.items()}
        diagnostics["spline_check"] = {"signed_residuals_meV": spline_residual, "changes_meV": spline_changes,
                                       "max_change_meV": max(spline_changes.values())}
        # Fit uncertainty enters the A4b value instead of a flag (review, 24 Oct): per mass variant the bound is the
        # largest |residual| of the degree-10, degree-8 and spline fits plus their spread, so a fit that cannot
        # follow the scan widens s_P rather than understating it.
        for name, v in result["mass_variants"].items():
            vals = [v["residual_meV"], comparison["mass_variants"][name]["residual_meV"], spline_residual[name]]
            v["fit_uncertainty_meV"] = float(max(vals) - min(vals))
            v["residual_bound_meV"] = float(max(map(abs, vals)) + v["fit_uncertainty_meV"])
        if (max(residual_changes.values()) > STABILITY_MAX_RESIDUAL_CHANGE_MEV
                or max(frequency_changes.values()) > STABILITY_MAX_FREQUENCY_CHANGE
                or max(spline_changes.values()) > STABILITY_MAX_RESIDUAL_CHANGE_MEV):
            diagnostics["flags"].append("fit_sensitive")
        # Gate: a gross misfit gives no usable A4b value (status not "complete", so aggregate_sites and
        # select_second_check cannot use it).
        if diagnostics["rms_fit_error_eV"] > FIT_MAX_RMS_NOISE * diagnostics["assumed_float32_noise_eV"]:
            diagnostics["flags"].append("poor_fit")
            return {"status": "fit_unstable", "error": "rms fit error above the noise gate",
                    **result, "fit_diagnostics": diagnostics}
        return {"status": "complete", **result, "fit_diagnostics": diagnostics}
    except (ValueError, np.linalg.LinAlgError) as exc:
        if isinstance(exc, FitError) and not diagnostics:
            diagnostics = exc.diagnostics
        return {"status": "invalid", "error": str(exc), "fit_diagnostics": diagnostics}


def distinct_hydrogens(atoms):
    import spglib

    symmetry = spglib.get_symmetry_dataset((atoms.cell.array, atoms.get_scaled_positions(), atoms.numbers),
                                           symprec=1e-4)
    if symmetry is None:
        raise ValueError("Cannot establish unit-cell symmetry")
    h_indices = np.flatnonzero(atoms.numbers == 1)
    groups = {}
    for i in h_indices:
        groups.setdefault(int(symmetry.equivalent_atoms[i]), []).append(int(i))
    result = [{"unit_cell_index": min(indices), "multiplicity": len(indices), "equivalent_indices": indices}
              for indices in groups.values()]
    assert sum(g["multiplicity"] for g in result) == len(h_indices)
    if not result:
        raise ValueError("Structure contains no H")
    return sorted(result, key=lambda g: g["unit_cell_index"])


def assign_bond(atoms, h_index):
    from ase.geometry import find_mic
    from ase.neighborlist import neighbor_list

    oxygens = np.flatnonzero(atoms.numbers == 8)
    if not len(oxygens):
        raise ValueError("H scan has no donor oxygen")
    _, nearest = find_mic(atoms.positions[oxygens] - atoms.positions[h_index], atoms.cell, atoms.pbc)
    # Bound the distance of the second O image without a chemical cutoff:
    # either a second base O, or a lattice-translated image of the nearest O.
    # By the triangle inequality the latter is at most d_nearest + |lattice|.
    ordered = np.sort(nearest)
    cutoff = float(ordered[min(1, len(ordered) - 1)])
    if np.any(atoms.pbc):
        image_bound = float(ordered[0] + np.min(np.linalg.norm(atoms.cell.array[atoms.pbc], axis=1)))
        cutoff = min(cutoff, image_bound) if len(ordered) > 1 else image_bound
    # ASE's cutoff is strict; include images on the bound despite roundoff.
    local_indices = np.concatenate(([h_index], oxygens))
    local = atoms[local_indices]
    centers, neighbours, vectors, shifts = neighbor_list(
        "ijDS", local, {(1, 8): cutoff + 1e-8})
    keep = centers == 0
    oxygen_indices = local_indices[neighbours[keep]]
    vectors, shifts = vectors[keep], shifts[keep]
    lengths = np.linalg.norm(vectors, axis=1)
    # A neighbour is (base atom, lattice translation), not just a base atom.
    # Resolve equal distances deterministically by atom index then translation.
    order = sorted(range(len(lengths)), key=lambda i: (
        float(lengths[i]), int(oxygen_indices[i]), *map(int, shifts[i])))
    donor = order[0]
    oh = -vectors[donor]
    if lengths[donor] <= 1e-8:
        raise ValueError("Coincident donor O and H")
    result = {"donor_O_index": int(oxygen_indices[donor]), "acceptor_O_index": None,
              "donor_O_image_shift": shifts[donor].tolist(), "acceptor_O_image_shift": None,
              "OH_A": float(lengths[donor]), "H_acceptor_A": None, "OO_A": None,
              "angle_deg": None, "stretch_direction": (oh / lengths[donor]).tolist(),
              "transfer_direction": None}
    if len(order) > 1:
        acceptor = int(order[1])
        # The two nearest oxygen images are selected relative to the SAME H.
        # Their difference gives a geometrically consistent O-H...O triangle.
        oo = vectors[acceptor] - vectors[donor]
        oo_length = float(np.linalg.norm(oo))
        cosine = float(np.dot(vectors[donor], vectors[acceptor]) / (lengths[donor] * lengths[acceptor]))
        result.update({"acceptor_O_index": int(oxygen_indices[acceptor]),
                       "acceptor_O_image_shift": shifts[acceptor].tolist(),
                       "H_acceptor_A": float(lengths[acceptor]), "OO_A": oo_length,
                       "angle_deg": float(np.degrees(np.arccos(np.clip(cosine, -1, 1)))),
                       "transfer_direction": (oo / oo_length).tolist() if oo_length > 1e-8 else None})
    return result


def minimum_image_distance(cell):
    """Shortest nonzero lattice vector, including nonorthogonal cells."""
    from ase.geometry import minkowski_reduce

    reduced, _ = minkowski_reduce(np.asarray(cell), pbc=True)
    return float(np.min(np.linalg.norm(reduced, axis=1)))


def make_scan_cell(atoms):
    if not np.all(atoms.pbc):
        raise ValueError("A4b requires a three-dimensional periodic cell")
    matrix = supercell_for_min_length(atoms, 8, 128)
    lattice = matrix @ atoms.cell.array
    widths = 1 / np.linalg.norm(np.linalg.inv(lattice), axis=0)
    if np.min(widths) < 8 - 1e-8 or minimum_image_distance(lattice) < 8 - 1e-8:
        matrix = supercell_for_min_length(atoms, 8, None)
    # ASE repeat preserves the entire unit cell as the first block, so the
    # representative unit-cell H index is also its index in this supercell.
    scan_cell = atoms.repeat(np.diag(matrix))
    distance = minimum_image_distance(scan_cell.cell)
    if distance < 8 - 1e-8:
        raise ValueError("Scan cell fails the 8 A periodic-image rule")
    return scan_cell, matrix, distance


def load_structure(struct_id):
    from ase import Atoms

    directory = find_cache(struct_id)
    loaded = load_fc(directory.name, root=directory.parent)
    if loaded is None:
        raise FileNotFoundError(f"Force-constant cache missing: {directory.name}")
    ph, _ = loaded
    unitcell = ph.unitcell
    atoms = Atoms(symbols=unitcell.symbols, cell=unitcell.cell,
                  scaled_positions=unitcell.scaled_positions, pbc=True)
    return atoms, directory.name


def aggregate_sites(sites, n_h):
    assert sum(h["multiplicity"] for h in sites) == n_h
    if n_h <= 0:
        raise ValueError("Cannot average an empty H population")
    invalid = False
    for site in sites:
        values = [v["residual_meV"] for scan in site["scans"] if scan["status"] == "complete"
                  for v in scan["mass_variants"].values()]
        bounds = [v.get("residual_bound_meV", abs(v["residual_meV"])) for scan in site["scans"]
                  if scan["status"] == "complete" for v in scan["mass_variants"].values()]
        valid = bool(values) and all(s["status"] == "complete" for s in site["scans"])
        site["signed_residuals_meV"] = values
        site["max_abs_residual_meV"] = max(bounds) if valid else None  # includes the fit uncertainty
        invalid |= not valid
    if invalid:
        return {"a4b_residual_meV_H": None, "max_abs_residual_meV": None, "status": "invalid"}
    return {"a4b_residual_meV_H": sum(s["multiplicity"] * s["max_abs_residual_meV"] for s in sites) / n_h,
            "max_abs_residual_meV": max(s["max_abs_residual_meV"] for s in sites), "status": "complete"}


def select_second_check(structures):
    values = {s: structures.get(s, {}).get("a4b_residual_meV_H") for s in SECOND_CHECK_IDS}
    complete = all(v is not None and np.isfinite(v) for v in values.values())
    return {"selection_rule": SELECTION_RULE, "second_P32_candidates_meV_H": values,
            "second_P32_check": max(values, key=values.get) if complete else None,
            "second_P32_selection_status": "complete" if complete else "incomplete_candidates"}


class ScanBudgetExceeded(RuntimeError):
    pass


class StaleEntry(ValueError):
    """A saved structure cannot be reanalysed without new calculator calls."""


@dataclass
class ScanBudget:
    limit_s: float = 720.0
    calculator_wall_s: float = 0.0
    points_evaluated: int = 0

    def energy(self, atoms):
        estimate = self.calculator_wall_s / max(self.points_evaluated, 1)
        if self.calculator_wall_s >= self.limit_s or self.calculator_wall_s + estimate > self.limit_s:
            raise ScanBudgetExceeded("A4b 0.2 GPU-hour calculator budget exhausted")
        started = time.perf_counter()
        try:
            energy = float(atoms.get_potential_energy())
        finally:
            self.calculator_wall_s += time.perf_counter() - started
        self.points_evaluated += 1
        if not np.isfinite(energy):
            raise ValueError("Calculator returned non-finite energy")
        return energy


def _fingerprint(atoms, matrix, info):
    data = {"numbers": atoms.numbers.tolist(), "positions_A": atoms.positions.tolist(),
            "cell_A": atoms.cell.array.tolist(), "pbc": atoms.pbc.tolist(),
            "supercell": matrix.tolist(), "calculator_info": info,
            "precision": "float32", "displacements_A": SCAN_DISPLACEMENTS.tolist(),
            "scan_protocol": 1}
    return hashlib.sha256(json.dumps(data, sort_keys=True, allow_nan=False).encode()).hexdigest()


def _reusable_raw(old_site, kind, direction):
    for scan in old_site.get("scans", []):
        if scan.get("type") != kind:
            continue
        x = np.asarray(scan.get("displacements_A", []), dtype=float)
        y = np.asarray(scan.get("raw_energies_eV", []), dtype=float)
        if (x.shape == (41,) and y.shape == (41,) and np.array_equal(x, SCAN_DISPLACEMENTS)
                and np.all(np.isfinite(y)) and scan.get("direction") == direction):
            return y
    return None


def scan_structure(atoms, cache_name, calc, info, budget, previous=None, allow_scan=True):
    """Scan one structure; with allow_scan=False only reanalyse matching saved raw energies."""
    cell, matrix, distance = make_scan_cell(atoms)
    fingerprint = _fingerprint(atoms, matrix, info)
    if not allow_scan and not (previous and previous.get("scan_fingerprint") == fingerprint):
        raise StaleEntry("saved scans do not match the current geometry or model")
    previous = previous if previous and previous.get("scan_fingerprint") == fingerprint else {}
    prior_sites = {h["unit_cell_index"]: h for h in previous.get("distinct_H", [])}
    cell.calc = calc
    initial = cell.positions.copy()
    baseline = None
    sites = []
    start_points = budget.points_evaluated
    for group in distinct_hydrogens(atoms):
        h = group["unit_cell_index"]
        bond = assign_bond(atoms, h)
        site = {**group, **bond, "scans": []}
        directions = [("stretch", bond["stretch_direction"])]
        if bond["OO_A"] is not None and bond["OO_A"] < 2.7:
            if bond["transfer_direction"] is None:
                raise ValueError("Degenerate O...O transfer coordinate")
            directions.append(("transfer", bond["transfer_direction"]))
        for kind, direction in directions:
            raw = _reusable_raw(prior_sites.get(h, {}), kind, direction)
            reused = raw is not None
            if raw is None and not allow_scan:
                raise StaleEntry(f"no reusable saved {kind} scan for H {h}")
            if raw is None:
                if baseline is None:
                    cell.positions[:] = initial
                    baseline = budget.energy(cell)
                raw = []
                try:
                    for displacement in SCAN_DISPLACEMENTS:
                        cell.positions[:] = initial
                        cell.positions[h] = initial[h] + displacement * np.asarray(direction)
                        raw.append(budget.energy(cell) - baseline)
                finally:
                    cell.positions[:] = initial
            scan = {"type": kind, "direction": direction, "displacements_A": SCAN_DISPLACEMENTS.tolist(),
                    "raw_energies_eV": np.asarray(raw).tolist(), "raw_reused": reused,
                    "energy_reference": "undisplaced cached geometry (separately evaluated)",
                    **analyze_scan(SCAN_DISPLACEMENTS, raw)}
            site["scans"].append(scan)
        sites.append(site)
    n_h = int(np.count_nonzero(atoms.numbers == 1))
    summary = aggregate_sites(sites, n_h)
    flags = sorted({flag for s in sites for scan in s["scans"]
                    for flag in scan.get("fit_diagnostics", {}).get("flags", [])})
    return {"cache_dir_name": cache_name, "scan_fingerprint": fingerprint,
            "supercell": matrix.tolist(), "natoms": len(cell), "natoms_unit_cell": len(atoms),
            "min_image_distance_A": distance,
            "min_perpendicular_width_A": float(np.min(1 / np.linalg.norm(np.linalg.inv(cell.cell.array), axis=0))),
            "n_H": n_h, "distinct_H": sites, "points_evaluated": budget.points_evaluated - start_points,
            "equilibrium_energy_eV": baseline if baseline is not None else previous.get("equilibrium_energy_eV"),
            "quality_flags": flags, **summary}


def _git_hash():
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _h1_flag(struct_id, structure):
    value = structure.get("a4b_residual_meV_H")
    structure["H1_above_0p19_meV_H"] = (None if value is None
                                        else bool(struct_id in STRUCT_IDS[:5] and value > 0.19))
    return structure


def _demote(old, status, reason):
    """Keep a saved entry's raw scans but strip every usable value from it.

    The raw energies stay reusable: a later run reuses them only if the
    scan fingerprint (geometry, supercell, model) still matches.
    """
    old = old or {}
    dropped = ("a4b_residual_meV_H", "max_abs_residual_meV", "status", "error", "H1_above_0p19_meV_H")
    entry = {k: v for k, v in old.items() if k not in dropped}
    if old and "previous_status" not in old:
        entry.update({"previous_status": old.get("status"),
                      "previous_a4b_residual_meV_H": old.get("a4b_residual_meV_H")})
    entry.update({"status": status, "error": reason, "a4b_residual_meV_H": None,
                  "max_abs_residual_meV": None, "H1_above_0p19_meV_H": None})
    return entry


def run(struct_ids, out, device="cuda"):
    """Collect scans, reanalyse compatible saved scans, and checkpoint structures.

    The output always holds every structure of the previous file: requested
    ids are rescanned (reusing matching raw scans), all others are reanalysed
    from their saved raw energies without calculator calls, or kept with their
    raw data and marked stale if the geometry or model no longer matches.
    """
    started = time.perf_counter()
    struct_ids = list(struct_ids)
    if not struct_ids or len(set(struct_ids)) != len(struct_ids) or any(s not in STRUCT_IDS for s in struct_ids):
        raise ValueError("Choose distinct P12 structure ids")
    out = Path(out)
    previous = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    old_structures = previous.get("structures", {})
    init_start = time.perf_counter()
    calc = get_calculator("mace", device=device)
    info = calculator_info(calc)
    budget = ScanBudget(calculator_wall_s=time.perf_counter() - init_start)
    report = {"schema_version": 1, "T_K": 300.0, "P": [16, 128, "inf"],
              "masses_u": {"H": M_H, "D": M_D, "O": M_O, "variants": mass_variants()},
              "calculator_info": info, "potential_precision": "float32", "git_hash": _git_hash(),
              "module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "units": {"length": "A", "raw_energy": "eV", "mass": "u", "temperature": "K",
                        "free_energy": "meV per H"},
              "sign_convention": "dF=F_D-F_H; Delta_anh=dF_fit-dF_harmonic at same P; residual=Delta_anh(16)-Delta_anh(128)",
              "limitations": LIMITATIONS, "structures": {}, "requested_structures": struct_ids,
              "gpu_budget_h": 0.2, "status": "running"}
    history = list(previous.get("run_history", []))
    out.parent.mkdir(parents=True, exist_ok=True)

    def save():
        report["structures"] = {s: report["structures"][s] for s in STRUCT_IDS if s in report["structures"]}
        report.update(select_second_check(report["structures"]))
        this_run = {"requested_structures": struct_ids, "git_hash": report["git_hash"],
                    "module_sha256": report["module_sha256"],
                    "wall_time_s": time.perf_counter() - started,
                    "calculator_wall_time_s": budget.calculator_wall_s,
                    "points_evaluated": budget.points_evaluated}
        report.update({"wall_time_s": this_run["wall_time_s"],
                       "calculator_wall_time_s": budget.calculator_wall_s,
                       "calculator_time_h": budget.calculator_wall_s / 3600,
                       "calculator_budget_exceeded": budget.calculator_wall_s > budget.limit_s,
                       "points_evaluated": budget.points_evaluated,
                       "missing_structures": [s for s in STRUCT_IDS if s not in report["structures"]],
                       "run_history": history + [this_run],
                       "calculator_time_h_all_runs": sum(r["calculator_wall_time_s"]
                                                         for r in history + [this_run]) / 3600})
        out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def carry(struct_id):
        old = old_structures[struct_id]
        if "scan_fingerprint" not in old:
            # Nothing to verify or reanalyse (an earlier invalid or budget stub).
            report["structures"][struct_id] = old
            return
        try:
            atoms, cache_name = load_structure(struct_id)
            structure = scan_structure(atoms, cache_name, calc, info, budget, old, allow_scan=False)
            structure["carried_over"] = True
            report["structures"][struct_id] = _h1_flag(struct_id, structure)
        except (ValueError, LookupError, OSError) as exc:
            report["structures"][struct_id] = _demote(old, "stale", f"not reanalysed: {exc}")

    # Seed with every saved structure so a subset rerun (or a crash midway)
    # never deletes the others. Requested ids keep their old entry until rescanned.
    for struct_id in STRUCT_IDS:
        if struct_id in old_structures:
            if struct_id in struct_ids:
                report["structures"][struct_id] = old_structures[struct_id]
            else:
                carry(struct_id)

    done = set()
    for struct_id in struct_ids:
        done.add(struct_id)
        old = old_structures.get(struct_id)
        try:
            atoms, cache_name = load_structure(struct_id)
            structure = scan_structure(atoms, cache_name, calc, info, budget, old)
            report["structures"][struct_id] = _h1_flag(struct_id, structure)
        except ScanBudgetExceeded as exc:
            report["structures"][struct_id] = _demote(old, "budget_exhausted", str(exc))
            report["status"] = "budget_exhausted"
            break
        except (ValueError, LookupError, OSError) as exc:
            report["structures"][struct_id] = _demote(old, "invalid", str(exc))
        save()
    # Requested ids never reached (budget stop) must not keep an unverified old entry.
    for struct_id in struct_ids:
        if struct_id not in done and struct_id in old_structures:
            carry(struct_id)
    if report["status"] == "running":
        if budget.calculator_wall_s > budget.limit_s:
            # A single in-flight calculator call cannot be interrupted safely.
            # Never mark such a run as having met the hard budget.
            report["status"] = "budget_exhausted"
        else:
            report["status"] = "complete" if all(s["status"] == "complete" for s in report["structures"].values()) else "invalid"
    save()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "results/pimd/a4b_scan_residual.json")
    parser.add_argument("--structs", nargs="+", choices=STRUCT_IDS, default=list(STRUCT_IDS))
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args(argv)
    report = run(args.structs, args.out, args.device)
    print(json.dumps({"status": report["status"], "points_evaluated": report["points_evaluated"],
                      "second_P32_check": report["second_P32_check"], "out": str(args.out)}))
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
