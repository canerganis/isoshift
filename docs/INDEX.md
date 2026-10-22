# Evidence index

Reading order for a judge. One line per document. Times are 21 and 22 Oct 2026, +0300, from `git log`. Status words: **computed** (our models, no measurement involved), **tested** (compared with measured data under a rule fixed in advance or a stated check), **exploratory** (a prediction outside the validated domain).

## Start here (2 minutes)

1. `README.md`: what IsoShift computes, the F01 headline, results table, limits, how to run.
2. `docs/decisions/07-freeze-wording.md`: the binding claim wording and frozen numbers; it governs where it differs from `docs/decisions/05-final-claims.md`, which records what was narrowed and why.
3. `docs/story/writeup.md`: the submission summary.

## Findings

| id | file | status | one line |
|---|---|---|---|
| F01 | [F01-xh-length-rule.md](findings/F01-xh-length-rule.md) | computed | Deuteration favours the polymorph with shorter O-H bonds in 185 of 212 O-H evaluations once H bonds are moderate to strong (model mean O-H ≥ 0.99 Å; baseline 131/212; pairs 74 right, 10 wrong, all 10 contain Al(OH)3 mp-985293); fails below (2 of 20). Frozen numbers, decision 07. |
| F03 | [F03-stretch-vs-experiment.md](findings/F03-stretch-vs-experiment.md) | tested | Model O-H stretch slope against O...O matches the measured Libowitzky correlation in 2.50 to 2.80 Å (f 0.91 to 0.92); consistency check on the stretch term only. |
| F02 | [F02-blind-test.md](findings/F02-blind-test.md) | tested | Prediction-first volume isotope effects (P01): mixed; hydrides and brucite right, two strong-H-bond oxyhydroxides wrong against weak data; does not test F01. |
| F04 | [F04-differential-spectroscopy.md](findings/F04-differential-spectroscopy.md) | tested | Predeclared O-H stretch and bend shifts (P02, P03): sign-level consistency for goethite to ε-FeOOH, two pairs inconclusive. |
| F04 audit | [F04-source-audit.md](findings/F04-source-audit.md) | tested | Literature audit of the F04 band choices and of the Sano-Furukawa 9.0 / 13.4 / 18.1 GPa numbers used in the card caveat. |
| F05 | [F05-fractionation-test.md](findings/F05-fractionation-test.md) | tested | Blind harmonic D/H fractionation (P04): sign and order brucite > goethite > manganite right, magnitudes 5 to 10 times too large; verdict "ordering only". |
| F06 | [F06-independent-replication.md](findings/F06-independent-replication.md) | computed | A second implementation (Codex, written without our code) reproduces ddF_iso and its stretch/bend split to 1e-9 meV/atom on 9 rows; checks code, not physics. |
| F07 | [F07-ice-boundary-test.md](findings/F07-ice-boundary-test.md) | tested | Blind H2O to D2O shift of three ice boundaries (P05): Ih-II and Ih-III wrong sign in 3 of 3 models, II-III right; both failures involve ice Ih through the ordered ice XI proxy. Reported as a failed prediction. |
| Card | [CARD-AlOOH.md](findings/CARD-AlOOH.md) | exploratory | Deuteration raises the diaspore to δ-AlOOH transition pressure by +1.13 (ORB) and +1.33 GPa (MACE) at 300 K; a sign prediction outside the harmonic domain; goethite to ε-FeOOH as a second, extrapolated card. |

## Predictions committed before the comparison data were read

