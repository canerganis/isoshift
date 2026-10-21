# IsoShift

IsoShift computes how swapping hydrogen for deuterium changes the vibrational free energy of a crystal, and uses that to ask which polymorph deuteration favours.

**Main finding (F01).** Across 197 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.12 to 0.15 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (moderate to strong hydrogen bonds), deuteration favours the polymorph with the shorter O-H bonds in 123 of 130 O-H model evaluations (67 pairs, 23 formulas), against 82 of 130 for a constant-sign baseline fitted on leave-one-formula-out training folds. One exploratory prediction: deuteration raises the diaspore to delta-AlOOH transition pressure by about 1 GPa.

## Why

Two groups of people deuterate crystals and would like to know what it does to phase stability.

1. Neutron-scattering crystallographers deuterate samples to reduce incoherent background. They need a warning when deuteration may move a sample toward a different polymorph than the hydrogenous one.
2. Researchers who use D2O or D2 in synthesis to target metastable phases need to know which polymorph pairs are sensitive to the isotope at all.

The effect is small (meV per atom) and static-energy errors of the models are larger. That is why the main output is the isotope double difference of free energies, which does not depend on the static energy gap between the polymorphs.

## Method

1. Born-Oppenheimer force constants do not depend on nuclear mass. One phonon calculation per structure therefore gives the harmonic and quasi-harmonic free energies for both H and D: the dynamical matrix is rebuilt with the D mass and diagonalised again. Formulas are in `docs/math/M01-isotope-formulas.md`.
2. Four universal machine-learned interatomic potentials (MLIPs) act as an ensemble: MACE, ORB, MatterSim and SevenNet (exact checkpoints in `DATA_SOURCES.md`). Phonons come from phonopy. The spread between models is reported as model spread.
3. Polymorph pairs are built from Materials Project and JARVIS-DFT: same composition, different structure, hydrogen present, no carbon, up to 32 atoms. The current set has 836 structures and 965 pairs (`data/isoshift/pairs.csv`, method in `data/isoshift/PAIRS.md`). Energies from the two databases are never subtracted from each other.
4. Validation uses measured volume and lattice isotope effects (see Results).

Sign convention: ddF_iso = [F_D(beta) - F_D(alpha)] - [F_H(beta) - F_H(alpha)]. Rules for ranking and reporting are in `PLAN.md` (P3, P13 to P15).

## How AI was used

Each step of the loop is logged so it can be checked.

1. A Valency Bond literature agent extracts the experimental validation numbers (value, unit, temperature, pressure, DOI). Bond queries are counted in the log. Every query, its purpose and what was kept are in `logs/bond_queries.jsonl`.
2. A second model cross-checks every extracted row against its source (`data/isoshift/validation.csv`).
3. Every formula in the code went through `mathcheck`: two independent derivations by two models, a numerical comparison, then reconciliation (`docs/math/M01-isotope-formulas.md`).
4. The MLIP ensemble computes the free energies (`src/isoshift_event/`).
5. Hard decisions went to a multi-model board that answers independently, with the chair writing the record including dissent. Records are in `docs/decisions/`. The gate decision (`01-gate.md`) shows one model arguing for failure and the chair overruling it on stated grounds.
6. Opus integrates the results, assigns work and makes the final calls. The task ledger is `state/LEDGER.md`, the workflow is described in `docs/WORKFLOW.md`.

## Results

Framing: H/D vibrational free energies validated against measured volume/lattice isotope effects (brucite, LiH); polymorph ddF_iso and transition shifts are exploratory ensemble predictions.

Volume isotope effect VIE = 100 (V_H / V_D - 1), quasi-harmonic, four models and four treatments of the imaginary modes (details in `docs/decisions/00-brucite-imaginary-modes.md` and `01-gate.md`, data in `results/validation/volume_isotope.csv`).

| system | computed | measured | comment |
|---|---|---|---|
| brucite Mg(OH)2 | +0.19 to +0.44% | +0.31% (Chakoumakos 2013, doi 10.2138/am.2013.4202) | sign right in 4 of 4 models under every treatment |
| LiH vs LiD | +1.02 to +1.27% | +0.81% (+1.04% from an alternative source; the two sources disagree) | sign right in 4 of 4, magnitude overestimated |
| ice XI proxy | negative in 4 of 4 | negative (anomalous) | sign reproduced, magnitude about 4 to 11 times too large; reported only |
| portlandite Ca(OH)2 | no clean result | no clean experimental H/D pair | null check, reported as uninformative |

Implementation checks (equal masses give zero shift, H/D swap flips the sign, classical-limit decay, LiH Gamma TO frequency) are in `results/validation/tier_a.csv`. SevenNet's LiH TO(H) is 15.3% off experiment, so it is excluded from quantitative claims and kept in sign votes and model spread.

### F01: an isotope rule for polymorph stability (`docs/findings/F01-xh-length-rule.md`)

![F01](figures/fig4_xh_rule.png)

