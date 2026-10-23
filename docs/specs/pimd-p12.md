# Spec: pimd-p12 (src/isoshift_event/pimd.py)

## Goal and why
Both round-1 referees asked for a beyond-harmonic control of the headline isotope double differences. `docs/predictions/P12_pimd.md` (committed in a91fcca, before any PIMD data) fixes the pairs, method, error targets and outcome rules. This module is the only producer of those numbers: per structure, the full H to D substitution free energy from path-integral MD with MACE medium-mpa-0, the same-cell harmonic value from the cached MACE force constants, and their difference Δ_anh. **Section 2 of P12 is binding. Do not change the method, temperature, quadrature, potential or supercell rule.** If something in it cannot be done, say so in your report. Do not work around it.

Owned files (the only files you may create or edit): `src/isoshift_event/pimd.py`, `tests/test_pimd.py`. Nothing under `isoshift/`, `docs/` or other `src/` modules is edited (reading and importing them is fine).

## Context to read first
`docs/predictions/P12_pimd.md` (sections 1 and 2), `docs/math/M00-plumbing-diatomic-zpe.md` (diatomic, masses, units), `docs/math/M01-isotope-formulas.md` (harmonic F per variant, the Γ acoustic treatment note at the end), `PLAN.md` P1 to P6.
Existing code:
* `isoshift/phonons.py`: `make_masses(atoms, substitution, default="light")` (H = 1.00782503 u, D = 2.01410178 u via `MASS_MAP`), `supercell_for_min_length(atoms, min_length, max_atoms)`, `phonopy_with_masses(ph, masses)`, `MeshFreqs` (drops modes below `GAMMA_TOL_THZ`, F in eV per unit cell), constants `KB_EV`, `H_EV_THZ`.
* `isoshift/cache.py`: `load_fc(key)` returns `(Phonopy, meta)`. Entries live in `.cache/isoshift/<hash>__mace-medium-mpa-0__sc<a>x<b>x<c>__d0.01__sym/` with `meta.json` keys `supercell`, `natoms_cell`, `natoms_supercell`, `energy_eV`, `volume_A3`. The relaxed unit cell is `ph.unitcell`.
* `results/raw/screen/mace/<id>.json` (gitignored, local): `fc_meta` has the same keys. `src/isoshift_event/refine.py::_cache_index` and `decompose.py` show the existing raw-to-cache matching. P12 requires matching on energy within 1e-6 eV, equal `natoms_cell` and equal `supercell`. Zero matches or more than one is an error, never a guess.
* `isoshift/calculators.py::get_calculator("mace")` loads float32. PIMD must run MACE in float64. Load the model yourself (mace-torch 0.3.16, torch 2.6 cu124 in `.venv`). `mace.calculators.MACECalculator` shows how it builds `AtomicData` and calls the model.

## Requirements (what, not how)
1. Ring polymer of P beads of the periodic supercell (fixed cell, PBC). All P bead configurations go through one batched MACE forward pass per step, with conservative forces in float64. A pure-numpy harmonic force backend (given a force-constant matrix and reference positions) gives the same interface for tests and for checking the integrator.
2. Normal-mode ring-polymer propagation with the exact free ring-polymer step and a PILE-L thermostat (Ceriotti et al., J. Chem. Phys. 133, 124104 (2010)). Centroid Langevin time constant tau0 (default 100 fs), internal modes critically damped (gamma_k = 2 omega_k). Masses are a per-atom array, so the H mass can be scaled on its own.
3. Centroid-virial kinetic energy of the H atoms only: K_H = (3 n_H / 2) kT + (1/2P) Σ_k Σ_{i∈H} (q_ik − qc_i) · (−f_ik). f are the physical forces on each bead. Bead coordinates must stay unwrapped (no wrapping or minimum image between beads of one atom).
4. TI over H mass with g = sqrt(m_H/m): F(m_D) − F(m_H) = ∫ from 1 to g_D of 2 <K_H(g)>/g dg, g_D = sqrt(m_H/m_D) = 0.70737. Gauss-Legendre with n points (default 4) on [g_D, 1]. Report per H in meV, with the statistical error from block averaging propagated through the quadrature weights. The result must be negative for any sane system.
5. Same-cell harmonic reference. From the cached force constants, harmonic F_D − F_H at T using only the q-points commensurate with the PIMD supercell. Masses come from `make_masses` with `{"H": "D"}` vs light H. Report per H in meV. The PIMD supercell (min_length 8, cap 128) can differ from the cache's force-constant supercell. That is expected, because the commensurate q-points are interpolated from the cached force constants.
6. CLI: `python -m src.isoshift_event.pimd --struct <id> --beads P --steps N --dt <fs> --masses-points 4 --out results/pimd/<id>_P<P>.json`. Defaults: T 300 K, dt 0.25 fs, tau0 100 fs, 20 % equilibration per mass point, and a seed recorded in the output. The JSON holds per mass point g, mass, weight, <K_H> and its error, steps used, block info and wall time. It also holds ΔF_PIMD with its error, ΔF_harm_samecell and Δ_anh, all per H in meV, plus struct_id, cache key, supercell, natoms, n_H, P, dt, T, tau0, model info, git hash, initial max |F| in float64, peak GPU memory and status.
7. Each mass point after the first starts from the end state of the previous one. Its own equilibration is discarded. The file is rewritten after every mass point, and a rerun with the same arguments resumes and skips the completed points. Bulky restart state belongs under `.cache/pimd/` (gitignored). `results/pimd/` is committed per P12, so keep the JSON small.

