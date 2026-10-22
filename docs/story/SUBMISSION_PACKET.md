# Moment submission packet

Ready-to-paste fields. Wording follows decision 07 ([07-freeze-wording.md](../decisions/07-freeze-wording.md)); numbers come from `results/F01_cv.json`, `docs/FAQ.md` and the files linked there. Character counts are for the text inside each block.

## Moment form (read live by the conductor, 22 Oct 14:25 TRT)

* Fields: social post link (required), write-up, repository URL (required, public, README checkbox), cover/gallery images (optional, up to 8), tracks, rules confirmation.
* Write-up field: Markdown, "up to a page, with figures", no character limit shown; images are pasted inline; LaTeX with `$...$`; `## ` lines become headings. The first paragraph is the gallery card text and leads the entry.
* Cover image: `figures/fig_headline.png`.
* Tracks: tick **Valency** (the work uses the Valency MCP Bond platform) and **Marimo** only. Do not tick Adaption; IsoShift does not use it.
* Entries can be edited until the deadline, Thu 22 Oct 7:00 PM CDT = Fri 23 Oct 03:00 TRT.

Team page "Your idea" (replaces the outdated text that begins "Mapping where hydrogen/deuterium isotope substitution shifts polymorph phase transitions"; 181 characters):

```
In harmonic calculations with three ML potentials, deuteration favours the polymorph with shorter O-H bonds in 185 of 212 evaluations with moderate-to-strong H bonds (baseline 131).
```

## (a) YouTube

Video URL (paste into the Moment form): https://youtu.be/X8ckZ7dV40Y. Uploaded with the title and description of `docs/story/video/RECORDING.md` and `captions.srt` as English subtitles.

Title (as published):

```
The short-bond rule: deuteration favours the polymorph with shorter O-H bonds
```

Description (as published, 3:47 video):

```
The short-bond rule: in crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds. Found at OSI Hackathon 2026 in a screen of 220 polymorph pairs with three universal ML potentials (MACE, ORB, MatterSim): it holds in 185 of 212 model evaluations, against 131 for a constant-sign baseline, and it fails for weak hydrogen bonds. It predicts that deuteration raises the diaspore to δ-AlOOH transition by about 1 GPa (exploratory sign prediction). Not yet tested experimentally; D/H partitioning between coexisting polymorphs would test it.

Code, data and decision records: https://github.com/canerganis/isoshift

AI disclosure: the calculations, literature search and drafts were produced by AI agents working under my direction; every query and decision is logged in the repository. Music and visuals were generated in code.
```

## (b) Write-up

Paste `docs/story/writeup.md` (word count by wc -w; the form shows no word limit, only "up to a page, with figures"; decision 14 cap 760). Its first paragraph becomes the gallery card and stands alone: the result, its regime, the counterexample, and the two experiments that would test it. Where the file has `![Headline figure](../../figures/fig_headline.png)`, paste `figures/fig_headline.png` inline as an image. Other links in the file are absolute GitHub URLs, so they work once the repo is public. `docs/story/moment_short.md` is the fallback only if a limit appears.

## (c) Valency Bond usage

```
Literature agents used Valency Bond to find measured values (H/D cell volumes, mineral D/H fractionation, ice boundaries) and logged every query in logs/bond_queries.jsonl: 182 rows, 85 sweep rows plus 97 agent rows (20 prior-art checks, 26 atlas-test queries plus one re-log, 9 ice-boundary queries, 41 other validation lookups; recount: python -m src.isoshift_event.bond_counts). Single-pass extraction needed checking: of 11 sweep items, 9 came back "ok" and 2 became quantitative targets, and the board caught a reference value off by 2x. Not every measured value came through Bond; the provenance table with log line numbers is in docs/story/agent_extraction_audit.md. The How we know tab of the app follows the brucite value from the Bond sweep queries to the gate ruling. A prior-art search of 20 Bond queries found no earlier survey of H/D free-energy differences across polymorph pairs; the closest recent work, Du et al. 2026 (arXiv:2610.11325), is cited.
```

## (d) marimo usage

```
The marimo app opens on the frozen 185 of 212 banner with five tabs below it: F01 isotope rule, Benchmark & stretch check, Check a pair, How we know and Legacy explorer. Check a pair shows each model's isotope free energy, the rule's call, whether the pair is inside the F01 headline, and the stretch and bend split for a screened pair, with diaspore against delta-AlOOH as the default. All data are precomputed, so it runs without a GPU: marimo run app/isoshift_app.py
```

## (e) Before and after the event

```
Before the event: everything reachable from git tag pre-event-baseline (commit a5aff16, 21 Oct 2026 14:19 +0300), namely the generic LLM harness (harness/), the isotope harness with MLIP calculators, phonon mass override, QHA and a GPU worker pool (isoshift/), prefetched data and planning documents. During the event: everything in src/isoshift_event/ and app/, the screen, results, findings, predictions, decision records and the video. Two event-time changes touched pre-event code: isoshift/pool.py (commit 62f1fde, Windows file-replace collisions) and harness/llm.py (commit d250b20, read-only repo access for the headless Gemini council call). Full list with commits and times: docs/PROVENANCE.md.
```

## (f) Social post (required by Moment: public, with the video inside; LinkedIn draft in linkedin_post.md)

```
IsoShift: in harmonic calculations with three ML potentials, deuteration favours the polymorph with shorter O-H bonds in 185 of 212 evaluations with moderate-to-strong H bonds (baseline 131). It fails with weak ones. Untested by experiment. https://github.com/canerganis/isoshift
```
