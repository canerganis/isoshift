# OSI Hackathon 2026 — Topic Selection & 34-Hour Discovery Plan

---

## 1. Four High-Scoring Discovery Topics

### Topic 1: `EigenDrop` — Discovering Hidden Ground-State Polymorphs by Following Imaginary Phonon Modes Across "Stable" Database Crystals
* **Video Headline:** *"We audited 1,200 'thermodynamically stable' Materials Project crystals, proved 90+ are dynamic saddle points, and discovered their true symmetry-broken ground states—matching unexplained anomalies in experimental papers."*
* **What the System Does:**
  1. Queries Materials Project (`mp-api`) for $E_{\text{hull}} = 0$ inorganic crystals (1–20 sites/cell) that lack DFT phonon data, focusing on functional oxides and halides.
  2. Computes supercell force constants and phonon dispersions via `phonopy` + `MACE-MP-0` (~4 sec/crystal on Colab GPU).
  3. For crystals with strong imaginary modes ($\omega < -1.0i\text{ THz}$), an agent perturbs atomic coordinates along the softest eigenvector (`spglib` + `ASE`), relaxes the symmetry-broken child structure, and checks if polar/ferroelectric symmetry emerges.
  4. Queries **Valency MCP Bond** (44.5M papers) with an LLM rubric to match each newly discovered polymorph against experimental reports of XRD peak splitting, phase transitions, or synthesis anomalies.
* **Data & Tools:** `mp-api`, `mace-torch` (`MACE-MP-0`), `phonopy`, `spglib`, `ase`, `pymatgen`, **Valency MCP Bond**, **Marimo**.
* **The One Figure:** A 3-panel summary: (A) Scatter of 1,200 "$E_{\text{hull}}=0$" crystals showing imaginary mode frequency vs. symmetry-breaking relaxation drop $\Delta E$ (meV/atom); (B) Phonon dispersion + double-well energy curve of the top discovered ferroelectric polymorph; (C) MCP Bond literature verification matrix comparing MP space groups vs. experimentally reported symmetries.
* **Criteria Scores (1–5):**
  * **Impact (5/5):** Directly corrects false ground-state assumptions in the most widely used materials database and uncovers overlooked polar/ferroelectric polymorphs.
  * **Innovativeness (5/5):** Combines automated eigenvector-following crystal relaxation with literature anomaly cross-verification rather than passive property prediction.
  * **Scalability (5/5):** Scales linearly ($O(N)$ embarrassingly parallel) to all >150k Materials Project and >4M Alexandria entries at ~4 GPU-seconds per crystal.
  * **Relevance (5/5):** Solves a foundational crystallography and solid-state thermodynamics problem at the core of materials discovery.
* **Hard Result:** A catalog of ~80–150 newly relaxed, lower-energy ground-state CIFs ($\Delta E < -10\text{ meV/atom}$) from ~1,200 supposedly stable MP crystals, plus 5–10 literature-corroborated cases where experimentalists observed the lower-symmetry phase.
* **Biggest Risk & Fallback:** *Risk:* MLIP soft-mode false positives on magnetic/strongly correlated 3$d$ transition metals. *Fallback:* Restrict query to closed-shell $d^0$/main-group oxides and halides (e.g., titanates, niobates, perovskites) where `MACE-MP-0` forces closely track PBE-DFT.

---

### Topic 2: `SinkBreaker` — Autonomous Parasitic-Sink Diagnosis & Precursor Rerouting for "Unsynthesizable" Solid-State Targets
* **Video Headline:** *"Why do DFT-stable materials fail in the furnace? Our agent identifies the exact intermediate impurity traps and designs alternative precursor routes that restore thermodynamic driving force."*
* **What the System Does:**
  1. Selects 60 high-value inorganic targets in `mp-api` that sit near the convex hull ($E_{\text{hull}} \le 15\text{ meV/atom}$) but are flagged as theoretical (`is_theoretical=True`) or notoriously impure.
  2. Uses `pymatgen` (`interface_reactions`) + Bartel machine-learned vibrational free energy $G(T)$ to enumerate all pairwise reaction steps from standard carbonate/oxide precursors and identify deep intermediate "sink" phases that stall the final step ($\Delta G_{\text{final}} \approx 0$).
  3. Uses **Valency MCP Bond** to mine experimental synthesis papers in that chemical system, confirming which parasitic impurity phases actually appear in failed runs.
  4. An LLM agent searches alternative commercial precursors (peroxides, halides, metathesis pairs, pre-reacted binaries) to bypass the sink and maximize target driving force $|\Delta G_{\text{target}}|$.
