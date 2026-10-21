# P05. Blind prediction: H2O to D2O shift of the ice Ih-II boundary (and two secondary ice boundaries)

Written and committed before any measured D2O (or H2O vs D2O) ice phase boundary was looked up. The only experimental facts used are textbook H2O facts: ice Ih, II and III meet near 0.2 GPa and about 240 K, ice II is proton ordered, Ih and III are proton disordered, and ice II is denser than III and Ih. Code: `src/isoshift_event/ice_boundary.py`. Numbers: `results/ice_boundary.json` and `results/ice_boundary.csv` (raw QHA JSON in `results/raw/ice/`, local).

## Question

Ice II is proton ordered, so its harmonic phonons are well defined, and the Ih-II boundary sits at modest pressure (about 0.2 GPa) where measured H2O and D2O boundaries may both exist. Predict the sign and size of the D2O shift of the Ih-II transition pressure at fixed temperature, using the M02 bridge.

## Method

Phases (Materials Project structures, primitive cells): ice II R-3 (mp-24043, 12 H2O), ice XI Cmc2_1 (mp-697111, 4 H2O) as proxy for Ih, ice IX P4_12_12 (mp-696735, 12 H2O) as proxy for III.

1. One QHA volume scan per phase and model at 0 GPa (isoshift.qha via the pool, queue results/queue/ice, GPU memory fraction 0.3): 11 volumes from -8% to +12% of the relaxed static volume, constant-volume relaxations, finite-displacement force constants with one fixed supercell per phase (min_length 10 A, max_atoms 300: XI 216 atoms, II 288, IX 288). The pool's QHA silently shrank the supercell at some volumes after CUDA out-of-memory errors (II and IX). Those volumes were recomputed on the CPU at the fixed supercell (`ice_boundary refc`), so every phase uses a single supercell at all volumes.
2. `ice_boundary collect` (CPU) rebuilds F_vib per volume from the cached force constants with the 3 Gamma acoustic modes removed (M01 (1)) and the four imaginary-mode treatments of validate.py collect (omit, |w|, 2|w|, 3 THz), then fits G(T, P) = min_V [E0(V) + F_vib(V, T) + P V] (phonopy QHA, Vinet) for H and D masses at pressures from -0.2 to 1.0 GPa, T = 0 to 320 K.
3. Per H2O, for a boundary a to b: ddG_iso = [G_D - G_H]_b - [G_D - G_H]_a, dV = V_b - V_a (H values), dP_iso = -ddG_iso / dV at fixed T (M02, first order), dT_iso = ddG_iso / dS at fixed P, and 1000 ln alpha(a - b) = 1000 ddG_iso / (2 k_B T) (M02 full-substitution bridge, n_H = 2).

Models: MACE (medium-mpa-0), ORB (v3 conservative inf mpa), MatterSim (v1.0.0-5M). Imaginary fraction (max over volumes): XI 0.15 / 0.37 / 0.23 %, II 0 / 0 / 0 %, IX 0.02 / 1.75 / 0.08 % (mace / orb / mattersim). All are inside the decision-02 bracketed tier (<= 2%); ORB ice IX is the only one with a wide treatment bracket. Every QHA volume at every reference point lies inside the scanned window.

## Assumptions and their limits

