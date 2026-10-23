# Response to referees, round 1

Manuscript: "A short-bond rule for the isotope effect on polymorph stability in hydrogen-bonded crystals" (`docs/paper/main.tex`). Reports: `round1_opus.md` (Claude Opus 5.5) and `round1_gpt-6-astra.md` (GPT-6 Astra, in Turkish). `round1_gemini-4-argon.md` contains no report; the Gemini run failed at authentication.

Scope of this revision: everything that can be done with existing repository data. No new DFT, PIMD, SSCHA or GPU runs were made; those items are listed at the end. New statistics are computed by `src/isoshift_event/paper_stats.py` from the frozen tables into `results/paper_stats.json`, and the new Fig. 5 (`docs/paper/figures/fig6_accuracy.png`) comes from the same script. Section numbers below refer to the revised `main.tex`. The frozen headline sentence of decision 07 is unchanged; the revision adds units, uncertainties and comparisons around it.

Status key: done, partly, not done (with reason).

## Referee 1 (Claude Opus 5.5)

### Numeric checks (report section 2)

| Item | Status | Change |
|---|---|---|
| 15, MatterSim mp-985293 compensation upper bound 1.02 | done | Sec. III B now 0.95 to 1.02 (`paper_stats.json` `mp985293`: 1.0247) |
| 16, partner volume minimum 7.53 | done | Sec. III B "7.53 to 7.88 for its headline partners" (7.535) |
| 25, one-mode estimate 4 to 34% high | done | Sec. III H, Conclusion (`analytic.ratio_min/max` 1.04, 1.342) |
| 26, 1/√2 overstatement 8% | done | Sec. III H: about 8% for the zero-point shift, about 6% for the high-T slope (also Astra item 32) |
| 33, "every reported number from three MLIPs", 572 vs 569 | done | Sec. II C reworded: SevenNet enters only as sign votes and in labelled pipeline counts; Sec. II D gives 569 (three models) and 572 (with SevenNet); brucite and LiH ranges restated for the three models at room temperature (+0.19 to +0.33%, +1.03 to +1.27%) |
| `results/F01_rule_fit.json` stale | done | `results/F01_rule_fit.SUPERSEDED.md` added; JSON kept unchanged |

### Major issues

**M1, statistical unit.** Done. (a) Structure-level fit with formula fixed effects: 0.120 (0.072 to 0.160), 0.116 (0.087 to 0.153), 0.126 (0.091 to 0.163) (Sec. III A, Table I). (b) Formula majority 27 of 28 and pair majority 74 of 84 now lead the abstract, Sec. III B and the conclusion; 89 structures, five formulas with 129 of 212 rows stated in Sec. III B. (c) Formula-clustered bootstrap intervals for slopes (0.068 to 0.154, 0.083 to 0.165, 0.090 to 0.169) and accuracy (pooled 0.68 to 0.98; formula-equal-weight 0.92, interval 0.85 to 0.98, baseline 0.49). The text says 0.11 to 0.13 is the model spread. (d) Theil-Sen 0.061, 0.111, 0.109; leave-one-formula-out range; O-H-only slopes; Al(OH)3 share of MACE rows (43 of 188).

**M2, baselines.** Done. Orientation stated (a = lower database energy, so the baseline means "deuteration destabilises the higher-database-energy polymorph"). Orientation-invariant pair-level null: mean 106, sd 10.7, maximum 154 in 2×10^5 draws, p < 10^-5 (stated as describing the arrangement, not a sampling probability). Density rule 104 of 212; MLIP static energy order 137; O...O sign 183 of 211 against 184 for O-H on the same rows (r = -0.80), with directions also chosen in training folds. The earlier sentence "the structure-only O...O rule is weaker" is replaced: the two descriptors are equivalent in sign on the same rows (Sec. III B, Discussion).

**M3, no anharmonic or quantum control.** Not done: requires new PIMD or SSCHA runs. The limitation is stated more sharply (Discussion, limitation 1, including that D is evaluated at the H geometry) and the missing controls are named with references (Ceriotti and Markland 2013, Cheng and Ceriotti 2014, Monacelli et al. 2021). Listed under new compute.

**M4, no higher-level reference for ΔΔF.** Not done: requires DFT phonons on a pair subset. The benchmark errors are now compared with the median signal (Sec. II C), and the missing DFT double difference is in the limitations and the conclusion. Listed under new compute.

