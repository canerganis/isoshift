# Spec: screen (src/isoshift_event/screen.py)

## Goal and why
The overnight GPU screen is the only producer of the numbers the whole project ranks, plots and claims: per-structure harmonic H and D vibrational free energies from four universal MLIPs, and per-pair isotope double differences ΔΔF_iso(T). It must run unattended for ~10 h on one 8 GB laptop GPU, survive crashes and restarts by a watchdog, and never silently lose or invent a structure. Per PLAN.md P3, compute happens per unique structure; pair quantities are post-processing only.

Owned files (the only files you may create or edit): `src/isoshift_event/screen.py`, `tests/test_screen.py`. Nothing under `isoshift/` is edited; if the pool or worker blocks you, say so in your report instead of patching it.

## Context to read first
`state/LEDGER.md` (module contracts, binding), `PLAN.md` (P1 to P6, P11, P13 to P15, P18, P19), `docs/specs/pool-persistent-gpu-worker.md`, `prep/feasibility_isoshift/REPORT.md`, `docs/math/` (accepted formulas only).
Existing code to build on:
* `isoshift/pool.py`: `submit(queue_dir, kind, cif, calc, out, **kw)` (returns None if `out` exists, job id hashes `[kind, cif, calc, out, kw]`), `launch(calc, queue_dir, device, idle_exit_s, mem_fraction, cache_root) -> pid`, `status(queue_dir)`, `requeue_stale(queue_dir)`, `launch_cmd` (already routes sevenn and mattersim to `.venv-sevenn/Scripts/python.exe`, so the pool serves all four models; confirm, do not build a second launcher unless you find it cannot). The sevenn/mattersim pool path was not exercised by pool acceptance, so treat its first job as a smoke test.
* `isoshift/worker.py` `harmonic_job(cif, calc_name, min_length, max_atoms, fmax, relax_cell, mesh, temps, subs, supercell, steps)`: relax (FixSymmetry + FrechetCellFilter, `isoshift/relax.py`), cached force constants, then per mass variant `zpe_eV_cell`, `F_eV_cell` on `temps`, `imag` (`min_freq_THz`, `has_imaginary` at `IMAG_TOL_THZ = -0.1`, `n_imag_modes`, `imag_fraction`); plus `relax` (`converged`, `energy` eV/cell, `volume` Å³/cell, `fmax_final`), `fc_meta` (`supercell`, `natoms_supercell`, `energy_eV`), `mesh`, `n_atoms`, `formula`, `calc` (name, model, version), and `pool` block.
* `isoshift/phonons.py`: `supercell_for_min_length`, `choose_mesh`, `make_masses`. `isoshift/calculators.py`: `MAX_ATOMS` (mace/orb 400, mattersim 300, sevenn 100), `DEFAULT_MODELS`. `isoshift/compare.py`: `crossing_temperatures`, `isotope_shift`, `ddF_iso_at`, `ensemble`.

## Inputs
* `data/isoshift/structures.csv` and `data/isoshift/pairs.csv`, schema in the LEDGER contracts (`struct_id`, `cif` repo-relative, `nsites`; `pair_id`, `struct_a`, `struct_b`, `dE_meV_atom` b minus a, `tier` 16|32, `flags` `;`-joined). Both are produced in parallel by `pairs.py` and may not exist yet when you run; do not wait for them and do not write them.
* Optional filter by pair tier. Only structures referenced by selected pairs are computed, each once per model.

## CLI (python -m src.isoshift_event.screen ...)
`submit`, `run`, `status`, `collect`, `dryrun`. Flags and defaults are yours; document them in `--help`. Defaults must point at the real paths below so the watchdog can call `run` and `status` with no arguments.
* submit: structures x models harmonic jobs. Re-running adds nothing for jobs whose result exists, is pending or running. P19: bounded retries (2) then the structure/model is quarantined; note that `pool.submit` on its own resubmits failed jobs forever.
* run: requeue stale claims and launch workers. mace and orb concurrently with `mem_fraction=0.45`; sevenn always alone on the GPU; mattersim never alongside sevenn. Must be safe to call repeatedly (watchdog): no duplicate live workers per model.
* status: queue counts per model, live workers, failures, ETA if you can.
* collect: builds the two CSVs below from whatever results exist; safe on a partial queue.
* dryrun: end to end on N pairs and the given models in an isolated queue and output dir outside the real `results/` (a fixed gitignored location such as `.cache/screen_dryrun/`, so a rerun can reuse it), real GPU jobs, then collect, printing both tables. When `pairs.csv`/`structures.csv` are missing it must fall back to a small built-in pair set from `data/isoshift/validation_structures/index.json` (e.g. MgH2, Mg(OH)2, Ca(OH)2 polymorphs; brucite is a good quarantine test, orb shows -37 THz).

