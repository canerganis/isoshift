# Prior-art sweep: arXiv, Semantic Scholar, Valency

Claim tested: under full H to D substitution in solids with moderate to strong O-H...O bonds (mean O-H >= 0.99 Å, O...O <= ~2.9 Å), deuteration favours the polymorph with the shorter O-H bonds. Harmonic ddF changes by ~0.12 to 0.15 meV per H per mÅ of O-H length difference. Computed over ~200 inorganic polymorph pairs with MACE, ORB, MatterSim and harmonic phonons.

Bottom line: no paper found states this rule, computes H vs D polymorph free-energy differences over a set of polymorph pairs with universal MLIPs, or gives a bond-length-difference coefficient. The qualitative picture (deuteration lengthens O-H...O bonds and shifts phase boundaries or selects polymorphs) is well established in the literature, going back to 1988 and the "geometric isotope effect" work. The novelty risk is in the qualitative direction, not the quantitative rule.

## Candidate table

Threat levels: high = same rule; medium = same observable or general correlation for a family; low = related. "Abs read" marks entries where the abstract was read, not just the title or a search snippet.

| # | Title | Authors | Year | Venue | Link | What it shows | Threat |
|---|---|---|---|---|---|---|---|
| 1 | Origins of isotopomeric polymorphism / Isotopomeric polymorphism | Zhou, Kye, Kolesnikov, Harbison | 2004, 2006 | Isotopes Env Health Stud / pubmed | https://pubmed.ncbi.nlm.nih.gov/15237992/ , https://pubmed.ncbi.nlm.nih.gov/16870562/ | Deuteration alone can select a different polymorph. Known family from the brief. | medium (known) |
| 2 | Isotopomeric polymorphism in a "doubly-polymorphic" multi-component molecular crystal | Schmidtmann, Middlemiss, Wilson | 2015 | CrystEngComm 17 | https://pubs.rsc.org/en/content/getauthorversionpdf/c5ce00123d | Deuterated isonicotinamide-oxalic acid forms polymorphs distinct from the hydrogenous ones. Same observable (H to D picks the polymorph) in an O-H...O system, no energetics. Not in brief. | medium |
| 3 | NMR studies of solid pentachlorophenol-4-methylpyridine complexes exhibiting strong OHN hydrogen bonds | not fetched | 2012 | J Phys Chem A | https://doi.org/10.1021/jp305863n | Deuteration of the phenol gives a monoclinic form with a weaker H-bond. Also reported in a 2021 CrystEngComm paper "Suppression of isotopic polymorphism" (pressure used to undo the isotope-driven form). Bond lengths per polymorph were not checked, so this cannot yet be used as a test case for the claim's O-H length rule. | medium |
| 4 | Geometric isotope effect of deuteration in a hydrogen-bonded host-guest crystal | Shi, Zhang, Yu, Yao, Zhang | 2018 | Nature Communications 9 | https://doi.org/10.1038/s41467-018-02931-8 | Deuteration lengthens O-H...O bonds in an imidazolium hydrogen terephthalate and creates a new phase with a lower dielectric transition temperature. Same H/D length direction and a phase boundary shift in an O-H...O crystal. Abstract read via S2 snippet only. | medium (closest qualitative match) |
| 5 | Geometric H/D isotope effect in a series of organic salts involving short O-H...O hydrogen bonds | not fetched | 2019 | CrystEngComm | https://doi.org/10.1039/C9CE00734B | Deuteration noticeably lengthens donor-acceptor distances in short carboxyl and carboxylate O-H...O bonds. Matches the brief's "short O-H...O" regime for the geometry sign. No energetics. | medium |
| 6 | Geometric Isotope Effect and Structural Phase Transition | not listed | 1998 | J Chem Soc Jpn (review) | https://doi.org/10.5940/JCRSJ.40.10 | Review of how deuteration alters H-bond geometry and phase diagrams. Qualitative prior for "deuteration moves phase boundaries via H-bond geometry". | medium |
| 7 | Geometric isotope effect in hydrogen-bonded crystals | not listed | 1990 | Phys Rev B 42 | https://doi.org/10.1103/PHYSREVB.42.10488 | Early theory of deuteration changing H-bond geometry in crystals. | low to medium |
| 8 | The isotope-effect in the phase transition of KDP: new insights from ab initio path-integral simulations | Srinivasan, Car, Sebastiani | 2010 | arXiv:1002.1457 | https://arxiv.org/abs/1002.1457 | PIMD shows deuteration shifts the KDP ferroelectric transition in an O-H...O crystal. Same observable family (H/D shifts a structural transition), no polymorph pairs. | medium |
| 9 | Anharmonic and Quantum Fluctuations in Molecular Crystals: A First-Principles Study of the Stability of Paracetamol | Rossi, Gasparotto, Ceriotti | 2016 | PRL 117, 115702 | https://arxiv.org/abs/1609.04469 | Free-energy calculations show anharmonic, vdW and nuclear quantum effects each shift which paracetamol polymorph is stable. Same observable (NQE reorders polymorphs), no H/D rule. 94 citing papers in Valency, including 2026 paracetamol polymorph follow-ups. | medium |
| 10 | The role of nuclear quantum effects in the relative stability of hexagonal and cubic ice | Buxton, Quigley, Habershon | 2019 | J Chem Phys | https://doi.org/10.1063/1.5123992 | NQE changes the relative stability of two ice polymorphs. Same observable for H2O, no isotope-substitution rule. | medium |
| 11 | Accelerating High-Throughput Phonon Calculations via Machine Learning Universal Potentials | Lee, Hegde, Wolverton, Xia | 2024 | arXiv:2407.09674 | https://arxiv.org/abs/2407.09674 | Universal MLIP (MACE) phonon free energies for polymorph differences, compared with DFT. Method overlap with the brief (universal MLIP, harmonic free energies, polymorph pairs). No isotopes. Abstract read via S2 snippet only. | medium (method) |
| 12 | Isotope Effects at Classical Cost through Mass-Differentiable Machine Learning (iso-EPIGS) | Du, He, Shen, Ye, Zeng, Zhang, Kapil, Fang | 2026 (Oct) | arXiv:2610.11325 | https://arxiv.org/abs/2610.11325 | Mass-differentiable NN reproduces path-integral H vs D free-energy differences for water and oxalic acid crystal at classical cost. Abs read. Newest and closest in method. Does not compare polymorph pairs. | medium (watch) |
| 13 | Importance of Nuclear Quantum Effects for Molecular Cocrystals with Short Hydrogen Bonds | Stocek, Socha, Cisarova, Slanina, Dracinsky | 2022 | JACS | https://doi.org/10.1021/jacs.1c10885 | NQE matter for structure in short H-bond cocrystals. Same regime (short H-bonds), no polymorph ranking or H/D rule. Abstract not read. | medium to low |
| 14 | Isotope-induced phase transition, NaOH quantum paraelectric | Schaack, Mangaud, Fallacara, Huppert, Depondt, Finocchi | 2023 | PRL 131, 126101 | https://arxiv.org/abs/2310.16462 | Isotope and pressure drive a structural phase transition via quantum fluctuations. Same observable family (H/D moves a phase boundary). Abstract not read. | medium to low |
| 15 | Vibrational free-energy corrections for molecular crystal polymorphism (DFT benchmark) | Weatherby, Rumson, Price, Otero de la Roza, Johnson | 2022 | J Chem Phys 156 | https://doi.org/10.1063/5.0083082 | Benchmarks vibrational free-energy corrections for polymorph ranking. Harmonic-correction context, no isotope. Abstract not read. | low to medium |
| 16 | Day and Nyman, vibrational energy and polymorph ranking across 1061 structures | Day, Nyman | 2015 | CrystEngComm | not fetched | Per a secondary summary: vibrational energy differences are usually below 2 kJ/mol, but re-rank polymorphs near room temperature in about 9% of pairs. Not verified against the primary paper. Relevant to "ZPE changes ranking" in general. | medium (unverified) |
| 17 | A complete description of thermodynamic stabilities of molecular crystals | Kapil, Engel | 2021 | arXiv:2102.13598 | https://arxiv.org/abs/2102.13598 | ML-potential polymorph free energies with FEP correction to ab initio Gibbs energies. Method neighbour. No isotopes. | low to medium |
| 18 | Importance of Nuclear Quantum Effects for NMR Crystallography | Engel, Kapil, Ceriotti | 2021 | JPCL | https://arxiv.org/abs/2106.14171 | NQE shifts NMR predictions for polymorphs. Not an energetics rule. | low |
| 19 | Quantum Anharmonic Effects in Hydrogen-Bond Symmetrization of High-Pressure Ice | Zhang, Wang | 2025 | arXiv:2507.01452 | https://arxiv.org/abs/2507.01452 | Known from brief. Not re-checked. | known |
| 20 | Quantum effects in the H-bond symmetrization and thermodynamic properties of high pressure ice | Cherubini, Monacelli, Yang, Car, Casula, Mauri | 2024 | arXiv:2403.09238 | https://arxiv.org/abs/2403.09238 | NQE on H-bond symmetrization and thermodynamics in ice. Pressure context, not H/D polymorph ranking. | low |
| 21 | Nuclear quantum and H/D isotope effects on hydrogen-bond symmetrization in lithium hydroxide crystals at high pressure | Tanaka, Kuwahata, Tachikawa, Udagawa | 2025 | J Chem Phys | https://doi.org/10.1063/5.0276067 | H/D effects on H-bond symmetrization under pressure. Same isotope-H-bond family, single phase. | low |
| 22 | Hydrogen Bonds Induce Double-Well Spectroscopic Signatures in alpha-Glycine | Pinsk et al. | 2025 | JACS | https://doi.org/10.1021/jacs.5c13223 | Double-well H-bond signatures in a glycine polymorph. Related to the short H-bond regime. | low |
| 23 | Isotope Effect on the Hydrogen Ordering from Ice V to Ice XIII | Yamashita, Loerting | 2026 | JPCB | https://doi.org/10.1021/acs.jpcb.6c01462 | H/D changes ordering pathway in an ice polymorph transition. Not a ranking rule. | low |
| 24 | Ab initio Phase Diagram of Ta2O5 | Gong, Tang, Yang, Kawazoe | 2026 | PRB; arXiv:2602.03649 | https://arxiv.org/abs/2602.03649 | Zero-point energy shifts oxide polymorph phase boundaries. No isotopes. | low |
| 25 | Harmonic-to-anharmonic thermodynamic integration made simple using REG TI | Kapil | 2026 | arXiv:2602.12240 | Valency id 2602.12240v1 | Free-energy method, not isotope-specific. | low |
| 26 | Path-integral molecular dynamics with actively-trained and universal machine learning force fields | Solovykh, Rybin, Novikov, Shapeev | 2025 | arXiv:2505.14245 | https://arxiv.org/abs/2505.14245 | PIMD with universal MLFFs. Method neighbour. | low |
| 27 | Inverse Ubbelohde effect in the short hydrogen bond of photosystem II | not listed | 2016 | J Comput Chem | https://doi.org/10.1002/jcc.24438 | Isotope effect on the symmetry of a short H-bond potential, computational. Not solid polymorphs. | low |
| 28 | Geometrical Isotope Effects on Chemical Bonding in Hydrogen Bonded Systems | not listed | 2025 | J Comput Chem | https://doi.org/10.1002/jcc.70226 | NEO-DFT: H to D to T shortens bonds in charge-inverted and dihydrogen bonds. Molecular, not solid. | low |
| 29 | Hydrogen bond symmetrisation in D2O ice observed by neutron diffraction | not listed | 2024 | Nat Commun | https://doi.org/10.1038/s41467-024-48932-8 | D2O ice symmetrization at high pressure. Experimental, single phase. | low |
| 30 | Effect of quantum nuclear motion on hydrogen bonding (McKenzie et al.) | McKenzie, Bekker, Athokpam, Ramesh | 2014 | J Chem Phys; arXiv:1401.3792 | https://arxiv.org/abs/1401.3792 | Known from brief. Valency forward citations of the related arXiv:1504.04939 (McKenzie 2015) list 5 papers, none solid polymorph. | known |
| 31 | Quantum nature of the hydrogen bond (Li, Walker, Michaelides) | Li, Walker, Michaelides | 2011 | PNAS 108 | DOI 10.1073/pnas.1102038108 | Known from brief. Not in Valency. Abstract not retrieved. The brief says a rule of thumb ties NQE magnitude to classical H-bond length or strength (per an APS abstract summary), which overlaps the claim's regime. Forward citations unavailable (no OpenAlex mapping, S2 endpoint returned 404). | known |
| 32 | Direct assessment of quantum nuclear effects on hydrogen bond strength by constrained-centroid ab initio PIMD | Walker, Michaelides | 2011 | J Chem Phys | https://doi.org/10.1063/1.3505038 | NQE on H-bond strength, not polymorphs. Li-Walker-Michaelides family. | low |

