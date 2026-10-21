# IsoShift polymorph pair provenance

## Method and energy provenance

Inputs: local `mp_h.json`, `dft_3d.pkl` and (cross-check only) `jarvis_h_pairs.csv`; no refetch.
Formula equality uses pymatgen elemental reduced composition, not source formula strings.
MP pair energies are `e_form_eV`, the summary's corrected formation energies. At fixed composition, the hull reference `e_form_eV - e_hull_eV` must agree within 1e-5 eV/atom; otherwise all MP comparisons of that composition are excluded and counted. This checks snapshot consistency, not the underlying DFT accuracy. The snapshot has no per-entry thermo-type identifiers, so a common corrected summary thermodynamic scale is an explicit assumption, not independent verification.
MP raw `e_per_atom_eV` is retained only in structures.csv as `e_source_eV_atom`, with contract `e_kind=mp_total_r2scan_or_gga`; it is NEVER subtracted. Pairs instead record `energy_kind=mp_corrected_formation`, both comparison energies and both original energy IDs.
JARVIS uses only finite `formation_energy_peratom` and verified `func=OptB88vdW` (case/punctuation normalized); other or missing functionals are excluded and counted. `ehull` and raw JARVIS total energies are not used. MP and JARVIS energies are never mixed.
Background: [MP energy corrections](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/thermodynamic-stability) and [MP phase diagrams](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/phase-diagrams-pds).

## Structural identity and output

Remove oxidation states/site properties; reduce primitive cells with pymatgen `get_primitive_structure(tolerance=0.01 Angstrom)`, Niggli-reduce and sort sites. This is numerical primitive-cell recognition, not a relaxation.
StructureMatcher: ElementComparator, ltol=0.2, stol=0.15 (fraction of mean free length per atom), angle_tol=5 degrees, scale=True, primitive_cell=False (already reduced), attempt_supercell=False, allow_subset=False. Only equal primitive atom counts can match. A fit in either direction counts as identity (fit can be asymmetric near a tolerance boundary). Different space groups at symprec=0.05 Angstrom block a merge; reported space groups use symprec=0.1 Angstrom.
Within each source choose deterministic representatives by lowest comparison energy, then numeric ID; greedily match to representatives (no transitive closure of approximate matches). Then match JARVIS representatives to MP representatives, always preferring MP. Members inherit their representative's mapping. Only one lowest-energy entry per source and canonical phase supplies comparisons.
A JARVIS-energy pair may therefore reference an MP structure. `energy_id_a/b`, `energy_a/b_eV_atom`, `energy_kind`, and `functional` preserve the actual subtraction. If both databases produce an eligible unordered pair, keep MP's gap; otherwise keep the eligible source. Do not average gaps. Stable pair IDs are the two canonical IDs in deterministic order. `a` has the lower comparison energy; exact ties use numeric energy-entry ID.
Keep gaps <=25 meV/atom (1e-8 meV floating-point tolerance), then primitive cells <=32 atoms. Tier 16 means both <=16; tier 32 is the remainder. Counts of 25<gap<=50 are before size filtering. These are source-energy prefilters: MLIP relaxation must reapply energy and structural-identity cuts. No claim of isotope switching or harmonic validity is made here.
structures.csv contains exactly the structures referenced by pairs.csv. CIFs are written as P1 without symmetry expansion and verified with ASE for species and atom count. Seven pre-event CIFs are never overwritten: reuse only if ASE verifies the same primitive atom count and StructureMatcher verifies the phase; otherwise fail before writing any output. Unreferenced existing CIFs are left on disk but are not included in structures.csv.
Per-composition caches live under `.cache/`, keyed by structure/energy inputs, implementation hash and pymatgen/spglib/numpy versions. Interrupted runs retain completed groups; stale or unreadable caches are recomputed. CSV/CIF/report content has no timestamps or cache-hit counts.

## Filter accounting

Counts of candidate pairs are per source until source duplicates are resolved. Duplicate rejection examples below are a sample of at most five per reason; no entry or pair processing is capped.

| Entry stage | MP | JARVIS |
|---|---:|---:|
| Entries read | 4421 | 93902 |
| Excluded: no H or contains C | 0 | 90466 |
| Malformed before composition established | 0 | 0 |
| After H/no-C filter | 4421 | 3436 |
| Malformed after composition established | 0 | 0 |
| Dropped partial occupancy | 0 | 0 |
| After occupancy/geometry check | 4421 | 3436 |
| Dropped missing/nonfinite energy | 0 | 0 |
| Dropped untrusted functional | 0 | 0 |
| Energy-eligible entries | 4421 | 3436 |
| Within-source duplicates | 19 | 339 |
| Unique after within-source dedup | 4402 | 3097 |
| Source phase representatives after cross-source dedup | 4402 | 3096 |
| Candidate distinct-phase pairs | 2390 | 1902 |
| Pairs after energy cut | 1811 | 600 |

