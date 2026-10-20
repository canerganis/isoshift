# Six new ideas

## 1. ChronoCSP: can a laptop predict crystal structures published after its models were trained?

1. **Steps:** Pull COD inorganic entries deposited after Jan 2025. Keep ordered cells with 24 atoms or fewer that have no StructureMatcher match in MP, Alexandria, GNoME or OQMD (5h). Pick 40 to 60 targets with new prototypes (2h). For each composition, build about 1000 candidates by prototype substitution plus PyXtal random search and relax them with MACE or ORB v3 (overnight on the GPU, about 14h). Compare the top 1 and top 10 results to the experimental structure (3h). Then relax the true structure and check whether it is the energy minimum. This separates search failures from energy ranking failures (3h).
2. **Data and tools:** COD with deposition dates, MP, Alexandria, GNoME (GitHub), PyXtal, pymatgen, MACE-MP, ORB v3.
3. **Hard result:** Top 1 and top 10 success rate on structures the models have never seen, plus the fraction of targets where the real structure is not the model's energy minimum.
4. **Why new:** CSPBench (Hu group, 2024) and CrystaLLM evaluations use MP structures that are probably in the training data. I know of no time split on new prototypes.
5. **Verification:** StructureMatcher plus RMSD. The deposition dates prove the targets are unseen. A null result still splits into search error versus energy error.
6. **Risk:** COD may contain too few small, ordered, new structures from after the cutoff.
7. **Odds:** 12%

## 2. AmorphousLimit at Scale: testing a synthesizability bound 3x to 5x wider

Aykol et al. (Sci. Adv. 2018) proposed that synthesizable polymorphs sit below the energy of the amorphous phase. They tested 41 systems with DFT AIMD.

1. **Steps:** Select systems with at least 2 ICSD-tagged polymorphs in MP, plus Aykol's 41 for calibration (3h). Melt and quench 150 to 250 atom cells with MACE-MPA-0 and ORB v3, 3 replicates each (overnight on the GPU, about 16h). Calibrate the MLIP amorphous energies against Aykol's DFT values (2h). List the known polymorphs that sit above the limit (3h). Apply the bound to GNoME and Alexandria candidates in the same systems (3h).
2. **Data and tools:** MP (ICSD tags, r2SCAN energies), Aykol's supplementary data, GNoME, Alexandria, ASE MD, two uMLIPs.
3. **Hard result:** The bound confirmed or refuted on about 100 to 150 systems, a list of named violators, and the fraction of GNoME candidates that cannot be synthesized under this bound.
4. **Why new:** I know of no MLIP-scaled test. The closest work is the original paper and recent uMLIP amorphous benchmarks.
5. **Verification:** Calibration on the original 41 systems, two potentials, replicate quenches and a quench rate sweep. Violators are rechecked against MP r2SCAN polymorph gaps.
6. **Risk:** uMLIP amorphous errors are comparable to polymorph energy spreads, which are tens of meV per atom.
7. **Odds:** 15%

## 3. InvariantFuzz: metamorphic testing of the materials software stack

1. **Steps:** Sample 5000 MP and COD structures (1h). Apply transforms that should change nothing: origin shift, axis permutation, supercell, setting change, atom reordering, rotation, and noise below tolerance (3h). Check that outputs stay the same:
   - space group (spglib, pymatgen)
   - StructureMatcher result
   - CrystalNN coordination and dimensionality
   - XRD pattern and oxidation state guesses
   - CIF round trip through pymatgen, ASE and gemmi
   - uMLIP energies and forces (MACE, CHGNet, ORB, SevenNet)

   That check takes about 12h. Shrink each violation to a minimal reproducer (5h). Count hull stability flips and file upstream issues (3h).
2. **Data and tools:** MP, COD, spglib, pymatgen, ASE, gemmi, matminer, the four uMLIPs.
3. **Hard result:** A violation matrix (tool by transform), N bugs filed with links, and the number of materials whose stability label flips after a pure relabeling.
4. **Why new:** Metamorphic testing is standard in software engineering, and Langer et al. (2024) probed rotation symmetry breaking in MLIPs. I know of no systematic test across the whole stack.
5. **Verification:** Each bug has a 10-line reproducer, and maintainers can acknowledge it.
6. **Risk:** The tools are mature, so the findings may be minor tolerance edge cases.
7. **Odds:** 8%