* **Data & Tools:** `mp-api`, `pymatgen`, `rxn-network`, **Valency MCP Bond**, **Marimo**.
* **The One Figure:** Reaction-pathway energy landscape (free energy $\Delta G$ at $1000\text{ K}$ vs. reaction coordinate) comparing conventional precursors (trapped in a deep binary-oxide sink) vs. the agent-discovered precursor pair (smooth downhill cascade to target), paired with an accuracy bar chart across 60 targets.
* **Criteria Scores (1–5):**
  * **Impact (5/5):** Bridges the gap between computational stability and experimental synthesizability without requiring wet-lab trials.
  * **Innovativeness (4.5/5):** Moves beyond recipe retrieval (2025 winner) into mechanistic thermodynamic trap diagnosis and precursor-swap optimization.
  * **Scalability (5/5):** Analytical phase-diagram algebra runs on CPU in <2 seconds per chemical system across any inorganic stoichiometry.
  * **Relevance (5/5):** Directly addresses solid-state synthesis, the primary bottleneck in inorganic materials discovery.
* **Hard Result:** Quantitative audit of 60 targets showing >75% match between predicted thermodynamic sinks and literature-reported impurities, plus 20+ concrete precursor-swap recipes that increase net target driving force by $>50\text{ meV/atom}$.
* **Biggest Risk & Fallback:** *Risk:* Sparse MCP Bond retrieval for completely unattempted quaternary systems. *Fallback:* Benchmark on 40 known "difficult-to-synthesize" battery/superconductor targets (e.g., garnet LLZO, NASICON, layered nickelates) with rich failure literature, plus 20 theoretical targets.

---

### Topic 3: `Humid-DAC` — Co-Adsorption & Hydrolytic Stability Re-Ranking of MOFs for Direct Air Capture
* **Video Headline:** *"80% of 'top' computational $\text{CO}_2$-capture MOFs fail in humid air—our agent simulates competitive water binding and mines 44.5M papers to find the survivors."*
* **What the System Does:**
  1. Pulls 150 top $\text{CO}_2$-selective structures from the open **CoRE-MOF 2019** / **QMOF** datasets.
  2. Runs an `ASE` + `MACE-DAC` / `MACE-MP-0` pocket-insertion loop to compute competitive adsorption energies $\Delta E_{\text{ads}}(\text{CO}_2)$ vs. $\Delta E_{\text{ads}}(\text{H}_2\text{O})$ at open metal sites and pore windows.
  3. Queries **Valency MCP Bond** for each MOF's metal node + organic linker chemistry to extract experimental reports of moisture degradation, BET surface-area loss, or water stability.
  4. Combines atomistic selectivity ($\Delta\Delta E_{\text{ads}}$) and literature hydrolytic survival rubrics into a reactive **Marimo** Pareto dashboard.
* **Data & Tools:** `CoRE-MOF` / `QMOF` (Figshare/ASE), `mace-torch`, `ase`, **Valency MCP Bond**, **Marimo**.
* **The One Figure:** Dry-vs-Humid Pareto front ($\Delta E_{\text{ads}}(\text{CO}_2)$ vs. $\Delta E_{\text{ads}}(\text{CO}_2) - \Delta E_{\text{ads}}(\text{H}_2\text{O})$), color-coded by literature moisture survivability, highlighting the ~10 surviving hydrophobic-pocket MOFs.
* **Criteria Scores (1–5):**
  * **Impact (4.5/5):** Eliminates the #1 cause of false positives in computational carbon-capture screening.
  * **Innovativeness (4.5/5):** Unifies atomistic competitive adsorption with automated linker/node stability extraction from literature.
  * **Scalability (4/5):** Site sampling in large MOF unit cells (200–500 atoms) takes ~30–60 sec/MOF, limiting single-GPU throughput to ~500 structures/day.
  * **Relevance (5/5):** Targets porous materials chemistry and climate-critical separation science.
