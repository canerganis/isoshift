# Prior-art sweep: geochemical D/H fractionation and computational isotope/ZPE phase stability

Scope: two literatures that could pre-empt F01 (deuteration favours the polymorph with the shorter O-H bond in strong O-H...O solids, slope about 0.12 to 0.15 meV/H per mÅ, stretch term about half cancelled by bend/libration, fails for weak H-bonds). Searched 23 Oct 2026 with WebSearch, WebFetch, Crossref, OpenAlex, valency (arXiv/PubMed semantic search). Semantic Scholar was rate-limited.

Access limits, stated up front. Publisher full texts were blocked (HTTP 403 or bot walls) for Méheut 2010, Reynard 2009, Zhu 2023, Horita 2002, the brucite PIMD paper, Chacko 2001, Graham 1980/81, Yapp 1987, Kuroda, Hariya-Tsutsumi. For these I read abstracts or search summaries only, and I say so per entry. arXiv full texts of McKenzie 2014/2015 and Markland-Berne were read. Verdicts below are therefore firm for the molecular and computational literature and provisional for the geochemistry papers whose full text I could not open.

## Headline finding

1. No paper found that states, for a pair of mineral polymorphs or for minerals in general, "D goes into the phase with the shorter O-H / weaker H-bond, with a slope in energy per bond-length difference, and a regime where bend terms reverse it."
2. No first-principles H beta-factor paper found for goethite, lepidocrocite, boehmite, diaspore, bayerite or nordstrandite. Goethite DFT beta-factors exist for Fe and O only. So a goethite/lepidocrocite or boehmite/diaspore H beta comparison appears not to have been published (absence of evidence from abstract-level search, not proof).
3. The sign and the stretch-versus-bend mechanism are NOT new. They are established for single H-bonds (McKenzie et al. 2014, 2015, Kreevoy-Liang 1980 fractionation factors) and in water (Markland-Berne). F01 must be framed as the solid-state, polymorph-level, quantified, cross-family version.
4. Closest computational competitor in method is new and dated this month: iso-EPIGS (Du et al., arXiv 2610.11325, 8 Oct 2026), which states a goal of "foundation models of isotope effects across chemical space". It benchmarks on oxalic acid crystal and water, not on a polymorph screen.

## Literature 1: geochemistry of D/H fractionation in hydrous minerals

Format: citation, what it states (as far as I could verify), verdict (pre-empts / partly / related / no).

1. Suzuoki T, Epstein S (1976), Geochim. Cosmochim. Acta 40, 1229. https://doi.org/10.1016/0016-7037(76)90158-7
   Abstract read. Mica and amphibole D/H fractionation to water depends on temperature and on Al, Mg, Fe fractions in the octahedral site. Notes that hydrogen bonding modifies the fractionation in boehmite and kaolinite (exceptions to the cation trend). No O-H length or slope. Verdict: related. It is the origin of "H-bonding is special in boehmite and kaolinite", worth one citation.

2. Xu Y, Zheng Y-F (1999), Geochim. Cosmochim. Acta (1999), brucite-water experiments, volume and pages not verified. https://doi.org/10.1016/s0016-7037(99)00047-2
   Per search summary of the abstract: sequence of D enrichment in hydroxyl minerals Al-OH > Mg-OH > Fe3+-OH. A cation-bond ranking, not an H-bond or O-H length statement. Verdict: related. 

3. Dobson PF, Epstein S, Stolper EM (1989), Geochim. Cosmochim. Acta 53, 2723. https://doi.org/10.1016/0016-7037(89)90143-9
   Abstract read. Vapor-glass D/H fractionations are larger than for most mineral-water pairs, "possibly due to strong hydrogen bonding" in the glass. Qualitative, glasses. Verdict: related.

4. Dyar and co-workers, ion-probe study of amphiboles and micas (search summary, authors and year not confirmed). Fractionation "depends essentially on the strength of the OH bond", correlated with octahedral cation electronegativity. Bond strength, not H-bond length. Verdict: related. I could not identify the reference; do not cite until located.

