# Prior-art sweep: H to D substitution, O-H...O bond length, and polymorph ranking

Agent: haiku (web). Date of sweep: 2026-10-23.

## Verdict

No source found states the claimed rule: deuteration favours the polymorph with the shorter mean O-H bond, with a coefficient of about 0.12 to 0.15 meV per H per mÅ of O-H length difference, a stretch ZPE term about half cancelled by bend and libration, and failure for weak H-bonds. The coefficient and the sign convention do not appear in any result.

What does exist is a set of individual systems where deuteration shifts a polymorph or phase boundary in the direction the rule would predict (NaOD, glycine, AlOOD), plus a large body of harmonic and quasi-harmonic free-energy work on polymorph re-ranking, and a 2024 precedent for the exact pipeline (universal MLIP plus harmonic phonons over more than 100 polymorph pairs) with no isotope study. The novelty risk is therefore in the statistical rule over about 200 inorganic pairs, not in the qualitative effect.

Limits of this sweep: all statements come from search-result snippets. No full text was opened with WebFetch. Several `site:` filters were ignored by the search index (APS, Wiley, AIP, and Nature returned no matching journal articles). Author lists and years marked "not verified" were not confirmed from the source.

## Results table

Threat levels: high = same rule; medium = same observable or family correlation; low = related or already known.

