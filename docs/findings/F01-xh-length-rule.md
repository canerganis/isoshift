# F01. Deuteration favours the polymorph with shorter X-H bonds: a compensation law across 341 polymorph pairs

Status: computed 21 Oct ~21:30 from the interim screen (mace, orb, mattersim; sevenn pending). Data: `results/decompose_pairs.csv`, fit `results/F01_rule_fit.json`, figure `figures/fig4_xh_rule.png`, code `src/isoshift_event/decompose.py`.

## Result
For polymorph pairs of covalent X-H compounds (nearest non-H neighbour < 1.3 A: hydroxides, oxyhydroxides, hydrates, ammonium salts, borohydrides), the isotope double difference ddF_iso(300 K) per H is linear in the change of the mean X-H bond length between the two polymorphs:

| model | pairs | r | slope (meV per H per mA) | stretch slope | bend/libration slope | compensation |
|---|---|---|---|---|---|---|
| MACE | 177 | 0.78 | 0.116 | +0.244 | -0.128 | 52% |
| ORB | 121 | 0.84 | 0.120 | +0.253 | -0.133 | 53% |
| MatterSim | 43 | 0.89 | 0.147 | +0.257 | -0.110 | 43% |

Positive slope means that deuteration stabilises the polymorph whose X-H bonds are shorter (weaker hydrogen bonding). 0.01 A of X-H length difference, typical between hydroxide polymorphs, shifts the H/D free-energy balance by about 1.2 meV per H.

Mechanism (mode-resolved mass integral, M01 section 6, quadrature checked against the direct F_D - F_H to < 0.01 meV/atom per structure): the X-H stretch term alone has slope +0.25 meV/H per mA in all three models; the bending and libration term has the opposite sign and cancels about half of it. Stretch and bend/libration contributions have opposite signs in 79 to 92% of pairs with |ddF_iso| > 0.1 meV/atom.

Secondary tendency (weaker): oriented from the MLIP ground state to the metastable polymorph, deuteration further stabilises the ground state in 64% of covalent pairs (median +0.28 meV/H; fit intercept +0.37 meV/H at equal X-H length). No such tendency for hydridic (metal-H) compounds.

## Why it is credible
* Three independently trained universal potentials give the same stretch slope within 5% and the same total slope within 25%.
* Order-of-magnitude check: the empirical red shift of O-H stretching with bond length (about 10 cm-1 per mA in hydroxides) times the harmonic H/D zero-point factor (1 - 1/sqrt2) gives about 0.18 meV/H per mA for the stretch alone; the ensemble gives 0.25.
* The same stretch-versus-bend competition was derived by McKenzie et al. for hydrogen-bond isotope fractionation in molecules and proteins (J. Chem. Phys. 140, 174508 (2014), 10.1063/1.4873352; 143, 044309 (2015), 10.1063/1.4927391). F01 is the solid-state, polymorph-stability counterpart, obtained from an MLIP ensemble over hundreds of real and hypothetical crystal pairs.

## Limits
* Harmonic, 300 K. H-bond symmetrisation, tunnelling and proton disorder are outside the model (negative controls KDP, KOH, NaOH, delta-AlOOH).
* Only structures where omitting or |w|-treating imaginary modes gives the same F are used ("clean", 608 of 851 structure-model results).
* Sign agreement between the rule and the computed ddF_iso is 58 to 75%: near zero X-H change the bend/libration term and the intercept dominate, so the rule predicts sign reliably only when |dX-H| is above about 5 mA.
* All models are trained on PBE-like data; a shared bias in X-H lengths would move both axes together.

## What it is useful for
A structure-only predictor: from two crystal structures (no phonons), the X-H length difference estimates which polymorph deuteration favours and by how much. This can be applied to every H-containing polymorph pair in a database in seconds, and it tells neutron crystallographers when a deuterated sample may not be the same phase balance as the protonated one.

## Out-of-sample test (leave one chemical family out, `src/isoshift_event/rule_cv.py`, `results/F01_cv.json`)
Each formula family is removed, the line is refitted on the rest, and the held-out family is predicted. Pooled over models (312 pair-model rows, 57 families): held-out R^2 = 0.62; sign accuracy 86% for |dX-H| >= 5 mA (150 rows) against 67% for the best constant-sign baseline; 70% over all rows. Per model at |dX-H| >= 5 mA: ORB 98%, MatterSim 79%, MACE 76%. The rule transfers to chemistries it was not fitted on.

## Structure-only use with database geometries (`src/isoshift_event/rule_map.py`, `results/rule_map_summary.json`)
With X-H lengths taken directly from the Materials Project / JARVIS structures (no MLIP relaxation, no phonons), the pooled line predicts the ensemble ddF_iso with r = 0.65 over 197 covalent pairs and gets the sign right in 69% of pairs with |dX-H| >= 5 mA (vs 86% with MLIP-relaxed geometry). Database H positions are noisier than relaxed ones, so the structure-only rule is a pre-screen; relaxed geometries (any DFT or MLIP relaxation) are needed for reliable signs.
