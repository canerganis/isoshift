# Candidate card (GOAL S7): deuteration and the diaspore to delta-AlOOH boundary

**Status: exploratory sign prediction outside the harmonic domain (decision 05).**

**Statement.** Exploratory harmonic/QHA prediction at 300 K: deuteration raises the diaspore to δ-AlOOH transition pressure by +1.13 GPa (ORB) and +1.33 GPa (MACE), using one linear fit through 10, 15 and 20 GPa for both isotopes (the MACE H root is extrapolated below 10 GPa), and by +0.3 to +0.4 GPa from 0 GPa geometries. The two models place the boundary 4.2 GPa apart but agree on the shift. The sign is the prediction; neither the size nor the sign is validated. δ-AlOOH undergoes isotope-dependent proton disorder in the same pressure window, which harmonic physics omits, and the boundary is crossed experimentally at high temperature, beyond the 300 K calculation.

**System.** AlOOH: diaspore (alpha-AlOOH, Pnma, mp-625152) and delta-AlOOH (P2_1nm, mp-23807). Both phases are real; delta-AlOOH is a high-pressure phase, quenchable to ambient, discussed as a water carrier in the deep mantle. Deuterated delta-AlOOD is the sample used for high-pressure neutron diffraction (Sano-Furukawa et al. 2018, 10.1038/s41598-018-33598-2), so an isotope shift of the boundary matters to the people who measure it.

**Numbers.** At 0 GPa geometry (harmonic, 300 K): ddF_iso (delta minus diaspore) = +0.52 / +0.77 / +0.83 meV/atom (MatterSim / MACE / ORB); dV = -0.30 to -0.32 A^3/atom; -ddF/dV = +0.28 to +0.42 GPa. QHA Gibbs energies at 10, 15, 20 GPa (`results/card_alooh_pressure.json`, one linear fit for both isotopes):

| model | P_t AlOOH | P_t AlOOD | dP_iso |
|---|---|---|---|
| MACE | 8.76 GPa (extrapolated below 10 GPa) | 10.09 GPa | +1.33 GPa |
| ORB | 13.00 GPa | 14.13 GPa | +1.13 GPa |

Mechanism as in F01: delta-AlOOH has the stronger H bond (O-H longer by 24 to 32 mA, O...O shorter by 60 to 90 mA at 0 GPa); the stretch term is partly cancelled by bend/libration.

**How to test.** A reversed-bracket, side-by-side AlOOH/AlOOD experiment (same press, pressure medium, calibrant and temperature path). A boundary shift of opposite sign at matched conditions contradicts the prediction; a shift not resolvable from zero at the experiment's bracketing resolution is a null result.

**Caveats.** Harmonic/QHA physics only; Sano-Furukawa et al. 2018 report the delta-AlOOH proton-disorder transition (P2_1nm to Pnnm) at 9.0 GPa for AlOOH and 13.4 GPa for AlOOD, and H-bond symmetrisation at 18.1 GPa in AlOOH only; this measured isotope shift of a neighbouring transition (+4.4 GPa) is anharmonic physics outside our model and shows that isotope effects in this system are large; the experimental boundary is crossed at high temperature, beyond the 300 K calculation; universal MLIPs trained on PBE-like data overbind H bonds (decision 01, F02).

**Novelty check.** Valency Bond query (logged) finds high-pressure neutron work on deuterated delta-AlOOD and epsilon-FeOOD and DFT stability studies of AlOOH phases without isotope effects; no measurement or prediction of the isotope shift of the diaspore to delta boundary was found.

## Second card: goethite to epsilon-FeOOH (same method, 3/6/9 GPa, 300 K)
Goethite (alpha-FeOOH, Pnma, mp-605437) transforms to the InOOH-type epsilon-FeOOH (P2_1nm, JVASP-92228) at high pressure; epsilon-FeOOD is used for high-pressure neutron work (Ikeda et al. 2025, 10.1021/jacs.4c11982). This is the pair whose O-H stretch and bend shifts were compared with measured spectra in F04.
| model | P_t FeOOH | P_t FeOOD | dP_iso |
|---|---|---|---|
| MACE | 11.0 GPa | 11.5 GPa | +0.46 GPa |
| ORB | 9.4 GPa | 9.8 GPa | +0.40 GPa |
Both roots lie beyond the 3 to 9 GPa grid (linear extrapolation). Same status as the AlOOH card: exploratory sign prediction; epsilon-FeOOH has a short H bond that symmetrises at higher pressure, outside harmonic physics.

## Temperature dependence
Computed with `src/isoshift_event/card_temperature.py` (`results/card_alooh_temperature.json`): Gamma-free QHA rebuilt from the cached force constants on a 0 to 1550 K grid, imaginary modes omitted, vinet EOS, the same linear fit through 10, 15 and 20 GPa for both isotopes. The imaginary fraction is at most 0.6 percent of the mesh modes (MACE delta-AlOOH; diaspore at most 0.03 percent), and the QHA volume stays inside the scanned volume grid up to 1500 K for all three models. The 300 K values reproduce the card (MACE +1.328, ORB +1.125 GPa). The MACE H root stays extrapolated below 10 GPa up to 1000 K.

| model | T (K) | P_t AlOOH (GPa) | P_t AlOOD (GPa) | dP_iso (GPa) |
|---|---|---|---|---|
| MACE | 300 | 8.76 | 10.08 | +1.33 |
| MACE | 600 | 8.99 | 10.22 | +1.23 |
| MACE | 1000 | 9.48 | 10.42 | +0.94 |
| MACE | 1500 | 10.18 | 10.84 | +0.66 |
| ORB | 300 | 12.99 | 14.12 | +1.13 |
| ORB | 600 | 13.51 | 14.57 | +1.06 |
| ORB | 1000 | 14.30 | 15.11 | +0.81 |
| ORB | 1500 | 15.17 | 15.73 | +0.56 |
| MatterSim | 300 | 15.14 | 16.13 | +0.99 |
| MatterSim | 600 | 15.52 | 16.46 | +0.94 |
| MatterSim | 1000 | 16.11 | 16.83 | +0.73 |
| MatterSim | 1500 | 16.79 | 17.31 | +0.52 |

At about 1000 K an experimentalist should expect the boundary to sit roughly 0.7 to 1.5 GPa above its 300 K position in each model and the deuterated sample to cross about 0.7 to 0.9 GPa higher than the protiated one, a shift that shrinks with temperature but keeps its sign; this remains a harmonic/QHA statement and ignores the proton disorder of delta-AlOOH.

Goethite to epsilon-FeOOH (same calculation, 3/6/9 GPa): ORB gives dP_iso = +0.37 (300 K), +0.42 (600 K), +0.38 (1000 K) and +0.18 GPa (1500 K, QHA volume off the grid), with P_t(FeOOH) 9.4, 9.9, 10.5 GPa at 300, 600, 1000 K. All FeOOH roots are extrapolated beyond 9 GPa. MACE leaves the volume grid above about 550 K (goethite is compressed below the grid at 9 GPa), so only its 300 K value is usable, and there the Gamma-free rebuild gives +0.22 GPa instead of the +0.46 GPa above. The difference is q-mesh sensitivity: changing the goethite mesh from 12x9x4 to 12x8x4 moves the 9 GPa dG by 0.1 to 0.2 meV/atom, as large as the isotope signal. The FeOOH shift is therefore a sign statement only, at +0.2 to +0.5 GPa.
