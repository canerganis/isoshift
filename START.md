# Start here (new session)

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
| Video | OBS installed; Can narrates (English) over screen recording; publish unlisted YouTube and/or LinkedIn (Can decides). |
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
- Gate at hour 10: validation (ice and brucite volume isotope sign, LiH ZPE, negative controls) must hold, else switch to the fallback framing in DECISION.md.
