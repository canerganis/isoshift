# 13. Close the gaps before submission

Date: Thu 22 Oct 2026, about 14:15 TRT. Council: Opus (chair), Astra; Argon unavailable (quota error 429 in both rounds, recorded as no answer, not as a vote). Evidence: state/GOAL.md, README.md, docs/story/writeup.md, docs/FAQ.md, docs/story/SUBMISSION_PACKET.md, docs/INDEX.md, docs/findings/F11-prospective-test.md, docs/decisions/07 and 12, app/isoshift_app.py, docs/story/agent_extraction_audit.md, plus logs/bond_queries.jsonl, docs/math/M02-bigeleisen-bridge.md and docs/findings/CARD-AlOOH.md.

## Decision

No new science. Every scientific validation gap is UNCLOSABLE today and gets a fixed limits sentence in the writeup and README before a judge can find it. Six presentation and correctness gaps are CLOSABLE in about 3.5 agent hours and are done in this order:

1. Fix the fractionation bridge in README line 19 (it drops the M02 R term and equates an energy with a boundary shift).
2. Add one compact Limits block to the writeup and the matching bullets to README; correct two false process claims (P04 timing, F06 scope); add F11 to moment_short.md and a dated F11 qualification to GOAL S3.
3. Make the judge path real: a five-package requirements-judge.txt, tested in a fresh venv.
4. App: label which rows are inside the F01 headline in Check a pair, rename the "Benchmark & atlas" tab, then three screenshots.
5. Make Valency Bond use auditable: count breakdown, provenance table, extraction audit linked, two numeric errors in the audit fixed.
6. Name the prospective users (Impact) and add a one-line prediction scorecard (Relevance).

F11 is final (commit 4ea0552: every computable ordered pair ran by 14:06; the 20:00 to 21:30 GPU window is not used). Both members assumed the counts would still move. They will not, so the final counts may now be quoted. The idle GPU is not a reason to start any new run.

## Why

Re-checked at 14:10 with the repo files and `.venv/Scripts/python.exe`:

* README line 19: "The D/H fractionation between two coexisting polymorphs equals the isotope shift of their boundary (n_H kT ln α = ΔΔG_iso ...)". M02 line 47: ddG_iso = n_H k_B T ln alpha_tr + R; R = 0 exactly only for one H site type with no H-H coupling (M02 item 5). Diaspore and δ-AlOOH each have one H site, so the AlOOH test stays clean, but the general sentence is wrong and also calls an energy a boundary shift. A physical chemist finds this in a minute. Highest gain per hour.
* writeup.md, 610 words. Zero hits for "training data", "anharmon", "transfer", "marimo", "neutron", "P04", "DFT", "carbon". Line 21 says "Predictions were committed before data"; README line 110 says the P04 comparison rule was committed with its result (90ad4cd). The writeup claim is false as written.
* moment_short.md (197 words, the fallback per packet line 39) has no F11 and says blind-test predictions were committed before data, again without the P04 exception.
* GOAL S3 still reads "done" with no F11 qualification.
* F11 JSON: 111 counted, 69 failed or unstable, 18 not clean, 24 scored, 16 right (14.4%), baseline 5; ceiling (111 - 87)/111 = 21.6% against the 75% bar; clean rows rule 16/24, constant -1 19/24, constant +1 5/24. F11 section 1 already says "The rule does not beat a constant guess on the clean rows" but nowhere says what that means for the claim: transfer to new pairs is not shown.
* Bond log: 182 rows = 85 sweep rows (no ts, no purpose) + 97 agent rows with purpose; of these, 20 are "prior-art check for 'first' claim", 26 atlas test, 9 ice boundaries, the rest validation lookups. Ikeda 2025 (10.1021/jacs.4c11982) IS in the log, lines 108, 110 and 157 (Astra is right; Opus round 1 was wrong). No literal match for Libowitzky or Graham/Chacko; the table must say "no matching log row", not "not found via Bond". The "three web searches" in the packet are not in this log.
* agent_extraction_audit.md line 28 says "about 1 in 5" without a count; line 13 says 0.22% where 1.04 - 0.81 = 0.23.
* Judge path: README box assumes the venv; How to run installs requirements.txt (167 pins, torch 2.6.0). rule_cv imports only numpy and pandas; the app adds marimo and matplotlib. A judge on a laptop may give up before seeing 185/212.
* App: pair_report (lines 270 to 330) prints agree yes/no for weak-regime, non-O-H and flagged rows alike, and MODELS includes sevenn. A judge clicking an arbitrary pair can read a weak-regime "no" as a counterexample to the headline, or a "yes" as support. The tab "Benchmark & atlas" (line 395) shows no atlas content.

