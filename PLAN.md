# IsoShift: 34-hour plan

Times are Turkey time. Official schedule (Moment): hacking may begin any time on Oct 21 anywhere on Earth, so we can start as soon as Can is ready (no need to wait for 17:00). Deadline Fri 23 Oct 03:00. Submit by 02:00 to keep a buffer. Block times below shift earlier accordingly.
Extra platform credits are listed in Slack #resources.

## Morning checklist for Can (before 17:00, ~30 min)
1. Materials Project API key: materialsproject.org → Dashboard → API key. Put it in `.env` as `MP_API_KEY=...` (never commit).
2. Valency MCP Bond: sign up at valency.io, connect to Claude Code (setup guide in #valency). Needed for the Valency prize and literature checks.
3. Join the hackathon Slack; read the kickoff video/notes when posted; check the submission form fields.
4. Read DECISION.md (10 min) and say go / no-go. Plan B is PackEvolve if you veto.

## Submission (Slack #general, Ben Blaiszik, 21 Oct)
- Submitted on the new OSI platform **Moment**: sign up early at scientificintelligence.org/onboarding?campaign=osi-hackathon-2026 (Globus preferred, Google login works via Globus; Auth0 fallback), create a team (solo = team of one).
- Fields: (1) link to social media post (the video goes here), (2) brief write-up with optional figure, (3) code repository link, (4) checkboxes for platforms used (tick Valency Bond, marimo).
- Code must be enough to show the work is real (Ben in #random); reusability is a bonus.
- Valency prize: use Bond in the project; help in #valency.

## Blocks
| Block | Time | Work | Exit check |
|---|---|---|---|
| 0. Kickoff | 17:00–18:00 | Read kickoff, confirm rules, lock scope, create `src/` for event code. | Rules OK |
| 1. Candidate pool | 18:00–21:00 | Agent builds H-polymorph pairs (MP + JARVIS), filters disorder/proton transfer, near-degenerate pairs (<25 meV/atom). Agent compiles validation set via Bond. | ≥30 pairs, ≥5 validation cases |
| 2. Validation first | 21:00–03:00 | Harmonic + QHA H/D for validation cases with 3 MLIPs. Compare isotope shifts to experiment, negative controls behave. MLIP vs DFT H-phonon spot checks. | **Gate (hour 10, ~03:00): sign/magnitude agree on harmonic-tractable cases → continue; else fallback framing** |
| 3. Overnight screen | 03:00–10:00 | Batch QHA over candidate pairs on GPU (runs unattended). Sleep. | Results cached |
| 4. Analysis | 10:00–15:00 | Ensemble agreement filter, ΔT_iso ranking, uncertainty, novelty check of top 10 via Bond, figure. | Top-10 table + main figure |
| 5. Tool + app | 15:00–19:00 | marimo app: CIF in → H/D free-energy crossing map; README; reproducible run script. | Fresh-clone run works |
| 6. Write-up | 19:00–23:00 | One-page summary with figure; record 4-min video; public repo; LinkedIn/X thread. | All links public, no login |
| 7. Submit | 23:00–02:00 | Form (prior work vs built during event stated honestly), buffer. | Submitted |

## Main figure (draft)
Left: validation (computed vs measured isotope shift for known cases, negative controls marked). Right: candidate map (polymorph gap vs ΔΔF_iso, ensemble error bars, top candidates labelled).

## Video outline (≤4 min)
Publishing: default is an unlisted YouTube video (no face, screen only) whose link goes in the Moment form; Can does not want to post it on LinkedIn/X for now and may decide later.
Format (Can's choice): screen recording with OBS, Can narrates in his own voice. Claude prepares the script (Turkish draft + English final), slides/figures and demo steps beforehand; one rehearsal, then record.
1. Hook (20 s): "Swap H for D and a crystal can choose a different structure. Where does that happen?"
2. Why it's hard (30 s): effect is meV, model errors are larger; trick: isotope shift from mass-independent force constants, ensemble of AI potentials.
3. Validation (60 s): known cases reproduced, negative controls honestly flagged.
4. Discovery (60 s): top isotope-tunable candidates, predicted transition shifts with error bars, cheap D2O experiments to test.
5. Tool demo (40 s): marimo app.
6. Close (10 s): open code, what's next.

## Disclosure for the form
Organizer guidance (Slack #2026-event, 18 Oct): pre-existing code/datasets are allowed but must be explicitly stated; judging is based on what was implemented during the hackathon. So the write-up must clearly separate pre-event infrastructure from event work.
Before event: generic LLM harness (harness/), topic harness (isoshift/: MLIP calculators, phonon mass override, QHA, comparison utilities), environment, feasibility tests, brainstorm docs. During event: candidate curation, validation, screening, analysis, app, write-up.