Entry identities: read = excluded-composition + malformed-before + H/no-C; H/no-C = malformed-after + partial-occupancy + ordered; ordered = missing-energy + untrusted-functional + energy-eligible; energy-eligible = within-duplicates + within-unique.

| Combined stage | Count |
|---|---:|
| Cross-source representative merges | 1064 |
| Unique structures after cross-source dedup | 6435 |
| Compositions | 4783 |
| Compositions with >=2 structures | 790 |
| MP compositions with inconsistent hull reference | 18 |
| Candidate pairs before energy eligibility/cuts | 4292 |
| Excluded MP pairs: inconsistent reference | 346 |
| Pairs excluded above 25 meV/atom | 1535 |
| Of those: 25<gap<=50 meV/atom | 453 |
| Of those: gap>50 meV/atom | 1082 |
| Pairs after energy cut | 2411 |
| Excluded: cell >32 atoms | 1300 |
| Pairs after cell-size cut | 1111 |
| Duplicate pairs found in both sources | 146 |
| Final tier 16 pairs | 504 |
| Final tier 32 pairs | 461 |
| Final pairs | 965 |
| Final referenced structures | 836 |
| Unique structures not referenced by a selected pair | 5599 |

Accounting identities: candidates = untrusted-reference + above-cut + after-energy; after-energy = oversized + after-size; after-size = source-duplicate-pairs + final-pairs; final-pairs = tier16 + tier32. Within-source unique sum = cross-merges + cross-unique. Cross-unique = final-structures + unused-unique.

## Flags (pair counts)

- `proton_transfer`: 257 pairs. Any H with two O/N/F neighbors <=1.6 Angstrom and X-H-X angle >=150 degrees; or H/O/P or H/O/S compounds (conservative acid-salt family); or MOOH with M=Al/Ga/In/Fe.
- `hbond_disordered`: 37 pairs. H2O, alkali hydroxides Li/Na/K/Rb/Cs OH, or N-containing halides with H:N>=4. Flags the family even if this particular ordered snapshot has no occupational disorder.
- `molecular_h2`: 66 pairs. At least one periodic H-H separation in [0.55, 1.0] Angstrom.
- `jarvis_only`: 341 pairs. At least one canonical member has no matched MP representative.
- `theoretical`: 588 pairs. At least one input MP entry merged into either phase has theoretical=True.

Flags are unioned over merged phase members; they overlap and are not exclusions. Geometric/composition heuristics are review prompts, not evidence of proton transfer or actual disorder. Partial occupancy is dropped, so no retained pair is labeled `partial_occ_dropped`.

## JARVIS functional audit

- `OptB88vdW`: 3436 ordered H/no-C entries.

## Pre-event candidate cross-check

The old formula/space-group list cannot create or override a pair. Its unique ID pairs are mapped through the new aliases and partitioned into the categories below. Different source IDs may map to one final pair; these are baseline ID-pair counts.

- baseline_provided: 1
- baseline_rows: 2830
- baseline_repeated_rows: 0
- baseline_unique_pairs: 2830
- baseline_ineligible_entry: 0
- baseline_same_phase: 30
- baseline_retained: 824
- baseline_not_selected: 1976

## Validation compositions

### MgH2

| Input ID | Primitive atoms | Space group | Source comparison eV/atom | Canonical ID |
|---|---:|---:|---:|---|
| mp-23710 | 6 | 136 | -0.2827190725 | mp-23710 |
| mp-23711 | 12 | 60 | -0.280843483333 | mp-23711 |
| mp-568441 | 24 | 61 | -0.236801459167 | mp-568441 |
| mp-569051 | 12 | 29 | -0.2389156025 | mp-569051 |
| mp-1102038 | 12 | 205 | -0.247419289167 | mp-1102038 |
| JVASP-3687 | 6 | 136 | -0.29675 | mp-23710 |
| JVASP-12557 | 12 | 60 | -0.29467 | mp-23711 |
| JVASP-12558 | 12 | 62 | -0.18743 | JVASP-12558 |
| JVASP-36262 | 3 | 225 | -0.17341 | JVASP-36262 |
| JVASP-56088 | 24 | 61 | -0.24279 | mp-568441 |
| JVASP-86200 | 12 | 205 | -0.25802 | mp-1102038 |
| JVASP-86802 | 12 | 205 | -0.25795 | mp-1102038 |
| JVASP-146129 | 12 | 205 | -0.26635 | mp-1102038 |
| JVASP-152688 | 12 | 205 | -0.26584 | mp-1102038 |

