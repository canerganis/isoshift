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