## Where the members converged

* Split: access, disclosure and claim consistency are closable; all validation gaps are not.
* No new study, no new threshold or rescoring, no favourable subset, no hosting project, mp-985293 stays in the counts.
* Do not present F11 clean-only numbers as a success, and do not call the constant -1 comparator preregistered.
* Do not append every caveat verbatim to the 610-word writeup; compress into one Limits block and put the long list in README.
* Fix the R bridge, the P04 and F06 wording, the extraction-audit numbers and the tab name.
* Name neutron diffraction and isotope geochemistry as prospective users, claim no adoption, and keep drug or organic polymorphs out (the screen excludes carbon).
* Submission target 23:45 TRT with an anonymous-clone check after Can makes the repo public.

## Remaining disagreement and ruling

* **Docs before 16:15?** Astra: yes. Opus: only slides and app are tied to the lock. Ruling: docs are not tied to the lock, but actions 1 and 2 run first anyway and finish by 15:45 because they carry the most value.
* **42/212 classical-limit flag in the writeup?** Astra: yes. Opus: README only, because decision 07 rules it a diagnostic and the one-page summary has no room to explain why 168/170 must not be read as a filter. Ruling: README only, with the decision 07 "does not certify" sentence.
* **F11 counts in the writeup?** Both said no because counts would move. F11 is final, so the writeup sentence carries the final counts.
* **Rank of the judge install path.** Astra rank 2 after claims, Opus rank 2 after the R fix. Same place; adopted.
* **App eligibility labels.** Opus treated it as a small label change; Astra made it a required fix before screenshots. Ruling: Astra's version. The screenshots and the How we know scene must not show a headline-looking verdict on an out-of-scope row.
* **Public flip time.** Opus proposed 22:45. This is Can's call; the conductor asks Can once, with the reason (the clone check needs about 30 minutes), and does not treat 22:45 as authorised.

## Gap list

### Against state/GOAL.md

| Row | Gap | Status | Writeup has it | README has it |
|---|---|---|---|---|
| S1 | Brucite and LiH are volume checks, not polymorph isotope free energies; ice volumes 4 to 11x off | UNCLOSABLE | partly ("no measurement has tested it directly") | yes |
| S2 | Shared PBE-level training data; spread is not a confidence interval; no DFT double difference | UNCLOSABLE | no | partly (no "no DFT double difference" sentence) |
| S3 | Threshold CV does not cover choice of regime variable or eligibility cuts | UNCLOSABLE | no | partly |
| S3 | F11 prospective test FAIL; transfer to new pairs not shown | UNCLOSABLE | verdict only | verdict only |
| S3 | GOAL row says "done" without F11 | CLOSABLE (action 2) | | |
| S4 | No direct experimental test of F01; F02 mixed; F07 Ih-II and Ih-III wrong sign | UNCLOSABLE | yes | yes |
| S5 | F09 H1 failed, no crossover mechanism; F05 magnitudes 5 to 10x | UNCLOSABLE | F09 partly, F05 magnitude no | yes |
| S5b | Stretch check covers O...O 2.50 to 2.80 Å, regime reaches about 2.93 Å | UNCLOSABLE | window yes, gap no | yes |
| S5c | F04 is one pair, signs only | UNCLOSABLE | yes | yes |
| S6 | Council agreement does not validate physics; P04 rule timing; F06 is a nine-row implementation check | wording CLOSABLE, science UNCLOSABLE | wrong ("committed before data") | yes |
| S7 | AlOOH shift is an exploratory sign; MACE root extrapolated; proton disorder not modelled; H boundaries 4.24 GPa apart | UNCLOSABLE | yes | yes |
| all | Harmonic physics: no anharmonicity, tunnelling, proton disorder | UNCLOSABLE | "harmonic" once, no exclusions | yes |
| all | Bridge to experiment needs R (M02) | wording CLOSABLE (action 1) | qualifier missing | wrong (line 19) |

### Against the judging criteria and prizes

