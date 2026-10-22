# Moment submission packet

Ready-to-paste fields. Wording follows decision 07 ([07-freeze-wording.md](../decisions/07-freeze-wording.md)); numbers come from `results/F01_cv.json`, `docs/FAQ.md` and the files linked there. Character counts are for the text inside each block.

## (a) YouTube

Title:

```
IsoShift: deuteration and polymorph stability, 185 of 212 model evaluations
```

Description (chapters from the time column of `docs/story/video_script.md`):

```
In harmonic calculations with three ML potentials (MACE, ORB, MatterSim), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 evaluations with moderate-to-strong hydrogen bonds (constant-sign baseline 131). It fails with weak ones (2 of 20), and all 10 pairs the model majority calls wrong involve one Al(OH)3 structure. No measurement has tested the rule directly. AI agents ran the work, with Valency Bond for the literature and marimo for the app.

Code, data and decisions: https://github.com/canerganis/isoshift

0:00 The rule
0:21 Method
0:48 Evidence
1:37 Stretch check
1:55 AlOOH prediction
2:23 How to test it
2:39 AI process
3:08 marimo app
3:21 Limits
```

Thumbnail text:

```
H to D: 185 of 212 model evaluations
```

## (b) Write-up

Paste `docs/story/writeup.md`. If the field limit is smaller, use `docs/story/moment_short.md`.

## (c) Valency Bond usage

```
Literature agents used Valency Bond to find measured values (H/D cell volumes, mineral D/H fractionation, ice boundaries) and logged every query: 182 entries in logs/bond_queries.jsonl. The How we know tab of the app traces one value end to end for brucite: Bond query, DOI and quote, model result, gate ruling. A prior-art search of 20 Bond queries plus three web searches found no earlier survey of H/D free-energy differences across polymorph pairs; the closest recent work, Du et al. 2026 (arXiv:2610.11325), is cited.
```

## (d) marimo usage

```
The marimo app opens on the frozen 185 of 212 banner with five tabs below it: F01 isotope rule, Benchmark & atlas, Check a pair, How we know and Legacy explorer. Check a pair shows each model's isotope free energy, the rule's call and the stretch and bend split for a screened pair, with diaspore against delta-AlOOH as the default. All data are precomputed, so it runs without a GPU: marimo run app/isoshift_app.py
```

## (e) Before and after the event

```
Before the event: everything reachable from git tag pre-event-baseline (commit a5aff16, 21 Oct 2026 14:19 +0300), namely the generic LLM harness (harness/), the isotope harness with MLIP calculators, phonon mass override, QHA and a GPU worker pool (isoshift/), prefetched data and planning documents. During the event: everything in src/isoshift_event/ and app/, the screen, results, findings, predictions, decision records and the video. Two event-time changes touched pre-event code: isoshift/pool.py (commit 62f1fde, Windows file-replace collisions) and harness/llm.py (commit d250b20, read-only repo access for the headless Gemini council call). Full list with commits and times: docs/PROVENANCE.md.
```

## (f) Social post (optional, X or LinkedIn)

```
IsoShift: in harmonic calculations with three ML potentials, deuteration favours the polymorph with shorter O-H bonds in 185 of 212 evaluations with moderate-to-strong H bonds (baseline 131). It fails with weak ones. Untested by experiment. https://github.com/canerganis/isoshift
```