| # | Title | Authors | Year | Venue | Link | One sentence | Threat |
|---|---|---|---|---|---|---|---|
| 1 | Glycine polymorph stability, deuterated vs protonated beta-glycine | Li et al. (per aggregator; not verified) | 2025 or 2026 | Cryst. Growth Des. | https://doi.org/10.1021/acs.cgd.5c01746 | Abstract-level summary says deuterated beta-glycine is more stable, attributed to stronger H-bonding from deuteration, which may favour gamma-glycine. | high (provisional; abstract only, direction matches the claim, molecular not inorganic) |
| 2 | Symmetrization of hydrogen bond in delta-AlOOH under mantle conditions (neutron diffraction) and AlOOD pressure shift | not verified | not verified (likely 2018) | PMC / neutron study | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6195538/ | Deuteration raises the P2_1nm to Pnnm transition pressure (about 9 vs about 12 GPa in reported sets) and the O-H length versus O...O relation is discussed explicitly. | medium (inorganic O-H...O phase boundary with isotope shift; the closest inorganic family hit) |
| 3 | When Quantum Fluctuations Meet Structural Instabilities: Isotope- and Pressure-Induced Phase Transition in the Quantum Paraelectric NaOH | Schaack et al. (per snippet) | 2023 | Phys. Rev. Lett.; arXiv 2310.16462 | https://arxiv.org/pdf/2310.16462 | ZPE fluctuations weaken H-bonds in NaOH, NaOD shows a first-order transition with restored (stronger) bonds, and strengthening bonds by isotope or pressure drives antiferroelectric order. | medium (closest inorganic hydroxide; isotope selects a phase; path-integral, not harmonic; notes weak bonds restored in NaOD, check against the "fails for weak H-bonds" clause) |
| 4 | Dissertation on NaOD vs NaOH (low-temperature transition at 153 K) | Bessonette (listed as contributor on DalSpace; not verified as author of record) | 1998 (per snippet) | Dalhousie University thesis | https://dalspace.library.dal.ca/handle/10222/55582 | Deuterated alkali hydroxides can form shorter, stronger H-bonds because of shorter O...O distances, which gives a transition in NaOD absent in NaOH. | medium (same direction statement for an inorganic hydroxide, old, thesis only) |
| 5 | Accelerating High-Throughput Phonon Calculations via Machine Learning Universal Potentials | not verified | 2024 | arXiv 2407.09674 | https://arxiv.org/pdf/2407.09674 | Universal MLIP harmonic phonons give Helmholtz free energies for 126 polymorphs across 49 polymorph types at 300 and 1000 K, compared against DFT. | medium (same method pipeline as the claim, no isotope substitution) |
| 6 | Structural and Vibrational Properties of D3Se from First Principles: Anharmonic Quantum and Isotope Effects | not verified | 2026 | arXiv 2607.18095 | https://arxiv.org/pdf/2607.18095 | Harmonic phonons give isotope-independent stability limits, while SSCHA anharmonic corrections make them mass dependent (critical pressure about 110 GPa harmonic vs about 65 GPa anharmonic). | medium (method caveat: harmonic ZPE arguments may not hold; directly relevant to a reviewer objection) |
| 7 | Vibration analysis of hydrogen, deuterium and tritium in metals: consequences on the isotope effect | not verified | 2018 | J. Phys.: Condens. Matter (HAL hal-02011296) | https://hal.archives-ouvertes.fr/hal-02011296 | Harmonic phonon vibrational contributions drive formation-pressure differences between hydride, deuteride and tritide, and the isotope effect can invert with temperature. | medium (same mechanism, harmonic phonons, metal hydrides not polymorph pairs) |
| 8 | Origins of isotopomeric polymorphism | not verified (ORNL record) | not verified | ORNL impact record | https://impact.ornl.gov/en/publications/origins-of-isotopomeric-polymorphism/ | Low-barrier H-bonds have near-zero proton/deuteron ZPE difference, while normal H-bonds have about 500 cm-1, which explains reversed polymorph stability on substitution. | medium (same ZPE mechanism, organic 4-MPPCP family, already on the known list) |
| 9 | Isotopomeric polymorphism in a doubly-polymorphic multi-component molecular crystal | not verified | 2015 | CrystEngComm | https://pubs.rsc.org/en/content/articlepdf/2015/ce/c5ce00123d | Deuteration selects a different polymorph, and deuterated forms lack the short strong acid-base H-bonds of the hydrogenous forms. | medium (same observable family, molecular) |
| 10 | Geometric isotope effect of deuteration in a hydrogen-bonded host-guest crystal | Shi et al. (per snippet) | 2018 | Nature Communications (DOI 10.1038/s41467-018-02931-8) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5797174/ | Deuteration lengthens the O-H...O donor-acceptor distance and creates a new phase, an isotopic polymorph. | medium (same observable, opposite sign of bond-length change, useful as a counter-direction example) |
| 11 | Static and lattice vibrational energy differences between polymorphs | Nyman, Day (per snippet) | 2015 | CrystEngComm | https://pubs.rsc.org/en/content/articlehtml/2015/ce/c5ce00045a | Vibrational free energy differences (rarely above 2 kJ/mol) re-rank 9% of 508 organic polymorphic pairs near or below room temperature. | medium (same ranking-by-vibrations method family, no isotopes) |
| 12 | Modelling temperature-dependent properties of polymorphic organic molecular crystals | Nyman, Day (per snippet) | 2016 | PCCP | https://pubs.rsc.org/en/content/articlehtml/2016/cp/c6cp05447a | Lattice vibrational Gibbs energies for 475 polymorph pairs imply an enantiotropic transition in 21% of systems. | medium (method precedent at scale, no isotopes) |
| 13 | Systematic assessment of universal MLIPs / phonon benchmarks (2024 to 2025) | not verified | 2024 to 2025 | Materials Genome Engineering; arXiv | https://journal.hep.com.cn/mgea/EN/10.1002/mgea.58 | Benchmarks of graph-network universal potentials on phonons and formation energies; relevant to choosing the potential for the claim's pairs. | low (methods only) |
| 14 | Extending Badger's rule: relationship between energy and structure of hydrogen bonds | not verified | 2025 | J. Chem. Phys. (PNNL record) | https://www.pnnl.gov/publications/extending-badgers-rule-i-relationship-between-energy-and-structure-hydrogen-bonds | Analytic link between H-bond strength and donor bond elongation, fitted to dimer ab initio data. | medium (mechanistic link between O-H length and bond strength, no isotope or polymorph test) |
| 15 | Libowitzky correlation of O-H stretch frequency and O...O distance in minerals | Libowitzky (per snippet; full citation not verified) | 1999 | not verified (likely Monatsh. Chem.) | not retrieved | Empirical exponential fit (R^2 about 0.96) from 125 O...O and frequency pairs, O...O from about 2.44 to 3.5 Å. | medium (the O-H and O...O bounds in the claim come from this family; no isotope polymorph test) |
| 16 | Hexamethylenetetramine: reverse Ubbelohde effect | not verified | not verified | Univ. Tor Vergata record | https://art.torvergata.it/handle/2108/350668 | Deuteration shortens the H-bond in HMT, which harmonic lattice models could not explain. | medium (counter-direction case for the claim's sign, relevant to exceptions) |
| 17 | Hydrogen-bonded fluoride crystals HF and DF, quantum fluctuations and heavy-atom distance | Dammak et al. (per snippet) | 2019 | Phys. Chem. Chem. Phys. (DOI 10.1039/C8CP06949B) | https://doi.org/10.1039/C8CP06949B | Quantum fluctuations shrink the heavy-atom distance in weak H-bond fluorides and deuteration reverses that trend. | low (weak-bond case, relevant to the claim's exception clause, not a polymorph ranking) |
| 18 | Deuterated KH2PO4 type crystals: Ubbelohde-type transition shift | not verified | 1990 (Nature 348:317) | Nature | https://www.nature.com/articles/348317a0 | Full deuteration can raise the KDP-type transition temperature by more than 100 K, with most of the change from H-bond dimensions. | low (known family, Ubbelohde) |
| 19 | Pentachlorophenol cocrystal isotopic polymorphism | not verified | 2021 | CrystEngComm | https://pubs.rsc.org/ar/content/articlelanding/2021/ce/d0ce01636e | Deuteration produces a different crystal form from the hydrogenated cocrystal. | low (known family) |
| 20 | Aspirin entropy-driven polymorph stability with neural network potential | not verified | 2024 | arXiv 2404.11587 | https://arxiv.org/pdf/2404.11587 | Neural network potential used for polymorph energy ordering with entropy terms. | low (method precedent only) |

