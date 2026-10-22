Status: post-freeze addendum, prospective. The frozen F01 headline (decision 07: 185 of 212, baseline 131, pairs 74/0/10) is unchanged.

# F11. Prospective held-out test of the frozen F01 rule on pairs never computed

Prediction: `docs/predictions/P10_prospective.md` and `results/post_freeze/P10_predictions.csv`, commit eb61ccf, pushed before any phonon job of this test (pilot submitted after the push). Scores: `results/post_freeze/F11_prospective.json`; rows: `results/post_freeze/P10_scored_rows.csv`; decomposition: `results/post_freeze/P10_decompose_structures.csv`. Commands as committed: `python -m src.isoshift_event.p10 decompose`, then `score`. Counts as of 13:46 TRT; updated after each GPU batch, last update by 22:30.

## 1. Predeclared verdict

**Primary: FAIL.** Frozen F01 sign rule at 300 K (rmax ≥ 0.99 Å, |Δ mean O-H| ≥ 5 mÅ), scored exactly as committed in P10 section 5.

* **Counted: 96 of 111 committed primary rows** (62 failed or unstable, 13 not clean, 21 scored); 14 right (14.6%), frozen constant-sign baseline (+1) 4. The other 15 committed rows have not been computed yet or cannot be (section 5).
* **Ceiling:** the 75 rows lost to the predeclared numerical rules count as not right whatever their sign, so even if every committed row still to come were clean and right, the pooled accuracy could reach at most (111 - 75)/111 = 32.4%, against the 75% bar.
* **Clean rows only (per protocol, no bar):** the rule is right in 14 of 21; a constant sign of -1 (deuteration favours b) would be right in 17 of 21, the frozen constant +1 in 4 of 21. The rule does not beat a constant guess on the clean rows.
* **Pairs (unique-pair majority, all counted rows):** 4 right, 1 tie, 29 wrong of 34.
* **Structure transfer (Al(OH)3 and H2O, formulas in the frozen F01 population):** 1 of 23 right.
* Per model: mace 5/33, orb 4/31, mattersim 5/32.

| Predeclared bar (decision 08) | Met |
|---|---|
| min size 30 evals 12 pairs 6 formulas | yes |
| pooled acc ge 0.75 | no |
| ge 15 points above baseline | no |
| pair majority right ge 0.80 | no |

**Secondary (600 K, no threshold, all O-H rows with |Δ| ≥ 5 mÅ): not met (bar ≥ 90%).** 14/96 right (14.6%), constant-sign baseline 2/96, 34 pairs, 16 formulas, pair majority right/tie/wrong 5/0/29. Per model: mace 3/33, orb 6/31, mattersim 5/32. The same numerical rules apply; clean rows only: 14/14 right (100.0%), constant-sign baseline 2/14, 7 pairs, 5 formulas, pair majority right/tie/wrong 7/0/0.

## 2. Not computed, in committed order

27 eligible pair-model rows have no result yet or cannot be computed (supercell above 160 atoms), in committed order: 33 mp-24043__mp-703459 mace (primary); 33 mp-24043__mp-703459 mattersim (primary); 33 mp-24043__mp-703459 orb (primary); 34 mp-510654__mp-1200251 mace (primary); 35 mp-554651__mp-1237009 mace (primary); 36 mp-557615__mp-1194761 mattersim (primary); 38 mp-696735__mp-703459 mace (primary); 38 mp-696735__mp-703459 mattersim (primary); 39 mp-697085__mp-703459 mace (primary); 39 mp-697085__mp-703459 mattersim (primary); 39 mp-697085__mp-703459 orb (primary); 40 mp-703459__mp-2739191 mace (primary); 40 mp-703459__mp-2739191 mattersim (primary); 40 mp-703459__mp-2739191 orb (primary); 41 mp-766178__mp-1198515 mattersim (primary); 43 mp-24004__mp-722516 mace; 43 mp-24004__mp-722516 mattersim; 43 mp-24004__mp-722516 orb; 44 mp-23879__mp-643392 mace; 44 mp-23879__mp-643392 mattersim; 44 mp-23879__mp-643392 orb; 45 mp-24595__mp-698170 mace; 45 mp-24595__mp-698170 mattersim; 45 mp-24595__mp-698170 orb; 46 mp-24595__mp-721300 mace; 46 mp-24595__mp-721300 mattersim; 46 mp-24595__mp-721300 orb.

## 3. Rows lost to the numerical rules, by structure

75 primary rows are lost (13 not clean, 62 unstable or failed). Structures responsible (a row can involve two), with the number of primary rows each touches, the largest quadrature-direct gap in meV/atom and the largest imaginary-mode fraction over the three models:

