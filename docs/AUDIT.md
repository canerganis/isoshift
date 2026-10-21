# Repository audit (21 Oct, late evening)

Scope: gaps, inconsistencies and loose ends a judge or a fresh reader would hit. No scientific claim was changed. Files owned by agents running at the same time (README, writeup, PROVENANCE, app, fig4, F01, F03, P05/F07 and the ice code, LEDGER, GOAL) were not edited; their issues are listed at the end.

## What was checked

1. **Tests.** `.venv/Scripts/python.exe -m pytest -q` on the full suite.
2. **Markdown under `docs/` plus README, DATA_SOURCES and app/README.** Relative links and backticked repo paths against the working tree and against `git ls-files`; `{{` placeholders and TODO/FIXME/TBD in non-story docs; wording that decision 05 removed ("discovery", "law", "independent", "95.5", "128/134" as headline, "upper estimate", "not an artefact"); numbers in the findings against `results/card_alooh_pressure.json`, `results/stretch_check_summary.json`, `results/P04_comparison.json`, `results/replicate_f01.json` and `results/validation/volume_isotope.csv`.
3. **Untracked files and secrets.** `git status`; which untracked files are read by code or cited by docs; `.env` is ignored (`git check-ignore`) and never committed; the value of `MP_API_KEY` from `.env` does not occur in any tracked file or in history (`git log -S`); `git grep -i -E "api[_-]?key|token|secret|password"` hits are all instructions or variable names (PLAN.md, START.md, fetch_mp.py, workflow text), none is a value.
4. **Evidence navigation.** New `docs/INDEX.md`; a status line at the top of every finding not owned by another agent.
5. **Code hygiene in `src/isoshift_event`.** Every module has a docstring and a `__main__` guard; every module imports cleanly; `--help` works for all argparse CLIs; no `breakpoint`, `pdb` or debug prints (the remaining prints are CLI output).

## What was fixed

| commit | change |
|---|---|
| 161ccc3 | `pairs.py`: the space-group cache was keyed by `id(crystal)` only. After a crystal is freed, a new structure can get the same id and receive a stale space group, which blocks or allows a merge wrongly. This made `test_flags_propagate_without_excluding_pair` fail in the full suite but pass alone. The cache entry now holds the crystal and checks identity. Within one `build_pairs` call every crystal stays referenced, so the committed `pairs.csv` (one call) is not affected. |
| c70d8b5 | `validate.py`: `python -m src.isoshift_event.validate --help`, which README documents, raised `KeyError`; it now prints the module usage. |
| 0722a64 | Status line at the top of F02, F04, F04 source audit, F05, F06. F02: ice overestimate "4 to 10x" corrected to "4 to 11x" (current CSV: -0.29 to -0.80% against -0.075%, ratio 3.8 to 10.7; decision 01 also says 4 to 11). F05: discloses that the P04 comparison rule was first committed together with the result (90ad4cd), so its precedence rests on the ledger, not on a separate commit. |
| 3427eb4 | Tracked the two logs the docs cite (`results/replicate_f01.log` for F06, `results/validation_run.log` for decision 01). Ignored regenerable outputs nothing reads (`results/screen_structures_extended.csv` 13 MB, `results/refined_structures.csv`) and local run logs. |
| 345d80c | `docs/INDEX.md` (reading order, findings with status, predictions with commit hash and time, decisions, math notes) and this file. |

Test result after the fixes: 161 passed, 1 deselected with `-m "not live"`. The one live test (`test_openalex_live`) fails with HTTP 429 from OpenAlex when run; that is the network, not the code.

Left untracked on purpose: `src/isoshift_event/ice_boundary.py` and two ice CIFs under `data/isoshift/validation_structures/prim/` (ice sprint agent, in progress).

## Open issues for the owners

