# F10. Isotope atlas: predicted deuteration preference for every O-H polymorph pair in the Materials Project set

Status: ATLAS ONLY, untested. Post-freeze addendum; it does not change the frozen F01 headline (decision 07). Council 08 set the literature test aside as low priority (the boehmite/diaspore literature test is run separately), so this finding reports the map, its counts and its cost, and no verdict on the rule.

## What was built

`src/isoshift_event/atlas.py` reads `data/isoshift/mp_h.json` (Materials Project, no C, E_hull ≤ 50 meV/atom) and, from the stored DFT geometry only (no phonons, no ML relaxation), writes `results/atlas.csv` and `results/atlas_summary.json`. Predictions for the observed strong-regime pairs were committed blind in `docs/predictions/P08_atlas_blind.md` (commit d991991) before any literature lookup.

* Population: structures with at least one O-H donor (H with nearest O ≤ 1.15 Å), no atom-count cap; same reduced composition, primitive cells, deduplicated with StructureMatcher (ltol 0.2, stol 0.15, angle_tol 5) and the space-group gate of `pairs.py`; pairs with |dE| ≤ 50 meV/atom from MP energies.
* Per structure: mean O-H over all donors, mean donor O...O over donors with an acceptor (H...O < 2.6 Å).
* Regime: strong if either polymorph has mean O...O ≤ 2.929 Å (translated threshold in `results/F01_oo.json`).
* Sign: F01 convention; deuteration favours the polymorph with the shorter mean O-H (longer mean O...O). Confidence from |dO-H| (5 mÅ) and |dO...O| (0.03 Å): high, medium, low, or conflict when the two differences disagree.
* Experimentally observed: MP theoretical=False for the phase (or any entry merged into it).

## Counts

| Quantity | Value |
|---|---|
| O-bearing formulas in mp_h.json | 2722 |
| Structures with an O-H donor | 3212 (14 duplicates merged) |
| Polymorph pairs | 1796 in 317 formulas |
| Regime | strong 1488, weak 292, undefined 16 |
| Confidence, all pairs | high 503, medium 386, low 383, conflict 524 |
| Both phases experimentally observed | 218 |
| Strong regime and both observed (P08 list) | 185 pairs, 122 formulas; high 62, medium 29, low 43, conflict 51 |

Where both differences are above their cuts (639 pairs), dO-H and dO...O agree in sign in 79% of pairs (correlation of dO-H with dO...O over all pairs, r = -0.54). Most conflicts sit at small differences (median |dO-H| 2.9 mÅ, |dO...O| 0.028 Å): the median |dO-H| between MP polymorphs is 4.1 mÅ, below the 5 mÅ headline eligibility, so most database pairs are low-signal calls.

## Scalability

The whole set (3402 O-bearing structures read, 3212 with O-H donors, 1796 pairs) runs in 53 s on one CPU core: 0.03 s per pair including deduplication, 8.6 s for the donor geometry. No GPU. The cost is set by StructureMatcher, not by the prediction, so the map scales to any database that stores relaxed structures.

## Caveats

1. The F01 rule was established on ML-relaxed structures with harmonic free energies; the atlas applies it to DFT database geometry, where polymorph O-H differences are often a few mÅ. It is untested on this geometry.
2. The rule is a statement about the vibrational isotope term between fixed, ordered structures. Isotope effects that come from proton order-disorder, tunnelling or kinetics are outside it; P08 predeclares their exclusion.
3. The 0.99 Å O-H boundary was chosen after inspecting the data (decision 07); its O...O translation inherits that.

## Literature step: collected, not scored

Before the council 08 redirect, the blind collection step of P08 ran: a Sonnet agent (`sonnet-atlas-blind`, 27 Bond queries in `logs/bond_queries.jsonl`, then OpenAlex and web) wrote 26 rows to `data/isoshift/atlas_lit.csv`. Most rows are proton order-disorder, ferroelectric, superionic or symmetrisation transitions, which the P08 exclusion rule E1 removes. The CSV is kept as raw input for whoever runs the test. Scoring against P08 was not done, so this finding makes no claim that the rule holds or fails on experiment.

## Blind literature test (P08)

Scored exactly by the rules in `docs/predictions/P08_atlas_blind.md` (committed d991991, before the literature lookup). Input: the 26 rows of `data/isoshift/atlas_lit.csv`, collected blind. Per-row record: `results/post_freeze/F10_lit_score.json`. No rule was added or changed after reading the rows.

