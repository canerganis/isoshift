# Decision 06: strategy from now to submission

Amended after the compute freeze by [07](07-freeze-wording.md): headline, statistics, F03, threshold re-choice, judge and organiser sentences, pair counts, video and figure counts. Where they differ, 07 governs.

Action 10 opening amended by [11](11-positive-framing.md).

Chair: Opus. Members: Opus, Astra (round 1 only; no round 2 answer), Gemini 4 Argon (consultative). Written Wed 21 Oct, about 23:30 TRT.
Binding claim wording stays as in [05-final-claims.md](05-final-claims.md). This decision only orders the work.

## Decision

No new science. The science is narrowed and red-teamed (decision 05 plus the Argon addendum). What decides the score now is whether a judge gets the claim in 30 seconds and finds the same numbers everywhere they look. Order of work:

1. **Tonight, agents only, no Can:** fix the defects a judge would see. These are provenance text, untracked files the app reads, the app headline population, the write-up population mix, the decision-04 wording in the video script, and fig4 panel 3. Then commit the freeze acceptance rule to the ledger and leave the GPU alone.
2. **Thu 08:00 to 12:30:** one freeze rerun under the rule committed tonight, with the numbers propagated by one script.
3. **Thu 12:30 to 14:00:** one headline figure. Single panel plus one inset, not a 4-panel composite.
4. **Thu 14:00 to 15:30:** a one-page summary of 550 words or fewer. Drop "We claim none" and use a bounded, positive opening.
5. **Thu 15:30 to 17:30:** a marimo "Check a pair" tab and one Bond provenance trace. This serves the marimo and Valency prizes and makes the AI process visible.
6. **Thu 17:30 to 18:30:** Can rehearses video v3. Record at 19:00, publish the video by 22:00, submit by 00:30.

**Cut or de-emphasise:**
* The overnight literature sweep for measured polymorph H/D shifts. Commit 6890fc7 already searched for measured inter-polymorph D/H fractionation and found none. The known H/D transition shifts (KDP, NaOH, KOH, ice, delta-AlOOH disorder) are order-disorder or tunnelling cases outside the harmonic domain.
* The NaBH4 card, the 56-atom gibbsite run, and the McKenzie crossover lookup. The last compares gas-phase dimer O...O distances with solid-state O-H lengths, which is a weak mapping.
* The goethite / epsilon-FeOOH card goes out of the video and summary and stays in the repo.
* F05 magnitudes, F06 precision and F02 details: one clause each in the summary, none in the video.
* AlOOH temperature dependence: one card line at most, never a headline (see action 6).
* No "law", "discovery", "independent validation" or "autonomous team that uncovered".

**Sentence a judge should remember:**
"Swapping hydrogen for deuterium tips hydrogen-bonded solids toward the polymorph with the shorter O-H bonds: three ML potentials agree in 123 of 130 evaluations where the hydrogen bonds are moderate or strong, no pair is called the wrong way by the model majority, and the rule says where it stops working."

Organiser question, answered in the summary's opening: "Two days produced a testable, regime-limited rule, its failure boundary and a falsifiable pressure prediction. It is not a confirmed discovery, because this observable has never been measured."

## Why

