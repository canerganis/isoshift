# 07. Freeze wording: mp-985293 stays in the headline at 0.99 Å; the pair count, its one counterexample structure and the Al(OH)3 fold go into the claim; "no pair is called the wrong way" and "0.99 Å in every fold" are withdrawn

Chair: Opus, 22 Oct. Members: Opus, Astra, Gemini 4 Argon (rounds 1 and 2, all answered). Weighed by argument, not by vote. Trigger: the freeze rule in `state/LEDGER.md` line 74 ("any unique-pair model majority becomes wrong") fired in `docs/freeze/FREEZE_REPORT.md`. Every number below was recomputed by the chair with `chair07.py` (session scratchpad, full path at the end) through `rule_cv.load()` on the frozen `results/decompose_pairs.csv`, plus direct reads of `results/F01_cv.json`, `results/F01_oo.json`, `results/stretch_check_summary.json`, `results/screen_structures.csv`, `results/stretch_check.csv`, `results/screen_pairs_refined.csv`, `data/isoshift/experimental.csv` and `data/isoshift/mp_h.csv`.

This decision amends 05 and 06 as a dated addendum. Their bodies stay as the historical record; each gets a one-line pointer to this file. Where 05 or 06 and this file disagree, this file governs.

## Decision

1. **mp-985293 stays in the headline.** No justification for treating it differently exists that does not depend on its outcome. The headline population is unchanged from decision 05: O-H pairs, larger mean model O-H of the pair ≥ 0.99 Å, |Δ mean O-H| ≥ 5 mÅ, no cut on the target. Frozen result: 185/212 (87.3%), 84 pairs, 28 formulas, fold baseline 131/212 (61.8%), unique-pair majority 74 right, 0 ties, 10 wrong.
2. **The boundary stays at 0.99 Å.** Moving it to 1.00 Å now would fit the threshold to the trigger. The nested re-choice (1.00 Å in 30 of 31 folds, 183/210 held out) is reported next to it, with the Al(OH)3 fold (8/28 against a baseline of 19/28).
3. **The pair clause enters the headline itself**, because the trigger that fired is a pair-level one: "by model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293."
4. **The two post hoc repairs (177/184 without mp-985293, 175/182 at 1.00 Å) are locators, not results.** They appear only in F01 details and in a collapsed app expander labelled post hoc. They do not appear in README, the write-up summary, the video, the figure count box or the judge sentence.
5. **No phase name and no mechanism for mp-985293 in submission text.** Argon's identification as high-pressure δ-Al(OH)3 (Matsui et al. 2011) and its "3D framework confinement stiffens bend and libration" explanation are not verified locally and the mechanism is untested. The computed fact is stated instead: bend and libration cancel 95 to 132% of the stretch term in these pairs. Optional action 9 may verify the phase identity for F01 details only.
6. **The freeze report and ledger are corrected:** mp-985293 is not theoretical, MatterSim is 8 of 9, not 8 of 10.
7. **P10(c) negative-result fallback is not triggered.** 87.3% and the nested 87.1% are above 85%; the margin over the fold baseline is 25.5 points.
8. **Decision 05's structure holds:** no discovery wording, same population, same 0.99 Å, F02, F04 and the AlOOH card unchanged.

### Exact sentences (verbatim; use mÅ and Å in files)

**Headline (README, docs/story/writeup.md, F01, state/GOAL.md):**
"Across 220 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.11 to 0.13 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds, chosen after inspecting the data), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (84 pairs, 28 formulas), against 131 of 212 for a constant-sign baseline fitted on leave-one-formula-out training folds. By model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293."

