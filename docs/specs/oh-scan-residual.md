# Spec: oh-scan-residual (src/isoshift_event/oh_scan_residual.py)

## Goal and why
P12 section 2a (`docs/predictions/P12_pimd.md`, decision 18 A4, A4b and action 3) runs every production PIMD value at P = 16 and references it to the same-P harmonic value. The P = 32 pilot on mp-625152 only detects gross bead errors near 0.45 meV/H. The fine bound on the anharmonic bead residual comes from this module: a per-structure 1D estimate, from float32 MACE energy scans of each symmetry-distinct H, of how far Delta_anh(16) is from the converged value. Its number enters s_P = max(0.05, A4b residual, |d| - sigma_d) for every structure, and it names the structure for the second P = 32 check (run table row 8). It must exist and be committed before PIMD row 1 runs, so it is blind to all PIMD data. Decision 18 also says: any H1 structure with an A4b residual above about 0.19 meV/H cannot meet the 1 meV/H bar at P = 16.

Owned files (the only files you may create or edit): `src/isoshift_event/oh_scan_residual.py`, `tests/test_oh_scan_residual.py`. Do not edit `isoshift/`, `docs/`, `src/isoshift_event/pimd.py` or other modules. Reading and importing them is fine.

## Context to read first
`docs/predictions/P12_pimd.md` (sections 1, 2a), `docs/decisions/18-pimd-design.md` (A3, A4, A4b, action 3), `docs/decisions/17-pimd-method.md` (item 3, the Morse table), `docs/math/M00-plumbing-diatomic-zpe.md` (reduced mass, finite O mass), `PLAN.md` P1 to P6.
Existing code to reuse:
* `src/isoshift_event/pimd.py`: `find_cache(struct_id)` returns the one matching cache dir (raises on 0 or several; never guess), constants `HBAR_EV_FS`, `AMU_EV`, `KB_EV`, `M_H`, `M_D`, and `_osc_free_energy(nu_thz, T, P)`, the analytic P-bead and quantum harmonic free energy used by the PIMD reference. Your harmonic numbers must agree with it.
* `isoshift/cache.py::load_fc(key_or_dirname)` returns `(Phonopy, meta)`; the relaxed unit cell is `ph.unitcell` (PhonopyAtoms; convert to ASE). The phonopy object also carries the symmetry of that cell.
* `isoshift/phonons.py`: `supercell_for_min_length(atoms, 8, 128)` (the PIMD cell rule), `MASS_MAP` (H 1.00782503, D 2.01410178 u).
* `isoshift/calculators.py::get_calculator("mace")`: medium-mpa-0, float32, falls back to CPU without CUDA. This is the PES of the cached force constants and of the PIMD runs (A1), so do not load float64.

## Requirements (what, not how)
1. Structures: the 9 P12 ids (mp-23807, mp-625054, JVASP-54682, JVASP-92228, mp-625152, mp-626497, mp-985293, mp-23940, mp-626000), geometry exactly as cached. No re-relaxation (P12 freezes the screen geometry, A13).
2. Scan cell: the PIMD supercell from `supercell_for_min_length(atoms, 8, 128)`, or a larger one if needed so the scanned H is at least 8 A from its own periodic images. Record the supercell and its minimum image distance. mp-985293 hits the cap at 7.32 A min width, so expect to enlarge it there.
3. Distinct H: symmetry-equivalence classes of H on the unit cell (spglib or phonopy). Multiplicity = class size; the multiplicities must sum to n_H of the cell (assert it).
4. Bond assignment per distinct H, minimum image: donor O = nearest O; acceptor = nearest O other than the donor. Record O-H, H...O, O...O and the O-H...O angle. A "no acceptor" case must be handled, not crash.
5. Scans (float32 MACE energies, only that one H moves, all other atoms fixed): (a) along the unit vector donor O to H, 41 points from -0.4 to +0.8 A relative to equilibrium; (b) if O...O < 2.7 A, also along the unit vector donor O to acceptor O, same 41-point range relative to the equilibrium H position (proton-transfer coordinate, may be a double well). Store the raw energies (relative to the equilibrium point, eV) so the analysis can be redone without the GPU.
6. Per scan, a smooth 1D potential from the scan energies with a safe confining extension outside the scanned range. Then the 1D quantum free energy at 300 K for H and D: primitive (Trotter) discretized path integral at P = 16 and P = 128, and the exact P = infinity value. Two mass variants per scan: O-H reduced mass (O = 15.999 u, M00) and bare H/D mass; store both.
7. Harmonic reference per scan: the harmonic potential with the same curvature at the minimum of the fitted potential, evaluated by the same numerical method at the same P. Delta_anh(P) = [F_D - F_H]_P,fit - [F_D - F_H]_P,harm in meV; residual = Delta_anh(16) - Delta_anh(128). Also store the harmonic frequency (cm^-1 and THz, both mass variants) and the offset of the fitted minimum from the scan origin.
8. Per structure: per-H value = largest |residual| over that H's scans and both mass variants (the scans overlap; do not add them). Report the multiplicity-weighted mean of the per-H values as `a4b_residual_meV_H` (this is the s_P input), the max, and the signed residuals behind them. `second_P32_check` = the structure with the largest `a4b_residual_meV_H` among mp-23807, mp-625054, JVASP-54682, JVASP-92228 (mp-625152 excluded by rule), with the four values listed.
9. Output `results/pimd/a4b_scan_residual.json` (create the directory): top-level T, P list, masses, model info (`calculator_info`), git hash, wall time, the selection rule text and `second_P32_check`; per structure: cache dir name, supercell, natoms, min image distance, n_H, per distinct H (index in the unit cell, multiplicity, donor and acceptor O indices, O-H, H...O, O...O, angle, scans with type `stretch` or `transfer`, raw energies, harmonic frequencies, Delta_anh at 16, 128 and inf per mass variant, residual, fit diagnostics), weighted mean and max |residual|. JSON stays small (no grids or matrices). Units: A, eV, u, K; free energies in meV per H.
10. CLI: `python -m src.isoshift_event.oh_scan_residual --out results/pimd/a4b_scan_residual.json [--structs id ...] [--device cuda]`. A rerun with an existing output may reuse stored scans, but only if the geometry and model match.

