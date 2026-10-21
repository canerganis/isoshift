# F02. Blind test of volume isotope predictions (P01) against measured H/D crystal data

**Status: tested (prediction-first, P01 committed in 0fffc54 before the measured rows were read). Result mixed; F02 does not test F01 (decision 04).**

Protocol: predictions in `docs/predictions/P01_volume_isotope_blind.csv` were committed and pushed at 2026-10-21 20:27:19 +0300 (0fffc54) before the conductor opened the measured rows that two literature agents had written to `data/isoshift/validation.csv` (agents were told to give no numbers in their replies; data committed unread in 3bb0ea4). Prediction method = gate validation method (Gamma-free QHA, four imaginary-mode treatments), mace and orb, 300 K.

Measured values come from CIF cell volumes of H and D compounds. None of the new pairs has a confirmed common temperature, several are cross-lab; the agents flagged them "NOT COMPUTED" for that reason. The comparison below computes V_H/V_D - 1 anyway and states the data quality.

| Compound (phase, our structure) | Measured V_H/V_D - 1 | Predicted mace / orb | Sign | Data quality |
|---|---|---|---|---|
| alpha-AlH3 (R-3c, mp-23933) | +1.08% (Turley and Rinn 1969, 10.1021/ic50071a005) | +1.62 / +1.43% | right, 1.3 to 1.5x too large | same paper, T not stated (room T presumed), 1969 |
| alpha-GaOOH (Pnma diaspore type, mp-634326) | +0.39% (cross-lab, DOIs unresolved, H 293 K) | -0.16 / n.a. | wrong | cross-lab, low |
| beta-CrOOH (P2_1nm, mp-24040) | +0.06% (10.1016/0022-4596(76)90180-8) | -0.27 / n.a. | wrong | same paper, T not stated; very short near-symmetric H bond, axis effects cancel |
| alpha-CrOOH (R-3m, H disordered; our R3m mp-23910) | -1.21% (10.1016/0022-4596(77)90130-x) | -0.27 / n.a. | right | H disordered in experiment, outside harmonic model |
| Be(OH)2 (P2_12_12_1) | -0.03% | not yet computed | | difference within experimental error |
Earlier, gate-quality targets: brucite +0.31% (pred +0.19 to +0.44, 4/4 sign right), LiH +0.81 or +1.04% (pred +1.02 to +1.27, 4/4), ice XI -0.075% (pred -0.29 to -0.80, sign right, 4 to 11x too large).

## Pattern
* Hydrides without H bonds (LiH, alpha-AlH3): sign right, magnitude about 1.3 to 1.5x too large in every model.
* Weak H bonds (brucite): right sign and magnitude.
* Strong, short H bonds (diaspore-type GaOOH, beta-CrOOH): the models predict a negative, ice-like volume isotope effect; the measurements are positive (low-quality data). Ice: right sign, 4 to 11x too large.
* Reading: the universal MLIPs over-weight the negative-Gruneisen O-H stretch contribution in H-bonded crystals (consistent with the 7% H-bond overbinding seen for ice XI in decision 01).

## Why this matters for F01
F01's slope is carried by the X-H stretch term in H-bonded compounds. If the MLIPs overbind H bonds, the stretch frequency versus X-H length slope (and therefore the F01 slope) could be exaggerated. The test is to compare the ensemble's stretch-frequency versus O-H length relation with the empirical spectroscopic correlation for real hydroxides (e.g. Libowitzky 1999, Mineral. Mag./Monatsh. Chem.) and to check whether the F01 sign rule depends on stretch magnitude or only on its direction.

## Statement adopted (decision 04)
Prediction-first volume-isotope comparisons show mixed transferability: alpha-AlH3 has the correct sign with a 1.3 to 1.5x overestimated magnitude; GaOOH and beta-CrOOH disagree in sign with references of limited comparability. Earlier brucite and LiH checks reproduce the measured sign, while ice shows a large quantitative error. The misses lie in the strong-H-bond regime, where harmonic quasi-harmonic treatment omits Ubbelohde-type proton anharmonicity. These results do not identify a unique failure mechanism. F02 does not test F01: it passed where F01 has no skill and missed where F01 applies.
