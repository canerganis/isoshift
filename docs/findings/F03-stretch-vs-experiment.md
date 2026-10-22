# F03. The ensemble is consistent with the measured O-H stretch versus hydrogen-bond length correlation

**Status: tested (consistency check of the stretch slope, O...O 2.50 to 2.80 Å; not a test of isotope free energies).**

**Current statement (decision 07, frozen `results/stretch_check_summary.json`).** For O-H donors with model O...O distances of 2.50 to 2.80 Å, the harmonic Γ-point stretch frequencies follow the slope of the empirical Libowitzky ν(OH) vs O...O correlation with slope ratios of 0.91 (MACE), 0.92 (ORB) and 0.92 (MatterSim), structure-bootstrap 95% intervals 0.67 to 1.07, 0.82 to 1.01 and 0.81 to 1.02 (`results/stretch_check_summary.json`). Above 2.80 Å the ratios are 0.67, 2.61 and 1.46, so ORB and MatterSim are too steep there, and the F01 strong regime reaches O...O of about 2.93 Å. This is a consistency check on the stretch term, not a validation of isotope free energies.

Test of the ingredient that carries F01: the dependence of the O-H stretch frequency on hydrogen-bond geometry. For every O-H donor in clean screened structures (`src/isoshift_event/stretch_check.py`), the Gamma-point stretch frequency is compared with the empirical correlation of Libowitzky (1999) built from measured IR/Raman spectra of minerals, nu = 3592 - 304e9 exp(-d(O...O)/0.1321) cm^-1, and with DFT (PBEsol) phonons from MDR phonondb.

| source | O-H donors | mean residual vs Libowitzky | RMS residual |
|---|---|---|---|
| MACE | 321 | -44 cm^-1 | 221 cm^-1 |
| ORB | 323 | +2 cm^-1 | 191 cm^-1 |
| MatterSim | 289 | +8 cm^-1 | 206 cm^-1 |
| DFT PBEsol (MDR) | 27 | +53 cm^-1 | 266 cm^-1 |

Averaged over all donors (2.5 to 3.2 A), the three potentials show no large systematic offset (mean residuals above) and scatter less than the DFT reference set (figure `figures/fig5_stretch_check.png`). The mean residuals hide the slope: only 2.50 to 2.80 A is checked against the measured slope, and above 2.80 Å ORB and MatterSim are too steep (ratios 2.61 and 1.46, windowed section below). Harmonic frequencies are compared with anharmonic measured fundamentals, so a positive offset of order 100 cm^-1 would be expected; the near-zero offset may reflect the MLIPs' slight H-bond overbinding cancelling it.

Scope: this is a consistency check on the stretch slope against O...O, not a validation of isotope free energies. Above 2.80 A the picture changes (see the windowed analysis below). The wrong-sign blind volume isotope effects for strongly H-bonded oxyhydroxides (F02) are a separate question, the volume derivative (Gruneisen and anharmonic, Ubbelohde-type geometric isotope effects), which harmonic QHA cannot describe.

## Windowed slope analysis (decision 04)

Code: `windowed_analysis` in `src/isoshift_event/stretch_check.py` (`python -m src.isoshift_event.stretch_check --from-csv` reruns it from `results/stretch_check.csv` in seconds), output `results/stretch_check_summary.json` key `windowed`, figure `figures/fig5_stretch_check.png` (main window shaded, f in the legend).

Procedure: keep donors with stretch_weight > 0.5 and a finite O...O; remove symmetry-equivalent donors within a structure (d_OH within 0.001 A, d_OO within 0.002 A, frequency within 2 cm^-1; this drops 0, 1 and 1 donors for MACE, MatterSim and ORB in the frozen run); take the donors in an O...O window; regress the model frequency on the Libowitzky frequency at the same O...O. The slope is the ratio f of model to measured slope (1 means the measured slope is reproduced). Theil-Sen is the robust variant; the 95% interval is a bootstrap over structures (2000 draws), because donors of one structure are not independent.

Main window 2.50 to 2.80 A:

| model | donors (structures) | f OLS (95% interval) | f Theil-Sen | median offset (cm^-1) | f OLS after gap change 150 / 400 cm^-1 |
|---|---|---|---|---|---|
| MACE | 52 (18) | 0.91 (0.67 to 1.07) | 0.98 | -39 | 1.00 / 1.21 |
| ORB | 58 (20) | 0.92 (0.82 to 1.01) | 0.97 | -53 | 1.02 / 1.22 |
| MatterSim | 58 (17) | 0.92 (0.81 to 1.02) | 0.93 | -10 | 1.01 / 1.21 |

