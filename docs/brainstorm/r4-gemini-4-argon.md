### Idea 1: HyperbolicScout (Condensed Matter Physics and Nanophotonics)

1. **Headline:** Reconstruct the full infrared permittivity tensor across 8,000 polar crystals to discover natural hyperbolic and monoclinic shear polariton materials validated against experimental mineral reflectance spectra.
2. **Steps:**
   1. Download precomputed harmonic force constants, Born effective charges, and high frequency dielectric tensors from Kyoto PhononDB and Materials Project (3 hours).
   2. Use Phonopy to extract zone center transverse and longitudinal optical phonon frequencies, eigenvectors, and mode oscillator strength tensors for all anisotropic polar crystals (4 hours).
   3. Analytically evaluate the frequency dependent complex Lorentz permittivity tensor from 0.5 to 60 THz and classify Type I, Type II, in plane biaxial hyperbolic, and monoclinic off diagonal shear polariton windows (5 hours).
   4. Cross match predicted Reststrahlen hyperbolic windows against experimental FTIR reflectance spectra in the RRUFF mineral database (6 hours).
   5. Build an interactive Marimo polariton dispersion explorer and produce the summary figure and video (8 hours).
3. **Data and tools:** Togo Kyoto PhononDB (10,034 crystals with `BORN` and `FORCE_SETS`), Materials Project DFPT dielectric dataset, RRUFF open FTIR mineral database, Phonopy, Pymatgen, NumPy, Marimo.
4. **The hard result:** An open atlas of 8,000 frequency dependent infrared dielectric tensors, an interactive Marimo tool, and a ranked table of 25 previously unrecognized in plane biaxial hyperbolic and shear polariton crystals (including candidates inside the 8 to 13 micrometer atmospheric thermal window) with overlaid RRUFF experimental FTIR reflectance peaks.
5. **Why it is new:** Experimental nanophotonics relies on roughly four natural hyperbolic crystals (hBN, alpha MoO3, calcite, beta Ga2O3). Existing databases tabulating static dielectric constants never assemble the dynamic frequency dependent tensor from Born charges and optical eigenvectors to hunt for sign indefinite principal permittivities across crystal symmetries.
6. **Verification:** First, recover the exact experimental hyperbolic frequency bands of hBN, alpha MoO3, quartz, and beta Ga2O3 within 15 inverse centimeters. Second, verify new mineral hits directly against experimental Reststrahlen reflectance plateaus in RRUFF FTIR spectra.
7. **Risk:** PhononDB uses PBE functional lattice parameters, which red shifts optical phonon frequencies by 3 to 5 percent relative to room temperature FTIR spectra.
8. **1st place odds:** 35%

### Idea 2: CrysRUM (Mathematical Crystallography and Mechanics)

1. **Headline:** Exact Bloch wave polyhedral rigidity nullspace enumeration across 40,000 framework crystals to discover rigid unit modes and negative thermal expansion materials.
2. **Steps:**
   1. Extract all corner sharing coordination polyhedra frameworks (tetrahedra and octahedra) from Materials Project and COD using Pymatgen Voronoi connectivity (4 hours).
   2. Construct the periodic Maxwell Calladine bar and joint rigidity matrix modulated by Bloch wavevector across high symmetry Brillouin zone paths (6 hours).
   3. Compute the exact singular value spectrum in NumPy to catalog crystals hosting zero energy Rigid Unit Modes (RUMs) along lines, planes, or full volumes of reciprocal space (4 hours).
   4. Calculate volume derivative mode Gruneisen parameters using MACE MP 0 on the RTX 4060 for the top 80 RUM hosts to identify negative thermal expansion (6 hours).
   5. Validate top candidates against multi temperature experimental X ray diffraction entries in COD and package in Marimo (6 hours).
3. **Data and tools:** Materials Project structure dump, Crystallography Open Database (COD), Pymatgen, SciPy SVD, MACE MP 0, ASE, Marimo.
4. **The hard result:** The `crysrum` Python package, a complete topological classification of Bloch rigidity nullspaces across 40,000 inorganic frameworks, and a validated list of 15 negative thermal expansion crystals with MACE Gruneisen parameters and historical multi temperature COD cell volumes.
5. **Why it is new:** Dove and Hammonds developed CRUSH in the 1990s for manual single crystal RUM analysis on about 40 zeolites and perovskites. A database wide periodic Bloch rigidity nullspace scan paired with MLIP Gruneisen validation has never been executed.
6. **Verification:** Recover classic NTE benchmarks (ZrW2O8, ScF3, beta cristobalite) with exact reciprocal space RUM manifolds, then confirm negative volumetric expansion on newly flagged crystals using multi temperature experimental CIFs in COD.
7. **Risk:** Automated coordination polyhedra perception can misassign distorted Jahn Teller octahedra, requiring strict bond length variance cutoffs.
8. **1st place odds:** 28%

### Idea 3: AtropoScope (Medicinal Chemistry and Stereochemistry)

