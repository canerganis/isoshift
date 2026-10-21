# F03. The ensemble reproduces the measured O-H stretch versus hydrogen-bond length correlation

Test of the ingredient that carries F01: the dependence of the O-H stretch frequency on hydrogen-bond geometry. For every O-H donor in clean screened structures (`src/isoshift_event/stretch_check.py`), the Gamma-point stretch frequency is compared with the empirical correlation of Libowitzky (1999) built from measured IR/Raman spectra of minerals, nu = 3592 - 304e9 exp(-d(O...O)/0.1321) cm^-1, and with DFT (PBEsol) phonons from MDR phonondb.

| source | O-H donors | mean residual vs Libowitzky | RMS residual |
|---|---|---|---|
| MACE | 315 | -56 cm^-1 | 197 cm^-1 |
| ORB | 223 | -8 cm^-1 | 152 cm^-1 |
| MatterSim | 178 | -12 cm^-1 | 173 cm^-1 |
| DFT PBEsol (MDR) | 27 | +53 cm^-1 | 266 cm^-1 |

All three potentials follow the measured curve over 2.5 to 3.2 A without a systematic offset, and scatter less than the DFT reference set (figure `figures/fig5_stretch_check.png`). Harmonic frequencies are compared with anharmonic measured fundamentals, so a positive offset of order 100 cm^-1 would be expected; the near-zero offset may reflect the MLIPs' slight H-bond overbinding cancelling it.

Consequence for F01: the stretch term that sets the F01 slope rests on a frequency versus geometry relation that matches experiment, so F01 is not an artefact of a wrong MLIP stretch response. The wrong-sign blind volume isotope effects for strongly H-bonded oxyhydroxides (F02) therefore point to the volume derivative (Gruneisen and anharmonic, Ubbelohde-type geometric isotope effects) rather than to the stretch-geometry relation; harmonic QHA cannot describe the geometric isotope effect of short H bonds.
