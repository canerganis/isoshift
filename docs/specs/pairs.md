# Spec: pairs (polymorph pair set for the H/D screen)

## Goal and why it matters
IsoShift asks where swapping H for D changes which polymorph is stable. Everything downstream (GPU screen, ranking, app, write-up) runs on the pair set this module builds. A bad pair set wastes the overnight GPU budget (duplicates of one phase screened twice, oversized cells) or poisons the science (energy gaps that mix two databases, "polymorphs" that are the same phase, disordered phases a harmonic model cannot describe). Build `src/isoshift_event/pairs.py` so that `python -m src.isoshift_event.pairs` writes:
* `data/isoshift/structures.csv` plus one CIF per structure in `data/isoshift/structs/<struct_id>.cif`
* `data/isoshift/pairs.csv`
* `data/isoshift/PAIRS.md` (provenance and counts)

Pairs = same reduced composition, genuinely different crystal structures, small source energy gap, small primitive cells.

## Interfaces other code depends on (binding, from state/LEDGER.md "Contracts between modules")
`structures.csv`, one row per unique structure:
* `struct_id`: the source id, `mp-NNN` or `JVASP-NNN`. `source`: `mp` or `jarvis`. `formula`: reduced formula (one convention for both sources, so MP and JARVIS rows of a composition compare equal). `spg`: space group number. `nsites`: atoms in the written (primitive) cell. `cif`: repo-relative path under `data/isoshift/structs/`.
* `e_source_eV_atom` (eV/atom) and `e_kind` (`mp_total_r2scan_or_gga` or `jarvis_formation`): provenance only, never used across sources.

`pairs.csv`, one row per unordered structure pair:
* `pair_id` (stable across reruns), `formula`, `struct_a`, `struct_b` (both must exist in structures.csv), `source` (the database whose energies gave dE), `dE_meV_atom` (meV/atom, b minus a, same source only), `nsites_a`, `nsites_b`, `tier` (16 or 32), `flags` (`;`-joined, empty string if none).
* Make `a` the lower-energy member so `dE_meV_atom >= 0`, with a deterministic tie-break.
* Extra columns are allowed (for example the source ids whose energies were subtracted); contract columns keep their names and meanings.

Downstream use: `screen.py` (built in parallel) runs one GPU job per structure (P3: per unique structure, not per pair) via `isoshift.pool.submit(..., cif=...)`, which ends in `isoshift.worker.harmonic_job`, reading the CIF with `ase.io.read`. Phonopy is forced to `primitive_matrix='P'`, so the CIF cell is the phonon unit cell: a non-primitive CIF multiplies supercell cost. So structures.csv should list exactly the structures referenced by pairs.csv, each CIF must round-trip through `ase.io.read` with correct species and atom count, and `nsites` must match what ASE reads.

## Inputs (already on disk, do not refetch)
* `data/isoshift/mp_h.json`: 4421 MP entries (H, no C, E_hull <= 50 meV/atom; 3542 formulas), list of dicts with `mp_id, formula, spg, nsites, e_hull_eV, e_form_eV, e_per_atom_eV, volume, theoretical, structure` (pymatgen `Structure.as_dict()`). Made by `src/isoshift_event/fetch_mp.py`. `nsites` is of the stored cell, not necessarily primitive.
* `data/isoshift/dft_3d.pkl`: pandas DataFrame, all 93,902 JARVIS dft_3d rows (filter to H, no C yourself; ~3,436 rows). Structure in `atoms` (JARVIS dict: `lattice_mat`, `coords`, `elements`, `cartesian`). Energies: `formation_energy_peratom` (eV/atom, OptB88vdW), `optb88vdw_total_energy`. Check the `func` column before trusting energies as one functional.
* `data/isoshift/jarvis_h_pairs.csv`: pre-event JARVIS candidate list (2830 rows), paired by formula and space group only, no StructureMatcher, `dEf_meV` from formation energy. Use as a cross-check, not as truth. Feasibility counts (prep/feasibility_isoshift/REPORT.md): 505 unique JARVIS pairs within 25 meV/atom, 319 with both <= 16 atoms, before any structural dedup.

