Post-freeze addendum; the frozen F01 headline (decision 07) is unchanged.

# P09: temperature-resolved F01 and the mp-985293 crossover (predeclared before any new run)

Decision 08, rank 1, action 3. This file is committed and pushed before any file exists in `results/post_freeze/` and before `decompose.py` is run at any temperature other than the frozen 300 K. The frozen files (`results/F01_cv.json`, `results/decompose_pairs.csv`, `results/decompose_structures.csv` and everything decision 07 froze) stay byte identical; every new output goes to `results/post_freeze/`.

## 1. Post hoc re-scoring of columns stored before the freeze

These numbers are not predictions. They re-score the refined ddF columns that `refine.py` wrote before the freeze (`results/screen_pairs_refined.csv`, `ddF_iso_{0,300,600,2000}K_refined_meV_atom`) on the frozen headline population: 212 O-H model evaluations (MACE, ORB, MatterSim) with rmax ≥ 0.99 Å and |Δ mean O-H| ≥ 5 mÅ, 84 pairs, 28 formulas. Rows come from `rule_cv.load()`. The sign of the stored 300 K refined column agrees with the frozen `decompose_pairs.ddF_total` in 212 of 212 rows. Baseline: constant sign from leave-one-formula-out training folds, recomputed at each temperature. Recomputed for this file with the chair's script; identical to decision 08.

| T | headline right / 212 | LOFO baseline | pair majority right / tie / wrong of 84 | mp-985293 rows | MACE / ORB / MatterSim |
|---|---|---|---|---|---|
| 0 K | 153 | 145 | 60 / 5 / 19 | 0/28 | 44/68, 54/73, 55/71 |
| 300 K (frozen) | 185 | 131 | 74 / 0 / 10 | 8/28 | 52/68, 64/73, 69/71 |
| 600 K | 210 | 114 | 84 / 0 / 0 | 28/28 | 67/68, 73/73, 70/71 |
| 2000 K | 211 | 113 | 84 / 0 / 0 | 28/28 | 67/68, 73/73, 71/71 |

| Subset (abs Δ X-H ≥ 5 mÅ) | 0 K | 300 K | 600 K | 2000 K |
|---|---|---|---|---|
| Weak O-H side (rmax < 0.99 Å) | 2/20 | 2/20 | 13/20 | 19/20 |
| O-H, no threshold (baseline) | 155/232 (165) | 187/232 (151) | 223/232 (123) | 230/232 (47) |
| All clean covalent, no threshold (baseline) | 164/242 (171) | 197/242 (158) | 233/242 (130) | 240/242 (68) |

The 0 K accuracy (153 of 212 against a baseline of 145) is close to the baseline. F01 is a thermal rule, not a zero-point rule.

**Flag analysis.** 42 of the 212 headline rows carry `classical_limit_violation`, including all 28 rows with mp-985293. They score 0/42 at 0 K, 17/42 at 300 K and 42/42 at 600 K. The 170 unflagged rows score 153, 168 and 168. So the whole 300 to 600 K gain sits in the flagged rows. The flag fires when |ddF(2000 K)| > |ddF(600 K)| (`refine.py` line 184). A sign crossover between 0 and 600 K produces that by construction, because 1/T decay needs hbar omega much smaller than kT and the O-H stretch has hbar omega/k of about 5000 K. Over all 1616 refined rows with these columns, 384 are flagged, 309 of them change sign between 0 and 2000 K, and the median |dd2000|/|dd600| is 1.79 flagged against 0.46 unflagged. The flag is mostly a crossover marker, but it can also mark omitted imaginary modes, which is why H3 below is a gate.

**Scope of 600 K.** A 600 K value is a statement about the harmonic isotope term at fixed 0 K geometry, not about phase stability. Gibbsite and many hydrates decompose below 600 K.

## 2. Mechanism under test

Zero-point energy weights a force-constant change by about 1/sqrt(k); the high-temperature Bigeleisen-Mayer limit weights the H force-constant trace, F_D - F_H → (hbar²/24kT)(1/m_D - 1/m_H) Tr K_H plus a mass constant that cancels between phases. Bend and libration (k about 5 eV/Å²) therefore count about sqrt(45/5) ≈ 3 times more relative to the stretch (k about 45 eV/Å²) at 0 K than at high T. F01 at 300 K would then be the room-temperature remnant of the classical trace rule, and mp-985293 the structure whose crossover lies above 300 K.