## Outputs (paths and units binding, other modules read them)
* Raw: `results/raw/screen/<model>/<struct_id>.json` (pool result, gitignored). Queue under `results/queue/` (gitignored).
* `results/screen_structures.csv`, one row per structure x model: relaxed E and V per atom (eV/atom, Å³/atom), F_vib^H(T) and F_vib^D(T) on the grid (meV/atom; wide or long layout, your call, but self-describing), ZPE H and D (meV/atom), S at 300 K for H and D (meV/atom/K), min frequency (THz) and imaginary-mode report, relax converged flag, supercell, n_atoms, H count, model id/version, status (ok | quarantined | failed | missing) with reason.
* `results/screen_pairs.csv`, one row per pair x model: ΔΔF_iso at 0, 300, 600 K per atom (meV/atom) and per H (meV/H); static ΔE from the MLIP relaxed energies (meV/atom, b minus a, same convention as `pairs.csv`); crossing temperatures for H and D when they exist (K, empty otherwise); flags. Pairs with a missing, failed or quarantined member stay in the table with a flag.
* Temperature grid 0 to 1000 K inclusive, fine enough that S(300 K) from it is accurate to well under the P3 slope guard (0.01 meV/atom/K). Same grid for every job.

## Physics rules (PLAN.md wins on conflict)
* P4: one supercell per structure, shared by all models (min perpendicular length ~9.5 Å, ≤ 160 atoms), passed explicitly as `supercell`. Explicit supercell disables the pool's OOM shrink, by design. sevenn's cap is 100 atoms: a structure whose shared supercell exceeds what a model can hold is recorded as skipped for that model with a reason, never run on a different supercell. Keep the q mesh identical across models for a structure too, otherwise model spread includes mesh spread.
* P2/P11: imaginary optical modes mean quarantined, listed, never dropped and never absolute-valued. Repair (eigenvector following) belongs to `stability.py`, not here. The worker report does not separate acoustic noise near Γ from optical modes; pick a documented threshold rule and record it in the CSV.
* P11 relax target fmax 1e-4 eV/Å; float32 models may not reach it in the default steps. Whatever you pass must be identical across models and the converged flag must be reported, not hidden.
* P13 sign: ΔΔF_iso = [F_D(β) − F_D(α)] − [F_H(β) − F_H(α)] with α = struct_a, β = struct_b. `compare.ddF_iso_at` uses the opposite (a minus b) order; do not inherit its sign by accident. Normalise per atom of each structure (Z1 ≠ Z2), per H from that.
* Crossings: G(T) = E_static + F_vib(T) per atom; P3 slope guard and P15 (crossings above 600 K flagged, ΔE > 25 meV/atom per model flagged per P13, no hard filter, nothing dropped). P5: flag pairs whose two members relax to the same structure.
* M01 (ΔΔF_iso, crossing, ΔT estimates) is still in mathcheck. Until `docs/math/M01*.md` is accepted, keep all pair formulas behind one small function so they can be swapped without touching the rest; if M01 has landed when you start, use it verbatim.
* `F_eV_cell` and `zpe_eV_cell` are per input cell (phonopy `primitive_matrix="P"` is identity), so normalise with the job's `n_atoms` and the H count of that relaxed cell, not the CIF's formula units.
* The worker output has no mode-band split, so P3's "anharmonic-sensitive" flag is out of scope here; say so in the CSV docs, do not add it by editing `isoshift/`.

## Pitfalls
* Job ids hash kw: any non-deterministic kw (float formatting, list vs tuple, dict order of `subs`) breaks idempotency. A result file written under an older config is accepted by `pool.submit`; collect should check that supercell, temps and model match what it expects and flag mismatches.
* Pool result JSON is atomic; partial files are never valid. Heartbeats go stale after 600 s.
* Windows: workers are detached processes; `run` must not block on them. Paths in jobs are absolute.
* GPU memory: ~8 GB total, mace + orb peak up to ~7.6 GB; sevenn 5 to 7 GB at ~100 atoms. Throughput (REPORT): 3 to 14 s per structure for mace/orb, 7 to 29 s for sevenn.

## Tests (tests/test_screen.py)
CPU only, no model downloads, no GPU, under ~30 s: use small synthetic results or `serve(..., loader=...)` with a cheap ASE calculator. Cover at least idempotent resubmit, shared supercell across models, collect on partial and quarantined inputs, the P13 sign with an H↔D swap, equal masses giving zero ΔΔF_iso, and units/normalisation for Z1 ≠ Z2.

## Acceptance
`.venv/Scripts/python.exe -m pytest -q tests/test_screen.py && .venv/Scripts/python.exe -m src.isoshift_event.screen dryrun --n-pairs 3 --models mace,orb`
Judged on: tests pass; dryrun finishes on the GPU, prints both tables with finite F, ZPE(D) < ZPE(H) for every ok structure, quarantined rows present rather than missing, a second dryrun invocation reuses results instead of recomputing, and nothing is written under the real `results/` or `isoshift/`. Report wall time per job and the number of model loads.