Known items on the user's list that the sweep also re-surfaced (not re-scored): McKenzie et al., J. Chem. Phys. 140, 174508 (2014); ROY d1 polymorph selection (IUCrJ 2018, https://journals.iucr.org/m/issues/2018/05/00/ed5015/); 4-MPPCP ZPE explanation; Ubbelohde effect; Pamuk ice (PRL 2012); water and ice Ih exception (https://www.ims.ac.jp/en/news/2019/12/02_4483.html).

## Queries run (28 WebSearch calls, mode standard)

Each query returned about 8 to 10 result links. None returned a page stating the claimed rule.

Plain queries (1 to 10):
1. deuteration polymorph stability hydrogen bond length isotope effect. Hits: about 9. Closest: Nat. Commun. 2018 host-guest, 4-MPPCP.
2. isotope effect polymorph zero-point energy hydroxide DFT phonon. Hits: about 9. Closest: PRL 2023 NaOH, ice QHA.
3. deuterium stabilizes shorter hydrogen bond phase. Hits: about 10. Closest: NaOD thesis (1998), alanine 2007.
4. isotopic polymorphism inorganic crystal H/D substitution relative stability. Hits: about 9. Closest: DClO4 2D2O abstract, barbituric acid (abstract only).
5. isotope-induced phase transition hydrogen bond. Hits: about 10. Closest: KDP, K3H(SO4)2, PRL 2023.
6. H/D isotope effect relative stability polymorphs DFT phonon free energy. Hits: about 10. Closest: D3Se SSCHA, metal hydride phonons.
7. deuterated polymorph nuclear quantum effects crystal energy landscape. Hits: about 9. Closest: LaH10 NQE landscape (not isotope pairs), paracetamol.
8. deuteration phase transition pressure hydroxide shift. Hits: about 9. Closest: NaOD calorimetry, LiOH high-pressure.
9. ice phases isotope effect stability rule hydrogen bond. Hits: about 10. Closest: ice VIII/X volume isotope effect.
10. hydrogen bond symmetrization isotope pressure shift correlation O...O distance. Hits: about 9. Closest: delta-AlOOH/AlOOD.

