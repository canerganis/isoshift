# Compute freeze report (22 Oct, run 02:25 to 02:50 TRT)

**Result: trigger fired.** Under the freeze rule in `state/LEDGER.md` ("Freeze rule (council 06 item 6)"), a unique-pair model majority is now wrong for 10 O-H strong-regime pairs. No claim wording was changed and no placeholder was filled. The wording goes back to the council chair.

## What was run

All CPU only (`CUDA_VISIBLE_DEVICES=""`, `OMP_NUM_THREADS=4`), once each. Logs are in `results/freeze/`.

| Step | Command | Log |
|---|---|---|
| 1 | `python -m src.isoshift_event.screen collect --models mace,orb,mattersim,sevenn` | `01_collect.log` |
| 2 | `python -m src.isoshift_event.refine --workers 6` (2009 structure-model results, 0 unmatched; 1616 pairs checked, 229 same relaxed phase) | `02_refine.log` |
| 3a | `python -m src.isoshift_event.analysis --screen-pairs results/screen_pairs_refined.csv --pairs data/isoshift/pairs.csv --output results/candidates.csv` | `03a_analysis_clean.log` |
| 3b | the same with `--screen-structures results/screen_structures_extended.csv --output results/candidates_extended.csv` | `03b_analysis_extended.log` |
| 4 | `python -m src.isoshift_event.decompose --workers 6 --models mace,orb,mattersim,sevenn` (1310 structures, 1314 pair rows) | `04_decompose.log` |
| 6 | `python -m src.isoshift_event.stretch_check` (full recompute) | `06_stretch_check.log` |
| 5 | `python -m src.isoshift_event.rule_cv`, then `python -m src.isoshift_event.rule_oo` | `05a_rule_cv.log`, `05b_rule_oo.log` |
| 7 | `python -m src.isoshift_event.fig_rule`, `python reproduce_figures.py` | `07a_fig_rule.log`, `07b_reproduce_figures.log` |

Screen inputs: mace 606, orb 606, mattersim 605 (1 failed), sevenn 192 of 192, so SevenNet enters under the rule.

Two deviations from the requested order and code, both deliberate:

* `stretch_check` ran before `rule_cv` and `rule_oo`. `rule_cv.load()` takes its O-H mask from `results/stretch_check.csv`, and `stretch_check` builds that file from `results/decompose_structures.csv`. In the requested order, the O-H mask would have come from the pre-freeze decompose. The O-H structure set grew from 184 to 192.
* `rule_cv.py` now limits every existing block to MACE, ORB and MatterSim (`QUANT_MODELS`), which is how it ran before the freeze, when decompose had only those three models. It also adds one separately labelled block, `sevenn_sign_votes`, as the freeze rule and decision 01 G1 require. `rule_oo.py` and `fig_rule.py` panel 3 call `rule_cv.load()` and therefore stay on three models. `fig_rule.py` panels 1 and 2 plot every model in `decompose_pairs.csv`, so SevenNet now shows there with its own colour, which the code already defined. `stretch_check` windowed slopes and `rule_oo` threshold translation are hardcoded to three models and were left that way, since they feed quantitative claims.

## Headline numbers, before and after

"Before" is the committed state at 64d7e84, recomputed from the snapshot files. "After" is the frozen `results/F01_cv.json`, `results/F01_oo.json`, `results/decompose_pairs.csv` and `results/stretch_check_summary.json`. Headline rows are three models (MACE, ORB, MatterSim). SevenNet appears only where labelled.

| Number | Before | After | Changed |
|---|---|---|---|
| O-H strong, no target cut (`oh_unfiltered_strong`) | 123/130 (94.6%) | 185/212 (87.3%) | yes |
| Training-fold baseline | 82/130 (63.1%) | 131/212 (61.8%) | yes |
| Pairs, formulas | 67, 23 | 84, 28 | yes |
| Per model | MACE 51/57, ORB 56/56, MatterSim 16/17 | MACE 52/68, ORB 64/73, MatterSim 69/71 | yes |
| Unique-pair majority (right/tie/wrong) | 62/5/0 of 67 | 74/0/10 of 84 | yes, **trigger** |
| O-H, no threshold | 124/146 (85%) | 187/232 (81%) | yes |
| Weak side | 1/16 | 2/20 | yes |
| All covalent, signal cut, strong (old app headline) | 128/134 (baseline 84) | 188/214 (baseline 134) | yes |
| No threshold, all covalent, signal cut | 129/150; formula majority 23/5/2 | 190/234; formula majority 29/4/0 | yes |
| Nested threshold re-choice, O-H no cut | 123/130, 0.99 Å in every fold | 183/210; 1.00 Å in 30 of 31 folds, 0.99 Å in 1 | yes |
| Pairs in the screen and slope fit (`unique_pairs`) | 197 | 220 (223 with SevenNet) | yes |
| Clean covalent rows per model | MACE 177, ORB 121, MatterSim 43 | MACE 188, ORB 163, MatterSim 170 | yes |
| Screen-wide all-row slope (meV/H per mÅ) | 0.116 / 0.120 / 0.147, so "0.12 to 0.15" | 0.112 / 0.117 / 0.128, so "0.11 to 0.13" | yes |
| Screen-wide compensation | 52 / 52 / 43%, "43 to 53%" | 54 / 55 / 49%, "49 to 55%" | yes |
| O-H strong total slope | 0.140 / 0.144 / 0.151 | 0.132 / 0.136 / 0.147 | yes |
| O-H strong compensation | 0.50 / 0.53 / 0.41, "41 to 53%" | 0.52 / 0.56 / 0.50, "50 to 56%" | yes |
| O...O predictor, translated strong regime | 127/153 (83%) vs 98/153 (64%), O...O ≤ 2.92 Å | 187/241 (78%) vs 147/241 (61%), O...O ≤ 2.93 Å | yes |
| F03 stretch slope ratio f_OLS (2.50 to 2.80 Å) | 0.91 / 0.95 / 0.91 | 0.91 / 0.92 / 0.92 | ORB and MatterSim |
| Candidates eligible, clean / extended tier | 4 / 60 | 2 / 40 | yes |

