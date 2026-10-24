#!/usr/bin/env bash
# P12 decision 18 rows 1 and 2: pilot on mp-625152 at P = 16 (dumps for C2) and P = 32, independent seeds.
set -e
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
COMMON="--struct mp-625152 --steps 3000 --dt 0.25 --masses-points 4 --equil 0.2 --pre-equil 1000 --splitting baoab --dtype float32 --init harmonic --bead-chunk 4 --log-every 500"
$PY -m src.isoshift_event.pimd $COMMON --beads 16 --seed 1601 --dump-every 30 --out results/pimd/mp-625152_P16.json > results/pimd/logs/mp-625152_P16.log 2>&1
$PY -m src.isoshift_event.pimd $COMMON --beads 32 --seed 3201 --out results/pimd/mp-625152_P32.json > results/pimd/logs/mp-625152_P32.log 2>&1
