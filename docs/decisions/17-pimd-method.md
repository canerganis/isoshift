# Decision 17: P12 PIMD method (amendments before data)

Council: Opus (rounds 1 and 2), Astra (round 1 only; round 2 returned nothing), Gemini 4 Argon (round 2 only; round 1 failed on a headless permission denial). Chair: Opus. Date 24 Oct 2026, branch `post-hackathon`, post-submission work. No file exists under `results/pimd/`, so everything below is registered before any MACE PIMD data. The frozen F01 headline (decision 07) is not touched.

## Decision

Run P12 as primitive PIMD with MACE medium-mpa-0 in **float32** on **all P = 16 beads**, score the **same-P, same-cell harmonic subtraction** Delta_anh(P) = dF_PIMD(P) - dF_harm,samecell(P), integrate the mass TI on **2 Gauss-Legendre nodes** with the harmonic reference integrated on the same nodes, and build the harmonic reference from a **finite-difference Hessian of the PIMD cell itself**. Ring-polymer contraction is rejected in every form proposed (P' = 4 and P' = 8). Run order is pair 3, then the bead and size checks on mp-23807, then pair 1, then pair 2, then pair 4. Pair 5 is not run: its reference structure is not a minimum. H2 becomes co-primary with H1. Section 1 of P12 gets two corrections (pair orientation labels, cache matching). Section 2 gets the amendments A1 to A13 below, each with its reason. The council's 1D local-mode numbers are registered as the quantitative prediction.

## Why

Numbers re-checked by the chair in this session (scripts in the session scratchpad, `bench_dtype.py`, `morseP.py`, inline checks):

1. **The declared plan cannot run, and float64 is the reason.** Steady-state MACE medium-mpa-0 on the RTX 4060, single 96-atom bead: float64 475 ms (4.95 ms per atom-bead), float32 93 ms (0.97 ms per atom-bead). That is 5.1x, not the 1.7x quoted in round 1. The cached force constants and every screen relaxation used float32 (`isoshift/calculators.py` line 52), so float64 PIMD is not more consistent with the reference; it is less. At float64 the declared design (P = 32, 4 nodes, about 100 atoms, 9 structures) is about 680 GPU-h.
2. **Contraction biases toward the harmonic answer.** For a free ring of P = 64 at 300 K, the Fourier modes kept by contraction carry this fraction of the internal bead-spread variance: P' = 4: 0.32 / 0.37 / 0.41; P' = 8: 0.57 / 0.62 / 0.66; P' = 16: 0.77 / 0.80 / 0.83 (stretches at 3600 / 3000 / 2500 cm^-1). A quartic-type first-order correction scales with the square of that fraction, so P' = 8 keeps roughly 33 to 44% of the stretch anharmonic correction, consistent with Opus's 25 to 40%. The difference potential MACE minus harmonic contains exactly the intramolecular O-H anharmonicity that contraction is not meant for. Any shortfall pushes Delta_anh toward zero, which makes H1 and H2 pass for the wrong reason. Argon's P' = 8 does not survive this.
3. **Primitive P = 16 with same-P subtraction is converged in 1D.** Exact transfer-matrix path integral, O-H Morse, 300 K. Delta_anh(P) in meV for the three parameter sets (3600 cm^-1, D = 4.6 eV; 3000, 2.0; 2500, 1.2):

   | P | 4 | 8 | 16 | 32 | 64 | inf |
   |---|---|---|---|---|---|---|
   | 3600 | 0.171 | 0.735 | 1.222 | 1.294 | 1.282 | 1.272 |
   | 3000 | 0.460 | 1.459 | 2.012 | 2.059 | 2.042 | 2.031 |
   | 2500 | 0.821 | 1.946 | 2.359 | 2.372 | 2.356 | 2.347 |

   The residual at P = 16 is at most 0.05 meV. The raw harmonic bead error it cancels is large: for a 3600 cm^-1 O-H oscillator, F_D - F_H is off by +5.70, +1.60, +0.41, +0.10 meV at P = 16, 32, 64, 128 (4000 cm^-1: +7.58, +2.17, +0.56, +0.14). So the declared rule "P vs 2P within 0.3 meV on F_D - F_H" would force P = 64 to 128 for no gain, and at small P it can pass while the value is 40% low (the 3000 cm^-1 set changes 1.0 meV from P = 4 to 8). The convergence check is therefore moved to Delta_anh at P >= 16.