| Criterion | Gap | Status |
|---|---|---|
| Impact | Writeup names no user | CLOSABLE, action 6 |
| Impact | No user validation, small magnitudes, F11 rules out pitching the rule or atlas as a screening tool, no drug polymorphs | UNCLOSABLE, limits sentence |
| Innovativeness | AI process visible but no outcome count in the summary | CLOSABLE, action 6 |
| Novelty | Mechanism is McKenzie's; logged search does not prove priority | UNCLOSABLE, already worded in README; one writeup clause in action 2 |
| Relevance | "Predictions were committed before data" overclaims; F06 scope missing | CLOSABLE, action 2 |
| Valency prize | Count only plus one trace; breakdown, audit, rejected example not surfaced; audit has two number errors; web searches unsourced | CLOSABLE, action 5 |
| Valency prize | No benchmark of Bond extraction accuracy can be made today | UNCLOSABLE, limits sentence |
| marimo prize | Heavy install, no screenshots, writeup silent, eligibility not labelled, misnamed tab | CLOSABLE, actions 3 and 4 |
| marimo prize | App inspects cached results only | UNCLOSABLE, limits sentence |
| Access | Repo private; anonymous clone untested | CLOSABLE only after Can flips it (action 7) |

## Limits sentences (exact text)

### Writeup: replace the current Limits paragraph with this block

> **Limits.** Re-choosing the boundary inside training folds gives 183 of 210 held-out evaluations right against 131; the fold holding out Al(OH)3 scores 8 of 28 against 19, so no sharp boundary is established, and cross-validation covers the threshold, not the choice of regime variable or eligibility cuts. F11, a post-freeze prospective test on pairs never computed before, failed its predeclared bar: 87 of 111 rows were lost to the predeclared numerical rules, and on the 24 clean rows the rule (16 right) did not beat a constant guess (19), so transfer to new pairs is not shown. The three potentials share PBE-level training data, so their agreement is not a validation; the DFT benchmark is per structure, and no DFT value of the double difference was computed. Free energies are harmonic or quasi-harmonic, without anharmonicity, tunnelling or proton disorder; the harmonic brucite to goethite D/H fractionation is 5 to 10 times larger than measured (F05). The stretch check covers O...O 2.50 to 2.80 Å, while the regime reaches about 2.93 Å. Experimental usefulness is untested, and drug or organic polymorphs lie outside this carbon-free screen.

Other writeup edits:

* Line 3, after "D/H partitioning between coexisting polymorphs": add "(exact for one H site type such as AlOOH; M02 gives the correction otherwise)".
* "Beyond the headline", replace with: "**Beyond the headline (post-freeze, 22 Oct).** Bend and libration, not the stretch, flip the 10 wrong pairs below a model-dependent crossover, and the predeclared explanation for it failed (F09); F12 (boehmite vs diaspore) agrees in sign but is inconclusive; F08 failed; F10 is an untested map."
* "How the AI worked", replace "Predictions were committed before data." with "Ten prediction files were committed before their data, except the P04 scoring rule, committed with its result; F07, F08, F09 (H1) and F11 failed and are reported." Replace "Codex reimplemented ΔΔF_iso blind to 1e-9 meV/atom (F06)." with "Codex reimplemented ΔΔF_iso blind to 1e-9 meV/atom on nine rows (F06, an implementation check)." Change "(182 queries)" to "(182 logged queries; extraction audit: [agent_extraction_audit.md](agent_extraction_audit.md))". Add: "A marimo app (Check a pair, How we know, Benchmark) inspects the cached results without a GPU; it computes no new phonons."
* Impact clause from action 6.
* Word cap 700. If over, cut in this order: the "Before vs during" line (README keeps it), the structure-only sentence in "What is new", the benchmark sentence in "Checks". If the Moment photo shows a smaller limit, use moment_short.md (decision 12 row 73).

### README