## Hard limits
* Budget 0.2 GPU h for all 9 structures (RTX 4060 Laptop, 8 GB). Record wall time and points evaluated.
* The fixed-atom 1D model covers the stretch and the 1D transfer coordinate only, not stretch-bend coupling (decision 18). Say so in the JSON, do not claim more.
* No sign convention of its own: F_D - F_H, Delta_anh = anharmonic minus harmonic at the same P, residual = Delta_anh(16) - Delta_anh(128).

## Known pitfalls
* Discretization must cancel. The P = 16 bead error of raw F_D - F_H is about 5.7 meV for an O-H stretch; the residual is about 0.05 meV. The harmonic and anharmonic values at a given P must use the same P, grid and propagator, and the harmonic one must also reproduce `_osc_free_energy` (P = 16, 128 and quantum) to well below 1e-3 meV, or the grid is not converged. At P = 128 the free-particle kernel width for H at 300 K is about 0.035 A.
* Float32 energy noise. Total energies of a 100-plus-atom cell are about -800 eV, so float32 rounding is about 5e-5 eV per point. Curvature from closely spaced points amplifies it. Show that the fitted frequency and residual are stable (for example against fit choice or point subsets) and record a diagnostic.
* The fitted minimum need not sit at displacement 0 (float32 relaxation, fmax up to 0.031 eV/A for mp-23940). Use the minimum of the fit for the harmonic reference, record the offset, and flag a large one.
* At -0.4 A the H is about 0.57 A from O, far outside MACE training data. Check the repulsive branch is monotonic; non-physical behaviour there must be flagged, not smoothed silently. The extension beyond the range must confine without creating a spurious well, and the probability density at the grid edges must be negligible (record it).
* Double wells (transfer scans in short H-bonds): the harmonic reference uses the curvature of the well the H sits in; the code must not fail if the two wells are near symmetric or the barrier is low. Report barrier height and well positions.
* Periodic images of the moved H move with it. That is why the 8 A image rule exists.
* Windows paths. No network, model download or GPU in tests.

## Already done
P12 section 2a is committed (7ce63d1). `pimd.py` exists with the constants, `find_cache` and the analytic P-bead harmonic free energy. Cache entries and raw screen JSONs for all 9 structures are local. The chair's `morse2.py` template is not in the repo; the reference numbers below were reproduced independently by the spec author with a primitive transfer matrix (700-point grid, sinc DVR for P = infinity, O = 15.999 u, harmonic frequency defined with the O-H reduced mass, same force constant for D). Neither owned file exists yet. `results/pimd/` does not exist.

## Tests (tests/test_oh_scan_residual.py)
CPU only, no MACE, deterministic, under a minute or two. At least:
* Morse O-H, omega_e = 3600 cm^-1, D = 4.6 eV, reduced mass with O 15.999 u (decision 17 row): Delta_anh(16) = 1.222, Delta_anh(inf) = 1.272, each within 0.005 meV; residual Delta_anh(16) - Delta_anh(128) = -0.053 within 0.005.
* Morse with omega_e = 3600 cm^-1, omega_e x_e = 82 cm^-1 (D about 4.90 eV): Delta_anh(16) - Delta_anh(96) = -0.051 within 0.005 (decision 18 quotes -0.052 at 108 THz). The spec author got Delta_anh(inf) = 1.195 for this set; the 1.27 figure belongs to the D = 4.6 eV set.
* Harmonic potential: Delta_anh = 0 at P = 16, 128 and inf to 1e-6 meV; F_D - F_H matches `_osc_free_energy` at each P.
* Symmetric double well: runs, finite outputs, barrier and wells reported.
* The full pipeline (fit, distinct-H grouping, assignment, weighting, selection, JSON schema, CLI) on a small synthetic periodic cell with a fake analytic energy calculator, including a no-acceptor H and a short O...O that triggers the transfer scan.

## Acceptance
`.venv/Scripts/python.exe -m pytest -q tests/test_oh_scan_residual.py`
Judged on: tests pass with the tolerances above, not loosened; the review checks the code against A4b (41 points, ranges, fixed atoms, 2.7 A rule, P = 16 vs 128, per-H weighting, selection rule excluding mp-625152) and the JSON fields. Do not run the MACE scans or commit `results/pimd/` output; the conductor runs and commits it.
