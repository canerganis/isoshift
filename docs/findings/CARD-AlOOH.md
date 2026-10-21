# Candidate card (GOAL S7): deuteration raises the diaspore to delta-AlOOH transition pressure by about 1 GPa

**System.** AlOOH: diaspore (alpha-AlOOH, Pnma, mp-625152) and delta-AlOOH (P2_1nm, mp-23807). Both phases are real; delta-AlOOH forms from diaspore at about 17 to 20 GPa and is quenchable. It is a candidate water carrier in the deep mantle, and deuterated delta-AlOOD is the standard sample for high-pressure neutron diffraction (Sano-Furukawa et al. 2018, 10.1038/s41598-018-33598-2), so an isotope shift of the boundary matters to the people who measure it.

**Prediction (harmonic, 0 GPa geometry, 300 K, three MLIPs).** ddF_iso = F_D - F_H (delta minus diaspore) = +0.52 / +0.77 / +0.83 meV/atom (MatterSim / MACE / ORB), i.e. +2.1 to +3.3 meV per H: deuteration destabilises delta-AlOOH relative to diaspore. Numerical error 2e-4 meV/atom; both structures free of imaginary modes in all models. Mechanism, as in F01: delta-AlOOH has the stronger H bond (O-H longer by 24 to 32 mA, O...O shorter by 60 to 90 mA); the stretch term (+1.7 to +2.1 meV/atom) is partly cancelled by bend/libration (-1.2 to -1.3).
With dV = V_delta - V_diaspore = -0.30 to -0.32 A^3/atom, dP_iso = -ddF/dV = +0.28 to +0.42 GPa at the 0 GPa geometry. The static transition pressures from the same models are 13 to 17 GPa, close to experiment.

**Prediction at the transition (QHA at 10, 15, 20 GPa, 300 K; `src/isoshift_event/card_alooh.py`, `results/card_alooh_pressure.json`).** Gibbs energies of both phases for H and D masses at each pressure; the transition pressure is the root of G_delta - G_diaspore.

| model | P_t (AlOOH) | P_t (AlOOD) | dP_iso |
|---|---|---|---|
| MACE | 8.8 GPa (root from the 10-20 GPa line, extrapolated) | 10.2 GPa | +1.4 GPa |
| ORB | 12.9 GPa | 14.0 GPa | +1.1 GPa |

The two models disagree by 4 GPa on where the boundary is, and agree on how far deuteration moves it: +1.1 to +1.4 GPa, about 8 to 15%. The isotope term grows with pressure (ddF at 10 GPa about 2.3 meV/atom vs 0.8 at 0 GPa) because the delta-AlOOH hydrogen bond shortens on compression, which is the F01 mechanism. Both models place the boundary below the pressures used to synthesise delta-AlOOH (about 20 GPa), a known tendency of PBE-trained potentials that the isotope difference largely cancels.

**How to falsify.** Synthesise or compress AlOOH and AlOOD side by side (multi-anvil or DAC with in-situ XRD, same pressure medium and calibrant) and bracket the diaspore to delta boundary at 300 K or along a common isotherm. Prediction: the AlOOD boundary lies higher, between the 0 GPa-geometry estimate (+0.3 to +0.4 GPa) and the QHA value at the transition (+1.1 to +1.4 GPa); the QHA value is an upper estimate because harmonic physics overstates the softening of the shortest H bonds. A shift of the opposite sign, or none within +/-0.2 GPa at matched conditions, contradicts the prediction. Kinetics make the boundary hard to bracket; reversed experiments are needed.

**Caveats.** Harmonic/QHA only. delta-AlOOH has a very short H bond; proton delocalisation and H-bond symmetrisation (about 9 GPa in AlOOH and 13 GPa in AlOOD per earlier literature rows) are anharmonic and outside the model, and they occur in the delta phase near the pressures of interest. Universal MLIPs trained on PBE-like data overbind H bonds (decision 01, F02). The prediction is a direction and an order of magnitude, not a number to 0.1 GPa.

**Novelty check.** Valency Bond query (logged) finds high-pressure neutron work on deuterated delta-AlOOD and epsilon-FeOOD and DFT stability studies of AlOOH phases without isotope effects; no measurement or prediction of the isotope shift of the diaspore to delta boundary was found.