* **Inconsistency costs more than new results gain.** I checked tonight and found the app, write-up, video script and fig4 each show a different population or wording:
  * The app prints the signal-cut count (`app/isoshift_app.py:84-88`, `y_min=0.1`; line 378). It reads 128/134, not the bound 123/130.
  * The write-up (line 9) and README (line 57) put the all-covalent signal-cut 129/150 next to the O-H no-cut headline. The matched O-H no-cut count is 124/146.
  * The video script still cites decision 04 and says "law", "four independent universal potentials", "about 0.13", "three independently trained", "within ten percent in slope", and "near 18 gigapascal" (the experimental high-T boundary, not the model's 300 K value of 8.8 to 14.1 GPa).
  * A judge who sees two of these finds two different stories. Every fix is cheap and can be done by agents tonight.
* **The provenance text contradicts itself.** README.md:145, writeup.md:23 and PROVENANCE.md:24 call `isoshift/pool.py` (62f1fde) the only event-time change to pre-event code. PROVENANCE.md:55 and the ledger record a second one, `harness/llm.py` (d250b20, Can approved, 22:10). This is an honesty item. The form asks exactly this before/during question.
* **A fresh clone breaks the app.** It reads `results/screen_pairs.csv`, `screen_structures.csv`, `screen_pairs_refined.csv` and `decompose_structures.csv`, and all four are untracked. `src/isoshift_event/card_temperature.py`, the source of a result we may show, is also untracked. App line 101 reads `results/raw/screen/...`, which is gitignored, so that cell must degrade gracefully.
* **More science adds little before freeze.** The only move that could add a full point to Novelty or Impact is a direct experimental check of F01. No polymorph isotope free energy or inter-polymorph D/H fractionation has been measured (decision 05; commit 6890fc7). M02 does give us a cheap Impact gain: it names the experiment that would test F01. Measured D/H fractionation between coexisting polymorphs gives the same double difference (n_H kT ln alpha = ddG_iso for full substitution). That is one sentence in the summary, not a new calculation.
* **Single-panel figure.** The deliverable is a one-page summary with a figure, and a judge spends seconds on it. Four panels shrink the 123/130 signal to a quarter of the area, and panels on F02, F05 and the card each need caveat text. fig4 (fixed) and the cards stay in the repo and the app.
* **Short judge sentence.** Argon's roughly 70-word, five-number sentence will not be remembered. The pair-level fact (62 right, 5 ties, 0 wrong of 67 pairs) is the strongest single answer to the obvious "correlated evaluations" objection, and no story file uses it yet.
* **Criteria.** CONTEXT.md lists scalability where this item lists novelty. The summary covers both with one sentence each:
  * Scalability: about 1750 structure-model phonon jobs on one 8 GB laptop GPU, plus a structure-only pre-screen (O...O ≤ 2.92 Å, 127/153) that applies to any hydrogen polymorph database.
  * Novelty: separation from the known stretch-bend competition (McKenzie), as in decision 05.

### Numbers re-checked tonight (`results/F01_cv.json`, `.venv` Python)

* `oh_unfiltered_strong`: 123/130 right, 67 pairs, 23 formulas, baseline 82/130. Definition: O-H, rmax ≥ 0.99 Å, |dX-H| ≥ 5 mÅ, no |ddF| cut, baseline from the leave-one-formula-out majority sign.
* Per model: ORB 56/56, MACE 51/57, MatterSim 16/17.
* Unique-pair majority: 62 right, 5 ties, 0 wrong of 67.
* `oh_split/all_eligible`: all regimes O-H 124/146, strong_0.99 O-H 123/130. The weak side is therefore 1/16.
* Signal-filtered pooled at 0.99 (all covalent): 128/134 right, baseline 84. That is what the app shows now.
* GPU at 23:20: 40 C, 371 MiB.
* Live processes:
  * One watchdog.
  * One MatterSim pool worker. It runs from `.venv-sevenn` because MatterSim needs e3nn ≥ 0.5 (`isoshift/calculators.py:4`).
  * One `card_temperature` job.
* No `card_temperature` output yet.
* `card_temperature.py` uses `TEMPS = 0..1500 K, step 50`. This is newer than decision 05's "QHA grid ends at 350 K" note.

## Where the members converged

* Freeze science now. Packaging, consistency and one figure carry the remaining score.
* Fix the app's 128/134 headline, the 129/150 population mix and the provenance omission. Commit the untracked CSVs and run a fresh-clone smoke test.
* Video v3 removes the decision-04 holdovers. Drop goethite and T-dependence from the video.
* Cut the write-up to one page and replace the "We claim none" opening with a positive but bounded framing.
* Lead with 123/130 (as bound), followed directly by the pair-level 62/5/0.
* SevenNet gets a hard cutoff with a pre-written 3-model fallback. The submission never waits on it.
* Before recording, a `git grep '{{'` gate must return empty.
* F04 is resolved at sign level (`docs/findings/F04-source-audit.md`, commit dc2a0dc). Astra's round-1 worry is closed unless the spectroscopy owner objects.

## Remaining disagreement

1. **Figure: single panel (Opus, Astra) vs 4-panel composite (Argon).** Ruled single panel plus inset, for the reasons above. Argon's panels survive as the fixed fig4 in the repo and as app tabs.
2. **AlOOH temperature dependence.** Argon dropped it in round 2, citing decision 05's 350 K note. Opus kept one line because `card_temperature.py` runs to 1500 K.
   * Ruling: one card line only, and only if all three hold. It finishes by 11:30. Its 300 K value reproduces the card (+1.13 ORB, +1.33 GPa MACE) within 0.05 GPa. Its script is committed.
   * The line carries a caveat: QHA at 1000 K sits in the delta-AlOOH proton-disorder regime and does not validate the 18 GPa boundary.
   * It stays out of the video and the headline.
3. **Duplicate SevenNet worker risk (Opus round 2).** Not observed. The `.venv-sevenn` process is the MatterSim worker (MatterSim lives in that env). The watchdog launches SevenNet only when no MACE, ORB or MatterSim heartbeat is live. Action 9 adds a 08:00 check: at most one sevenn worker.
4. **Judge sentence.** Argon wants the slope and the card in it. Ruled short (above). The slope and card belong in the summary body.
5. **Freeze acceptance thresholds.** Opus proposed 90% and 85% bands. Ruled below as "always report the frozen numbers; the wording changes only if a trigger fires", because the numbers are never ours to keep stale.

## Ordered action list for the conductor

| # | When | Action | Owner | Time | Done-check |
|---|---|---|---|---|---|
| 1 | Tonight 23:30 | **Provenance fix.** README.md:145, docs/story/writeup.md:23 and docs/PROVENANCE.md:24 list both event-time changes to pre-event code: `isoshift/pool.py` 62f1fde and `harness/llm.py` d250b20 (Can approved 22:10; read-only `--add-dir` for headless agy). | Sonnet agent | 15 min | `git grep -n "only event"` returns nothing; all three files name both hashes. |
| 2 | Tonight 23:45 | **Track app and figure inputs.** `git add` results/screen_pairs.csv, screen_structures.csv, screen_pairs_refined.csv, decompose_structures.csv and src/isoshift_event/card_temperature.py, plus refined_structures.csv only if a published script reads it. Make app line 101 (`results/raw/...`, gitignored) degrade with a message instead of an error. Confirm `.env` stays ignored. | Sonnet agent | 20 min | Fresh `git clone` into the scratchpad, then `.venv` python `-m marimo export html app/isoshift_app.py` succeeds and both tabs show non-empty tables; `git status` shows no untracked file read by `app/` or `figures/`. |
| 3 | Tonight 00:05 | **Number consistency.** <br>• App F01 tab: default to the O-H, \|dX-H\| ≥ 5 mÅ, no-target-cut population, showing 123/130 against the 82/130 fold baseline. Keep all-covalent signal-cut (128/134) as a labelled toggle. <br>• writeup.md:9, README.md:57 and F01-xh-length-rule.md: "without any threshold the rule holds in 124 of 146 O-H evaluations (85%)". Keep 129/150 only with its own label "all covalent pairs, signal cut". <br>• Add "\|Δ mean O-H\| ≥ 5 mÅ" to the headline sentence. <br>• README "measured regime boundary" becomes "model-derived regime boundary". <br>• Reconcile the MatterSim F03 CI to `results/stretch_check_summary.json`. | Sonnet agent, Opus review | 35 min | `grep -n "128" app/ docs/story/ README.md` finds no headline use; `grep -n "129 of 150"` hits carry the "signal cut" label; app headline reads 123 of 130. |
| 4 | Tonight 00:40 | **fig4 panel 3.** Use the O-H no-cut population: "strong 123/130 (baseline 82/130); weak 1/16". Fix the truncated title and change the axis unit "mA" to "mÅ". | Sonnet agent | 20 min | Read the regenerated PNG: title fully visible, counts match `F01_cv.json` `oh_unfiltered_strong` and `oh_split`. |
| 5 | Tonight 01:00 | **Video script v3.** <br>• Header cites decision 05. <br>• Use "three universal ML potentials; SevenNet in sign votes only", "a simple rule", "0.12 to 0.15 meV per H per thousandth of an angstrom", and "three separate models". <br>• "123 of 130 model evaluations when hydrogen bonds are moderate or strong; no pair called the wrong way; it fails when they are weak (1 of 16)". <br>• "Their stretch slope matches measured mineral spectra between O...O 2.5 and 2.8 Å." <br>• "The static energy gap cancels" in place of "most model errors cancel". <br>• Card: "the measured boundary near 18 GPa is at high temperature; our 300 K models put it at 9 to 14 GPa and agree deuteration raises it by about 1.1 to 1.3 GPa, a sign prediction outside the clean harmonic domain". <br>• Drop goethite and T-dependence. Add a 20 s app plus Bond-trace segment. <br>• Keep 430 to 460 spoken words. | Opus | 40 min | `grep -n -i -E "law\|independent\|within ten\|0\.13\|decisions/04" docs/story/video_script.md` returns empty; spoken word count is 460 or fewer. |
| 6 | Tonight 01:40 | **Commit the freeze rule to state/LEDGER.md before any new numbers are seen.** <br>• At Thu 12:00, or when the queue drains if earlier, run refine, decompose, analysis and rule_cv once. Report the frozen numbers whatever they are. <br>• Binding wording stays unless a trigger fires: the O-H strong side falls below 85%, or it is less than 20 points above its fold baseline, or any pair majority turns wrong. A trigger sends the wording to the chair. <br>• SevenNet: at 11:00, if 150 or more of its 192 jobs are done, its sign votes enter as a separately labelled line. Otherwise use "SevenNet runs did not finish before the compute freeze and are not used." Write both variants tonight. <br>• Temperature card: as ruled in disagreement 2. <br>Then stop for the night. | Opus | 15 min | Ledger commit timestamp earlier than any post-23:30 change to `results/F01_cv.json`. |
| 7 | Thu 08:00 | **Morning check.** Watchdog alive. At most one sevenn worker. GPU below 87 C. Pending queue count logged. Failed jobs listed (one MatterSim OOM so far). Can, while having coffee and only if not done last night: Moment login and team, the live form's summary length limit, the video host (public, no login). | Opus; Can 10 min | 20 min | Ledger line with queue counts; Can's answers recorded in the ledger. |
| 8 | Thu 11:00 to 12:30 | **Freeze.** <br>• Stop SevenNet launches at 11:00. Snapshot the inputs at 12:00 and run the pipeline once. <br>• One script fills the numbers in writeup, README, app and video from `results/F01_cv.json`. <br>• Commit the four CSVs again. | Opus | 90 min | `git grep -n "{{" docs/ README.md app/` returns empty; every displayed count matches the JSON; one freeze commit. |
| 9 | Thu 12:30 to 14:00 | **Headline figure** (`figures/fig_headline.png`; also the video shot at 1:15 to 2:05). <br>• Plot ddF_iso(300 K) per H against Δ mean O-H in mÅ, with a zero line. <br>• Strong side coloured by model; weak side grey, labelled "fails, 1/16"; ±5 mÅ dead zone shaded. <br>• Count box: "123/130 evaluations (baseline 82/130); pairs 62 right, 5 ties, 0 wrong". <br>• Inset: stretch +0.25 against bend/libration -0.12 meV/H per mÅ. <br>• Caption: eligibility, post-hoc 0.99 Å threshold (fold-stable), correlated evaluations. | Sonnet build, Opus review | 90 min | PNG legible at one-page width (check at 50% zoom); counts match the frozen JSON. |
| 10 | Thu 14:00 to 15:30 | **One-page summary** of 550 words or fewer (or the form limit, if smaller). The 1009-word version moves to `docs/story/writeup_long.md`, linked from the README. <br>• Opening: the organiser-question sentence above. <br>• Add the M02 sentence naming the direct experiment (inter-polymorph D/H fractionation). <br>• One scalability sentence and one novelty sentence. <br>• F02, F03, F04, F05 and F06 in one paragraph of about 90 words, failures kept visible. <br>• Before/during section with both event-time changes. | Opus | 90 min | `wc -w` 550 or fewer; no "We claim none", "law" or "discovery" as a claim; renders on one page as PDF with the figure. |
| 11 | Thu 15:30 to 17:30 | **marimo and Valency.** <br>• "Check a pair" tab: select a pair to see its O-H lengths, regime, predicted sign and each model's ddF. <br>• "How we know" trace: Bond query id, DOI, extracted value, second-reader correction, decision row. Use the brucite +0.31% case and show the single-pass precision (9 of 11 marked ok, 2 survived). <br>• Use cached data only; no live compute. | Sonnet build, Opus review | 2 h | Fresh-clone CPU-only `marimo export html` succeeds; both new tabs show content; Bond query id resolves in `logs/bond_queries.jsonl`. |
| 12 | Thu 17:30 to 22:00 | **Video.** Can reads v3 aloud with a timer: 3:50 or less, trimming the F03 line first. Record at 19:00. Make SRT captions from the script. Upload public by 22:00. | Can, Opus | 1.5 h Can | Public link opens logged out; runtime under 4:00. |
| 13 | Thu 23:00 to 00:30 | **Submit.** <br>• Secret scan (`.env`, keys) before the repo goes public; this needs Can's authorization. <br>• Check every link logged out. <br>• Keep an offline packet (summary PDF, links, form text). Submit by 00:30. <br>• The 02:00 hard stop is a buffer, not a plan. The form deadline is Fri 03:00 TRT. | Can, Opus | 90 min | Submission confirmation screenshot in the ledger. |

Total agent time tonight is about 2.5 h; Can's time tonight is zero. If tonight's pass overruns, actions 1 to 3 come first. Actions 4 and 5 can move to Thu 08:30 at the latest, because the video is recorded at 19:00.

## What would change this

* **The freeze rerun fires a trigger** (O-H strong side below 85%, less than 20 points above baseline, or a wrong pair majority). The wording goes back to the chair before the figure and summary are built, and actions 9 and 10 slip by up to an hour.
* **A clean, direct measurement turns up** without a search: a measured H/D shift of an ordered-to-ordered polymorph boundary, or an inter-polymorph D/H fractionation, for a pair in `results/rule_map.csv`. It is scored against the committed prediction, reported whatever the sign, and becomes the second line of the summary.
* **The live form's limit is much shorter than 550 words**, or it wants no figure. The summary shrinks to the opening, the headline and the before/during paragraph.
* **The fresh-clone smoke test fails on something not fixable by 14:00.** The app ships with a static HTML export as fallback, and the video shows the export.
* **Can cannot record at 19:00.** Opus produces a narrated-slide fallback from the v3 script and the headline figure by 21:00.
