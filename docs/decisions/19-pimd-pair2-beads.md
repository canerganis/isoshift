# 19. P12 pair 2 (FeOOH) at P = 32 for both members, committed A4b bound kept as primary, discounted pilot term at P = 32

Council: Opus (chair), Astra, Argon. Two rounds, all three answered both. Chair re-checks on 24 Oct with the project venv: the committed A4b bound at P = 16, 24 and 32 plus the P128 to infinity tail was recomputed from the stored `raw_energies_eV` in `results/pimd/a4b_scan_residual.json` with no MACE calls (scratchpad script C:/Users/can02/AppData/Local/Temp/claude/C--Users-can02-Projects-osi-hackathon-2026/1be949f7-8f5b-49a2-96bd-e9f5aaa4aea8/scratchpad/chair19_a4b.py, 19 s CPU; the P16 values reproduce the stored 0.122, 0.146, 0.386, 0.290, 0.197 exactly). Run hours, E_pair and the branch arithmetic were recomputed inline from the chunk-4 smoke-test rates in `docs/specs/pimd-p12-measurements.md`. Post-submission P12 work on branch post-hackathon; the frozen hackathon numbers are unchanged.

Status when this was written (03:07, 24 Oct): row 1 (mp-625152, P = 16) started at 02:49 and is in pre-equilibration; `results/pimd/mp-625152_P16.json` has status partial and `"points": []`, so no K_H at any GL point exists or has been read. The pilot difference d needs rows 1 and 2, so every rule below that uses d is blind. The only change here that touches a P = 16 s_P is the infinity tail, which raises it by 0.001 to 0.005 meV/H.

## Decision

1. **Pair 2 at P = 32 for both members.** Rows 6 and 7 become JVASP-54682 P32 (7.87 h) and JVASP-92228 P32 (8.31 h). Pairs 1 and 3 stay at P = 16 unless the pilot fires branch F. Mixed P inside a pair is forbidden. Pair 2 is never run at P = 16: there E_pair2 = 1.21 meV/H before s_hess, so it is inconclusive before it starts.
2. **Row 8 is repurposed, not deleted.** The old "second P32 check" is now a P = 16 diagnostic run on JVASP-54682 (3.94 h). It is run after row 7 only if it fits the cap. It never enters ddF_corr. It gives the only 3D bead comparison on FeOOH, d_Fe = Delta_anh(32) - Delta_anh(16) on JVASP-54682, and can only raise pair 2's s_P (rule 4).
3. **A4b bound: the committed definition stays primary, with the infinity tail added.** For structure i, H site h (multiplicity m_h, N_H hydrogens), scan direction q in {stretch, transfer}, mass model mu in {reduced, bare}, fit f in {degree 10, degree 8, not-a-knot spline}:

   r_f(P) = Delta_f(P) - Delta_f(128),  t_f = Delta_f(128) - Delta_f(inf)

   A_i(P) = sum_h (m_h / N_H) * max_(q, mu) [ max_f |r_f(P)| + (max_f r_f(P) - min_f r_f(P)) + max_f |t_f| ]

   Directions and mass models are alternatives (maximised), not summed. The grid numerics converge to 1e-4 meV, so no separate numerical term is added. A polynomial plateau bound b_poly = |r_10| + max(0.01, |r_11 - r_10|, |r_12 - r_10|) per scan is reported as sensitivity only and never sets eligibility.
4. **s_P per structure,** d = Delta_anh(32) - Delta_anh(16) on mp-625152 from rows 1 and 2, sigma_d its error:
   * P = 16 (pairs 1 and 3, main branch, unchanged): s_P,i = max(0.05, A_i(16), max(0, |d| - sigma_d)).
   * P = 32, not branch F (pair 2): s_P,i = max(0.05, A_i(32), max(0, |d| - sigma_d) / 2, max(0, |d_Fe| - sigma_dFe) / 2), the last term only if row 8 ran.
   * P = 24 fallback (pair 2 only, rule 6): s_P,i = max(0.05, A_i(24), max(0, |d| - sigma_d)).
   * Branch F (all of pairs 1 to 3 at P = 32): unchanged from decision 18 A11, s_P,i = max(0.05, A_i(32), |d| / 2).
