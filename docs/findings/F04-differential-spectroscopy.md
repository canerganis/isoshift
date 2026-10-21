# F04. Predeclared differential spectroscopy test of the compensation term: sign-level consistency, one pair

**Status: tested (predeclared in P02/P03 before band lookup). Sign-level consistency on one pair, two pairs inconclusive (decision 05).**

Protocol: model predictions and decision rules committed and pushed before any band was looked up (`docs/predictions/P02_differential_spectroscopy.md`, v1 6a3064b 20:50, v2 after Astra review da560cf 20:52). Bands were sourced by a literature agent afterwards (`data/isoshift/oh_bands.csv`, Bond queries logged) and audited in `docs/findings/F04-source-audit.md`. Verdicts apply the v2 rules.

## Conclusion (decision 05 sentence)

In one predeclared literature pair (goethite to ε-FeOOH) the O-H stretch falls and the assigned O-H bend rises, as predicted: nominal shifts are about -260 cm⁻¹ (from the midpoint of a 2600 to 3100 cm⁻¹ band, so anywhere from -511 to -11 cm⁻¹) against -273 predicted, and +290 against +195 cm⁻¹. The diaspore to δ-AlOOH pair was inconclusive. This is consistent with the sign of the compensating bend shift at the zone centre, not a measurement of its size or of the compensation fraction; the measured bend/stretch shift ratio (about 1.1) exceeds the model median (0.7).

## Pair 1: goethite α-FeOOH to ε-FeOOH: SUPPORT (sign level)

| | measured | model median (mace / orb / mattersim) |
|---|---|---|
| Delta stretch | 2850 (midpoint of the broad 2600 to 3100 band) minus 3111 = -261 cm⁻¹ | -273 (-206 / -292 / -273) |
| Delta highest δ(OH) bend | 1175 minus 885 = +290 cm⁻¹ | +195 (+205 / +195 / +192) |

Sources: ε-FeOOH from Thompson et al. 2020 (10.2138/am-2020-7468), ambient-pressure IR; stretch from Fig. 4b, bends from Fig. 4a. Goethite bands (3111, 885) are attributed to Liu et al. 2013 (10.1016/j.saa.2013.06.102). That paper is paywalled and the numbers are unconfirmed.

Interval on the stretch. Thompson give a broad band over 2600 to 3100 cm⁻¹ and no peak position, so 2850 is a range midpoint. Against goethite 3111, Delta stretch spans -511 to -11 cm⁻¹ over that range. It is resolved (at least 30 cm⁻¹) for -511 to -31; the top 20 cm⁻¹ of the range would be inconclusive by the 30 cm⁻¹ rule. Mashino et al. 2026 read the same figure as two maxima near 2800 to 2900 and 3300 to 3400; if the upper component were the main band the stretch sign would reverse (Delta +189 to +289) and the pair would be a CHALLENGE. Both papers call the upper component the weaker one, so the lower component is taken as the main band, but this is a reading choice and not a measurement.

Robustness to the goethite source. Ruan, Frost and Kloprogge 2002 report goethite OH bands at 3194 to 3212, 884 to 888 and 798 to 800 cm⁻¹. With those: Delta stretch is -344 to -362 at the 2850 midpoint (-594 to -94 over the full 2600 to 3100 range), and Delta bend is +287 to +291. Signs are unchanged, the stretch window stays resolved, and both shifts stay inside the factor-3 window.

Mashino et al. 2026 (10.1007/s00269-026-01355-x) is not an ambient measurement. Its values (2700, 3200, 1200, 1350) come from compression and decompression IR runs over roughly 0 to 50 GPa at unstated pressure, and the stretching bands soften up to about 18 GPa. 2700 and 3200 are two separate bands (a band and a shoulder), not one. Using 2700 and 1350 as a loose cross-check gives -411 and +465, but ambient values would be higher for the stretch and lower for the bend, so this is not a second ambient measurement.

Bend/stretch shift ratio, measured: 290/261 = 1.11 (Thompson, midpoint) and 465/411 = 1.13 (Mashino, pressure unstated, nominal). Model: 0.99 / 0.67 / 0.70, median 0.71. The measured ratio is above the model median.

## Disclosure on the rules

P02 v2 dropped the net-sign criterion from decision 04 before any band was looked up. Under decision 04 a net-sign test would also have been scored. The v2 verdict uses the stretch and bend signs and the factor-3 window only, so SUPPORT here means the two signs and rough sizes agree, not that the net compensated shift was tested.

## Pair 2: diaspore α-AlOOH to δ-AlOOH: INCONCLUSIVE (rule 1)

Kagi et al. 2010 (10.1088/1742-6596/215/1/012052) see no IR O-H stretch above 2500 cm⁻¹ in δ-AlOOH at ambient pressure, so the stretch comparator would mix IR (diaspore) and Raman (δ-AlOOH, 2121 to 2748, secondary source). The diaspore bend assignment (1078 cm⁻¹) is secondary. Rule 1 makes this INCONCLUSIVE. Unscored: bend 1330 minus 1078 = +252 (model +287), stretch about -520 (model -497).

## Pair 3 (P03): manganite γ-MnOOH to groutite α-MnOOH: INCONCLUSIVE (rule 1)

Predeclared in `docs/predictions/P03_differential_spectroscopy.md` (mirrored signs: stretch up, bend down; model +119 and -49 cm⁻¹). Manganite has assigned bands (stretch about 2631 to 2650, highest δ(OH) 1149). Groutite has no assigned bands: no separate stretch peak is resolved from manganite's, and the bend assignment is disputed and secondary. Rule 1 gives INCONCLUSIVE. The bend/stretch ratio is not measurable. Kohler 1997 or the Chukanov 2021 tables would be needed to upgrade it.

## Overall

One pair at sign-level consistency, two inconclusive. This tests the direction of the bend shift at the Gamma point against one literature pair, not the size of the compensation or the full Brillouin-zone free energy.