**Statistics and caveat (README, writeup, F01):**
"The 0.99 Å boundary was chosen after inspecting the pre-freeze data and is kept for the frozen result. Re-choosing it inside each leave-one-formula-out training fold picks 1.00 Å in 30 of 31 folds and 0.99 Å only in the fold that holds out Al(OH)3, and gives 183 of 210 held-out evaluations right against a baseline of 131. In that Al(OH)3 fold the rule scores 8 of 28 against a baseline of 19, so a sharp, universal boundary is not established; the cross-validation covers the threshold value, not the choice of regime variable, grid or eligibility cuts. The 10 wrong pairs all contain mp-985293 (P2₁2₁2₁, listed by the Materials Project as experimental, no imaginary modes in any of the three models), whose mean model O-H of 0.996 to 0.999 Å sits just above the boundary while its mean O...O contacts are short (2.77 to 2.82 Å). In these pairs the stretch term has the predicted sign, but bend and libration cancel 95 to 132% of it instead of about half: MACE calls 0 of 10 right, ORB 0 of 9 and MatterSim 8 of 9, with every MatterSim value at |ΔΔF| ≤ 0.26 meV per H. Without any threshold the rule holds in 187 of 232 O-H evaluations (81%). Below the boundary it fails (2 of 20 evaluations, 13 pairs, 7 formulas). In the O-H strong regime the fitted total slope is 0.13 to 0.15 meV per H per mÅ, with bend and libration cancelling 50 to 56% of the stretch slope. A structure-only version using mean O...O ≤ 2.93 Å is weaker (187 of 241 evaluations with |ΔΔF| > 0.1 meV per H, 78%, against 61%). The evaluations share structures and models, the three potentials are separate models, not independent validations, and no polymorph isotope free energy has been measured to test the rule directly."

**SevenNet slot (writeup, F01):**
"SevenNet, used for sign votes only, gets 10 of 10 on the same population (baseline 7 of 10); as a fourth vote the count is 195 of 222 against 138, with 75 pairs right and the same 10 wrong."

**Post hoc locator (F01 details and the app expander only):**
"Post hoc, chosen after seeing the frozen data, and only to locate the failure: leaving out the 10 pairs that contain mp-985293 gives 177 of 184 (74 pairs right, none wrong); raising the boundary to 1.00 Å gives 175 of 182 (73 pairs, none wrong). These are nearly the same intervention, because 28 of the 30 evaluations between 0.99 and 1.00 Å come from mp-985293 (the other 2, both right, from mp-697136__JVASP-54742). Neither replaces the frozen result or the nested 183 of 210."

**Numerical quality (F01 details, writeup_long methods):**
"42 of the 212 headline evaluations carry the stored classical_limit_violation flag, including all 28 that involve mp-985293; mp-985293 itself has no imaginary modes in any model, so the flag on those rows comes from its partners or from flags kept across refinement passes. 17 of the 42 agree with the rule, and the other 170 give 168; this is a diagnostic, not a filter. 'Clean' in this work means that the mass-integral quadrature and the direct isotope free-energy calculation agree within 0.01 meV/atom per structure; it does not certify relaxation convergence, dynamical stability or robustness to the treatment of imaginary modes."

