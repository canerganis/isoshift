# OSI 2026: four topics, scored against the judging criteria

## 1. HiddenHull: can a frontier agent find stable materials it has never seen?
**Video headline:** "We hid 250k DFT-verified crystals from three frontier agents and counted how many they found again, and how many they found that nobody had."

**What it does:**
1. The agent's known world is Materials Project, and its hull is the MP convex hull.
2. Three agents, plus baselines, propose new compositions and prototypes. Each agent gets the same tool budget. Tools are pymatgen substitution, a prototype lookup and an MLIP relaxation.
3. An oracle scores each proposal. It relaxes the structure with two MLIPs (MACE-MP-0 and ORB or SevenNet) and computes E_hull against MP.
4. Ground truth is the WBM set from Matbench Discovery, which is held-out DFT. Proposals that match WBM count as verified rediscoveries. Proposals found in no database (MP, WBM, Alexandria, GNoME) count as novel candidates.
5. Run a leakage probe: ask each model to recall known compounds without tools, and subtract that.

**Data and tools:** MP API, Matbench Discovery/WBM, Alexandria, GNoME public release, pymatgen, `SubstitutionPredictor` (Hautier), MACE-MP-0, CHGNet, marimo.

**The figure:** discovery-rate curves (cumulative DFT-verified stable hits vs oracle calls) for each model, the substitution baseline and random. A novel-candidate table sits inset.

| Criterion | Score | Why |
|---|---|---|
| Impact | 5 | Gives a number for "do LLM agents speed up discovery beyond classic heuristics?" |
| Innovation | 5 | First closed-loop discovery benchmark with a held-out DFT oracle. Matches the featured talk. |
| Scalability | 5 | Adds new models, chemistries or oracles (DFT later) with no redesign. It stops scaling where MLIP accuracy runs out. |
| Relevance | 5 | Inorganic materials stability is the core problem of the field. |

**Hard result:** hit rate and precision@k for each model vs the baseline, with confidence intervals. It also yields a list of about 20–50 novel candidates within 50 meV/atom of the hull, agreed by both MLIPs.

**Biggest risk:** few overlaps with WBM, which makes the verification sparse. **Fallback:** use WBM as a retrospective test. Ask agents to rank WBM candidates (a closed pool, DFT labels known), which gives a clean metric every time.

## 2. Triage of GNoME/Alexandria stable compounds for synthesis
**Video headline:** "Of 380k predicted stable crystals, these 30 are the ones worth making first, with recipes."

**What it does:** filter on hull distance, then check dynamic stability (MLIP and phonopy phonons). Next, score synthesizability (SynthNN-style PU model, retrained or used off the shelf). Then check novelty in the literature through Valency MCP Bond. Finally, propose precursors and temperatures from the nearest text-mined recipes, with the reaction driving force taken from MP.

**Data and tools:** GNoME release on GitHub, Alexandria, Kononova et al. 2019 text-mined solid-state recipes (about 31k), MP, phonopy, MACE, Valency MCP.

**The figure:** a funnel from 380k to about 30, plus one example card showing the structure, its phonons, the recipe and its citations.

| Criterion | Score | Why |
|---|---|---|
| Impact | 4 | Hands experimental groups a target list they can act on. |
| Innovation | 3 | Close to the 2025 winner. The new parts are phonon and literature gates. |
| Scalability | 4 | Each step is cheap. Phonons are the bottleneck. |
| Relevance | 5 | Directly about making materials. |

**Hard result:** a ranked list of about 30 compounds, each with a recipe, a confidence and citations. It also measures what fraction of "stable" GNoME entries fail the phonon check.

**Biggest risk:** no experimental check is possible within 34 hours. **Fallback:** a retrospective test. Hide recipes for compounds already in the dataset and score recipe recovery.

## 3. DataDoctor: finding errors in experimental datasets that ML models train on
**Video headline:** "We found N likely errors in a benchmark that thousands of ML papers train on."

**What it does:**
1. Take experimental datasets: Zhuo 2018 band gaps (about 6k entries) and experimental formation enthalpies (Kim/Matbench).
2. Flag outliers using DFT (MP and, if available, HSE values from Alexandria), ML predictions and chemical-family consistency.
3. An agent pulls the original papers through Valency MCP Bond. It extracts the reported value and decides between "dataset error", "real physics" or "unclear".
4. The output is a corrections file with evidence.