| id | file | commit, time | one line |
|---|---|---|---|
| P01 | [P01_volume_isotope_blind.csv](predictions/P01_volume_isotope_blind.csv) | 0fffc54, 20:27 | Volume isotope effects for 13 known H compounds (MACE, ORB); measured rows had been committed unread in 3bb0ea4 (19:53). Scored in F02. |
| P02 | [P02_differential_spectroscopy.md](predictions/P02_differential_spectroscopy.md), [P02_spectro_model.csv](predictions/P02_spectro_model.csv) | v1 6a3064b, 20:50; v2 da560cf, 20:52 | Model O-H stretch and bend shifts for diaspore to δ-AlOOH and goethite to ε-FeOOH with support and challenge rules, before band lookup. Scored in F04. |
| P03 | [P03_differential_spectroscopy.md](predictions/P03_differential_spectroscopy.md), [P03_spectro_model.csv](predictions/P03_spectro_model.csv) | c990f11, 21:27 | Manganite to groutite, the opposite direction to P02, before band lookup. Scored in F04 (inconclusive). |
| P04 | [P04_fractionation_blind.csv](predictions/P04_fractionation_blind.csv) | f3ac0ac, 21:36 | Harmonic 1000 ln beta (25 to 400 C) for 118 known hydroxide structures, three models; data committed unread in e7ee2d5 (21:43). |
| P05 | [P05_ice_boundary_blind.md](predictions/P05_ice_boundary_blind.md) | bec68d7, 22 Oct 01:15 | Model H2O to D2O shift of the ice Ih-II, Ih-III and II-III boundaries with support and challenge rules, before any measured D2O boundary was read. Scored in F07. |
| P04 rule | [P04_comparison_rule.md](predictions/P04_comparison_rule.md) | 90ad4cd, 21:49 | Scoring rule for P04. Written before the comparison but first committed together with F05; see the timing note in F05. |

Related search: `data/isoshift/polymorph_fractionation.csv` (6890fc7, 23:00) records a blind search for measured inter-polymorph D/H fractionation; none was found.

## Decisions (multi-model board records, with dissent)

| # | file | one line |
|---|---|---|
| 00 | [00-brucite-imaginary-modes.md](decisions/00-brucite-imaginary-modes.md) | Brucite imaginary H branch: excluded from F_vib and bracketed by four treatments. |
| 01 | [01-gate.md](decisions/01-gate.md) | Hour-7 gate: conditional pass on brucite and LiH volume isotope effects, framing narrowed; one member argued for failure. |
| 02 | [02-soft-modes-and-relax-tolerance.md](decisions/02-soft-modes-and-relax-tolerance.md) | Soft-mode structures go to a bracketed tier; ORB relax tolerance. |
| 03 | [03-headline-real-phase-pairs.md](decisions/03-headline-real-phase-pairs.md) | Headline candidates only from pairs of two experimentally known, ordered phases. |
| 04 | [04-discovery-claim.md](decisions/04-discovery-claim.md) | F01 stays the headline, narrowed to the strong-H-bond O-H regime; F02 reported as a separate mixed test. Superseded on wording by 05; its planned "04-final-claims" record is decision 05. |
| 05 | [05-final-claims.md](decisions/05-final-claims.md) | Final claims: no blocking flaw; F01 is a regime-limited computational rule; F04 sign-level; card exploratory. Binding wording. |
| 06 | [06-strategy-to-submission.md](decisions/06-strategy-to-submission.md) | No new science; consistency fixes, one freeze rerun, one headline figure, one-page summary. |
| 07 | [07-freeze-wording.md](decisions/07-freeze-wording.md) | Frozen headline after the compute freeze: 185 of 212, baseline 131, pairs 74 right and 10 wrong, all 10 with mp-985293; binding wording and grep gate. |
| 10 | [10-cpu-discovery-study.md](decisions/10-cpu-discovery-study.md) | No new CPU study: an isotope-switchable polymorph list would be decided by model energy noise about 10 times the isotope term; F11 stays the one prediction-first test. |
| 11 | [11-positive-framing.md](decisions/11-positive-framing.md) | Result-first openings for README and the one-page summary, with the two experiments that would test the rule; no "discovery" or "first"; video unchanged. |

## Post-freeze addendum (22 Oct), frozen F01 headline unchanged

Everything below was planned by decision 08 after the compute freeze. Each study has its prediction or rule committed before the result. None of it changes the frozen numbers of decision 07, the README headline, the one-page summary headline or the headline figure.

