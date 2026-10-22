# 10. CPU-only discovery study: NONE. No new study is registered. F11 (P10) stays the one prospective test, and its write-up must prepare for the clean-rule outcome.

Chair: Opus, 22 Oct, about 13:15 TRT. Members: Opus, Astra, Gemini 4 Argon (rounds 1 and 2, all answered). Weighed by argument, not by vote; Astra carries the most weight on physics and math. The chair recomputed every number this decision depends on from files on disk, with `chk.py` (session scratchpad) reading `results/post_freeze/P10_predictions.csv`, `results/post_freeze/P10_decompose_structures.csv`, `results/raw/p10/{mace,orb,mattersim}/` and `results/decompose_structures.csv`. The 1616-row static-energy statistics (median |dE_static| 5.96 meV/atom, median |ddF_iso(300 K)| 0.21, inter-model SD of dE 2.49) were computed independently by Opus and Argon and agree; the chair did not recompute them.

Binding frame: decision 07 headline unchanged; decisions 05 (no "discovery" wording), 08 and 09 (post-freeze addenda only, predictions committed before outcomes) apply. Nothing here edits `docs/predictions/P10_prospective.md`, `results/post_freeze/P10_predictions.csv` or any frozen file.

## Decision

1. **No new CPU study.** None of the four options is run: not the isotope-switchable polymorph list, not a measured-transition dT_iso study, not an F09 crossover claim, and not the P12 slope/compensation test that Opus proposed in the deliberation round.
2. **The genuine prediction-first experiment of this submission is F11 (P10), already running.** It predicted the sign of ddF_iso on 42 never-computed pairs before any phonon job. The remaining hours go to scoring it honestly, not to a fourth study.
3. **Descriptive slope and compensation go inside F11** under a heading that says they were not predeclared, with the exposure disclosed (below). They carry no verdict.
4. The mp-985293 transfer call (Opus's Q-C) is **dropped**: raw P10 outputs for mp-27540 and mp-985293 appeared at 13:10 to 13:11, during this decision, so it can no longer be registered blind.

## Why

**(1) The switchable-polymorph list is decided by model noise.** Astra's algebra settles it. With g = G_H(b) - G_H(a) and q = [G_D(b) - G_H(b)] - [G_D(a) - G_H(a)], deuteration flips the order only when g(g + q) < 0, which needs opposite signs of g and q and |g| < |q|; the proposed |dF_H| < |ddF_iso| condition alone is not enough. An additive static-energy error e leaves the switch intact only when |e| < min(|g|, |g + q|) <= |q|/2, which is 0.05 to 1 meV/atom for q of 0.1 to 2 meV/atom. The three MLIPs disagree on dE_static for the same pair by a median SD of 2.49 meV/atom, against 0.16 for ddF_iso, and they share PBE training data, so their errors are not independent. "2 of 3 models agree" does not fix this. Argon found only 2 of 965 clean pairs pass the predicate, both hypothetical JARVIS-only phases with no ICSD entry. The literature arm would repeat F10 (26 rows, 0 scored: 22 E1 order-disorder or tunnelling, 2 E3, 2 unmappable); NaOD, KDP, squaric acid and ice are all E1, and oxalic acid and squaric acid are carbon-bearing and excluded at pair construction.

**(2) The anchored dT_iso study is the right physics with no target.** At measured H coexistence, dT = q(T_H)/dS_H (dT[K] = 96.4853 N q[meV/atom] / dS_H[J mol^-1 K^-1]) and dP[GPa] = -0.1602177 q[meV/f.u.] / dV[Å^3/f.u.]. This removes the static offset (not the error in q). But the eligible ordered-to-ordered pairs are used up: ice in F07, boehmite-diaspore in F12, delta-AlOOH and epsilon-FeOOH are proton-disordering transitions (E1), and the rest of the F10 list is E1, E3 or has no reversible solid-solid T_H below 600 K. Astra withdrew this option in round 2. Argon's version (ddF(300 K)/dS_vib,H(300 K)) is not anchored at a measured T_t and divides by a model entropy, so it is a table, not a test; rejected.

**(3) F09 crossovers cannot be re-labelled prospective.** They were computed and inspected (decision 09), they solve q(T) = 0 rather than g(T) = 0, and they span about 200 K across models above the Al(OH)3 dehydroxylation range. Unanimous.

**(4) P12 fails its own coverage gate before it can be registered.** This is the deciding point; the chair checked it rather than taking either side's word.
* Exposure. At 13:12, of 111 P10 primary evaluations, 24 are already decomposed (orders 1 to 8 and 42), 56 more have a raw phonon file for at least one member in some model, and only **31 rows, 13 pairs, 10 formulas** have no output at all. Raw JSON holds the H and D free energies, so a row with raw output is not blind (Astra). The blind pool lost 6 rows in the 20 minutes of this decision and will shrink further before any commit could land; every Al(OH)3 row is now exposed.
* Clean rule. P10 section 5 counts a member as not clean when quadrature and direct F_D - F_H differ by 0.01 meV/atom or more. Of the 24 decomposed primary rows, **only 5 pass** (order 42 HIO3 and order 7). The per-structure gaps reach 0.11 to 0.37 meV/atom on mp-24263, mp-706579, mp-721062 and mp-1205457, which is the size of the signal. In `decompose.py` the quadrature integrates |ω| while the direct value comes from phonopy's `helmholtz_free_energy`; Argon attributes the gap to soft modes treated differently by the two paths, which fits the code but the chair did not trace the phonopy side. The remaining blind pool is mostly the KH2PO4, NaH2PO4 and TlH2PO4 short-H-bond family, the same chemistry that failed clean in the exposed rows. Astra's gate (>= 30 eligible evaluations, 12 pairs, 6 formulas, >= 90% eligibility) would almost certainly end INCONCLUSIVE.
* Contamination. Argon computed pooled C = 0.285 on the 24 exposed rows during the council. Any compensation window chosen now is set after seeing a sample from the same population; Opus's [0.35, 0.70] window would be a known self-goal or would have to move after the fact. Neither is prediction-first.
* So P12 would cost the conductor about 3 hours on a test whose most likely predeclared outcome is "below the size bar", during the video block. Argon's clutter objection holds once these numbers are in.

**(5) F11 needs a warning, not a new study.** By the rule already committed in P10 section 5, 19 of the 24 decomposed primary rows are "not right" before any sign is read. The pooled-accuracy ceiling is already (111 - 19)/111 = 82.9% even if every other row were clean and right, against a 75% bar; with the clean pass rate seen so far, the primary bar is likely to fail on cleanliness, not on sign. The rule was committed before the data and must not change. P10 section 5 already lists the per-protocol (clean-only) count as a reported, non-scored number, so both numbers will appear.

## Where the members converged

* Reject the switchable-polymorph list (all three; Astra's g(g + q) < 0 and |q|/2 tolerance adopted as the formal reason).
* Reject re-labelling F09 crossovers as a prediction (all three).
* The anchored dT_iso = q/dS_H is the only physically valid bridge from ddF_iso to a phase boundary, and no unexposed eligible pair exists for it now (Astra withdrew it in round 2; Argon closed its gate as NO_ELIGIBLE_CASE; Opus called it optional at most).
* Wording: no "discovery", no "validated"; any model-internal transfer is only that.
* Frozen surfaces stay untouched.

## Remaining disagreement

* Opus (0.72) still wanted P12 on blind rows. Astra (0.85) accepted P12 only behind a coverage and timing gate and said "None" if it fails. Argon (0.97) said None. The chair's recount shows Astra's gate fails, so Astra's conditional position lands on None. Opus's case rested on 87 blind rows; that count treated phonon-complete but undecomposed rows as blind, which Astra correctly rejected, and it did not include the clean rule.
* Whether the |ω| vs direct gap is a defect worth fixing. Not ruled here: changing it now would alter P10's committed scoring. F11 may add a clearly labelled sensitivity line (gap per structure, count of rows lost to it); it may not re-score.
* Opus's mp-985293 anomaly claim (the counterexample belongs to the structure, not its partners) remains an untested idea; recorded, not pursued.

## Ordered action list for the conductor

| # | Action | Owner | Time | Done-check |
|---|---|---|---|---|
| 1 | Commit this decision file and one INDEX row for decision 10. Commit the uncommitted incremental-decompose patch in `src/isoshift_event/p10.py` separately, with a message saying it only skips already-decomposed rows from the same force-constant cache and does not change any value. | Conductor | 10 min | `git log -1 -- docs/decisions/10-cpu-discovery-study.md` shows the commit; `git diff -- src/isoshift_event/p10.py` empty after its own commit. |
| 2 | Do not register P12, Q-C, a switchable list or a dT_iso study. Do not add jobs, reorder or cut the P10 queue for any reason this decision raised. | Conductor | 0 | No new file under `docs/predictions/` after `P11_*`; `results/queue/p10` order unchanged. |
| 3 | After the 16:22 GPU batch: run `p10.py decompose` and `p10.py score` exactly as committed. Write F11 with the predeclared verdict first, the not-clean count and its causes by structure second, then the per-protocol clean-only count that section 5 already names. Rows from the 20:00 to 21:30 window are added once with the same commands, by 22:30. | Conductor | 45 min | `git diff <P10 commit>..HEAD -- docs/predictions/P10_prospective.md results/post_freeze/P10_predictions.csv` empty; F11 reports `n_primary_total` and `n_primary_scored` (clean) side by side. |
| 4 | Prepare the F11 wording for a primary-bar FAIL on cleanliness: say the sign rule was tested on new pairs, how many rows failed the predeclared numerical-cleanliness rule (19 of the first 24 already did), and what the clean rows show, without re-scoring. | Conductor | 20 min | The F11 verdict line uses the predeclared bar; `grep -ciE "discover|validated" docs/findings/F11-*.md` returns 0. |
| 5 | Optional, only if 1 to 4 are done: a section "Descriptive, not predeclared" in F11 with pooled slope of ddF/H on Δ mean O-H, per-model slopes and pooled C on clean rows, and a disclosure that a council member computed C = 0.285 on orders 1 to 8 and 42 during decision 10. No verdict, no window. | Conductor | 20 min | Heading text present; no number from it in README, video or the one-page summary. |
| 6 | Tell Can in two sentences: a "deuteration flips the stable polymorph" list would be decided by model energy noise ten times larger than the isotope effect, and the real prediction-first attempt is F11, which predicted new pairs before computing them and will be reported whichever way it falls. | Conductor | 5 min | Message sent in chat. |
| 7 | Frozen-surface check before submission. | Conductor | 5 min | `git diff --stat b291359..HEAD -- README.md docs/findings/F01-xh-length-rule.md results/decompose_pairs.csv results/decompose_structures.csv results/F01_cv.json docs/story/video_script.md figures/fig_headline.png` shows only changes authorized by earlier decisions (none from this one). |

## What would change this

* Someone names, before 15:00 and without consulting H/D outcomes, an ordered, experimentally mapped pair with cached clean force constants, a measured first-order H transition below 600 K with ΔH or ΔS and uncertainties, and D data nobody on the team has seen. Then Astra's anchored dT_iso protocol runs with a 60-minute cap, files under new paths only.
* Can explicitly overrides "None" in chat. Then the only admissible study is Astra's gated slope/compensation transfer on rows with no raw output at registration, with its coverage gate unchanged and the C window disclosed as set after the 0.285 exposure.
* The P10 queue turns out not to have reached orders 17 to 41 by 16:22 and the clean rate on new rows is far higher than 5 of 24. That still does not reopen P12 (outcomes would already exist); it only changes how F11 reads.