Bootstrap 95% intervals for f_OLS (resampling structures, 2000 resamples, seed 0, `results/stretch_check_summary.json`): MACE 0.67 to 1.07, ORB 0.82 to 1.01, MatterSim 0.81 to 1.02 (frozen run). Before the freeze ORB and MatterSim had 15 and 8 structures in this window and intervals of 0.82 to 1.07 and 0.41 to 1.05 (superseded).

Scope note: the checked window ends at 2.80 Å, while the F01 strong regime extends to a mean O...O of about 2.93 Å. The stretch slope is therefore not checked over the last 0.13 Å of the F01 regime, and above 2.80 Å ORB and MatterSim are too steep (below).

The measured Libowitzky curve spans 1646 cm^-1 over this window. The point estimates reproduce the measured slope within 9% (OLS) and within 8% (Theil-Sen), but the intervals are wide (lower edges 0.67 to 0.82), so the data do not exclude a slope 20 to 30% too shallow; the upper edges are 1.01 to 1.07. There is a roughly uniform median offset of -10 to -53 cm^-1. Only one DFT (PBEsol) donor falls in the window, so the DFT set gives no slope.

Harmonic against fundamental. The models give harmonic Gamma frequencies, Libowitzky is built from measured fundamentals. The gap between the two grows with hydrogen bond strength, so the true harmonic slope is flatter than the measured one by (gap change)/(span). I could not find a tabulated harmonic-minus-fundamental gap for O-H stretches in solids (a literature search returned only the Libowitzky correlation itself and a roughly 50 cm^-1 anharmonic red shift in one molecular crystal), so the bracket is an assumption: the gap grows from about 150 cm^-1 at the weak end (2.8 A, about twice the gas-phase OH anharmonicity constant) to about 300 cm^-1 at the strong end (2.5 A), a change of 150 cm^-1 (central case), and up to a change of 400 cm^-1 (pessimistic case). Dividing f by (1 - change/1646) gives the corrected f in the last column: 1.00 to 1.02 in the central case and 1.21 to 1.22 in the pessimistic case, with Theil-Sen at most 1.30. The model slope therefore exceeds the harmonic reference by at most about 1.3. F01 would change sign only at f of about 1.9 to 2.3 (decision 04), so the margin is still about 1.5 to 1.8.

Sensitivity and limits.
* The slope is constrained only over the whole window. Split in two, f is 0.78, 0.90, 0.93 (MACE, ORB, MatterSim) in 2.50 to 2.65 Å and 0.80, 0.96, 0.62 in 2.65 to 2.80 Å, with wide intervals. Do not quote sub-window slopes.
* The MACE main-window interval is the widest (0.67 to 1.07, 18 structures). Before the freeze the MatterSim interval was 0.41 to 1.05 with 8 structures (superseded); the frozen run has 17.
* The bootstrap upper edge stays at 1.01 to 1.07 for all three models, so the data do not support a large over-steepening in this window. The intervals extend well below 1, so the data also do not pin the slope tightly.
* In the weak range 2.80 to 3.10 A the frequency span is only 170 cm^-1 and the picture changes: f OLS is 0.67 (MACE, 11 donors, interval -0.06 to 1.66), 2.61 (ORB, 32 donors, 1.47 to 3.85) and 1.46 (MatterSim, 15 donors, 0.33 to 3.15), with median offsets of -105, -16 and -128 cm^-1. ORB and MatterSim are steeper than the measured correlation there. That range is mostly outside the F01 strong regime, which reaches about 2.93 Å, so the part of the regime between 2.80 and 2.93 Å is not covered by the check; this is a caveat on the stretch-support sentence.
* Selection issues stay as disclosed in decision 04: the stretch mode is the Gamma mode above 1500 cm^-1 with the largest projection on the O-H bond, there is no acceptor-angle criterion, and the periodic acceptor search is not robust. The check supports the stretch slope against O...O only, not the bend and libration term.

Correction to decision 04 (pre-freeze values, superseded by the frozen 0.91 / 0.92 / 0.92 above): the decision lists f_OLS as 0.91 / 0.92 / 0.95 for "mace/orb/mattersim", which is the wrong order. The correct values are MACE 0.91, ORB 0.95, MatterSim 0.91 (0.912, 0.948, 0.913; the chair script prints alphabetical order mace, mattersim, orb, so 0.92 was MatterSim). With the tolerance-based dedup here MatterSim gives 0.913 (41 donors) instead of 0.92 (42 donors with rounding-based dedup); the other two are identical. Theil-Sen is 0.98 (MACE), 0.98 (ORB), 0.93 (MatterSim).