5. Méheut M, Lazzeri M, Balan E, Mauri F (2010), Geochim. Cosmochim. Acta 74, 3874. https://doi.org/10.1016/j.gca.2010.04.020
   Abstract read only (full text blocked). Harmonic DFT phonons, H/D beta-factors for brucite, kaolinite, lizardite, gibbsite vs water gas. Curves share a shape with a minimum from about 200 C (brucite) to about 500 C (gibbsite). Calculated mineral-liquid curves overestimate data by 15 to 8 per mil. Internal H fractionation between inner-surface and inner hydroxyls: -23 per mil (kaolinite) and +63 per mil (lizardite) at 25 C, linear in T^-2.
   Relevance: it is a harmonic first-principles beta-factor set for hydroxides, so a polymorph-pair comparison is formally derivable from this kind of data, but all four minerals have different formulas, and the abstract gives no polymorph pair and no O-H-length or H-bond rule. The opposite-sign internal fractionation in two layered silicates is itself evidence that site-level H-bond environment can flip the sign. Verdict: partly (method precedent and closest geochemical data set). Action: open the full text and grep for "hydrogen bond", "stretching", "bending" before freezing the prior-art paragraph.

6. Reynard B, Caracas R (2009), Chem. Geol. (2009), D/H fractionation brucite-water from first-principles vibrational modeling. https://doi.org/10.1016/j.chemgeo.2009.01.007
   Full text and abstract not retrieved. A search snippet (source not confirmed) says brucite's beta-factor is very sensitive to the high-frequency OH stretches where anharmonicity matters, with harmonic results deviating from experiment by about +20 to 25 per mil. Verdict: related, supports F01's harmonic-validity caveat. Verify wording before quoting.

7. Asaduzzaman A, Ganguly J et al. (2021), ACS Earth Space Chem., talc-serpentine-brucite-water. https://doi.org/10.1021/acsearthspacechem.1c00003
   Abstract read. DFT D/H fractionation, brucite calculated 5 to 13 per mil below the experimental curve, opposite sign of discrepancy to an earlier first-principles calculation. Also epidote (2018) https://doi.org/10.1021/acsearthspacechem.8b00076. Verdict: related (harmonic first-principles D/H for hydroxides, with disclosed error bars of the order of 10 per mil).

8. Horita J, Driesner T, Cole DR (1999), Science 286, 1545. https://doi.org/10.1126/science.286.5444.1545 and Horita et al. (2002), Geochim. Cosmochim. Acta. https://doi.org/10.1016/s0016-7037(02)00887-6
   Brucite-water D/H increases by 12.4 per mil from 15 to 800 MPa at 380 C, linked to water density. Pressure effect on fractionation, not a polymorph or H-bond-length rule. Verdict: related (cite only if F01 discusses pressure).

9. Driesner T (1997), Science 277, 791, effect of pressure on D/H fractionation in high-temperature water. https://doi.org/10.1126/science.277.5327.791
   This is the "Driesner 1997" that exists; it concerns water, not H-bond length versus mineral fractionation. I found no Driesner paper relating mineral D/H to H-bond length. Verdict: no. Do not cite for the rule.

10. Zhu et al. (2023), Chem. Geol., portlandite/brucite-water from vibrational spectra at elevated T and P. https://doi.org/10.1016/j.chemgeo.2023.121470
    Title only. Experimental spectra-based beta-factors for Ca(OH)2 and Mg(OH)2, which differ in O-H length and H-bonding (portlandite has a slightly different H environment). A direct portlandite vs brucite comparison in this paper would be the nearest published "pair" of isostructural hydroxides. Verdict: unknown, potentially partly. Must be read.

11. Path-integral MD with machine-learned potentials for H and O fractionation between brucite and water, Geochim. Cosmochim. Acta (2023). https://www.sciencedirect.com/science/article/abs/pii/S0016703723000686 (authors and DOI not retrieved)
    Per search summary: compares PIMD with the harmonic approximation to assess quantum effects. Verdict: related. It is the geochem precedent for "MLIP plus NQE for D/H in a hydroxide", and for quoting harmonic error.

