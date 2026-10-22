# IsoShift: deuteration and polymorph stability

In harmonic calculations with three ML potentials, deuteration favours the polymorph with shorter O-H bonds in 185 of 212 evaluations with moderate-to-strong hydrogen bonds (constant-sign baseline 131), fails with weak ones (2 of 20) and has one Al(OH)3 counterexample by pair majority; no measurement has tested it directly. Two would: D/H partitioning between coexisting polymorphs ([M02](../math/M02-bigeleisen-bridge.md)), and matched reversed-bracket AlOOH/AlOOD runs on the diaspore to δ-AlOOH transition, where the models predict a higher pressure for AlOOD (exploratory sign prediction).

**Result (F01).** Across 220 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.11 to 0.13 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds, chosen after inspecting the data), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (84 pairs, 28 formulas), against 131 of 212 for a constant-sign baseline fitted on leave-one-formula-out training folds. By model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293.

![Headline figure](../../figures/fig_headline.png)

*O-H pairs with |Δ mean O-H| ≥ 5 mÅ. Regime by the larger mean model O-H of the pair; the 0.99 Å boundary was chosen after inspecting the data (nested re-choice picks 1.00 Å in 30 of 31 folds). Open markers: evaluations involving Al(OH)3 mp-985293, kept in the counts. Evaluations share structures and models.*

**Limits.** Re-choosing the boundary inside training folds gives 183 of 210 held-out evaluations right against 131; the fold holding out Al(OH)3 scores 8 of 28 against 19, so no sharp boundary is established.

**What is new.** McKenzie et al. showed the stretch-bend competition for isotope fractionation; new here is its polymorph-stability version, slope and failure boundary. Du et al. (2026, arXiv:2610.11325) treat single systems by path integrals. A literature search (logged) found no earlier survey of H/D free-energy differences across polymorph pairs of the same compound. One laptop GPU ran 2,009 structure-model phonon jobs; a structure-only version (mean O...O ≤ 2.93 Å, 78% against 61%, signal-filtered) needs no phonons.

**Checks.** F03: stretch slopes match measured spectra at O...O 2.50 to 2.80 Å (ratios 0.91 to 0.92). F04: stretch and bend shift signs match for goethite to ε-FeOOH. F05: D/H fractionation, ordering only. F02: volume isotope effects, mixed. F07: blind ice boundaries, Ih-II and Ih-III wrong sign in 3 of 3 models (failed prediction), II-III right. Benchmark against PBEsol phonons (four models, per H): isotope ZPE MAE 0.7 to 1.5 meV, 300 K free-energy MAE 0.5 to 1.1 meV.

**Beyond the headline (post-freeze addendum, 22 Oct).** In the 10 wrong pairs bend and libration, not the stretch, flip the total below a model-dependent crossover (F09, computed); F12 (boehmite vs diaspore) matches measurement in sign but is inconclusive, F08 failed, F10 is an untested map and prospective test F11 is running ([INDEX](../INDEX.md)).

**AlOOH card (exploratory sign prediction).** Deuteration raises the diaspore to δ-AlOOH transition pressure: +1.13 to +1.33 GPa at 300 K (ORB, MACE), +0.7 to +0.9 GPa near 1000 K (three models; MACE root extrapolated). δ-AlOOH proton disorder is not modelled.

**How the AI worked.** Valency Bond agents found validation data (182 logged queries). Formulas passed a two-model mathcheck. Predictions were committed before reading data. Councils of three models logged hard calls and dissent (`docs/decisions/`). Codex reimplemented ΔΔF_iso blind to 1e-9 meV/atom (F06).

**Before vs during.** Pre-event: `harness/`, `isoshift/` (tag `pre-event-baseline`); details in `docs/PROVENANCE.md`.

Evidence: [docs/INDEX.md](../INDEX.md). Long version: [writeup_long.md](writeup_long.md).
