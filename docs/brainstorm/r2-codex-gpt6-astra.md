**My pick: a counterexample-seeking agent that finds directional auxetic behavior hidden by ordinary materials screening.** It offers a physical result that can be independently checked, runs on modest compute, and makes a strong four-minute demonstration.

These are proposals, not verified discoveries. Dataset names below are established public resources; I have not checked current download availability. Scores are comparative judgments, not predicted judging outcomes.

**1. Hidden auxetics: discover what averaged material properties conceal**

**Video headline:** “This crystal looks ordinary in the database—but stretches sideways when pulled in the right direction.”

**System:** Load elastic tensors → validate conventions and mechanical stability → calculate directional Young’s modulus and Poisson’s ratio → let an agent propose composition/symmetry hypotheses and request counterexample searches → verify shortlisted directions with an independent calculation. Reserve a chemical-family holdout for testing any explanatory rules.

**Data/tools:** The public de Jong elastic-tensor collection, distributed through matminer’s `elastic_tensor_2015`; NumPy, SciPy, pymatgen, optional marimo.

**One figure:** Average Poisson’s ratio versus minimum directional Poisson’s ratio. Highlight crystals with positive averages but negative directional values; annotate their loading directions.

**Scores:** Impact **4**—exposes candidates missed by averaged screening; innovation **4**—conditional on useful counterexample-guided explanations, since directional elasticity itself is established; scalability **5**—cheap tensor calculations extend across databases; relevance **5**—direct structure–mechanical-property discovery.

**Hard result:** A reproducible list of mechanically admissible candidate crystals, their minimum Poisson’s ratios, loading/transverse directions, and directional stiffnesses. Report the fraction overlooked by an average-property filter. These are predictions from existing DFT tensors, not experimentally demonstrated auxetics.

**Risk/fallback:** Tensor conventions or numerical artifacts create false positives. Validate against isotropic references and tensor rotations; exclude questionable records. If candidates are already known, deliver a verified screening-failure atlas and explicitly label rediscoveries.

**2. Molecular design rules that reverse direction**

**Video headline:** “The same molecular edit improves one electronic property in one chemical context—and worsens it in another.”

**System:** Extract matched molecular pairs → enumerate a small, preregistered set of edits → have an agent propose contextual explanations → test them on untouched molecular families → return replicated sign reversals with supporting and contradicting examples.

**Data/tools:** Public QM9 molecular structures and calculated properties; RDKit, pandas, SciPy, scikit-learn. Use HOMO–LUMO gaps, polarizability, and dipole moments; do not describe orbital gaps as measured optical gaps.

**One figure:** Effect of one molecular transformation across chemical contexts, with uncertainty intervals and representative molecule pairs.

**Scores:** Impact **4**—replaces misleading universal design rules with conditional ones; innovation **4**—counterexample-driven rule revision; scalability **5**—extends to larger property datasets; relevance **5**—direct molecular structure–property relationships.

**Hard result:** A ranked table of transformations with opposite effects across contexts, sample sizes, effect magnitudes, and holdout replication results.

**Risk/fallback:** Too few independent matched pairs; QM9’s small molecules limit generality. Begin with a pair-count gate. If no reversal survives validation, publish a useful negative result: which proposed rules fail replication and which remain supported. Matched pairs establish associations, not universal causal effects.

**3. Dielectric candidates that survive stricter scrutiny**

**Video headline:** “An AI scientist tries to disqualify every promising dielectric—and shows which candidates survive.”

**System:** Build an initial dielectric/band-gap shortlist → agent identifies reasons rankings may be misleading → apply predefined completeness, gap-method, anisotropy, and eligibility checks → measure ranking sensitivity → produce an auditable survivor list.

**Data/tools:** Public JARVIS-DFT `dft_3d` through jarvis-tools; pymatgen, pandas, SciPy. Use only records with the necessary dielectric components and electronic-property calculations.

**One figure:** Candidate trajectories from permissive ranking to progressively stricter filters, with rejection reasons.

**Scores:** Impact **4**—reduces wasted follow-up calculations; innovation **4**—automated adversarial evaluation rather than straightforward ranking; scalability **5**—reusable checks across databases; relevance **5**—functional-materials selection.

**Hard result:** Initial and surviving candidate counts, ranking changes, and a small shortlist with provenance and explicit missing evidence.

**Risk/fallback:** **Uncertain data intersection:** I cannot guarantee enough records jointly contain the required dielectric tensors and multiple gap estimates. Audit coverage first; narrow to electronic dielectric response and one gap method if necessary. Do not claim breakdown strength, synthesizability, or device performance.

**4. Can scientific agents discover efficiently when chemistry changes?**

**Video headline:** “We gave AI scientists the same experimental budget—and tested whether their discovery strategy survives unfamiliar chemistry.”

**System:** Treat existing measured labels as a hidden experimental oracle → agents select batches and revise hypotheses → compare random, diversity-based, and surrogate-model acquisition → repeat across seeds and held-out chemical families.

**Data/tools:** Matbench’s public `matbench_expt_gap`; matminer composition features, scikit-learn, frontier-model APIs if available.

**One figure:** Discovery yield versus revealed-label budget, separated into familiar and unfamiliar chemical families.

**Scores:** Impact **4**—tests whether agent recommendations justify experimental expenditure; innovation **4**—iterative discovery under distribution shift; scalability **5**—a reusable benchmark harness; relevance **4**—materials-specific outcomes, though primarily evaluation research.

**Hard result:** Budget required to recover a predefined fraction of target-gap compounds, uncertainty across runs, and strategy failure cases.

**Risk/fallback:** Literature familiarity can contaminate LLM performance, and formula-only inputs lose polymorph information. Disclose both; include anonymized feature-only trials. Call it retrospective discovery simulation, not new-material discovery.

**Best topic: hidden auxetics — 34-hour execution**

Its advantage is **a checkable physical finding without model training, expensive simulation, or uncertain multi-dataset joins**. Its main weakness is novelty: the agent must produce a useful scientific explanation or screening insight beyond a standard tensor scan.

1. **Hours 0–4: feasibility gate.** Load data, inspect licensing/provenance, validate units and tensor conventions. Implement isotropic and rotation-invariance checks. Freeze the candidate criteria.
2. **Hours 4–10: deterministic discovery engine.** Filter inadmissible tensors, scan orientations, refine extrema, and independently verify shortlisted directional responses.
3. **Hours 10–16: bounded agent loop.** Allow hypothesis proposals, targeted calculations, and counterexample requests through explicit tools. Log every decision. Compare against an equal-budget random hypothesis/search baseline.
4. **Hours 16–22: scientific validation.** Test rules on reserved chemical families; assess numerical sensitivity and stiffness tradeoffs. Check literature for the leading candidates and distinguish known examples from potentially unreported findings.
5. **Hours 22–28: freeze the result.** Finalize candidate tables, the main figure, reproducible notebook, and limitations. Select one convincing crystal for the demonstration.
6. **Hours 28–34: deliver.** Clean public code, rerun from documented inputs, write the one-page summary, and record a sub-four-minute video centered on the physical counterexample and its verification.