Entries 1, 3, 4 and 8 are from earlier-known or search snippets. Entries 11 and 12 are the methodological neighbours to watch. Nothing in the table uses the claim's exact observable (polymorph pairs, H minus D free-energy difference, bond-length difference coefficient).

## Queries run and hit counts

Valency (semantic_search_papers, search_by_abstract, search_by_abstract_batch, get_citing_papers, get_paper_by_id, search_by_author). Counts are the number of papers returned.

1. semantic: "H/D isotope substitution changes relative stability of polymorphs in molecular crystals through nuclear quantum effects": 15
2. batch (6 keywords: isotope effect polymorph; deuteration polymorph stability; zero-point energy polymorph; isotopic polymorphism; deuterated crystal phase stability; NQE polymorph energy ranking): 40 (truncated; mostly unrelated keyword noise)
3. abstract: "machine learning interatomic potential phonons zero-point energy isotope hydrogen bond crystal": 15 (semantic fallback, no strong matches)
4. abstract: "Li Walker Michaelides NQE hydrogen bond polymorph": 15 (semantic fallback)
5. get_citing_papers: 10.1073/pnas.1102038108 (Li-Walker-Michaelides 2011): 0 (no OpenAlex mapping)
6. get_citing_papers: 10.1063/1.4921286 (McKenzie 2015 DOI): 0 (no OpenAlex mapping)
7. get_citing_papers: arXiv 1504.04939 (McKenzie 2015 preprint): 5
8. get_citing_papers: arXiv 1609.04469 (Rossi 2016 paracetamol): 94
9. abstract, author Michaelides + "polymorph": 15 (noise)
10. batch (5 keywords: deuterium polymorph relative stability; H-bond length isotope free energy crystal; quantum nuclear effects lattice energy polymorph; phonon free energy H/D substitution molecular crystal; path integral polymorph ranking H-bond), from 2015: 1
11. semantic: universal MLIP (MACE, ORB, MatterSim) phonon free energy polymorph stability: 20
12. batch (5 keywords: H-bond symmetrization isotope pressure; isotope effect phase transition H-bonded crystal; ferroelectric deuteration Curie T shift; ZPE polymorph ranking; vibrational free energy polymorph ranking), from 2010: 21
13. batch (5 keywords: deuterated polymorph; isotope substitution polymorphism free energy; H/D isotope effect polymorph; H-D substitution crystal stability; NQE polymorph), from 2019: 30 (truncated, mostly noise)
14. semantic: "quantum nature of the hydrogen bond PIMD ...": 15
15. get_paper_by_id: 2610.11325: 1 (found, abstract read)