* **Hard Result:** Re-ranking of 150 top DAC MOFs showing the exact fraction poisoned by $\text{H}_2\text{O}$, plus a curated shortlist of 8–12 moisture-tolerant MOFs with favorable $\Delta E_{\text{ads}}(\text{CO}_2) < \Delta E_{\text{ads}}(\text{H}_2\text{O})$ and experimental water-stability citations.
* **Biggest Risk & Fallback:** *Risk:* Zero-Kelvin single-molecule $\Delta E_{\text{ads}}$ ignores entropic water clustering in large pores. *Fallback:* Restrict to ultra-microporous MOFs (pore limiting diameter $3.3\text{–}5.0\text{ \AA}$) where single-site enthalpy dominates Henry-regime selectivity.

---

### Topic 4: `DiscoveryGym` — Process-Rubric Benchmark & Live Active-Learning Agent for Ductile / Ultra-Low-$\kappa_L$ Ceramics
* **Video Headline:** *"We built a zero-leakage benchmark testing whether frontier LLMs can run iterative materials discovery—then unleashed the winning agent to discover 10 new ductile, ultra-low thermal conductivity ceramics."*
* **What the System Does:**
  1. Masks chemical identities on a holdout split of `Materials Project` elastic/thermomechanical data (`matbench_log_kvrh` / `log_gvrh`) and gives Opus 5.5, GPT-6 Astra, and Gemini 4 Argon a 25-query active-learning budget to find high-Pugh-ratio ($B/G > 1.75$, ductile) + ultralow Slack/Cahill thermal conductivity ($\kappa_L$) crystals.
  2. Scores every reasoning trace using a professional **LLM Process Rubric** (hypothesis falsification, physics-guided feature engineering, exploration efficiency).
  3. Deploys the best-performing agent architecture uncapped on unscreened quaternary chalcogenides/halides using `MACE-MP-0` elastic tensor relaxations (`ase` strain-stress finite differences) + **Valency MCP Bond** checks to discover new candidates.
* **Data & Tools:** `matminer` / `Matbench`, `mp-api`, `mace-torch`, `ase`, **Valency MCP Bond**, **Marimo**.
* **The One Figure:** Left: Discovery regret curves + process-rubric radar plot comparing Opus 5.5, GPT-6 Astra, and Gemini 4 Argon. Right: Pugh ratio ($B/G$) vs. minimum thermal conductivity ($\kappa_{\min}$) map highlighting 10 newly discovered ductile thermal-barrier candidates.
* **Criteria Scores (1–5):**
  * **Impact (4.5/5):** Provides both a reusable scientific-discovery eval suite (aligned with the featured hackathon talk) and new thermomechanical candidates.
  * **Innovativeness (5/5):** Evaluates *how* agents formulate and falsify physical hypotheses rather than static QA accuracy.
  * **Scalability (5/5):** Modular benchmark harness plugs into any property oracle or LLM API.
  * **Relevance (4.5/5):** Connects AI-for-science evaluation directly to structural/thermal ceramic discovery.
* **Hard Result:** A 3-model leaderboard across 5 iterative discovery runs with rubric failure breakdowns, plus 10 newly identified ductile/low-$\kappa_L$ crystals ($B/G > 1.8$, $\kappa_{\min} < 0.6\text{ W/m}\cdot\text{K}$).
* **Biggest Risk & Fallback:** *Risk:* Training-data memorization if crystal formulas are shown. *Fallback:* Use anonymized structural graph features + masked elemental tokens during the benchmark phase, revealing true formulas only in the uncapped discovery phase.

---

## 2. Best Pick & Concrete 34-Hour Execution Plan

