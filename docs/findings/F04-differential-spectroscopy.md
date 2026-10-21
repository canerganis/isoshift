# F04. Predeclared differential spectroscopy test of the compensation term: partial support

Protocol: model predictions and decision rules committed and pushed before any band was looked up (`docs/predictions/P02_differential_spectroscopy.md`, v1 6a3064b 20:50, v2 after Astra review da560cf 20:52). Bands sourced by a literature agent afterwards (`data/isoshift/oh_bands.csv`, Bond queries logged). Verdicts apply the v2 rules exactly.

## Pair 1: goethite alpha-FeOOH -> epsilon-FeOOH: SUPPORT
| | measured (Thompson et al. 2020, 10.2138/am-2020-7468; goethite Liu et al. 2013, 10.1016/j.saa.2013.06.102) | model median (mace / orb / mattersim) |
|---|---|---|
| Delta stretch | 2850 (midpoint of the broad 2600 to 3100 band) - 3111 = -261 cm-1 | -273 (-206 / -292 / -273) |
| Delta highest delta OH bend | 1175 - 885 = +290 cm-1 | +195 (+205 / +195 / +192) |
Signs as predicted, both resolved, both inside the factor-3 window -> SUPPORT. An independent ambient spectrum of epsilon-FeOOH (Mashino et al. 2026, 10.1007/s00269-026-01355-x: 2700, 1350) gives -411 and +465, also inside the window.
Caveats: the epsilon-FeOOH stretch is broad and its midpoint is used; epsilon-FeOOH bend assignments are by analogy and DFT in those papers, without a delta/gamma split; the two phases come from different papers.

## Pair 2: diaspore alpha-AlOOH -> delta-AlOOH: INCONCLUSIVE (rule 1)
Kagi et al. 2010 (10.1088/1742-6596/215/1/012052) see no IR O-H stretch above 2500 cm-1 in delta-AlOOH at ambient pressure, so the stretch comparator would have to mix IR (diaspore) and Raman (delta-AlOOH, 2121 to 2748, secondary source); the diaspore bend assignment (1078 cm-1) is secondary. Rule 1 makes this INCONCLUSIVE. For the record only, the numbers point the predicted way: bend 1330 - 1078 = +252 (model +287), stretch about -520 (model -497).

## Overall (v2 rule): partial support
One pair SUPPORT, one INCONCLUSIVE. In the one clean real-crystal pair, the measured O-H stretch drops by the amount the ensemble predicts (-261 vs -273 cm-1) while the O-H bend rises (+290 vs +195): the bend/libration side of the F01 compensation is present in experiment, with the right sign and a magnitude within a factor 1.5. This is a test of the direction and rough size of the compensation term at the Gamma point, not of the full Brillouin-zone free energy.
