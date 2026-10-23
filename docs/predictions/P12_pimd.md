Post-submission test on branch `post-hackathon`; the frozen F01 headline (decision 07) is unchanged.

# P12: path-integral check of the harmonic isotope double difference (predeclared before any PIMD data)

Both round-1 referees of the paper draft (`docs/paper/reviews/round1_opus.md` item 3, `round1_gpt-6-astra.md` item C) asked for a beyond-harmonic control on a few headline pairs. This file fixes the pairs, the method, the harmonic reference values and the outcome rules before any path-integral simulation is run. It is committed before the first PIMD job; every PIMD output goes to `results/pimd/` with commits after this one.

## 1. Pairs and structures

Same orientation and sign convention as F01 and `decompose.py`: ddF_iso(b - a) = [F_D - F_H]_b - [F_D - F_H]_a per H at 300 K; positive means deuteration favours a. Mean O-H is the frozen `decompose.py` definition. Harmonic values are MACE medium-mpa-0, full q-mesh, from `results/decompose_pairs.csv` (`ddF_total / H_per_atom`).

| # | pair (a__b) | formula | role | Δ mean O-H (b - a), mÅ | harmonic ddF_iso, meV/H | rule's sign |
|---|---|---|---|---|---|---|
| 1 | mp-23807__mp-625054 | AlHO2 | strong regime, large signal | +41.8 | +5.03 | + (agrees) |
| 2 | JVASP-54682__JVASP-92228 | FeHO2 | strong regime, large signal | +23.5 | +6.00 | + (agrees) |
| 3 | mp-23807__mp-625152 | AlHO2 (δ-AlOOH vs diaspore) | strong regime, the AlOOH prediction pair | +32.4 | +3.07 | + (agrees) |
| 4 | mp-626497__mp-985293 | Al(OH)3 | the mp-985293 exception | -15.9 | +1.50 | - (harmonic disagrees with the rule) |
| 5 | mp-23940__mp-626000 | NaOH | weak regime (rmax 0.984 Å) | -11.5 | +5.80 | - (harmonic disagrees; weak side) |

Nine structures in total (mp-23807 is shared by pairs 1 and 3). Geometries are the MACE-relaxed cells of the screen, read from the force-constant cache (`.cache/isoshift/*__mace-medium-mpa-0__*`, matched by energy and atom count to `results/raw/screen/mace/<id>.json`).

## 2. Method (fixed before data)

* Potential: MACE medium-mpa-0, the same model as the harmonic reference. Conservative forces, float64.
* Ensemble: path-integral molecular dynamics, NVT, 300 K, at the fixed relaxed cell and positions of the screen (Helmholtz, the same thermodynamic quantity as the harmonic screen at fixed volume). Supercell: the smallest diagonal supercell with all perpendicular widths at least 8 Å (`supercell_for_min_length`, cap 128 atoms).
* Integrator: normal-mode ring-polymer propagation with a PILE-L thermostat (centroid Langevin time constant 100 fs, internal modes critically damped), time step 0.25 fs for the H runs.
* Free energy of full H to D substitution by thermodynamic integration over the hydrogen mass. With g = sqrt(m_H/m), F(m_D) - F(m_H) = ∫ from 1 to g_D of 2 <K_H(g)>/g dg, g_D = sqrt(m_H/m_D) = 0.70737, where <K_H> is the centroid-virial kinetic energy of all hydrogen atoms. Gauss-Legendre quadrature on 4 points in g. The classical part of this integral is the same for both polymorphs and cancels in ddF.
* Same-cell harmonic reference: F_D - F_H from the cached MACE force constants on the q-points commensurate with the PIMD supercell. The anharmonic and quantum correction is Δ_anh = [F_D - F_H]_PIMD - [F_D - F_H]_harm,same cell, per structure, and the corrected double difference is ddF_corr = ddF_harm,full mesh + Δ_anh(b) - Δ_anh(a). The same-cell subtraction removes the finite-size difference between the PIMD supercell and the full q-mesh.
* Convergence and error, set now: beads P chosen in the pilot so that F_D - F_H per H changes by less than 0.3 meV between P and 2P on the pilot structure; statistical error of F_D - F_H per H from block averaging, target below 0.3 meV per structure. A pair whose combined error on ddF_corr exceeds 1 meV/H is reported as inconclusive.
* Acceptance tests before production: 1D harmonic oscillator and an isolated O-H diatomic (analytic quantum F, `docs/math/M00-plumbing-diatomic-zpe.md`), H to D difference within 0.2 meV of the analytic value.

