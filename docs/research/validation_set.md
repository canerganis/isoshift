# IsoShift validation set (research notes, 2026-10-21)

Machine-readable version: validation_set.csv (18 rows). Everything below was gathered from web search and fetched pages. The "verification" column in the CSV says what I actually saw. Items marked "memory" or "not found" must NOT be quoted as facts before checking the primary source.

## Honest headline
Clean, quantitative, experimentally known H/D shifts of a polymorph transition that are also harmonic-tractable are rare. Only one is a textbook-grade case: ice Ih/XI, where DFT-QHA already gets the shift (+6 K computed vs +4 K experiment). Most other known H/D transition shifts are order-disorder, tunneling or H-bond geometry problems, which makes them negative controls. Plan the gate around ice XI plus volume/ZPE observables, not around a large set of transition shifts.

## Positive validation (harmonic or QHA tractable)
1. Ice Ih -> XI, H2O vs D2O. Exp 72 K vs 76 K (+4 K). QHA vdW-DF-PBE: 91 K vs 97 K (+6 K, ratio 1.07 vs exp 1.06). PBE gives 202/215 K (absolute T wrong by over 100 K, shift +13 K). Origin: ZPE difference between ordered and disordered ices, not tunneling. Disordered Ih needs large cells plus Pauling entropy N kB ln(3/2). Pamuk, Allen, Fernandez-Serra, PRB 92, 134105 (2015), doi:10.1103/PhysRevB.92.134105, arXiv:1506.02009.
   Caution for MLIPs: functional sensitivity is severe (vdW needed), so an MLIP trained on PBE may overestimate the shift as PBE does. Use as the sign and magnitude gate.
2. Ice Ih volume isotope effect: V(H2O) about 0.1% smaller than V(D2O) at 0 K (anomalous), reproduced by DFT QHA. Pamuk et al., PRL 108, 193003 (2012), arXiv:1111.4870. Ice VIII shows the normal sign at 0 GPa (UMN abstract), so the sign changes with H-bond length. Good sign test for any QHA pipeline.
3. Metal hydrides MHy (115 compounds, y=0.5,1,2, 30 metals): harmonic phonons give the H/D/T difference in formation enthalpy and plateau pressure, matched to experiment, plus an inversion of the isotope effect at higher T. Bourgeois, Crivello, Cenedese, Paul-Boncour, Joubert, J. Phys.: Condens. Matter (2018), HAL hal-02011296. Closest prior art and also the best harmonic validation. Numbers not retrieved (HAL blocked the fetch).
4. Brucite Mg(OH)2 vs Mg(OD)2: V(H) larger by 0.31% at room temperature (mostly c axis). Neutron study to 9 GPa gives K0 = 39.0 +- 2.8 (H) and 40.4 +- 1.3 GPa (D), indistinguishable. Good for volume isotope checks (QHA), weak for transition shifts. High-P phase P41212 predicted above about 17 GPa, stable with or without ZPE (Mg(OH)2 only), PNAS 113, 13971 (2016).
5. LiH/LiD B1 -> B2: ZPE dominated (Roma 1996 DFPT, up to 10 GPa), shift visible at 300 K and large above 2000 K, 6LiH vs 7LiT about 15 GPa at 0 K. Chen et al., arXiv:1607.01970 (QHA, phonopy, PBE). No experiment near 300 GPa, so theory-vs-theory only.
6. Ice VII -> VIII: about 273 K near-isotherm from 2 to about 15 GPa (H2O) and 20 GPa (D2O), no isotope effect there. On the falling branch D2O orders at higher pressure, T=0 end about 60 GPa (H2O) vs 80 GPa (D2O). Attributed to ZPE. Ackland et al., arXiv:2504.06244 (mean-field model with DFT/QHA inputs, not a DFT-only reproduction). Semi-tractable, ordering needs a model.
7. ZrH2/ZrD2 cubic-tetragonal: isotope first-principles study exists (arXiv:1305.6109), results not read. Check before use.

## Negative controls (declare in advance)
- KDP/DKDP: Tc 122 K vs 229 K. Geometric isotope effect plus tunneling/order-disorder. Koval et al. cond-mat/0206029; Torresi et al. JCP 2025 (quantum paraelectric at high pressure).
- KOH/KOD: 233 K vs 257 K (+24 K). Order-disorder (P21/a to P21/m). PIMD, Fallacara et al., J. Phys. Chem. C 125, 22328 (2021), doi:10.1021/acs.jpcc.1c06953. A PIMD reference exists and the high-T phase is dynamically disordered, so QHA should fail.
- NaOD: low-T transition at 153.2 K absent in NaOH (above 6 K). Tunneling. Extreme case.
- delta-AlOOH/AlOOD: P21nm -> Pnnm at 9.0 GPa (H) vs 13.4 GPa (D), +4.4 GPa; symmetrization 18.1 GPa (H), not reached in D up to 17.4 GPa. Double-well disorder. Sano-Furukawa et al., Sci. Rep. 8, 15520 (2018), doi:10.1038/s41598-018-33598-2. Best stress test: a harmonic model should miss it, and a miss is a result.
- Ice VIII -> X symmetrization: about 60 GPa for H2O (classical above 100), D2O shifted about 10 GPa (from a search snippet, check source arXiv:2403.09238). Quantum anharmonic. Zhang and Wang arXiv:2507.01452 (MACE + neural canonical transformation, H2O only). Gaussian ansatz is 2 GPa off. Also adjacent MACE-based NQE work.
- NH4Cl/ND4Cl: H 242.6 K verified (PRL 1970). ND4Cl about 249 K is from memory, unverified. NH4Br/ND4Br: ND4Br 214.86 K and 166.7 K verified, NH4Br values from memory. Order-disorder.
- LiBH4/LiBD4: LiBH4 381 K (hysteresis about 8 K). No LiBD4 transition temperature found. HT phase has shallow rotational barriers (about 0.2 eV), strongly anharmonic. Do not claim a shift number.
- NaBH4/NaBD4: NaBD4 about 190 K (192.2 K, Na11BD4). NaBH4 value not retrieved. Order-disorder.
- PdH/PdD Tc: inverse isotope effect, anharmonic (SSCHA 5.0/6.5/6.9 K for H/D/T, below experiment). Not a polymorph, only an anharmonicity example.
- (NH4)2MX6 family: deuteration often raises T and entropy, sometimes creates transitions only in D (JPSJ 70 Suppl A, 383).

## Not found / not checked
KBH4/KBD4, VH2/VD2, TiH2 isotope data, LiAlH4/NaAlH4, CaH2, FeOOH, (NH4)2SO4, CsHSO4 family, squaric acid. No numbers found, so no entries. Cs/Rb hydrogen sulfates and (NH4)2SO4 are known isotope-sensitive but I did not source them.
ICSD/MP/COD ids were not looked up (web only). Do that with pymatgen/MP API in the build phase.

## Recommended gate design
Gate A (must pass): ice Ih/XI sign and rough size of the shift, ice volume isotope effect sign, hydride H/D formation-pressure trend (Bourgeois). Gate B (reported honestly): KOH/KOD, KDP and AlOOH should come out wrong or flagged "outside harmonic validity". Cross-check with a DFT QHA baseline on a small subset because the ice result depends strongly on the functional.