## Hard rules (PLAN.md P3, P5, P6 and task)
1. Distinct structures only (P5). Use pymatgen `StructureMatcher` to decide identity, both within a source (MP and especially JARVIS hold duplicate entries of one phase) and across sources. A phase present in both databases becomes one structure, the MP one. Report the tolerances used in PAIRS.md.
2. Never subtract MP and JARVIS energies (P5). Every dE comes from two entries of one database. Dedup interacts with this: if a JARVIS pair's member was merged into an MP structure, the pair may reference the MP struct_id while its dE comes from JARVIS entries; keep that traceable (extra column) and say in PAIRS.md how pairs found in both sources are resolved.
3. MP energies: `e_per_atom_eV` across entries of one composition can come from different functionals (GGA, GGA+U, r2SCAN mixing). Pick an MP quantity that is consistent within a composition and state which in PAIRS.md and `e_kind`. JARVIS `ehull` is unusable for H compounds (REPORT.md); formation energy differences within one composition are fine.
4. Cuts: `|dE| <= 25 meV/atom` on source energies. Tier 16 if both primitive cells have <= 16 atoms, tier 32 if both <= 32 and not tier 16; larger pairs excluded. This 25 meV cut is a pre-filter: the screen re-relaxes with each MLIP, re-applies the cut on MLIP energies and dedups again after relaxation (P5, P11). Report how many pairs fall in 25 to 50 meV/atom so the cut is visible, not silent.
5. Drop structures with partial occupancy (count them; likely zero for MP, still check). Flag, do not drop, families outside harmonic validity (P17 classes): `proton_transfer` (short or symmetric H bonds, acid salts, KDP/AlOOH-like), `hbond_disordered` (ice-like, KOH/NH4Cl-like orientational disorder), `molecular_h2` (H-H contacts at molecular distance). Other flags are fine (for example `jarvis_only`, `theoretical`); document every flag's rule in PAIRS.md.
6. No silent caps or drops (P6). Every filter step has a count in PAIRS.md: entries read per source, after H/no-C filter, after partial-occupancy drop, unique structures after within-source dedup, after cross-source dedup, compositions with >= 2 structures, candidate pairs, after dE cut, per tier, flag counts, final structures and pairs. Mention a few concrete rejected examples (P6 asks to audit rejections).

## Limits
* Deterministic: same inputs give byte-identical CSVs and CIFs (sorted rows, no set-order or timestamp dependence in outputs).
* Resumable and under about 15 min wall on this laptop (CPU, single run). StructureMatcher over thousands of structures is the slow part; think about what actually needs comparing. Any intermediate cache goes under `.cache/` (gitignored), never in `data/`.
* Memory: mp_h.json is 48 MB, dft_3d.pkl 140 MB; fine to load whole.
* Files you may create or edit: `src/isoshift_event/pairs.py`, `tests/test_pairs.py`, `data/isoshift/PAIRS.md`, plus the generated outputs above. `data/isoshift/structs/` already holds 7 committed pre-event JARVIS CIFs used by `prep/` scripts: do not delete or change them. Do not edit `isoshift/`, `fetch_mp.py`, LEDGER.md or PLAN.md.
* Python: `.venv/Scripts/python.exe` (pymatgen 2026.10.16, ase, pandas, jarvis-tools installed). Run as module `src.isoshift_event.pairs` from repo root.

## Existing code you can use
* `isoshift.cache.structure_hash(atoms)`: species+cell+scaled-position hash (exact-ish identity, not a polymorph matcher).
* `isoshift.worker._read(cif)`: the reader the screen will use (`ase.io.read`); use it to verify CIFs.
* `isoshift.phonons.supercell_for_min_length(atoms, min_length, max_atoms)`: how the screen sizes supercells, useful if you want to report expected supercell sizes per tier.
* No formula from docs/math applies here (only M00, a diatomic ZPE plumbing test).

## Tests (tests/test_pairs.py, CPU, < 60 s, no network)
Cover with small synthetic structures: the same phase in a different setting or cell is merged; a genuine polymorph pair is kept; a cross-source pair never gets an MP minus JARVIS dE; MP is preferred when a phase is in both; partial occupancy is dropped; tier assignment at the 16/32 boundaries; dE sign and the 25 meV cut; determinism (two runs, identical output); written CIFs read back with ASE to the same atom count.

## Acceptance (judged from command output)
```
.venv/Scripts/python.exe -m pytest -q tests/test_pairs.py && .venv/Scripts/python.exe -m src.isoshift_event.pairs && .venv/Scripts/python.exe -c "import pandas as p; s=p.read_csv('data/isoshift/structures.csv'); q=p.read_csv('data/isoshift/pairs.csv'); print(len(s), len(q), (q.tier==16).sum()); assert len(q)>=100 and set(q.struct_a).union(q.struct_b) <= set(s.struct_id) and q.dE_meV_atom.abs().max() <= 25"
```
Reviewers also check: PAIRS.md counts add up and explain every drop; no pair mixes sources in dE; no two struct_ids in structures.csv match each other under the stated StructureMatcher settings; a second run is fast (resume) and produces identical files; known validation polymorphs present in the inputs (for example MgH2 rutile vs gamma, AlOOH variants) appear as pairs if they pass the cuts, or their absence is explained.
