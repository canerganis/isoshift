# Author responses to the Valency Review of v1 (W_kqr3a38p)

For the Hub's per-point author responses once "Reviewing" is live (listed as SOON on 9 Nov 2026). Section numbers refer to v2 (published 9 Nov 2026, same permalink). Decision record: `docs/decisions/C-terra-v2.md`.

**W1, cross-polymorph stretch assumption.** Agreed. v2 states the assumption after statement (1) in Sec. II and tests it within the models: the stretch term has the sign of the O-H difference in all 232 eligible O-H evaluations and in 413 of 415 with a difference of at least 1 mÅ. It fails in 17 of 65 below 1 mÅ, where the rule is not scored. The 0, 300 and 600 K counts are reported as one test.

**W2, cutoff and the high-temperature limit.** Agreed. Sec. III A now restricts the 1/T trace limit to a complete, stable spectrum and gives both cutoff cases: a mode cut in one phase only leaves (k_BT/2) ln 2 per pure-H mode, and a cut that separates the isotopes leaves a term growing as T ln T. No consistency check exists at 2000 K, so the trace result is labelled a sign test on direct values.

**W3, 600 K rows failing the check.** Agreed. Sec. IV F repeats the counts on the 190 rows consistent at 0 and 600 K: compensation falls in 176, median C is 0.645, 0.580 and 0.402, the rule is right in 188, and all 24 consistent mp-985293 rows keep the crossover.

**W4, ice triple point against fixed temperature.** Agreed that the comparison was not matched. Sec. V now writes the Clapeyron correction. Bridgman's 1912 H2O slopes give about +3 MPa for Ih-II and -0.7 MPa for Ih-III, so the fixed-temperature shifts keep their sign. The D2O triple-point temperature still comes from a secondary compilation.

**W5, no DFT double difference.** Partly addressed. Sec. III C adds a post hoc check on same-formula pairs of the PBEsol benchmark: mean deviation 0.49 meV per H, DFT sign in 22 of 24 evaluations above 0.1 meV per H, and one reversal for the stable NaHS pair. No O-H screen pair has DFT force constants, so the limitation stays in Sec. VI.

**W6, AlOOH mesh convergence.** Addressed. Sec. IV G reports a rebuild from the same force constants at 40, 60 and 80 points per 1/a on Gamma-centred and shifted meshes. The 300 K shift stays within 0.003 GPa for each model. Supercell size and anharmonicity were not varied.

**W7, exact identity for truncated spectra.** Agreed. Sec. III B states the identity for complete spectra and the direct minus quadrature residual for the computed values, bounded at 0.02 meV/atom per pair at 0, 300 and 600 K only.

**W8, X-H against O-H slope in the abstract.** Agreed. The abstract now gives 0.11 to 0.13 for all covalent X-H pairs and 0.124 to 0.145 for O-H pairs.

**W9, MatterSim slope 0.126 against 0.128.** Not in the paper. The PDF gives 0.128 in Sec. IV A and Table I. The Hub text of v1 read 0.126 in that sentence; 0.126 is the separate formula fixed-effects slope. Reported to Valency support with crops on 9 Nov 2026. The v2 Hub text reads 0.128.

**W10, equal traces.** Agreed. Sec. III A adds that when the trace difference vanishes, the next possible term is of order 1/T^3 and sets the sign if nonzero.

**W11, missing mode index in Eq. 5.** Not in the paper. The PDF has w^H_{q nu} in Eq. 5 and its definition; the Hub rendering of v1 dropped the nu. Reported to support. In v2 the q-point weight is renamed g_q to avoid any confusion.

**W12, conditioning of the null test.** Agreed. Sec. IV B now says none of 2x10^5 draws reaches 185 (Monte Carlo p at most 5x10^-6) and that the value is conditional on rows and choices selected after inspecting the data, without adjustment for that selection.
