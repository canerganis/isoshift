# P02. Predeclared differential O-H spectroscopy test of the F01 compensation term (decision 04, item 5, step A)

Written and committed before any measured band position for these phases was looked up. Model numbers: `docs/predictions/P02_spectro_model.csv` (`src/isoshift_event/spectro.py`, Gamma point, H-projected, harmonic).

## What is tested
F01 says the isotope shift between polymorphs is a stretch term half cancelled by bend/libration. Its spectroscopic signature for a pair where polymorph b has the stronger hydrogen bond: the O-H stretch goes down and the O-H bends go up. F03 already checked the stretch against measured spectra; this test targets the bends, i.e. the compensation term.

## Pairs and model predictions (b minus a, cm^-1; mace / orb / mattersim)
| pair (a -> b) | stretch | in-plane bend (delta OH) | out-of-plane bend (gamma OH) | d(O...O) change |
|---|---|---|---|---|
| diaspore alpha-AlOOH (mp-625152) -> delta-AlOOH (mp-23807) | -484 / -480 / -408 | +193 / +184 / +180 | +131 / +96 / +95 | -61 to -92 mA |
| goethite alpha-FeOOH (mp-605437) -> epsilon-FeOOH (JVASP-92228, Pmn2_1) | -204 / -285 / -266 | +151 / +143 / +132 | +71 / +56 / +66 | -36 to -53 mA |

Excluded before looking at data: diaspore -> boehmite with JVASP-12038 as boehmite. In that ordered model the acceptor O is 0.58 to 0.74 A further away and the model stretch is about 3700 cm^-1, i.e. the H bond of real boehmite is missing from the structure model. Comparing it with measured boehmite spectra would test the structure file, not the physics.

## Predeclared outcomes (per pair; measured values must be assigned bands of the same technique, room temperature, from the literature)
* SUPPORT: measured stretch shift is negative AND at least one assigned OH bend shift is positive, with each measured shift within a factor 2.5 of the model ensemble median, allowing a +/-150 cm^-1 bracket for harmonic vs fundamental (anharmonicity) on the stretch.
* CHALLENGE: reliable assigned spectra show the bend shifts are negative or zero within 30 cm^-1 while the stretch drops (compensation absent), or the stretch shift is positive.
* INCONCLUSIVE: bend assignments missing or disputed, different techniques or phases not matched, or delta-AlOOH/epsilon-FeOOH spectra only at high pressure without an ambient-pressure value.
Overall: the compensation term is supported if both pairs are SUPPORT, or one SUPPORT and one INCONCLUSIVE; challenged if any pair is CHALLENGE.

## Caveats stated in advance
Harmonic frequencies vs anharmonic fundamentals; delta-AlOOH has a very short H bond (proton may be delocalised at pressure, decision 03 negative-control class), so its stretch may be broad; epsilon-FeOOH is a high-pressure phase that can be quenched. Bands of the two phases may come from different papers.


## v2 (after Astra review of step A, still before any band lookup)
Astra (gpt-6-astra, high) returned "fix first": periodic acceptor search, compare peak modes not projection means, mutually exclusive rules, boehmite exclusion by a structure check. Changes:
* Acceptor = nearest periodic O image with H...O <= 2.6 A and O-H...O >= 110 deg (pymatgen neighbour search). Boehmite exclusion confirmed structurally: JVASP-12038 has no such acceptor for any H, so the ordered model lacks the H bond of real boehmite.
* delta-AlOOH and epsilon-FeOOH have near-linear O-H...O (175 to 178 deg), so the in-plane/out-of-plane split is ill-defined there. The comparator is the highest-frequency assigned O-H bending band (delta OH) of each phase, and the model value is the dominant Gamma mode with the largest in-plane bend projection.
* Model predictions used for the test (dominant Gamma modes, b minus a, mace / orb / mattersim; medians in brackets):
  * diaspore -> delta-AlOOH: stretch -498 / -497 / -415 (-497); delta OH bend +299 / +287 / +251 (+287)
  * goethite -> epsilon-FeOOH: stretch -206 / -292 / -273 (-273); delta OH bend +205 / +195 / +192 (+195)

Decision rules v2 (mutually exclusive, applied per pair to measured Delta = b minus a; stretch = main O-H stretching band, bend = highest-frequency assigned delta OH band; same technique for both phases where possible):
1. INCONCLUSIVE if either measured band is missing, unassigned or disputed, if the two phases were measured under incompatible conditions (one only at high pressure), or if |Delta stretch| < 30 or |Delta bend| < 30 cm^-1 (unresolved).
2. otherwise CHALLENGE if Delta stretch > 0, or if Delta bend < 0 (compensation reversed).
3. otherwise SUPPORT if |Delta stretch + 150 bracket| and |Delta bend| are both within a factor 3 of the model medians above (stretch compared as |Delta_meas| between |median|/3 - 150 and 3 |median| + 150).
4. otherwise PARTIAL (signs as predicted, magnitude outside the factor-3 window).
Overall: both pairs SUPPORT -> compensation supported; any CHALLENGE -> challenged; any other combination with at least one SUPPORT or PARTIAL -> partial support; both INCONCLUSIVE -> untested. The factor 3 reflects the harmonic vs fundamental gap for strongly H-bonded O-H (stretch fundamentals can sit several hundred cm^-1 below harmonic values) and mode mixing at Gamma; it is a generous window by design, because the test is about the direction of the bend shift.
