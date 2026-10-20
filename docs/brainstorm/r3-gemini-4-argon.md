### 1. Finalist Scorecard & Harsh Critique

| Finalist | Impact | Innovation & UX | Scalability | MatSci Relevance | Total (/20) | Feasibility (34h Solo) |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **A. DataDoctor** | 4.5 | 4.0 | 4.5 | 5.0 | **18.0** | **Realistic** |
| **B. DiscoveryGym** | 3.0 | 3.0 | 3.5 | 3.5 | **13.0** | **Tight / Unrealistic** |
| **C. EigenDrop** | 4.5 | 3.5 | 4.5 | 5.0 | **17.5** | **Realistic** |
| **D. Contradiction Court** | 2.5 | 3.0 | 2.5 | 3.0 | **11.0** | **Unrealistic** |
| **E. SinkBreaker** | 4.5 | 4.5 | 4.0 | 5.0 | **18.0** | **Tight** |

#### **A. DataDoctor**
* **Why it wins 1st:** Delivers an undeniable, paper-worthy scientific artifact in 34h: *"We audited `matminer` `expt_gap`, proved X% of benchmark outliers are extraction/polymorph/temperature errors via MCP Bond, and changed GNN benchmark rankings."* Hits both Valency and Marimo prizes effortlessly.
* **Why it loses:** Judges could dismiss it as "data janitorial work" rather than materials discovery if the physics-vs-error triage looks like a simple LLM prompt wrapper.
* **Prior work:** Generic label auditing (*Cleanlab*, Northcutt et al. 2021); Matbench curation notes (Dunn et al. 2020); LLM extraction verification (*ChatExtract*, Polak & Morgan 2024). However, a physics-triaged, citation-verified correction release for `expt_gap` is novel (unsure if an early 2026 preprint did this exact audit).
* **Feasibility:** **Realistic.** Fast local DFT/ML/family filtering shrinks ~4,600 rows to ~120 suspects in <1h; 120 CLI calls take ~1h. **Bottleneck:** MCP Bond full-text coverage for older (1960s–1990s) experimental papers where values sit in paywalled tables.

#### **B. Discovery Benchmark (HiddenHull / DiscoveryGym)**
* **Why it wins 1st:** Plays directly to the participant’s professional LLM-evaluator pedigree; a clean leakage-vs-oracle-efficiency curve across Opus 5.5, GPT-6 Astra, and Gemini 4 Argon is publishable at an AI4Mat workshop.
* **Why it loses:** Fails the 2025 winner test: benchmarks grade models, they don't make a bench material scientist's life easier or produce a materials discovery. Weak MCP Bond integration.
* **Prior work:** Heavily crowded: *Matbench Discovery* (Riebesell et al. 2023), *LLMatDesign* (Jia et al. 2024), *ChemCrow*, and Bayesian optimization crystal benchmarks (Baird et al.).
* **Feasibility:** **Tight / Unrealistic.** **Bottleneck:** Subscription CLI latency (10–60s/call, no batch API) makes multi-seed, multi-model trajectories painfully slow, and open-ended MLIP relaxations frequently collapse on overlapping-atom hallucinations.

#### **C. EigenDrop**
* **Why it wins 1st:** Purest physics discovery: catching "stable" ($E_{\text{hull}}=0$) Materials Project crystals that are actually dynamical saddle points, relaxing them into lower-energy symmetry-broken ground states, and proving via MCP Bond that experimentalists already saw the low-T phase.
* **Why it loses:** The AI agent is bolted on at the end. 90% of the pipeline is a deterministic `phonopy` + `MACE-MP-0` loop; without DFT verification, judges may distrust MLIP soft modes.
* **Prior work:** High-throughput DFPT phonons (Petretto et al. 2018), mode-following (`phonopy`), and recent universal-MLIP phonon stability screens (Batatia et al. 2024; Loew et al. 2024–2025).
* **Feasibility:** **Realistic.** RTX 4060 runs MACE-MP-0 supercell forces in seconds (~1,000 structures in 2h). **Bottleneck:** MLIP potential-energy-surface roughness causing false-positive imaginary acoustic modes near $\Gamma$.

#### **D. Literature Contradiction Court**
* **Why it wins 1st:** Directly showcases Valency’s 44.5M-paper corpus with an intuitive hook.
* **Why it loses:** Plain RAG disguised as a courtroom. In materials science, "conflicting" values for the same formula almost always reflect unindexed sample differences (polycrystal vs. single crystal, porosity, oxygen deficiency $\text{TiO}_{2-\delta}$, film strain).
* **Prior work:** FutureHouse’s *PaperQA2* / *LitQA2* contradiction detection (Skarlinski et al. 2024) and *SciFact*.
* **Feasibility:** **Unrealistic.** **Bottleneck:** Without anchoring to a structured dataset first, text-only pair mining over 44.5M papers via 30s CLI calls will drown in false positives.

