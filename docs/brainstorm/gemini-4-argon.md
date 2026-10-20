### Idea 1: ScheilForge — Autonomous Discovery of Crack-Free 3D-Printable Alloys
1. **One-line pitch:** An autonomous metallurgist that mines 44M papers for solidification-cracking data, couples non-equilibrium CALPHAD with a 3D thermal solver, and discovers micro-dopants that make "unprintable" alloys printable.
2. **How it works:**
   - Queries MCP Bond for laser powder bed fusion (LPBF) experiments across Al, Ni, and Ti alloys, extracting composition, laser parameters, and binary cracking outcomes (cracked vs. dense).
   - Feeds laser parameters into your 3D thermal solver to compute cooling rate ($\dot{T}$) and thermal gradient ($G$) at the melt-pool tail.
   - Runs `pycalphad` Scheil-Gulliver solidification simulations on each composition to compute Kou’s cracking susceptibility index ($|dT/d(f_s^{1/2})|$ near $f_s \to 1$) and brittle intermetallic fractions.
   - Fits a physics-informed printability boundary in $(\text{Kou Index}, G/\dot{T})$ space, then runs an agentic Bayesian search over low-cost micro-dopants (e.g., Zr, Si, Ti, Nb additions) to shift commercial cracking-prone alloys into the crack-free regime without sacrificing primary phase stability.
3. **Data/tools:** MCP Bond (literature extraction), `pycalphad` + open `.tdb` databases (OpenCalphad, NIST, COST507), Metalliksa 3D enthalpy solver, `marimo` (interactive alloy explorer).
4. **Validation figure:** A 2D "Universal Printability Map" ($x$: thermal strain parameter $G/\dot{T}$, $y$: CALPHAD Kou cracking index) cleanly separating 80+ literature alloys into cracked (red) and crack-free (blue) zones, highlighting 5 agent-discovered doped compositions validated against held-out grain-refinement papers.
5. **Why judges rank it first:** Directly answers "two days to a real discovery" in a high-value industrial domain (metallurgy/AM) where almost no other teams compete, uniting literature mining, thermodynamics, and PDE simulation.
6. **Biggest risk & fallback:** Multi-component open `.tdb` files lack some trace elements. *Fallback:* Restrict search to ternary/quaternary subsystems fully covered by COST507 (Al-alloys) and NIST Ni-superalloy databases.
7. **1st-place odds:** **High**

---

### Idea 2: GhostPeak — Forensic Discovery of Unreported Phases in Published XRD Data
1. **One-line pitch:** An agent that cross-examines published raw XRD patterns against the authors' own paper claims, discovering unreported impurity phases that explain "anomalous" material properties.
2. **How it works:**
   - Queries Zenodo/Figshare and Crystallography Open Database (COD) for raw powder XRD patterns linked to peer-reviewed materials papers, pulling synthesis recipes and phase claims via MCP Bond.
   - Simulates the authors' claimed phase(s) using `pymatgen` and subtracts them from the raw diffractogram (with Le Bail/background fitting) to isolate statistically significant residual "ghost peaks."
   - Queries the Materials Project API for all thermodynamically accessible phases in the precursor + atmosphere + crucible chemical space.
   - Matches residual peaks to specific side-phases and flags papers where the unindexed impurity explains the paper's headline property (e.g., trace ferromagnetic oxides or conductive sub-phases).
3. **Data/tools:** Zenodo REST API, Materials Project (`mp-api`), `pymatgen.analysis.diffraction.xrd`, `scipy.signal`, MCP Bond, `marimo`.
4. **Validation figure:** Two-panel forensic plot: (Left) Prevalence of unreported precursor-derived secondary phases across 150 published raw datasets; (Right) Three "smoking-gun" diffractograms showing residual peaks matching an active secondary phase that explains the reported property anomaly.
5. **Why judges rank it first:** Finding real, verifiable scientific oversights in published literature is unforgettable in a 4-minute video and showcases rigorous AI-evaluator verification.
6. **Biggest risk & fallback:** Raw XRD files on Zenodo have messy formats/headers and zero-point shifts. *Fallback:* Use an LLM parser to standardize `.xy`/`.dat`/`.asc` files and include a $\pm 0.2^\circ$ $2\theta$ shift-alignment step before residual matching.
7. **1st-place odds:** **High**

