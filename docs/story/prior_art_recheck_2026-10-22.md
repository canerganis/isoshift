# Prior-art recheck, 22 Oct 2026 (after submission)

Can asked for a second literature search on whether the short-bond rule is already published. One conductor pass (Valency Bond semantic search plus a 10-query abstract batch, then a WebSearch on Merz and Kupka 2015) and five Claude Haiku agents, each on one angle, about 55 Valency Bond and WebSearch queries in total. These queries are logged here, not in `logs/bond_queries.jsonl`, so the 182-row count in the write-up stays the count at submission. Abstracts and search snippets only; no full texts were read in this pass.

## Angles

1. Isotopic and isotopomeric polymorphism.
2. High-throughput or database-scale isotope effects on phase stability.
3. Zero-point energy and D/H fractionation against O-H length, O...O distance or hydrogen-bond strength.
4. Isotope shift of the diaspore to δ-AlOOH boundary and of similar hydrous-mineral transitions.
5. Deuterated samples as stand-ins in neutron work, deuterated pharmaceuticals and ferroelectrics, and any 2025 to 2026 survey.

## Closest work found

| Work | What it shows | General rule across compounds? |
|---|---|---|
| Zhou, Kye, Harbison 2004 and 2006 (PubMed 15237992, 16870562) | Deuteration switches the stable polymorph of 4-methylpyridine pentachlorophenol; the short-hydrogen-bond form is disfavoured on deuteration through a smaller H/D zero-point difference | No, one system. Its direction agrees with the short-bond rule: a short hydrogen bond goes with a longer O-H bond |
| Falk, Hofmann, Merz 2018, ROY (doi 10.1107/S2052252518009995) | Deuteration selects one of two concomitant polymorphs | No, one compound |
| Shi et al. 2018, imidazolium hydrogen terephthalate (doi 10.1038/s41467-018-02931-8) | Deuteration lengthens O...O and gives a new phase | No, one system |
| Ford et al. 2012, 3,5-pyridinedicarboxylic acid (doi 10.1002/chem.201101104) | Vibrational free-energy stabilisation of a phase transition grows with deuteration | No, one compound |
| Merz and Kupka 2015, Cryst. Growth Des. 15, 1553 (secondary, via citing papers) | Survey that isotopic substitution can change molecular arrangement in crystals | Not established; the abstract was not retrieved, citing papers describe it as qualitative |
| McKenzie et al. 2014, 2015; Li, Walker, Michaelides 2011 | Stretch against bend competition, sign set by hydrogen-bond strength | Mechanism, no polymorph ranking (already cited) |
| Bourgeois et al. 2018 | 115 metal hydrides, H/D/T, gas-solid formation | Many compounds, but no polymorph pairs (already cited) |
| Lee et al. 2024, arXiv 2407.09674 | MACE phonons, polymorph stability in 126 systems | No isotopes |
| Du et al. 2026, arXiv 2610.11325 | Mass-differentiable path-integral surface for water and one oxalic acid crystal | Method for single systems (already cited) |
| Scheiner 2000 (PubMed 10812023) | In gas-phase complexes, deuteration strengthens neutral hydrogen bonds and weakens ionic ones | No; a reminder that the sign can depend on bond type |

## AlOOH prediction

No work found measures or computes the isotope shift of the diaspore to δ-AlOOH boundary. Related measured shifts all raise the transition pressure on deuteration: δ-AlOOH disorder 9.0 to 13.4 GPa (Sano-Furukawa et al. 2018, full text audited in `docs/findings/F04-source-audit.md`; a 2016 JpGU abstract gave a preliminary 12.1 GPa), ε-FeOOD staying asymmetric above the 17.9 GPa symmetrisation of ε-FeOOH (Ikeda et al. 2025), and LiOD symmetrising above LiOH in path-integral calculations (Tanaka et al. 2025).

## Verdict

No paper in this search states a general rule for which polymorph deuteration favours across many compounds, and none reports a slope of the isotope free-energy difference against O-H length. The nearest precedent, Zhou et al., is a single system whose direction agrees with the rule. The write-up wording ("a correlation we did not find in earlier work", "a logged literature search found no...") stands. Coverage is limited to abstracts and snippets.