1. XI proxy for Ih. The Pauling configurational entropy of Ih, k_B ln(3/2) per H2O, does not depend on hydrogen mass, so it cancels in ddG_iso, and the isotope shift of the Ih-II boundary is vibrational to first order. The vibrational part of Ih is approximated by ordered XI. Limits: the phonon density of states of disordered Ih is broader than that of XI (librations and O-H stretch especially), and any isotope dependence of the degree of order is ignored. Ih and XI differ by a small ordering enthalpy that shifts the boundary location but not, to first order, its isotope shift.
2. IX proxy for III (secondary boundaries only). Ice III is only partially proton ordered, and its partial order may itself depend on isotope. Boundaries with III are therefore reported as secondary.
3. Harmonic QHA. No explicit O-H anharmonicity, no nuclear quantum effects beyond harmonic zero point. F02 found the same models overestimate the volume isotope effect of ice XI by 4 to 10 times (mace, orb about -0.65 to -0.75 % vs measured -0.075 %; mattersim -0.30 %). The same over-weighting of the O-H stretch could inflate |ddG_iso| here.
4. Model boundary location. All three models put the static energy of ice II far above XI (65 to 85 meV per H2O at the static minima; IX is 41 to 61 meV above XI), so their own Ih-II boundary lies near 2 to 4 GPa (first-order estimate), not at 0.2 GPa, and the root search on -0.2 to 1.0 GPa finds no H boundary. The models also make XI 7 to 9 % too dense (29.7 to 29.9 A^3 per H2O at 0 K, 0 GPa, vs about 32 A^3 for Ih), with O...O = 2.68 A (overbound H bonds). The prediction is therefore made at reference points on the measured H2O boundary (fixed T and P), not at the model boundary: ddG_iso and dV are evaluated at T = 150 to 250 K and P = 0, 0.2, 0.4 GPa. This tests the isotope physics, not the boundary location.
5. Model dV is smaller in magnitude than the real H2O Ih-II volume change (model -3.5 to -5.1 A^3 per H2O). From textbook densities (Ih about 0.92, II about 1.17 g/cm^3, quoted from memory, not looked up) the real dV is near -6.5 A^3, which would scale |dP_iso| down by 0.55 (mace), 0.75 (orb) and 0.77 (mattersim). This is a sensitivity, not part of the prediction.

## Predictions

### Primary: Ih-II boundary (a = Ih via XI, b = II)

dP_iso = P_t(D2O) - P_t(H2O) at fixed T, P = 0.2 GPa; brackets are the min and max over the four imaginary-mode treatments.

| T (K) | mace (MPa) | orb (MPa) | mattersim (MPa) | median |
|---|---|---|---|---|
| 150 | -104 [-104, -104] | -34 [-35, -34] | +2 [+2, +3] | -34 |
| 170 | -109 | -36 | 0 | -36 |
| 190 | -114 | -39 | -4 | -39 |
| 210 | -122 [-122, -122] | -43 [-45, -43] | -8 [-8, -7] | -43 |
| 230 | -130 | -47 | -12 | -47 |
| 250 | -140 [-141, -140] | -52 [-54, -52] | -17 [-17, -17] | -52 |

At 0 GPa and 0.4 GPa the mace and orb values change by 5 to 20 %; mattersim moves by about 5 MPa (same sign except mattersim at 150 K, which is +7 MPa at 0 GPa and -2.5 MPa at 0.4 GPa).

* Predicted sign: negative. Deuteration stabilises ice II relative to Ih, so the D2O Ih-II boundary lies at lower pressure than the H2O boundary. All three models agree at 170 to 250 K; at 150 K mattersim is at zero within 2 to 7 MPa.
* Predicted magnitude: model median -35 to -50 MPa over 150 to 250 K (about -43 MPa at 210 K), model range 0 to -140 MPa. With the real H2O dV (assumption 5) the median would be about -30 MPa.
* Origin (harmonic band split of ddF at 200 K, 0.2 GPa, mace / orb / mattersim, meV per H2O): O-H stretch -9.7 / -7.7 / -7.0, librations +6.8 / +6.2 / +6.9, bend -0.3 / -0.2 / -0.3, translations +0.2 / +0.1 / +0.1. The net shift is a residue of two large opposing terms: the stronger hydrogen bonds of Ih soften its O-H stretch (which favours D in II) and stiffen its librations (which favours D in Ih). The net is 3 to 30 % of either term, so the sign is fragile against the H-bond overbinding that F02 identified.
* Temperature shift at fixed P: not predicted. The model vibrational entropy difference S_II - S_XI is +0.1 to +0.5 k_B per H2O, and with the Pauling term of Ih (-0.405 k_B) the total dS is within the M01 slope guard (|dS| < 0.01 meV/atom/K) at every reference point, so dT = ddG/dS is ill conditioned. The models describe a nearly isobaric Ih-II line; the pressure shift is the well-posed quantity.
* Fractionation (M02 bridge, full substitution): 1000 ln alpha(Ih proxy - II) = -77 / -36 / -7 permil at 210 K, 0.2 GPa (mace / orb / mattersim). D concentrates in ice II. This is the same quantity as dP_iso in other units, not an independent prediction.

