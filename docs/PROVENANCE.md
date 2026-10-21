# Provenance: pre-event and event work

All times are 2026-10-21 +0300 unless stated, taken from `git log`. Tag `pre-event-baseline` points at commit a5aff16 (14:19:04). Everything reachable from that tag is pre-event. Commits after it are event work.

Note on the boundary: the baseline commit was made on 21 Oct at 14:19, after planning and before the event ledger started (14:20). The persistent GPU worker pool in that commit (`isoshift/pool.py`, `isoshift/worker.py`, `tests/test_pool.py`, `docs/specs/pool-persistent-gpu-worker.md`) was written on the day of the event, before the event proper, and is declared as pre-event infrastructure.

## Pre-event artifacts (in the tag)

| artifact | commit | time |
|---|---|---|
| `harness/` generic LLM CLI wrapper, parallel runner, OpenAlex client, tests, environment | 1446cbe | 20 Oct 23:58 |
| `isoshift/` topic harness (MLIP calculators, phonon mass override, QHA, comparison, cache) and feasibility scripts in `prep/` | 7ba1155 | 21 Oct 01:02 |
| Topic decision, plan, research and feasibility report (`DECISION.md`, `PLAN.md`, `docs/research/`, `docs/brainstorm/`) | bccf257 | 21 Oct 01:03 |
| Planning, orchestration and workflow documents (`docs/WORKFLOW.md`, `START.md`, `CONTEXT.md`, `docs/preflight/`), orchestra workflows | fed5cd0 to 44ceaee | 21 Oct, morning |
| Pre-event curated data: validation structures (42 CIFs), curated pair list, prefetch manifest `data/isoshift/PREFETCH.md` | c4a906a | 13:56 |
| Plan review decisions P10 to P25 | 6fac324 | 14:16 |
| Persistent GPU worker pool: `isoshift/pool.py`, `isoshift/worker.py`, `tests/test_pool.py`, `docs/specs/pool-persistent-gpu-worker.md` | a5aff16 (tagged) | 14:19 |

## Event artifacts (after the tag)

| artifact | commit | time |
|---|---|---|
| `src/isoshift_event/` scaffold, MP H-compound fetch, Bond query log, ledger | cfb3152 | 14:22 |
| Fix to pre-event code: `isoshift/pool.py` and `tests/test_pool.py`, Windows file-replace collisions (first of two event-time changes to pre-event code; the second is `harness/llm.py`, d250b20, below) | 62f1fde | 14:41 |
| M01 isotope formulas (mathcheck), validation table | 0eb8954 | 14:51 |
| Brucite imaginary-mode decision, validation QHA runner | c734d5f | after 14:51 |
| DFT isotope benchmark (`benchmark.py`) | aa1f6a0 | after c734d5f |
| Screen driver (`screen.py`) | 8f2ff96 | after aa1f6a0 |
| Polymorph pair set (836 structures, 965 pairs) and 4-model validation table | 4228246 | 15:26 |
| Tier A sanity checks | 0f58aef | after 4228246 |
| marimo app (`app/isoshift_app.py`) | 47def1b | 15:31 |
| Analysis and refine | 7f8bc45 | 16:04 |
| Experimental provenance per structure | 4f5ffcb | after 7f8bc45 |
| Gate follow-ups G2, G3, F1, G1, F4, G4, F3 and decision records `docs/decisions/` | cbfb528, 9129ab6, eb82b7f, 6ab028e | after 16:04 |

Exact commit times: `git log --format='%h %ad %s' --date=iso`. The ledger of event tasks is `state/LEDGER.md`.

## Prefetched data (pre-event, committed 21 Oct 13:56 as a manifest, raw files local only)

File times are from the local filesystem. Source details and licences are in `DATA_SOURCES.md` and `data/isoshift/PREFETCH.md`.

| data | local path | fetched |
|---|---|---|
| JARVIS-DFT `dft_3d` snapshot (`jdft_3d-9-24-2025.json.zip`, `dft_3d.pkl`) | `data/isoshift/` | 21 Oct 00:23 |
| JARVIS H-compound pair summary | `data/isoshift/jarvis_h_pairs.csv` | 21 Oct 00:23 |
| Petretto 2018 phonons (figshare 5649298), 40 compounds | `data/isoshift/dft_phonons/petretto/`, archive in `petretto_raw/` | 21 Oct 13:43 |
| MDR phonondb (Togo), 40 datasets of 257 candidates | `data/isoshift/dft_phonons/mdr_phonondb/` | 21 Oct 13:44 to 13:55 |
| Materials Project phonon records, 40 | `data/isoshift/dft_phonons/mp_phonon/` | 21 Oct 13:55 |
| Materials Project validation structures, 42 CIFs (committed) | `data/isoshift/validation_structures/` | 21 Oct 13:56 (commit c4a906a) |

Fetched during the event: Materials Project H compounds (`data/isoshift/mp_h.json`, `mp_h.csv`, 4421 entries) at 14:20, by `src/isoshift_event/fetch_mp.py`.

Ignored by git (see `.gitignore`): `data/isoshift/*` except small curated files, raw downloads, `.venv`, `.venv-sevenn`, queues.

* Event-time change (21 Oct 22:10, Can's approval): `harness/llm.py` passes `--add-dir <repo>` to the headless agy call so Gemini 4 Argon can read repository files during councils (read-only in headless mode).