12. Liu et al. (2019), Geochim. Cosmochim. Acta, gypsum/bassanite/water DFT (O and H). https://doi.org/10.1016/j.gca.2018.08.045
    Harmonic DFT fractionation for two hydration states of CaSO4 (H and O isotopes, 0 to 60 C). Hydrates, but different formula (CaSO4.2H2O vs CaSO4.0.5H2O), not polymorphs, no H-bond rule in the abstract. Verdict: related, relevant to the hydrate subset of the screen.

13. Goethite beta-factors: Blanchard M et al. (2015), Geochim. Cosmochim. Acta, "Reduced partition function ratios of iron and oxygen in goethite" (Fe and O, with NRIXS). https://hal.sorbonne-universite.fr/hal-01096956 . Hydrogen not treated. Goethite and hematite O beta-factors similar. Verdict: no for H.

14. Aluminum hydroxides, experimental: Vitali F, Blanc G, Larqué P, Lefèvre J, Eisenberg B (2001), Geochim. Cosmochim. Acta 65, 1391, H isotope fractionation in gibbsite, nordstrandite, bayerite synthesized at 8 to 51 C. alpha(gibbsite-water) 0.998 +/- 0.006. Companion O-isotope paper (Clays Clay Miner. 2000) says alpha(Al(OH)3-H2O) is polymorph dependent. Abstract-level; first-author and DOI not verified. Verdict: related. These are the only polymorph-resolved D/H data found for Al(OH)3 and could serve as an experimental check, but the abstract gives no polymorph-to-polymorph D/H difference.

15. Goethite experimental D/H: Yapp CJ (1983, 1987, 1990 curves), Feng and Yapp (2008) Geochim. Cosmochim. Acta, https://doi.org/10.1016/j.gca.2007.12.013 ; Sultan et al. (2015) Orient. J. Chem. https://doi.org/10.13005/ojc/310107 . Goethite-water only, structural vs non-stoichiometric H pools. No lepidocrocite D/H found. Verdict: related, not pre-empting.

16. Zheng Y-F: Zheng (1993) EPSL 120, 247, O isotopes in hydroxyl-bearing silicates; Zheng (1998) Phys. Chem. Minerals, O isotopes between hydroxide minerals and water. https://doi.org/10.1007/s002690050105 . Both are oxygen isotopes. No Zheng hydrogen increment paper located. Verdict: no for H. Do not cite as D/H precedent.

17. Chacko T, Cole DR, Horita J (2001), Rev. Mineral. Geochem. 43, 1. https://doi.org/10.1515/9781501508745-004 . Review chapter, text not read. Presumably tabulates empirical D/H calibrations. Verdict: unknown, cite as review only after skimming its hydrogen-bond discussion.

