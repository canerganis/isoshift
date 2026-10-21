# IsoShift app

Run: `.venv/Scripts/python.exe -m marimo run app/isoshift_app.py`

Reads `app/demo_data/` if it exists (same layout as the repo root: `results/screen_pairs.csv`,
`results/screen_structures.csv`, `results/validation/volume_isotope.csv`, `data/isoshift/pairs.csv`,
`data/isoshift/structures.csv`, optional `results/raw/screen/<model>/<id>.json`), otherwise the repo.
Override with `ISOSHIFT_DATA=<dir>`.
