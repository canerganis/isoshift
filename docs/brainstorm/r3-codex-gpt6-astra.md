**My ranking: A > E > D > B > C.** A has the strongest route to a useful tool plus a defensible scientific result. None deserves a novelty premium merely for using multiple agents.

Scores below assess the **credible 34-hour submission**, not the ideal product. Prior-work references are from memory, unverified in this round.

| Finalist | Research impact | Innovation / usefulness | Scalability | Materials / chemistry | Feasibility |
|---|---:|---:|---:|---:|---|
| **A. DataDoctor** | 5 | 4 | 4 | 5 | **Realistic**, narrowly scoped |
| **E. SinkBreaker** | 4 | 4 | 4 | 5 | **Tight** |
| **D. Contradiction court** | 4 | 3 | 4 | 5 | **Realistic**, narrowly scoped |
| **B. Discovery benchmark** | 3 | 2 | 5 | 5 | **Tight** |
| **C. EigenDrop** | 4 | 3 | 3 | 5 | **Unrealistic** for convincing discovery |

**A — DataDoctor**

- **Could win:** A documented error in a widely reused dataset, traced to its original source, corrected reproducibly, and shown to affect downstream conclusions. Researchers can immediately use the output.
- **Could lose:** Treating disagreement with DFT or ML as evidence that an experiment is wrong. Band gaps depend on phase, temperature, defects, and measurement definition; consensus can erase real physics.
- **Prior work:** *matminer* (Ward et al., 2018) and *Matbench* (Dunn et al., 2020) establish much of the infrastructure. Confident Learning (*Cleanlab*; Northcutt et al., 2021) establishes automated label-error detection, principally for classification. None establishes this exact provenance-based correction workflow.
- **Bottleneck:** Obtaining original tables and resolving provenance. Evaluate against an untouched, independently checked test set; lower MAE after editing test labels proves little.

**E — SinkBreaker**

- **Could win:** Explain a documented failed synthesis through a specific competing reaction, then identify a precursor change supported by an existing successful route.
- **Could lose:** Presenting thermodynamic accessibility as a kinetic mechanism. Interface reactions omit transport, nucleation, atmosphere, and changing chemical potentials.
- **Prior work:** McDermott et al., *“A graph-based network for predicting chemical reaction pathways in solid-state materials synthesis”* (2021), directly overlaps. Merely wrapping reaction networks in an agent is insufficient.
- **Bottleneck:** Finding comparable failed/successful experiments with sufficiently complete conditions. Restrict to one chemistry and a small retrospective validation set.

**D — Literature contradiction court**

- **Could win:** Resolve an influential apparent contradiction into a previously overlooked condition dependence—or identify a demonstrable transcription/unit error propagated across papers.
- **Could lose:** A polished literature assistant with cherry-picked examples. An additional paper is not automatically independent evidence, especially when citations share an original measurement.
- **Prior work:** *ChemDataExtractor* (Swain and Cole, 2016) and *ChemDataExtractor 2.0* (2021) reduce novelty in extraction and normalization. I cannot confidently name an exact materials contradiction-adjudication predecessor.
- **Bottleneck:** Matching material identity and experimental conditions. One property, one family, explicit unresolved outcomes.

**B — Discovery benchmark**

- **Could win:** Establish a surprising, statistically robust result about whether frontier agents outperform inexpensive search under genuinely matched information and computational budgets.
- **Could lose:** Rebranding retrospective candidate ranking as discovery. Public WBM structures and labels create contamination risk; a leakage probe cannot establish absence of memorization.
- **Prior work:** *Matbench Discovery* directly occupies this territory; *Wren* already demonstrates efficient stability screening using crystallographic representations.
- **Bottleneck:** Enough replicated trajectories given CLI latency. Fix the candidate universe, count all oracle access, and include strong surrogate baselines. Open-ended MLIP energies cannot be compared naively with an MP DFT hull.

**C — EigenDrop**

- **Could win:** Find an unreported distortion that survives independent calculation and matches overlooked experimental evidence.
- **Could lose:** Rediscover numerical artifacts or MLIP deficiencies. A lower MLIP energy after mode following is not a verified new phase.
- **Prior work:** Soft-mode condensation is established; Pallikara et al., *“The physical significance of imaginary phonon modes in crystals”* (2022), reviews the underlying issues. Universal-MLIP phonon calculations are already an active field.
- **Bottleneck:** Supercell calculations plus convergence and independent validation. Without affordable DFT confirmation, this is a hypothesis generator.

**Sharpened winner — A with D’s adjudication discipline**

1. Audit one chemically coherent slice of one experimental dataset.
2. Retrieve original evidence; distinguish transcription, identity, conditions, and unresolved disagreement.
3. Release a versioned correction ledger with exact source locations.
4. Measure changes on a frozen, independently checked evaluation set.
5. Demonstrate confirmed corrections and honest abstentions in an interactive notebook.

**Three additional discovery bets**

These offer plausible findings, not guaranteed novelty; each needs a targeted literature check.

1. **Hidden negative linear compressibility.** Screen open **JARVIS-DFT elastic tensors** for mechanically stable crystals with a negative eigenvalue of the hydrostatic compressibility tensor. Finding: an underreported candidate and its contraction direction. Verify tensor conventions, stability, numerical sensitivity, and an independent same-phase tensor where available. Novelty lies in the specific candidate; independent tensors may be unavailable.

2. **Adsorbent ranking reversals with temperature.** Use the **NIST/ARPA-E Adsorption Database** to identify matched materials whose low-pressure CO₂ adsorption rankings cross with temperature. Verify against original isotherms, uncertainty-aware Henry fits, and consistent activation conditions. Finding: a previously unreported crossover within a defined comparison set, not a process-performance claim. Sufficient matched measurements are uncertain.

3. **Does diffusion compensation survive chemical controls?** Analyze the open **UW dilute-solute diffusion database** for activation-energy/prefactor compensation within hosts. Verify with host-stratified analysis, leave-element-out validation, permutation tests, and source parameter checks. Finding: a robust host-specific relation—or evidence that an apparent pooled relation disappears after controls. Exact novelty requires checking prior compensation studies.