## 4. NoveltyCourt: how novel are generative crystal models really?

1. **Steps:** Collect the released sample sets from MatterGen, DiffCSP, CrystaLLM and Chemeleon, plus the "new materials" claimed in papers (4h). Build a union reference from MP, Alexandria, GNoME, OQMD, AFLOW, JARVIS and COD. Matching is disorder-aware, so ordered structures map to known disordered parents (8h). Relax with an MLIP and match (8h). Report per model (3h).
2. **Data and tools:** The open databases above, pymatgen, one uMLIP.
3. **Hard result:** The true novelty fraction per model and a released checking tool.
4. **Why new:** Cheetham and Seshadri (2024) did this manually for GNoME, and the TaCr2O6 critique hit MatterGen. LeMat-GenBench checks only against LeMat-Bulk.
5. **Verification:** Manual review of 30 random matches and a tolerance sweep.
6. **Risk:** Missing sample sets, partial overlap with LeMat, and closeness to ideas 5 and 7.
7. **Odds:** 9%

## 5. ConjectureBreaker: counterexamples to open conjectures in chemical graph theory

1. **Steps:** Collect open conjectures on Randić, Wiener, Zagreb, ABC and Szeged indices from AutoGraphiX and Graffiti surveys (Aouchiche, Hansen) and from arXiv (4h). Check every chemical graph with max degree 4 up to about 14 vertices with nauty, and trees up to about 22 vertices (8h). Beyond that, run LLM-guided local search and Wagner-style reinforcement learning (10h). Test PubChem molecular graphs (3h). Verify any hit in exact arithmetic (2h).
2. **Data and tools:** nauty geng, networkx, PubChem.
3. **Hard result:** A counterexample graph that anyone can check instantly, or a verified bound up to n.
4. **Why new:** Wagner (2021) and FunSearch did this for general combinatorics. I know of no systematic sweep of chemical index conjectures.
5. **Verification:** Exact rational recomputation, done twice independently.
6. **Risk:** The conjectures may already be settled, nothing may turn up, and the link to materials is weak.
7. **Odds:** 4%

## 6. AntiHammond: where Bell–Evans–Polanyi fails across about 170k DFT reactions

1. **Steps:** Load RGD1 and Transition1x (2h). Classify reactions by the bonds that change, using RDKit reaction center templates (6h). Fit a Bell–Evans–Polanyi (BEP) line per class and flag classes with flat or negative slopes and Hammond anomalies in transition state geometry (6h). Spot-check outliers with xtb reaction paths (6h). Explain the violators with Marcus intrinsic barriers (4h).
2. **Data and tools:** RGD1, Transition1x, RDKit, xtb.
3. **Hard result:** A table of BEP slopes per class and a list of violating classes with mechanistic explanations.
4. **Why new:** These datasets are used for machine learning, but I know of no class-by-class test of the BEP law on them.
5. **Verification:** IRC information in RGD1, and xtb reproducing the sign of the trend.
6. **Risk:** Violations may turn out to be data errors, which collapses into a plain audit.
7. **Odds:** 6%

# The wow idea

AmorphousLimit at Scale. An expert reacts when a well-known Science Advances hypothesis about what can be synthesized gets tested on 3x to 5x more systems in two days. Either way the event's question gets an answer. If the bound holds, it becomes a cheap, physical filter for millions of predicted materials, and you report the share of GNoME candidates it rules out. If it breaks, you name specific counterexample materials, and anyone can check them against MP polymorph energies.

Feasibility solo is moderate, around 60% for a clean result. Throughput is the constraint: a MACE-small quench of about 200 atoms over roughly 20k steps should take 6 to 10 minutes on the RTX 4060, so 100 to 150 systems fit in one overnight run. The real danger is accuracy. Calibration against Aykol's 41 DFT values in the first 6 hours decides whether to continue. If MLIP error against DFT is above about 30 meV per atom, switch to idea 1, which uses the same setup.
