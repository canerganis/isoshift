# P04 comparison rule (written before any prediction was compared with a measurement)

Predictions: `docs/predictions/P04_fractionation_blind.csv` (committed before the fractionation data were read). Measurements: `data/isoshift/fractionation_HD.csv`. Nothing in this file was changed after the comparison was computed.

## Test quantity

Water cancels in mineral-mineral differences. For minerals A and B at temperature T:

    measured:   Delta(A,B,T) = 1000 ln alpha(A-water) - 1000 ln alpha(B-water)
    predicted:  Delta(A,B,T) = 1000 ln beta_A(T) - 1000 ln beta_B(T)

1000 ln beta is the harmonic reduced partition function ratio per H from the blind file. The prediction for each mineral is the median over the three models (MACE, ORB, MatterSim) at each computed temperature, with the min-max over models as the spread. The predicted difference is the median beta of A minus the median beta of B, with a min-max band built from the per-model differences (each model's own A minus B). Predictions are interpolated linearly in 1/T^2 between the computed temperatures (25, 100, 200, 300, 400 C). No anharmonic correction is applied. Harmonic beta of O-H minerals is known to be biased (anharmonic O-H stretch, no tunnelling or proton disorder), so a constant offset per mineral is possible; differences should carry the ordering and the magnitude, not the absolute level.

## Structure mapping

brucite = mp-30247, goethite = mp-605437, manganite = mp-29159. Gibbsite: the only entry in the comparison is excluded unless a structure in `data/isoshift/structures.csv` is identified as gibbsite. Identification criterion: primitive cell of 56 atoms (Z = 8, P2_1/n type, reduced cell near a 8.7, b 5.1, c 9.7 A, beta 94.5 deg, two octahedral layers per cell). Gibbsite is not in the blind set if no such structure was predicted; in that case it is excluded and no substitute (for example a 28-atom polymorph) is used.

## Measured values used, and what is excluded

Used (experiments only):
- goethite: 1000 ln alpha = 1000 ln(0.905) = -99.8 permil, constant for 25 to 145 C (Yapp 1987, 2001), uncertainty from alpha 0.905 +/- 0.004, i.e. +/- 4.4 permil.
- brucite: 1000 ln alpha = -4.88e6/T^2 - 22.5 (T in K), valid 15 to 120 C only (Xu and Zheng 1999, as recorded in the data file with a verify flag). No stated uncertainty.
- manganite: alpha = 0.7894 (150 C), 0.7958 (200 C), 0.8078 (250 C) (Hariya and Tsutsumi 1981), converted to 1000 ln alpha by me; only these three temperatures, no equation.
- brucite at 250 C: DeltaD(brucite - 0.5 kb 3.2 wt% NaCl solution) = -32 permil, converted as 1000 ln(1 + Delta/1000). This is a mineral-salt-solution value at pressure, not a calibrated water equation. It is used only for the brucite-manganite pair at 250 C and is labelled weak. Uncertainty taken as +/- 5 permil (salt effect up to +4, pressure effect up to +12 at 380 C and 0.8 GPa, which is larger than at 0.05 GPa).

Not used as measurements: all rows with method `theory` (Asaduzzaman and Ganguly, Meheut et al., Reynard and Caracas, Gao and Liu), the Sultan 2015 goethite value at 70 C (snippet only, flagged outlier; reported as a sensitivity only), natural goethites with postulated source water (0.968, 0.971), the 22 C goethite value (below the lowest computed temperature, 25 C), brucite pressure-effect rows (differences, not factors), gibbsite (excluded as above), and the mineral dD rows of natural manganite and groutite.

## Temperatures and pairs

Use only temperatures where both minerals have a measured value or a calibrated equation valid at that T, and which lie inside the computed range 25 to 400 C. No extrapolation outside stated validity.

- brucite - goethite: overlap of 15 to 120 C and 25 to 145 C. Evaluated at 25, 50, 75, 100 and 120 C. These five points are smooth functions of T and are not independent.
- goethite - manganite: goethite validity ends at 145 C and manganite starts at 150 C. No admissible overlap. Not scored. A sensitivity at 150 C (holding goethite constant, 5 C beyond its stated validity) is reported separately and is excluded from all scores.
- brucite - manganite: one point, 250 C, using the weak brucite value above. Scored, but flagged weak.

## Scores

(i) Sign agreement of Delta for each scored mineral pair (brucite-goethite, brucite-manganite). A sign is counted as wrong if the sign of the median predicted Delta differs from the measured one. Also reported: sign of each individual model, and whether the measured Delta is within its stated uncertainty of zero.

(ii) Rank order of minerals. Where two or three minerals share a common T, rank by predicted median 1000 ln beta and by measured 1000 ln alpha. No temperature has all three minerals admissible (brucite is valid to 120 C, manganite starts at 150 C), so a three-mineral order is only inferred transitively from the two scored pairs and is labelled as such, not as an independent test.

(iii) Slope and Pearson r of predicted Delta (y) against measured Delta (x), over all scored points (brucite-goethite at 5 temperatures, brucite-manganite at 250 C), ordinary least squares with intercept, plus the through-origin ratio. Because the five brucite-goethite points are nearly collinear in T, the effective number of independent points is two or three and r is not a significance test. The same statistics are repeated with the excluded sensitivity points added, labelled as such.

Interpretation thresholds fixed in advance: "quantitative agreement" needs slope between 0.5 and 2 and r above 0.9; "ordering only" means signs and ranks agree but the slope is outside 0.5 to 2; otherwise "not supported".
