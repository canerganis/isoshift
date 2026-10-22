# P08. Blind isotope atlas: which polymorph deuteration favours, for every experimentally observed strong-regime O-H pair in the Materials Project set

Post-freeze addendum. It does not change the frozen F01 headline (decision 07). Written and committed before any literature lookup on isotope-induced polymorphism, deuteration-shifted transitions or H/D phase differences. Code: `src/isoshift_event/atlas.py`. Data: `results/atlas.csv`, `results/atlas_summary.json`.

## Method (database geometry only)

1. Population: every entry of `data/isoshift/mp_h.json` (Materials Project, no C, E_hull ≤ 50 meV/atom) with at least one O-H donor (H whose nearest O is within 1.15 Å). No atom-count cap. 3212 such structures in 2722 O-bearing formulas.
2. Same reduced composition, primitive cells, deduplicated as in `src/isoshift_event/pairs.py` (StructureMatcher ltol 0.2, stol 0.15, angle_tol 5, space-group gate at symprec 0.05; lowest energy entry kept). 14 duplicates merged. Pairs: all representative pairs with |dE| ≤ 50 meV/atom from MP energies. A phase counts as experimentally observed if any MP entry merged into it has theoretical=False.
3. Per structure from the stored MP (DFT) geometry: mean O-H over all donors; mean donor O...O over donors with an acceptor (nearest other O with H...O < 2.6 Å, as in `stretch_check._donors`).
4. Regime: strong if either polymorph has mean O...O ≤ 2.929 Å (`threshold_translation_summary.median_OO_A` in `results/F01_oo.json`).
5. Sign: F01 convention, ddF_iso(b − a) has the sign of dO-H(b − a); deuteration favours the polymorph with the shorter mean O-H (longer mean O...O). The O-H difference sets the call; the O...O difference is the consistency check.
6. Confidence: high (|dO-H| ≥ 5 mÅ and |dO...O| ≥ 0.03 Å, agreeing), medium (one above its cut, the other agreeing or undefined), low (both below), conflict (dO-H and dO...O imply opposite signs; the call still follows dO-H).

Counts: 1796 pairs, 317 formulas; strong 1488, weak 292, undefined 16; 218 pairs with both phases observed, 185 of them strong (122 formulas; confidence high 62, medium 29, low 43, conflict 51). Run time 53 s on one CPU core for the whole set (0.03 s per pair, including deduplication).

Caveats stated before the test: the F01 rule was established on ML-relaxed structures and harmonic free energies, not on DFT database geometry; MP polymorph O-H differences are often a few mÅ, below the 5 mÅ headline eligibility; the rule concerns the vibrational isotope term at fixed structure, so any observed effect that comes from changed proton order, tunnelling or kinetics is outside its scope.

## Exclusion and scoring rule (predeclared, binding for F10)

A literature case is **excluded** from the score, and listed with the reason, if any of these holds:

* **E1 proton disorder or tunnelling.** At least one of the two phases is proton disordered (partial H occupancy, or described as disordered in the source), or the transition is a proton order-disorder, ferroelectric or antiferroelectric ordering transition (for example the KH2PO4 family and its Ubbelohde effect, squaric acid, ice Ih/XI, VII/VIII), or the source attributes the isotope effect to proton tunnelling or to a change of the hydrogen-bond potential from double to single well. This covers ice boundaries that involve Ih, III, V, VI or VII.
* **E2 not a polymorph pair.** The H and D materials differ in composition (hydration number, stoichiometry), or one phase is a different compound.
* **E3 no direction.** The source reports a difference but not which phase deuteration favours (for example only a change in transition width or hysteresis).

Cases that pass are **scored**: right if the phase whose stability field deuteration enlarges (higher transition temperature or pressure out of it, or the phase that forms from D but not from H under the same conditions) is the phase the atlas says deuteration favours. A case maps onto an atlas pair by formula and space group of both phases. If a phase is not in the atlas, its O...O and O-H may be computed with the same `donor_geometry` code from an MP or COD CIF; such cases are scored separately as "mapped by CIF". Thermodynamic observations (equilibrium transition shifts, phase diagrams) are the primary count; crystallisation outcomes (H and D samples crystallising differently from solution or melt) are a secondary count, because nucleation kinetics are outside the rule. Weak-regime cases are reported but not counted (F01 says the rule fails there). Conflict-class pairs are counted, and also reported separately. No baseline beyond a coin flip is claimed; with fewer than ten scored cases the result is anecdotal.

## Predictions: all 185 strong-regime pairs with both phases experimentally observed

Space groups as stored by MP. dO-H in mÅ; "Deuteration favours" names the polymorph with the shorter mean O-H in the MP structure.