* The isotope double difference per H is linear in the change of mean X-H bond length between the polymorphs: slope 0.12 (MACE), 0.12 (ORB), 0.15 (MatterSim) meV/H per mA; r 0.78 to 0.89.
* Mechanism, from a mode-resolved mass integral: the X-H stretch term (+0.24 to +0.26 meV/H per mA, same in all models) is about half cancelled by bending and libration (-0.11 to -0.13).
* Domain: when at least one polymorph has a moderate or strong H bond (mean model O-H at least 0.99 A, O...O below about 2.92 A), the sign of the bond-length change predicts which polymorph deuteration favours in 123 of 130 O-H model evaluations (67 pairs, 23 formulas; baseline 82/130 from leave-one-formula-out training folds). Re-choosing the threshold inside each fold picks 0.99 A every time; without any threshold the rule holds in 129 of 150 evaluations (all covalent pairs, signal cut, baseline 100/150). With weak H bonds on both sides the rule has no skill (1 of 16). The threshold was found after looking at the data; the full scan is in `results/F01_cv.json`.

### F03: the stretch ingredient matches measured spectra (`docs/findings/F03-stretch-vs-experiment.md`)

![F03](figures/fig5_stretch_check.png)

Model O-H stretch frequencies follow the empirical correlation of Libowitzky (1999) from measured mineral spectra: slope ratio 0.91 to 0.95 for O...O 2.50 to 2.80 A, mean offset -8 to -56 cm-1 over all donors.

### F02: prediction-first volume isotope test (`docs/findings/F02-blind-test.md`)

Predictions committed before the measured values were read (`docs/predictions/P01_volume_isotope_blind.csv`, commit 0fffc54). Mixed: alpha-AlH3 right sign but 1.3 to 1.5x too large; GaOOH and beta-CrOOH wrong sign against low-quality references; brucite and LiH right. The misses are in the strong-H-bond regime, where harmonic quasi-harmonic physics omits Ubbelohde-type proton anharmonicity. F02 does not test F01.

### Candidate card: diaspore to delta-AlOOH (`docs/findings/CARD-AlOOH.md`)

Deuteration destabilises delta-AlOOH relative to diaspore by +0.5 to +0.8 meV/atom (three models) and, in an exploratory QHA prediction at 300 K, raises the transition pressure by +1.13 GPa (ORB) and +1.33 GPa (MACE) (+0.3 to +0.4 GPa from 0 GPa geometries). The two models place the boundary 4.2 GPa apart but agree on the shift; the sign is the prediction, and proton disorder in delta-AlOOH lies outside harmonic physics. In one predeclared literature pair (goethite to ε-FeOOH) the O-H stretch falls and the assigned O-H bend rises, as predicted: nominal shifts are about -260 cm⁻¹ (from the midpoint of a 2600 to 3100 cm⁻¹ band, so anywhere from -511 to -11 cm⁻¹) against -273 predicted, and +290 against +195 cm⁻¹. The diaspore to δ-AlOOH pair was inconclusive. This is consistent with the sign of the compensating bend shift at the zone centre, not a measurement of its size or of the compensation fraction; the measured bend/stretch shift ratio (about 1.1) exceeds the model median (0.7) (`docs/findings/F04-differential-spectroscopy.md`).

### F05: blind test against measured mineral D/H fractionation (`docs/findings/F05-fractionation-test.md`)

The same H/D free energies give reduced partition function ratios, so mineral-mineral differences of measured mineral-water D/H fractionation test them without any water model. Predictions for 118 structures were committed before the data were read (`docs/predictions/P04_fractionation_blind.csv`, f3ac0ac) and the comparison rule before the comparison (`docs/predictions/P04_comparison_rule.md`). Result: the sign of every scored difference (6 of 6) and the order brucite > goethite > manganite are right in all three models, and the mineral with the longer O-H bonds takes up less deuterium, as F01 implies. The magnitudes are 5 to 10 times too large and the brucite-goethite temperature trend has the wrong sign, so the preset verdict is "ordering only": harmonic partition functions of O-H minerals are known to be biased by stretch anharmonicity.

### F06: independent reimplementation (`docs/findings/F06-independent-replication.md`)

A second model (Codex) reimplemented the isotope double difference and its stretch/bend split from the cached force constants without reading our code, using a different quadrature and q-mesh. It reproduces our numbers to 1e-9 meV/atom with 9 of 9 signs: the implementation is checked; the force fields are not.

### Benchmark

MACE vs DFT phonons (PBEsol, 40 MDR phonondb entries): isotope ZPE difference MAE 1.5 meV, F(300 K) difference MAE 1.1 meV, X-H stretch MAE 45 cm-1 (`results/benchmark/summary.csv`).

## Prior work

