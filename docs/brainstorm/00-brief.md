# Brainstorm brief: idea to win 1st place at the OSI Hackathon 2026

You are one of several independent models brainstorming. Do not run tools, do not edit files. Answer in English, plain text/markdown only.

## The event
4th Annual Open Scientific Intelligence Hackathon (organizer Ben Blaiszik; formerly "LLM Hackathon for Applications in Materials Science and Chemistry"). Virtual, ~2000 registrants, ~120+ submissions expected.
- Time: starts Oct 21 2026, submissions due Oct 22 7pm CT. About 34 hours of work.
- Scope: anything that meaningfully advances the physical sciences or mathematics using LLMs, agents, multimodal models.
- Judging: potential for impact, innovativeness, relevance, novelty.
- Organizer framing this year: frontier models (Fable, Opus 5.5, GPT-6 Astra, Gemini 4 Argon) are far beyond last year; "is two days to a real discovery now possible?" Scope ambitiously. Speed over polish.
- Deliverables: video up to 4 minutes, one-page summary with a figure, public code. Form asks what existed before vs what was built during the hackathon.
- Prizes: MDRI general prize (~$10K total), sponsor prizes from Valency (must use MCP Bond, a literature search MCP over 44.5M papers), Adaption Labs (credits), Marimo (must use marimo notebooks), NVIDIA DGX Spark.
- Selected teams may co-author a collective paper.

## 2025 winners (Lila Prize)
1. SKY (Imperial): LLM synthesis exploration agent. Similarity search on Materials Project, retrieves neighbor synthesis recipes, adapts them to a new target, outputs protocol with confidence scores and citations. Clean CLI + notebook.
2. Triple_As: polished AI tutoring platform for chemistry/materials students.
3. MixSense (MIT): agent that deconvolutes 1H NMR mixture spectra into components and quantities.
4. CrystaLenz (solo dev): end-to-end XRD phase ID pipeline with pymatgen simulation and Materials Project references.
5. ACME (Argonne): closed-loop discovery with automated lab.
Other awards went to solo projects too (olfactory receptor CNN, GCxGC-MS analysis, MLIP docking agent). Plain RAG chatbots did not win. Almost no projects on metals, alloys or additive manufacturing.

## The participant
Can Erganiş, solo. Metallurgical and materials engineer. No lab access. Has access to Claude (Opus 5.5), Codex (GPT-6 Astra), Gemini 4, personal PC (GPU unknown, assume modest; Colab possible).
Existing personal project "Metalliksa": LPBF (laser powder bed fusion) research platform with a working 3D Ti-6Al-4V transient thermal (enthalpy) CPU solver with evaporation loss, pycalphad CALPHAD checks, source/evidence tracking. Never compared against experiments. Using it is optional.
Current leading candidate: agent mines LPBF papers for Ti64 process params + measured melt pool dimensions, runs the Metalliksa solver, compares, then finds where the model fails and proposes/calibrates a correction (e.g. absorptivity vs energy density, keyhole threshold) validated on held-out papers.

## Your task
Propose 5 ideas that could realistically win FIRST place, done solo in ~34 hours. Do not need to relate to Can's background, but may. Avoid ideas that are generic RAG/chatbots or already done in 2025.
For each idea give:
1. One-line pitch (what the 4-minute video headline would say)
2. What the agent/system actually does, step by step
3. Data/tools (must be real, open, accessible today; name them)
4. The single validation figure
5. Why judges would rank it first (impact, novelty, "discovery")
6. Biggest risk and a fallback if it fails mid-hackathon
7. Your honest 1st-place odds relative to the field (low/medium/high)

Then: rank your 5 and give a brief honest critique of the current leading candidate (Metalliksa melt-pool idea): would it win 1st? what would make it win?
Keep total under 1200 words.