**M5, accuracy against effect size and model spread.** Done. |ΔΔF| ≥ 1 meV/H: 151 of 159; below: 34 of 53; models disagree in sign in 19 of 74 multi-model pairs; median spread 1.36 against median |ΔΔF| 2.37 meV/H; normalised by spread: 81 of 81 above two spreads, 42 of 43 between one and two, 53 of 78 below one; flagged 17 of 42, unflagged 168 of 170 (Sec. III B, new Fig. 5b). The referee's median spread (1.26) differs from ours (1.36, max minus min per pair); we quote ours with its definition in `paper_stats.json`.

**M6, prospective test.** Done. Abstract and conclusion state the failure; conclusion gives 16 of 111, 16 of 24 against 19, pair majority 5/1/4; Sec. IV notes that the clean filter selects ordered oxyhydroxides and hydroxides close to the training population, and Sec. III B notes the weight of five formulas.

**M7, weak side.** Done. Sec. III E reframed as a reversal at modest confidence: 18 of 20 reversed, 12 of 13 pairs and 6 of 7 formulas wrong by majority, negative slopes in all three models, prospective weak side 2 of 9, linked to Li, Walker and Michaelides and McKenzie et al.; NaOH linked to Schaack et al. 2023. Abstract mentions it.

**M8, analytic estimate partly circular.** Done. Sec. III H renamed "An analytic explanation within the same models"; circularity stated; experimental dν/dr not used; 4 to 34%; the estimate does not explain the 153 to 185 rise, stated in Sec. III H and the conclusion. An experimental dν/dr(O-H) (e.g. Steiner 2002) was not added because no such source is in the repository or verified here.

**M9, δ-AlOOH reality check.** Partly. Abstract now conditional and exploratory. Sec. III I reports the QHA isotope term at 10, 15, 20 GPa (MACE 2.30, 2.42, 2.22; ORB 1.86, 2.30, 2.50 meV/atom) against 0.77 and 0.83 at 0 GPa, and links the growth to H-bond strengthening. Model transition pressures 8.76, 13.00, 15.14 GPa stated as 4 to 6 GPa apart and not compared with experiment; Ohtani et al. 2001, Tsuchiya et al. 2002 and Sano-Furukawa et al. 2008 are cited. Not done: O-H and O...O against pressure (not stored; needs recomputation), symmetrisation check inside the grid, and a quantitative comparison with the experimental boundary (no primary source read).

**M10, feasibility of the direct experiment.** Partly. Conditional conversion with R = 0 at each model's transition pressure: 265 to 363 per mil at 300 K, 66 to 90 per mil at 1000 K (Discussion, `paper_stats.json` `alooh`), labelled not a prediction. Comparison with SIMS/NanoSIMS precision not done: no source in the repository; stated as not assessed. R not bounded (needs dilute-D supercell calculations).

**M11, novelty.** Done. Introduction and Discussion now say the direction follows from Bigeleisen-Mayer, Urey and McKenzie-type arguments, that the rule reduces to the force-constant trace at high T (211 of 212), and that the contribution is the quantification and its limits. Crawford et al. 2009 (pyridine), Ubbelohde and Gallagher 1955 and Koval et al. 2002 (KDP) added.

**M12, model independence and SevenNet cut.** Partly. Pair and formula counts lead; pooled 185/212 kept in brackets because decision 07 freezes it. SevenNet cut explained with numbers (15.3% vs MACE 12.8%) and described as a tolerance choice, not a physical criterion (Sec. II C). SevenNet is not added to quantitative claims (it has 23 clean rows, too few for a slope claim).

**M13, forking paths.** Done. Multiverse in Sec. III B and `paper_stats.json` (`multiverse`): r_min 138/144 (baseline 100), mean 177/188 (114), O...O regime 185/222 (141), eligibility 3 mÅ 203/232 (141), 10 mÅ 165/188 (120), and 0, 600, 2000 K. 250 and 350 K are not available (free energies stored only at 0, 300, 600, 2000 K).

### Minor issues

