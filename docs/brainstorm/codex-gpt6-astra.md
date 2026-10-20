My strongest bet is a system that produces a defensible scientific result and tries to disprove it. The winning video should show a surprising finding, independent validation, and why the agent was necessary.

These are conditional bets, not promises of novelty. Following your no-tools instruction, I have not verified current dataset availability or event details.

## 1. Failure Atlas: an agent discovers where a physics model stops working

**Headline:** “Our AI found where a metal-printing simulator breaks—and tested whether one physical correction fixes it.”

**What it does**
1. Extract Ti64 laser parameters, experimental conditions, and measured melt-pool dimensions from openly available papers.
2. Require a source location and uncertainty annotation for every measurement; manually verify the small evaluation set.
3. Run the existing thermal solver and map residuals against physically meaningful variables.
4. Have agents propose competing explanations: absorptivity, beam-radius conventions, conduction-to-keyhole transition, or incompatible measurement definitions.
5. Compare one-parameter corrections against a constant calibration baseline, holding out entire papers.

**Data/tools:** Metalliksa; NIST AM Bench datasets/publications, subject to matching alloy and observable; open-access LPBF papers; MCP Bond; SciPy; marimo. Do not depend on one specific dataset before checking compatibility.

**Single figure:** Measured versus predicted depth on unseen papers, showing original model, constant calibration, and proposed correction, with uncertainty bars.

**Why first:** It turns literature into an executable scientific test and produces a falsifiable result. A failure boundary that predicts when simulation becomes unreliable can be valuable even without a successful correction.

**Risk/fallback:** Incompatible experiments or an unstable solver. Restrict to single tracks and publish a validated applicability boundary instead of claiming repaired physics.

**First-place odds:** **Medium**, conditional on a substantial, independently validated result.

## 2. Conjecture Breaker: AI finds a mathematical statement and delivers its proof

**Headline:** “An AI conjectured a sharp graph-theory bound, attacked it with millions of examples, and produced a checkable proof.”

**What it does**
1. Choose one narrow, parameterized graph family and two or three invariants.
2. Enumerate small examples and propose a simple inequality or extremal characterization.
3. Search adversarially for counterexamples using enumeration and graph mutations.
4. Identify equality cases and construct a proof using the family’s recursive structure.
5. Verify algebra mechanically and distinguish exhaustive finite verification from a general proof.

**Data/tools:** House of Graphs; nauty/Traces `geng`; NetworkX; SymPy; open graph-theory literature. Favor trees or another tractable family over arbitrary graphs.

**Single figure:** The proposed bound against exhaustive examples, highlighting equality cases and the structural lemma establishing the general result.

**Why first:** A genuinely new theorem is the clearest possible “discovery in two days.” The artifact includes a proof, not just model-generated prose.

**Risk/fallback:** Rediscovering a known result or failing to prove it. Deliver a minimal counterexample to a clearly attributed conjecture, or explicitly label the output an experimentally supported conjecture.

**First-place odds:** **Low–medium**: exceptional upside, unreliable novelty and proof timeline.

## 3. Mechanism Duel: find the experiment that separates competing explanations

**Headline:** “Two reaction models explain the same data. Our agent identifies the measurement that tells them apart.”

**What it does**
1. Select a small hydrogen-oxidation ignition-delay dataset with reported conditions.
2. Fit competing, physically constrained hypotheses about a small subset of reaction rates.
3. Demonstrate that both explain the initial observations.
4. Search temperature, pressure, and composition for maximum predictive disagreement.
5. Reveal a previously hidden experimental observation near that condition and test which hypothesis survives.

**Data/tools:** ReSpecTh experimental combustion datasets; Cantera’s hydrogen mechanisms; SciPy. Use a small kinetic mechanism and a few fitted parameters to stay CPU-feasible.

**Single figure:** Both hypotheses fit the training region but diverge at the selected condition; the blinded experimental result discriminates between them.

**Why first:** It demonstrates scientific reasoning through experimental discrimination. The agent’s contribution is deciding what evidence matters next.

**Risk/fallback:** No suitable held-out experiment, or both hypotheses remain indistinguishable. Use synthetic truth for workflow validation, clearly separated from the experimental analysis; report non-identifiability honestly.

**First-place odds:** **Medium** if the experimental reveal works; **low** with synthetic validation alone.

## 4. Crystal Doppelgängers: expose and repair misleading materials evaluations

**Headline:** “Our agent tested whether a materials model learned physics—or recognized relatives of its training crystals.”

**What it does**
1. Audit one manageable materials-property benchmark.
2. Identify exact duplicates, equivalent structures, and broader composition/prototype families separately.
3. Train inexpensive descriptor-based baselines.
4. Compare random splits with duplicate-controlled and family-held-out splits.
5. Match training sizes, quantify uncertainty, and locate the families driving performance differences.

**Data/tools:** Matbench `matbench_log_kvrh` or `matbench_log_gvrh`; pymatgen StructureMatcher; matminer; scikit-learn.

**Single figure:** Prediction error across the three split designs, with uncertainty and a concrete example of structural overlap.

**Why first:** A substantial, previously undocumented evaluation failure could affect many materials-AI claims. Can’s evaluation experience is a strong execution advantage.

**Risk/fallback:** The dataset is clean or the effect is familiar. Publish a reproducible stress test. Family-held-out degradation demonstrates distribution shift; it does not, by itself, prove leakage.

**First-place odds:** **Low–medium**, rising only with a surprising, well-controlled finding.

## 5. Catalyst Stress Test: discover whether the “best catalyst” survives its assumptions

**Headline:** “Our agent challenged a catalyst ranking—and found which conclusions survive uncertainty.”

**What it does**
1. Select one reaction and a small, internally comparable adsorption-energy dataset.
2. Reconstruct its descriptor-based activity ranking.
3. Extract the assumptions governing reference energies, corrections, and scaling relations.
4. Perturb those assumptions within justified ranges, accounting for correlated errors.
5. Identify robust winners, rank reversals, and the additional calculation most likely to resolve uncertainty.

**Data/tools:** Catalysis-Hub reaction energies and calculation metadata; ASE; CatHub tooling; NumPy/SciPy; MCP Bond for supporting literature.

**Single figure:** Catalyst rank distributions under justified uncertainty, highlighting a fragile nominal winner and any robust alternative.

**Why first:** It changes a scientific decision: which candidate deserves expensive follow-up. The strongest result identifies a specific overlooked candidate that survives multiple defensible assumptions.

**Risk/fallback:** Incompatible calculations or arbitrary uncertainty choices. Restrict to one internally consistent study and publish a transparent sensitivity audit.

**First-place odds:** **Low–medium**; uncertainty propagation alone is insufficient.

## Ranking and Metalliksa verdict

**My ranking: 1 > 3 > 2 > 4 > 5.** For Can specifically, Failure Atlas offers the best balance of existing capability, scientific relevance, and a compelling demonstration.

The current Metalliksa proposal **could win, but paper extraction plus fitted absorptivity probably would not**. That can look like routine calibration wrapped in an agent.

What would make it competitive:

- Establish numerical convergence and a trustworthy baseline before interpreting residuals.
- Hold out entire papers and prevent their measurements from influencing correction selection.
- Beat constant calibration and a simple empirical baseline.
- Predict a failure regime or transfer behavior—not merely lower average error.
- Show the agent rejecting a plausible explanation because evidence contradicts it.
- State exactly what predated the hackathon.

The strongest ending is either “this correction transfers to unseen experiments” or “this physical boundary predicts failure.” A confidently explained negative result beats an overclaimed discovery.