| file | line | problem | suggested fix |
|---|---|---|---|
| README.md | 91 | "measured over hundreds of crystal pairs with three independent ML potentials" contradicts decision 05 (197 pairs; "separate models, not independent validations"). | "computed over 197 crystal pairs with three separate ML potentials". **Done.** |
| README.md | 19 | "Four universal MLIPs act as an ensemble" next to a headline that uses three. | Add "(SevenNet in sign votes only)" as in decision 06. **Done.** |
| README.md | 55 to 57 | Units "per mA", "0.99 A" while the headline uses mÅ and Å. | Use mÅ and Å throughout the Results section. **Done (mÅ and Å in the F01 bullets).** |
| README.md | 71 | The F04 spectroscopy sentence sits inside the "Candidate card" paragraph. | Give F04 its own `### F04` heading with the link. **Done (own F04 heading).** |
| README.md | 75 | "and the comparison rule before the comparison" overstates the git record: the rule was committed with the result (90ad4cd). | "the comparison rule was written before the comparison and committed with the result (timing note in F05)". **Done (rule committed with the result, 90ad4cd; predictions f3ac0ac).** |
| README.md | 85 to 91 | "Prior work" and "Novelty" repeat the same McKenzie and Bourgeois paragraph with different wording. | Keep the "Prior work" paragraph (decision 05 wording) and drop or shorten "Novelty". **Open: left for the README owner (editorial; wording in Novelty already fixed).** |
| README.md | How to run | No test command; a plain `pytest` hits the live OpenAlex test, which fails on rate limits. | Add `.venv/Scripts/python.exe -m pytest -q -m "not live"`. (`pytest.ini` is pre-event code, so changing its defaults would be a third event-time change to pre-event code; not done.) **Done (Tests line).** |
| docs/findings/F01-xh-length-rule.md | 1 | No status line at the top. | Add "**Status: computed (three MLIPs; no polymorph isotope free energy has been measured).**" under the title. **Done.** |
| docs/findings/F01-xh-length-rule.md | 33 | "Three independently trained universal potentials" in the older section. | "Three separately trained", matching decision 05. **Done.** |
| docs/findings/F01-xh-length-rule.md | 35 | "over hundreds of real and hypothetical crystal pairs". | "over 197 crystal pairs". **Done.** |
| docs/findings/F03-stretch-vs-experiment.md | 1 | No status line; the title "reproduces the measured ... correlation" is stronger than the decision 05 sentence. | Add "**Status: tested (consistency check of the stretch slope, O...O 2.50 to 2.80 Å; not a test of isotope free energies).**" and title it "is consistent with". **Done (status line, title).** |
| docs/findings/F03-stretch-vs-experiment.md | 12 | "All three potentials follow the measured curve over 2.5 to 3.2 A" conflicts with the windowed result (two models 2 to 3 times too steep above 2.80 Å). | Limit the sentence to the mean residuals and point to the windowed section. **Done.** |
| docs/findings/CARD-AlOOH.md | 5, 20 | Statement and caveats say "beyond the 300 K calculation", but commit 2529442 added a 0 to 1500 K section; the statement names two models while that section has three. | Per decision 06 ruling 2: one line in the statement with the 1000 K values and the proton-disorder caveat, or keep the statement at 300 K and say the temperature section is supplementary. **Done (1000 K shift +0.7 to +0.9 GPa, three models, proton-disorder caveat).** |
| state/GOAL.md | 12, 21 | "Law" and "independent MLIPs" in S2 and the fallback line, which decisions 05 and 06 removed. | "Rule" and "separate MLIPs", or mark both rows as historical like line 1. **Done (also S3 row).** |
| state/GOAL.md | 23 | "superseded by the action list in docs/decisions/04-discovery-claim.md": the current plan is decision 06. | Point to `docs/decisions/06-strategy-to-submission.md`. **Done.** |
| docs/decisions/04-discovery-claim.md | 83 | Done-check names `docs/decisions/04-final-claims.md`, which never existed (the record became decision 05). | Historical record, left as is; INDEX explains it. An erratum line is optional. **Left as is (historical record).** |
| docs/WORKFLOW.md | 8 | Names `state/ledger.json`, which was never created (only `state/LEDGER.md`). | Pre-event planning document; optional erratum. **Left as is (pre-event planning document).** |
| docs/specs/screen.md | 35 | Names `stability.py`; the module is `stabilize.py`. | Pre-implementation spec; optional erratum. **Left as is (pre-implementation spec).** |
| docs/decisions/06-strategy-to-submission.md | 95, 96 | `figures/fig_headline.png` and `docs/story/writeup_long.md` do not exist yet. | Planned outputs for Thu; check they exist before submission (`docs/story/video_script.md:41` also cites the figure). **Open: planned outputs, check they exist before submission.** |