## 3. Predictions and outcome rules

* H1 (primary). Pairs 1, 2 and 3: ddF_corr has the same sign as the harmonic ddF_iso. Support: 3 of 3 with the sign resolved beyond the combined error. Challenge: any of the three changes sign beyond the error.
* H2. Pairs 1, 2 and 3: |ddF_corr - ddF_harm| is smaller than half of |ddF_harm|. Reported per pair; a larger correction in any pair is stated as a limit of the harmonic screen even if the sign holds.
* H3 (exploratory, no direction predicted). Pair 4: whether the anharmonic correction moves ddF toward the rule's sign (negative). Reported either way.
* H4 (exploratory, no direction predicted). Pair 5: the size and sign of the correction on the weak side. Reported either way.
* Not tested here: the sign rule across the screen, the pressure prediction for AlOOH, and any model other than MACE.

## 4. What this does not change

The frozen F01 numbers and the hackathon entry are unchanged. A failure of H1 is reported in the paper next to F07, F02 and F11 and limits the rule's claims to the harmonic models.

## 2a. Amendments before production data (24 Oct 2026, decisions 17 and 18)

Committed before any MACE PIMD sampling; `results/pimd/` does not exist at this commit. The only MACE calls so far are the float32 vs float64 force gate on harmonic-backend configurations (A1) and cost benchmarks, none of which samples the MACE ensemble. Decision 18 (`docs/decisions/18-pimd-design.md`, converged, Opus and Astra over two rounds) governs. Decision 17 (`docs/decisions/17-pimd-method.md`, not converged, Astra absent from round 2) is superseded where the two differ; three points of 17 that 18 does not cover are kept as A12 to A14. Where 2a and section 2 differ, 2a holds.

