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
