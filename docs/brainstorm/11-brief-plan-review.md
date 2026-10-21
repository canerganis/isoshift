# Final plan review: find every gap before we start

You are a senior reviewer (computational materials science + hackathon execution). Do not edit files and do not run commands. Answer in English, under 900 words.

Context: solo participant, OSI Hackathon 2026 (MDRI). Work window Wed 21 Oct 17:00 to Fri 23 Oct 03:00 Turkey time (submit by 02:00). Topic IsoShift (see DECISION.md). Judging: impact, innovativeness, novelty, relevance (1 to 5). Submission on Moment: public social post with video ≤4 min, write-up with figure, public GitHub repo with README, rules confirmation. Organizers allow pre-existing code if explicitly stated; judging is on work done during the event. Hardware: one RTX 4060 laptop. Models: Claude Opus/Sonnet/Haiku, Codex gpt-6-astra, Gemini 4 Argon (consultation only). Valency MCP Bond works in Claude and Codex.

The full plan (PLAN.md) and decision (DECISION.md) follow below (or read them from the repo if you have file access: PLAN.md, DECISION.md, START.md, docs/WORKFLOW.md).

## Task
Find what is MISSING, WRONG, or RISKY in the plan. Be concrete and prioritized. Cover at least:
1. Science: validation logic, gate criteria (are they achievable and meaningful?), ΔT_iso method, negative controls, claims that judges could attack.
2. Judging fit: does the plan make the AI/LLM/agent contribution visible enough? Novelty framing vs prior work (Bourgeois et al. 2018, 115 metal hydrides). Impact story (who uses it).
3. Execution: timeline realism for one person + one GPU, single points of failure (no backup/remote repo, laptop crash, GPU OOM, quota exhaustion), handoffs that depend on Can, what happens if the gate fails.
4. Deliverables: anything the submission needs that the plan does not produce (license, citations/data attribution, captions, figure quality, write-up structure, disclosure of pre-event work, reproducibility).
5. Anything else that would cost first place.

Output: a table with columns: # | gap | severity (blocker/high/medium/low) | concrete fix (one line) | which plan block it belongs to. Then a 3-line verdict.
