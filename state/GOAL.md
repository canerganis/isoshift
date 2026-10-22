# GOAL (Can, 21 Oct 20:30; historical wording, superseded for submission by decision 05): a real scientific discovery, shown with evidence a materials scientist accepts

Submit by Fri 23 Oct 00:30 TRT (hard stop 02:00). Every work decision is checked against this file; the conductor updates the status column after each step.

## Submission headline (decision 07 after the compute freeze; replaces decision 05's)
"Across 220 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.11 to 0.13 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds, chosen after inspecting the data), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (84 pairs, 28 formulas), against 131 of 212 for a constant-sign baseline fitted on leave-one-formula-out training folds. By model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293."

## Success criteria (all must hold to use the headline; otherwise fall back as noted)
| # | Criterion | Evidence | Status |
|---|---|---|---|
| S1 | Physics validated on measured isotope effects | brucite 4/4, LiH 4/4 (01-gate) | done |
| S2 | Rule holds in >= 3 separate MLIPs with consistent slope | F01: slopes 0.11/0.12/0.13 meV/H per mÅ, r 0.76 to 0.84 (frozen, MACE/ORB/MatterSim) | done (SevenNet in sign votes only) |
| S3 | Rule transfers to unseen chemical families (O-H solids, formula holdout) | strong regime (pair max mean O-H >= 0.99 Å): O-H 185/212 (84 pairs, 28 formulas) vs fold baseline 131/212; pairs 74 right, 0 ties, 10 wrong, all 10 containing mp-985293; nested threshold re-choice 183/210 (1.00 Å in 30 of 31 folds); weak regime fails (2/20); database-geometry pre-screen r 0.65 (pre-freeze run) | done, regime-limited (decision 07); 22 Oct: F11 prospective test FAIL (post-freeze), transfer to new pairs not shown |
| S4 | Blind test against measured H/D data, predictions committed first | F02: hydrides and brucite right sign, strong-H-bond oxyhydroxides wrong (low-quality data); F03: stretch-geometry relation matches measured spectra (Libowitzky) in all 3 MLIPs | done, mixed; does not test F01 (decision 04) |
| S5 | Mechanism explained and tied to prior theory | stretch +0.25 vs bend/libration -0.13 meV/H per mÅ screen-wide (O-H strong: +0.28 to +0.31 vs -0.15 to -0.17); McKenzie 2014/2015 | done |
| S5b | Stretch ingredient anchored in experiment | F03: For O-H donors with model O...O distances of 2.50 to 2.80 Å, the harmonic Γ-point stretch frequencies follow the slope of the empirical Libowitzky ν(OH) vs O...O correlation with slope ratios of 0.91 (MACE), 0.92 (ORB) and 0.92 (MatterSim), structure-bootstrap 95% intervals 0.67 to 1.07, 0.82 to 1.01 and 0.81 to 1.02 (`results/stretch_check_summary.json`). Above 2.80 Å the ratios are 0.67, 2.61 and 1.46, so ORB and MatterSim are too steep there, and the F01 strong regime reaches O...O of about 2.93 Å. This is a consistency check on the stretch term, not a validation of isotope free energies. | done |
| S5c | Compensation (bend/libration) term tested against experiment | F04: goethite -> epsilon-FeOOH SUPPORT (stretch -261 vs -273 predicted, bend +290 vs +195), diaspore -> delta-AlOOH INCONCLUSIVE (no IR stretch in delta-AlOOH) | done, sign-level consistency (1 pair); P03 inconclusive |
| S6 | Survives a multi-model red team (final-claims board) | docs/decisions/05-final-claims.md: no blocking flaw, claims narrowed | done, see 05 |
| S7 | One concrete experimental prediction on a real material | CARD-AlOOH: dP_iso(diaspore -> delta-AlOOH) = +1.13 (ORB) and +1.33 GPa (MACE), QHA 10-20 GPa, 300 K | done, exploratory sign prediction (2 models) |

Fallbacks: S4 fails -> claim the rule as a computational result with the blind miss reported; S6 finds a blocking flaw -> P10(c) negative-result framing plus validated volume isotope effects and benchmark.

## Remaining plan (owner Opus unless noted; superseded by the action list in docs/decisions/06-strategy-to-submission.md)
1. Compare P01 blind predictions with measured values (S4); write docs/findings/F02-blind-test.md.
2. NaBH4 tetragonal to Pnma pressure shift prediction, then compare (S7 option).
3. SevenNet results in (GPU chain), rerun refine/decompose/analysis/rule_cv; update F01 numbers.
4. Apply the rule structure-only to all H polymorph pairs (database map) and the real-phase candidate card (S7).
5. Final-claims board (Opus, Astra, Gemini) on F01, F02 and the candidate card (S6).
6. Freeze compute Thu 12:00. Figures final, README results, write-up, video script final (story centred on F01).
7. Can: public repo go-ahead, video recording Thu ~19:00, Moment submission.
