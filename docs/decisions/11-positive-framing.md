# 11. Positive framing: replace the writeup.md and README openings with result-first text; video unchanged; "computational finding" yes, "discovery" and "first" no

Council: Opus, Astra, Gemini 4 Argon (two rounds). Chair: Opus. 22 Oct, after the compute freeze. Amends decision 06 action 10 (opening of the one-page summary) only. Decision 07 sentences, decision 05 claim rules and decision 09's video lock are unchanged.

## Can's question

"If something in our work could be called a discovery, can't we say it in a discovery-like way even though we did not measure it?"

Answer: yes in substance, no in the label. The strongest honest version leads with what is new and specific: the sign, the count against its baseline, where the rule fails, the one counterexample, and the two experiments that would test it, one of them with a predicted sign. Materials-science judges read "discovery" or "first" without a measurement as overclaiming; they read a specific, falsifiable computational result as strong. The limit stays, but as a clause that points to the test, not as a negation in sentence 2.

## Decision

1. **docs/story/writeup.md, line 3** becomes (2 sentences, 79 words):

   > In harmonic calculations with three ML potentials, deuteration favours the polymorph with shorter O-H bonds in 185 of 212 evaluations with moderate-to-strong hydrogen bonds (constant-sign baseline 131), fails with weak ones (2 of 20) and has one Al(OH)3 counterexample by pair majority; no measurement has tested it directly. Two would: D/H partitioning between coexisting polymorphs ([M02](../math/M02-bigeleisen-bridge.md)), and matched reversed-bracket AlOOH/AlOOD runs on the diaspore to δ-AlOOH transition, where the models predict a higher pressure for AlOOD (exploratory sign prediction).

   To stay within the 550-word cap (decision 06 action 10; the file is 549 now), three cuts go with it:
   * delete the whole `**Direct test.**` paragraph (its experiment and the M02 link are now in the opening; this also removes the unconditional "it equals the boundary isotope shift", which M02 says holds only when R = 0);
   * delete the last sentence of `**Limits.**`, " With weak hydrogen bonds it fails (2 of 20)." (the 2 of 20 is now in the opening);
   * delete the last sentence of the AlOOH card, " Falsifier: matched side-by-side reversed-bracket AlOOH and AlOOD runs; an opposite-sign shift refutes it." (the matched reversed-bracket test is now in the opening; CARD-AlOOH.md keeps the full falsifier).

   Chair's scratch build of exactly these edits: `wc -w` = 550, two sentences, no em or en dash, no " - ", no discovery, law, independent or first anywhere in the file, verbatim decision 07 headline still present.

2. **README.md, line 3** becomes (2 sentences, 97 words):

   > IsoShift computes harmonic H and D phonon free energies of crystal polymorphs with three universal ML potentials and finds that deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 evaluations with moderate-to-strong hydrogen bonds (constant-sign baseline 131), fails with weak ones (2 of 20) and has one Al(OH)3 counterexample by pair majority; no measurement has tested this rule directly. Two would: D/H partitioning between coexisting polymorphs ([M02](docs/math/M02-bigeleisen-bridge.md)), and matched reversed-bracket AlOOH/AlOOD runs on the diaspore to δ-AlOOH transition, where the models predict a pressure about 1 GPa higher for AlOOD (exploratory sign prediction).

   And on README line 5, delete the trailing sentence " One exploratory prediction: deuteration raises the diaspore to delta-AlOOH transition pressure by about 1 GPa." The chair checked that line 5 is then exactly "**Main finding (F01).** " plus the decision 07 headline.

3. **Video (docs/story/video_script.md): no change.** The hook (line 11) is the decision 07 verbatim hook, already leads with the result, says "in our calculations" and contains no "discovery". Decision 09 locks the narration byte for byte; the recording window is 16:30 to 20:00; narration stays at 462 words (cap 480).

4. **Words.** "Computational finding" is allowed (decision 05 item 2); "Main finding (F01)" as a heading stays. Bare "finding" with nothing implying measurement is fine in headings. "Discovery", "law", "first", "to our knowledge first", "new mechanism" and "independent" for the models stay out.