### Secondary: boundaries with ice III (IX proxy)

| boundary (a to b) | T, P | dP_iso mace / orb / mattersim (MPa) | sign |
|---|---|---|---|
| Ih-III (b = III) | 250 K, 0.2 GPa | -177 / -34 / -3 | negative, 3 of 3 (mattersim near zero) |
| II-III (a = II, b = III; III is the less dense phase) | 250 K, 0.2 to 0.4 GPa | -76 to -84 / -117 to -145 (treatment bracket to -87) / -83 to -130 | negative, 3 of 3 |

For II-III, ddG_iso = [G_D - G_H]_III - [G_D - G_H]_II is +0.4 to +0.9 meV per H2O: deuteration stabilises II relative to III, so at fixed T the III to II transition on compression moves to lower pressure (the II field grows). Translated to temperature: if III is the high-temperature side of the II-III line in H2O (S_III > S_II), the D2O II-III transition temperature at fixed P is higher. No number is given for dT because the configurational entropy of partially ordered III is not modelled. In all three models the ordering of [G_D - G_H] is II < III < Ih, so D2O enlarges the ice II field at the expense of both neighbours.

Triple point Ih-II-III: since the model Ih-II line is nearly isobaric, the predicted pressure shift of the triple point equals dP_iso(Ih-II) at the triple-point temperature (about -50 MPa median at 230 to 250 K, range -12 to -140 MPa). The predicted temperature shift is positive (the II field grows), sign only, unscored.

## Predeclared comparison rules

Test quantity: the measured difference P_t(D2O) - P_t(H2O) of the Ih-II boundary at fixed T, at a temperature in 150 to 260 K. Prediction: the per-model dP_iso at the reference temperature nearest the measured one, P = 0.2 GPa, omit treatment (treatment brackets are under 3 MPa for Ih-II). Model median = median of mace, orb, mattersim.

* SUPPORT: the measured sign equals the predicted sign in at least 2 of the 3 models, AND the measured magnitude is within a factor 5 of the model median (|measured| between |median|/5 and 5 |median|).
* CHALLENGE: the measured sign is opposite to the sign of the model majority (at least 2 of 3 models), with the measured shift larger than its stated uncertainty.
* INCONCLUSIVE: no measured H2O vs D2O Ih-II boundary; data not at comparable conditions (T outside 150 to 260 K or P outside 0 to 0.4 GPa); H2O and D2O data from different studies whose stated uncertainties exceed the measured difference; or a measured difference within its own uncertainty of zero. A sign match with a magnitude outside the factor 5 window is reported as INCONCLUSIVE with the label "sign agrees, magnitude off".

Data conversions fixed now:
1. If the D2O and H2O boundaries are given as P_t(T) lines or point lists, the shift is taken at common temperatures by linear interpolation, without extrapolation beyond either data range.
2. If only a temperature shift at fixed P is reported for Ih-II, it is converted with the measured H2O slope of the same boundary from the same source: dP = -(dP/dT) dT. If no slope is reported, INCONCLUSIVE.
3. If only the Ih-II-III triple points of H2O and D2O are available, the triple-point pressure shift is compared with dP_iso(Ih-II) at the triple-point temperature under the same rule, labelled "triple-point geometry" (this assumes a nearly isobaric Ih-II line near the triple point).
4. Secondary boundaries (Ih-III, II-III) are scored with the same rule, separately, and do not change the primary verdict. A II-III shift reported as a temperature shift at fixed P is scored by sign only, against the conditional sign stated above.

Expected difficulty stated in advance: the net shift is a cancellation of stretch and libration terms of 6 to 10 meV each; F02 indicates these models overweight the O-H stretch in ice, which in this decomposition pushes ddG_iso negative. A measured shift of opposite sign (D2O boundary at higher pressure) would be read as that bias, not as a failure of the M02 bridge itself.