Source-level filter accounting: {"after_energy_cut": 7, "candidate_pairs": 25, "pairs_25_to_50_meV": 8, "pairs_above_50_meV": 10}
Retained pairs: JVASP-12558__JVASP-36262 (14.02 meV/atom), mp-23710__mp-23711 (1.87559 meV/atom), mp-568441__mp-1102038 (10.6178 meV/atom), mp-568441__mp-569051 (2.11414 meV/atom), mp-569051__mp-1102038 (8.50369 meV/atom)
Space groups and source IDs permit the rutile/gamma MgH2 and AlOOH variants to be audited without inferring phase names solely from space group. Missing comparisons are accounted for by structural merges, energy eligibility, gap or cell-size cuts above.

### AlHO2

| Input ID | Primitive atoms | Space group | Source comparison eV/atom | Canonical ID |
|---|---:|---:|---:|---|
| mp-23807 | 8 | 31 | -2.61113276531 | mp-23807 |
| mp-625054 | 8 | 36 | -2.64545543656 | mp-625054 |
| mp-625152 | 16 | 62 | -2.65282558219 | mp-625152 |
| mp-625404 | 16 | 62 | -2.64212627781 | mp-625404 |
| mp-625420 | 16 | 62 | -2.61882850281 | mp-625420 |
| JVASP-12038 | 8 | 59 | -2.43011 | JVASP-12038 |
| JVASP-29781 | 8 | 36 | -2.47436 | mp-625054 |
| JVASP-29782 | 8 | 36 | -2.47433 | mp-625054 |
| JVASP-29785 | 8 | 1 | -2.29297 | JVASP-29785 |
| JVASP-29798 | 16 | 62 | -2.45103 | mp-625420 |
| JVASP-29869 | 8 | 36 | -2.4744 | mp-625054 |
| JVASP-34788 | 8 | 31 | -2.46066 | mp-23807 |
| JVASP-53396 | 8 | 26 | -2.26461 | JVASP-53396 |
| JVASP-54676 | 16 | 62 | -2.48546 | mp-625152 |
| JVASP-54695 | 16 | 62 | -2.4751 | mp-625404 |
| JVASP-90648 | 8 | 58 | -2.44848 | JVASP-90648 |
| JVASP-113647 | 4 | 166 | -1.60623 | JVASP-113647 |
| JVASP-113651 | 4 | 160 | -2.46924 | JVASP-113651 |
| JVASP-149693 | 8 | 63 | -2.44664 | JVASP-150288 |
| JVASP-149697 | 8 | 63 | -2.44664 | JVASP-150288 |
| JVASP-149723 | 8 | 63 | -2.44664 | JVASP-150288 |
| JVASP-150288 | 8 | 63 | -2.44665 | JVASP-150288 |
| JVASP-153245 | 16 | 59 | -2.18303 | JVASP-153245 |
| JVASP-153266 | 16 | 59 | -2.40159 | JVASP-154281 |
| JVASP-153293 | 16 | 59 | -2.40167 | JVASP-154281 |
| JVASP-153460 | 16 | 59 | -2.40018 | JVASP-154281 |
| JVASP-154059 | 16 | 59 | -2.40156 | JVASP-154281 |
| JVASP-154150 | 16 | 59 | -2.40215 | JVASP-154281 |
| JVASP-154281 | 16 | 59 | -2.40218 | JVASP-154281 |
| JVASP-154417 | 16 | 59 | -2.40205 | JVASP-154281 |
| JVASP-154660 | 16 | 59 | -2.40193 | JVASP-154281 |

