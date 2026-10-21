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

**Caveats.** Harmonic/QHA physics only; delta-AlOOH undergoes isotope-dependent proton disorder in the same pressure window, which harmonic physics omits (pressures to be cited only after the source check in `docs/findings/F04-source-audit.md`); the experimental boundary is crossed at high temperature, beyond the 300 K calculation; universal MLIPs trained on PBE-like data overbind H bonds (decision 01, F02).

**Novelty check.** Valency Bond query (logged) finds high-pressure neutron work on deuterated delta-AlOOD and epsilon-FeOOD and DFT stability studies of AlOOH phases without isotope effects; no measurement or prediction of the isotope shift of the diaspore to delta boundary was found.
