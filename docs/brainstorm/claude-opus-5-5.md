# Claude (Opus 5.5), independent ideas, written before reading Codex/Gemini

1. Literature contradiction court. Agent uses Bond to find paper pairs reporting conflicting numbers for the same material property (e.g. elastic modulus, band gap, melting point of a phase), normalizes conditions, then adjudicates with an independent source (Materials Project, MLIP calculation, or a third measurement). Figure: N contradictions found, how many resolved, which side was right. Odds: medium-high. Risk: false contradictions due to differing conditions; fallback: restrict to one property family.

2. Agent rediscovers then extends empirical laws (AI Feynman for metallurgy). Blind test: give agent raw open datasets where the law is known (Hall-Petch, Arrhenius diffusion, Larson-Miller), it must recover them; then point it at HEA hardness/yield data with no accepted law and report a new compact relation validated on held-out alloys. Tools: PySR symbolic regression + LLM hypothesis loop. Figure: recovered vs true law, then held-out error of new law vs ML baseline. Odds: medium-high. Risk: "new law" is overfit; fallback: rediscovery benchmark alone is still a paper-worthy result.

3. Metalliksa physics-correction agent (current candidate, extended). Mine Ti64 melt-pool measurements, run solver, find systematic error, agent proposes and calibrates correction, held-out validation, extract keyhole threshold. Odds: medium. Risk: too few clean measurements; fallback: comparison only.

4. Figure-to-data agent for dead datasets. Most experimental data in papers lives only in plots. Multimodal agent digitizes figures (Gemini 4 vision + axis calibration), validates against papers that also give tables, and releases the first open dataset for an underserved domain (e.g. LPBF Ti64 melt pools or HEA stress-strain). Figure: digitization error vs table ground truth. Odds: medium. Risk: axis parsing errors; fallback: semi-automatic with human check.

5. Stability discovery in a sparse chemistry. Substitution + universal MLIP (MACE-MP-0/UMA) + MP hull, novelty check with Bond. Odds: low-medium, GNoME-style work is crowded.

Ranking: 1, 2, 3, 4, 5.
Critique of the Metalliksa idea: credible and novel domain, but the AI contribution looks like extraction + plotting unless the agent does the scientific reasoning step (diagnose and fix the model). Its audience is narrow. Combining 4 into 3 (digitize melt pool figures to get enough data) strengthens it.