Source-level filter accounting: {"after_energy_cut": 29, "candidate_pairs": 101, "pairs_25_to_50_meV": 21, "pairs_above_50_meV": 51}
Retained pairs: JVASP-113651__JVASP-150288 (22.59 meV/atom), JVASP-12038__JVASP-150288 (16.54 meV/atom), JVASP-12038__JVASP-90648 (18.37 meV/atom), JVASP-90648__JVASP-113651 (20.76 meV/atom), JVASP-90648__JVASP-150288 (1.83 meV/atom), mp-23807__JVASP-113651 (8.58 meV/atom), mp-23807__JVASP-150288 (14.01 meV/atom), mp-23807__JVASP-90648 (12.18 meV/atom), mp-23807__mp-625054 (13.74 meV/atom), mp-23807__mp-625152 (24.8 meV/atom), mp-23807__mp-625404 (14.44 meV/atom), mp-23807__mp-625420 (7.69574 meV/atom), mp-625054__JVASP-113651 (5.16 meV/atom), mp-625054__mp-625152 (7.37015 meV/atom), mp-625054__mp-625404 (3.32916 meV/atom), mp-625054__mp-625420 (23.37 meV/atom), mp-625152__JVASP-113651 (16.22 meV/atom), mp-625152__mp-625404 (10.6993 meV/atom), mp-625404__JVASP-113651 (5.86 meV/atom), mp-625404__mp-625420 (23.2978 meV/atom), mp-625420__JVASP-113651 (18.21 meV/atom), mp-625420__JVASP-12038 (20.92 meV/atom), mp-625420__JVASP-150288 (4.38 meV/atom), mp-625420__JVASP-90648 (2.55 meV/atom)
Space groups and source IDs permit the rutile/gamma MgH2 and AlOOH variants to be audited without inferring phase names solely from space group. Missing comparisons are accounted for by structural merges, energy eligibility, gap or cell-size cuts above.

## Rejection/merge audit examples

- cross-source duplicate: JVASP-18383 -> mp-24147 (AcH2); JVASP-42876 -> mp-861605 (AcH3); JVASP-120451 -> mp-1193238 (Ag2Te(H2O3)2); JVASP-51768 -> mp-643431 (AgH4WS4N); JVASP-145099 -> mp-1103149 (AgMoH4S4N)
- energy cut: JVASP-80722 / JVASP-138304 (AgH): 85.09 meV/atom; JVASP-138309 / JVASP-138304 (AgH): 84 meV/atom; JVASP-138307 / JVASP-138305 (AgH2): 170.03 meV/atom; JVASP-138307 / JVASP-138300 (AgH2): 173.71 meV/atom; JVASP-138307 / JVASP-138303 (AgH2): 233.75 meV/atom
- inconsistent MP hull reference: Ba5(Ga3H)2: spread 68.236 meV/atom; mp-643683, mp-2745379; BeH12(N2Cl)2: spread 7.28096 meV/atom; mp-1203786, mp-2911751; Ca(H8O5)2: spread 206.504 meV/atom; mp-626225, mp-626227, mp-626230, mp-626275, mp-626279, mp-626291, mp-626317, mp-626552, mp-626553, mp-626562, mp-626564, mp-1182334, mp-1182430, mp-3346478, mp-3346813, mp-3347217; CaAlH5: spread 33.6963 meV/atom; mp-583071, mp-654956, mp-966582; Cu2GeP2(H5O7)2: spread 7.24146 meV/atom; mp-604273, mp-1181554
- pair also found in other source: mp-1079418__mp-1188477; mp-1084805__mp-1178678; mp-1095543__mp-2659898; mp-1103290__mp-1192265; mp-1105641__mp-1188681
- primitive cell >32 atoms: mp-27540 / mp-626435 (Al(HO)3): 56, 28; mp-27540 / mp-554002 (Al(HO)3): 56, 14; mp-27540 / mp-626470 (Al(HO)3): 56, 56; mp-27540 / mp-626496 (Al(HO)3): 56, 56; mp-27540 / mp-985293 (Al(HO)3): 56, 28
- within-source duplicate: JVASP-165683 -> JVASP-87313 (Ag2PHO4); JVASP-138301 -> JVASP-138309 (AgH); JVASP-150963 -> JVASP-145099 (AgMoH4S4N); JVASP-29794 -> JVASP-29385 (Al(HO)3); JVASP-29835 -> JVASP-29833 (Al(HO)3)

## Reproduction

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_pairs.py
.venv/Scripts/python.exe -m src.isoshift_event.pairs
```

Curation and ASE round-trip checks complete when the module exits successfully. Unit tests are a separate command; this generated report does not assert their result.

Input SHA-256:
- `dft_3d.pkl`: `28e533d72b445ae58837c7d88d50f13574c51657d5ec55205d6ea0f142067b9c`
- `jarvis_h_pairs.csv`: `01e8c9c8eeb803e1fffdef66bcf49a74536c52fd2d14362b54fb06784fe4fa93`
- `mp_h.json`: `fef522f53416e4ef474ce6ddccb532c20292b37cf379620857b6836a4ebb341b`
