# F07. Ice boundary test: the H2O to D2O shift of the Ih-II boundary against experiment

Verdict on the primary test (Ih-II, triple-point geometry, rule 3 of P05): CHALLENGE, provisional because the measured numbers are secondary. All three models predict the wrong sign. On the secondary boundaries the models get II-III right (sign in 3 of 3, magnitude within a factor 3) and Ih-III wrong (sign opposite in 3 of 3). Both failures involve ice Ih, which we model through ordered ice XI.

## Protocol

Predictions and comparison rules were committed and pushed in `docs/predictions/P05_ice_boundary_blind.md` (bec68d7, 2026-10-22 01:15 +0300) before any measured D2O ice boundary was looked up. A separate Sonnet agent then collected the measured data into `data/isoshift/ice_boundaries_HD.csv` without seeing the predictions. Its Valency Bond queries are in `logs/bond_queries.jsonl` (agent "sonnet-ice-blind"). The comparison below applies the P05 rules unchanged.

## What was measured, and how good it is

No study we could read reports H2O and D2O Ih-II boundary lines side by side. Bridgman (1935, 10.1063/1.1749561) measured the D2O solid-solid transitions in the same apparatus family as his earlier H2O work, but the full text is paywalled. Its abstract says only that the D2O transition lines lie at higher temperatures than the H2O lines. The usable numbers are triple points:

| triple point | H2O (P MPa, T K) | D2O (P MPa, T K) | D2O minus H2O |
|---|---|---|---|
| Ih-II-III | 212.9, 238.45 | 225, 242.15 | +12.1 MPa, +3.7 K |
| II-III-V | 344.3, 248.85 | 347, 251.65 | +2.7 MPa, +2.8 K |
| Ih-III-L | 209.9, 251.165 (IAPWS 2008) | 220.2 to 222.4, 254.415 (Herrig et al. 2018, 10.1063/1.5053993, from Bridgman) | +10.3 to +12.5 MPa, +3.25 K |

