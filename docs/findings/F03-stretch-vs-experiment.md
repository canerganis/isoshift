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


## Windowed slope analysis (decision 04)

Code: `windowed_analysis` in `src/isoshift_event/stretch_check.py` (`python -m src.isoshift_event.stretch_check --from-csv` reruns it from `results/stretch_check.csv` in seconds), output `results/stretch_check_summary.json` key `windowed`, figure `figures/fig5_stretch_check.png` (main window shaded, f in the legend).

Procedure: keep donors with stretch_weight > 0.5 and a finite O...O; remove symmetry-equivalent donors within a structure (d_OH within 0.001 A, d_OO within 0.002 A, frequency within 2 cm^-1; this drops 0, 1 and 1 donors for MACE, MatterSim and ORB); take the donors in an O...O window; regress the model frequency on the Libowitzky frequency at the same O...O. The slope is the ratio f of model to measured slope (1 means the measured slope is reproduced). Theil-Sen is the robust variant; the 95% interval is a bootstrap over structures (1000 draws), because donors of one structure are not independent.

Main window 2.50 to 2.80 A:

| model | donors (structures) | f OLS (95% interval) | f Theil-Sen | median offset (cm^-1) | f OLS after gap change 150 / 400 cm^-1 |
|---|---|---|---|---|---|
| MACE | 52 (18) | 0.91 (0.66 to 1.07) | 0.98 | -39 | 1.00 / 1.21 |
| ORB | 30 (15) | 0.95 (0.81 to 1.07) | 0.98 | -58 | 1.04 / 1.25 |
| MatterSim | 41 (8) | 0.91 (0.36 to 1.06) | 0.93 | -13 | 1.01 / 1.21 |

The measured Libowitzky curve spans 1646 cm^-1 over this window. The models reproduce the measured slope within 10% (OLS) and within 7% (Theil-Sen), with a roughly uniform offset of -13 to -58 cm^-1. Only one DFT (PBEsol) donor falls in the window, so the DFT set gives no slope.

Harmonic against fundamental. The models give harmonic Gamma frequencies, Libowitzky is built from measured fundamentals. The gap between the two grows with hydrogen bond strength, so the true harmonic slope is flatter than the measured one by (gap change)/(span). I could not find a tabulated harmonic-minus-fundamental gap for O-H stretches in solids (a literature search returned only the Libowitzky correlation itself and a roughly 50 cm^-1 anharmonic red shift in one molecular crystal), so the bracket is an assumption: the gap grows from about 150 cm^-1 at the weak end (2.8 A, about twice the gas-phase OH anharmonicity constant) to about 300 cm^-1 at the strong end (2.5 A), a change of 150 cm^-1 (central case), and up to a change of 400 cm^-1 (pessimistic case). Dividing f by (1 - change/1646) gives the corrected f in the last column: 1.00 to 1.04 in the central case and 1.21 to 1.25 in the pessimistic case, with Theil-Sen at most 1.30. The model slope therefore exceeds the harmonic reference by at most about 1.3. F01 would change sign only at f of about 1.9 to 2.3 (decision 04), so the margin is still about 1.5 to 1.8.

Sensitivity and limits.
* The slope is constrained only over the whole window. Split in two, f is 0.78, 0.88, 1.08 (MACE, ORB, MatterSim) in 2.50 to 2.65 A and 0.80, 1.35, 0.50 in 2.65 to 2.80 A, with wide intervals. Do not quote sub-window slopes.
* The bootstrap interval of the MatterSim main-window slope is wide (0.36 to 1.06) because only 8 structures contribute.
* The bootstrap upper edge stays near 1.07 for all three models, so the data do not support a large over-steepening in this window.
* In the weak range 2.80 to 3.10 A the frequency span is only 170 cm^-1 and the picture changes: f OLS is 0.67 (MACE, 11 donors, interval -0.06 to 1.67), 2.71 (ORB, 28 donors, 1.37 to 4.75) and 2.04 (MatterSim, 12 donors, 1.18 to 4.23), with median offsets of -105, +6 and -144 cm^-1. ORB and MatterSim are steeper than the measured correlation there. That range is where hydrogen bonds are weak and F01 has no skill, but it is a caveat on the stretch-support sentence.
* Selection issues stay as disclosed in decision 04: the stretch mode is the Gamma mode above 1500 cm^-1 with the largest projection on the O-H bond, there is no acceptor-angle criterion, and the periodic acceptor search is not robust. The check supports the stretch slope against O...O only, not the bend and libration term.

Difference from decision 04: the decision lists f_OLS as 0.91 / 0.92 / 0.95 for "mace/orb/mattersim"; the chair's script prints alphabetical order (mace, mattersim, orb), so 0.92 is MatterSim and 0.95 is ORB. With the tolerance-based dedup here MatterSim gives 0.913 (41 donors) instead of 0.92 (42 donors with rounding-based dedup); the other two are identical.