Web (WebFetch to arXiv API and Semantic Scholar, WebSearch).

16. arXiv: all:"isotope effect" AND all:polymorph: 2
17. S2: "deuteration polymorph stability hydrogen bond": 3611 total, 30 returned
18. arXiv: all:"nuclear quantum effects" AND all:polymorph: 5
19. S2: "zero-point energy polymorph deuterium machine learning potential": HTTP 429 (rate limit), not retried successfully
20. arXiv: all:"universal machine learning potential" AND all:"isotope": 0
21. S2: "geometric isotope effect hydrogen bond deuteration": 3611 total, 30 returned (same index as query 17 result)
22. S2: "isotopic polymorphism deuterated crystal": HTTP 429
23. arXiv: all:"geometric isotope effect", newest first: 4
24. arXiv: deuteration or H/D substitution AND hydrogen bond AND (phonon or polymorph): 2
25. S2 citations of DOI 10.1073/pnas.1102038108: HTTP 404
26. WebSearch: deuteration changes polymorph stability H-bond ZPE: summary only, no direct rule found. Gave Day and Nyman 2015 and Kapil-Engel 2021.
27. WebSearch: arXiv isotope substitution crystal polymorph free energy MLIP phonons: Kapil-Engel, 2407.09674, MolCryst-MLIPs. No isotope-polymorph work.
28. WebSearch: Li, Walker, Michaelides 2011 PNAS: found the paper title only ("Quantum nature of the hydrogen bond"), no full text.
29. WebSearch: McKenzie 2015 DOI 10.1063/1.4921286: not found. Related isotopomeric polymorphism papers returned.
30. WebSearch: high-throughput isotope effect deuteration universal MLIP phonon free energy 2026 (extended mode): returned a public GitHub repo, see below.
31. WebSearch: 2011 PNAS and "proton ordering": returned solid hydrogen (Li et al. 2013 J Phys Condens Matter, arXiv:1302.0062), a different paper.