* Line 19, replace the "How to test it" sentence with: "**How to test it.** No polymorph isotope free energy has been measured. Measured D/H fractionation between two coexisting polymorphs constrains their isotope free-energy difference through ΔΔG_iso = n_H k_B T ln α + R, with α the a to b fractionation factor of [M02](docs/math/M02-bigeleisen-bridge.md) and R = 0 for one H site type with no H-H coupling, as in diaspore and δ-AlOOH; the boundary shift then follows from ΔΔG_iso and ΔV. For the AlOOH card, matched reversed-bracket runs on AlOOH and AlOOD test the sign of the pressure shift." The conductor copies the α orientation from M02 line 45 and checks the sign convention against M02 before committing.
* Limitations, add these bullets (the others are already there):
  * "F11, a post-freeze prospective test on pairs never computed before, failed its predeclared bar (16 of 111 right; 87 rows lost to the predeclared numerical rules; on the 24 clean rows the rule got 16 and a constant guess 19). Transfer of F01 to new pairs is not shown."
  * "The DFT benchmark is per structure. No DFT value of a polymorph isotope double difference was computed."
  * "'Clean' means the two free-energy routes agree within 0.01 meV/atom; it does not certify relaxation convergence, dynamical stability or robustness to imaginary modes. 42 of 212 headline evaluations carry a classical-limit flag (decision 07: a diagnostic, not a filter)."
  * "Cross-validation covers the 0.99 Å threshold, not the choice of regime variable, grid or eligibility cuts."
  * "Experimental usefulness is untested. The screen excludes carbon, so drug and organic polymorphs are out of scope."
  * "Bond-assisted extraction needed source checking: of 11 sweep items, 9 came back 'ok' in one pass and 2 became quantitative targets, and the board caught a reference value off by 2x. These are screening outcomes, not an extraction accuracy."
  * "The marimo app inspects cached results for screened pairs. It does not compute phonons and does not predict arbitrary pairs."
* "How AI was used", P04 line already correct; add "F06 is a nine-row implementation check, not a physics test."

### Already present, keep as is

S4 (F07 failed, F02 mixed, no direct measurement), S5c (one pair), S7 caveats, shared training data and model spread (README only), harmonic only (README), F10 untested, novelty and priority disclaimer (README), post hoc boundary and Al(OH)3 fold (both).

## Ordered action list for the conductor

Gain per hour is a relative priority, not a score prediction.

| # | Action | Owner | Time | Window | Done-check | Gain/h |
|---|---|---|---|---|---|---|
| 1 | R bridge fix: README line 19 text above; writeup line 3 qualifier; same qualifier in moment_short.md, FAQ, packet and INDEX line 73 if they paraphrase it | conductor | 15 min | now, by 14:45 | `git grep -n "equals the isotope shift"` and `git grep -n "= ΔΔG_iso"` return no uncorrected bridge; README sentence matches M02 lines 45 to 47 and item 5 | highest |
| 2 | Limits block and claim fixes: writeup edits above; README Limitations bullets above; F11 section 1 gets "Transfer of F01 to new pairs is not shown." after "The rule does not beat a constant guess on the clean rows."; moment_short.md gets "A prospective test on new pairs failed its predeclared bar (F11), and one scoring rule (P04) was committed with its result." and "committed before the data were read" is qualified; GOAL S3 gets a dated line "22 Oct: F11 prospective test FAIL (post-freeze), transfer to new pairs not shown" without rewriting earlier text | conductor | 45 min | by 15:45 | writeup ≤ 700 words and greps ≥ 1 for "training data", "anharmon", "2.93", "transfer", "P04", "nine rows", "carbon", "marimo"; decision 07 headline sentences byte-identical (`git diff` shows no change to them); `grep -niE "discover\|law\|first\|independent"` hits reviewed by hand, no positive use (literal zero is not required); F11 numbers equal `results/post_freeze/F11_prospective.json` | high |
| 3 | Judge path: `requirements-judge.txt` with numpy==2.5.4, pandas==2.3.3, scipy==1.18.1, matplotlib==3.11.2, marimo==0.25.2 (versions from requirements.txt); README box line: "`pip install -r requirements-judge.txt` (five packages, no torch), then `python -m src.isoshift_event.rule_cv` and `marimo run app/isoshift_app.py`". PEP 723 header in the app only if it works inside the time box | fixer agent | 40 min | app header before 16:15 or after 20:00; README any time | fresh venv in scratchpad, install time recorded; rule_cv prints right 185 n 212 baseline 131 and pairs 74/0/10; `marimo export html app/isoshift_app.py -o out.html` exits 0; `tests/test_app.py` 6/6 | high |
| 4 | App: add column "in F01 headline" (yes only if both structures covalent O-H, regime strong, \|Δ\| ≥ 5 mÅ, row clean; otherwise the reason: weak regime, not O-H, below 5 mÅ, flagged); agree shows "outside headline" for those rows; sevenn rows marked "secondary, sign only"; missing values shown as blank, not 0; tab "Benchmark & atlas" renamed to what it shows ("Benchmark" or "Benchmark & stretch check"), RECORDING.md line 34 and packet updated. Then three 1920x1080 screenshots (banner and tabs; Check a pair on diaspore vs δ-AlOOH; How we know with the Bond trace) into README box and packet box (d) | fixer agent (sole app writer) | 45 min + 15 min screenshots | code by 15:55 with tests green, else after 20:00; never 16:30 to 20:00 | tests 6/6 plus one new test that a weak-regime pair shows "outside headline"; for the 212 headline rows the new column says yes on exactly the rows rule_cv counts; screenshot numbers match results/F01_cv.json | medium-high |
| 5 | Bond provenance: in agent_extraction_audit.md replace "about 1 in 5" with the actual count and 0.22 with 0.23; append a table (finding, measured value, DOI, log line or "no matching log row") for F02, F04, F05, F07, F12, CARD-AlOOH and the prior-art check, using Ikeda lines 108, 110, 157 and marking Libowitzky and Graham/Chacko "no matching log row"; packet box (c) and README "How AI was used" state 182 = 85 sweep + 97 agent rows (20 prior-art, 26 atlas test, 9 ice, rest validation lookups), the 9 of 11 / 2 kept audit result, the 2x ice catch, and link the audit; the "three web searches" phrase is cited from its record or removed | Sonnet sweep agent, conductor verifies | 45 min + 10 min | by 18:30 | a script recomputes every count from logs/bond_queries.jsonl; every DOI in the table greps to its cited line; no sentence says every measured value came through Bond | medium |
| 6 | Impact and scorecard: one writeup clause and README "Why" lines: "Possible users: high-pressure neutron groups that use δ-AlOOD and ε-FeOOD as stand-ins for hydrous mantle phases (the models give the AlOOD boundary about 1 GPa higher, exploratory sign), and isotope geochemists comparing D/H partitioning between coexisting minerals (M02, with R stated)." Scorecard in README: one line per prediction file P01 to P10 with outcome (failed: F07, F08, F09 H1, F11; mixed F02; ordering only F05; inconclusive F12; sign-level one pair F04; nothing scorable F10) and P07 parked per decision 08, also as a row in INDEX | conductor | 25 min | by 19:00 | every citation greps to CARD-AlOOH.md, F-files or the Bond log; every outcome greps to INDEX; no drug, pharma or adoption wording | medium |
| 7 | Release: ask Can once for a flip time that leaves 30 min before 23:45; after the flip run an anonymous clone, `pip install -r requirements-judge.txt`, rule_cv and tests; save the submission receipt | conductor prepares, Can flips and submits | 30 min | after Can's flip, before 23:45 | clone check output saved under results/; receipt captured | gate |

