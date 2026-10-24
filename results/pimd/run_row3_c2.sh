#!/usr/bin/env bash
# P12 decision 18 row 3: C2 float64 re-evaluation of the row 1 snapshots, started once rows 1 and 2 are complete
# (the GPU is then free). Polls the run JSONs; no decision is taken here.
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
done_() { $PY -c "import json,sys;sys.exit(0 if json.load(open('$1'))['status']=='complete' else 1)" 2>/dev/null; }
until done_ results/pimd/mp-625152_P16.json && done_ results/pimd/mp-625152_P32.json; do sleep 300; done
$PY results/pimd/controls/c2_float64.py results/pimd/mp-625152_P16.json results/pimd/c2_mp-625152_P16.json > results/pimd/logs/c2_mp-625152_P16.log 2>&1
