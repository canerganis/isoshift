# Start here (new session)

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