## Hard limits
* GPU: RTX 4060 Laptop, 8 GB. P beads × up to 128 atoms in float64 must fit. Measure the peak. If a bead batch does not fit, fail clearly or use an explicit, recorded option. A silent change of P, supercell or dtype is never acceptable.
* Units: Å, eV, u, fs, K. Get hbar and kT in consistent units, because the free ring-polymer frequencies depend on them. Print or record steps/s so production cost can be estimated (P12 has 9 structures, a P vs 2P pilot and 4 mass points each).
* No sign convention of its own: Δ_anh = [F_D − F_H]_PIMD − [F_D − F_H]_harm,same cell per structure. Pair assembly (ddF_corr) is not part of this module.

## Known pitfalls
* Translation and Γ acoustic modes. The PIMD centroid includes the free whole-cell translation, while `MeshFreqs` drops Γ modes below `GAMMA_TOL_THZ`. The two references must treat the zero modes consistently, or Δ_anh picks up a spurious mass-dependent term (small per H, but the targets are 0.3 meV). Document your choice.
* Finite P. The harmonic-backend PIMD converges to the quantum harmonic result only as P grows. A test that compares against the P → ∞ value at small P mixes discretization with sampling error. The finite-P harmonic answer is known in closed form.
* Restarting at a new mass. Momenta and normal-mode transforms depend on the masses and must be consistent with the new mass at the start of each point.
* The cached geometry was relaxed in float32, so float64 forces at t = 0 are small but nonzero. Record them; do not re-relax (P12 fixes the screen geometry).
* Block averaging underestimates the error if the blocks are shorter than the K_H correlation time. Show that the error has reached a plateau in block size, or report the number of blocks and the block length.
* Imaginary modes on the commensurate grid: flag them in the JSON and never take absolute values (P2).
* Windows paths, and no network or model download inside tests.

## Already done
P12 is predeclared and committed. Cache entries and raw screen JSONs exist locally for all 9 structures. Neither `pimd.py` nor `tests/test_pimd.py` exists yet. No PIMD data exists, and none may be produced before this module passes acceptance.

## Tests (tests/test_pimd.py)
CPU only. No MACE load, no GPU, no network, seeded and deterministic, a few minutes at most. A GPU MACE smoke test is optional and must skip cleanly without CUDA. Cover at least:
* 1D harmonic oscillator and an isolated O-H diatomic (M00 masses, finite O mass), where P12 requires H to D within 0.2 meV of the analytic quantum value.
* TI quadrature: with exact harmonic <K_H(g)>, the 4-point rule reproduces the analytic F_D − F_H.
* A small periodic toy crystal with known force constants, where harmonic-backend PIMD agrees with the same-cell harmonic reference within its error.
* Equal masses give zero, and the H-only estimator ignores non-H atoms.
* CLI matching and JSON schema on a fake cache and raw tree in tmp_path, including the ambiguous and missing cases, plus resume after an interrupted run.

## Acceptance
`.venv/Scripts/python.exe -m pytest -q tests/test_pimd.py`
Judged on: the tests pass and the 0.2 meV analytic checks are real, not loosened. The review then checks the code against P12 section 2 point by point (potential, float64, single batched call, PILE-L parameters, estimator, quadrature, same-cell reference, supercell rule, cache matching) and the JSON fields above. Report the steps/s and peak memory of one short MACE run on mp-23807 if the GPU is free. Do not commit any `results/pimd/` output.