#### **E. SinkBreaker**
* **Why it wins 1st:** Direct spiritual successor to 2025’s 1st-place synthesis tool, upgraded from "recipe lookup" to "thermodynamic failure diagnosis + precursor redesign." Combines `pymatgen` reaction hulls, MCP Bond impurity evidence, and Marimo interactivity.
* **Why it loses:** 0 K DFT $\Delta G_{\text{rxn}}$ ignores kinetics, melting eutectics, and $p_{\text{O}_2}$. If demonstrated on only 3 cherry-picked oxides, it looks like a thin wrapper around `pymatgen`.
* **Prior work:** Persson group reaction networks (`rxn_network`, McDermott et al. *Nat. Commun.* 2021), Miura et al. (2021), and *A-Lab* precursor selection (Szymanski et al. 2023).
* **Feasibility:** **Tight.** **Bottleneck:** Assembling a statistically convincing validation set of failed syntheses with documented impurity phases from MCP Bond in 34h.

---

### 2. Final Ranking (Probability of Winning 1st Place)
1. **A — DataDoctor** (Best balance of 34h solo feasibility, guaranteed quantitative discovery, sponsor alignment, and evaluator skillset)
2. **E — SinkBreaker** (Best user-facing researcher tool; loses to A only on validation-set curation risk)
3. **C — EigenDrop** (Strongest physics finding, weaker agentic novelty)
4. **B — DiscoveryGym** (Too meta; misses the "usable tool for scientists" bar)
5. **D — Contradiction Court** (Too noisy without a structured dataset anchor)

---

### 3. Sharpened Winner (Merge A + D, 5 Lines)
**DataDoctor: Contradiction-Driven Benchmark Auditor.** Instead of mining random literature pairs (D), anchor the court on **two canonical experimental benchmarks** (`matminer` `expt_gap` and `expt_formation_enthalpy_kingsbury`). Use DFT (`mp-api`), MACE-MP-0 features, and chemical-family laws to flag the top 150 physical anomalies, then deploy a 3-model CLI "Court" via MCP Bond to audit the original and citing papers for polymorph, temperature, or stoichiometry mismatches. Where papers genuinely conflict, adjudicate using fundamental thermodynamic/electronic bounds. Ship an interactive **Marimo** audit workbench, a citation-backed corrected dataset, and a one-page figure showing benchmark ML error before vs. after repair.

---

### 4. Three New 34-Hour Discovery Topics

1. **SpinGhost (Unflagged Antiferromagnetic Insulators Masquerading as Metals in DFT Hulls)**
   * **Finding:** Identify 30–50 transition-metal/rare-earth compounds listed as non-magnetic or ferromagnetic metals in Materials Project that are experimentally antiferromagnetic (AFM) Mott/charge-transfer insulators with significantly different hull stability.
   * **Why new:** High-throughput DFT hulls initialize most structures ferromagnetic or non-magnetic; systematic cross-auditing against experimental Néel temperatures and optical gaps has not been packaged as an automated hull-correction filter.
   * **Verification & Data:** Cross-match `mp-api` (`is_metal=True`, magnetic ordering) against the open **NEMAD** (Northeast Materials Database of magnetic transitions) / **MAGNDATA** and verify Néel transitions + insulating behavior via **MCP Bond**. *(Uncertainty: formula/polymorph matching between NEMAD and MP requires space-group filtering).*

2. **ThermoGhost (Extrinsic Doping Contamination in "Intrinsic" Transport Benchmarks)**
   * **Finding:** Prove that a substantial fraction of high-$zT$ or high-conductivity entries in experimental thermoelectric compilations used to train ML models are intentionally extrinsically doped or off-stoichiometric samples mislabeled as pristine compositions.
   * **Why new:** ML benchmarks frequently collapse doped sample curves onto nominal parent formulas, corrupting structure-property learning.
   * **Verification & Data:** Compare **Starrydata2** / `matminer` transport datasets against `mp-api` / BoltzTraP2 intrinsic limits; flag compositions exceeding theoretical intrinsic carrier bounds and verify nominal vs. doped synthesis recipes in source papers via **MCP Bond**. *(Uncertainty: Starrydata2 composition tags vary in formatting cleanliness).*

3. **HydrateTrap (Polymorph & Reference-State Ghosts in Experimental Formation Enthalpies)**
   * **Finding:** Uncover 25+ systematic errors in `matminer` `expt_formation_enthalpy` where room-temperature calorimetric data were mapped to the wrong 0 K DFT polymorph, hydrated precursor, or defect phase (e.g., $\text{Fe}_{1-x}\text{O}$).
   * **Why new:** Experimental $\Delta H_f$ datasets are treated as gold standards for benchmarking universal MLIPs (MACE, CHGNet), yet composition-only structure matching introduces silent $>100\text{ meV/atom}$ errors.
   * **Verification & Data:** Compare `expt_formation_enthalpy` against `mp-api` polymorph hulls and **MACE-MP-0** energies, then audit the original calorimetry citations via **MCP Bond** and **NIST WebBook**. *(Uncertainty: older calorimetric papers may only have abstracts in MCP Bond).*
