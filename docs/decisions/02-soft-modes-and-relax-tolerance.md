# 02. Soft-mode structures and relax tolerance in the screen

Decision (Opus, 21 Oct ~18:30; extends the gate board's brucite ruling in 01 to the mass screen; no new board, revisited at the final-claims board).

Evidence (interim screen, mace/orb/mattersim): 67% (mace) and 81% (orb) of screened structures were quarantined. Quarantined structures have real imaginary branches (median min frequency -2 to -6 THz) that are small (median imaginary fraction about 1%), the same pattern as brucite (decision 00): symmetry-constrained relaxation of database structures leaves H libration saddles. ORB relaxations stop at fmax about 3e-3 eV/A (median), its force noise floor, so the 1e-3 target never converges.

Rules:
1. Two ranking tiers. Clean tier = no imaginary modes; P14 applies unchanged and supplies headline candidates. Bracketed tier = structures whose imaginary fraction is <= 2% (`soft_mode_bracketed`); F_vib is computed with imaginary modes omitted and with |w|, and |ddF_omit - ddF_abs| (max over 0/300/600 K) enters the numerical error, so a pair ranks only if its signal exceeds that bracket too. Bracketed results are always labelled as such.
2. The classical-limit check (01, F3) runs on the |w| treatment for bracketed structures, since omitting modes breaks the kT ln(w_D/w_H) cancellation by construction.
3. A relaxation counts as converged when fmax_final <= 5e-3 eV/A. The F_vib change from such residual forces is far below the 0.1 meV/atom floor.
4. Structures with > 2% imaginary fraction stay quarantined and listed. Every top-10 candidate, from either tier, gets the P11 eigenvector-following check before a candidate card is written.

Effect on the interim run: clean tier 7 eligible pairs, bracketed tier 38.