4. **2 GL nodes are enough when the harmonic reference uses the same rule.** In the 1D Morse tests the anharmonic-part quadrature error is at most 6e-4 meV with 1 node and below 1e-4 meV with 2. GL2 nodes: g = 0.7692 and 0.9382 (m = 1.7033 and 1.1451 u), g_D = 0.70737851. At a fixed total step budget, Var(dF) N_tot / sigma_K^2 = n sum c_j^2 is 0.484, 0.508, 0.525 for n = 2, 3, 4, so fewer nodes are slightly better statistically and need fewer equilibrations. Argon's 0.528 / 0.526 / 0.525 is not right for n = 2 and 3. Astra's GL4 vs GL6 check has nothing to detect at this precision.
5. **Run length.** The harmonic-backend PIMD on the real mp-23807 force constants (Opus, round 1) gave a per-H-mean centroid-virial std of 6.3 meV at n_H = 24 with tau_int about 2 fs. Two picoseconds per node gives N_eff about 500, SEM(K) about 0.28 meV and SEM(dF) about 0.49 x 0.28 = 0.14 meV/H for the fast part. The slow, centroid-modulated anharmonic part is unmeasured; 2 ps production with a precision-gated maximum of 6 ps covers a 1 to 2 meV component at tau about 100 fs. Astra's 20 to 30 ps per node assumed the whole variance decorrelates on 100 fs, which the measurement contradicts, and costs hundreds of GPU-h here.
6. **Pair 5 has no valid reference.** `results/raw/screen/mace/mp-23940.json`: relax.converged = false, 500 steps, fmax 0.0309 eV/A, plus a commensurate imaginary mode at -0.91 THz at q = (0,0,1/2). A harmonic expansion about a non-stationary point has a linear term that the harmonic reference omits, so Delta_anh would contain a relaxation artifact, not anharmonicity. mp-626000 also stopped at 500 steps (fmax 2.3e-4 eV/A). The other seven structures converged with fmax below 1e-4 eV/A.
7. **Orientation.** `results/screen_pairs_refined.csv` (model mace) has struct_a = mp-625054, JVASP-92228, mp-625152, mp-985293, mp-626000 for pairs 1 to 5, the second id of each pair_id. The P12 numbers (Delta O-H, ddF) are b - a with b = the first id, but the column header says "pair (a__b)". The numbers are right, the label is reversed. An assembler that splits pair_id as a__b would flip Delta_anh(b) - Delta_anh(a).
8. **Cost of the adopted plan.** Float32, 0.97 ms per atom-bead (single-bead calls; batched throughput is measured in the pilot), dt 0.5 fs, P = 16, two nodes x (0.5 ps equilibration + 2 ps production) = 10,000 steps: 96 atoms 4.1 h, 112 atoms 4.8 h, 64 atoms 2.8 h per structure. At dt 0.25 fs everything doubles.

## Where the members converged

