# Brainstorm round 4: wide-scope brief (no tools, no file edits, answer from your own knowledge)

## Event facts
4th Open Scientific Intelligence Hackathon (organizer MDRI, Ben Blaiszik). Virtual. Work window is about 34 hours (Wed 21 Oct 17:00 to Fri 23 Oct 03:00 Turkey time). Submission: public video (max 4 min), one-page summary with a figure, public code, and a form asking what existed before versus what was built during the event.
Four official judging criteria: impact, innovativeness, scalability, relevance to materials science and chemistry.
Organizer framing: "is two days to a real discovery possible?"
Pattern of 2025 winners: usable, validated tools that produce a concrete result. Plain RAG or chat wrappers did not win.
Sponsor tracks (optional): Valency MCP Bond (literature search over 44.5M papers), Marimo notebooks, Adaption.

## Team and resources
One solo participant (metallurgical and materials engineer). 34 hours total including video. Laptop with RTX 4060 8GB, Python. Subscription CLI access to three frontier LLMs (Opus 5.5, GPT-6 Astra, Gemini 4 Argon), usable as agents. No wet lab, no paid compute, no API keys for gated databases. Only open data and free tools (Materials Project dumps via public mirrors, OQMD, JARVIS, AFLOW, COD, NOMAD, Alexandria, PubChem, ChEMBL, NIST, arXiv, OpenAlex, etc., ML potentials such as MACE, CHGNet, ORB, pymatgen, ASE, RDKit, xtb, LAMMPS are fine).

## Ideas ALREADY considered (do not repeat, do not lightly rephrase)
1. Agentic discovery benchmark with oracle budget (exists: MADE, ICML 2026).
2. EigenDrop: MLIP imaginary-mode scanning to find lower-energy polymorphs (exists: VibroML).
3. Hidden auxetics or negative linear compressibility mined from elastic databases (exists: Dagdelen 2017 and follow-ups).
4. SinkBreaker: reaction network thermodynamic sink analysis (exists: Ceder/Persson networks, A-Lab).
5. GNoME reality check: how many GNoME predicted materials were later synthesized.
6. DataDoctor: agent audit of experimental datasets (matbench expt_gap, Kingsbury formation enthalpies), source tracing, correction ledger.
7. Unified hull reconciliation across GNoME, Alexandria and MP.
8. COD inorganic structure chemical consistency audit.
9. SpinGhost (MP metals that are experimentally AFM insulators), ThermoGhost (doped samples labeled pure in thermoelectric data), HydrateTrap (wrong polymorph or hydrate matching in formation enthalpy).
10. Adsorption temperature rank reversal in NIST data, solute diffusion compensation effect, literature contradiction court.
Common pattern so far: "find systematic errors in data everyone uses". You may propose that type again only if it is clearly different from the list.

## Your task
Propose 6 NEW ideas spanning the whole scope: materials, chemistry, physics, mathematics, and also datasets, benchmarks and scientific software. At least 3 must be outside plain "audit a materials dataset". Each idea must produce a concrete, checkable, discovery-type result within 34 hours using real open data (a list, a number, a law, a counterexample, a validated tool plus a finding).

For each idea give:
1. Headline (one line)
2. Steps (4 to 6 short steps, with rough hours)
3. Data and tools (name real, openly accessible resources)
4. The hard result (what exactly is produced and what a judge can check)
5. Why it is new (what you believe has not been done, and the closest prior work you know)
6. Verification (how we know the result is real, not an artifact)
7. Risk (the main way it fails)
8. Your own estimate of 1st-place odds in percent

Then answer: "What single idea would make an expert judge say wow, and is it feasible solo in 34 hours?" Give one idea, one paragraph, honest feasibility.

Prioritize boldness and headline impact over safety. We want the idea an expert would call the most surprising result of the hackathon, still executable solo in 34 h with real data. Do not propose dataset audits, database cleaning, or agent benchmarks; those were already considered.

Be critical. Prefer ideas where a surprising result is likely and a null result is still publishable. Avoid anything needing synthesis, gated data, or more than 8GB of GPU memory. No filler, no dashes as punctuation. Limit 1300 words.
