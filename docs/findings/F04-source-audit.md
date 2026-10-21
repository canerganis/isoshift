# F04 source audit and P03 band lookup (council 05 actions 2 and 4)

Auditor: sonnet-audit-05, 21 Oct. Bond queries are logged in `logs/bond_queries.jsonl`. New band rows are appended to `data/isoshift/oh_bands.csv`. Full texts were read for Sano-Furukawa 2018 (Europe PMC PMC6195538), Thompson 2020 (NSF PAR copy) and Mashino 2026 (open access PDF and SI). Liu 2013, Kohler 1997 and Chukanov 2021 could not be read in full (paywall or bot gate, not bypassed), so those parts are marked secondary.

## Action 2: what 9.0, 13.4 and 18.1 GPa mean in Sano-Furukawa et al. 2018

All three numbers are confirmed. 9.0 and 13.4 GPa are the proton disorder transition (P21nm to Pnnm) for delta-AlOOH and delta-AlOOD. 18.1 GPa is hydrogen bond symmetrisation, observed for AlOOH only.

* Abstract: "the transition from P21nm to Pnnm at 9.0 GPa ... corresponds to the disorder of hydrogen bond between two equivalent sites across the center of the O...O line."
* Abstract: "Symmetrization of the hydrogen bond is observed at 18.1 GPa, which is considerably higher than the disorder pressure."
* Results, "D/H Isotope effect on phase transition": "the transition pressure was found to be 13.4 GPa in the case of δ-AlOOD, which is 4.4 GPa higher than that of δ-AlOOH."
* Same section: "Under pressures of up to 17.4 GPa, the distribution remained bimodal and did not merge into a single peak in the case of δ-AlOOD." So AlOOD symmetrisation was not reached in the data.
* Discussion: "the disorder transition observed at 9.0 GPa in δ-AlOOH and 13.4 GPa in δ-AlOOD could be interpreted as the dynamically disordered state by the proton tunneling."
* Discussion: "the hydrogen is not centered but dynamically disordered between pressures of 9.0 GPa to at least 15.1 GPa in the case of δ-AlOOH."

Consequence for the card: the isotope-dependent window is 9.0 (H) to 13.4 (D) GPa for the disorder transition. The model roots (8.8 to 10.1 GPa MACE, 13.0 to 14.1 GPa ORB) sit on those numbers, which strengthens the council's out-of-domain caveat. 18.1 GPa is symmetrisation and is not an isotope pair. The ledger should not write "13.4 for symmetrisation".

## Action 4: F04 band audit

### (a) Thompson et al. 2020, epsilon-FeOOH at ambient

Technique: room-temperature IR absorption in a diamond cell, spectrum at ambient pressure (Results, "Infrared and visible absorption spectroscopy"; Fig. 4a lattice and OH-bending region, Fig. 4b OH-stretching region; Fig. 5 bending versus pressure).

* Stretch: "At ambient pressure, the O-H stretching region presents as a broadband feature (2600-3100 cm-1)". No peak position is given and no components are named in the text. The F04 midpoint 2850 is therefore a range midpoint, as the ledger already says.
* Bends: "three distinct absorption bands at 965, 1145, and 1175 cm-1 that were identified as O-H bending vibrations based on comparison to similar structures". Assignment is by analogy (Williams and Guenther 1996, Mashino et al. 2016, Pinney and Morgan 2013). There is no delta/gamma split, as the ledger says. 1175 is the highest of the three.

### (b) Mashino et al. 2026

* The 2700 / ~3200 / 1200 / 1350 values are not ambient values and the text gives no single pressure. They come from compression and decompression IR runs (runs 1 and 3) over roughly 0 to 50 GPa, and the paper says the stretching bands soften up to about 18 GPa. The ambient stretch values are therefore higher than 2700 and 3200. "Independent ambient spectrum" is wrong for Mashino and must be removed. A bend value of 1350 is likewise at unstated pressure, and bends rise with pressure, so the ambient value is lower than 1350.
* 2700 and 3200 are two separate IR bands, not two components of one band: "one distinct band at ~2700 cm-1 and a shoulder at ~3200 cm-1". They are assigned by DFT to the A1 (lower) and B2 (higher) modes. The SI tracks their intensity ratio against pressure (Fig. S4).
* Mashino reads Thompson's ambient spectrum differently from Thompson's own text: they say Thompson described "a single broad band between 2600 and 3400 cm-1" with "broad maxima around 2800-2900 cm-1 and 3300-3400 cm-1" (apparently from Fig. 4b, whose axis runs to 3400). Thompson's text says 2600 to 3100. The discrepancy is real and the figure itself should be checked by eye.
* Bends: "two distinctive bands at ~1200 and ~1350 cm-1", assigned to OH bending by analogy and DFT (1200 is B1; 1350 mixes B2 and A1). Mashino sees nothing at 965 and 1145 in the third run and its highest band (1350) is far above Thompson's 1175. They also cite Kagi 2010 for delta-AlOOH at 0.5 GPa: "~1180 and 1330 cm-1".

### (c) Goethite, Liu et al. 2013