| # | Compound | Observation | Source direction | Decision | Rule | Reason | Atlas mapping |
| 1 | K3H(SO4)2 (potassium trihydrogen disulf) | transition_shift_T | phase_2 | excluded | E1 | K3H(SO4)2 para to antiferroelectric ordering; source attributes to H tunnelling in a disordered short bond | not in atlas |
| 2 | K3H(SO4)2 (potassium trihydrogen disulf) | transition_shift_T | phase_2 | excluded | E1 | same compound, split-wavefunction/tunnelling picture, no symmetry change | not in atlas |
| 3 | Cs3H(SeO4)2 (tricesium hydrogen diselenat) | transition_shift_T | phase_2 | excluded | E1 | Cs3H(SeO4)2 proton-disordered para to antiferroelectric ordering, tunnelling | atlas has Cs3H(SeO4)2 pairs (Cc, P2_1/m, Cm) but none of these phases |
| 4 | Cs3H(SeO4)2 (tricesium hydrogen diselenat) | transition_shift_T | phase_2 | excluded | E1 | superionic phase, H-bond network reconstruction (disordered protons) | no |
| 5 | Cs3H(SO4)2 (tricesium hydrogen disulfate) | crystallisation_outcome | phase_2 | excluded | E1 | Cs3H(SO4)2 superionic phase, H-bond network reconstruction; also a crystallisation/decomposition-limited observation | not in atlas |
| 6 | TlH2PO4 (thallium dihydrogen phosphat) | transition_shift_T | phase_2 | excluded | E1 | TlH2PO4 KDP-family order-disorder | not in atlas |
| 7 | KOH (potassium hydroxide) | transition_shift_T | phase_2 | excluded | E1 | KOH proton order-disorder, double-well tunnelling | atlas has KHO pairs, phases not matched |
| 8 | NaOH (sodium hydroxide) | transition_shift_T | phase_2 | excluded | E1 | NaOH quantum paraelectric to antiferroelectric ordering, zero-point fluctuations | atlas has NaHO pairs (weak regime), phases not matched |
| 9 | KH2PO4 (potassium dihydrogen phospha) | transition_shift_T | phase_2 | excluded | E1 | KH2PO4 order-disorder ferroelectric (Ubbelohde effect, named in the rule) | not in atlas |
| 10 | KH2PO4 (potassium dihydrogen phospha) | phase_diagram | none | excluded | E1 | KDP family, tunnelling; also no phase direction (E3) | not in atlas |
| 11 | NH4H2PO4 (ammonium dihydrogen phosphat) | transition_shift_T | phase_1 | excluded | E1 | NH4H2PO4 is the KDP family, room-T phase has disordered H2PO4 protons; source attributes shift to NH4 motion | not in atlas |
| 12 | AlOOH (delta-aluminium oxyhydroxide) | transition_shift_P | phase_1 | excluded | E1 | P21nm to Pnnm, Pnnm is H-disordered | atlas pair AlHO2 mp-625152 (Pnma) / mp-23807 (Pmn2_1) is not this pair (Pnnm absent) |
| 13 | AlOOH (delta-aluminium oxyhydroxide) | transition_shift_P | phase_1 | excluded | E1 | H-bond symmetrisation after disorder | no |
| 14 | FeOOH (epsilon-iron oxyhydroxide) | transition_shift_P | phase_1 | excluded | E1 | FeOOH P21nm to Pnnm, Pnnm has disordered H-bonds | atlas FeHO2 pair (Pnma / Cmc2_1) not matched |
| 15 | FeOOH (epsilon-iron oxyhydroxide) | transition_shift_P | none | excluded | E3 | magnetic spin reorientation at 8 GPa for both isotopologues: null result, no phase favoured, not a polymorph pair | no |
| 16 | Ca(OH)2 (portlandite (calcium hydroxi) | transition_shift_P | none | excluded | E3 | null result: no significant H/D difference in transition pressure, so no direction; high-P phase assignment unclear in the source | atlas pair Ca(HO)2 mp-23879 (P-3m1) / mp-643392 (P2_1/c) exists (#17 in P08) but the high-P phase is not identified with mp-643392, nothing to score |
| 17 | H2O (water ice (ice VII to symmet) | transition_shift_P | phase_1 | excluded | E1 | ice VII to symmetric phase (VII named in the rule) | no |
| 18 | H2O (water ice Ih / XI) | transition_shift_T | phase_2 | excluded | E1 | ice Ih to XI (named in the rule) | no |
| 19 | H2O (water ice II / Ic) | other | phase_2 | excluded | E1 | ice Ic is proton-disordered; also enthalpy sign only, not a free-energy ordering | atlas H2O pairs do not contain ice II/Ic |
| 20 | H2O (water ice XIV / XII) | transition_shift_T | unclear | excluded | E1 | XIV/XII hydrogen order-disorder; also no sign (E3) | no |
| 21 | CaAl2Si2O7(OH)2·H2O (lawsonite) | transition_shift_T | phase_2 | excluded | E1 | lawsonite proton ordering transition (ferroelectric P21cn) | atlas CaAl2Si2(H2O5)2 has Pna2_1, Pnma, Cmcm only |
| 22 | CaAl2Si2O7(OH)2·H2O (lawsonite) | transition_shift_T | none | excluded | E1 | lawsonite Cmcm/Pmcn transition, partly proton order-disorder; null result (E3) | as row 21 |
| 23 | (NH4)2Cu(H2O)6(SO4)2 (ammonium copper(II) Tutton s) | crystallisation_outcome | phase_2 | unmappable | n/a | Tutton salt H-type vs D-type differ by the direction of the Jahn-Teller long Cu-O bond. See text. | ambiguous |
| 24 | (NH4)2Cu(H2O)6(SO4)2 (ammonium copper(II) Tutton s) | crystallisation_outcome | phase_2 | unmappable | n/a | same compound and phase pair as row 23 (abrupt switch at about 50% D); same ambiguity. See text. | ambiguous |
| 25 | KH3(SeO3)2 (potassium trihydrogen disele) | transition_shift_T | phase_2 | excluded | E1 | KH3(SeO3)2 ordering of O-H-O hydrogens; D value also unverified | atlas KH3(SeO3)2 pairs exist, not matched |
| 26 | review (general H-bonded ionic and m) | other | unclear | excluded | E1 | review names no phase pair; source attributes to proton tunnelling (also unmappable) | no |
### Counts

| Quantity | Value |
|---|---|
| Rows | 26 |
| Scored right | 0 |
| Scored wrong | 0 |
| Excluded | 24 (E1 proton disorder, order-disorder or tunnelling: 22; E3 no direction: 2) |
| Unmappable | 2 (rows 23 and 24, same Tutton salt pair) |
| Mapped by CIF | 0 |
| Thermodynamic cases scored | 0 |
| Crystallisation cases scored | 0 |

### Rows that needed a judgement

* Row 11 (NH4H2PO4): read as the KDP family, so E1. The source itself attributes the shift to ammonium motion.
* Row 19 (ice II to Ic): the rule lists Ih, III, V, VI and VII, not Ic, but E1 also covers any proton-disordered phase and Ic is proton-disordered, so E1.
* Rows 15, 16: null results (no isotope shift). E3 is worded for a reported difference without a direction. A null result has no phase whose field deuteration enlarges, so it cannot be right or wrong; marked E3 on that reading.
* Rows 23, 24: not E1 (the source says no proton disorder) and not E2, so they are the only candidate crystallisation cases. The rule maps by formula and space group, but the atlas pair for this formula (mp-722275 theoretical, mp-504531 experimental, both P2_1/c, both Jahn-Teller elongated, dO-H +1.1 mÅ, low confidence) has one space group on both sides and MP carries no O7/O8 labels. Which entry is the H-type and which the D-type cannot be fixed with the P08 rule, so they are unmappable. The pair is also outside the 185 predeclared strong-regime observed pairs.

### Verdict

The blind literature test returns no score. Every experimental H/D polymorph or phase-boundary result found is a proton order-disorder, ferroelectric, superionic, symmetrisation or ice proton-ordering case, which is the class the atlas rule does not address, or a null result. The two remaining rows cannot be mapped to an atlas pair. With 0 scored cases (the rule asks for at least ten before even calling a result anecdotal), this test neither supports nor refutes the atlas sign calls, and F10 stays a map of database geometry with no experimental validation. A usable test needs an H/D result on two ordered, stoichiometrically identical polymorphs, which this search did not find.