Totals: about 30 distinct queries across Valency, arXiv API and Semantic Scholar, with web search as a supplement. Semantic Scholar was rate-limited (429) on 3 of 6 requests, and the DOI citations endpoint returned 404, so forward citations of the 2011 and 2015 McKenzie and Li papers were not obtained from S2.

## Coverage gaps

1. Forward citations of Li-Walker-Michaelides 2011 PNAS and of McKenzie 2015 (DOI 10.1063/1.4921286) are not available: Valency has no OpenAlex mapping for either DOI, and S2 rate-limited or returned 404. The Valency result for arXiv 1504.04939 returned only 5 citers. Retry S2 later with an API key or with a title query.
2. Abstracts for entries 5, 6, 7, 13, 14, 15, 16 and 17 were not read. Their rows rely on titles or search snippets. Read before citing.
3. Day and Nyman 2015 numbers (9 percent of pairs re-ranked, 1061 structures) come from a secondary summary and need checking against the primary paper.
4. The paracetamol NQE work (entry 9) and the Lee et al. phonon work (entry 11) are the main method neighbours. A targeted check for "isotope" within their full text would settle whether either tests H vs D.

## Note on a result from the sweep

A WebSearch returned https://github.com/canerganis/isoshift, described as IsoShift: H/D isotope shifts of polymorph free energies with universal MLIPs (OSI Hackathon 2026). This is the project's own repository, so it is not prior art. It is public, though, which matters for any priority-date argument. The search snippet gives 220 polymorph pairs, 185 of 212 rule evaluations holding, and a diaspore to delta-AlOOH shift of +1.13 to +1.33 GPa. The claim text says about 200 pairs. The repo was not opened, so the snippet numbers are unverified and may differ from the claim.

