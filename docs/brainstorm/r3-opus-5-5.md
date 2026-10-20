# Round 3: Opus 5.5 judgment

## 1. Per-finalist critique

Scores are on a 1–5 scale: **I** = impact, **N** = innovativeness and ease for researchers, **S** = scalability, **R** = relevance to materials science and chemistry.

| | I | N | S | R | Total |
|---|---|---|---|---|---|
| A DataDoctor | 4 | 4 | 4 | 5 | **17** |
| B HiddenHull | 3 | 3 | 4 | 4 | 14 |
| C EigenDrop | 4 | 4 | 3 | 5 | 16 |
| D Contradiction court | 3 | 2 | 3 | 4 | 12 |
| E SinkBreaker | 4 | 3 | 3 | 5 | 15 |

**A. DataDoctor**
- **Why it could win:** a named, widely used benchmark (matbench_expt_gap) turns out to contain verifiable errors. The output is a corrections file plus "the leaderboard changes" — a real discovery inside two days, and a natural fit for the Valency prize.
- **Why it would lose:** if most of the flags are duplicates, polymorph ambiguity or metals stored as 0 eV, judges will call it janitorial work. The MAE gain is also **circular** if the same ML model both flags outliers and scores the result.
- **Prior work:** Dunn et al. 2020 (Matbench) already deduplicated this data. Generic label-noise detection exists (Northcutt et al., confident learning / cleanlab). I don't know of a systematic, literature-traced audit of Zhuo 2018, but I'm only moderately sure.
- **Hidden risk:** I'm not sure Zhuo 2018 gives a source citation for each entry. If it doesn't, finding the original paper becomes a composition-plus-"band gap" search, and precision drops. Verify this first.

