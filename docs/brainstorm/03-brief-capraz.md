# Round 3: cross-critique and final ranking

You are one of three judges (Opus 5.5, GPT-6 Astra, Gemini 4 Argon). Earlier, each of you proposed topics independently. Now rank the finalists harshly, as if you were a hackathon judge. Do not run tools or edit files. English, markdown, under 900 words.

## Event and criteria
Open Scientific Intelligence Hackathon 2026 (MDRI). Solo participant, ~34 hours, modest GPU (RTX 4060 8GB), access to Opus 5.5, GPT-6 Astra, Gemini 4 Argon via subscription CLIs (no API keys; each call ~10 to 60 s). Metallurgical and materials engineer.
Official criteria: (1) impact on research, (2) innovativeness and making researchers' lives easier, (3) scalability, (4) relevance to materials science and chemistry. Organizer framing: "is two days to a real discovery possible?", paper-worthy results. Deliverables: 4 min video, one-page summary with figure, code. 2025 1st place was a usable tool (synthesis recipe agent with Materials Project, confidence, citations); top 5 were working tools validated on real data; plain RAG did not win. Sponsor prizes: Valency (MCP Bond literature search, 44.5M papers), Marimo (marimo notebooks).

## Finalists
A. DataDoctor: agent audits a widely used experimental materials dataset (e.g. Zhuo 2018 experimental band gaps, matminer expt_gap; experimental formation enthalpies). Flags outliers via DFT (Materials Project), ML predictions and chemical-family consistency, retrieves the original papers via MCP Bond, classifies dataset error / real physics / unclear, releases a corrections file with evidence, and measures model MAE change after correction.
B. Discovery benchmark (HiddenHull / DiscoveryGym): frontier agents get the same oracle budget to find stable crystals. Closed pool version on Matbench Discovery WBM (DFT labels hidden) vs random, substitution and ML-surrogate baselines; leakage probe; optional open-ended proposals scored by MLIPs (MACE-MP-0, CHGNet) against the MP hull.
C. EigenDrop: MLIP phonons (MACE-MP-0 + phonopy) on E_hull=0 MP crystals without DFT phonons, follow imaginary modes to lower-symmetry, lower-energy structures, check literature (MCP Bond) for experimental lower-symmetry reports.
D. Literature contradiction court: agent finds paper pairs reporting conflicting values for the same property of the same material via MCP Bond, normalizes conditions, adjudicates with an independent source.
E. SinkBreaker: thermodynamic diagnosis of why near-hull targets fail to synthesize (intermediate sink phases via pymatgen interface reactions / reaction networks), literature confirmation of impurities, agent proposes alternative precursors.

## Task
1. For each finalist: score 1 to 5 on the four criteria, give the strongest reason it could win 1st and the strongest reason it would lose. Name any prior published work you know that reduces its novelty (be specific, say if unsure).
2. Feasibility for this solo participant in 34 h: realistic / tight / unrealistic, with the main bottleneck.
3. Final ranking A to E by probability of winning 1st place.
4. If you would change the winner (merge two, sharpen scope), give the sharpened version in 5 lines.
5. NEW DISCOVERIES: propose 3 additional topics (not A to E) where a solo participant could plausibly produce a genuine new scientific finding in 34 h (a new material candidate, a new relation, a found error, a new dataset-level fact), with real open data. For each: the finding it would produce, why it is new, how it is verified, and the data source. Flag uncertain data.
Word limit for this round: 1300.
