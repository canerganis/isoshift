# P11. Boehmite vs diaspore: model D/H fractionation, predeclared before any source (post-freeze addendum)

Status: predeclared, post-freeze addendum. Written and committed before the literature agent opened any source on boehmite or diaspore D/H fractionation (decision 08, action 6). The frozen F01 headline of decision 07 (185 of 212, baseline 131, pairs 74 right, 0 ties, 10 wrong) is unchanged. The result is scored in `docs/findings/F12-boehmite-diaspore.md` (numbering per the ledger after council 08; decision 08 calls it the F10 case).

## Structures and orientation

Pair `mp-625054__mp-625152` in `results/decompose_pairs.csv`: struct_a = diaspore (mp-625152, Pnma, 16 atoms, 4 H, one H site), struct_b = boehmite model (mp-625054, Cmc2_1, 8 atoms, 2 H, one H site, Materials Project theoretical). All differences below are boehmite minus diaspore. Mean model O-H (MACE, ORB, MatterSim): boehmite 1.0059, 1.0028, 1.0058 Å; diaspore 1.0153, 1.0130, 1.0160 Å (`results/decompose_structures.csv`). Boehmite is the shorter O-H phase in all three models, so F01 says D prefers boehmite.

## Prediction from the frozen decompose rows (300 K)

ddF_total in `decompose_pairs.csv` is meV per atom with H_per_atom = 0.25, so per H it is 4 times that. kT = 25.852 meV.

| model | ddF_total (meV/atom) | ddF per H (meV) | 1000 ln α(boehmite - diaspore) at 300 K |
|---|---|---|---|
| MACE | -0.4884 | -1.954 | +75.6 ‰ |
| ORB | -0.2409 | -0.964 | +37.3 ‰ |
| MatterSim | -0.4389 | -1.756 | +67.9 ‰ |

Negative ddF per H means the deuterated boehmite is lower in free energy relative to diaspore, so D prefers boehmite.

## Prediction from `fractionation.py` (cached force constants, 25 to 450 °C)

Computed with `src.isoshift_event.fractionation._one` on the cached phonopy force constants of the frozen relaxations (`.cache/isoshift/*__sc3x3x2__*` for boehmite, `*__sc3x2x1__*` for diaspore), harmonic, |ω| treatment of imaginary modes (imaginary fraction 0 for boehmite, 0.0001 for diaspore in all three models), mesh rule as in the module, with `TEMPS_C` set to (25, 100, 200, 300, 400, 450) in the calling script (the module itself is unchanged and stops at 400 °C). Full rows, including dF per H, in `docs/predictions/P11_boehmite_diaspore.csv`.

1000 ln β (‰), mineral relative to the classical limit, per H:

| T (°C) | boehmite MACE | ORB | MatterSim | diaspore MACE | ORB | MatterSim |
|---|---|---|---|---|---|---|
| 25 | 2491.5 | 2486.1 | 2493.7 | 2415.6 | 2448.8 | 2425.5 |
| 100 | 1837.3 | 1836.7 | 1840.9 | 1772.3 | 1800.3 | 1781.1 |
| 200 | 1309.8 | 1313.0 | 1314.5 | 1254.7 | 1278.2 | 1262.4 |
| 300 | 983.2 | 988.3 | 988.3 | 935.7 | 955.8 | 942.5 |
| 400 | 765.2 | 771.0 | 770.2 | 724.0 | 741.3 | 729.9 |
| 450 | 682.2 | 688.1 | 687.0 | 643.7 | 659.9 | 649.3 |

1000 ln α(boehmite - diaspore) = 1000 ln β(boehmite) - 1000 ln β(diaspore) (‰). Water's β cancels, so this equals L(boehmite-water) - L(diaspore-water) from measurements at the same T, P and water.

| T (°C) | MACE | ORB | MatterSim | sign |
|---|---|---|---|---|
| 25 | +75.9 | +37.3 | +68.2 | + in 3 of 3 |
| 100 | +65.0 | +36.4 | +59.9 | + in 3 of 3 |
| 200 | +55.1 | +34.8 | +52.1 | + in 3 of 3 |
| 300 | +47.5 | +32.5 | +45.8 | + in 3 of 3 |
| 400 | +41.2 | +29.7 | +40.2 | + in 3 of 3 |
| 450 | +38.4 | +28.2 | +37.7 | + in 3 of 3 |