1. X-H vs O-H definition: done (Sec. II D; 41 non-O-H rows, X = B, N, P or F; O-H-only slopes in Sec. III A).
2. Table I format: done (ratios throughout, pair and formula counts, intervals, Theil-Sen, structure-level slope).
3. Numeric fixes: done (see table above).
4. Three-MLIP sentence: done.
5. MDR citation; uncited Petretto and Torresi: done for MDR (Togo et al. 2023, Loew et al. 2025). Petretto and Torresi are in `refs.bib` but not cited; revtex prints only cited entries, so they do not appear.
6. Normalisation: done (Sec. II A states per H unless labelled meV/atom).
7. Imaginary modes in Eq. (2): done.
8. Quadrature error and eigenvectors: partly. Eigenvectors at each mass stated. The quadrature test against the direct difference is the clean criterion (0.01 meV/atom); a separate quadrature-error figure is not added.
9. Mesh density and sensitivity: partly. Density stated; screen-wide mesh sensitivity not tested (needs recomputation), FeOOH card value quoted.
10. SevenNet population: done.
11. PBEsol donors in Fig. 3 window: done (caption: one donor in the window).
12. 0 K unflagged count: done (153 of 170).
13. F04 stretch sign: done (Table II "stretch sign not determined").
14. Ubbelohde direction: done (Discussion).
15. Commit hash for the paper version: done in words (branch post-hackathon at the commit that adds the manuscript); the hash is in the commit message history.
16. AI workflow in Methods: done (Methods G trimmed; detail kept in the AI-use statement).
17. Title: not done. The title is the author's decision; the abstract and introduction now state the scope (carbon-free inorganic pairs, harmonic models).
18. to 21. Figures: partly. Captions of Figs. 1, 2 and 4 corrected (neutral reading of the Fig. 1 title, inset population, panel naming left/middle/right, window n, unexplained donors). Fig. 2 pipeline chart removed from the paper; counts are given in the text. Regenerating Figs. 1, 2 and 4 (capitalised model names, panel letters, binned means, Å label) is not done in this round because it means editing the repository figure scripts that produced the submitted figures; listed as a TODO.

### Missing references (22 to 38)

All 17 were checked on Crossref by us on 23 October 2026 (title and authors match) and added: Crawford 2009, Ubbelohde 1955, Urey 1947, Ceriotti and Markland 2013, Cheng and Ceriotti 2014, Ceriotti et al. 2016, Markland and Ceriotti 2018, Rossi et al. 2016, Kapil and Engel 2022, Kapil et al. 2019, Monacelli et al. 2021, Koval et al. 2002, Limbach et al. 2009, Sano-Furukawa et al. 2008, Ohtani et al. 2001, Tsuchiya et al. 2002 (Crossref gives no page or article number; none is printed), Loew et al. 2025. All are cited in the text.

### Abstract (report section 5)

1. Unit: done (pairs and formulas lead). 2. Precision: done (clustered interval in the abstract). 3. Undersold points: weak-side reversal and effect-size reliability added; the high-T trace result is in Sec. III G and the Discussion but not in the abstract (word limit). 4. Failures and prediction: prospective failure stated; AlOOH sentence marked exploratory and quasi-harmonic. The detailed prospective numbers are in the conclusion.

## Referee 2 (GPT-6 Astra)

**Numeric table.** Item 32 (7% for 1/√2): done (8% and 6%). Item 33 (10^-9 as approximate): the text says "to 10^-9 meV/atom", which we keep as approximate (1.0×10^-9). F01_rule_fit.json: done (superseded note).

**A, clean criterion vs physical stability.** Partly. New Sec. III D reports the subset with converged relaxations (86 of 93, pairs 45/7/0) and with converged relaxations and no imaginary modes (35 of 36, pairs 27/0/1, 9 formulas), with slopes, from the per-structure screen records; flag counts on headline rows given (119 relaxation-not-converged, 161 soft-mode; the referee reports 103 relaxation-not-converged rows; our join of the 212 headline rows to `screen_pairs_refined.csv` gives 119, and we could not reproduce 103; ours is in `paper_stats.json` `flags_headline_rows`). Not done: per-structure final stress and imaginary-mode eigenvectors, minimisation along soft modes (needs recomputation).

**B, MLIP validation does not test the target observable.** Partly. Benchmark errors compared with the signal; model-relaxed-geometry benchmark not added to the text (the DFT-geometry values are the ones in the paper; the relaxed-geometry values are in `results/benchmark/summary.csv`). Direct DFT ΔΔF on a preselected subset: not done (new compute).