| # | Formula | Phase a (spg) | Phase b (spg) | dE b-a (meV/atom) | mean O...O a / b (�) | dO-H b-a (m�) | Deuteration favours | Confidence |
|---|---|---|---|---|---|---|---|---|
| 1 | Al(HO)3 | mp-27540 (P2_1/c) | mp-560196 (P2_1/c) | +12.9 | 2.915 / 2.936 | -3.5 | mp-560196 (P2_1/c) | low |
| 2 | Al(HO)3 | mp-27540 (P2_1/c) | mp-560572 (P2_1/c) | +9.4 | 2.915 / 3.041 | -4.0 | mp-560572 (P2_1/c) | medium |
| 3 | Al(HO)3 | mp-27540 (P2_1/c) | mp-985293 (P2_12_12_1) | +7.8 | 2.915 / 2.754 | +15.4 | mp-27540 (P2_1/c) | high |
| 4 | Al(HO)3 | mp-985293 (P2_12_12_1) | mp-560196 (P2_1/c) | +5.1 | 2.754 / 2.936 | -18.9 | mp-560196 (P2_1/c) | high |
| 5 | Al(HO)3 | mp-985293 (P2_12_12_1) | mp-560572 (P2_1/c) | +1.6 | 2.754 / 3.041 | -19.4 | mp-560572 (P2_1/c) | high |
| 6 | AlH12(NO5)3 | mp-1203296 (C2/c) | mp-699485 (Ia-3) | +4.4 | 2.659 / 2.743 | +7.3 | mp-1203296 (C2/c) | conflict |
| 7 | AlHO2 | mp-625152 (Pnma) | mp-23807 (Pmn2_1) | +41.7 | 2.606 / 2.562 | +32.6 | mp-625152 (Pnma) | high |
| 8 | AlP(H2O3)2 | mp-24045 (Pbca) | mp-24398 (P2_1/c) | +1.7 | 2.732 / 2.777 | -5.5 | mp-24398 (P2_1/c) | high |
| 9 | B(HO)3 | mp-23791 (P-1) | mp-759069 (P3_2) | +2.6 | 2.631 / 2.621 | +0.8 | mp-23791 (P-1) | low |
| 10 | BHO2 | mp-1198592 (P2_1/c) | mp-696403 (Pnma) | +2.7 | 2.624 / 2.678 | -10.1 | mp-696403 (Pnma) | high |
| 11 | BHO2 | mp-1198592 (P2_1/c) | mp-721851 (P-43n) | +5.6 | 2.624 / 2.512 | +48.3 | mp-1198592 (P2_1/c) | high |
| 12 | BHO2 | mp-696403 (Pnma) | mp-721851 (P-43n) | +2.9 | 2.678 / 2.512 | +58.4 | mp-696403 (Pnma) | high |
| 13 | Ba(HO)2 | mp-626973 (P2_1/c) | mp-699501 (P2_1/c) | +12.4 | 2.901 / 3.107 | +0.3 | mp-626973 (P2_1/c) | conflict |
| 14 | Ba(HO)2 | mp-626973 (P2_1/c) | mp-723021 (Pnma) | +24.4 | 2.901 / 3.111 | -4.4 | mp-723021 (Pnma) | medium |
| 15 | BaAsHO4 | mp-23810 (Pbca) | mp-1196910 (P2_1) | +7.9 | 2.547 / 2.643 | -17.2 | mp-1196910 (P2_1) | high |
| 16 | BaGaB4H3O10 | mp-1194652 (P-1) | mp-1195154 (C2/c) | +1.0 | 2.781 / 2.744 | +0.1 | mp-1194652 (P-1) | medium |
| 17 | Ca(HO)2 | mp-23879 (P-3m1) | mp-643392 (P2_1/c) | +35.4 | 3.216 / 2.887 | +9.6 | mp-23879 (P-3m1) | high |
| 18 | Ca3Be2P4(HO2)10 | mp-707876 (P2_1/c) | mp-707838 (P-1) | +0.1 | 2.840 / 2.815 | +0.9 | mp-707876 (P2_1/c) | low |
| 19 | CaAl2Si2(H2O5)2 | mp-24603 (Pna2_1) | mp-505288 (Pnma) | +2.1 | 2.798 / 2.832 | -5.2 | mp-505288 (Pnma) | high |
| 20 | CaAl2Si2(H2O5)2 | mp-24603 (Pna2_1) | mp-733653 (Cmcm) | +4.5 | 2.798 / 2.777 | -14.1 | mp-733653 (Cmcm) | conflict |
| 21 | CaAl2Si2(H2O5)2 | mp-505288 (Pnma) | mp-733653 (Cmcm) | +2.4 | 2.832 / 2.777 | -9.0 | mp-733653 (Cmcm) | conflict |
| 22 | CaAl2Si3H6O13 | mp-707746 (Cc) | mp-1202683 (Cc) | +6.6 | 2.856 / 2.837 | -2.0 | mp-1202683 (Cc) | conflict |
| 23 | CaB2(HO)8 | mp-1199389 (P-1) | mp-721875 (P-1) | +3.1 | 2.820 / 2.742 | -7.2 | mp-721875 (P-1) | conflict |
| 24 | CaB3H5O8 | mp-560899 (P2_1) | mp-705495 (P2_1/c) | +4.4 | 2.811 / 2.780 | -11.5 | mp-705495 (P2_1/c) | conflict |
| 25 | CaFe3Si2HO9 | mp-721924 (P2_1/c) | mp-541023 (Pnma) | +14.2 | 2.641 / 2.696 | -1.4 | mp-541023 (Pnma) | medium |
| 26 | CaH4SO6 | mp-23690 (C2/c) | mp-753183 (C2/c) | +18.9 | 2.778 / 2.935 | +7.0 | mp-23690 (C2/c) | conflict |
| 27 | CaH8(NO5)2 | mp-1202729 (P2_1/c) | mp-559136 (P2_1/c) | +7.2 | 2.846 / 2.824 | -1.9 | mp-559136 (P2_1/c) | conflict |
| 28 | CaH8(NO5)2 | mp-1202729 (P2_1/c) | mp-762501 (P2_1/c) | +8.8 | 2.846 / 2.845 | -2.4 | mp-762501 (P2_1/c) | conflict |
| 29 | CaH8(NO5)2 | mp-559136 (P2_1/c) | mp-762501 (P2_1/c) | +1.6 | 2.824 / 2.845 | -0.5 | mp-762501 (P2_1/c) | low |
| 30 | CaPHO4 | mp-24390 (P1) | mp-1194747 (P2_1/c) | +18.7 | 2.501 / 2.739 | -39.5 | mp-1194747 (P2_1/c) | high |
| 31 | Cd2H2SO6 | mp-558011 (P2_1/c) | mp-634113 (C2/c) | +3.1 | 2.734 / 2.764 | -1.5 | mp-634113 (C2/c) | medium |
| 32 | CeH8(SO6)2 | mp-1196048 (Fddd) | mp-1202113 (Pnma) | +0.6 | 2.770 / 2.680 | -7.4 | mp-1202113 (Pnma) | conflict |
| 33 | CoH2SeO4 | mp-505469 (P2_1/c) | mp-757297 (P2_1/c) | +0.4 | 2.849 / 2.877 | -1.9 | mp-757297 (P2_1/c) | low |
| 34 | CoPH6NO5 | mp-697560 (Pmn2_1) | mp-1202160 (Pnma) | +2.5 | 2.881 / 2.999 | -4.1 | mp-1202160 (Pnma) | medium |
| 35 | CrHO2 | mp-24040 (Pmn2_1) | mp-23910 (R3m) | +6.7 | 2.503 / 2.493 | +3.7 | mp-24040 (Pmn2_1) | low |
| 36 | CrHSe3O8 | mp-1182406 (P2_1/c) | mp-761681 (Pnma) | +6.1 | 2.739 / nan | -23.2 | mp-761681 (Pnma) | medium |
| 37 | CsB5(H2O3)4 | mp-23742 (P2_1/c) | mp-1203003 (C2/c) | +1.2 | 2.736 / 2.750 | -1.5 | mp-1203003 (C2/c) | low |
| 38 | CsHSO4 | mp-1192419 (P2_1/c) | mp-540981 (P2_1/c) | +5.0 | 2.536 / 2.539 | -2.0 | mp-540981 (P2_1/c) | low |
| 39 | CsMnH24(SO10)2 | mp-729644 (Pbca) | mp-746676 (Pa-3) | +8.0 | 2.720 / 2.720 | -0.9 | mp-746676 (Pa-3) | low |
| 40 | CsP(HO2)2 | mp-1188121 (P2_1) | mp-1188838 (P2_1/m) | +1.1 | 2.498 / 2.554 | -5.2 | mp-1188838 (P2_1/m) | high |
| 41 | CsP(HO2)2 | mp-1197651 (P2_1/c) | mp-1188121 (P2_1) | +0.1 | 2.498 / 2.498 | +0.3 | mp-1197651 (P2_1/c) | conflict |
| 42 | CsP(HO2)2 | mp-1197651 (P2_1/c) | mp-1188838 (P2_1/m) | +1.2 | 2.498 / 2.554 | -4.8 | mp-1188838 (P2_1/m) | medium |
| 43 | CsScAs2(HO4)2 | mp-1199276 (P-1) | mp-542557 (P2_1/c) | +3.2 | 2.783 / 2.849 | -4.8 | mp-542557 (P2_1/c) | medium |
| 44 | CsTiH24(SO10)2 | mp-699488 (Pbca) | mp-699489 (Pa-3) | +0.4 | 2.717 / 2.739 | -0.4 | mp-699489 (Pa-3) | low |
| 45 | Cu2PHO5 | mp-510654 (Pnnm) | mp-1200251 (P2_1/c) | +1.7 | 2.874 / 2.858 | +0.1 | mp-510654 (Pnnm) | low |
| 46 | CuH6SO7 | mp-1192826 (Cc) | mp-707170 (Cc) | +1.0 | 2.715 / 2.710 | +2.3 | mp-1192826 (Cc) | low |
| 47 | ErH3(SO4)3 | mp-24640 (Pbca) | mp-765463 (P2_1/c) | +8.2 | 2.810 / 2.751 | +2.0 | mp-24640 (Pbca) | medium |
| 48 | FeP(H2O3)2 | mp-510510 (Pbca) | mp-510511 (P2_1/c) | +2.5 | 2.762 / 2.811 | -5.1 | mp-510511 (P2_1/c) | high |
| 49 | FeP2HO7 | mp-558841 (P2_1/c) | mp-728069 (P2_1/c) | +9.4 | 2.624 / 2.712 | -26.9 | mp-728069 (P2_1/c) | high |
| 50 | GaAs(H2O3)2 | mp-1195440 (Pbca) | mp-1195891 (Pbca) | +20.8 | 2.761 / 2.663 | -7.4 | mp-1195891 (Pbca) | conflict |
| 51 | GaHO2 | mp-634326 (Pnma) | mp-23803 (Pmn2_1) | +14.4 | 2.607 / 2.549 | +20.2 | mp-634326 (Pnma) | high |
| 52 | H13S2N3O8 | mp-541932 (P2/c) | mp-757652 (P-1) | +2.2 | 2.511 / 2.542 | -10.7 | mp-757652 (P-1) | high |
| 53 | H2O | mp-24043 (R-3) | mp-2739191 (C222_1) | +43.9 | 2.696 / 2.679 | +4.9 | mp-24043 (R-3) | low |
| 54 | H2O | mp-24043 (R-3) | mp-696735 (P4_12_12) | +1.1 | 2.696 / 2.674 | +1.8 | mp-24043 (R-3) | low |
| 55 | H2O | mp-24043 (R-3) | mp-697085 (I4_1/amd) | +14.9 | 2.696 / 2.873 | -7.3 | mp-697085 (I4_1/amd) | high |
| 56 | H2O | mp-696735 (P4_12_12) | mp-2739191 (C222_1) | +42.8 | 2.674 / 2.679 | +3.1 | mp-696735 (P4_12_12) | conflict |
| 57 | H2O | mp-696735 (P4_12_12) | mp-697085 (I4_1/amd) | +13.8 | 2.674 / 2.873 | -9.1 | mp-697085 (I4_1/amd) | high |
| 58 | H2O | mp-697085 (I4_1/amd) | mp-2739191 (C222_1) | +29.0 | 2.873 / 2.679 | +12.2 | mp-697085 (I4_1/amd) | high |
| 59 | H2O | mp-697111 (Cmc2_1) | mp-24043 (R-3) | +5.6 | 2.654 / 2.696 | -6.6 | mp-24043 (R-3) | high |
| 60 | H2O | mp-697111 (Cmc2_1) | mp-2739191 (C222_1) | +49.5 | 2.654 / 2.679 | -1.6 | mp-2739191 (C222_1) | low |
| 61 | H2O | mp-697111 (Cmc2_1) | mp-696735 (P4_12_12) | +6.7 | 2.654 / 2.674 | -4.8 | mp-696735 (P4_12_12) | low |
| 62 | H2O | mp-697111 (Cmc2_1) | mp-697085 (I4_1/amd) | +20.5 | 2.654 / 2.873 | -13.9 | mp-697085 (I4_1/amd) | high |
| 63 | H2O | mp-697111 (Cmc2_1) | mp-703459 (P6_3cm) | +1.1 | 2.654 / 2.652 | -0.1 | mp-703459 (P6_3cm) | conflict |
| 64 | H2O | mp-703459 (P6_3cm) | mp-24043 (R-3) | +4.5 | 2.652 / 2.696 | -6.5 | mp-24043 (R-3) | high |
| 65 | H2O | mp-703459 (P6_3cm) | mp-2739191 (C222_1) | +48.4 | 2.652 / 2.679 | -1.6 | mp-2739191 (C222_1) | low |
| 66 | H2O | mp-703459 (P6_3cm) | mp-696735 (P4_12_12) | +5.6 | 2.652 / 2.674 | -4.7 | mp-696735 (P4_12_12) | low |
| 67 | H2O | mp-703459 (P6_3cm) | mp-697085 (I4_1/amd) | +19.4 | 2.652 / 2.873 | -13.8 | mp-697085 (I4_1/amd) | high |
| 68 | H2SO4 | mp-690733 (C2/c) | mp-24172 (P2_1/c) | +1.1 | 2.597 / 2.618 | +1.5 | mp-690733 (C2/c) | conflict |
| 69 | H2SeO3 | mp-27996 (P2_12_12_1) | mp-1102846 (P1) | +7.8 | 2.594 / 2.605 | -4.7 | mp-1102846 (P1) | low |
| 70 | H3NO4 | mp-626256 (Pna2_1) | mp-706430 (Pna2_1) | +41.6 | 2.570 / 2.848 | -15.7 | mp-706430 (Pna2_1) | high |
| 71 | H4Pd(NO4)2 | mp-1193008 (P2_1/c) | mp-1204994 (Pbca) | +1.7 | 2.776 / 2.789 | -3.5 | mp-1204994 (Pbca) | low |
| 72 | H4SO5 | mp-29095 (P2_1/c) | mp-1181245 (P2_12_12_1) | +4.3 | 2.578 / 2.580 | -2.8 | mp-1181245 (P2_12_12_1) | low |
| 73 | H5NO5 | mp-29943 (P2_1/c) | mp-849229 (P2_1/c) | +3.3 | 2.638 / 2.625 | +6.5 | mp-29943 (P2_1/c) | medium |
| 74 | H7SIO10 | mp-849800 (I4_1/a) | mp-766881 (P-1) | +1.0 | 2.735 / 2.777 | -3.1 | mp-766881 (P-1) | medium |
| 75 | HIO3 | mp-23963 (P2_12_12_1) | mp-556216 (Pbca) | +1.8 | 2.717 / 2.683 | -1.0 | mp-556216 (Pbca) | conflict |
| 76 | InP(H2O3)2 | mp-766835 (P2_1/c) | mp-707473 (Pbca) | +3.1 | 2.629 / 2.684 | +0.1 | mp-766835 (P2_1/c) | conflict |
| 77 | K2CoP4(HO2)8 | mp-1195899 (P-1) | mp-758882 (Pnma) | +34.4 | 2.590 / 2.685 | +4.2 | mp-1195899 (P-1) | conflict |
| 78 | K2Cr2AsHO10 | mp-728774 (P3_2) | mp-728030 (P3_1) | +0.0 | 2.541 / 2.513 | -11.2 | mp-728030 (P3_1) | conflict |
| 79 | K2FeH4(SO5)2 | mp-697221 (P-1) | mp-644324 (P-1) | +2.1 | 2.763 / 2.816 | -3.6 | mp-644324 (P-1) | medium |
| 80 | K2MgH8(SO6)2 | mp-699266 (C2/c) | mp-24742 (P2_1/c) | +0.0 | 2.674 / 2.675 | +0.1 | mp-699266 (C2/c) | conflict |
| 81 | K2MnH8(SO6)2 | mp-542145 (P2_1/c) | mp-727702 (C2/c) | +1.5 | 2.701 / 2.716 | -0.9 | mp-727702 (C2/c) | low |
| 82 | K2P2H2O7 | mp-721217 (P-1) | mp-699445 (P2_1/m) | +12.9 | 2.829 / 2.969 | -2.9 | mp-699445 (P2_1/m) | medium |
| 83 | K2TeH6SeO10 | mp-723043 (C2/c) | mp-863010 (Cc) | +0.8 | 2.750 / 2.740 | +0.8 | mp-723043 (C2/c) | low |
| 84 | K3Np(H3O4)2 | mp-1194761 (P2_1/c) | mp-557615 (P2_1/c) | +16.2 | 2.742 / 2.842 | +5.2 | mp-1194761 (P2_1/c) | conflict |
| 85 | K3Pu(H3O4)2 | mp-1237009 (P2_1/c) | mp-554651 (P2_1/c) | +16.6 | 2.743 / 2.834 | +4.9 | mp-1237009 (P2_1/c) | conflict |
| 86 | K4LiH3(SO4)4 | mp-709186 (P4_1) | mp-1196827 (P4_1) | +27.6 | 2.549 / 2.594 | -32.9 | mp-1196827 (P4_1) | high |
| 87 | KAl2P2H5O11 | mp-541870 (P2_1/c) | mp-730945 (P2_12_12_1) | +1.3 | 2.817 / 2.824 | -4.7 | mp-730945 (P2_12_12_1) | low |
| 88 | KFeBP2HO9 | mp-1204854 (P2_1/c) | mp-541794 (P-1) | +12.5 | 2.416 / 3.187 | +2.3 | mp-1204854 (P2_1/c) | conflict |
| 89 | KGdP2H4O9 | mp-24277 (P2_1/c) | mp-1203721 (P2_1/c) | +25.2 | 2.792 / 2.905 | -8.5 | mp-1203721 (P2_1/c) | high |
| 90 | KH(IO3)2 | mp-720407 (P2_1/c) | mp-706273 (Pca2_1) | +0.3 | 2.650 / 2.512 | +27.0 | mp-720407 (P2_1/c) | high |
| 91 | KH3(SeO3)2 | mp-1180593 (P2_1/c) | mp-706579 (Pbcn) | +3.7 | 2.620 / 2.620 | -1.3 | mp-706579 (Pbcn) | low |
| 92 | KP(HO2)2 | mp-1181168 (P2_1) | mp-24262 (P2_1/c) | +4.0 | 2.567 / 2.502 | +19.8 | mp-1181168 (P2_1) | high |
| 93 | KP(HO2)2 | mp-1181168 (P2_1) | mp-24263 (P-1) | +0.2 | 2.567 / 2.506 | -8.0 | mp-24263 (P-1) | conflict |
| 94 | KP(HO2)2 | mp-1181168 (P2_1) | mp-695799 (I-4) | +45.5 | 2.567 / 2.835 | -50.6 | mp-695799 (I-4) | high |
| 95 | KP(HO2)2 | mp-1181168 (P2_1) | mp-699437 (P2/c) | +31.6 | 2.567 / 2.632 | -17.0 | mp-699437 (P2/c) | high |
| 96 | KP(HO2)2 | mp-1181168 (P2_1) | mp-757909 (Cc) | +1.3 | 2.567 / 2.510 | +19.6 | mp-1181168 (P2_1) | high |
| 97 | KP(HO2)2 | mp-23959 (Fdd2) | mp-1181168 (P2_1) | +2.6 | 2.493 / 2.567 | -5.5 | mp-1181168 (P2_1) | high |
| 98 | KP(HO2)2 | mp-23959 (Fdd2) | mp-24262 (P2_1/c) | +6.6 | 2.493 / 2.502 | +14.3 | mp-23959 (Fdd2) | conflict |
| 99 | KP(HO2)2 | mp-23959 (Fdd2) | mp-24263 (P-1) | +2.8 | 2.493 / 2.506 | -13.5 | mp-24263 (P-1) | medium |
| 100 | KP(HO2)2 | mp-23959 (Fdd2) | mp-695799 (I-4) | +48.1 | 2.493 / 2.835 | -56.1 | mp-695799 (I-4) | high |
| 101 | KP(HO2)2 | mp-23959 (Fdd2) | mp-699437 (P2/c) | +34.2 | 2.493 / 2.632 | -22.4 | mp-699437 (P2/c) | high |
| 102 | KP(HO2)2 | mp-23959 (Fdd2) | mp-757909 (Cc) | +3.9 | 2.493 / 2.510 | +14.1 | mp-23959 (Fdd2) | conflict |
| 103 | KP(HO2)2 | mp-24262 (P2_1/c) | mp-695799 (I-4) | +41.5 | 2.502 / 2.835 | -70.4 | mp-695799 (I-4) | high |
| 104 | KP(HO2)2 | mp-24262 (P2_1/c) | mp-699437 (P2/c) | +27.6 | 2.502 / 2.632 | -36.8 | mp-699437 (P2/c) | high |
| 105 | KP(HO2)2 | mp-24263 (P-1) | mp-24262 (P2_1/c) | +3.8 | 2.506 / 2.502 | +27.9 | mp-24263 (P-1) | medium |
| 106 | KP(HO2)2 | mp-24263 (P-1) | mp-695799 (I-4) | +45.3 | 2.506 / 2.835 | -42.6 | mp-695799 (I-4) | high |
| 107 | KP(HO2)2 | mp-24263 (P-1) | mp-699437 (P2/c) | +31.4 | 2.506 / 2.632 | -8.9 | mp-699437 (P2/c) | high |
| 108 | KP(HO2)2 | mp-24263 (P-1) | mp-757909 (Cc) | +1.1 | 2.506 / 2.510 | +27.6 | mp-24263 (P-1) | conflict |
| 109 | KP(HO2)2 | mp-699437 (P2/c) | mp-695799 (I-4) | +13.9 | 2.632 / 2.835 | -33.6 | mp-695799 (I-4) | high |
| 110 | KP(HO2)2 | mp-757909 (Cc) | mp-24262 (P2_1/c) | +2.7 | 2.510 / 2.502 | +0.2 | mp-757909 (Cc) | low |
| 111 | KP(HO2)2 | mp-757909 (Cc) | mp-695799 (I-4) | +44.2 | 2.510 / 2.835 | -70.2 | mp-695799 (I-4) | high |
| 112 | KP(HO2)2 | mp-757909 (Cc) | mp-699437 (P2/c) | +30.4 | 2.510 / 2.632 | -36.6 | mp-699437 (P2/c) | high |
| 113 | KPH3O4F | mp-761185 (P2_1/c) | mp-24214 (P2_1/c) | +2.1 | 2.519 / 2.560 | -6.1 | mp-24214 (P2_1/c) | high |
| 114 | Li2Sn(H5O4)2 | mp-1195757 (P2_1/c) | mp-703343 (P2_1/c) | +6.5 | 2.679 / 2.824 | -5.6 | mp-703343 (P2_1/c) | high |
| 115 | Li3V(H4O3)4 | mp-1201415 (P1) | mp-1198234 (Pc) | +4.2 | 2.680 / 2.716 | -5.1 | mp-1198234 (Pc) | high |
| 116 | LiAlSiH2O5 | mp-697020 (Pna2_1) | mp-1204399 (Pna2_1) | +15.3 | 2.836 / 2.920 | +3.0 | mp-697020 (Pna2_1) | conflict |
| 117 | LiCu2BP2(HO5)2 | mp-1199484 (P2_12_12_1) | mp-1202117 (C2/c) | +15.4 | 2.853 / 3.158 | -7.1 | mp-1202117 (C2/c) | high |
| 118 | LiZnPH2O5 | mp-24585 (Pna2_1) | mp-703550 (Pca2_1) | +0.8 | 2.925 / 2.910 | -4.6 | mp-703550 (Pca2_1) | conflict |
| 119 | Mg2PHO5 | mp-23740 (Pnma) | mp-24079 (P2_1/c) | +5.1 | 2.799 / 2.774 | +7.8 | mp-23740 (Pnma) | medium |
| 120 | Mg3P2(H22O15)2 | mp-698183 (P-1) | mp-706658 (P-1) | +1.1 | 2.780 / 2.785 | +0.6 | mp-698183 (P-1) | conflict |
| 121 | Mg3P2(HO)16 | mp-766572 (C2/c) | mp-24638 (C2/m) | +4.4 | 2.754 / 2.786 | -1.8 | mp-24638 (C2/m) | medium |
| 122 | MgB3H15O13 | mp-706339 (P2_1/c) | mp-24391 (P-1) | +1.1 | 2.815 / 2.809 | +1.4 | mp-706339 (P2_1/c) | low |
| 123 | MgH10SO9 | mp-1200606 (P-1) | mp-24399 (P-1) | +15.4 | 2.775 / 2.849 | +9.4 | mp-1200606 (P-1) | conflict |
| 124 | MgH8(ClO6)2 | mp-865188 (C2/m) | mp-989229 (C2) | +9.1 | 2.841 / 2.907 | +10.1 | mp-865188 (C2/m) | conflict |
| 125 | MgP2(H8O5)2 | mp-24195 (I4_1/acd) | mp-758660 (P4_2/nmc) | +0.3 | 2.755 / 2.773 | -0.1 | mp-758660 (P4_2/nmc) | low |
| 126 | Mn2AsHO5 | mp-1202591 (Pnnm) | mp-765297 (P2_1/c) | +14.4 | 2.867 / 2.951 | +8.2 | mp-1202591 (Pnnm) | conflict |
| 127 | MnAl2P2(HO)18 | mp-504975 (P-1) | mp-759189 (P-1) | +0.4 | 2.833 / 2.797 | -1.2 | mp-759189 (P-1) | conflict |
| 128 | MnH6SO6 | mp-765484 (P2_1/c) | mp-556670 (P2_12_12_1) | +1.1 | 2.787 / 2.859 | +1.6 | mp-765484 (P2_1/c) | conflict |
| 129 | MnHO2 | mp-626270 (Pnma) | mp-29159 (P2_1/c) | +3.2 | 2.609 / 2.588 | +7.7 | mp-626270 (Pnma) | medium |
| 130 | MnPH6NO5 | mp-732315 (Pmn2_1) | mp-1195120 (Pnma) | +1.7 | 2.871 / 2.993 | -2.7 | mp-1195120 (Pnma) | medium |
| 131 | Na2P3HO9 | mp-1193174 (P-1) | mp-978284 (P-1) | +5.1 | 2.458 / 2.524 | -17.9 | mp-978284 (P-1) | high |
| 132 | Na2PH5O6 | mp-720853 (Pbca) | mp-698223 (Pbca) | +29.8 | 2.748 / 2.662 | +7.6 | mp-720853 (Pbca) | high |
| 133 | Na2TiSi4H4O13 | mp-1200866 (P42_12) | mp-733509 (P2_1/c) | +1.1 | 2.910 / 2.698 | -2.8 | mp-733509 (P2_1/c) | conflict |
| 134 | Na2ZnP4(H4O5)4 | mp-1198456 (P2_1/c) | mp-505561 (P2_1/c) | +5.5 | 2.699 / 2.684 | +4.4 | mp-1198456 (P2_1/c) | low |
| 135 | Na3H(SO4)2 | mp-23780 (P2_1/c) | mp-707941 (P1) | +2.0 | 2.421 / 2.445 | +18.6 | mp-23780 (P2_1/c) | conflict |
| 136 | Na3SiH5O6 | mp-703468 (Pbca) | mp-721564 (Pbca) | +8.2 | 2.815 / 2.759 | +1.3 | mp-703468 (Pbca) | medium |
| 137 | Na4NiH38(W3O20)2 | mp-1202939 (P-1) | mp-1237121 (P-1) | +11.6 | 2.817 / 2.837 | -3.2 | mp-1237121 (P-1) | low |
| 138 | NaFeH4SO6F | mp-1193859 (P2_1/m) | mp-1307582 (P2_1/m) | +2.0 | 2.830 / 2.844 | -1.8 | mp-1307582 (P2_1/m) | low |
| 139 | NaH4ClO6 | mp-1192167 (P-1) | mp-1196288 (Pbca) | +2.1 | 2.921 / 2.895 | +0.5 | mp-1192167 (P-1) | low |
| 140 | NaInBP2HO9 | mp-1198616 (P2_1/c) | mp-757312 (P2_1/c) | +13.6 | 2.800 / 2.428 | -2.9 | mp-757312 (P2_1/c) | conflict |
| 141 | NaP(HO2)2 | mp-24109 (P2_1/c) | mp-504944 (P2_1/c) | +31.9 | 2.527 / 2.886 | -40.2 | mp-504944 (P2_1/c) | high |
| 142 | NaP(HO2)2 | mp-24109 (P2_1/c) | mp-697367 (P-1) | +31.9 | 2.527 / 2.824 | -45.8 | mp-697367 (P-1) | high |
| 143 | NaP(HO2)2 | mp-504944 (P2_1/c) | mp-697367 (P-1) | +0.1 | 2.886 / 2.824 | -5.5 | mp-697367 (P-1) | conflict |
| 144 | NaPH4O5 | mp-554288 (Pna2_1) | mp-720825 (P-1) | +24.6 | 2.727 / 2.908 | -18.3 | mp-720825 (P-1) | high |
| 145 | NdH12(NO5)3 | mp-504828 (P-1) | mp-695894 (P-1) | +15.4 | 2.766 / 2.868 | +8.0 | mp-504828 (P-1) | conflict |
| 146 | NdH5(SeO4)2 | mp-24574 (P2_12_12_1) | mp-1195973 (P2_12_12_1) | +15.4 | 2.825 / 2.946 | -4.9 | mp-1195973 (P2_12_12_1) | medium |
| 147 | NiH12(NO6)2 | mp-1194565 (P-1) | mp-733522 (P-1) | +37.2 | 2.840 / 2.841 | -2.7 | mp-733522 (P-1) | low |
| 148 | NiH12SO10 | mp-559054 (P4_12_12) | mp-1197114 (C2/c) | +1.8 | 2.756 / 2.804 | -2.1 | mp-1197114 (C2/c) | medium |
| 149 | NiH12SO10 | mp-559054 (P4_12_12) | mp-695985 (P4_32_12) | +1.4 | 2.756 / 2.763 | -2.3 | mp-695985 (P4_32_12) | low |
| 150 | NiH12SO10 | mp-695985 (P4_32_12) | mp-1197114 (C2/c) | +0.3 | 2.763 / 2.804 | +0.2 | mp-695985 (P4_32_12) | conflict |
| 151 | NiP2H2O7 | mp-1202294 (P2_1/c) | mp-746672 (P2_1/c) | +3.1 | 2.883 / 2.686 | -2.5 | mp-746672 (P2_1/c) | conflict |
| 152 | PH5NO3F | mp-759962 (P2_1/c) | mp-24712 (P-1) | +2.5 | 2.489 / 2.508 | -16.1 | mp-24712 (P-1) | medium |
| 153 | PH9(NO2)2 | mp-1197623 (P2_1/c) | mp-720644 (P2_1/c) | +2.6 | 2.654 / 2.637 | -1.4 | mp-720644 (P2_1/c) | conflict |
| 154 | Rb4LiH3(SO4)4 | mp-1198331 (P4_1) | mp-709066 (P4_3) | +1.0 | 2.537 / 2.574 | -14.9 | mp-709066 (P4_3) | high |
| 155 | Rb4LiH3(SO4)4 | mp-1198331 (P4_1) | mp-709885 (P2_1) | +22.6 | 2.537 / 2.564 | -25.3 | mp-709885 (P2_1) | medium |
| 156 | Rb4LiH3(SO4)4 | mp-709066 (P4_3) | mp-709885 (P2_1) | +21.6 | 2.574 / 2.564 | -10.4 | mp-709885 (P2_1) | conflict |
| 157 | RbH2(IO3)3 | mp-1192404 (P1) | mp-1196732 (P2_1/c) | +0.8 | 2.742 / 2.697 | -0.4 | mp-1196732 (P2_1/c) | conflict |
| 158 | RbH3(SeO3)2 | mp-24022 (P2_12_12_1) | mp-1205457 (P2_12_12) | +49.7 | 2.572 / 2.613 | -23.3 | mp-1205457 (P2_12_12) | high |
| 159 | RbHSO4 | mp-1195896 (P2_1/c) | mp-1197989 (Pc) | +0.1 | 2.579 / 2.588 | +0.5 | mp-1195896 (P2_1/c) | conflict |
| 160 | RbHSO4 | mp-1195896 (P2_1/c) | mp-707377 (Pc) | +27.9 | 2.579 / 2.721 | -12.9 | mp-707377 (Pc) | high |
| 161 | RbHSO4 | mp-1197989 (Pc) | mp-707377 (Pc) | +27.8 | 2.588 / 2.721 | -13.3 | mp-707377 (Pc) | high |
| 162 | RbHSeO4 | mp-696794 (P2_12_12_1) | mp-695829 (P1) | +0.5 | 2.537 / 2.529 | +1.7 | mp-696794 (P2_12_12_1) | low |
| 163 | RbP(HO2)2 | mp-23667 (Fdd2) | mp-643791 (P2_1/m) | +13.4 | 2.496 / 2.558 | -21.2 | mp-643791 (P2_1/m) | high |
| 164 | RbP(HO2)2 | mp-23667 (Fdd2) | mp-703528 (P2_1/c) | +7.1 | 2.496 / 2.522 | -12.4 | mp-703528 (P2_1/c) | medium |
| 165 | RbP(HO2)2 | mp-703528 (P2_1/c) | mp-643791 (P2_1/m) | +6.3 | 2.522 / 2.558 | -8.8 | mp-643791 (P2_1/m) | high |
| 166 | Sr2Sn(HO)8 | mp-1198515 (P2_1/c) | mp-766178 (P2_1/c) | +46.3 | 3.022 / 2.907 | +7.6 | mp-1198515 (P2_1/c) | high |
| 167 | TeAsHO5 | mp-1202171 (P2_1/c) | mp-1203323 (P2_1/c) | +7.2 | 2.619 / 3.083 | -35.4 | mp-1203323 (P2_1/c) | high |
| 168 | TeHO3 | mp-1195796 (Pna2_1) | mp-625630 (Pna2_1) | +26.2 | 2.784 / 3.041 | -8.4 | mp-625630 (Pna2_1) | high |
| 169 | TlP(HO2)2 | mp-1196113 (P-1) | mp-690711 (P2_1/c) | +2.7 | 2.537 / 2.559 | -5.2 | mp-690711 (P2_1/c) | medium |
| 170 | TlP(HO2)2 | mp-697267 (P2_1/c) | mp-1196113 (P-1) | +1.5 | 2.550 / 2.537 | +4.8 | mp-697267 (P2_1/c) | low |
| 171 | TlP(HO2)2 | mp-697267 (P2_1/c) | mp-690711 (P2_1/c) | +4.2 | 2.550 / 2.559 | -0.5 | mp-690711 (P2_1/c) | low |
| 172 | V2Cu3H6O11 | mp-721062 (C2/m) | mp-1204591 (Cc) | +3.7 | 2.843 / 2.850 | -1.4 | mp-1204591 (Cc) | low |
| 173 | V6H2Pb4Se3O26 | mp-1195119 (P2_1) | mp-1196385 (P2_1) | +6.8 | 2.909 / 2.741 | -8.9 | mp-1196385 (P2_1) | conflict |
| 174 | V6H2Pb4Se3O26 | mp-1196049 (P-1) | mp-1195119 (P2_1) | +0.1 | 2.944 / 2.909 | -0.1 | mp-1195119 (P2_1) | conflict |
| 175 | V6H2Pb4Se3O26 | mp-1196049 (P-1) | mp-1196385 (P2_1) | +6.9 | 2.944 / 2.741 | -9.0 | mp-1196385 (P2_1) | conflict |
| 176 | VH10SO10 | mp-1179147 (Pmn2_1) | mp-699251 (Pmn2_1) | +17.7 | 2.729 / 2.705 | +2.3 | mp-1179147 (Pmn2_1) | low |
| 177 | VH10SO10 | mp-721365 (P2_1/c) | mp-1179147 (Pmn2_1) | +3.5 | 2.749 / 2.729 | +0.6 | mp-721365 (P2_1/c) | low |
| 178 | VH10SO10 | mp-721365 (P2_1/c) | mp-699251 (Pmn2_1) | +21.2 | 2.749 / 2.705 | +2.9 | mp-721365 (P2_1/c) | medium |
| 179 | Zn(HO)2 | mp-625830 (P2_12_12_1) | mp-697146 (P2_12_12_1) | +2.4 | 2.685 / 2.687 | -0.6 | mp-697146 (P2_12_12_1) | low |
| 180 | Zn2PHO5 | mp-722516 (P-1) | mp-24004 (Pnnm) | +9.2 | 2.834 / 2.817 | -7.2 | mp-24004 (Pnnm) | conflict |
| 181 | Zn3P2(H2O3)4 | mp-1200806 (Pnma) | mp-706444 (Pnma) | +11.0 | 2.877 / 2.896 | -4.2 | mp-706444 (Pnma) | low |
| 182 | ZnH20S2(NO7)2 | mp-706284 (P2_1/c) | mp-696089 (P2_1/c) | +15.3 | 2.772 / 2.718 | +8.7 | mp-706284 (P2_1/c) | high |
| 183 | ZnH8SO8 | mp-24708 (P2_1/c) | mp-1197363 (P2_1/c) | +12.7 | 2.841 / 2.866 | -1.5 | mp-1197363 (P2_1/c) | low |
| 184 | ZnP2(H4O5)2 | mp-1196989 (P2_1/c) | mp-1200196 (P-1) | +24.0 | 2.600 / 2.882 | -14.4 | mp-1200196 (P-1) | high |
| 185 | ZrH6O3F4 | mp-1201375 (P2_1/c) | mp-706386 (P-1) | +0.6 | 2.767 / 2.723 | +0.7 | mp-1201375 (P2_1/c) | medium |