18. Not located at all: Graham 1980/81 discussion of H-bonding, Hariya-Tsutsumi 1981 (exists as Chem. Geol. 33; https://doi.org/10.1016/0009-2541(81)90070-x , Mn minerals), Kuroda, Wang/Rustad H-isotope work. I did not find any statement from these relating D/H to O-H length. Treat as unchecked.

### Mechanistic prior art from physical chemistry (more dangerous than geochemistry)

19. McKenzie RH, Bekker C, Athokpam B, Ramesh SG (2014), J. Chem. Phys. 140, 174508. https://doi.org/10.1063/1.4873352 (arXiv 1401.3792)
    Abstract read. Two-diabat model for O-H...O, R about 2.4 to 3.0 Å. Quantum effects of bending modes "compete with those of the stretching mode for weak to moderate H-bond strengths". Verdict: partly pre-empts the mechanism (competition), not the polymorph claim, and it is a single-bond model. This is already cited in decision 05.

20. McKenzie RH, Athokpam B, Ramesh SG (2015), J. Chem. Phys. 143, 024305. https://doi.org/10.1063/1.4927391 (arXiv 1504.04939)
    Full text read. H/D fractionation factor Phi of a protein H-bond vs the solvent, as function of donor-acceptor distance R. Stretch zero-point difference alone makes Phi fall as R decreases (D avoids strong H-bonds, prefers the weaker one); bend hardening with decreasing R raises Phi, "competing quantum effects", and the bend contribution is described as one of the main results. Includes secondary geometric isotope effect and tunnelling (small, mostly R about 2.4 to 2.6 Å). Compares with the empirical Phi(R) of Kreevoy and Liang (JACS 102, 3315, 1980) and Mildvan et al. Verdict: partly pre-empts the SIGN and the stretch/bend cancellation concept for O-H...O. It does not do polymorphs, solids, slopes in meV per mÅ, or a screen. Note the model's reference is a donor-acceptor distance of 2.8 Å, close to F01's weak/strong cut near 2.9 Å. The recommended decision-05 optional action 10 (compare McKenzie crossover with F01 about 2.9 Å) can be done from the data in this paper.

21. Markland TE, Berne BJ (2012), PNAS, "Unraveling quantum mechanical effects in water using isotopic fractionation" (arXiv 1307.7684, text read). Harmonic or rigid O-H models greatly over-predict fractionation; anharmonic models give partial cancellation between intra- and intermolecular quantum effects (competing quantum effects). Verdict: related, supports "harmonic over-predicts" caveat. DOI not retrieved, cite via arXiv number or look up PNAS.

22. Ice Ih, bend/libration versus stretch: Pamuk et al. (2012) PRL 108, 193003 https://doi.org/10.1103/PhysRevLett.108.193003 ; Rasti et al. (2022) J. Phys. Chem. Lett., volume isotope effect from "a delicate competition between" intramolecular stretches and librations https://doi.org/10.1021/acs.jpclett.2c03212 ; Umemoto et al. (2015) PRL 115, 173005 https://doi.org/10.1103/PhysRevLett.115.173005 . Verdict: related (same competition, single compound, volume not stability).

23. Bigeleisen's rule that the heavy isotope concentrates where the bonding is stiffer (Bigeleisen, Science 147, 463, 1965), from memory, not retrieved. This is the textbook basis of "D prefers the stiffer, shorter O-H". F01's sign is the stretch-dominated Bigeleisen outcome. Verdict: the sign is textbook; cite it so a reviewer cannot say the sign was presented as new.

## Literature 2: computational multi-compound isotope and zero-point phase-stability work

24. Bourgeois N, Crivello J-C, Cenedese P, Joubert J-M (2018), J. Phys.: Condens. Matter. https://hal.archives-ouvertes.fr/hal-02011296 (already in novelty.md). 115 hydrides, harmonic phonons, H/D/T formation enthalpies and plateau pressures. Companion: Bourgeois et al., Systematic first-principles study of binary metal hydrides, ACS Comb. Sci. 2017 https://doi.org/10.1021/acscombsci.7b00050 (not read; check whether it also contains isotope data). Verdict: partly (largest prior isotope screen, but gas-solid formation, metals, DFT).

25. Lee H, Hegde VI, Wolverton C, Xia Y, arXiv 2407.09674 (Materials Today Physics 2025). MACE trained on 2,738 crystals, harmonic F(300 K) MAE 2.19 meV/atom, "thermodynamic analysis of polymorphic stability in 126 systems" at 300 and 1000 K. No isotopes. Verdict: related, nearest MLIP high-throughput polymorph free-energy paper. Reviewer may say isotope substitution is a one-line extension of this workflow, so F01's content must stay the finding, not the workflow.

26. Sahasrabuddhe H et al., ChemRxiv 2026, High-throughput harmonic phonon database for 26,413 inorganic crystals for Materials Project. https://doi.org/10.26434/chemrxiv.15004632/v1 . Phonon DOS and F, S, Cv, no isotope dependence in the abstract. Related: with force constants available, isotope shifts are derivable by anyone. Also Petretto et al. (2018) Sci. Data, DFPT phonons for 1,521 semiconductors https://doi.org/10.1038/sdata.2018.65 . Verdict: related.

27. Friedrich R et al. (2019), Coordination corrected ab initio formation enthalpies, arXiv 1811.08952. States zero-point and thermal contributions to oxide/halide formation enthalpies are small and of opposite sign, largely cancelling; includes polymorph ranking correction. Verdict: related (ZPE in inorganic phase stability, no isotopes).

28. Molecular-crystal vibrational free-energy and ZPE polymorph ranking:
    a. Nyman J, Day GM (2015), CrystEngComm 17, 5154. https://doi.org/10.1039/C5CE00045A . 1,061 structures of 508 molecules: re-ranking below or at room temperature in about 9% of pairs; vibrational contributions dominated by entropy.
    b. Nyman J, Day GM (2016), Phys. Chem. Chem. Phys., 475 polymorph pairs, re-ranking in 21% at melting point. https://doi.org/10.1039/C6CP05447A
    c. Weatherby JA et al. (2022), J. Chem. Phys., PV17 benchmark, mean Delta F_vib 1.0 kJ/mol, max 2.3. https://doi.org/10.1063/5.0083082
    d. Rossi M, Gasparotto P, Ceriotti M (2016), PRL 117, 115702, paracetamol: nuclear quantum effects matter for polymorph stability. https://doi.org/10.1103/PhysRevLett.117.115702
    e. Kapil V, Engel EA (2022), PNAS, benzene, glycine, succinic acid Gibbs free energies with MLIP and NQE. https://doi.org/10.1073/pnas.2111769119
    f. Reilly AM, Tkatchenko A (2014), J. Chem. Phys., vibrational contributions in 23 molecular crystals (sublimation enthalpy, not polymorph ranking). https://doi.org/10.1063/1.4812819
    Verdict for all: related. They show ZPE and vibrational terms change polymorph ranking, no isotope substitution scan, organics. They justify the "ZPE can flip rankings" premise and supply magnitude scale (1 to 3 kJ/mol, i.e. 10 to 30 meV per molecule), against which F01's meV/H shifts should be placed.

29. Single-system H/D polymorph or phase-boundary calculations (all single compound):
    Pamuk, Allen, Fernandez-Serra (2015), PRB 92, 134105, ice XI/Ih H2O vs D2O https://doi.org/10.1103/PhysRevB.92.134105 (quasi-harmonic, 6 K vs 4 K experiment);
    Ramírez, Neuerburg, Herrero (2012), J. Chem. Phys., ice Ih/II/III quasi-harmonic: ice II stabilised by lower ZPE https://doi.org/10.1063/1.4757064 ;
    Errea I et al. (2016), Nature 532, 81, H3S/D3S symmetrization pressure lowered by 72 and 60 GPa https://doi.org/10.1038/nature17175 ;
    Cherubini et al., arXiv 2403.09238, ice VIII to X, 10 GPa H/D shift;
    Taureau et al., arXiv 2307.15684, H3S, about 25 GPa H/D shift;
    Schmidt J, Spaldin NA (2026), Phys. Rev. Lett. (as listed), 18O in SrTiO3 with MLIP + SCHA https://doi.org/10.1103/4293-1g2r (journal listing as returned, not verified);
    Belli, Zurek, arXiv 2406.13178 (PdCuH2 MLIP + SSCHA, 2025).
    Verdict: related; each is one compound. Ramírez 2012 is useful: "lower ZPE phase is stabilised by quantum effects" is the general pattern.

30. Du M-Z, He S-Y, Shen J, Ye Z, Zeng J-X, Zhang DH, Kapil V, Fang W (2026), "Isotope Effects at Classical Cost through Mass-Differentiable Machine Learning", arXiv 2610.11325 (8 Oct 2026). Isotope-resolved free energies for gas, liquid, crystal (water, oxalic acid crystal), transferable to partially deuterated isotopologues, aims at "foundation models of isotope effects across chemical space". Verdict: related now, potential pre-emption of the method (not of the inorganic polymorph finding) within months. Track it. It is not in novelty.md.

31. Wang X et al. (2026), arXiv 2604.20230, deep free energy learning for CSP with nuclear quantum effects in La-Sc-H at 200 GPa. High-throughput CSP with NQE for hydrides, no H/D scan. Verdict: related.

32. MLIP phonon accuracy caveat (relevant to F01 reviewers): Loew et al., npj Comput. Mater. 2025, "Universal MLIPs are ready for phonons" https://doi.org/10.1038/s41524-025-01650-1 ; Deng et al., "Systematic softening in universal MLIPs", npj Comput. Mater. 2024 https://doi.org/10.1038/s41524-024-01500-6 (systematic frequency underprediction biases ZPE). Verdict: related; supports reporting three-model agreement and stating the softening bias.

Searches in this literature that found nothing: a high-throughput or multi-compound H/D polymorph-stability study with universal MLIPs; a Materials Project/OQMD analysis of isotope effects on phase stability; any ZPE-versus-polymorph study that defines a regime variable in O-H length or O...O.

## Is F01 pre-empted?

Short answer: not as stated, with three real exposures.

What survives. I found no source that (a) applies the sign rule at the level of inorganic solid polymorph free-energy differences, (b) gives a slope in energy per H per mÅ of O-H difference, (c) screens about 200 inorganic pairs with several universal MLIPs, or (d) draws the strong/weak regime boundary at O-H 0.99 Å or O...O about 2.9 Å. The closest data sets (Méheut 2010, Asaduzzaman 2018/2021, Liu 2019) compare phases of different formula against water, and Bourgeois 2018 compares hydrides against H2 gas. A polymorph-pair beta comparison for goethite/lepidocrocite, boehmite/diaspore or gibbsite/bayerite is not in anything I could access.

Exposure 1, the mechanism and the sign. The rule "D prefers the weaker H-bond, stretch dominates, bend/libration partly cancels, and bends dominate for weak to moderate bonds" is in McKenzie 2014 and 2015 for a single O-H...O bond, in the Kreevoy-Liang fractionation-factor literature, in Markland-Berne for water, and in Rasti 2022 for ice Ih. Any novelty wording that sounds like "we discovered that deuteration favours the shorter O-H" will be rejected as textbook (Bigeleisen). The defensible novelty is quantitative and systematic: the slope, the cancellation fraction (about half), the regime boundary, and the multi-model held-out test (123/130 in the O-H subset).

Exposure 2, formal equivalence to beta-factors. The harmonic ln beta difference between two phases of one formula is the same physical quantity as F01's ddF, so the geochemistry community owns the formalism and will say the "polymorph version" is a trivial rearrangement of mineral-water beta-factor tables (note: usual practice computes ln beta from the fully substituted phase, which equals F_D - F_H at the harmonic level; I did not verify this per paper). The answer is that nobody tabulated the polymorph differences or correlated them with O-H length across 23 formulas, but the paper should say plainly that the quantity is a beta-factor difference.

Exposure 3, unread full texts. Méheut 2010, Reynard 2009, Zhu 2023 and the brucite PIMD paper may contain a sentence linking beta to O-H frequency or H-bond strength, and Zhu 2023 may contain a portlandite/brucite pair. Until these are read, "no published statement" should be worded as "we did not find".

Net: F01 survives as "first systematic, multi-model, solid-state polymorph test of a known stretch-versus-bend competition, with a fitted slope and a regime boundary". It does not survive as "new rule" or "first to show D favours the shorter O-H". Decision 05's prior-art sentence is adequate in spirit but under-cites. Decision 05 "what would change this" item 4 (a paper reports the polymorph-level rule with a regime boundary) is not triggered by anything I found.

## Must-cite list and suggested sentence changes

Must cite (add):
1. Méheut, Lazzeri, Balan, Mauri 2010, https://doi.org/10.1016/j.gca.2010.04.020 (read full text first).
2. McKenzie, Athokpam, Ramesh 2015, https://doi.org/10.1063/1.4927391 (fractionation factor vs R, stretch/bend), with Kreevoy and Liang 1980 JACS 102, 3315.
3. Suzuoki and Epstein 1976, https://doi.org/10.1016/0016-7037(76)90158-7 (H-bonding exceptions boehmite, kaolinite).
4. Reynard and Caracas 2009, https://doi.org/10.1016/j.chemgeo.2009.01.007, and the brucite PIMD paper (harmonic validity for hydroxides), after reading.
5. Markland and Berne 2012 (arXiv 1307.7684) for harmonic over-prediction.
6. Nyman and Day 2015, https://doi.org/10.1039/C5CE00045A, and Rossi et al. 2016, https://doi.org/10.1103/PhysRevLett.117.115702, for ZPE/NQE re-ranking polymorphs.
7. Lee, Hegde, Wolverton, Xia (arXiv 2407.09674) as the nearest MLIP high-throughput polymorph F paper without isotopes.
8. Pamuk et al. 2015 and Errea et al. 2016 as the single-system H/D phase-boundary precedents (Pamuk is already in novelty.md).
9. Du et al. 2026 (arXiv 2610.11325) as concurrent work on isotope free energies with ML.

Cite if space: Dobson et al. 1989, Xu and Zheng 1999, Liu et al. 2019 (gypsum/bassanite), Vitali et al. 2001 (Al(OH)3 polymorph D/H, as an experimental route), Asaduzzaman 2018/2021, Bigeleisen 1965.

Suggested sentence changes.

Prior art sentence in decision 05, replace with:
"The sign of the effect and its stretch-bend competition are established for single O-H...O bonds and fractionation factors (Kreevoy and Liang 1980; McKenzie et al. 2014, 2015), for water (Markland and Berne 2012) and for ice (Pamuk et al. 2012; Rasti et al. 2022). Harmonic first-principles D/H beta-factors exist for individual hydroxides, hydrates and phyllosilicates against water (Méheut et al. 2010; Reynard and Caracas 2009; Asaduzzaman et al. 2021; Liu et al. 2019), and a harmonic isotope screen exists for 115 metal hydrides (Bourgeois et al. 2018). We found no published comparison of polymorph pairs across inorganic O-H...O solids, no slope against the O-H difference, and no regime boundary, which is what we report."

Headline wording for F01: avoid "rule", "discovery", "first". Use "In this screen, deuteration favours the polymorph with the shorter O-H in the strong-H-bond subset, with held-out sign accuracy 123/130, a fitted slope, and failure for weak bonds."

Add a one-line formal remark to the methods: "The harmonic isotope free-energy difference between two polymorphs equals the difference of their ln beta factors for full substitution, so the quantity is the geochemical beta-factor difference."

Add to limitations: universal MLIP phonon softening bias (Deng et al. 2024; Loew et al. 2025), and harmonic overestimate for hydroxides (Reynard and Caracas 2009 per snippet; Markland and Berne 2012).

## Residual risk and suggested follow-ups

1. Read Méheut 2010 and Reynard 2009 full texts via institutional access and grep "hydrogen bond", "bending", "libration", "stretch". 20 minutes. This is the single highest-value check, since it could sharpen or weaken Exposure 1 for the minerals.
2. Open Zhu 2023 (portlandite vs brucite), the brucite PIMD paper, Chacko 2001 section on hydrous minerals, and the Dyar-type ion-probe reference (author unknown) to settle items 4, 10, 11, 17.
3. Look for lepidocrocite or boehmite D/H experimental values to test whether F01's goethite/lepidocrocite and boehmite/diaspore sign predictions can be checked against the geochemical literature. None found in this sweep.
4. Re-run the sweep with arXiv/ChemRxiv full-text search for "iso-EPIGS" follow-ups and for any "foundation model isotope" preprint; Du et al. is only two weeks old.
5. Not covered: Russian and Chinese mineralogy literature, Zheng's Chinese-language increment work, spectroscopic Badger-type correlations for hydroxide polymorph stability, and SCAN/PIMD studies of lepidocrocite or boehmite.