5. **The 0.19 meV/H line of decision 18 was a planning heuristic, not a gate.** mp-625152 at A = 0.199 does not move pair 3 to P = 32; pair 3's planned E is 0.857. The module flag `H1_above_0p19_meV_H` is informational.
6. **Run order and cap (48 measured GPU h, unchanged).** Rows 1 to 7, then row 8 (diagnostic), then pair 4 only if both members fit. Drop order if slower: pair 5 (already out, A13), pair 4, row 8, pair 2 from P32 to P24, pair 2 omitted as a whole pair. The pair 2 P choice is made once, before row 6 starts, from the measured rates of rows 1 to 5 and the tau_int rule only, never from any Delta_anh except through branch F. Trajectories are never shortened and controls are never waived to fit the cap. A cap extension is Can's decision, not the conductor's.
7. **Scoring.** H1 and H2 rules and the denominator of 3 are unchanged. Each structure is referenced to its own same-P harmonic value (A2), so pair 2 at P = 32 tests the same continuum quantity with a smaller s_P. On the main branch pair 3 uses row 1 (mp-625152 P16) and row 4; row 2 only feeds d. The scorer reads P from every run JSON, asserts equal P inside each pair, applies the matching s_P rule and reports P per pair. Decision 18's clause "taking the larger d of the two P32 checks" is replaced by rule 4: the pilot d applies to everyone, d_Fe only to pair 2.

### Numbers this rests on (meV/H at 300 K, chair recompute)

Committed A4b bound with tail, A_i(P):

| structure | pair | P16 | P24 | P32 |
|---|---|---|---|---|
| mp-23807 | 1, 3 | 0.124 | 0.052 | 0.036 |
| mp-625054 | 1 | 0.150 | 0.105 | 0.073 |
| JVASP-54682 | 2 (b) | 0.390 | 0.158 | 0.085 |
| JVASP-92228 | 2 (a) | 0.291 | 0.099 | 0.046 |
| mp-625152 | 3 | 0.199 | 0.057 | 0.023 |

E_pair = 1.96 sqrt(2) 0.160 + 0.09 + s_P,a + s_P,b with sigma = 0.160 per structure (plan), s_dt + s_f32 + s_quad = 0.06 + 0.02 + 0.01, before s_hess and before any pilot term:

| case | E_pair |
|---|---|
| pair 1, P16 | 0.808 (+ s_hess of mp-625054) |
| pair 3, P16 | 0.857 |
| pair 2, P16 | 1.215 (inconclusive at any s_hess) |
| pair 2, P24 | 0.791 |
| pair 2, P32 | 0.669 |

Worst non-F case for pair 2 at P32: the Hessian check gate (`HESSIAN_TOL_MEV` = 0.1 in pimd.py) caps s_hess at 0.1 per FeOOH structure, and the largest non-F pilot is |d| = 0.445. With the discounted term (0.445 - 0.227)/2 = 0.109 per structure, E = 0.4435 + 0.09 + 0.218 + 0.2 = 0.95, under the bar. With the literal |d|/2 = 0.2225 it would be 1.18, so pilot noise alone could make pair 2 inconclusive.

Run table, 13000 steps per run (17000 under branch T), chunk 4, measured s per ring step scaled linearly in P:

| row | run | P | GPU h | cumulative |
|---|---|---|---|---|
| 1 | mp-625152 | 16 | 4.44 | 4.44 |
| 2 | mp-625152 pilot | 32 | 8.88 | 13.32 |
| 3 | C2 float64 re-evaluation | 16 | 0.80 | 14.12 |
| 4 | mp-23807 | 16 | 4.55 | 18.68 |
| 5 | mp-625054 | 16 | 4.08 | 22.76 |
| 6 | JVASP-54682 | 32 | 7.87 | 30.63 |
| 7 | JVASP-92228 | 32 | 8.31 | 38.93 |
| 8 | JVASP-54682 diagnostic (not scored, feeds d_Fe) | 16 | 3.94 | 42.87 |
| 9, 10 | pair 4 (mp-626497, mp-985293) | 16 | 10.87 | 53.74, not run |
| 11, 12 | pair 5 | | | not run, A13 |

