# IsoShift

IsoShift computes how swapping hydrogen for deuterium changes the vibrational free energy of a crystal, and uses that to look for hydrogen-containing polymorph pairs whose relative stability could shift on deuteration.

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

1. A Valency Bond literature agent extracts the experimental validation numbers (value, unit, temperature, pressure, DOI). Bond was queried 34 times. Every query, its purpose and what was kept are in `logs/bond_queries.jsonl`.
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

Main figure:

<!-- RESULTS: filled after analysis -->

Candidate table:

<!-- RESULTS: filled after analysis -->

## Novelty

Bourgeois et al. (2018, J. Phys.: Condens. Matter, doi 10.1088/1361-648X/aad259) modelled H, D and T effects on gas-solid hydride formation with DFT. That effect is dominated by the zero-point energy of the H2 or D2 gas. IsoShift maps solid-solid polymorph free-energy differences, where the gas terms cancel, across hydroxides, borohydrides, alanates and hydrides with an MLIP ensemble, validated against measured volume and lattice isotope effects. The claim is this demonstrated extension, not exhaustive novelty.

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