* The mass TI identity dF/dg = 2 <K_H>/g is exact for full simultaneous H to D substitution; the centroid-virial estimator uses physical forces only; divide by the supercell H count once. "Unbiased" holds only for the sampled finite-P, finite-dt ensemble (Astra's wording is adopted).
* Same-P harmonic subtraction using the analytic discretized harmonic value (`dF_P_eV`) is the right estimator (all three).
* Same-cell subtraction is sound as stated by Astra: it removes the harmonic part of the finite-size error, not the anharmonic part. Drop only the three Gamma translations by eigenvector, never take absolute values of imaginary modes, add F_COM = -(3/2) kT ln M_tot for the unconstrained PIMD (about 0.02 meV/H). Fixed-cell Helmholtz only; the isotope-volume term and the AlOOH pressure prediction are outside P12.
* Same-cell vs full-mesh harmonic F_D - F_H differ by at most 0.014 meV/H on the 7 checkable structures.
* Fixes before data: pair orientation (S1), cache matching (S2), float32 consistency with the force constants (Opus, Argon), commensurability problem for JVASP-54682 and JVASP-92228 (all).
* CPU harmonic-backend PIMD on the real Hessians must reproduce the analytic finite-P value, including a P = 1 classical check; TD-FEP between neighbouring masses is dropped (Astra's overlap variance about 189 for N_H = 32, P = 64).
* Error accounting: stat and systematic terms reported separately and combined; four outcome categories; missing pairs stay in the denominator; pairs 1 and 3 share mp-23807 and are correlated. Order pair 3 then pair 1 (Astra, adopted by Opus). Extension of runs decided by precision, never by sign.
* H1 has low power: in pairs 1 to 3 stretch anharmonicity softens the longer O-H more, so the expected correction reinforces the harmonic sign (Opus, Argon).

## Remaining disagreement

* **Contraction.** Argon wants RPC with P = 64 and P' = 8. Rejected on the variance-fraction numbers above (P' = 8 keeps 57 to 66% of the bead spread). Opus withdrew P' = 4 for the same reason.
* **Quadrature.** Argon and Astra want 3 or 4 nodes as a smoothness check. Rejected for PIMD; the cost is extra equilibrations and shorter runs per node. The smoothness question is checked instead on the 3D local-mode model (action 6), which gives Delta_anh(g) at many g for the real MACE potentials at no PIMD cost.
* **Run length and bead tests.** Astra's 20 to 30 ps per node and P = 32 / 64 / 128 production tests are replaced by 2 to 6 ps with a block-plateau SEM rule and one P = 16 vs P = 32 check. Astra did not answer round 2, so this is unconfirmed by her.
* **Cell choice for pair 2.** Argon wants the FC supercells 4x2x1 and 4x2x2 (128 atoms) to make the cached q-points exact. Not needed once the reference is fd_hessian of the PIMD cell; the default 96-atom cells are kept (cheaper, same 8 A rule as the others). 4x2x1 / 4x2x2 remain an allowed swap if the conductor prefers exactness against the cache.
* **3D local DVR.** Argon calls it necessary, Opus optional. Adopted as optional with a hard deadline: it counts as a registered prediction only if committed before the first MACE PIMD step.
* **H2 as co-primary.** Opus and Argon for; Astra not asked in round 2. Adopted because it makes failure of the harmonic screen more likely to be reported, not less.

## Section 1 corrections (labels and plumbing, not method)

* **S1.** Replace the "pair (a__b)" column with explicit struct_b / struct_a: pair 1 b = mp-23807, a = mp-625054; pair 2 b = JVASP-54682, a = JVASP-92228; pair 3 b = mp-23807, a = mp-625152; pair 4 b = mp-626497, a = mp-985293; pair 5 b = mp-23940, a = mp-626000. ddF = [F_D - F_H]_b - [F_D - F_H]_a. Values unchanged.
* **S2.** Cache matching must be unique for mp-625054 and mp-626497 (two caches share energy, atom count and supercell). Match on `fc_meta.volume_A3` within 1e-5 A^3 in addition to energy and atom count. In the current working tree `find_cache` already returns a single cache for both; the fix is to lock that with a test.

## Section 2 amendments (made before data, with reasons)

* **A1. MACE float32** for forces (was float64). Ring-polymer coordinates, momenta, estimators and accumulators stay float64. Reason: the force constants and relaxations are float32, so the minimum and the Hessian are float32 objects; 5.1x faster measured. Gate: centroid-virial K_H from float32 and float64 forces on 20 harmonic-backend bead configurations of mp-23807 agree within 0.05 meV/H.
* **A2. Primitive PIMD, P = 16, MACE on every bead.** Reason: 1D residual at most 0.05 meV; contraction rejected (Why 2).
* **A3. Primary estimator Delta_anh(P) = dF_PIMD(P) - dF_harm,samecell(P)**, the second term analytic at the same P, same cell, same GL nodes. ddF_corr = ddF_harm,full mesh + Delta_anh(b) - Delta_anh(a). The raw dF_PIMD(P) - dF_harm,samecell(inf) is reported as a diagnostic only. Reason: cancels the 5.7 meV harmonic bead error exactly.
* **A4. Bead check replaces "P vs 2P".** On mp-23807 in a 2x2x2 cell (64 atoms, 16 H), one GL node at g = 0.8537 (the GL1 midpoint), P = 16 and P = 32. The difference enters sys as max(|diff|, 2 sigma_diff). If |diff| > 0.3 meV/H beyond 2 sigma_diff, production switches to P = 32 for the remaining structures and mp-23807 is rerun at P = 32. Reason: the old rule is unsafe at small P and needlessly strict at large P.
* **A5. GL2 nodes** g = 0.7692, 0.9382 (m = 1.7033, 1.1451 u), harmonic reference on the same nodes. Reason: Why 4.
* **A6. Harmonic reference from `fd_hessian` of the PIMD cell** (float32 MACE, delta 0.01 A, ASR enforced, Gamma translations by eigenvector), with `harmonic_samecell` from the cache kept as a diagnostic that must agree within 0.02 meV/H where the q-points are exact. Reason: JVASP-54682 (PIMD 3x2x1 vs FC 4x2x1) and JVASP-92228 (3x2x2 vs 4x2x2) are not commensurate; dtype consistency; cache ambiguity. Gate: max |F| at x0 below 1e-3 eV/A in float32, and no non-translational eigenvalue <= 0; a structure failing either is "invalid reference".
* **A7. Cells.** The 8 A / 128-atom rule stays as written. Declared actual cells: mp-23807 3x2x2 (96), mp-625152 3x2x1 (96), mp-625054 3x2x2 (96), JVASP-54682 3x2x1 (96), JVASP-92228 3x2x2 (96), mp-626497 2x2x2 (112), mp-985293 2x2x1 (112, minimum width 7.32 A because the cap wins). One size check: mp-23807 2x2x2 (64 atoms, from the A4 P = 16 run) vs 3x2x2; the difference (corrected for the 1-node vs 2-node quadrature, bounded by the DVR check) enters sys for every structure. Reason: actual widths stated instead of an implied guarantee; anharmonic finite size is otherwise unmeasured.
* **A8. Integrator.** BAOAB splitting stated explicitly (the CLI default; the class default is OBABO), normal-mode PILE-L, tau0 100 fs, gamma_k = 2 omega_k. dt 0.5 fs only if the harmonic-backend PIMD on each PIMD-cell Hessian shows |dF(0.5) - dF(0.25)| < 0.1 meV/H and `check_step_stable` passes; otherwise 0.25 fs. Reason: halves cost; the gate uses no MACE-sampled data.
* **A9. Run length.** First node 1 ps equilibration, second node 0.5 ps (started from the first node's last configuration). Production 2 ps per node. If the block-plateau SEM of Delta_anh exceeds 0.3 meV/H, extend in 2 ps steps up to 6 ps. The extension decision reads only the SEM column and is logged with the SEM value. Reason: Why 5.
* **A10. Error and inconclusive rule.** sigma_tot = sqrt(stat^2 + sys^2), sys = bead term (A4) + size term (A7) + dt term (A8) added in quadrature, shared across structures. Target stat SEM 0.2 meV/H per structure, minimum 0.3. A pair with sigma_tot(ddF_corr) > 1 meV/H is inconclusive. Pairs 1 and 3 carry the mp-23807 covariance. Reason: the old rule ignored systematic error.
* **A11. Scoring.** Each pair is supported, challenged, unresolved, invalid reference or not run. H1 sign resolved means |ddF_corr| > 2 sigma_tot. H2 (now co-primary with H1): supported when the 95% upper bound of |Delta_anh(b) - Delta_anh(a)| is below 0.5 |ddF_harm| (half-signal 2.515, 3.000, 1.535 meV/H for pairs 1, 2, 3); challenged when the 95% lower bound is above it; else unresolved. Overall H1 or H2 support needs all three of pairs 1 to 3 supported; a not-run pair blocks overall support. H3 separates a negative correction from a negative corrected ddF. Reason: H1 has little power (Why, converged points); the old text left "beyond the error" undefined.
* **A12. Pair 5 invalid reference, not run.** Reason: Why 6. H4 is reported as "not run: reference structure not converged (fmax 0.031 eV/A, commensurate imaginary mode)". A re-relaxed pair 5 would change the frozen harmonic reference and is out of scope for P12.
* **A13. Acceptance and monitors.** The existing section 2 acceptance tests stay. Added: harmonic-backend PIMD reproducing the analytic same-cell dF(P = 16) within 2 sigma on each PIMD cell; P = 1 classical limit dF = -26.849 meV/H within 2 sigma; a 1D Morse unit test (Delta_anh(P = 16) within 0.06 meV of P = inf, GL2 anharmonic quadrature within 1e-3 meV). Monitors: heavy-atom centroid RMSD from x0 below 0.15 A, O-H coordination unchanged, proton-transfer coordinate delta = d(O-H) - d(H...O) histogram reported. Heavy-atom drift or a coordination change is a sampling failure (pair unresolved); proton delocalization at fixed heavy atoms is physics and is reported.

## Registered quantitative prediction (before any PIMD)

Opus's 1D frozen-lattice O-H stretch DVR on the MACE potential (P = inf, stretch only, not re-run by the chair). Delta_anh(b) - Delta_anh(a), meV/H: pair 1 +1.85 (37% of ddF_harm, H2 holds), pair 2 +3.62 (60%, H2 fails), pair 3 +0.84 (27%), pair 4 -0.74 (toward the rule's sign), pair 5 -0.32. Bend and libration anharmonicity is missing and may cancel 30 to 50% (Argon). Every convergence shortfall (beads, contraction, short runs) biases Delta_anh toward zero, that is toward the harmonic screen; a small measured correction must be read with that in mind.

## Ordered action list for the conductor

| # | Action | Owner | Time | Done-check |
|---|---|---|---|---|
| 1 | Commit this decision and the amended P12 (S1, S2, A1 to A13, registered prediction) before any MACE PIMD run | conductor | 1 h | `git log` shows the P12 amendment commit; `results/pimd/` empty or absent at that commit |
| 2 | S1 in the assembler: read struct_a / struct_b from `results/screen_pairs_refined.csv`, assert recomputed ddF_harm(b - a) gives +5.03, +6.00, +3.07, +1.50 (refined 1.507) meV/H | conductor (build) | 0.5 h | unit test passes |
| 3 | S2: `find_cache` matches volume_A3; test for mp-625054 and mp-626497 returns one cache each | conductor (build) | 0.5 h | `pytest tests/test_pimd.py -k cache` passes |
| 4 | A1 code: `MaceForces(dtype=...)`, float32 default for P12, float64 integrator; float32 vs float64 K_H gate on 20 configs | conductor (build) | 1.5 h | gate result <= 0.05 meV/H logged in `results/pimd/gates.json` |
| 5 | A6: fd_hessian (float32) for the 7 PIMD cells and the 64-atom mp-23807 cell; residual force and eigenvalue gates; compare with cached `harmonic_samecell` where exact | conductor | 1 h GPU | 8 Hessians saved with hashes; gates pass; diagnostic agreement <= 0.02 meV/H |
| 6 | Optional: 3D local-proton DVR (stretch + 2 bends, 15^3 grid per unique H site, float32) for the 7 structures, including Delta_anh(g) on a fine g grid as the GL2 check; runs on GPU while 7 and 8 run on CPU | conductor | <= 2 h GPU | committed before the first MACE PIMD step, else dropped and not cited as a prediction |
| 7 | CPU harmonic-backend checks on each PIMD-cell Hessian: P = 1, P = 16, P = 32 vs analytic; dt 0.25 vs 0.5; 1D Morse unit test (A13) | conductor | 1 h CPU | all within 2 sigma / 0.1 meV/H; dt choice written to `gates.json` |
| 8 | Throughput pilot: 30 min of mp-23807 P = 16 float32 with bead chunking; measure sustained s per ring step and throttling | conductor | 0.5 h GPU | measured step time within 1.5x of 1.49 s (96 atoms); if not, recompute the schedule and drop pair 4 first |
| 9 | Pair 3, structure b: mp-23807 3x2x2, GL2, 2 ps per node | conductor | 4.1 h GPU | SEM <= 0.3 meV/H, monitors pass |
| 10 | A4 + A7 checks: mp-23807 2x2x2, GL1, P = 16 and P = 32 | conductor | 4.1 h GPU | bead and size terms written to `gates.json`; P = 32 switch rule applied if triggered |
| 11 | Pair 3, structure a: mp-625152 3x2x1 | conductor | 4.1 h GPU | SEM, monitors; pair 3 scored |
| 12 | Pair 1, structure a: mp-625054 3x2x2 | conductor | 4.1 h GPU | pair 1 scored with mp-23807 covariance |
| 13 | Pair 2: JVASP-54682 3x2x1, JVASP-92228 3x2x2 | conductor | 8.3 h GPU | pair 2 scored |
| 14 | Pair 4: mp-626497 2x2x2, mp-985293 2x2x1, only if the remaining budget covers both | conductor | 9.6 h GPU | pair 4 scored, or reported "not run, compute" |
| 15 | Report: per-structure table (stat, sys, monitors), per-pair category, H1 to H4 with A11 rules, comparison with the registered prediction, pair 5 as invalid reference | conductor | 2 h | written to the paper's P12 section; no edit to F01 or hackathon posts |

GPU total: about 17 h for pairs 3 and 1 with the checks, about 25 h with pair 2, about 35 h with pair 4, at dt 0.5 fs. With dt 0.25 fs only pairs 3 and 1 plus the checks fit in 48 h. Keep about 25% of the budget for reruns.

## What would change this

* The throughput pilot (8) comes in above 1.5x the estimate, or the float32 gate (4) fails: drop pair 4, then pair 2; if pairs 3 and 1 no longer fit, run pair 3 only.
* The bead check (10) shows |Delta(16) - Delta(32)| > 0.3 meV/H beyond noise: P = 32 for everything, which doubles cost and leaves only pairs 3 and 1.
* Measured tau_int of the MACE centroid-virial above about 0.5 ps, so 6 ps does not reach SEM 0.3: report the achieved SEM and let A10 decide inconclusive; do not lengthen beyond 6 ps for one structure at the cost of a registered pair.
* The 3D DVR (6) shows Delta_anh(g) with curvature that GL2 misses by more than 0.05 meV/H: switch to GL3 before production.
* Heavy-atom drift or a proton-ordering change in mp-23807 or JVASP-54682: that structure is a sampling failure and the pairs that use it are unresolved; no rescue runs chosen after seeing values.
* Astra objects to the run-length or bead-check reductions with a concrete measurement: reopen before step 9.