1. **Headline:** Uncover unannotated Class 3 axial enantiomers hidden inside clinical and bioactive molecules that are registered as flat achiral structures in ChEMBL.
2. **Steps:**
   1. Filter ChEMBL clinical candidates, approved drugs, and PDB bound ligands using RDKit SMARTS for sterically hindered ortho substituted biaryls, heterobiaryls, and benzamides Marked with zero tetrahedral stereocenters (3 hours).
   2. Run fast MMFF94s dihedral pre screening followed by parallelized GFN2 xTB constrained torsion scans on the top 400 hindered single bonds (6 hours).
   3. Calibrate GFN2 xTB barriers against the 80 compound experimental LaPlante atropisomer benchmark to identify Class 3 stealth atropisomers with rotational barriers above 28 kcal/mol (4 hours).
   4. Extract RCSB PDB co crystal structures for each Class 3 hit and measure dihedral angles across independent protein pockets to prove single enantiomer selection (6 hours).
   5. Package the CLI scanner, calibrated barrier dataset, and 3D PDB overlays into a Marimo notebook (7 hours).
3. **Data and tools:** ChEMBL 34 SQLite dump, RCSB Protein Data Bank, LaPlante benchmark set, RDKit, GFN2 xTB, SciPy, Marimo.
4. **The hard result:** A calibrated axial chirality barrier predictor and a checkable table of 15 to 30 clinical or bioactive compounds registered as achiral in ChEMBL that possess multi month racemization half lives at 37 Celsius and crystallize as a single axial enantiomer in PDB protein pockets.
5. **Why it is new:** Standard cheminformatics tools (RDKit CIP rules) detect point and double bond stereocenters from topology alone but ignore axial chirality because it depends on a kinetic barrier threshold. No public audit has crossed quantum torsional barriers of flat ChEMBL clinical structures with PDB enantiomer locking.
6. **Verification:** Calibrate barriers against experimental racemization half lives ($R^2 > 0.85$ expected) and verify that independent PDB crystal structures of the same drug resolve exclusively to one axial atropisomer ($P$ or $M$) with low B factors.
7. **Risk:** GFN2 xTB in vacuum can underestimate barriers stabilized by solvent hydrogen bonding; running ALPB implicit water solvation mitigates this at minimal CPU cost.
8. **1st place odds:** 25%

### Idea 4: TopoTwin (Solid State Chemistry and Synthesis)

1. **Headline:** Build the bipartite anonymous sublattice isomorphism graph across 60,000 experimental crystals to discover synthetically anchored topochemical intercalation hosts.
2. **Steps:**
   1. Extract all experimentally observed inorganic crystals from MP and COD and generate stripped host sublattices by removing mobile ions (Li, Na, K, Mg, Zn, Cu, Ag) (4 hours).
   2. Compute scale invariant anonymous Wyckoff and coordination graph fingerprints to link experimentally synthesized empty crystals to experimentally synthesized stuffed analogues in different chemical families (6 hours).
   3. Filter for redox active empty experimental hosts paired with stuffed structural twins where the guest ion was never tested in that host chemistry (3 hours).
   4. Insert guest ions into the exact twin Wyckoff sites, relax with MACE MP 0 on RTX 4060, and compute voltage, hull distance, and Voronoi percolation radius (7 hours).
   5. Deliver the interactive sublattice twin graph and top 20 topochemical battery candidates (6 hours).
3. **Data and tools:** Materials Project experimental subset, COD, Pymatgen StructureMatcher, Spglib, MACE MP 0, Marimo.
4. **The hard result:** A bipartite graph linking thousands of experimental stuffed and empty crystal structures across chemical families, plus 20 low strain topochemical cathode candidates where both the empty host crystal and the stuffed Wyckoff geometry are experimentally proven in nature.
5. **Why it is new:** Prior battery screens either remove Li from known Li phases or insert ions into arbitrary voids of hypothetical crystals. Pairing an already synthesized empty crystal with an already synthesized stuffed isostructural twin in another chemistry guarantees both host synthesizability and steric site viability.
6. **Verification:** Hold out known topochemical pairs (such as TiS2/LiTiS2 and V2O5/LiV2O5) to prove the graph recovers them blind, and verify volume changes under 8 percent and zero host bond breaking during MACE relaxation.
7. **Risk:** Space group setting differences or slight monoclinic distortions can hide sublattice matches unless loose fractional coordinate tolerances are used.
8. **1st place odds:** 22%

### Idea 5: AlchemGrad (Scientific Software and MLIP Physics)

1. **Headline:** Turn discrete universal ML potentials into continuous differentiable alchemical engines over the site occupancy simplex to solve disordered crystals and spinel cation inversion in seconds.
2. **Steps:**
   1. Wrap the `mace-torch` atomic number embedding layer to accept continuous probability simplex vectors across 89 elements with analytical autograd gradients and Hessians (5 hours).
   2. Calibrate the on site quadratic alchemical self energy correction against explicit ordered supercells across 30 binary solid solutions (4 hours).
   3. Implement Riemannian projected gradient descent with configurational entropy annealing to relax joint atomic positions and continuous site occupancies directly from partial occupancy CIFs (6 hours).
   4. Predict the degree of cation inversion and inversion temperature across 120 experimental $AB_2\text{O}_4$ spinels (5 hours).
   5. Benchmark against experimental single crystal XRD site occupancy refinements in COD and wrap into a pip installable tool (6 hours).