**C, anharmonicity.** Not done (new compute). Markland and Berne 2012 added and cited; the scope is stated as "within these harmonic models" throughout.

**D, statistical unit.** Done (as Opus M1): formula-clustered bootstrap, formula-equal-weight accuracy, leave-one-formula-out slope change, high-|Δ| influence via Theil-Sen. The referee's 98/212 for AlOOH, FeOOH and Al(OH)3 matches our 39 + 31 + 28.

**E, post hoc boundary.** Done. Accuracy-coverage curve (Fig. 5a), multiverse, statement that 183/210 and 185/212 are not directly comparable, "empirical region of these model geometries", and the Discussion limitation no longer says the selection effect is small.

**F, baseline and same-population comparison.** Done (as Opus M2). Orientation defined; same-row comparisons; training-fold direction choice. A free-intercept fit was not added as a separate competitor; the leave-one-formula-out line fit is in `results/F01_cv.json` (`strong_regime_cv`).

**G, prospective test in the conclusions.** Done. Precommitted baseline (5/24) separated from the after-the-fact constant (19/24) in Sec. IV and Table II; pair majority given; the conclusion says transfer is not shown.

**H, analytic estimate.** Done (as Opus M8). Language changed to "explanation within the same models"; the two fitted populations are named. A same-population, same-weighting comparison was not computed (needs per-donor stretch weights in the regression; possible with existing data but not done in this round).

**I, Libowitzky check as an error bound.** Done in wording: the 150 to 400 cm^-1 range is "not a confidence interval", the 1.9 to 2.3 sign-change ratio is conditional on the bend term, no angle criterion is stated, unexplained donors are noted in the Fig. 3 caption. Verification of periodic acceptor geometry: not done.

**J, AlOOH presentation.** Partly (as Opus M9). Abstract conditional; denser pressure grid, EOS sensitivity and ΔV at pressure not done (new compute).

**K, trace vs full substitution.** Done in wording: +359 per mil replaced by a labelled conditional conversion (265 to 363 per mil); R is conditional; single-D supercell calculations not done (new compute). The abstract says partitioning "would test it" with the conditions in the Discussion.

**L, novelty.** Done (as Opus M11); the ROY case is described as crystallisation selection, distinct from the equilibrium quantity computed here (Introduction).

**Minor.** Scope in title: not done (author decision), scope in abstract and introduction: done. Methods detail (mesh, supercells): partly (mesh rule stated; symmetrisation and sum-rule handling not described). Mode notation (mass-weighted eigenvector, sum over H): done. Symbol clash f: done (compensation is C throughout; f only for the Libowitzky ratio). Units and V_H/V_D definition: done. Analytic precision (5×10^-5): done (now "within 1.5×10^-4 relative"). Figures: partly (see Opus 18 to 21). New mp-985293 temperature figure: not done. F12 same-temperature values 42.5, 30.3, 41.3 per mil and 2 vs 4 kbar: done. Secondary experimental sources: stated in Sec. IV. Reproducibility: force constants not in the repository, stated in Data availability. AI workflow length: done.

**Missing references.** Markland and Berne 2012, Schaack et al. 2023, Urey 1947, Liu, Tossell and Liu 2010 checked on Crossref and added; Lee et al. updated to the published Materials Today Physics 53, 101688 (2025).

## Items that need new computation (not done in this revision)

1. Path-integral mass thermodynamic integration or SSCHA on 3 to 5 headline pairs (diaspore/δ-AlOOH, boehmite/diaspore, one mp-985293 pair, one large-Δ pair), and the deuteration-induced change of mean O-H.
2. DFT (PBE and a functional with better H-bond energetics) double differences on a stratified subset including mp-985293 pairs and the AlOOH pair; common-geometry vs separately relaxed comparison.
3. Re-relaxation of unconverged structures, minimisation along soft modes, per-structure final stress and imaginary-mode eigenvectors.
4. q-mesh convergence of ΔΔF across the screen.
5. AlOOH: denser pressure grid, EOS sensitivity, ΔV at pressure, O-H and O...O against pressure, symmetrisation check.
6. Dilute single-D supercells to bound R for AlOOH.
7. Free energies at 250 and 350 K for the multiverse.
8. Regenerated Figs. 1, 2 and 4 with corrected labels (no new physics; needs edits to repository figure scripts).
