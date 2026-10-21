# IsoShift ledger

Conductor: Opus (orchestrating session). Started Wed 21 Oct 14:20 TRT, about 2.5 h ahead of PLAN.md v3, so every block below is shifted earlier. Hard stop Fri 02:00, target submitted Fri 00:30.

## Timed plan (v4, shifted)
| When (TRT) | Track | Work | Exit |
|---|---|---|---|
| Wed 14:20 to 14:45 | WF0 | pool acceptance + commit, tag `pre-event-baseline`, `src/` scaffold, MP fetch, Bond check | done |
| Wed 14:45 to 18:30 | WF1 | mathcheck (all formulas, one batch); build `pairs.py`; build `screen.py` on `isoshift.pool`; sweep validation literature via Bond; Opus: brucite/AlOOH stability repair per P2 (`stability.py`) | 3 modules accept, validation.csv >= 6 verified rows |
| Wed ~18:30 | GPU | harmonic mace+orb screen starts as soon as `screen.py` dry run passes; validation jobs interleaved | queue running |
| Wed 18:30 to 22:00 | WF2 | QHA validation (brucite, portlandite, LiH, ice), tier A sanity, negative controls, X-H benchmark parity (sweep DFT phonons) | numbers in results/validation |
| **Wed 22:00** | GATE | board(gate) per P1 tiers | docs/decisions/01-gate.md |
| Wed 22:00 to Thu 08:00 | GPU overnight | screen all pairs mace+orb, then sevenn+mattersim on sign-agreeing pairs; watchdog hourly | queue drained |
| Evening/overnight | Product, Story | marimo app skeleton + README skeleton with placeholder data; video script draft | skeletons committed |
| Thu 08:00 to 12:00 | WF3 | ensemble filter + ranking (mathcheck stats), QHA top 10 to 20, Bond novelty per candidate, board(headline), main figure | top-10 table, figure |
| Thu 12:00 to 16:00 | WF4 | app filled with cached pairs, README, public repo (Can go-ahead), fresh clone test | clone runs app |
| Thu 16:00 to 21:00 | WF5 | write-up, red team of claims, video script final + slides; Can records ~20:00 | video uploaded Public |
| Thu 21:00 to Fri 00:30 | WF6 | Moment form text, link checks, Can submits | submitted |

## Contracts between modules (Opus, binding)
- `data/isoshift/structures.csv`: one row per unique structure. `struct_id` (e.g. `mp-23879`, `JVASP-2002`), `source` (mp|jarvis), `formula` (reduced), `spg`, `nsites`, `cif` (repo-relative path under `data/isoshift/structs/`), `e_source_eV_atom` and `e_kind` (mp_total_r2scan_or_gga|jarvis_formation) for provenance only.
- `data/isoshift/pairs.csv`: `pair_id`, `formula`, `struct_a`, `struct_b`, `source`, `dE_meV_atom` (same-source only, b minus a), `nsites_a`, `nsites_b`, `tier` (16|32), `flags` (`;`-joined: proton_transfer, hbond_disordered, partial_occ_dropped ...).
- Screen results: one JSON per (structure, model) at `results/raw/screen/<model>/<struct_id>.json` (pool output), summary `results/screen_structures.csv` with per-structure F_vib^H(T), F_vib^D(T), S, min freq, relaxed V and E, and pair table `results/screen_pairs.csv` (post-processing only).

## Task status
| id | task | owner | status | note |
|---|---|---|---|---|
| 0.pool | pool acceptance | Opus | done | a5aff16; fix bare "cuda" device |
| 0.1 | src scaffold | Opus | done | |
| 0.2 | MP fetch | Opus | done | 4421 entries, 3542 formulas -> data/isoshift/mp_h.csv |
| 0.3 | Bond check | Opus | done | list_sources OK, first query logged |
| 1.math | mathcheck batch | workflow | done | docs/math/M01, Astra/Opus agree; 3 review fixes applied (0eb8954) |
| 1.3 | pairs.py | build workflow | running | |
| 1.5 | screen.py | build workflow | running | |
| 1.1 | validation literature | sweep + Sonnet follow-up | done | data/isoshift/validation.csv 30 rows; brucite +0.31% (10.2138/am.2013.4202), LiH +0.81%, ice Ih -0.09..-0.21%; portlandite no clean pair |
| 1.4 | brucite imaginary modes | Opus | done | docs/decisions/00; K-point H off-axis branch, physical (H disorder), isotope quantity converged |
| 2.1 | validation QHA 4 models | GPU queue | running | src/isoshift_event/validate.py, results/queue/validation |
| 2.3 | DFT isotope benchmark module | Sonnet | running | src/isoshift_event/benchmark.py, MDR phonondb FCs |

## Notes
- Planning session (other Claude) stood down 15:45; this session is the only writer. Its pool fix 62f1fde is post-baseline (event-time).
- Double-well isotope-ordering idea tested on NaOH and dropped (see docs/decisions/00).
- Bond found NaOH/NaOD isotope-induced transition (PRL 131, 126101, 2023): quantum paraelectric, add as negative control.