## Top 5 threats

1. Isotopomeric polymorphism in H-bonded organic crystals (Schmidtmann 2015 CrystEngComm; Zhou, Kye, Harbison; pentachlorophenol-4-methylpyridine): deuteration selects a different polymorph in O-H...N and O-H...O systems. Same observable as the claim, no rule.
2. Geometric isotope effect in O-H...O crystals (Shi et al. 2018 Nat Commun; short-bond organic salts 2019 CrystEngComm; 1998 review): deuteration lengthens O-H...O bonds and shifts phase transition temperatures. Matches the claim's bond-length direction qualitatively.
3. Rossi et al. 2016 PRL (arXiv 1609.04469): nuclear quantum and anharmonic effects change which paracetamol polymorph is stable. Same class of result (NQE reorders polymorphs), 94 citers.
4. Lee et al. 2024 (arXiv 2407.09674): universal MLIP (MACE) harmonic phonon free energies for polymorph pairs. Same method, no isotope.
5. Du et al. 2026 (arXiv 2610.11325, iso-EPIGS): ML-accelerated H vs D free-energy differences in crystals, including oxalic acid. Newest and closest in method, does not compare polymorphs.

Near misses to check next: Srinivasan, Car and Sebastiani 2010 (KDP transition isotope effect), Schaack et al. 2023 PRL (NaOH isotope-driven phase transition), Day and Nyman 2015 (vibrational re-ranking, unverified).