Site-filtered queries (11 to 17):
11. site:pubs.acs.org deuteration polymorph hydrogen bond. Hits: about 9, including ACS CGD 2025 (glycine) via aggregator.
12. site:pubs.rsc.org isotope effect polymorph stability zero-point. Hits: about 9, mostly RSC CrystEngComm 2015 and ORNL.
13. site:journals.aps.org isotope effect hydrogen bond polymorph zero-point. Hits: about 9, zero APS journal pages returned.
14. site:onlinelibrary.wiley.com deuteration polymorph stability hydrogen bond. Hits: about 9, zero Wiley pages; filter not applied.
15. site:nature.com deuterium polymorph hydrogen bond isotope stability. Hits: about 9, one unrelated Nature Index page.
16. site:journals.iucr.org isotope effect hydrogen bond length deuterated polymorph. Hits: about 9, one IUCrJ ROY page.
17. site:pubs.aip.org deuterium isotope polymorph stability zero-point phonon. Hits: about 9, zero AIP pages.

Method and mechanism queries (18 to 28):
18. universal machine learning potential polymorph energy ordering H D isotope phonon free energy. Hits: about 9. Closest: arXiv 2407.09674.
19. isotope effect on relative stability of polymorphs quasi-harmonic free energy hydrogen bonded inorganic solids. Hits: about 8. Closest: ice QHA volume framework.
20. deuteration changes polymorph preference shorter O-H bond zero-point stretch bend libration. Hits: about 10. No stretch-bend-libration split found.
21. Ubbelohde effect hydrogen bond length deuteration rule weak hydrogen bonds fail. Hits: about 10. Closest: HMT reverse Ubbelohde, HF/DF fluorides.
22. high-throughput phonon free energy polymorph pairs isotope substitution hydrogen machine learning. Hits: about 9. No isotope study found.
23. Libowitzky O-H stretching frequency O...O distance correlation deuterium isotope shift. Hits: about 9 plus 9 from a second result set. Closest: Libowitzky fit, Rao 1975 isotope ratio, diabatic O...O shift up to 0.04 Å (source not identified).
24. Nyman Day vibrational free energy polymorph ranking re-ranking hydrogen deuterium. Hits: about 10. No isotope content.
25. 2025 arXiv deuteration hydrogen bond strength polymorph energy ordering universal interatomic potential isotope. Hits: about 9. The specific 2025 preprint was not found.
26. McKenzie isotope effect polymorph stability hydrogen bond zero-point energy 2014 2015 Crystal Growth Design. Hits: about 10. The McKenzie CGD paper was not found; J. Chem. Phys. 2014 model found instead.
27. deuterated versus hydrogenated crystal polymorph transition temperature hydrogen bond shorter stronger rule mineral hydroxide. Hits: about 9. Closest: NaOD thesis, KDP Nature 1990.
28. isotope substitution changes relative free energy of polymorphs phonon calculation hydrogen bond O-H length mass dependence. Hits: about 9. Closest: path-integral isotope free energy method, ORNL record.

## Points that need checking before any novelty claim

1. The NaOD PRL 2023 (row 3) says deuteration restores weak H-bonds. The claim says the rule fails for weak H-bonds. These may conflict in direction. Check the full text.
2. The glycine result (row 1) is an abstract summary. The detailed O-H lengths are not confirmed.
3. Harmonic ZPE arguments are challenged by the D3Se anharmonic result (row 6). The claim's stretch versus bend and libration split is harmonic-looking. A reviewer will ask for anharmonic or PIMD checks.
4. The HMT reverse Ubbelohde case (row 16) shows deuteration can shorten H-bonds, so the sign convention for "shorter O-H" needs to be stated carefully.
5. The method precedent in row 5 (126 polymorphs, 49 types, MLIP plus harmonic phonons) is close to the claim's pipeline. The isotope observable is the new part.

## Top 5 threats

1. Glycine beta-d versus beta (ACS CGD 2025/2026): deuteration stabilizes the polymorph with stronger H-bonds, same direction, abstract only.
2. delta-AlOOH/AlOOD (neutron, PMC6195538): deuteration shifts an inorganic O-H...O phase boundary, the closest inorganic family hit.
3. NaOH/NaOD PRL 2023 (arXiv 2310.16462) with the 1998 NaOD thesis: isotope-selected phase in a hydroxide, with shorter O...O in deuterated alkali hydroxides.
4. Universal MLIP harmonic phonon polymorph free energies, 126 pairs (arXiv 2407.09674): same pipeline, no isotope study.
5. D3Se SSCHA (arXiv 2607.18095): harmonic stability limits are isotope independent and anharmonic corrections change the mass dependence, a direct objection to a harmonic ZPE rule.