Data quality is low. The Ih-II-III and II-III-V values come from a secondary web compilation (Chaplin, LSBU) that does not label them. The agent assigned the D2O label because the other values in that column match Herrig's uncorrected Bridgman D2O triple points to within 0.2 K. There are no stated uncertainties for these two triple points. The same compilation also lists the H2O Ih-II-III point as 209.9 MPa, 239.0 K, which would make the pressure shift +15.1 MPa. Bridgman's pressure scale is about 1% low (Herrig's correction factor 1.0102). If both isotopes share that scale, the error cancels in the difference. The Ih-III-L row is better documented, with a 3% equation uncertainty on each side. It gives an independent shift of the same size and sign for a boundary next to Ih.

## Primary test: Ih-II

Rule 3 of P05 applies, because only triple points are available. The measured triple-point pressure shift, about +12 MPa (+15 MPa with the alternative H2O value), is compared with the predicted Ih-II shift at fixed T near 240 K and 0.2 GPa:

| model | predicted dP_iso at 230 to 250 K (MPa) | measured | sign |
|---|---|---|---|
| mace | -130 to -140 | +12 to +15 | opposite |
| orb | -47 to -52 | +12 to +15 | opposite |
| mattersim | -12 to -17 | +12 to +15 | opposite |

The sign is opposite in 3 of 3 models, so the rule gives CHALLENGE. The measured shift (12 MPa) is four times the 3 MPa spread between the two H2O values. It also agrees in sign and size with the better-documented Ih-III-L shift.

Triple-point geometry. Rule 3 assumes that the triple-point pressure shift equals the Ih-II shift at fixed T. If instead the whole Ih-II line moves +3.7 K in temperature, the shift at fixed T is +12 MPa minus s x 3.7 K, where s = dP/dT of the Ih-II line. The sign survives unless s exceeds about 3.3 MPa/K. A Clapeyron estimate dominated by the Pauling entropy (dS about -3.4 J/mol/K, dV about -3.9 cm^3/mol) gives s near 0.9 MPa/K. That estimate uses textbook H2O values that were not looked up, and was made after the data were read. On this basis the fixed-T Ih-II shift is plausibly +8 to +12 MPa, still positive. The measured Ih-III line, with slope -0.2 to -0.4 MPa/K, gives +12.5 MPa at fixed T (below), which is consistent.

In M02 terms, the measured sign means that deuteration stabilises Ih relative to II. With dV of about -6.5 A^3 per H2O, ddG_iso(II - Ih) is about +0.5 meV per H2O, and 1000 ln alpha(Ih - II) is about +12 permil at 240 K: D prefers Ih. The models give -0.2 to -3.1 meV per H2O and -7 to -77 permil.

## Secondary tests

* II-III (no Ih involved). The measured II-III line is the straight line between the Ih-II-III and II-III-V triple points, with slope 12.6 MPa/K for H2O and 12.8 MPa/K for D2O. At fixed T in 242 to 249 K it lies 33 to 35 MPa lower in D2O. Predicted: -70 to -145 MPa, median -74 to -106 MPa, all three models negative. The sign agrees in 3 of 3 models, and the magnitude is within a factor of 2 to 3 of the median, inside the factor-5 window. By the P05 rule this is SUPPORT, with low-quality data (secondary, inferred isotope label, a line through two points). The conditional temperature sign also agrees: the D2O II-III transition sits about 2.6 K higher at fixed P.
* Ih-III. The measured line runs from the Ih-II-III point to the Ih-III-L point. At 245 K it is 12.5 MPa higher in D2O. Predicted: -177 / -34 / -3 MPa (mace / orb / mattersim). The sign is opposite in 3 of 3 models, so this is CHALLENGE. Mattersim is within 3 MPa of zero.

## Reading

The model ensemble gets the isotope ordering right for the two ordered or nearly ordered high-pressure phases (D favours II over III) and wrong whenever ice Ih is involved (the models say D favours II and III over Ih, but experiment says the opposite). Two explanations are consistent with that pattern, and this test cannot separate them.

1. Overbound hydrogen bonds in the Ih proxy. In all three models ice XI is 7 to 9% too dense, with O...O of 2.68 A against about 2.75 A in real Ih. In the band split, the predicted Ih-II shift is a residue of an O-H stretch term (-7 to -10 meV per H2O) and a libration term (+6 to +7 meV). Overbinding exaggerates the stretch red shift in XI, which is the term that pushes ddG negative. A stretch term about 15% (mattersim) to 35% (mace) smaller would flip the sign. This is the same bias F02 found in the volume isotope effect of ice, which is overestimated 4 to 10 times. The ranking also matches: mattersim has the smallest F02 ice error and the smallest Ih-II error here.
2. The XI proxy itself. The isotope shift of a disordered phase is not the shift of its ordered analogue. Proton disorder broadens the libration and stretch bands of Ih and changes the bond-length distribution. Any isotope dependence of the configurational term is also ignored, though it is zero for ideal Pauling disorder. Ice III (IX proxy) is partly disordered too, and the II-III test passed. That argues the proxy is not the main problem, but it is one data point.

What the test does not show: it does not test the M02 bridge as an identity. The bridge was applied correctly, and the error sits in the model ddG_iso. Nor does it test the model boundary location, which is off by 2 to 4 GPa in all three models. P05 deliberately evaluated the shift at the measured H2O conditions.

## Status

Primary Ih-II: CHALLENGE (provisional; the triple-point data are secondary with an inferred D2O label and no stated uncertainty; triple-point geometry assumed, with a plausible slope keeping the sign). Secondary II-III: SUPPORT (low-quality data). Secondary Ih-III: CHALLENGE. A firm verdict needs Bridgman's 1935 D2O Ih-II line (full text) or a modern same-apparatus measurement.

Files: `src/isoshift_event/ice_boundary.py`, `results/ice_boundary.json`, `results/ice_boundary.csv`, `docs/predictions/P05_ice_boundary_blind.md`, `data/isoshift/ice_boundaries_HD.csv`.
