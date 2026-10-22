# IsoShift app

Run: `.venv/Scripts/python.exe -m marimo run app/isoshift_app.py`

Reads `app/demo_data/` if it exists (same layout as the repo root: `results/screen_pairs.csv`,
`results/screen_structures.csv`, `results/validation/volume_isotope.csv`, `data/isoshift/pairs.csv`,
`data/isoshift/structures.csv`, optional `results/raw/screen/<model>/<id>.json`), otherwise the repo.
Override with `ISOSHIFT_DATA=<dir>`.

Tabs: F01 isotope rule, Benchmark & atlas, Check a pair, How we know. "Check a pair" reads
`results/screen_pairs_refined.csv`, `results/decompose_*.csv`, `data/isoshift/{pairs,structures,experimental}.csv`.
"How we know" reads `logs/bond_queries.jsonl`, `data/isoshift/validation.csv`, `results/validation/volume_isotope.csv`
and `docs/decisions/01-gate.md`. Files missing from `app/demo_data/` fall back to the repo. Everything is precomputed.
Export check: `.venv/Scripts/python.exe -m marimo export html app/isoshift_app.py -o out.html`.
