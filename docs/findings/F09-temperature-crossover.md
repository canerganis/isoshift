# F09. Temperature-resolved F01 and the mp-985293 crossover: H2, H3, H4 pass, H1 fails

**Status: post-freeze addendum.** The frozen F01 headline of decision 07 (185 of 212, baseline 131, pairs 74 right, 0 ties, 10 wrong) is unchanged. Predictions and rules: `docs/predictions/P09_temperature.md`, commit d03f8d2 (22 Oct 10:11), pushed before any file existed in `results/post_freeze/`. Scoring code: `src/isoshift_event/f09_temperature.py`. Output: `results/post_freeze/F09_temperature.json`, decompose runs in `results/post_freeze/T0`, `T300`, `T600`.

## Verdict

| Hypothesis | Rule (P09, unchanged) | Result | Verdict |
|---|---|---|---|
| H1 compensation shrinks with T | C(600 K) < 0.6 C(0 K) in ≥ 80% of eligible rows | 98 of 212 (46%); MACE 33/68, ORB 32/73, MatterSim 33/71. Median C: 0.665 (0 K), 0.582 (300 K), 0.406 (600 K); median ratio 0.61 | **FAIL** |
| H2 mp-985293 reversal sits in bend/libration | all 28 rows: stretch term has the F01 sign at 0 and 600 K, C(0 K) > 1, C(600 K) < 1 | 28 of 28 on every clause | **PASS** |
| H3 product rule (numerical gate) | max per-H deviation ≤ 1e-3 at every q, both members of the 10 mp-985293 pairs, every model | 31 structure-model cases, 0 failures, max 2.6e-11 per H (all 224 headline structure-model cases: max 2.3e-9) | **PASS** |
| H4 high-T trace limit | sign(ddF(2000 K)) = -sign(Δ Tr K_H) in ≥ 202 of 212 rows | 211 of 212 (MACE 67/68, ORB 73/73, MatterSim 71/71); the one miss is mp-754004__mp-768422 (MACE, ddF(2000 K) = -0.008 meV/atom) | **PASS** |

Regression: `decompose.py --T 300 --out-dir results/post_freeze/T300` reproduces the frozen `results/decompose_pairs.csv` in 1314 of 1314 rows with max |Δ ddF_total| = 0 meV/atom (tolerance 1e-9). The frozen files are byte identical.

## What this says

* **The 10 wrong pairs are a temperature effect, not a numerical artefact (H2, H3).** In all 28 mp-985293 rows the stretch term alone has the F01 sign at both 0 and 600 K. What flips the total is the bend and libration share: it outweighs the stretch at 0 K (C > 1) and no longer does at 600 K (C < 1). The product rule holds to 1e-11 per H, so missing or spurious modes do not explain it.
* **Crossover temperatures (descriptive, 25 K grid, not predeclared).** MACE 431 to 506 K, ORB 317 to 406 K, MatterSim below 300 K in 8 of 9 rows and 318 K in the ninth (mp-985293__JVASP-29795). The model spread is large: the crossover is a model-dependent number, not a measured one.
* **High-T limit confirmed (H4).** At 2000 K the sign follows the on-site H force-constant trace in 211 of 212 rows, and in all 212 rows the larger trace sits in the shorter O-H phase. This is the textbook Bigeleisen-Mayer limit; it is expected, not new.
* **The simple mechanism H1 does not hold as stated.** Compensation does fall with temperature on average (median 0.67 to 0.41), but fewer than half the rows fall by the predeclared 40%. So we do not claim that "zero-point energy gives bending and libration more weight than heat" explains the whole set. Decision 08 action 9 therefore allows the first video sentence and forbids the causal clause.
* **Accuracy by temperature (recomputed from the new decompose runs, same 212 rows):** 153 at 0 K, 185 at 300 K, 210 at 600 K. F01 is a thermal rule; at 0 K it is close to its baseline (145, decision 08). A 600 K value is the harmonic isotope term at fixed 0 K geometry, not a statement about phase stability (gibbsite and many hydrates decompose below 600 K).

## Disclosure

The scoring script was run twice. The first run (22 Oct 10:34) gave H4 124 of 212 (fail); the H4 code in `f09_temperature.py` was then changed by the previous conductor session and the script rerun at 10:38, giving 211 of 212. The file was untracked at the time, so the first version is not in git; the committed code is the one that produced the second run, and its on-site lookup (`fc[row, s_]`, primitive row index for compact arrays, supercell index for full arrays) is the standard phonopy layout. The hypothesis text, threshold and row set did not change; H1, H2 and H3 gave the same verdicts in both runs. The JSON in the repo is the second run. A reader should weigh H4 knowing it was scored after a code fix that the first result prompted.