3. **Data and tools:** Pretrained MACE MP 0 (`mace-torch`), PyTorch autograd, COD disordered spinel subset, Pymatgen, Marimo.
4. **The hard result:** An open source PyTorch wrapper (`alchem-mace`) that lets universal MLIPs ingest fractional occupancy CIFs directly and compute 89 element dopant chemical potential maps in one backward pass, validated by predicting cation inversion parameters across 120 experimental spinels ($2\text{ seconds}$ per crystal versus hours of supercell Monte Carlo).
5. **Why it is new:** Over half of experimental CIFs have partial site occupancies and crash every universal MLIP. While continuous species embeddings appear in generative models like FlowMM, extracting calibrated analytical alchemical gradients and entropy annealed site occupancies from pretrained MACE MP 0 to solve experimental disorder has not been done.
6. **Verification:** Compare continuous simplex predictions directly against brute force supercell enumerations on 20 small spinels and against experimental site occupancies from single crystal diffraction.
7. **Risk:** Large ionic radius mismatches between co occupying cations create local bond length splitting that a single average coordinate underestimates without split site displacements.
8. **1st place odds:** 24%

### Idea 6: WignerLaw (Physics and Symbolic Mathematics)

1. **Headline:** Symbolic discovery of a dimensionally exact analytical equation for wave tunneling thermal conductivity in complex and rattling crystals.
2. **Steps:**
   1. Assemble the 1,400 crystals with full first principles anharmonic lattice thermal conductivity tensors and matching harmonic force constants from Alexandria, Matbench, and PhononDB (3 hours).
   2. Compute exact harmonic spectral invariants for each crystal: acoustic Debye velocity, mean interband optical frequency spacing, participation ratio of low frequency modes, and off diagonal velocity coupling norm (5 hours).
   3. Run PySR with strict Buckingham Pi dimensional homogeneity constraints to discover an additive analytical correction to the 1973 Slack equation that captures Wigner interband wave tunneling (6 hours).
   4. Apply the discovered formula to all 10,034 crystals in PhononDB in 30 seconds to identify crystalline materials with glass like temperature independent heat transport (5 hours).
   5. Validate against experimental ultralow thermal conductivity crystals and build the Marimo explorer (7 hours).
3. **Data and tools:** PhononDB, Alexandria/Matbench `matbench_log_kvrh` and Phono3py datasets, Phonopy, PySR, SymPy, Marimo.
4. **The hard result:** A closed form, dimensionally homogeneous two term analytical equation ($\kappa_L = \kappa_{\text{particle}} + \kappa_{\text{wave}}$) that cuts the 50 year old Slack equation error on complex unit cells by over 60 percent, plus a ranked list of 30 harmonic glass like crystals from PhononDB.
5. **Why it is new:** Simoncelli, Marzari, and Mauri (2019) derived the exact Wigner transport equation requiring expensive 3rd order DFT force constants. Discovering a closed form analytical surrogate for the Wigner wave tunneling channel from pure harmonic spectral spacing invariants has not been done.
6. **Verification:** Enforce exact physical limits (vanishing wave contribution as unit cell atom count approaches 1, correct $T^0$ vs $T^{-1}$ scaling) and validate out of sample on experimental complex oxides and halide perovskites.
7. **Risk:** Harmonic interband spacing alone lacks the anharmonic linewidth broadening parameter, requiring a universal Gruneisen proxy estimated from MACE or elastic moduli.
8. **1st place odds:** 20%

### What single idea would make an expert judge say wow, and is it feasible solo in 34 hours?

**HyperbolicScout (Idea 1)** would make an expert materials and physics judge say wow because it turns already public static lattice dynamics tables into a genuine condensed matter physics discovery that experimentalists usually spend months hunting one crystal at a time in *Nature* and *Science*. Reconstructing the full frequency dependent infrared permittivity tensor across 8,000 crystals requires zero new DFT calculations because the exact Cochran Cowley oscillator formula is a pure linear algebra contraction of Born effective charges and zone center phonon eigenvectors already sitting in Kyoto PhononDB and Materials Project. One solo researcher on a laptop CPU can diagonalize all 8,000 zone center dynamical matrices in under 20 minutes using Phonopy, recover every famous benchmark (hBN, alpha MoO3, calcite, and monoclinic beta Ga2O3 shear polaritons) to prove physical exactness, and then overlay the newly discovered hyperbolic Reststrahlen frequency windows directly onto raw experimental FTIR reflectance curves from the open RRUFF mineral database. Showing a 4 minute video where an interactive Marimo app predicts a previously unknown in plane hyperbolic mineral and immediately proves it with an experimental RRUFF infrared reflectance spectrum is 100 percent feasible in 34 hours and directly answers whether a two day discovery is possible.