**B. HiddenHull / DiscoveryGym**
- **Why it could win:** clean experimental design and a "frontier agents vs. baselines" headline.
- **Why it would lose:** it measures discovery rather than making one. With CLI calls taking 10–60 s each, you can afford only a few runs, so the statistics will be weak. WBM is public, so leakage could sink the result.
- **Prior work:** Riebesell et al., Matbench Discovery (Nature Machine Intelligence, 2025). Gruver et al. 2024 (fine-tuned LLMs generating stable crystals). LLM-evolutionary crystal search: LLMatDesign, MatLLMSearch (I'm unsure of exact authors).

**C. EigenDrop**
- **Why it could win:** a list of candidate lower-symmetry ground states for "stable" MP entries, backed by phonon band figures and literature hits. It reads as a discovery.
- **Why it would lose:** universal MLIPs systematically underestimate force constants ("softening"), which produces false imaginary modes. Many hits will also be known high-temperature phases kept stable by anharmonicity (cubic perovskites, for example). With no DFT check, skeptical judges will discount it.
- **Prior work:**
  - Loew et al. 2024/25, *Universal MLIPs are ready for phonon calculations*.
  - Deng et al. 2024 on MLIP softening.
  - Petretto et al. 2018 (MP phonon database) and Togo's phonondb.
  - Malyi & Zunger on polymorphous structures.

**D. Literature contradiction court**
- **Why it could win:** the story appeals to working scientists.
- **Why it would lose:** normalizing measurement conditions (temperature, phase, film vs. bulk, method) is an unsolved problem. Judges will see "RAG with extra steps", which lost in 2025.
- **Prior work:** SciFact-style contradiction detection; Court & Cole 2018 (Curie/Néel temperature database); Dong & Cole 2022 (auto-extracted band gap database).

**E. SinkBreaker**
- **Why it could win:** synthesis is the field's bottleneck, and the 2025 winner was a synthesis tool.
- **Why it would lose:** the Ceder group owns this space, and ground-truth failed syntheses are scarce.
- **Prior work:**
  - Aykol et al. 2021 (JACS, synthesis routes).
  - McDermott et al. 2021 (reaction networks).
  - Szymanski et al. 2023: ARROWS3 and the A-Lab, with its failure analysis.
  - Todd et al. 2021 (selectivity via local chemical potentials).
  - Chen et al. 2024 (precursor selection by phase-diagram navigation).
  - Leeman & Palgrave 2024 (critique of the A-Lab).

## 2. Feasibility (solo, 34 h)

| | Verdict | Main bottleneck |
|---|---|---|
| A | Tight but realistic | Tracing each entry to its source paper; MCP Bond may return abstracts, not tables |
| B | Tight | Agent throughput → too few runs for statistics |
| C | Realistic on compute (8 GB is fine for small cells) | Telling real instabilities from MLIP artifacts without DFT |
| D | Unrealistic at quality | Condition normalization |
| E | Tight | No validation set beyond about 17 A-Lab failures and scattered negative results |

## 3. Ranking by probability of winning 1st

1. **A DataDoctor**: about 35%
2. **C EigenDrop**: about 25%
3. **E SinkBreaker**: about 17%
4. **B HiddenHull**: about 15%
5. **D Contradiction court**: about 8%

## 4. Sharpened winner (A, with C's consensus trick)

1. Audit two datasets: matbench_expt_gap (visibility) and an experimental formation-enthalpy set with references (cleaner physics, since DFT error bars there are about 0.05–0.1 eV/atom).
2. Flag an entry only when **three independent signals agree**: MP2020 DFT, two ML models from different families, and chemical-family trends. This avoids the circularity problem.
3. Trace each flag to its source via MCP Bond and assign one of three verdicts (dataset error / real physics / unclear) with quoted evidence. Hand-verify 30 entries to report precision.
4. Headline result: "X% of labels wrong; Matbench leaderboard rank changes", measured with a model that played **no** part in flagging.
5. Ship it as a Marimo notebook app plus a corrections CSV, which makes it eligible for both sponsor prizes.

## 5. Three new-discovery topics

**N1. Cross-database hull reconciliation (GNoME × Alexandria × MP)**
- **Finding:** the fraction of GNoME "stable" entries that sit more than 25 meV/atom above the convex hull once Alexandria and MP entries are merged in, and the reverse. Results broken down by chemical system.
- **Why new:** Cheetham & Seshadri 2024 critiqued GNoME on a hand-picked sample. I don't know of a full joint-hull reconciliation, though Alexandria may already have absorbed GNoME data.
- **How verified:** pymatgen PhaseDiagram on the merged entries; relax disputed cases with MACE and CHGNet.
- **Data:** GNoME GitHub release, Alexandria PBE (ICAMS), MP API. ⚠ Energy compatibility between the three databases (functional, pseudopotentials, U values) is not certain; check it before building any hull.

**N2. Time-split check: how many GNoME predictions have since been synthesized?**
- **Finding:** how many GNoME-only stable predictions (released Nov 2023) were independently reported experimentally in 2024–2026, plus whether that rate rises with distance below the hull.
- **Why new:** a dataset-level fact nobody has published at scale, as far as I know. The A-Lab tested 41 targets, and that work was itself disputed.
- **How verified:** MCP Bond search on composition plus structure type; check the reported crystal structure against the predicted one with StructureMatcher; manually verify the top hits.
- **Data:** GNoME CSV, MCP Bond. ⚠ Formula-string recall is noisy, and literature indexing may lag for 2026 papers.
- **Fit:** strong for the Valency prize.

**N3. Chemical-sanity audit of COD inorganic structures**
- **Finding:** a ranked list of COD inorganic entries that are probably mis-deposited (wrong element, missing H, impossible occupancy). Detection uses three checks: bond-valence-sum deviation, charge-balance failure, and very large MLIP forces or relaxation energy.
- **Why new:** checkCIF validates single structures at deposition. A database-wide physics-based audit is, as far as I know, unpublished, though I'm unsure about this.
- **How verified:** an MLIP relaxation should collapse or distort the bad entries; agent retrieves the original papers to confirm the error.
- **Data:** COD (open, about 500k entries; restrict to the inorganic subset of tens of thousands), pymatgen BVAnalyzer, MACE-MP-0.

**Bottom line:** A wins only if it finds errors in a **named benchmark**, verified by humans. Without that headline number, C's discovery story beats it.