| id | file | commit | one line |
|---|---|---|---|
| 08 | [08-post-freeze-science.md](decisions/08-post-freeze-science.md) | dfacd79 | Council plan for the addendum: temperature crossover, prospective held-out test, boehmite vs diaspore; video gate for one labelled sentence. |
| 09 | [09-video-sentence.md](decisions/09-video-sentence.md) | 23b1693 | Video SKIP: no post-freeze sentence in the video, narration unchanged; F09 erratum (H3 scope, H4 label, 600 K subset cleanliness). |
| P06, F08 | [P06_refined_rule.md](predictions/P06_refined_rule.md), [F08-refined-rule.md](findings/F08-refined-rule.md) | cdb32da, a66d602 | A refined rule with the O-H...O angle failed its predeclared SevenNet test (it could not pass); reported as a failure. |
| P09, F09 | [P09_temperature.md](predictions/P09_temperature.md), [F09-temperature-crossover.md](findings/F09-temperature-crossover.md) | d03f8d2, b9832a1 | Same calculations at 0, 300 and 600 K: headline rows right 153, 185, 210 of 212; all 28 mp-985293 rows follow the rule by 600 K with the stretch sign unchanged (H2 pass), product rule holds (H3 pass), 2000 K trace-limit signs 211 of 212 (H4 pass after a disclosed orientation fix), the zero-point weighting test fails (H1, 98 of 212). Fixed-geometry harmonic result; not in the video (decision 09). |
| P08, F10 | [P08_atlas_blind.md](predictions/P08_atlas_blind.md), [F10-isotope-atlas.md](findings/F10-isotope-atlas.md) | d991991, bb5f8f8 | Structure-only atlas of 1796 Materials Project O-H polymorph pairs; blind literature test scored 0 of 26 (22 excluded E1, 2 E3, 2 unmappable). An untested map, no verdict on the rule. |
| P11, F12 | [P11_boehmite_diaspore.md](predictions/P11_boehmite_diaspore.md), [F12-boehmite-diaspore.md](findings/F12-boehmite-diaspore.md) | 184fbee, 42a8282 | Boehmite vs diaspore model D/H fractionation against Graham et al. 1980 via a compilation: sign agrees at 380 C in 3 of 3 models but INCONCLUSIVE under the rule (no uncertainty, diaspore 25% exchange). |
| P10, F11 | [P10_prospective.md](predictions/P10_prospective.md), [F11-prospective-test.md](findings/F11-prospective-test.md) | eb61ccf | Prospective held-out test of the frozen rule on experimental pairs never computed (111 primary rows, 42 pairs, 20 formulas); predictions committed after relax-only geometry and before any phonon job. F11 prospective test: FAIL against its predeclared bar; see docs/findings/F11-prospective-test.md. |

## Math notes (two separate derivations, numeric cross-check)

| id | file | one line |
|---|---|---|
| M00 | [M00-plumbing-diatomic-zpe.md](math/M00-plumbing-diatomic-zpe.md) | Plumbing test of the mathcheck workflow on a diatomic ZPE isotope ratio. |
| M01 | [M01-isotope-formulas.md](math/M01-isotope-formulas.md) | All harmonic and QHA H/D formulas the code uses, including the mode-resolved mass integral behind the stretch/bend split. |
| M02 | [M02-bigeleisen-bridge.md](math/M02-bigeleisen-bridge.md), [M02-line47.md](math/M02-line47.md) | Links the polymorph-boundary isotope shift to inter-polymorph D/H fractionation (ddG_iso = n_H k_B T ln alpha + R, with R = 0 for one H site type such as AlOOH), which names the direct experiment for F01. Line 47 variance correction verified by mathcheck on 22 Oct (1366e27). |

## Provenance and process

* `docs/PROVENANCE.md`: what existed before the event (tag `pre-event-baseline`) and what was built during it, including both event-time changes to pre-event code.
* `DATA_SOURCES.md`: databases, experimental references and model checkpoints with licences.
* `state/LEDGER.md` and `state/GOAL.md`: the conductor's task ledger and success criteria.
* `logs/bond_queries.jsonl`: every Valency Bond literature query with its purpose.
* `docs/story/agent_extraction_audit.md`: one literature-to-decision trace and the extraction audit.
* `docs/AUDIT.md`: repository audit, fixes and open issues.
