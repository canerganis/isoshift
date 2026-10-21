# Start here (new session)

## Handover from the planning session (21 Oct afternoon)
Can gives the start signal; nothing starts on its own. On "başla":
1. Tag the last pre-event commit: `git tag pre-event-baseline` (PLAN.md P8). Then event work only in `src/` and `app/`.
2. Read `PLAN.md` from "Execution plan (v3)" to the cut list: owners, effort policy, advisory board, final authority (Opus decides), Astra for physics/math, Sonnet/Haiku for workers and scans, parallel tracks, **Pre-flight decisions P1 to P9 (binding)**. Then `docs/WORKFLOW.md`.
3. Orchestra is ready and tested: `.claude/workflows/` has `board`, `mathcheck` (tested, Astra and Opus agreed), `build`, `sweep`. Run with Workflow `{scriptPath: ".claude/workflows/<name>.js", args: {...}}`. `harness.cli` / `ask(..., effort="xhigh")` call Astra and Gemini (both tested live). Apply P7 (trimmed ceremony) when launching them.
4. Valency Bond works in Claude (`mcp__valency__*`, `list_sources` OK) and in Codex. Log Bond queries to `logs/bond_queries.jsonl`.
5. Data ready (`data/isoshift/PREFETCH.md`): 42 validation CIFs with index.json, DFT phonon references from Petretto (CC0), MDR phonondb and MP (40 each, local only). Open: confirm diaspore/boehmite and ice Ih labels.
6. GPU pool `isoshift/pool.py` (persistent workers, ~35 s model load saved per job) was being built by the `build` workflow in the planning session; check `git log` for "src: pool-persistent-gpu-worker" (or uncommitted isoshift/pool.py, tests/test_pool.py, docs/specs/). If not committed, finish it first: run tests/test_pool.py and the acceptance in docs/specs/pool-persistent-gpu-worker.md.
7. Submission: YouTube video published **Public** is the "social media post" (Moment page checked). Target submitted by 00:30, hard stop 02:00.
8. First moves: WF0 then WF1 (one batched mathcheck for all formulas, build pairs.py and screen.py on top of pool.py, sweep validation literature via Bond, brucite imaginary-mode fix per P2).


## Quick reference
| What | Where |
| --- | --- |
| Deadline | Fri 23 Oct 03:00 Turkey time (Thu 22 Oct 7pm CDT). Aim 02:00. Hacking already open (Oct 21 anywhere on Earth). |
| Submission | Moment, team **IsoShift** (solo): https://scientificintelligence.org/campaigns/osi-hackathon-2026 → your team page → Submit. Needs: public social post link (video ≤4 min inside), write-up (+figure), public GitHub repo with README, rules confirmation. |
| Judging | Impact, Innovativeness, Novelty, Relevance (1 to 5 each; rubric on the campaign page). Awards Nov 19. |
| Pre-existing work | Allowed if explicitly stated; judged on what was built during the event (organizer, Slack #2026-event). |
| Slack | Open Scientific Intelligence workspace: #general (announcements), #help, #2026-event, #valency, #resources, #idea-time, #2025-paper. Contact: blaiszik@uchicago.edu |
| Valency Bond | MCP `valency` (https://mcp.valency.io/). Codex: logged in, tested. agy: added, needs `/mcp` → Authenticate. Claude: claude.ai connector (verify with `list_sources`). Sources: arXiv, PubMed, bio/med/Psy/Soc/EarthArXiv, Valency Hub; use OpenAlex for journals. |
| Materials Project | `MP_API_KEY` in `.env`, tested OK (LiH mp-23703). |
| GitHub | `gh` logged in as `canerganis`. Create the public repo only with Can's go-ahead. |
| Video | OBS installed; Can narrates (English) over screen recording; publish on YouTube as **Public** (P9); LinkedIn/X optional (Can decides). |
| Datasets list | github.com/blaiszik/awesome-matchem-datasets |

**First task in the new session:** with Can, build a detailed end-to-end plan (from now to submission) on top of `PLAN.md`: concrete tasks per block, who does what (Claude / Codex / Gemini 4 Argon / Can), gates, and timings shifted to start now. Then start executing.

Read in this order: `CONTEXT.md`, `DECISION.md` (approved: IsoShift), `PLAN.md`, then `prep/feasibility_isoshift/REPORT.md` and `harness/README.md`.

- Event window: Wed 21 Oct 17:00 → Fri 23 Oct 03:00 Turkey time. Submit by 02:00.
- Project code goes in `src/` and is written after 17:00 Wednesday. `harness/` and `isoshift/` are disclosed pre-event infrastructure.
- Two venvs: `.venv` (MACE, ORB, phonopy) and `.venv-sevenn` (SevenNet, MatterSim); `isoshift.worker.run_job` routes automatically.
- Secrets in `.env` (gitignored): `MP_API_KEY`. Never commit or print it.
- Gemini: use only Gemini 4 Argon, and only for consultation/review (Can's rule).
- Valency MCP Bond: added to agy and Codex (`valency`, https://mcp.valency.io/); Claude via claude.ai connector. Verify each with the `list_sources` tool.
- Save Claude quota: use Codex (gpt-6-astra) and Gemini 4 Argon through `harness.ask` for reviews and bulk LLM work; Sonnet subagents for mechanical work.
- Video: Can narrates in English over an OBS screen recording, with captions; Claude prepares script, slides, demo steps.
- Gate at Thu 00:00 with three outcomes and redefined tiers: see PLAN.md "Final review decisions" P10 to P25 (they override older text).
