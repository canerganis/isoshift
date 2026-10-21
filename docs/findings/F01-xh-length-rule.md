# F01. Deuteration favours the polymorph with the shorter O-H bonds once hydrogen bonds are moderate to strong

**Status: computed (three MLIPs; no polymorph isotope free energy has been measured).**

## Current statement (decision 05, numbers reproduced by `src/isoshift_event/rule_cv.py` into `results/F01_cv.json`)

**Headline.** Across 197 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.12 to 0.15 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds), deuteration favours the polymorph with the shorter O-H bonds in 123 of 130 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (67 pairs, 23 formulas), against 82 of 130 for a constant-sign baseline fitted on leave-one-formula-out training folds.

**Statistics and caveats.** The 0.99 Å boundary is model-derived and was chosen after inspecting the data; re-choosing it inside each leave-one-formula-out training fold selects 0.99 Å in every fold and leaves the held-out count unchanged, which covers the threshold value but not the choice of regime variable. Without any threshold the rule holds in 124 of 146 O-H evaluations (85%). On all covalent pairs with a signal cut (|ΔΔF| > 0.1 meV per H) it holds in 129 of 150 evaluations (86%; 23 of 28 decided formulas). Below the boundary it fails (1 of 16 evaluations, 13 pairs, 7 formulas). In the O-H strong regime the fitted total slope is 0.140 to 0.151 meV per H per mÅ, with bend and libration cancelling 41 to 53% of the stretch slope. A structure-only version using mean O...O ≤ 2.92 Å is weaker (127 of 153, 83%, against 64%). The three potentials are separate models, not independent validations, and no polymorph isotope free energy has been measured to test the rule directly.

**Prior art.** The stretch-bend competition behind the rule is established for hydrogen-bond isotope fractionation (McKenzie et al. 2014, 2015) and for competing quantum effects in hydrogen-bonded systems, and large-scale harmonic isotope thermodynamics has been reported for metal hydrides (Bourgeois et al. 2018). The contribution here is the systematic polymorph-stability version of that competition, its slope and its regime boundary.

Counts used above. 197 pairs is the size of the screen and of the slope fit, not of the sign test. The sign test is 130 O-H evaluations (67 pairs, 23 formulas) for the headline, 134 all-covalent evaluations with the 0.1 meV/H signal cut (70 pairs, 25 formulas) in the detail paragraph below. The 0.1 meV/H cut uses the target, so the headline drops it; it changes 2 rows. The 0.12 to 0.15 slope and the 43 to 53% compensation are all-row fits over the whole screen; the O-H strong-regime fit (0.140, 0.144, 0.151; compensation 0.50, 0.53, 0.41 for MACE, ORB, MatterSim) is a different population and is quoted separately. The O...O predictor is quoted at 83% (127/153), never at 95%. Experimental polymorph isotope free energies remain untested; the compensation term has one sign-level consistency check in F04.

Reproduced from the current files (decision 05 numbers, all matched): O-H strong, no target cut 123/130 (67 pairs, 23 formulas, per model MACE 51/57, ORB 56/56, MatterSim 16/17), training-fold baseline 82/130, unique-pair majority 62 right, 5 ties, 0 wrong; nested threshold re-choice 128/134 (all covalent, signal cut), 129/136 (all covalent, no cut), 122/128 (O-H, signal cut), 123/130 (O-H, no cut), 0.99 Å chosen in every fold of every variant (`nested_threshold_cv` in `results/F01_cv.json` has the per-fold ledger: formula, chosen threshold, held-out right/n; grid 0.97 to 1.03 Å in 0.01 steps, maximise right minus wrong, lowest threshold wins ties; the O-H variants have 28 folds, the all-covalent ones 30, folds without strong-side rows score 0/0). A 128/135 figure from an earlier grid is not reproduced and is dropped. No threshold, O-H, no cut: 124/146 (80 pairs; strong 123/130, weak 1/16). No threshold, all covalent, signal cut: 129/150 against a training-fold baseline of 100/150; formula majority 23 right, 5 wrong, 2 ties (binomial p = 0.0009, descriptive only, not a confirmatory test); on the strong side 23 right, 0 wrong, 2 ties.

