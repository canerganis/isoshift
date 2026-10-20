# Universal MLIP accuracy for H-containing phonons

## Benchmarks found
1. Loew et al., "Universal MLIPs are ready for phonons", arXiv:2412.16551 (npj Comput. Mater. 2025). 7 models vs the NIMS MDR phonon database (about 10,000 non-magnetic semiconductors, recomputed with PBE in VASP; 8189 stable, 1769 unstable). MAE of max frequency (K) / entropy (J/K/mol) / free energy (kJ/mol): MatterSim 17/15/5, SevenNet 40/48/19, MACE 61/60/24, CHGNet 89/114/45, M3GNet 98/150/56, ORB 291/421/175, OMat24 780/403/241 (PBEsol reference 33/25/10). M3GNet, CHGNet, MACE, SevenNet soften. ORB and OMat24 (forces predicted directly, not as energy gradients) are worst for phonons, often imaginary modes, though best for volumes. No hydrogen-specific analysis, but max frequencies of light-element compounds reach about 5500 K vs 500-2000 K typical. These are the older ORB (v1/v2) and OMat24 direct-force models. Newer conservative ORB v3 did far better, see next.
2. Han and Cheng (ORNL), "Benchmarking uMLIPs for real-time analysis of INS data", arXiv:2506.01860, Mach. Learn.: Sci. Technol. 6, 030504 (2025). 4869 crystals from MP (up to 12 atoms, 86 elements), DFT phonons on Zenodo 10.5281/zenodo.15298436, code github maplewen4/phonon_uMLIP. 12 models (April 2025 Matbench Discovery top). Phonon frequency MAE: ORB v3 0.50 meV, SevenNet-MF-ompa 0.71, GRACE-2L-OAM 0.90, eSEN-30M-OAM 1.20, MatterSim 5M 1.43, MACE-MPA-0 1.61, eqV2 M 9.8, M3GNet 7.6. Best: ORB v3, SevenNet-MF-ompa, GRACE-2L-OAM. Hydrogen case: ZrH2 libration band near 150 meV reproduced in shape by all, but MatterSim and MACE-MP-0 significantly underestimate frequency, MACE-MP-0 peaks too broad. Systematic softening of high-frequency optical bands in most uMLIPs. Molecular H systems (ZIF-8, polyethylene) need MACE-OFF or ORB v3.
3. Deng et al., "Systematic softening in universal MLIPs", npj Comput. Mater. 2025 (arXiv:2405.07105). M3GNet, CHGNet, MACE-MP-0 under-predict PES curvature, fixable by fine-tuning on very little data. Follow-up: Koker et al., PFT phonon fine-tuning (arXiv:2601.07742).
4. Large foundation model phonon assessment on 2429 OQMD crystals, arXiv:2509.03401 (force accuracy does not predict force-constant quality).

## What is missing
No benchmark isolates H-containing compounds, O-H/N-H/B-H stretches (2000 to 3700 cm-1) or hydrides. SevenNet and OMat-trained MACE not tested on hydrides in anything found. This gap is itself a deliverable (H-phonon benchmark fallback). Loew's max-frequency error is the relevant metric because the H modes set the ZPE.

## Why it matters for IsoShift
ZPE of an X-H mode is about hbar*omega/2, so a 5% softening of a 3300 cm-1 stretch shifts ZPE by about 4 meV per H, comparable to the ice Ih/XI energy difference (about 4.5 meV per molecule). But the isotope shift depends mostly on differences between polymorphs, so uniform softening partly cancels. Test shifts, not absolute T.

## Reference data for H-containing inorganic compounds
- MDR/PhononDB (NIMS, Togo): per-compound entries "Ab-initio phonon calculation for X / spacegroup / materials id N" at mdr.nims.go.jp, finite displacement via phonopy, VASP, MP structures, phonopy files included, older mirror phonondb.mtl.kyoto-u.ac.jp. Contains H-containing compounds (filter by formula). Loew recomputed the set in PBE, so check functional per entry.
- Petretto et al., Sci. Data 5, 180065 (2018), doi:10.1038/sdata.2018.65. DFPT phonons for 1521 semiconductors with dielectric and thermodynamic data. Check H content before use.
- Han and Cheng 4869-crystal DFT phonon set (Zenodo above), MP-derived.
- Materials Project phonon database (LBNL, atomate2 + Pheasy, about 30,000 compounds per a 2026 MRS abstract). Newer, verify availability.
- JARVIS-DFT phonons: not verified in this search, check directly.
- Experimental INS spectra for H systems (ZrH2 etc.) in Han and Cheng supplement.

## Recommendation
Primary: ORB v3 (conservative) and SevenNet-MF-ompa (best MAE in Han and Cheng), MatterSim v1 (best in Loew, but low on ZrH2 libration), MACE-MPA-0 as third baseline, MACE-OMAT-0 optional (MACE foundations page claims good phonons, unconfirmed here). Avoid direct-force models (older ORB, eqV2, OMat24 direct). Use at least two architectures and treat ensemble spread as uncertainty. Check on a small H subset (ice XI/Ih, brucite, LiH, ZrH2, MDR hydrides) before trusting.
