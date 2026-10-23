# Prior-art sweep for F01, 23 Oct 2026

Five agents (3 Haiku, 2 Sonnet) searched Crossref (Elsevier member 78), OpenAlex, arXiv, Semantic Scholar, Valency and publisher-filtered web search (ACS, RSC, APS, Wiley, Nature, IUCr, AIP). About 140 queries in total. Per-agent tables and query logs sit next to this file.

## Verdict

Nobody has published F01 itself. No source applies the shorter-O-H sign rule to polymorph free-energy differences across inorganic solids, gives a slope per H per mÅ, screens about 200 pairs with universal MLIPs, or draws the 0.99 Å / about 2.9 Å regime boundary.

The direction and the mechanism are prior art. The paper must not claim either one.

## What is already published

| Item | What it states | In refs.bib | Action |
|---|---|---|---|
| Zhou, Kye, Harbison 2004, 2006; Ip 2012 | For one OHN complex (4-MPPCP), deuteration favours the polymorph with the weaker H-bond, explained by ZPE | yes, cited | Say plainly that the sign was proposed there for one system |
| McKenzie 2014, 2015 | Stretch-bend competition in fractionation against O...O, model reference 2.8 Å | yes | Compare their crossover with our 2.9 Å, or say the comparison was not made |
| Ichikawa 1978, 1987 (PRB 36, 874), 1995, 2000; Robertson-Ubbelohde 1939 | Tc against O...O within isostructural families; deuteration lengthens O...O and stabilises the ordered phase | **no** | Add. The sign agrees when the variable is O-H length. Their mechanism is anharmonic geometry, ours is harmonic at fixed geometry, which also explains why KDP, NaOH and KOH are negative controls |
| Méheut 2010; Reynard-Caracas 2009; Asaduzzaman 2018/2021; Liu 2019 | Harmonic DFT D/H beta-factors for individual hydrous minerals against water | Méheut yes, others **no** | State that harmonic ddF for full substitution is the difference of ln beta-factors, so the formalism belongs to geochemistry. No H beta-factor was found for goethite/lepidocrocite, boehmite/diaspore or gibbsite/bayerite |
| Kreevoy-Liang 1980 | Fractionation factor against H-bond strength | **no** | Add next to McKenzie |
| Lee, Hegde, Wolverton, Xia 2024 (arXiv 2407.09674) | Same pipeline (MACE harmonic F, 126 polymorph systems), no isotopes | yes | A reviewer may call H/D a one-line extension. The answer is the rule, the slope decomposition and the held-out test, not the pipeline |
| Du et al. 2026 iso-EPIGS (arXiv 2610.11325) | Mass-differentiable ML isotope free energies, water and oxalic acid | yes | Track it. Method paper, no polymorph result |
| Nyman-Day 2015; Rossi-Gasparotto-Ceriotti 2016 | ZPE and NQE re-rank polymorphs (molecular) | Rossi yes, Nyman-Day **no** | Optional |

## Open items

1. NaOH/NaOD, PRL 2023 (arXiv 2310.16462), says deuteration restores weak H-bonds. Read the full text and check it against the "fails for weak H-bonds" sentence. NaOH is already a negative control.
2. Méheut 2010 and Reynard-Caracas 2009: full text was blocked. Search them for "hydrogen bond", "bending", "libration" and "stretch". This is the most likely place for a missed sentence.
3. The secondary O...O predictor (83%) may not map onto the KDP phases. Add one hedge sentence.
4. Not covered: Google Scholar full text, Russian and Chinese mineralogy literature, and forward citations of McKenzie 2015 and Li-Walker-Michaelides 2011 (Semantic Scholar rate limit).

## Council review (decision 15)

The council (Opus, Astra, Argon) kept the edits with wording fixes. It refuted the first absence sentence: single-system polymorph isotope comparisons exist and the paper uses two of them (Graham 1980 boehmite/diaspore in F12, Bridgman 1935 ice in F07), plus Pamuk et al. 2015 (ice XI/Ih, PRB 92, 134105). Further threats to track: Jodin-Caumon 2009 and Vitali, Longstaffe, Bird, Gage, Caldwell 2001 (Al(OH)3 D/H, calibrates on gibbsite only, not a polymorph comparison).

## Wording

Use (decision 15, action 5c): "In the abstracts and texts we could read (the full texts of Graham 1980, Méheut 2010 and Reynard 2009 were not accessible), we found no study that compares polymorph pairs across many inorganic O-H...O compounds, fits the polymorph isotope free-energy difference against the O-H length difference, or locates in O-H length where the sign of that comparison reverses." Avoid: "first", "discovery", "new direction of the isotope effect", "first rule linking H-bond strength to isotopic polymorphism".