The full text is paywalled. The abstract confirms the sample (synthetic goethite, ATR and FT-IES), the technique and a 3708 cm-1 free-OH band, but contains none of 3111, 885 or 782. These three numbers are not confirmed here. The ledger quote ("bands at 885 and 782 assigned to delta(OH) and gamma(OH)") is also consistent with the standard literature. Independent open evidence: Ruan, Frost and Kloprogge 2002 (abstract) report goethite OH vibrations at 3212-3194, 888-884 and 800-798 cm-1; a dehydration FTIR study quotes the in-plane OH deformation near 890 and the stretch near 3150. So the bend 885 and the gamma band near 800 are robust; the stretch of goethite is 3111 to about 3210 depending on source and on which component is called bulk. A higher goethite stretch makes Delta stretch more negative, so it does not threaten the sign.

### Are the F04 band choices defensible?

* Stretch midpoint 2850: defensible only as a sign test. It lands inside Mashino's reading of the main (lower) component, 2800 to 2900, so it is not an outlier. It is not a measured peak.
* Bend 1175 (highest Thompson band, by analogy) versus goethite delta OH 885: defensible and it is the highest-frequency assigned bend of that spectrum, as rule 1 of P02 v2 asks. Using Mashino's 1350 instead gives +465, still inside the factor 3 window (65 to 585).
* Goethite 3111 for stretch: acceptable but unverified in the paper; 3111 to 3212 is the plausible range.

### Interval of Delta stretch (epsilon-FeOOH minus goethite 3111)

| epsilon-FeOOH stretch taken as | Delta stretch | v2 verdict on stretch |
|---|---|---|
| Thompson text range 2600 to 3100 | -511 to -11 | negative; resolved (|Delta| at least 30) only if the band is below 3081, so -511 to -31; the top 20 cm-1 of the range is INCONCLUSIVE by the 30 cm-1 rule |
| Mashino reading of Thompson's lower maximum, 2800 to 2900 | -311 to -211 | SUPPORT window |
| Mashino 2700 (at pressure, so ambient is higher) | -411 or less negative | SUPPORT window |
| Mashino-reading full band 2600 to 3400 | -511 to +289 | sign reverses if the main band were the upper component (3300 to 3400, Delta +189 to +289), which gives CHALLENGE |

With goethite at 3212 instead, every Delta shifts by -101. Whole-range extremes should be quoted as "-511 to -11" for Thompson's stated range, with the footnote that Mashino's reading of the same figure extends it to +289.

Verdict for the pair: SUPPORT stands under the stated 2600 to 3100 range (all of it except the top 20 cm-1) and under the lower-component reading. It is not robust to a reading where the main band is the upper component, but both papers describe the upper component as the weaker one (Mashino: "shoulder"), so the lower component is the defensible main band. The bend/stretch ratio is 290/261 = 1.11 (Thompson, midpoint) or 465/411 = 1.13 (Mashino, pressure unstated, mixed technique conditions); the model median is 0.71. Changes needed in F04: remove "independent ambient spectrum" for Mashino and say Mashino spectra are at unstated pressure within a compression series; give Thompson's range and the bend source (Fig. 4a); disclose that Mashino reads two maxima where Thompson's text gives one band.

## P03: manganite to groutite (gamma-MnOOH to alpha-MnOOH)

What was found (appended to `oh_bands.csv`):

* Manganite, synthetic, KBr FTIR, Cerâmica 2008 (Brazil), Fig. 4 text: broad OH stretch 2631 cm-1; "peaks at 1083, 1117, 1149 cm-1" assigned to gamma-OH, delta2-OH and delta1-OH. Kohler et al. 1997, as quoted in a feitknechtite report: broad 2500 to 2700 cm-1 stretch (about 2650) and OH bends between about 900 and 1200 cm-1. Libowitzky (conference abstract): manganite powder shows three deformation bands.
* Groutite: only two weak items. Libowitzky abstract: O-H stretch moves "from ~3100, via ~2950, to 2650-2700 cm-1" for manganite and groutite together, so no separate groutite stretch peak. A search snippet of Chukanov et al. 2021 (Minerals 11:969, not opened) says groutite has strong stretching absorption in 1900 to 2900, OH bending/libration at 990 to 1030, and calls the weak 1080 to 1150 bands overtones or combinations, disputing Kohler's assignment. No delta/gamma split and no peak positions that can be checked.

Applying the P03 rules (mirror of P02 v2):

* Manganite comparator: stretch 2631 to 2650, highest delta OH 1149 (delta1).
* Groutite comparator: no assigned main stretch peak that differs from manganite's. With both minerals at 2650 to 2700, Delta stretch lies between about -50 and +70, which straddles the 30 cm-1 resolution limit and zero. The groutite bend is either 990 to 1030 (Delta -119 to -159, if Chukanov's libration/bend band counts) or unassigned.
* Rule 1: a band is missing or disputed (groutite stretch peak not resolved, groutite bend assignment disputed and secondary, only one source for manganite delta/gamma). Result: INCONCLUSIVE.

For the record only, not scored: if the groutite bend were 990 to 1030, the bend shift (-119 to -159) has the predicted sign and exceeds the model median (-49) by a factor 2.4 to 3.2. The stretch shift is at most about +50 to +70 against a model +119, so the measured bend/stretch magnitude ratio would be at least about 2 (not computable with a defined sign for the stretch). The ratio is therefore recorded as not measurable. Obtaining Kohler 1997 or Chukanov 2021 Tables (or RRUFF IR with assignment, bot-gated here) is needed to upgrade this.
