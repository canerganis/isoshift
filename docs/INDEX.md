# Evidence index

Reading order for a judge. One line per document. Times are 21 Oct 2026, +0300, from `git log`. Status words: **computed** (our models, no measurement involved), **tested** (compared with measured data under a rule fixed in advance or a stated check), **exploratory** (a prediction outside the validated domain).

## Start here (2 minutes)

1. `README.md`: what IsoShift computes, the F01 headline, results table, limits, how to run.
2. `docs/decisions/05-final-claims.md`: the binding claim wording, the numbers behind it and what was narrowed (with the Argon addendum).
3. `docs/story/writeup.md`: the submission summary.

## Findings

| id | file | status | one line |
|---|---|---|---|
| F01 | [F01-xh-length-rule.md](findings/F01-xh-length-rule.md) | computed | Deuteration favours the polymorph with shorter O-H bonds in 123 of 130 O-H evaluations once H bonds are moderate to strong (mean O-H ≥ 0.99 Å); fails below (1 of 16). |
| F03 | [F03-stretch-vs-experiment.md](findings/F03-stretch-vs-experiment.md) | tested | Model O-H stretch slope against O...O matches the measured Libowitzky correlation in 2.50 to 2.80 Å (f 0.91 to 0.95); consistency check on the stretch term only. |
| F02 | [F02-blind-test.md](findings/F02-blind-test.md) | tested | Prediction-first volume isotope effects (P01): mixed; hydrides and brucite right, two strong-H-bond oxyhydroxides wrong against weak data; does not test F01. |
| F04 | [F04-differential-spectroscopy.md](findings/F04-differential-spectroscopy.md) | tested | Predeclared O-H stretch and bend shifts (P02, P03): sign-level consistency for goethite to ε-FeOOH, two pairs inconclusive. |
| F04 audit | [F04-source-audit.md](findings/F04-source-audit.md) | tested | Literature audit of the F04 band choices and of the Sano-Furukawa 9.0 / 13.4 / 18.1 GPa numbers used in the card caveat. |
| F05 | [F05-fractionation-test.md](findings/F05-fractionation-test.md) | tested | Blind harmonic D/H fractionation (P04): sign and order brucite > goethite > manganite right, magnitudes 5 to 10 times too large; verdict "ordering only". |
| F06 | [F06-independent-replication.md](findings/F06-independent-replication.md) | computed | A second implementation (Codex, without our code) reproduces ddF_iso and its stretch/bend split to 1e-9 meV/atom on 9 rows; checks code, not physics. |
| Card | [CARD-AlOOH.md](findings/CARD-AlOOH.md) | exploratory | Deuteration raises the diaspore to δ-AlOOH transition pressure by +1.13 (ORB) and +1.33 GPa (MACE) at 300 K; a sign prediction outside the harmonic domain; goethite to ε-FeOOH as a second, extrapolated card. |

The ice work (P05, F07) is in progress at the time of writing and is not indexed yet.

## Predictions committed before the comparison data were read

| id | file | commit, time | one line |
|---|---|---|---|
| P01 | [P01_volume_isotope_blind.csv](predictions/P01_volume_isotope_blind.csv) | 0fffc54, 20:27 | Volume isotope effects for 13 known H compounds (MACE, ORB); measured rows had been committed unread in 3bb0ea4 (19:53). Scored in F02. |
| P02 | [P02_differential_spectroscopy.md](predictions/P02_differential_spectroscopy.md), [P02_spectro_model.csv](predictions/P02_spectro_model.csv) | v1 6a3064b, 20:50; v2 da560cf, 20:52 | Model O-H stretch and bend shifts for diaspore to δ-AlOOH and goethite to ε-FeOOH with support and challenge rules, before band lookup. Scored in F04. |
| P03 | [P03_differential_spectroscopy.md](predictions/P03_differential_spectroscopy.md), [P03_spectro_model.csv](predictions/P03_spectro_model.csv) | c990f11, 21:27 | Manganite to groutite, the opposite direction to P02, before band lookup. Scored in F04 (inconclusive). |
| P04 | [P04_fractionation_blind.csv](predictions/P04_fractionation_blind.csv) | f3ac0ac, 21:36 | Harmonic 1000 ln beta (25 to 400 C) for 118 known hydroxide structures, three models; data committed unread in e7ee2d5 (21:43). |
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

## Math notes (two independent derivations, numeric cross-check)

| id | file | one line |
|---|---|---|
| M00 | [M00-plumbing-diatomic-zpe.md](math/M00-plumbing-diatomic-zpe.md) | Plumbing test of the mathcheck workflow on a diatomic ZPE isotope ratio. |
| M01 | [M01-isotope-formulas.md](math/M01-isotope-formulas.md) | All harmonic and QHA H/D formulas the code uses, including the mode-resolved mass integral behind the stretch/bend split. |
| M02 | [M02-bigeleisen-bridge.md](math/M02-bigeleisen-bridge.md) | Links the polymorph-boundary isotope shift to inter-polymorph D/H fractionation (n_H kT ln alpha = ddG_iso), which names the direct experiment for F01. |

## Provenance and process

* `docs/PROVENANCE.md`: what existed before the event (tag `pre-event-baseline`) and what was built during it, including both event-time changes to pre-event code.
* `DATA_SOURCES.md`: databases, experimental references and model checkpoints with licences.
* `state/LEDGER.md` and `state/GOAL.md`: the conductor's task ledger and success criteria.
* `logs/bond_queries.jsonl`: every Valency Bond literature query with its purpose.
* `docs/story/agent_extraction_audit.md`: one literature-to-decision trace and the extraction audit.
* `docs/AUDIT.md`: repository audit, fixes and open issues.