Add the actual pre-row-1 ledger (A4b calculator time 0.028 h from the JSON, plus the row 0a smoke test) to every cumulative figure. With about 0.1 h overhead the reserve after row 8 is about 5.0 h. Row 8 comes before pair 4 (decision 18 A11 order). Pair 4 runs only if both members fit after row 8, that is rows 1 to 8 at most 37.13 h, which needs measured rates about 13 % faster than the smoke test; at smoke-test rates it is not run.

Thresholds on the measured rate factor f (actual over smoke-test rate) and branch T:
* P32 for pair 2 fits rows 1 to 7 if f <= 1.23 and no branch T.
* Row 8 fits if f <= 1.12 and no branch T.
* P24 (12.13 h nominal) fits if f <= 1.37 off branch T, or f <= 1.05 under branch T (45.38 h at f = 1).
* Branch T with P32 costs 50.67 h, so branch T moves pair 2 to P24 unless the measured rate is faster than the smoke test.
* Branch F: mp-625152 P16 and P32, C2, then mp-23807, mp-625054, JVASP-54682 and JVASP-92228 at P32, 47.56 h. No P24 fallback inside branch F. If the cap would be exceeded, pair 2 is omitted whole and reported not run. Under branch F the literal |d|/2 with |d| > 0.445 makes pair 2 very likely inconclusive anyway (E >= 0.98 before s_hess).

Registered 1D expectation for pair 2 before any FeOOH PIMD: Delta_anh(b) - Delta_anh(a) = +3.51 (stretch) to +3.81 (transfer) meV/H at P128 from the stored scans, against decision 17's +3.62. ddF_corr would then be about +9.5, the same sign as the harmonic +6.00, so H1 for pair 2 is not at risk on the 1D model. H2 for pair 2 (half threshold 3.000) is likely unresolved or exceeded. Expected d_Fe on the 1D model: about +0.27, below sigma_d, so the row 8 term should be near zero unless the 3D residual is much larger than the 1D one.

## Why

* **P32 for both members, not P16 and not mixed.** At P16 pair 2 has E = 1.215 before s_hess under the committed bound and still about 1.10 with degree-10 magnitudes alone. The bound definition cannot rescue it: degree 8, not the spline, sets both FeOOH envelopes (Astra; the spline residual lies between degree 10 and degree 8 on both transfer scans). Mixed P (JVASP-54682 at P32, JVASP-92228 at P16) gives 0.85 to 0.90 before s_hess, on the bar once s_hess is added. Both members at P32 cost 16.18 h against 16.6 h for old rows 6 to 8, so this is cost-neutral.
* **Committed bound kept primary (Astra, Opus round 2, over Argon).** No planned verdict changes with the bound rule: pair 1 is 0.808 vs 0.64, pair 3 0.857 vs 0.71, pair 2 at P32 0.669 vs 0.66. The rule matters only if the measured sigma is about 33 % above plan: pair 3 crosses 1 at sigma 0.213 under the committed rule and at 0.265 under the plateau rule. Lowering mp-625152's s_P from 0.197 to 0.11 while row 1 samples it would be a change made after sampling started, with no planned benefit. A clean Morse does not calibrate a polynomial on the FeOOH shoulder. Argon's |r_10 - r_8| term measures degree 8 underfitting (rms 1.5 to 3 times degree 10), so it is not a fit-uncertainty estimate either. The infinity tail (Astra) makes the bound refer to the continuum target rather than to P128 and costs at most 0.005.
* **Discounted pilot term at P32 (Opus, Argon, over Astra).** The committed P16 rule already subtracts sigma_d. Without the subtraction at P32, the same pilot result would penalise the better-converged run more: |d|/2 > |d| - sigma_d for every non-F |d| < 2 sigma_d = 0.454. On r(P) proportional to 1/P^2, r(32) = |d|/3, so /2 is already conservative by 1.5 times. On the 1D scans, |r(32)|/|r(16)| is 0.20 to 0.13, which is more conservative still. Astra's concern that subtracting sigma_d weakens a coarse pilot is real, but it applies equally at P16 and was accepted there in decision 18. The structure-specific protection is A_i(32), not the AlOOH pilot. Branch F keeps the literal |d|/2 as committed, since there |d| is already resolved.
* **Row 8 as a P16 diagnostic (chair addition).** All three members named the loss of a 3D P16 vs P32 comparison on FeOOH as the main residual risk: the 1D scans miss stretch-bend coupling and libration on the 2.551 A H bond. Pair 2 at P32 tolerates a 3D bead residual about 2.6 times the 1D value. One P16 run on JVASP-54682 (3.94 h) measures d_Fe directly. It fits in the reserve that pair 4 cannot use anyway (pair 4 needs 10.87 h, 49.8 h without row 8), and decision 18 A11 already ranked the second check above pair 4. It enters only as a one-sided term in pair 2's s_P, so it can make pair 2 inconclusive but never rescue it.
* **P24 fallback, then whole-pair omission (all three in round 2).** P16 spends 8 h on a pair that is inconclusive before it runs. P24 keeps E at 0.79 and fits branch T at 45.38 h. Its pilot term is the undivided P16 form, because nothing has measured P24.
* **No consequence for H1 across pairs.** Pair 2 shares no structure with pairs 1 and 3. Same-P harmonic subtraction makes Delta_anh an estimate of the same continuum correction at any P, up to s_P. Different P across pairs gives different error budgets, not different hypotheses; the paper must not claim uniform bead convergence.

