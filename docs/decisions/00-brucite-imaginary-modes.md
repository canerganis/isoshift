# 00. Brucite imaginary modes (P2 application)

Decision (Opus, 21 Oct, no board: evidence is unambiguous). Brucite P-3m1 stays the reference structure for QHA; its small imaginary branch is documented, not "fixed".

Evidence (MACE medium-mpa-0, ORB v3 conservative; primitive cell, fmax 1e-4):
* Imaginary branch at K = (1/3,1/3,0): -3.6 THz (MACE), -2.0 THz (ORB). Pure H in-plane motion (H weight 0.50 to 0.55): H moving off the three-fold axis.
* Not a supercell artefact: mesh minimum -3.6 to -3.7 THz for 2x3x2, 3x3x2, 4x4x2 supercells; imaginary fraction 0.6 to 0.9% of modes.
* The isotope quantity is converged anyway: F_H - F_D at 300 K changes by 0.1 meV/cell across the three supercells (180.6 meV/cell).
* P2 displacement along the K mode and symmetry-free relaxation gives a sqrt3 x sqrt3 P31m structure only 0.26 meV/atom (MACE) and 0.07 meV/atom (ORB) lower.
* This matches the measured H disorder of brucite (H split over three off-axis sites in neutron data) and the anharmonic stabilisation of P-3m1 reported by Trevino et al. 2018 (10.1039/c8cp02490a). The well depth is far below the H libration zero-point energy, so the quantum H sits on average on the axis.

Consequences:
* QHA on P-3m1 with phonopy, which omits the imaginary modes from F_vib (same modes for H and D). Reported with the imaginary fraction.
* Brucite counts for gate tier B, flagged "shallow H multi-well".
* Exploratory idea tested and dropped (30 min timebox): a 1D soft-mode double-well classifier for isotope-induced ordering. On NaOH (NaOD orders at 153 K, NaOH does not) MACE and ORB disagree on the soft mode (heavy-atom layer shift vs 43 meV H well) and both predict H and D localized. MLIP barriers at this scale are not reliable enough; not pursued.

## Amendment (gate follow-up F1, 21 Oct)

Four-model check over the 9 QHA volumes, from `results/validation/volume_isotope.csv` (`python -m src.isoshift_event.validate collect`, cached force constants, Γ acoustic modes dropped per M01 (1)). Imaginary fraction counts non-acoustic modes below -0.1 THz, H masses. VIE = 100 (V_H/V_D - 1) at 290 K. Measured brucite +0.31%; portlandite has no clean experimental pair (null check, decision 01).

| case | model | imaginary fraction over V grid | min freq (THz) | VIE omit | VIE \|ω\| | VIE range, 4 treatments |
|---|---|---|---|---|---|---|
| brucite | mace | 0.36 to 0.83% | -4.66 | +0.292 | +0.321 | +0.280 to +0.335 |
| brucite | orb | 0.24 to 0.68% | -4.65 | +0.278 | +0.310 | +0.278 to +0.310 |
| brucite | mattersim | 0.13 to 0.29% | -2.18 | +0.192 | +0.194 | +0.192 to +0.194 |
| brucite | sevenn | 0 to 0.82% | -5.26 | +0.394 | +0.438 | +0.394 to +0.438 |
| portlandite | mace | 0.51 to 0.96% | -3.32 | -0.027 | +0.000 | -0.052 to +0.018 |
| portlandite | orb | 0.60 to 0.92% | -5.84 | +0.082 | +0.080 | +0.079 to +0.082 |
| portlandite | mattersim | 0.28 to 0.67% | -1.50 | +0.041 | +0.041 | +0.040 to +0.042 |
| portlandite | sevenn | 0.15 to 0.54% | -2.09 | +0.232 | +0.241 | +0.232 to +0.241 |

Brucite stays positive in 16/16 model × treatment cases; the treatment spread per model (at most 0.055 pp) is well below the model spread (0.25 pp). Portlandite changes sign only within mace, around zero.

Deviation logged: the PLAN.md 1.4 done criterion ("brucite min optical freq > -0.5 THz in ≥3 models") is not met (min -2.2 to -5.3 THz in all four models); the branch is physical (H off the three-fold axis, see above) and its effect on the volume isotope effect is bounded by the four-treatment bracket.