---

### Idea 3: PiClosure — Symbolic Discovery of Dimensionless Physical Laws from Multi-Study Data
1. **One-line pitch:** An agent that extracts fragmented experimental tables across decades of papers, enforces Buckingham $\Pi$ dimensional invariance, and discovers compact analytical laws that beat textbook correlations.
2. **How it works:**
   - Targets a messy multiphysics regime (e.g., high-temperature alloy creep-rupture, boiling heat transfer critical heat flux, or LPBF keyhole porosity onset) via MCP Bond, extracting 500+ multi-study data points and material properties.
   - Agent constructs the dimensional matrix of all physical variables and computes the null-space basis of dimensionless $\Pi$ groups.
   - Alternates between `PySR` (symbolic regression) and LLM physical critique (checking asymptotic limits as $\Pi_i \to 0$ or $\infty$, enforcing monotonicity) to evolve parsimonious closed-form equations.
   - Evaluates out-of-distribution generalization on held-out chemical/material families unseen during fitting.
3. **Data/tools:** MCP Bond, `PySR` (symbolic regression), `sympy` (asymptotic/dimensional verification), NIST / NIMS creep or thermophysical tables, `marimo`.
4. **Validation figure:** Parity and Pareto plot (error vs. equation complexity) showing collapse of scattered multi-study data from 10+ materials onto a single newly discovered master curve, outperforming classical empirical laws on held-out materials by >40% RMSE.
5. **Why judges rank it first:** Pure scientific discovery: deriving a human-readable physical equation that collapses messy experimental data across studies feels like a genuine breakthrough.
6. **Biggest risk & fallback:** Literature tables have inconsistent units or missing material constants. *Fallback:* Anchor on a curated baseline dataset (e.g., NIMS creep data or published multi-alloy keyhole datasets) augmented by MCP Bond property lookups.
7. **1st-place odds:** **Medium-High**

---

### Idea 4: MirageHull — Empirical Synthesizability Corrections to the $T=0\text{ K}$ DFT Hull
1. **One-line pitch:** By mining "failed" syntheses and decomposition products buried in 44M papers, our agent builds a finite-temperature synthesizability corrector that exposes DFT-stable "mirage materials."
2. **How it works:**
   - Uses MCP Bond to specifically mine experimental paragraphs describing *unsuccessful* target syntheses, parasitic phase formation, and thermal decomposition temperatures across inorganic oxides/chalcogenides/intermetallics.
   - Maps each target and observed parasitic byproduct to Materials Project $T=0\text{ K}$ DFT energy above hull ($E_{\text{hull}}$) and vibrational entropy approximations.
   - Trains an interpretable classifier + symbolic correction term that predicts when a material with $E_{\text{hull}} \approx 0$ is kinetically or entropically trapped by a competing precursor phase at synthesis temperature $T_{\text{syn}}$.
   - Audits recent AI-predicted "stable" crystal datasets (e.g., GNoME/MatterGen public subsets) to flag specific high-profile candidates that will decompose into known competing phases.
3. **Data/tools:** MCP Bond, Materials Project API (`mp-api`), `pymatgen` (`PhaseDiagram`, `ReactionCalculator`), `scikit-learn`, `marimo`.
4. **Validation figure:** An "Empirical vs. DFT Phase Stability Matrix" showing false-positive DFT-stable materials (and false-negative metastable synthesizable materials) separated by the agent's precursor-competition score, validated on post-2024 synthesis attempts.
5. **Why judges rank it first:** Turns the biggest blind spot in AI for Materials (negative results buried in text and $T=0\text{ K}$ DFT illusions) into a quantitative predictive tool.
6. **Biggest risk & fallback:** Authors rarely state failures in abstracts; full-text mining is needed. *Fallback:* Query MCP Bond specifically for phrases like *"impurity phase," "attempts to synthesize," "decomposed into,"* and *"secondary phase"* within experimental sections.
7. **1st-place odds:** **Medium**