**Recommended Winner: Topic 1 (`EigenDrop`)**
It delivers an unmistakable, paper-worthy scientific discovery (new ground-state crystal structures for materials everyone assumed were already in their ground state), runs deterministically in seconds per structure on Colab, leverages your LLM rubric expertise to reconcile computational discoveries with experimental literature anomalies, and qualifies for **all three sponsor prizes** (Valency MCP Bond, Marimo, Adaption Labs).

### 34-Hour Execution Plan (6 Blocks)
* **Block 1 (Hours 0–4): Pipeline Setup & Target Curating.** Install `mp-api`, `mace-torch`, `phonopy`, `spglib`, `marimo`, and configure **Valency MCP Bond**. Query `mp-api` for ~1,200 closed-shell, non-magnetic crystals with $E_{\text{hull}} = 0$, $N_{\text{sites}} \le 16$, and no existing MP phonon entry (focusing on oxides, halides, and chalcogenides).
* **Block 2 (Hours 4–10): High-Throughput Phonon Audit on Colab GPU.** Run batched supercell finite-displacement force calculations with `MACE-MP-0` + `phonopy` (~3–4 sec/structure; ~1.5 hours total compute). Filter for structures exhibiting non-trivial imaginary modes ($\omega < -1.0i\text{ THz}$ away from $\Gamma$-acoustic drift).
* **Block 3 (Hours 10–16): Autonomous Eigenvector Perturbation & Relaxation Loop.** Build the agentic symmetry-breaker: modulate unstable structures along soft-mode eigenvectors across amplitude steps, relax cell + positions with `MACE-MP-0` (`FrechetCellFilter`), determine the new space group via `spglib`, and compute $\Delta E_{\text{relax}}$ and point-group polarity (new ferroelectrics/pyroelectrics).
* **Block 4 (Hours 16–23): Valency MCP Bond Literature Reconciliation & Rubric Scoring.** For the top 60 structures with the largest energy drops ($\Delta E < -15\text{ meV/atom}$), run an agentic **MCP Bond** search over 44.5M papers. Apply a 4-point LLM verification rubric to classify each material: *(1) Experimental literature confirms our lower-symmetry space group; (2) Literature reports unexplained phase transitions/peak splitting; (3) Synthesis failed/impure; (4) Never synthesized.*
* **Block 5 (Hours 23–28): Interactive Marimo App & Master Figure.** Build a reactive **Marimo** notebook where judges can pick any discovered polymorph, inspect its imaginary phonon band structure, toggle the 3D symmetry-breaking distortion, and read the cited MCP Bond experimental evidence. Export the 3-panel publication figure.
* **Block 6 (Hours 28–34): One-Page Summary, GitHub Packaging & 4-Minute Video.** Package all newly discovered CIFs + JSON rubric traces on GitHub, write the 1-page PDF summary, and record a fast-paced 3.5-minute demo video leading with the headline discovery numbers.

---

## 3. Data & Tool Honesty Audit

* **100% Verified & Immediately Accessible:** `mp-api` (Materials Project summary + structure endpoints), `mace-torch` (`MACE-MP-0` weights via GitHub/PyPI), `phonopy`, `spglib`, `ase`, `pymatgen`, `matminer` (`Matbench`), and `marimo` are all open-source, pip-installable, and verified.
* **Flagged Uncertainties:**
  1. **Valency MCP Bond schema & rate limits:** While provided by the hackathon sponsor over 44.5M papers, its exact query latency, full-text vs. abstract snippet depth, and rate limits during the event are unknown until onboarding. *Mitigation:* Cache all MCP Bond queries locally to JSON and batch queries only on the top 60–100 candidate compounds rather than all 1,200.
  2. **CoRE-MOF / QMOF water-binding accuracy (Topic 3):** While QMOF and CoRE-MOF CIFs are public on Figshare, open MLIPs (`MACE-MP-0`) can misestimate weak physisorption without D3 dispersion (`torch-dftd`) enabled; Topic 1 (`EigenDrop`) avoids weak intermolecular dispersion entirely by relying on strong covalent/ionic lattice forces where `MACE-MP-0` is battle-tested.