Model order in every triple is MACE / ORB / MatterSim.

SevenNet line (`sevenn_sign_votes`, sign votes only): 23 clean covalent rows. It is 10/10 alone on the O-H strong population (baseline 7/10), with no weak-side rows. Adding it as a fourth vote gives 195/222 (baseline 138), with pairs 75 right, 0 ties and 10 wrong. Its strong-regime slope (0.102, compensation 0.65, n 13) is reported in the JSON, not claimed.

What changed it: SevenNet adds only 10 headline rows, all right. The change comes from the completed MatterSim and ORB queues. After the freeze collect, refine and decompose, 82 new three-model rows enter the headline population: MatterSim 54, ORB 17, MACE 11. The old 130 rows are unchanged: 123/130, and their 67 pairs now split 62 right, 5 ties, 0 wrong.

## Trigger check (O-H strong regime, `oh_unfiltered_strong`, three models)

| Trigger | Threshold | Frozen value | Fires |
|---|---|---|---|
| Accuracy | below 85% | 87.3% (185/212) | no |
| Margin over fold baseline | under 20 points | +25.5 points (87.3% vs 61.8%) | no |
| Any unique-pair model majority wrong | any | 10 wrong of 84 (four-model vote: 10 wrong of 85) | **yes** |

Diagnosis for the chair (no wording changed):

* All 10 wrong pairs share one structure, mp-985293, an Al(OH)3 polymorph listed by the Materials Project as experimental (theoretical=False; the pair-level theoretical, soft-mode and classical-limit flags come from its partners; it has no imaginary modes in any model). Its mean model O-H is 0.996 Å (MACE), 0.997 Å (ORB) and 0.999 Å (MatterSim), just above the 0.99 Å boundary. MACE and ORB call all 10 wrong. MatterSim gets 8 of 9 right, with small values (|ΔΔF| ≤ 0.26 meV/H).
* These pair rows were absent before the freeze, because ORB and MatterSim had not run on mp-985293. In `results/screen_pairs_refined.csv` the rows carry `theoretical`, `soft_mode_bracketed`, `classical_limit_violation` and, for ORB, `relax_not_converged`. The `clean` flag in `decompose.py` tests only the quadrature check, so none of these flags removes them.
* Dropping the pairs that contain mp-985293 gives 177/184 (96.2%), with pairs 74 right, 0 ties, 0 wrong. Raising the boundary to 1.00 Å gives 175/182 (96.2%, 73 pairs). 28 of the 30 evaluations between 0.99 and 1.00 Å are mp-985293. This is also why the nested re-choice now picks 1.00 Å in 30 of 31 folds. As a result, the sentence "re-choosing it inside each fold selects 0.99 Å in every fold" is false on the frozen numbers.
* Both repairs are post hoc and would be chosen after seeing the frozen data. That choice belongs to the chair, not to the freeze run.

## Not done because the trigger fired

* No double-brace placeholder was filled, and README.md, docs/story/writeup.md, docs/findings/F01-xh-length-rule.md, state/GOAL.md and app/ were not edited. The decision 06 grep gate for double braces still finds the video script placeholders, the three SEVENN slots in the writeup and the literal gate string in decision 06 and docs/AUDIT.md.
* `fill_placeholders.py` was drafted but not committed. Its value map is ready for whatever population the chair rules on.
* `figures/fig4_xh_rule.png` panel 3 now shows the frozen 185/212 and 2/20, matching the JSON. The README and story texts still say 123/130, so the figure and the text disagree until the chair decides.