---

### Idea 5: EchemAutopsy — Physics-Constrained Mechanistic Diagnosis of Battery Degradation
1. **One-line pitch:** An autonomous electrochemical diagnostician that couples literature degradation hypotheses with differentiable `PyBaMM` simulations to decompose raw cycling curves into exact physical failure modes.
2. **How it works:**
   - Pulls public raw voltage-capacity cycling datasets (NASA, CALCE, BatteryArchive/Zenodo) across diverse C-rates and temperatures.
   - Uses MCP Bond to retrieve chemistry-specific degradation parameters (diffusivities, SEI kinetic constants, cracking thresholds) for the cell’s cathode/anode pair.
   - Runs an agentic hypothesis-testing loop with `PyBaMM` (Python Battery Mathematical Modeling): proposes coupled degradation mechanisms (SEI growth vs. lithium plating vs. active material loss), fits differential voltage ($dV/dQ$) signatures, and isolates the dominant physical failure mode over cycle life.
3. **Data/tools:** `PyBaMM`, NASA/CALCE open battery datasets, MCP Bond (parameter priors), `scipy.optimize`, `marimo`.
4. **Validation figure:** Trajectory plot showing the agent decomposing a nonlinear capacity-fade "knee" into a hidden transition from SEI growth to lithium plating 150 cycles before catastrophic drop, validated against post-mortem tear-down data from the source paper.
5. **Why judges rank it first:** Replaces black-box battery ML curve-fitting with mechanistic physical interpretability.
6. **Biggest risk & fallback:** Coupled `PyBaMM` DFN models can be slow or stiff during parameter inversion. *Fallback:* Use `PyBaMM`'s fast Single Particle Model with Electrolyte (SPMe) and bound priors tightly via MCP Bond.
7. **1st-place odds:** **Medium**

---

### Ranking of the 5 Ideas
1. **Idea 1 (ScheilForge)** — Unfair domain advantage, zero crowding, combines your existing 3D solver + `pycalphad` + MCP Bond + Marimo (eligible for General + Valency + Marimo prizes).
2. **Idea 2 (GhostPeak)** — Highest "wow" factor for general judges; finding missed phases in real papers feels like an immediate scientific discovery.
3. **Idea 3 (PiClosure)** — Cleanest mathematical/physical discovery story; fast to compute on CPU.
4. **Idea 4 (MirageHull)** — High conceptual impact on the materials AI community, though text extraction is noisier.
5. **Idea 5 (EchemAutopsy)** — Strong engineering, but battery projects face heavy competition.

---

### Honest Critique of Your Leading Candidate (Metalliksa Ti64 Melt-Pool Calibration)
* **Would it win 1st place as currently scoped?** **No (Top 15–20%, unlikely 1st).** To a general panel of physicists and chemists, "calibrating an absorptivity factor in a Ti-6Al-4V thermal solver against literature melt-pool widths" sounds like **parameter fitting / model validation**, not a scientific discovery.
* **What would make it win 1st place?** Elevate it from *calibrating one alloy's solver* to **discovering a universal cross-alloy law or designing new alloys**:
  1. **Go Multi-Alloy + Symbolic (Merge with Idea 3):** Mine melt-pool data across **8–10 diverse metals** (Ti64, IN718, 316L, AlSi10Mg, Cu, W) via MCP Bond. Show where classical enthalpy fails across reflectivity/conductivity regimes, and have the agent discover a **single symbolic dimensionless absorptivity/keyhole law** ($\Pi$-group equation) that collapses all 10 metals onto one curve without per-paper tuning.
  2. **Add the CALPHAD Discovery Step (Merge with Idea 1):** Once the calibrated thermal solver predicts $(G, \dot{T})$ accurately, feed those exact thermal fields into `pycalphad` to predict **non-equilibrium microstructure or solidification cracking**, proposing a novel printable composition. *Parameter fitting is homework; discovering a cross-alloy scaling law or a crack-free alloy is a 1st-place discovery.*