## 3. Method (fixed now)

1. `decompose.py` gets `--T` (K, default 300) and `--out-dir` (default `results/`, file names unchanged). Default behaviour stays byte identical. At T = 0 the mode weight K_nu is the T → 0 limit E/4 and the direct F is the zero-point energy.
2. **Regression gate.** `decompose.py --T 300 --out-dir results/post_freeze/T300` must reproduce the frozen `ddF_total` of `results/decompose_pairs.csv` within 1e-9 meV/atom in every row it shares with the frozen file, with the same model set. If it does not, the 0 and 600 K runs are not scored and F09 reports the failure.
3. Runs at 0 K and 600 K into `results/post_freeze/T0` and `results/post_freeze/T600`. Scoring uses only the 212 frozen headline rows (pair_id, model) and the frozen geometry columns (x = 1000 dXH_mean_A, rmax) from `rule_cv.load()`. Per H: divide by `H_per_atom`. ddF_str and ddF_perp come from these runs.
4. Compensation C(T) = -ddF_perp(T) / ddF_str(T) per row.
5. F01 sign: sign(ddF) = sign(x), as in `rule_cv` (right = sign(x) == sign(y)).

## 4. Predeclared hypotheses (212 headline rows, three models)

**H1 (zero-point weighting of bend and libration).** On rows with |ddF_str| ≥ 0.1 meV/H at both 0 K and 600 K: C(600 K) < 0.6 × C(0 K) in at least 80% of those rows. Pass if the fraction is ≥ 0.80, fail otherwise. Counts per model are reported, the verdict is pooled.

**H2 (mp-985293 reversal sits in the bend/libration share).** Every one of the 28 headline rows that contain mp-985293 satisfies all four: ddF_str has the F01 sign at 0 K, ddF_str has the F01 sign at 600 K, C(0 K) > 1, C(600 K) < 1. Pass only if 28 of 28; any single row failing any condition fails H2. The failing rows are listed.

**H3 (product rule, numerical gate).** For each structure in the 10 mp-985293 headline pairs (mp-985293 and its 10 partners), in every model in which that pair is a headline row, at every q point of the `decompose.py` mesh (shifted, Gamma free): |Σ over all modes of ln(ω_D²/ω_H²) - 3 n_H ln(m_H/m_D)| / n_H ≤ 1e-3, with n_H the H count of the unit cell and ω² taken in absolute value (the congruence M^-1/2 Φ M^-1/2 keeps the number of negative eigenvalues the same for H and D). Pass if every structure, model and q passes. If a structure fails, every row containing it is reported as numerically compromised and the temperature claim is restricted to rows without it.

**H4 (high-temperature trace limit).** Δ Tr K_H = Tr_b/N_b - Tr_a/N_a, with Tr_p the sum over the H atoms of the unit cell of the trace of the on-site 3×3 force-constant block Φ_ii (eV/Å²), read from the cached real-space force constants (`.cache/isoshift/*/phonopy_params.yaml`, the same cache `decompose.py` uses), N the atoms per cell, b minus a as in `decompose_pairs.csv`. Because 1/m_D - 1/m_H < 0, the high-T limit predicts sign(ddF(2000 K)) = -sign(Δ Tr K_H): D prefers the phase with the larger H trace. Decision 08's wording "sign of Δ Tr K_H equals the sign of ddF(2000 K)" is scored as agreement with this prediction. ddF(2000 K) is the stored pre-freeze column `ddF_iso_2000K_refined_meV_atom`. Pass if agreement holds in ≥ 95% of the 212 headline rows (≥ 202 of 212).

Each hypothesis is scored once, as written here. No threshold, row set or definition is changed after the runs. Failures are reported in F09 with the same prominence as passes.

## 5. Outputs

`results/post_freeze/F09_temperature.json` (regression line, H1 to H4 with pass or fail and counts, per-row tables for H2) and `docs/findings/F09-temperature-crossover.md`.