Total about 3.9 hours of agent and conductor time, most of it in parallel.

## What not to do

* No new CPU or GPU study, including the free 20:00 to 21:30 window, path integrals, more F11 pairs, DFT double differences or anything in the F10 atlas.
* Do not turn the atlas or Check a pair into a "predict any MP pair" tool; F11 failed and F10 is untested.
* Do not quote F11 clean-only advantages over the frozen +1 baseline, call the constant -1 comparator preregistered, or say "mostly numerical failures, so the rule is fine".
* Do not put the 168/170 unflagged figure in the writeup.
* Do not claim every measured value came via Bond, and do not claim Bond extraction accuracy.
* Do not mention drug or pharmaceutical polymorphs except as out of scope.
* Do not change the decision 07 headline sentences, the narration column, P10 files or cleanliness rules; no slide change after 16:15; no app edit 16:30 to 20:00.
* Do not run the marimo WASM link (decision 12 action 7) unless actions 1 to 6 are done and Can says yes.
* Do not treat any flip time as decided without Can.

## What would change this

* The Moment form shows a write-up limit below 700 words: the Limits block stays whole, and the cut order above applies; below 610, submit moment_short.md with the F11 and R lines.
* The fresh-venv install fails on the pinned versions: drop the pins to the nearest versions that resolve, record them, and keep requirements.txt as the full path.
* The new eligibility column disagrees with rule_cv on any of the 212 headline rows: stop, do not ship the column or the screenshots, and report the mismatch to the conductor (it would mean the app and the headline use different eligibility).
* A Bond log row for Libowitzky or Graham/Chacko turns up: cite the line; nothing is added to the log after the fact.
* Can declines a flip before about 23:15: skip the anonymous-clone check, say so in the packet, and submit by 23:45.
* Argon returns before 18:00 with a blocking objection to a limits sentence: the conductor weighs it against the evidence above, not as a vote.