Older sections below are kept as the record of how the result developed; where they disagree with this statement (e.g. "341 polymorph pairs", "transferable across chemical families", pooled leave-family-out numbers that count a pair up to three times), this statement wins.

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
* Three separately trained universal potentials give the same stretch slope within 5% and the same total slope within 25%.
* Order-of-magnitude check: the empirical red shift of O-H stretching with bond length (about 10 cm-1 per mA in hydroxides) times the harmonic H/D zero-point factor (1 - 1/sqrt2) gives about 0.18 meV/H per mA for the stretch alone; the ensemble gives 0.25.
* The same stretch-versus-bend competition was derived by McKenzie et al. for hydrogen-bond isotope fractionation in molecules and proteins (J. Chem. Phys. 140, 174508 (2014), 10.1063/1.4873352; 143, 044309 (2015), 10.1063/1.4927391). F01 is the solid-state, polymorph-stability counterpart, obtained from an MLIP ensemble over 197 crystal pairs.

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


## Regime analysis (decision 04)

Code: `src/isoshift_event/rule_cv.py` (`results/F01_cv.json`: `regime_scan`, `oh_split`, `n_unique_pairs`, `pair_majority_0.99_signal_filtered`, `strong_regime_cv`) and `src/isoshift_event/rule_oo.py` (`results/F01_oo.json`). The regime variable is the larger of the two polymorphs' mean model X-H length ("strong" side: at least the threshold, "weak" side: below). The 0.99 A cut was found after looking at the data. Sign tests use |dX-H| >= 5 mA. "Signal-filtered" additionally requires |ddF_iso| > 0.1 meV per H (the cut used since the first rule_cv and by the chair; decision 04 writes meV/atom but its counts are per H, which is what is reproduced here). "All-eligible" drops that second cut.

Counts: 341 clean covalent model evaluations, 197 unique pairs (178 O-H bearing, 19 not), 60 formulas. Eligible sign tests: 152 evaluations all-eligible, 150 signal-filtered, both over 83 unique pairs.

### Regime scan on the pair's maximum mean X-H length

Sign of dX-H predicts sign of ddF_iso, right/total evaluations (unique pairs in brackets). Signal-filtered first, all-eligible in the last two columns.

| threshold (A) | strong, filtered | weak, filtered | strong, all-eligible | weak, all-eligible |
|---|---|---|---|---|
| 0.97 | 129/150 (83) | 0/0 | 130/152 (83) | 0/0 |
| 0.98 | 128/148 (81) | 1/2 (2) | 129/150 (81) | 1/2 (2) |
| 0.99 | 128/134 (70) | 1/16 (13) | 129/136 (70) | 1/16 (13) |
| 1.00 | 128/134 (70) | 1/16 (13) | 129/136 (70) | 1/16 (13) |
| 1.01 | 111/114 (60) | 18/36 (26) | 112/116 (60) | 18/36 (26) |
| 1.02 | 86/86 (43) | 43/64 (40) | 87/87 (43) | 43/65 (41) |
| 1.03 | 80/80 (42) | 49/70 (44) | 81/81 (42) | 49/71 (44) |

The 0.99 and 1.00 rows are identical because no structure has a mean model X-H length between them. The 0.99 row reproduces decision 04 exactly (128/134 and 1/16); the all-eligible variant differs only by two extra rows (129/136). Per model on the strong side at 0.99 (filtered): MACE 54/59, MatterSim 15/16, ORB 59/59. Weak side at 0.99: MACE 0/11, MatterSim 0/3, ORB 1/2.

Unique pairs by model majority (filtered, strong side at 0.99): 65 right, 5 ties, 0 wrong of 70. Weak side at 0.99: 1 right, 12 wrong of 13. Constant-sign baseline on the strong side: 84/134 in sample (62.7% of rows have positive dX-H); inside the formula-clustered CV below the baseline comes from each training fold and gives the same 84/134.

Slopes (meV per H per mA, all clean rows on the side, 0.99 A): strong side MACE 0.124 (r 0.84, n 101), MatterSim 0.153 (r 0.90, n 31), ORB 0.121 (r 0.84, n 80). Weak side MACE -0.27 (r -0.69, n 76), MatterSim -0.06 (r -0.50, n 12), ORB -0.02 (r -0.10, n 41). The weak-side failures are not one formula: the 16 rows come from Al(OH)3, Be(OH)2, Cd(OH)2, Zn(OH)2, NaOH and RbOH (all wrong) and one FeOOH row (right). Without NaOH the weak side is 1/12. "No skill when both bonds are weak" is safe; "reversed law" is not.

O-H split (filtered): over all regimes O-H bearing pairs 123/144 (80 pairs), non-O-H 6/6 (3 pairs). On the strong side at 0.99, O-H 122/128 (67 pairs) and non-O-H 6/6 (3 pairs). Non-O-H support stays anecdotal.