The 25 °C values match the 300 K decompose values within 0.6 ‰ (different k-mesh and 298 vs 300 K). **Predicted sign: positive at every temperature in all three models. Boehmite is D-enriched relative to diaspore, i.e. measured L(boehmite-water) should exceed L(diaspore-water).**

Calling script (session scratchpad, not committed): imports `src.isoshift_event.fractionation as fr`, sets `fr.TEMPS_C = (25, 100, 200, 300, 400, 450)`, and for each model in (mace, orb, mattersim) and structure in (mp-625054, mp-625152) calls `fr._one((model, sid, str(fr._cache_dir(model, sid))))`, serially on CPU.

## Flags

* Boehmite model mp-625054 is Materials Project theoretical (Cmc2_1, 8 atoms). Real boehmite is usually described in Cmcm with disordered or zigzag hydrogen chains; the ordered Cmc2_1 cell is a model of it, not the refined structure.
* `proton_transfer` in all three models (family flag from `pairs.py`: every MOOH with M = Al, Ga, In or Fe gets it, as do structures with a near-linear short O-H...O).
* `soft_mode_bracketed` in all three models (imaginary-mode bracket of 0.00017 meV/atom, small against the 0.24 to 0.49 meV/atom ddF).
* ORB: `relax_not_converged` and `b_relax_not_converged` (the boehmite relaxation did not reach fmax).
* Harmonic only, fixed 0 K relaxed geometry, no anharmonic or tunnelling correction, no pressure. F05 found harmonic mineral-mineral fractionation magnitudes 4.6 to 10 times too large for brucite minus goethite, so only the sign is scored.
* The three potentials are not independent validations.

## Scoring rule (decision 08, action 6, verbatim in substance)

Let Δ_meas(T) = L(boehmite-water) - L(diaspore-water) at a shared temperature T, with L = 1000 ln α in permil.

* **CONSISTENT** if, at a shared temperature where the measured Δ_meas excludes zero at two combined standard uncertainties, at least 2 of 3 models give its sign and no other such temperature contradicts it.
* **INCONSISTENT** if, at such a temperature, at least 2 of 3 models give the opposite sign.
* **INCONCLUSIVE** otherwise, or if exchange is incomplete or the values are interpolated without an uncertainty.
* The magnitude ratio (predicted over measured) is reported, not scored.

Operational clarifications, fixed now, before any source is read:

1. Combined standard uncertainty u_c = sqrt(u_b² + u_d²), where u_b and u_d are the standard uncertainties of the two mineral-water values at that temperature. If a source gives a 2σ or a range, it is converted to 1σ as stated in the source; if the source does not say what the uncertainty means, it is taken as 1σ (the conservative reading for "excludes zero").
2. A shared temperature is one where both minerals have a measured value, or a calibration equation within its stated validity range. Extrapolating an equation outside its stated range does not count. A value interpolated from an equation counts only if the source gives an uncertainty for the equation or its calibration points; otherwise that temperature is INCONCLUSIVE by the rule above.
3. If the source says exchange is incomplete for either mineral at a temperature (for example diaspore at ≤ 450 °C) and gives no extrapolated equilibrium value with an uncertainty, that temperature is not scored.
4. Only experimental equilibration or exchange data count. Natural-sample estimates, theory rows and empirical bond-strength estimates are reported but not scored (as in F05).
5. Values quoted in secondary sources (Chacko, Cole and Horita 2001, or later papers quoting Graham's equations) count only with their location recorded; if a secondary quote and the primary disagree, the primary wins.
6. The model sign is the same (+) at every temperature from 25 to 450 °C in all three models, so a shared temperature inside that range uses that sign; one outside it uses the sign of the nearest computed temperature only if it lies within 50 °C, otherwise it is not scored.

NaOH/NaOD, KOH/KOD and LiOH/LiOD are not part of this score. They pass through P08's E1 to E3 gate; if they pass, they are reported as weak-regime cases, not counted (P08).

## Source gate and stop rule

Blind Sonnet agent (`sonnet-p11-blind`), not shown these numbers. Targets: Graham, Sheppard and Heaton 1980, GCA 44, 353 (doi 10.1016/0016-7037(80)90143-x); Chacko, Cole and Horita 2001, RiMG 43 tables; papers that quote Graham's boehmite or diaspore equations. If no numeric boehmite and diaspore values with temperatures are found within 90 min, the branch is logged "not obtainable" and stopped (verdict INCONCLUSIVE, not obtainable). Hard stop 3 h total. Rows go to `data/isoshift/polymorph_fractionation.csv` with source locations; queries to `logs/bond_queries.jsonl`.