| structure | formula | primary rows touched | max gap (meV/atom) | max imaginary fraction | min frequency (THz) |
|---|---|---|---|---|---|
| mp-1181168 | KP(HO2)2 | 18 | 0.017 | 0.027 | -2.93 |
| mp-757909 | KP(HO2)2 | 16 | 0.028 | 0.051 | -3.54 |
| mp-24043 | H2O | 9 | 0.048 | 0.013 | -2.16 |
| mp-696735 | H2O | 8 | 0.181 | 0.045 | -4.32 |
| mp-24263 | KP(HO2)2 | 6 | 0.226 | 0.073 | -9.46 |
| mp-699437 | KP(HO2)2 | 6 | 0.029 | 0.037 | -3.95 |
| mp-2739191 | H2O | 6 | 2.244 | 0.061 | -48.24 |
| mp-24262 | KP(HO2)2 | 6 | 0.406 | 0.052 | -16.09 |
| mp-690711 | TlP(HO2)2 | 6 | 0.418 | 0.057 | -18.34 |
| mp-24022 | RbH3(SeO3)2 | 3 | 0.036 | 0.069 | -3.78 |
| mp-1205457 | RbH3(SeO3)2 | 3 | 0.254 | 0.090 | -5.19 |
| mp-1180593 | KH3(SeO3)2 | 3 | 0.030 | 0.059 | -3.30 |
| mp-706579 | KH3(SeO3)2 | 3 | 0.371 | 0.066 | -15.36 |
| mp-1200196 | ZnP2(H4O5)2 | 3 | 0.024 | 0.022 | -3.11 |
| mp-1182406 | CrHSe3O8 | 3 | 0.002 | 0.031 | -2.47 |
| mp-24390 | CaPHO4 | 3 | 0.011 | 0.046 | -3.77 |
| mp-1201415 | Li3V(H4O3)4 | 3 | 0.018 | 0.010 | -2.69 |
| mp-1198234 | Li3V(H4O3)4 | 3 | 0.015 | 0.009 | -2.57 |
| mp-1196113 | TlP(HO2)2 | 3 | 0.015 | 0.036 | -2.57 |
| mp-697267 | TlP(HO2)2 | 3 | 0.014 | 0.030 | -2.93 |
| mp-1198592 | BHO2 | 2 | 0.071 | 0.013 | -2.66 |
| mp-696403 | BHO2 | 2 | 0.016 | 0.017 | -2.22 |
| mp-761681 | CrHSe3O8 | 2 | 0.408 | 0.020 | -2.65 |
| mp-697085 | H2O | 2 | 0.023 | 0.005 | -1.63 |
| mp-1196989 | ZnP2(H4O5)2 | 1 | 0.011 | 0.011 | -3.10 |
| mp-721062 | V2Cu3H6O11 | 1 | 0.201 | 0.046 | -6.78 |

Cause, as far as traced: the gap tracks the imaginary modes. Over all 129 decomposed structure-model entries, the 68 with a gap ≥ 0.01 meV/atom have a median imaginary fraction of 0.035 and a median lowest frequency of -3.16 THz, against 0.0030 and -1.49 THz for the rest. `decompose.py` integrates |ω| in the quadrature while the direct value from `isoshift.phonons` drops modes below 0.1 THz, so soft modes enter the two numbers differently (decision 10 records the same reading; the phonopy side was not traced further). The rule was committed before the data and is not changed here; this is a sensitivity note, not a re-score.

## 4. Rows that pass the predeclared numerical rules (per protocol, no bar)

* Primary: 14/21 right (66.7%), constant-sign baseline 4/21, 8 pairs, 6 formulas, pair majority right/tie/wrong 4/1/3. Per model: mace 5/7, orb 4/6, mattersim 5/8.

## 5. Other predeclared subsets (reported, not scored against a bar)

* Primary at 1.00 Å (all evaluated rows): 13/87 right (14.9%), constant-sign baseline 2/87, 31 pairs, 15 formulas, pair majority right/tie/wrong 4/1/26.
* Primary, structure transfer (Al(OH)3 and H2O, formulas in the frozen F01 population): 1/23 right (4.3%), constant-sign baseline 2/23, 8 pairs, 2 formulas, pair majority right/tie/wrong 0/0/8.
* Primary, new formulas: 13/73 right (17.8%), constant-sign baseline 2/73, 26 pairs, 14 formulas, pair majority right/tie/wrong 4/1/21.
* Weak side (rmax < 0.99 Å, |Δ| ≥ 5 mÅ) at 300 K: 0 rows.
* P08 MP-geometry sign on clean primary rows: agrees with the computed sign in 14 of 21; the relaxed-geometry prediction in 14 of 21.
* Pairs with mp-985293 (orders 16 and 18): 1 of 6 primary rows right; outcomes: mace mp-27540__mp-985293 scored y=-1.012, orb mp-27540__mp-985293 scored y=-0.193, mattersim mp-27540__mp-985293 scored y=-0.055, mace mp-560572__mp-985293 scored y=+1.238, orb mp-560572__mp-985293 scored y=+0.172, mattersim mp-560572__mp-985293 scored y=-0.065.

## 6. Descriptive, not predeclared

Disclosure: during decision 10 (about 13:15) a council member computed a pooled compensation C = 0.285 on the 24 primary rows decomposed by then (orders 1 to 8 and 42). The numbers below were therefore computed after part of the data had been seen. No window was set for them and they carry no verdict.

* Clean primary rows (n = 21), pooled: total slope 0.179 meV/H per mÅ, stretch 0.322, bend/libration -0.143, compensation C = 0.444 (frozen F01 O-H strong regime: 0.13 to 0.15, stretch 0.28 to 0.31, C 0.50 to 0.56).
* mace (n = 7): total 0.153, stretch 0.310, bend/libration -0.157, C = 0.506.
* mattersim (n = 8): total 0.196, stretch 0.333, bend/libration -0.137, C = 0.411.
* orb (n = 6): total 0.186, stretch 0.324, bend/libration -0.138, C = 0.425.

## Caveats

* Harmonic, fixed geometry, three ML potentials; rows share structures and models and are not independent. No polymorph isotope free energy in this set has been measured.
* The pairs are new to the calculation, not to the authors in every case: the atlas (P08) had given MP-geometry signs for them, and Al(OH)3 and H2O occur in the frozen F01 population. Most primary pairs are KH2PO4 and ice polymorphs (P10 section 3), so the formula count, not the row count, measures breadth.
* This addendum does not change the frozen headline; a contradiction is only reported here (decision 08, What would change this, item 5).