The competition between O-H stretch and bend zero-point energies that underlies F01 is known: McKenzie et al. derived it for hydrogen-bond isotope fractionation (J. Chem. Phys. 140, 174508 (2014), 10.1063/1.4873352; J. Chem. Phys. 143, 044309 (2015), 10.1063/1.4927391), Li, Walker and Michaelides showed competing quantum effects whose net sign depends on H-bond strength (PNAS 108, 6369 (2011)), and Zhou, Kye and Harbison explained isotopomeric polymorphism in molecular crystals by zero-point energy differences (2004, 2006). The Ubbelohde geometric isotope effect is a related geometry effect. Bourgeois et al. (2018, 10.1088/1361-648X/aad259) modelled H/D/T effects on gas-solid hydride formation. IsoShift's contribution is the solid-state polymorph-stability version of the stretch-bend competition, quantified with three ML potentials over 197 crystal pairs, with a measured regime boundary (mean O-H 0.99 A, O...O about 2.92 A) and a separate O...O sign predictor (83% vs 64% baseline).

## Novelty

The stretch-versus-bend competition behind F01 was derived for hydrogen-bond isotope fractionation in molecules and proteins by McKenzie et al. (J. Chem. Phys. 140, 174508 (2014); 143, 044309 (2015)). F01 is its solid-state, polymorph-stability counterpart, measured over hundreds of crystal pairs with three independent ML potentials. Bourgeois et al. (2018, J. Phys.: Condens. Matter, doi 10.1088/1361-648X/aad259) modelled H, D and T effects on gas-solid hydride formation with DFT. That effect is dominated by the zero-point energy of the H2 or D2 gas. IsoShift maps solid-solid polymorph free-energy differences, where the gas terms cancel, across hydroxides, borohydrides, alanates and hydrides with an MLIP ensemble, validated against measured volume and lattice isotope effects. The claim is this demonstrated extension, not exhaustive novelty.

## Limitations

* Harmonic and quasi-harmonic physics only. Anharmonic effects are not included. Pairs where most of ddF_iso comes from X-H stretches are flagged as anharmonic-sensitive.
* All four MLIPs are trained on PBE-level data and share its biases. Four related models are not four independent validations.
* Model spread is the range across models. It is not a confidence interval.
* The volume isotope effect tests the volume derivative of F_H - F_D inside one phase. It does not validate polymorph double differences or transition shifts. The one double difference we checked, alpha/gamma MgH2, splits in sign across models.
* Brucite has an imaginary H branch (up to 0.8% of modes). It is excluded from F_vib and its effect is bounded by a four-treatment bracket, not computed anharmonically. Relaxed volumes are off: brucite 5.4 to 7.2% too large, ice 6.5 to 7.9% too dense.
* No nuclear tunnelling and no order-disorder physics. Negative controls are labelled by mechanism: tunnelling (KDP, delta-AlOOH), configurational disorder (KOH, NH4Cl), plus NaOH/NaOD. They test stated limits and are not required to fail.
* Open items are listed in `docs/decisions/01-gate.md`.

## How to run

```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt            # MACE and ORB
# SevenNet and MatterSim need e3nn>=0.5 and live in a second environment:
python -m venv .venv-sevenn
.venv-sevenn/Scripts/pip install -r requirements-secondary.txt
```

Screen, analysis and validation (the screen needs a GPU):

```
python -m src.isoshift_event.pairs                 # build structures.csv and pairs.csv
python -m src.isoshift_event.screen --help         # restartable per-structure H/D screen
python -m src.isoshift_event.analysis --top 10     # ensemble audit, writes results/candidates.csv
python -m src.isoshift_event.validate --help       # QHA volume isotope effect runs
python -m src.isoshift_event.sanity mace,orb       # tier A checks
```

App (reads cached results, no GPU needed):

```
marimo run app/isoshift_app.py
```

See `app/README.md` for the data layout the app reads.

## Prior work and event work

Declared for the hackathon. The full list with commits and timestamps is in `docs/PROVENANCE.md`.

Before the event (git tag `pre-event-baseline`, commit a5aff16, 21 Oct 2026 14:19 +0300):

* `harness/`, a generic LLM command-line wrapper, parallel runner and OpenAlex client.
* `isoshift/`, the topic harness: MLIP calculators, phonon mass override, QHA, comparison utilities, and a persistent GPU worker pool (`isoshift/pool.py`, `isoshift/worker.py`, `tests/test_pool.py`).
* Python environment, feasibility studies in `prep/`, planning and review documents in `docs/`, and prefetched data (validation structures, DFT phonon sets) in `data/isoshift/`.

During the event (21 Oct onward):

* Everything in `src/isoshift_event/` and `app/`: pair builder, screen driver, validation and QHA runs, sanity checks, benchmark against DFT phonons, analysis, refinement, provenance, convergence checks, Bond log.
* `data/isoshift/validation.csv`, pairs, structures, `results/`, decision records, math checks and the ledger.
* One event-time fix to pre-event code: `isoshift/pool.py`, commit 62f1fde, which handles Windows file-replace collisions.

## License and citation

MIT, see `LICENSE`. Citation metadata is in `CITATION.cff`. Data and model licences are in `DATA_SOURCES.md`.
