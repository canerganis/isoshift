# OSI Hackathon 2026: working context

Owner: Can Erganiş (solo). Prep done by Claude overnight 2026-10-20/21 at Can's request; Claude decides topic and builds the harness.

## Event
4th Open Scientific Intelligence Hackathon (MDRI, organizer Ben Blaiszik). Virtual. Work window: Wed 21 Oct 17:00 to Fri 23 Oct 03:00 (Turkey time, UTC+3), submissions due Thu 22 Oct 7pm CT.
Criteria: impact, innovativeness, scalability, relevance to materials science and chemistry. Organizer framing: "is two days to a real discovery possible?"
Deliverables: video max 4 min (public, no login), one-page summary with a figure, public code, form (asks what existed before vs built during the event).
Sponsor prizes: Valency (must use MCP Bond, literature over 44.5M papers), Marimo (marimo notebooks), Adaption.

## Rule we follow
Project-specific code is written after kickoff. Before kickoff: design, environment, data feasibility checks, generic harness (disclosed as pre-existing).

## Candidate topics (from 3-model brainstorm, see docs/brainstorm/)
1. GNoME reality check (leading, ambitious): how many GNoME (DeepMind 2023) predicted stable materials were independently synthesized/reported 2024 to 2026; agent searches literature, matches composition/structure, classifies with evidence.
2. DataDoctor (fallback, all 3 models ranked #1): agent audits widely used experimental materials datasets (matminer expt_gap: 6354 entries, no per-entry references; Kingsbury experimental formation enthalpies), flags errors via independent signals, traces sources, releases corrections, measures benchmark impact.

## Environment
Windows 11, RTX 4060 8GB, Python 3.12 at C:\Users\can02\AppData\Local\Programs\Python\Python312\python.exe. No API keys; models via subscription CLIs:
- codex exec --skip-git-repo-check -s read-only -m gpt-6-astra -o OUT - < PROMPT
- agy: C:\Users\can02\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\agy\bin\agy.exe -p "PROMPT" --model gemini-4-argon-high|claude-opus-5-5-high --output-format text
No Materials Project API key, no Valency Bond account yet (Can will create in the morning).
