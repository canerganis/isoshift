# results/F01_rule_fit.json is superseded

`results/F01_rule_fit.json` holds a pre-freeze fit of the F01 slope (rows 177 MACE, 121 ORB, 43 MatterSim; slopes 0.1163, 0.1203, 0.1471 meV per H per mÅ). It was not regenerated after the compute freeze and does not match the frozen numbers.

Current values (three models, clean covalent rows of `results/decompose_pairs.csv`, OLS of ddF_total/H_per_atom on 1000·dXH_mean_A):

| model | rows | slope | r |
|---|---|---|---|
| MACE | 188 | 0.112 | 0.76 |
| ORB | 163 | 0.117 | 0.83 |
| MatterSim | 170 | 0.128 | 0.84 |

Sources: `docs/freeze/FREEZE_REPORT.md` (frozen table), `docs/decisions/07-freeze-wording.md`, and `results/paper_stats.json` (`slopes_all_rows`, with formula-clustered intervals and Theil-Sen slopes, written by `src/isoshift_event/paper_stats.py`). The old JSON is kept unchanged as part of the record; do not cite it.