## Where the members converged

* Both FeOOH members at P = 32, the same P inside every pair, pairs 1 and 3 at P = 16 on the main branch (all three, round 1).
* Pair 2 at P = 16 is inconclusive at planning precision (all three; Astra notes that only about 3.6 times the sampling would make it passable).
* Rows 1 to 7 at 38.93 h; pair 5 out by A13; pair 4 dropped first (all three).
* P24 for both FeOOH members as the timing fallback, decided before row 6 on timing and tau_int only, then whole-pair omission; never P16 for pair 2, never shortened trajectories (all three, round 2).
* Pair 3 is scored from row 1, not row 2, on the main branch; the scorer asserts equal P per pair (all three).
* Infinity tail added to the bound (Astra proposed, Opus and Argon accepted).
* C1 and C4 must be rerun at every new P, and s_hess for the interpolated structures is still unmeasured (all three).

## Remaining disagreement

* **Primary bound.** Argon: degree-(8, 10) polynomial bound with the spline as a 0.10 meV gate, which removes the spline inflation on mp-625152 and mp-625054. Astra and Opus: keep the committed envelope. Adopted: committed envelope, plateau as sensitivity (Why).
* **Pilot term at P32.** Astra: literal |d|/2, extending branch F. Opus and Argon: max(0, |d| - sigma_d)/2. Adopted: discounted outside branch F, literal inside it.
* **P24 pilot term.** Opus: |d| - sigma_d; Argon: 0.6 (|d| - sigma_d); Astra: |d|. Adopted: max(0, |d| - sigma_d), the P16 form, as the conservative choice that stays consistent with A4.
* **Row 8.** All three members deleted it. The chair keeps it as an unscored P16 diagnostic in the reserve. This is the one point no member proposed.
* **Overhead.** Astra used a provisional 0.40 h; Argon measured about 0.10 h. Adopted: the actual ledger.

## Ordered action list for the conductor

