# IsoShift ledger
nThe goal and success criteria are in state/GOAL.md (Can, 21 Oct 20:30); every block is checked against it.

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
| 1.3 | pairs.py | build + Opus fixes | done | 836 structures, 965 pairs (504 tier16); sg-gated matcher, tight primitive tol (4228246) |
| 1.5 | screen.py | build + Opus fix | done | degenerate crossings fixed (8f2ff96) |
| 1.1 | validation literature | sweep + Sonnet follow-up | done | data/isoshift/validation.csv 30 rows; brucite +0.31% (10.2138/am.2013.4202), LiH +0.81%, ice Ih -0.09..-0.21%; portlandite no clean pair |
| 1.4 | brucite imaginary modes | Opus | done | docs/decisions/00; K-point H off-axis branch, physical (H disorder), isotope quantity converged |
| 2.1 | validation QHA 4 models | GPU queue | done | brucite 4/4 (+0.22..+0.34 vs +0.31%), LiH 4/4 sign, ice 4/4 negative, portlandite 2/4 (no exp pair) |
| 2.0 | tier A sanity | Opus | done (3/4 models) | equal mass, swap, classical decay, LiH TO within 15%; sevenn pending GPU slot |
| 3.1 | screen tier16 mace+orb | GPU | running | started 15:27, ~1 h |
| 5.1 | marimo app skeleton | Sonnet | done | 47def1b |
| 4.1 | analysis + refine | build + Opus | done | 7f8bc45; refine supplies identity + numerical error (median 2e-4 meV/atom) |
| 4.0 | experimental provenance | Opus | done | 192/965 pairs both observed, 126 of them tier32 -> prioritise tier32 experimental pairs overnight |
| 2.G | gate board | board workflow | done | conditional pass (P12 framing); G1-G4, F1, F3, F4 closed; G5 (LiH dZPE via benchmark) and F2 open |
| 3.2 | screen queue: tier16 mace/orb finishing, experimental pairs (192, tier32 incl.) mace/orb/mattersim, mattersim tier16 | GPU | running | 3 workers; sevenn later alone |
| 5.2 | README, PROVENANCE, LICENSE, CITATION, DATA_SOURCES | Sonnet | done | 18e663f, results placeholders |
| 4.1b | decision 02 soft-mode tier + P13 gap cut | Opus | done | d88e1d8; clean 4, bracketed 29 eligible (interim) |
| 4.3 | Bond literature + accessibility for 11 candidate families | sweep | running | state/sweeps/candidate-lit.jsonl |
| 4.2b | P11 eigenvector following, 5 experimental-family pairs | GPU | done (mace, orb) | GaOOH +2.56/+1.98, AlOOH +2.06/+2.08, FeOOH +1.95/+1.39 and -1.29/-0.71 survive at true minima; AlH3 cubic member collapses (-10.5 meV/atom, mace), signal drops 3x -> out of headline |
| 4.4 | reproduce_figures.py (main, funnel, benchmark) | Sonnet | running | |
| 6.2 | video script draft v1 | Opus | done | 31e984a, placeholders |
| 2.3b | DFT benchmark run (G5) | GPU | queued after mace drains | |
| ops | thermal: workers relaunched with 4 threads each (19:00), GPU temp alarm at 87 C | Opus | done | |
| 2.3 | DFT isotope benchmark | Sonnet | module done (aa1f6a0), GPU run queued after screen tier16 | |

## Notes
- Planning session (other Claude) stood down 15:45; this session is the only writer. Its pool fix 62f1fde is post-baseline (event-time).
- Double-well isotope-ordering idea tested on NaOH and dropped (see docs/decisions/00).
- Bond found NaOH/NaOD isotope-induced transition (PRL 131, 126101, 2023): quantum paraelectric, add as negative control.

## Status 21:45 Wed (conductor checkpoint; read with state/GOAL.md)
- Findings: F01 (rule, regime-limited; 123/130 O-H, decision 05 wording), F02 (blind volume test mixed), F03 (stretch vs Libowitzky), F04 (P02 sign-level consistency, 1 pair; P03 inconclusive), CARD-AlOOH (+1.13 ORB / +1.33 MACE GPa, exploratory) + card 2 goethite to epsilon-FeOOH (+0.40 / +0.46 GPa, extrapolated).
- Decisions: 04-discovery-claim, 05-final-claims (S6 passed; "discovery" removed from submission headings).
- Blind predictions committed: P01 (0fffc54), P02 (6a3064b, da560cf), P03 (c990f11), P04 fractionation (f3ac0ac).
- Running agents: F06 independent replication (Codex script, compare fix), F05 fractionation comparison (rule file first), F04 rewrite + card caveat (Sano-Furukawa: proton disorder 9.0 AlOOH / 13.4 GPa AlOOD).
- GPU: main queue mattersim ~300, orb ~40, then sevenn 192 (auto-chain bwna4a5e0); qha_top: mattersim AlOOH pressure QHA (6 jobs, mem 0.35). Workers run with 2-4 threads (thermal).
- Next: integrate F05/F06, final figures after Thu 12:00 freeze, write-up, video script v3, Can: public repo + video Thu 19:00.