5. **"First" is not defensible.** McKenzie et al. 2014/2015 own the stretch-bend mechanism; Bourgeois et al. 2018 (115 metal hydrides) blocks "first large-scale isotope screen" (decision 05 item 10); Zhou, Kye and Harbison covered isotopomeric polymorphism; and no systematic search for a polymorph-level precedent was run, so "to our knowledge first" carries the same exposure. Novelty stays as the existing sentence: "new here is its polymorph-stability version, slope and failure boundary."

6. **Unchanged:** docs/story/writeup_long.md line 3 (the organiser sentence answers the organisers' "real discovery" question there, its decision 07 role), docs/story/moment_short.md, every decision 07 sentence, every number.

## Why

* The old writeup opening spends sentence 1 on the time budget ("Two days produced") and makes sentence 2 a negation whose memorable word is "discovery". The README opening describes software, not the result. Both undersell a specific result.
* Every number in the new text is frozen: 185/212 and baseline 131 (`results/F01_cv.json`, `oh_unfiltered_strong`, rechecked by the chair), 2 of 20 (decision 07), +1.13/+1.33 GPa at 300 K and +0.7 to +0.9 GPa near 1000 K behind "about 1 GPa" (CARD-AlOOH, decision 05). No new claim.
* "One Al(OH)3 counterexample by pair majority", not bare "one counterexample": the chair rechecked `posthoc_locators`; without mp-985293 the count is 177/184, so 7 wrong evaluations sit elsewhere, while all 10 wrong pair majorities contain mp-985293. The qualifier keeps the sentence exact.
* The limit is in sentence 1 as a clause ("no measurement has tested it directly"), so it is visible but sentence 2 is the forward test. This satisfies both readings of "not as the second sentence" (Argon's strict reading and Opus's).
* The weak-side count and both experiments move into the opening, which pays for the opening inside the word cap without dropping any caveat: the 2 of 20, the M02 test and the bracketing falsifier remain on the page.
* Dropping the "equals" sentence fixes a physics overstatement Astra raised: M02 gives n_H k_B T ln α_tr = ΔΔG_iso − R, so trace fractionation equals the full-substitution shift only when R = 0.

## Where the members converged

* Replace the writeup.md and README openings; keep the video unchanged (Opus R2, Argon R1 and R2, Astra R1).
* "Computational finding" acceptable; "first" in any form not defensible (all three, both rounds).
* Leave writeup_long.md line 3 and moment_short.md unchanged (Opus, Argon R2).
* Delete the trailing "about 1 GPa" sentence from README line 5 so it is the verbatim headline (Opus R2, Argon R2).
* Withdraw any 2:23 narration edit (Opus R2, Argon R2).

## Remaining disagreement

* **Counts in the opening.** Argon R2 and Astra R1 wanted no counts in line 3 because line 5 repeats them. Chair: counts stay. A judge may read only the opening, and 185 of 212 against 131 is the result; a "tends to favour" opening is weaker than the evidence. Accepted cost: the counts appear twice in adjacent paragraphs.
* **Word budget.** Argon R2's 69-word opening with no cuts would put the file near 586 by `wc -w`; Opus R2's 61-word opening dropped "exploratory" from the writeup sentence. The decided text keeps "exploratory sign prediction" and lands at 550 by trading the Direct test paragraph, the Limits 2 of 20 sentence and the card falsifier line.
* **Astra round 2** answered a different item (item 10, P10/F11) and did not address this question; its round 1 position (replace openings, video unchanged, finding yes, first no) is counted. Its F11 remarks are out of scope here.
* **Video 2:23 line** ("the isotope shift of a phase boundary equals the D/H fractionation") keeps the unconditional "equals" that M02 qualifies with R. Not changed, because decision 09 locks the narration and recording is imminent. Logged as a known shorthand; the written record (writeup, M02) is exact.

## Ordered actions for the conductor

| # | Action | Owner | Time | Done-check |
|---|---|---|---|---|
| 1 | Edit `docs/story/writeup.md`: replace line 3 with the exact text in Decision 1; delete the `**Direct test.**` paragraph and its blank line; delete " With weak hydrogen bonds it fails (2 of 20)." from Limits; delete " Falsifier: matched side-by-side reversed-bracket AlOOH and AlOOD runs; an opposite-sign shift refutes it." from the AlOOH card. | Opus (conductor) | 5 min | `wc -w docs/story/writeup.md` prints 550 or less; `grep -c "185 of 212 O-H model evaluations" docs/story/writeup.md` is 1; `grep -c "Direct test" docs/story/writeup.md` is 0. |
| 2 | Edit `README.md`: replace line 3 with the exact text in Decision 2; delete the trailing " One exploratory prediction: ... by about 1 GPa." from line 5. | Opus | 3 min | Line 5 equals "**Main finding (F01).** " plus the decision 07 headline (string compare in Python); `grep -c "about 1 GPa" README.md` is 1 (the opening). |
| 3 | Grep gate on both files. | Opus | 2 min | `git grep -n -i -E "discovery\|\blaw\b\|independent\|\bfirst\b\|Two days" -- README.md docs/story/writeup.md` returns nothing; `git grep -n -P "\x{2014}\|\x{2013}\| - " -- README.md docs/story/writeup.md` returns nothing (code spans excepted, if any); M02 link resolves (`docs/math/M02-bigeleisen-bridge.md` exists). |
| 4 | Video untouched. | Opus | 1 min | `git diff --stat -- docs/story/video_script.md` empty; narration still 462 words. |
| 5 | Record: add one line under the title of `docs/decisions/06-strategy-to-submission.md`: "Action 10 opening amended by [11](11-positive-framing.md)."; add the decision 11 line to `docs/INDEX.md`. | Opus | 3 min | `git grep -n "11-positive-framing" docs/decisions/06-strategy-to-submission.md docs/INDEX.md` returns two lines. |
| 6 | Commit only these files plus this decision: "docs: result-first openings for writeup and README (decision 11); no number or claim changed; video unchanged". Leave the unrelated working-tree changes (`src/isoshift_event/p10.py`, `results/post_freeze/*`, benchmark logs) out of the commit. No push without Can. | Opus | 2 min | `git show --stat HEAD` lists only README.md, docs/story/writeup.md, docs/decisions/06-strategy-to-submission.md, docs/decisions/11-positive-framing.md, docs/INDEX.md. |
| 7 | Tell Can in one short Turkish line: discovery wording stays out, the openings now lead with the result and the test; video script is unchanged for the 16:30 recording. | Opus | 1 min | Message sent in the session. |

Total about 17 minutes, no compute.

## What would change this

* A one-page form limit below 550 words, or a PDF render that spills past one page: cut the writeup's "(constant-sign baseline 131)" to "(baseline 131)" and the Scale sentence before touching the opening.
* Can still unrecorded and asking for a video change: only a new council may touch the narration (decision 09). The hook stays; the 2:23 "equals" shorthand is the one candidate.
* A measured polymorph isotope free energy, D/H partitioning between coexisting polymorphs, or an AlOOH/AlOOD bracketing result: then the opening reports agreement or refutation, and decision 05's ban on stronger words is reopened.
* A literature hit for a prior polymorph-level isotope stability rule: the novelty sentence shrinks (decision 05 risk 4); the openings themselves claim no priority and stand.
* F11/P10 prospective test meeting its predeclared bars: may enter the opening only through a separate council; it is partial now and stays out.

## Conductor amendment (22 Oct, after the chair's record)

The chair kept "first" out partly because "no polymorph-precedent search was run". That search finished while this council deliberated: 20 Valency Bond queries (logged in `logs/bond_queries.jsonl`) and 3 web searches found no earlier study that computes H/D free-energy differences between polymorph pairs at database scale, with or without ML potentials. The closest work is Bourgeois et al. 2018 (115 metal hydrides, formation, DFT, no polymorph pairs) and Du et al. 2026, arXiv:2610.11325 (iso-EPIGS, path-integral method, water and one oxalic acid crystal). An absence found by search supports "we found no", not "first". So: the openings stay exactly as decided above; the "What is new" section of README.md and docs/story/writeup.md may add one sentence, "A literature search (logged) found no earlier survey of H/D free-energy differences across polymorph pairs of the same compound.", and must cite Du et al. 2026. "First" and "to our knowledge, first" stay out. Pushing to the private remote follows the standing rule; making the repo public still needs Can.