* **A1 Precision.** MACE medium-mpa-0 in float32 (positions, momenta, transforms, centroid virial and statistics in float64; TF32 and autocast off). The cached force constants and every screen relaxation are float32 (`isoshift/calculators.py`), so float32 PIMD runs on the same PES as the harmonic reference; float64 at P = 64 would take about 5 weeks. Gate passed on 24 Oct: centroid-virial K_H from float32 and float64 forces on 20 harmonic-backend P = 16 configurations of mp-23807, max difference 8e-5 meV/H (tolerance 0.05). Control C2 (float64 re-evaluation of production snapshots) still applies.
* **A2 Same-P reference.** Delta_anh = dF_PIMD,P - dF_harm,samecell,P, the second term the analytic P-bead harmonic value on the same commensurate q set with the same COM treatment; the infinite-P value is stored. For a harmonic PES this is zero at every P, so the 1.8 to 5.9 meV/H harmonic bead error at P = 16 cancels. The P vs 2P rule of section 2 applies to Delta_anh, not to raw F_D - F_H.
* **A3 No ring-polymer contraction.** On a Morse O-H stretch at P = 64, contraction to n_c = 8 keeps 56 % of Delta_anh; plain P = 16 with A2 misses by 0.023 to 0.052 meV.
* **A4 Beads.** P = 16 for every production value. Pilot on mp-625152 at P = 16 and P = 32 with d = Delta_anh(32) - Delta_anh(16): P = 16 is rejected only if |d| > 0.3 meV/H and |d| > 1.96 sigma_d (then branch F, A11). Otherwise s_P = max(0.05, A4b residual, |d| - sigma_d) per structure. The pilot detects gross failures near 0.45 meV/H; the finer bound is A4b. A second P = 32 check runs on the H1 structure with the largest A4b residual (excluding mp-625152).
* **A4b 1D scan bound.** For each of the 9 structures, float32 MACE scans along each symmetry-distinct O-H (41 points, -0.4 to +0.8 A, other atoms fixed) and along O...O where O...O < 2.7 A; exact 1D transfer-matrix residual at P = 16 against P = 128, weighted per H. Committed before run 1; it names the second-check structure.
* **A5 Time step.** dt = 0.25 fs, BAOAB ("middle") splitting set explicitly in every run, PILE-L tau0 100 fs, gamma_k = 2 omega_k. s_dt = max(0.06, C1). `check_step_stable` must pass for each run.
* **A6 Sampling.** Initialise from the analytic harmonic P-bead distribution of the PIMD cell (centroid included, zero amplitude on the 3 translations and imaginary modes); 1000 pre-equilibration steps at g = 1 discarded; 3000 steps per GL point with 600 discarded, warm-started point to point. Fixed step count with two sign-blind exceptions: (i) if tau_int at the first point of the mp-625152 P = 16 run exceeds 24 steps, all runs use 4000 steps per point (branch T); (ii) a point whose kept halves differ by more than 3 sigma_half gets one 3000-step extension, and a second failure fails the stationarity gate.
* **A7 Quadrature.** Four GL points kept (g = 0.72770, 0.80395, 0.90343, 0.97968). Check C4: 4 vs 8 points with exact finite-P harmonic K on all 9 spectra, below 0.01 meV/H.
* **A8 Cache match.** Energy (1e-6 eV), natoms_cell, supercell, n_displacements and volume_A3 (1e-4 A^3); unique for all 9 (commit 1122c05).
* **A9 Imaginary modes.** mp-626497 (-0.62 THz) and mp-23940 (-0.91 THz) have one imaginary heavy-atom mode on the commensurate grid. The primary reference folds it to |nu|, as `decompose.py` does on the full mesh; s_imag = |folded - dropped| (0.023 and 0.009 meV/H) is an allowance, not a bound. Retention gate: mean centroid displacement along that eigenvector below 0.1 A and no change in the O-H...O assignment, else the pair is not assessable. This replaces "never take absolute values" for these two structures.
* **A10 Error and scoring.** Per structure, sigma from block averaging through the GL weights; sigma_pair = sqrt(sigma_a^2 + sigma_b^2); B_pair = s_dt + s_f32 + s_quad + s_P,a + s_P,b + s_hess,a + s_hess,b + s_imag,a + s_imag,b, added linearly; E_pair = 1.96 sigma_pair + B_pair is the combined error of sections 2 and 3. Resolved: |ddF_corr| > E_pair. Inconclusive: E_pair > 1 meV/H or a failed gate (C1, C2, stationarity, Hessian check, retention, A13, A14). H1 support: pairs 1 to 3 all resolved with the harmonic sign. H1 challenge: any of them resolved with the opposite sign. Otherwise undecided, with counts and denominator 3. H2 per pair: supported if |Delta_anh(b) - Delta_anh(a)| + E_pair is below half of |ddF_harm| (2.515, 3.000, 1.535 meV/H), exceeded if |...| - E_pair is above it, else unresolved. Pairs 1 and 3 share mp-23807; the covariance is stated.
* **A11 Priority and cap.** Order: smoke test, A4b, mp-625152 at P = 16 then P = 32 (pilot), C2, mp-23807, mp-625054, JVASP-54682, JVASP-92228, second P = 32 check, pair 4, pair 5. Hard cap 48 measured GPU hours; pair 5 drops first, then pair 4. Branch F (pilot rejects P = 16): pairs 1 to 3 at P = 32, pairs 4 and 5 not run, decided on the pilot alone. Not run is reported as not run.
* **A12 Orientation (decision 17 S1).** The section 1 column "pair (a__b)" lists b first: pair 1 b = mp-23807, a = mp-625054; pair 2 b = JVASP-54682, a = JVASP-92228; pair 3 b = mp-23807, a = mp-625152; pair 4 b = mp-626497, a = mp-985293; pair 5 b = mp-23940, a = mp-626000, as in `results/screen_pairs_refined.csv` (struct_a is the second id). Values unchanged. The scorer asserts that recomputed ddF_harm(b - a) reproduces +5.03, +6.00, +3.07, +1.50 and +5.80 meV/H.
* **A13 Residual force (decision 17).** mp-23940 stopped its screen relaxation unconverged (500 steps, fmax 0.031 eV/A); mp-626000 also hit 500 steps (fmax 2.3e-4 eV/A). A harmonic expansion about a non-stationary point omits a linear term. Each run records max |F| at x0 in float32; above 1e-3 eV/A the structure is an invalid reference and its pair is not scored. This is expected for mp-23940, so pair 5 is likely not assessable. No re-relaxation inside P12, since that would change the frozen harmonic reference.
* **A14 Structural monitors (decision 17).** Heavy-atom centroid RMSD from x0 below 0.15 A and O-H coordination unchanged, else a sampling failure (pair inconclusive). The proton-transfer coordinate d(O-H) - d(H...O) is histogrammed and reported; proton delocalisation at fixed heavy atoms is physics, not failure.

Registered expectation before any PIMD: decision 17's 1D frozen-lattice O-H stretch DVR on MACE gives Delta_anh(b) - Delta_anh(a) of +1.85, +3.62, +0.84, -0.74 and -0.32 meV/H for pairs 1 to 5 (stretch only; bend and libration missing). Every convergence shortfall biases Delta_anh toward zero, that is toward the harmonic screen.
