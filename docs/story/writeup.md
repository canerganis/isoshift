# IsoShift: deuteration and polymorph stability

Two days produced a testable, regime-limited computational rule, its failure boundary, one named counterexample and a falsifiable pressure prediction. It is not a confirmed discovery, because this observable has never been measured.

**Result (F01).** Across 220 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.11 to 0.13 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds, chosen after inspecting the data), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (84 pairs, 28 formulas), against 131 of 212 for a constant-sign baseline fitted on leave-one-formula-out training folds. By model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293.

![Headline figure](../../figures/fig_headline.png)

*O-H pairs with |Δ mean O-H| ≥ 5 mÅ. Regime by the larger mean model O-H of the pair; the 0.99 Å boundary was chosen after inspecting the data (nested re-choice picks 1.00 Å in 30 of 31 folds). Open markers: evaluations involving Al(OH)3 mp-985293, kept in the counts. Evaluations share structures and models.*

**Limits.** Re-choosing the boundary inside training folds gives 183 of 210 held-out evaluations right against 131; the fold holding out Al(OH)3 scores 8 of 28 against 19, so no sharp boundary is established. With weak hydrogen bonds it fails (2 of 20).

**Direct test.** Measured D/H partitioning between coexisting polymorphs would test F01 directly: it equals the boundary isotope shift (n_H kT ln α = ΔΔG_iso, M02).

**Scale and novelty.** 2009 structure-model phonon results ran on one 8 GB laptop GPU; a structure-only version (mean O...O ≤ 2.93 Å, 78% against 61%, signal-filtered) needs no phonons. McKenzie et al. showed the stretch-bend competition for isotope fractionation; new here is its polymorph-stability version, slope and failure boundary.

**Checks.** F03: stretch slopes match measured spectra at O...O 2.50 to 2.80 Å (ratios 0.91 to 0.92). F04: stretch and bend shifts match in sign for one pair (goethite to ε-FeOOH). F05: mineral D/H fractionation, ordering only. F02: volume isotope effects, mixed. F07: ice, Ih boundaries challenged, II-III supported. Benchmark: four models against PBEsol phonons at DFT geometries, 300 K H/D free-energy MAE 0.5 to 1.1 meV per H (`results/benchmark/summary.csv`).

**AlOOH card (exploratory sign prediction).** Deuteration raises the diaspore to δ-AlOOH transition pressure: +1.13 to +1.33 GPa at 300 K (ORB, MACE), +0.7 to +0.9 GPa near 1000 K (three models). δ-AlOOH proton disorder is not modelled. Falsifier: matched side-by-side reversed-bracket AlOOH and AlOOD runs; an opposite-sign shift refutes it.

**How the AI worked.** Valency Bond agents found validation data (132 logged queries, `logs/bond_queries.jsonl`). Formulas passed a two-model mathcheck. Predictions were committed before reading data. Councils (Opus, Astra, Gemini) logged hard calls and dissent in `docs/decisions/`. Codex reimplemented ΔΔF_iso blind, matching to 1e-9 meV/atom (F06).

**Before vs during.** Before (tag `pre-event-baseline`): `harness/`, `isoshift/` and its GPU pool. During: `src/isoshift_event/`, `app/`, all findings and decisions. Event-time changes to pre-event code: `isoshift/pool.py` (62f1fde, Windows file fix) and `harness/llm.py` (d250b20, read-only repo access for Gemini, Can approved).

Evidence: [docs/INDEX.md](../INDEX.md). Long version: [writeup_long.md](writeup_long.md).