Formula-clustered CV inside the strong regime (leave one formula out, line refitted on the training formulas, strong side at 0.99, 134 scored evaluations, 70 pairs, 25 scored formulas; the regression fit set has 44 formulas, because it includes strong-side rows with |dX-H| < 5 mA that are fitted but not scored): the fitted line gets 128/134 (95.5%), identical to the bare sign of dX-H, against 84/134 (62.7%) for the training-fold constant-sign baseline; held-out R^2 0.67. Per model: MACE 54/59 against baseline 35/59, MatterSim 15/16 against 1/16 (that baseline is an artefact: its 16 strong-side signs split 8 positive and 8 negative, so leaving a formula out always hands the training fold the opposite majority; ignore it for this model), ORB 59/59 against 39/59. The all-eligible fit set gives 129/136 against 86/136. The original all-regime CV is unchanged (129/150, 86%, all covalent, signal cut, baseline 100/150, R^2 0.62).

### Version in O...O

Predictor: mean donor O...O distance per structure (mean over the O-H donors of the primitive cell in `results/stretch_check.csv`, acceptor = nearest other O of the H with H...O < 2.6 A), difference taken in the same orientation as dX-H (struct_a and struct_b of `screen_pairs_refined.csv`, which is not the order in `pair_id`). It exists for 268 of 341 evaluations (146 of 197 pairs, 42 formulas; MACE 133, ORB 99, MatterSim 36). The rule reads: deuteration favours the polymorph with the longer mean O...O, sign(ddF_iso) = -sign(dOO). Sign tests use |dOO| >= 0.03 A (about 4 mA of O-H at the fitted dO-H/dO...O of -0.13).

Translation of the 0.99 A model O-H threshold: the mean model O-H reaches 0.99 A at an O...O of about 2.92 A (donor-level fit 2.88 to 2.92 A across models, structure-level fit 2.92 to 2.97 A, inverse fit 2.85 to 2.92 A, median of structures with mean O-H within 12 mA of 0.99 A: 2.88 to 2.92 A). Strong regime in O...O means the shorter polymorph's mean O...O is at most about 2.9 A.

Sign accuracy of -sign(dOO), signal-filtered, right/total evaluations (pairs), regime = shorter polymorph's mean O...O at most t:

| t (A) | strong (O...O <= t) | weak (O...O > t) |
|---|---|---|
| 2.60 | 63/63 (34) | 73/127 (81) |
| 2.70 | 99/103 (55) | 37/87 (57) |
| 2.80 | 120/131 (70) | 16/59 (40) |
| 2.90 | 127/149 (81) | 9/41 (31) |
| 2.92 (translated) | 127/153 (83) | 9/37 (27) |

Over all regimes the O...O rule gets 136/190 (71.6%) and the O-H rule gets 135/190 on the same rows. In the translated strong regime the pooled counts are 127/153 against a training-fold baseline of 98/153 (64%); per model MACE 52/69, ORB 57/63, MatterSim 18/21. The O...O regime and the O-H regime agree on all but 21 of 190 eligible evaluations (17 are O-H weak and O...O strong). Skill rises as the O...O limit tightens (92% at 2.80 A, 100% at 2.60 A), and on the weak side the sign is reversed (24%), as with the O-H scan.

As a magnitude predictor, O...O is much weaker than O-H length. Linear fit of ddF_iso per H on dOO over all 268 evaluations: slope -9.4 meV per H per A (r -0.45; MACE -7.8, r -0.42; ORB -10.6, r -0.51; MatterSim -24.8, r -0.54), against r 0.88 for dX-H on the same rows. In the strong regime the leave-one-formula-out line gets 112/153 signs (73%, held-out R^2 0.16), below the bare sign rule (127/153, 83%). So the usable O...O statement is the sign rule and the domain, not a linear law. The relation is also non-linear because dO-H against dO...O flattens at long distances and the mean over donors mixes hydrogen bonded and weakly bonded H. A sensitivity run with only donors with d(O...O) <= 3.2 A (or 3.0 A) keeps the picture (82% and 80% sign accuracy over all regimes, strong side 87% and 84%, translated threshold 2.90 and 2.83 A) but drops coverage to 138 and 123 pairs; see `sensitivity_donor_cap` in `results/F01_oo.json`.

Decision 04 trigger 2 (O...O refit loses the strong-regime sign skill) is not met: the sign rule in O...O keeps 83% against a 64% baseline. Trigger 3 (weak-side failure from one formula) is not met either; six formulas contribute.