**F03 (replaces decision 05's F03 sentence):**
"For O-H donors with model O...O distances of 2.50 to 2.80 Å, the harmonic Γ-point stretch frequencies follow the slope of the empirical Libowitzky ν(OH) vs O...O correlation with slope ratios of 0.91 (MACE), 0.92 (ORB) and 0.92 (MatterSim), structure-bootstrap 95% intervals 0.67 to 1.07, 0.82 to 1.01 and 0.81 to 1.02 (`results/stretch_check_summary.json`). Above 2.80 Å the ratios are 0.67, 2.61 and 1.46, so ORB and MatterSim are too steep there, and the F01 strong regime reaches O...O of about 2.93 Å. This is a consistency check on the stretch term, not a validation of isotope free energies."

**Decision 05 converged item 4 and the "selection optimism is small" sentence, replaced by:**
"After the freeze, threshold re-choice inside formula folds picks 1.00 Å in 30 of 31 folds because of one Al(OH)3 structure; the fold that holds out Al(OH)3 keeps 0.99 Å and scores 8 of 28 against a baseline of 19. Nested held-out: 183 of 210 against 131. Threshold selection depends on whether the Al(OH)3 failure is in the training fold, so a universal sharp boundary is not established."

**Prior art sentence, last clause, replaced by:**
"The contribution here is the systematic polymorph-stability version of that competition, its slope, and where it holds and fails in three models."

**Judge sentence (replaces decision 06 line 26):**
"In harmonic calculations with three ML potentials, swapping hydrogen for deuterium tips hydrogen-bonded solids toward the polymorph with the shorter O-H bonds in 185 of 212 evaluations where the hydrogen bonds are moderate or strong; all 10 pairs the model majority calls wrong involve one Al(OH)3 structure, and with weak hydrogen bonds the rule fails."

**Organiser sentence (decision 06 line 28):**
"Two days produced a testable, regime-limited computational rule, its failure boundary, one named counterexample and a falsifiable pressure prediction. It is not a confirmed discovery, because this observable has never been measured."

**Decision 06 line 41:** "Short judge sentence. The pair-level count (74 right, 0 ties, 10 wrong of 84, all 10 containing mp-985293) answers the correlated-evaluations objection and names the one counterexample structure."
**Decision 06 line 48:** "`oh_unfiltered_strong`: 185/212 right, 84 pairs, 28 formulas, baseline 131/212."
**Decision 06 line 50:** "Unique-pair majority: 74 right, 0 ties, 10 wrong of 84."

**Video, `docs/story/video_script.md` line 11 (hook):**
"Swap hydrogen for deuterium in a hydrogen-bonded crystal and, in our calculations, it leans toward the polymorph with the shorter O-H bonds. Three machine-learned potentials get this sign in 185 of 212 cases where the hydrogen bonds are moderate or strong, and the rule says where it stops working."

**Video, line 13:**
"We screened 220 polymorph pairs. The isotope free-energy difference follows the change in mean O-H length, 0.11 to 0.13 meV per hydrogen per thousandth of an angstrom. The O-H stretch drives it, and bending and libration cancel about half. Where hydrogen bonds are moderate or strong, deuteration favours the shorter O-H bonds in 185 of 212 model evaluations. A baseline that always guesses one sign gets 131. Counted per pair, 74 are right and 10 are wrong, and all 10 wrong pairs contain the same aluminium hydroxide structure, where bending and libration outweigh the stretch. With weak hydrogen bonds it fails, 2 of 20. We chose that boundary after seeing the data, and we say so."

**Headline figure (decision 06 action 9):**
* Count box: "185/212 evaluations (baseline 131/212); pairs 74 right, 0 ties, 10 wrong (all contain Al(OH)3 mp-985293)".
* Weak side grey, labelled "fails, 2/20".
* The 28 mp-985293 evaluations drawn as open markers in their model colour, kept in every count.
* No threshold line: the x axis is Δ mean O-H, so an absolute bond length has no place on it. Regime is shown by colour against grey.
* Inset: stretch +0.28 to +0.31 against bend/libration -0.15 to -0.17 meV/H per mÅ (`oh_strong_slopes`).
* Caption: "O-H pairs with |Δ mean O-H| ≥ 5 mÅ. Regime by the larger mean model O-H of the pair; the 0.99 Å boundary was chosen after inspecting the data (nested re-choice picks 1.00 Å in 30 of 31 folds). Open markers: evaluations involving Al(OH)3 mp-985293, kept in the counts. Evaluations share structures and models."

**App (`app/isoshift_app.py`):** default banner "185/212 O-H evaluations agree with the rule (87.3%; baseline 131/212). Pair majorities: 74 right, 0 ties, 10 wrong; all 10 involve mp-985293." A collapsed expander titled "Post hoc sensitivity (not the result)" holds the post hoc locator sentence. No toggle that swaps the headline population.

## Why

**Re-checked numbers (chair, `chair07.py`):**

| Quantity | Value |
|---|---|
| Headline (O-H, rmax ≥ 0.99 Å, \|Δ\| ≥ 5 mÅ, no target cut) | 185/212, 84 pairs, 28 formulas; baseline 131/212 |
| Per model | MACE 52/68, ORB 64/73, MatterSim 69/71 |
| Unique-pair majority | 74 / 0 / 10; all 10 wrong pairs contain mp-985293 |
| mp-985293 rows in the headline | 28 in 10 pairs: MACE 0/10, ORB 0/9, MatterSim 8/9; max MatterSim \|y\| 0.255 meV/H |
| Without mp-985293 (post hoc) | 177/184, 27 formulas, pairs 74/0/0 |
| Fixed 1.00 Å (post hoc) | 175/182, 73 pairs, 73/0/0 |
| 0.99 to 1.00 Å band | 30 rows: 28 mp-985293, 2 mp-697136__JVASP-54742 (ORB, MatterSim, both right) |
| Nested CV, O-H no cut | 183/210 vs 131; 1.00 Å in 30 folds, 0.99 Å in 1 (Al(HO)3, 8/28 vs baseline 19/28) |
| No threshold, O-H | 187/232 |
| Weak side | 2/20, 13 pairs, 7 formulas |
| Compensation in mp-985293 headline rows | MACE 1.19 to 1.32, ORB 1.02 to 1.14, MatterSim 0.95 to 1.03; median of other strong rows 0.50 |
| classical_limit_violation in headline | 42 rows, 17 right; all 28 mp-985293 rows; unflagged 168/170 |
| soft_mode_bracketed / theoretical (pair flags) | 161 / 106 of 212 rows |
| Slopes | screen-wide all-row 0.112/0.117/0.128, compensation 54/55/49% (freeze report table); O-H strong 0.132/0.136/0.147, compensation 0.524/0.557/0.498; stretch 0.277/0.308/0.293, perp -0.145/-0.171/-0.146 |
| O...O predictor | 187/241 (signal-filtered, translated strong regime), freeze baseline 147/241 |
| SevenNet | alone 10/10 (baseline 7); four-model 195/222 vs 138, pairs 75/0/10 |
| F03 | f_OLS 0.912/0.922/0.919, CI 0.668 to 1.071, 0.821 to 1.009, 0.811 to 1.015; outer 0.665/2.608/1.462 |

**Why mp-985293 cannot be set aside.** Every candidate reason fails on the local records:
* Provenance: `data/isoshift/experimental.csv` line 20 and `mp_h.csv` record it as experimental (MP theoretical=False). The freeze report's "theoretical" is wrong. The `theoretical` tag on its pair rows is a pair-level flag from partners.
* Dynamics: zero imaginary modes in MACE, ORB and MatterSim (min frequency about -5e-7 THz). The soft-mode and classical-limit flags on its pairs cannot come from it.
* Relaxation: MACE and MatterSim converged (fmax 8.9e-5 and 5.6e-5 eV/Å). ORB did not (6.8e-3), but MACE, which converged, calls all 10 pairs wrong.
* Duplicate: no. 28 atoms, P2₁2₁2₁, 6.79 to 6.94 Å³/atom in the models against 7.54 to 7.88 for every partner.
* Regime membership: borderline only on the rmax ruler (0.996 to 0.999 Å). Its donors span 0.987 to 1.005 Å and its mean O...O (2.77 to 2.82 Å) is shorter than its partners', so on hydrogen-bond geometry it is inside the strong regime, not at its edge.
* No uniform, documented filter isolates it. Filtering on soft_mode_bracketed or theoretical reshapes the whole population and still leaves wrong pairs; classical_limit_violation isolates it but tracks the outcome (17 of 42 right), so it cannot be a headline filter.

**Why not 1.00 Å.** The band fact (Opus round 2) settles it: 28 of the 30 evaluations between 0.99 and 1.00 Å are mp-985293. Raising the boundary and dropping the structure are the same post hoc move. The nested switch to 1.00 Å is not independent evidence for a better boundary: the training folds pick 1.00 Å because they contain mp-985293, and the one fold without it in training keeps 0.99 Å and loses to the constant baseline (8/28 against 19/28). Astra's point, adopted.

**Why the pair clause goes into the headline.** The trigger that fired is the pair count. A headline that says 185/212 while the judge finds 10 wrong pairs in the JSON reads as hiding. Stating them with their common structure answers the correlated-evaluations objection more honestly than "no pair is called the wrong way" did.

**Why no phase name and no mechanism.** Argon's δ-Al(OH)3 identification is plausible (dense pseudo-cubic cell, a ≈ 5.08, b ≈ 5.14, c ≈ 7.25 Å, MP volume 6.75 Å³/atom) but not verified against a source in this review, and the confinement mechanism is an explanation fitted after the fact. The computed cancellation (95 to 132%) is the defensible statement.

**Why 190/234 and the p-value leave the statistics sentence.** 190/234 is the all-covalent signal-cut population; decision 06 action 3 already ruled that the no-cut headline pairs with the matched O-H no-cut count (187/232). The binomial p stays in F01 details only, labelled descriptive (decision 05 disagreement 2). The O...O count is signal-filtered, so its sentence now says so.

**Wording fixes taken from the members' pushback.**
* "Three ML potentials agree in 185 of 212" reads as three-model unanimity; it is pooled sign agreement (Astra). The judge sentence and video hook now say the potentials "get this sign" or describe the calculations.
* "Stretching an X-H bond by 1 mÅ lowers the H-D shift" (Argon) has the wrong signed reading and describes a controlled stretch the regression across polymorphs does not test (Opus, Astra). Not used.
* "Below 0.99 Å bend/libration stiffening flips the sign" (Argon) is an untested mechanism. The claim stays "fails, 2 of 20".
* "ICSD-linked" (Opus) rests only on the MP flag. The text says "listed by the Materials Project as experimental".

## Where the members converged

1. mp-985293 stays in the headline; no outcome-independent exclusion exists (all three, both rounds).
2. 0.99 Å stays; 1.00 Å and the exclusion are post hoc and only locate the failure (all three).
3. The freeze report is wrong on "theoretical" and on MatterSim 8 of 10; mp-985293 has no imaginary modes; the pair flags come from partners (all three).
4. "No pair is called the wrong way" and "0.99 Å in every fold" are withdrawn everywhere outside the decision record (all three).
5. Headline numbers: 185/212 vs 131/212, 84 pairs, 28 formulas, 74/0/10; nested 183/210 with 1.00 Å in 30 of 31 folds; weak side 2/20; slopes 0.11 to 0.13 screen-wide, 0.13 to 0.15 O-H strong; compensation about half (all three).
6. Opus's 300/2000 linear-kT correction for omitted partner soft modes is dropped (Astra and Argon objected, Opus withdrew in round 2). Only the flag count is reported.
7. F03 numbers refreshed to 0.91/0.92/0.92 with outer-window 0.67/2.61/1.46; "2 to 3 times too steep" goes.
8. SevenNet stays a separate sign-vote line. P10(c) not triggered.
9. mp-985293 evaluations are highlighted in the figure, kept in the counts.

## Remaining disagreement

1. **Pair clause in the headline or only in the statistics sentence.** Opus round 1 and Argon kept it out; Opus round 2 and Astra put it in. Ruling: in the headline (Decision 3).
2. **Where the post hoc 177/184 and 175/182 appear.** Opus and Argon put them in the statistics sentence; Astra wanted details only. Ruling: details and a collapsed app expander only (Decision 4). Astra's argument wins: a 96.2% next to the headline becomes the number people remember.
3. **δ-Al(OH)3 phase name and confinement mechanism.** Argon wants both in the statistics sentence, judge sentence, video and count box. Opus and Astra want the identity verified first. Ruling: neither in submission text now; optional action 9.
4. **1.00 Å line on the figure.** Argon: draw it dashed. Opus: no. Astra: only labelled, and never an absolute threshold on a Δ axis. Ruling: no threshold line (the axis is Δ mean O-H); 1.00 Å goes in the caption.
5. **App toggle.** Opus and Argon: a labelled toggle. Astra: no prominent toggle. Ruling: collapsed expander, default population fixed.
6. **Edit 05 and 06 in place or addendum.** Opus round 1 and Argon: edit. Opus round 2 and Astra: addendum. Ruling: this file is the addendum; 05 and 06 get pointer lines only.
7. **168/170 after excluding classical-limit rows.** Argon reported it as a quality sensitivity; Astra allowed it as a diagnostic; Opus kept it out of the headline because the flag tracks the outcome. Ruling: F01 details only, labelled diagnostic, never a filter.

## Ordered action list for the conductor

| # | Action | Owner | Time | Done-check |
|---|---|---|---|---|
| 1 | **Pointers and record.** Add one line under the title of `docs/decisions/05-final-claims.md` and `06-strategy-to-submission.md`: "Amended after the compute freeze by [07](07-freeze-wording.md): headline, statistics, F03, threshold re-choice, judge and organiser sentences, pair counts, video and figure counts. Where they differ, 07 governs." Do not rewrite the bodies. | Opus | 5 min | `git grep -n "07-freeze-wording" docs/decisions/05-final-claims.md docs/decisions/06-strategy-to-submission.md` returns two lines. |
| 2 | **Correct the freeze report and ledger** in one commit. In `docs/freeze/FREEZE_REPORT.md` Diagnosis: replace "a theoretical Al(OH)3 polymorph" with "an Al(OH)3 polymorph listed by the Materials Project as experimental (theoretical=False; the pair-level theoretical, soft-mode and classical-limit flags come from its partners; it has no imaginary modes in any model)"; replace "MatterSim gets 8 of 10 right" with "MatterSim gets 8 of 9 right"; add "28 of the 30 evaluations between 0.99 and 1.00 Å are mp-985293". Append to `state/LEDGER.md` (do not edit line 79): "22 Oct chair 07: correction to the freeze line, mp-985293 is MP experimental, not theoretical; MatterSim 8/9. Wording decided in docs/decisions/07-freeze-wording.md: 0.99 Å kept, mp-985293 kept, pair clause in the headline." | Sonnet agent | 10 min | `git grep -n "theoretical Al(OH)3" docs/freeze state` returns only the historical ledger line 79; `git grep -n "8 of 10" docs/freeze` is empty. |
| 3 | **Regenerable locators in `src/isoshift_event/rule_cv.py`.** Add two labelled blocks to `F01_cv.json` without touching existing ones: `posthoc_locators` (without mp-985293: 177/184, pairs 74/0/0; fixed 1.00 Å: 175/182, 73/0/0; band 0.99 to 1.00 Å: 30 rows, 28 mp-985293, 10 right in that structure; per model mp-985293 MACE 0/10, ORB 0/9, MatterSim 8/9) and `quality_flags_diagnostic` (classical_limit_violation 42 rows, 17 right; unflagged 168/170). Each block carries the note "post hoc, not a headline". Rerun `python -m src.isoshift_event.rule_cv`. | Opus | 20 min | A diff of `F01_cv.json` before and after shows only the two added keys; `oh_unfiltered_strong` is 185/212 with 74/0/10 and `nested_threshold_cv.OH_no_cut` is 183/210. |
| 4 | **Fill the text.** Commit `fill_placeholders.py` with a value map read from `F01_cv.json`. Put the verbatim headline, statistics and SevenNet sentences above into README.md, docs/story/writeup.md, docs/findings/F01-xh-length-rule.md and state/GOAL.md; replace the F03 sentence wherever decision 05's version was copied (F01, F03 finding, GOAL S5b). Add to F01 details, labelled: the post hoc locator, the numerical-quality sentence, the mp-985293 geometry (mean O-H 0.996/0.997/0.999 Å, donors 0.987 to 1.005, mean O...O 2.77 to 2.82, 6.79 to 6.94 Å³/atom vs 7.54 to 7.88), and 190/234 labelled "all covalent, signal cut, descriptive" with its p-value labelled "descriptive, not a confirmatory test". Prior art last clause and organiser sentence as above. | Opus | 35 min | `git grep -n "{{" README.md docs/story docs/findings app state/GOAL.md` is empty; `git grep -n "185 of 212" README.md docs/story/writeup.md docs/findings/F01-xh-length-rule.md state/GOAL.md` hits all four. |
| 5 | **Video script.** Replace lines 11 and 13 of `docs/story/video_script.md` with the verbatim text above; update the placeholder table (lines 29 to 38) to the frozen values or delete it. Recount spoken words. | Opus | 15 min | No `{{` in the file; spoken word count 460 or fewer; `grep -n -i -e "wrong way" -e "agree in" docs/story/video_script.md` is empty. |
| 6 | **App.** Default banner as above, reading counts from `F01_cv.json`. Collapsed expander "Post hoc sensitivity (not the result)" with the locator sentence read from `posthoc_locators`. No population toggle. | Sonnet agent, Opus review | 25 min | CPU-only `marimo export html app/isoshift_app.py` succeeds; exported HTML contains "185/212" and "74 right, 0 ties, 10 wrong"; "177" appears only inside the expander. |
| 7 | **Headline figure** (`figures/fig_headline.png`) per decision 06 action 9 as amended above: count box, open markers for the 28 mp-985293 evaluations, weak side "fails, 2/20", no threshold line, inset slopes, caption. Rebuild `figures/fig4_xh_rule.png` if any panel text quotes counts. | Sonnet build, Opus review | 60 min | Read the PNG: count box text matches exactly; 28 open markers (count them from the plotting data, print it in the build log); no "0 wrong" or "1/16" anywhere on the image. |
| 8 | **Grep gate**, empty outside `docs/decisions` and `docs/freeze`: `git grep -n -e '123 of 130' -e '123/130' -e 'every fold' -e 'no pair' -e 'wrong way' -e '1 of 16' -e '1/16' -e '62 right' -e '0.12 to 0.15' -e '82 of 130' -e '197 ' -e 'theoretical Al' -e '0.95 (ORB)' -e '2 to 3 times' -e '{{' -- README.md docs/story docs/findings app state/GOAL.md` | Opus | 10 min | Command returns nothing (any hit in a historical or superseded block must carry the word "superseded" on the same line). |
| 9 | **Optional, 10 min cap, non-blocking.** Look up the ICSD reference behind mp-985293 on the MP page. If a primary source confirms the phase (for example δ-Al(OH)3), F01 details may name it with the citation as an identity, never as a mechanism or a reason to discount the pairs. | Opus | 10 min | Either a citation with a checked DOI in F01 details, or nothing changes. |

Order matters: 1 and 2 first (record), 3 before 4 and 6 (numbers come from JSON), 7 after 3, 8 last. Total about 3 h of agent time, which fits before decision 06 action 10.

## What would change this

1. **mp-985293 shown to be a wrong or duplicate entry by an outcome-blind check:** a documented rule applied to the whole population (for example, MP marks the entry deprecated, or a symmetry match shows it is the same relaxed phase as a partner in all models). Then it leaves by that rule, every structure the rule catches leaves with it, and the headline is recomputed and reported as a new count with the change disclosed.
2. **A coding error in `rule_cv.load()`** (rmax, the O-H mask or the sign convention) that moves the headline by more than a few rows: the chair reopens items 1 to 3.
3. **The headline falls below 85% or within 20 points of baseline** after any correction from action 3 or 9: P10(c) fallback, per decision 05.
4. **Phase identity verified (action 9):** the name goes into F01 details only. It changes the headline only if the source shows the Materials Project structure is not the reported phase, which falls under item 1.
5. **A new argument from a member,** not a vote, reopens a ruling in the disagreement list.

Chair recompute script: `C:\Users\can02\AppData\Local\Temp\claude\C--Users-can02--claude-spares-spare-MvrxRR\6cbef617-8c25-4b42-bf3b-8e15cd3cc49b\scratchpad\chair07.py`