1. **Commit the amendment before row 1 writes its first GL point.** Owner: conductor. 30 min. Add A15 to docs/predictions/P12_pimd.md section 2a with Decision items 1 to 7, the s_P rules as formulas, the run table and the drop order, citing this decision. Update decision 18's row 8 line by reference only, not by editing it. State the timing exactly: "after row 1 began pre-equilibration at 02:49, before any GL point K_H was written or read". Done-check: at commit time `results/pimd/mp-625152_P16.json` still has `"points": []` (record the check output in the commit message), and `git log -1 --stat` shows only P12_pimd.md and this file.
2. **Extend oh_scan_residual.py and rerun on CPU.** Owner: conductor via build. 1 h code, under 1 min run, no MACE calls. Beads (16, 24, 32, 128); per scan and mass model store r_f(P) for f in degree 10, degree 8, spline and the tail t_f; `a4b_bound_meV_H` per P under rule 3; `a4b_plateau_sensitivity_meV_H` from degrees 10, 11 and 12, flagged sensitivity only; the 0.19 flag relabelled as informational. Reuse `raw_energies_eV` through the scan fingerprint. Done-check: the JSON reproduces A_i(P) in the table above to 0.001 meV/H, its P16 bound without the tail equals the committed 0.122, 0.146, 0.386, 0.290, 0.197, `points_evaluated` unchanged, tests pass with `.venv/Scripts/python.exe -m pytest -q tests/test_oh_scan_residual.py`. Commit together with or right after step 1.
3. **CPU controls at the new bead counts, before row 2.** Owner: conductor. 30 min setup, CPU in background. C1 at P = 32 and P = 24 with the harmonic backend, BAOAB 0.25 fs, 150000 steps per point, on mp-625152 and mp-23807 (commensurate, CLI works), and on the FeOOH force constants in their own FC supercells (4x2x1, 4x2x2) through controls_cpu.py, because pimd.py refuses the harmonic backend when the PIMD cell differs from the FC cell. C4 (4 vs 8 GL points, exact finite-P harmonic K) at P = 24 and 32 for all H1 structures. Done-check: `results/pimd/controls_cpu.json` has C1 and C4 entries at P = 24 and 32 with pass true; s_dt for each P recorded as max(0.06, |diff|). If C1 at P = 32 fails, row 2 does not start.
4. **Run rows 1 to 5 as planned.** Owner: conductor. 22.8 GPU h. Apply the A4 pilot rule and the A6 tau_int rule after rows 1 and 2; record measured s per ring step at P = 32 from row 2. Done-check: `results/pimd/pilot_decision.json` (d, sigma_d, branch, tau_int, s_f32, measured P32 rate) committed before row 4 starts.
5. **Fix pair 2's P before row 6.** Owner: conductor. 10 min. Project the cumulative time through row 7 from the measured rates of rows 1 to 5, the actual ledger and branch T. P32 if it is at most 48 h, else P24 if that fits and the P24 controls passed, else pair 2 not run. Done-check: `results/pimd/pair2_beads.json` with the projection, the choice and the rule text, committed before row 6 starts and containing no Delta_anh of any structure other than what pilot_decision.json already holds.
6. **Rows 6 and 7 at the chosen P.** Owner: conductor. 16.2 GPU h at P32. The auto Hessian check runs at the start of each FeOOH run and of mp-625054. Done-check: run JSONs with P equal to the step 5 choice, `hessian_check.passed` true, status complete, stationarity flag.
7. **Row 8 diagnostic if it fits.** Owner: conductor. 3.94 GPU h. JVASP-54682 at P = 16, same seed policy and step count. Done-check: run JSON tagged `diagnostic: true`, and d_Fe with sigma_dFe written to `results/pimd/pilot_decision.json` as a separate field. If the projection after row 7 leaves less than its measured cost, record "row 8 not run (cap)" instead.
8. **Pair 4 only if both members fit** in what remains after row 8. Owner: conductor. Done-check: run JSONs, or "not run (cap)" recorded.
9. **Scorer.** Owner: conductor via build. 2 h. p12_score.py reads P per run, asserts equal P inside each pair, applies rule 4 per structure and branch, excludes diagnostic runs from ddF_corr, reports P per pair, primary E_pair, plateau-sensitivity E_pair, and labels a pair that is inconclusive only through the fit allowance. Done-check: `results/pimd/p12_scores.json` with these fields and a unit test that a pair with mixed P raises.

## What would change this

* Measured sigma at P = 32 (row 2) more than about 1.5 times the P16 value: pair 2 at P32 approaches the bar; reconvene before row 6 rather than lengthen runs.
* C1 at P = 32 fails or gives s_dt above about 0.15: P32 is not usable at 0.25 fs; pair 2 goes to P24 if its C1 passes, else not run.
* A Hessian check fails on either FeOOH structure: pair 2 is inconclusive by gate, whatever its P.
* Branch F: pairs 1 to 3 all at P32 with the literal |d|/2; row 8 and pair 4 dropped.
* Branch T or f above 1.23: pair 2 at P24 (rule 6).
* d_Fe resolved above about 0.6 meV/H: the 1D scans understate the FeOOH bead residual by more than 2 times; pair 2 is very likely inconclusive, and that is reported as a limit of the 1D bound for all pairs.
* A validated calibration of the polynomial estimator on noisy non-Morse scans (not available now) would justify making the plateau bound primary in a later programme, not in P12.