**The figure:** a parity plot with flagged points, and the share of flags confirmed as errors.

| Criterion | Score | Why |
|---|---|---|
| Impact | 4 | Cleaner benchmarks improve every model trained on them. |
| Innovation | 4 | Agentic data audit with citations. |
| Scalability | 5 | Works for any property dataset. |
| Relevance | 5 | Core materials data. |

**Hard result:** a count of verified errors with DOIs, and the change in MAE after correction.

**Biggest risk:** Valency may return abstracts only. **I'm not sure about full-text access.** **Fallback:** check against a second source (e.g., the matminer `expt_gap` vs Citrine copies, which disagree in places).

## 4. Fast screening for solid electrolytes, checked against experimental data
**Video headline:** "An agent ran 2,000 picoseconds of MLIP dynamics and ranked untested Li-ion conductors, after first passing a test against real measured conductivities."

**What it does:**
1. Run MLIP MD (MACE-MP-0) at 600–1000 K on known conductors.
2. Fit an Arrhenius curve and compare with experimental conductivity to calibrate the screen.
3. Screen about 100 MP Li compounds that have never been measured.
4. An LLM proposes dopant substitutions for the top hits and reruns them.

**Data and tools:** OBELiX (Therrien et al. 2024, about 600 experimental conductivities) and/or the Liverpool Li-ion conductivity dataset. **I'm moderately confident both are public. Verify licensing and format first.** Also MP, ASE, MACE, Colab GPU.

**The figure:** predicted vs experimental log σ (Spearman ρ), with new candidates overlaid.

| Criterion | Score | Why |
|---|---|---|
| Impact | 4 | — |
| Innovation | 3 | MLIP-MD screening already exists. The calibration loop is the new part. |
| Scalability | 3 | MD cost limits it. |
| Relevance | 5 | — |

**Hard result:** Spearman ρ on the experimental set, plus a top-10 list of untested candidates.

**Biggest risk:** short MD runs are noisy, and Colab time is limited. **Fallback:** use cheaper descriptors (BV-pathway / softBV) and keep MD only for the top 20.

## Best pick: HiddenHull (topic 1)
It's the only topic that scores 5/5/5/5. It answers the organizers' question ("is two days to a discovery possible?") with a measured answer. It matches the featured benchmark talk and plays to your strength in evaluation. It also produces both a benchmark and a candidate list, so the result holds up whichever way the numbers go. Build it in marimo for the sponsor prize.

### 34-hour plan
| Block | Hours | Work |
|---|---|---|
| 1. Oracle | 0–6 | Pull the MP hull for 3–5 chemical systems (e.g., Li–M–O, nitrides, chalcogenides). Load WBM with its DFT labels. Wrap MACE + CHGNet relax → E_hull. Calibrate the oracle on 500 WBM entries (MAE, classification F1). |
| 2. Baselines | 6–10 | Random, Hautier substitution and prototype enumeration. Same call budget for each (e.g., 200 oracle calls per system). |
| 3. Agent harness | 10–17 | One tool-use loop (propose → relax → observe → revise), identical prompt and budget for every model. Log every call. Add the leakage probe (no-tool recall). |
| 4. Runs | 17–24 | 3 models × 4 systems × 3 seeds, run in parallel overnight. Fallback track: run the closed-pool WBM ranking task at the same time. |
| 5. Analysis | 24–29 | Discovery curves, precision@k, bootstrap CIs. Split hits into memorized, rediscovered and novel. Dedupe novel candidates against Alexandria/GNoME (StructureMatcher). Spot-check the top 5 with a third MLIP. |
| 6. Deliverables | 29–34 | Figure, one-page summary, public repo with a `run_benchmark.py` anyone can extend, 4-minute video (hook: "we hid 250k crystals"). |

## Where I'm not sure the data or access exists
- **WBM overlap:** I'm unsure how many agent proposals will actually match WBM entries. That's why the closed-pool fallback exists.
- **GNoME release:** I'm confident the stable-structure release is public. I'm less sure that every entry has a full structure plus energy.
- **OBELiX / Liverpool datasets:** I'm moderately confident they exist and are public. Check this before committing to topic 4.
- **Valency full text:** I don't know whether it gives full-text or abstract-only access. This affects topics 2 and 3.
- **Leakage (all topics):** the frontier models were likely trained on MP, GNoME and Alexandria. Report this openly. Measuring it is a finding in its own right.
