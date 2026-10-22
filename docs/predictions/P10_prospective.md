Post-freeze addendum; the frozen F01 headline (decision 07) is unchanged.

# P10: prospective held-out test of the frozen F01 rule (predeclared after relax-only geometry, before any phonon job)

Decision 08, rank 2, action 4. This file and `results/post_freeze/P10_predictions.csv` are committed and pushed after the relax-only step and before any phonon job is submitted to `results/queue/p10`. Every phonon output of this test (`results/raw/p10/`, `results/post_freeze/P10_decompose_structures.csv`, `results/post_freeze/P10_scored_rows.csv`, `results/post_freeze/F11_prospective.json`) is newer than this commit. Frozen files stay byte identical. Code: `src/isoshift_event/p10.py` (subcommands `candidates`, `relax`, `predict` run before this commit; `submit`, `decompose`, `score` after).

## 1. Population (pairs never computed)

Recomputed from `data/isoshift/mp_h.json` with the atlas grouping (`atlas.py`: O-H donors, primitive cells, `pairs.py` matcher and space-group gate, |ΔE| ≤ 50 meV/atom on MP energies) and listed against `results/atlas.csv`. Kept: both phases experimentally observed (MP theoretical=False for at least one MP entry merged into the phase), both primitive cells ≤ 64 atoms, pair not in `data/isoshift/pairs.csv`, and at least one phase not screened. A phase counts as screened if its MP ID or any merged ID is in `results/screen_structures.csv`, or if it matches a screened structure of the same formula with the `pairs.py` matcher (structural check, not only IDs). Result: **98 pairs in 60 formulas, 137 structures**, identical to decision 08 (98 pairs, 60 formulas). On MP geometry, 43 pairs in 26 formulas are in the atlas strong regime with |Δ mean O-H| ≥ 5 mÅ (decision 08: 43 and 26). 29 pairs contain one phase that was screened before the freeze; the other phase is new. Lists: `results/post_freeze/P10_candidates.csv`, `results/post_freeze/P10_structures.csv`; input CIFs in `results/post_freeze/structs/input/`.

**Orientation** (same convention as `pairs.py`): a = the phase with the lower MP corrected formation energy (`e_form_eV`), ties by numeric ID; b = the other. ddF_iso(b - a) = [F_D - F_H]_b - [F_D - F_H]_a per H (`decompose.py` quadrature, as in the frozen F01 y). Positive means deuteration favours a.

## 2. Relax-only geometry

Each structure relaxed once per model with the screen's settings (`isoshift.relax.relax`, FIRE, FixSymmetry 1e-3, cell relaxed, fmax 1e-4 eV/Å, 500 steps; MACE medium-mpa-0, ORB v3 conservative inf mpa, MatterSim v1.0.0-5M; GPU, one persistent calculator per model). Relaxed structures: `results/post_freeze/structs/relaxed/<model>/<id>.extxyz` with a JSON record each; the phonon job starts from that file and relaxes again with the same settings. Converged at fmax 1e-4 including the cell: mace 13/137, mattersim 10/137, orb 0/137. As in the screen, non-convergence is flagged, not filtered. No relax failures.

Mean model O-H per relaxed structure uses the frozen `decompose.py` definition: for every H, the distance to its nearest non-H atom (fractional minimum image), averaged over all H. A full minimum-image distance is stored next to it for audit (`P10_relaxed_structures.csv`, `XH_mean_mic_A`). A pair-model row is dropped before prediction if the two relaxed structures are the same phase (`refine._same_phase`) or a structure is not covalent X-H (some H farther than 1.3 Å from every non-H atom), as in the frozen pipeline. Row status counts: ok 270, same_relaxed_structure 24.

## 3. Predictions

**Primary (frozen F01, 300 K):** eligible when rmax = the larger mean model O-H of the pair ≥ 0.99 Å and |Δ mean O-H| ≥ 5 mÅ, O-H pair, no cut on the target. Predicted sign(ddF_iso(b - a)) = sign(Δ mean O-H(b - a)): deuteration favours the phase with the shorter mean O-H. **111 eligible rows in 42 pairs from 20 formulas** (mace 39, orb 34, mattersim 38). Sensitivity at 1.00 Å: 98 rows in 35 pairs.

**Secondary (decision 08 rank 1, 600 K, no threshold):** every O-H row with |Δ mean O-H| ≥ 5 mÅ, same predicted sign, scored on ddF_iso at 600 K. **123 rows in 46 pairs from 23 formulas** (mace 43, orb 38, mattersim 42).

**Baseline (frozen, no refit):** the constant sign of ddF_iso/H over the 212 frozen headline rows, in the orientation above: 131 of 212 are positive, so the baseline predicts **+1** (deuteration favours a, the lower-formation-energy phase) for every row. For the 600 K secondary, the frozen O-H rows with |Δ| ≥ 5 mÅ at 600 K (refined column) give 123 of 232 positive, baseline **+1**. Baselines are reported; only the primary bar uses one.

**Composition of the primary set, stated before any result:** 11 of the 42 primary pairs are KP(HO2)2 and 10 are H2O (rows: KP(HO2)2 31, H2O 28); the remaining 21 pairs come from 18 formulas with 1 to 2 pairs each. KH2PO4 and the ice phases carry the screen's `proton_transfer` and `hbond_disordered` flags (ordered model cells of phases that are proton disordered or have very short hydrogen bonds in reality). Two Al(OH)3 pairs contain mp-985293, the structure behind all 10 wrong pairs of the frozen headline (orders 16 and 18); they are in the pool by its definition and stay in. In 18 of 411 relaxed structure-model entries some H is nearest to N or F rather than O; mean X-H then averages over all H, exactly as the frozen definition does.

Also listed per row: the P08 sign from MP geometry (`results/atlas.csv`, converted to this orientation), relax flags and the supercell sizes. Full table: `results/post_freeze/P10_predictions.csv` (one row per pair and model).

Eligible pairs in processing order (sign = predicted sign of ddF_iso(b - a) per model, MACE/ORB/MatterSim; `.` = not eligible in that model; P = primary, S = secondary only):

| # | pair (a__b orientation in CSV) | formula | supercell atoms | MACE | ORB | MatterSim | Δ mean O-H MACE/ORB/MS (mÅ) | rmax MACE/ORB/MS (Å) |
|---|---|---|---|---|---|---|---|---|
| 1 | mp-24022__mp-1205457 | RbH3(SeO3)2 | 48 | P -1 | P -1 | P -1 | -18.7/-19.2/-21.7 | 1.041/1.040/1.040 |
| 2 | mp-1180593__mp-706579 | KH3(SeO3)2 | 48 | P +1 | P +1 | P +1 | 45.4/54.8/51.5 | 1.093/1.092/1.094 |
| 3 | mp-24263__mp-757909 | KP(HO2)2 | 64 | P -1 | P -1 | P -1 | -29.5/-26.8/-27.9 | 1.083/1.083/1.083 |
| 4 | mp-757909__mp-695799 | KP(HO2)2 | 64 | P -1 | P -1 | P -1 | -63.1/-65.0/-63.9 | 1.054/1.056/1.055 |
| 5 | mp-757909__mp-699437 | KP(HO2)2 | 64 | P -1 | P -1 | P -1 | -37.9/-39.5/-40.6 | 1.054/1.056/1.055 |
| 6 | mp-1196989__mp-1200196 | ZnP2(H4O5)2 | 84 | P -1 | P -1 | P -1 | -20.0/-22.2/-20.6 | 1.010/1.013/1.013 |
| 7 | mp-558841__mp-728069 | FeP2HO7 | 88 | P -1 | P -1 | P -1 | -22.2/-17.0/-14.0 | 1.019/1.014/1.011 |
| 8 | mp-721062__mp-1204591 | V2Cu3H6O11 | 88 | . | P +1 | . | 3.3/5.8/2.1 | 1.000/1.003/0.999 |
| 9 | mp-24043__mp-2739191 | H2O | 96 | P +1 | P +1 | P +1 | 114.2/111.8/112.2 | 1.111/1.110/1.110 |
| 10 | mp-697111__mp-24043 | H2O | 96 | P -1 | P -1 | P -1 | -10.2/-7.9/-8.3 | 1.007/1.007/1.006 |
| 11 | mp-1198592__mp-696403 | BHO2 | 96 | P -1 | P -1 | P -1 | -15.5/-15.4/-9.0 | 1.013/1.013/1.010 |
| 12 | mp-696735__mp-2739191 | H2O | 96 | P +1 | P +1 | P +1 | 109.8/108.6/109.3 | 1.111/1.110/1.110 |
| 13 | mp-697111__mp-696735 | H2O | 96 | P -1 | . | P -1 | -5.8/-4.7/-5.4 | 1.007/1.007/1.006 |
| 14 | mp-1182406__mp-761681 | CrHSe3O8 | 104 | P -1 | P -1 | P -1 | -28.3/-29.5/-31.5 | 1.013/1.014/1.014 |
| 15 | mp-24390__mp-1194747 | CaPHO4 | 112 | P -1 | P -1 | P -1 | -52.6/-46.7/-48.6 | 1.054/1.048/1.049 |
| 16 | mp-27540__mp-985293 | Al(HO)3 | 112 | P +1 | P +1 | P +1 | 11.2/11.6/12.7 | 0.996/0.997/0.999 |
| 17 | mp-1199276__mp-542557 | CsScAs2(HO4)2 | 112 | P -1 | P -1 | P -1 | -10.6/-9.6/-9.6 | 1.013/1.013/1.014 |
| 18 | mp-985293__mp-560572 | Al(HO)3 | 112 | P -1 | P -1 | P -1 | -15.1/-15.5/-15.7 | 0.996/0.997/0.999 |
| 19 | mp-1201415__mp-1198234 | Li3V(H4O3)4 | 128 | P -1 | P -1 | P -1 | -5.8/-5.4/-6.0 | 1.009/1.009/1.011 |
| 20 | mp-23959__mp-1181168 | KP(HO2)2 | 128 | P -1 | P -1 | P -1 | -17.2/-15.1/-14.6 | 1.060/1.058/1.058 |
| 21 | mp-23959__mp-757909 | KP(HO2)2 | 128 | P -1 | . | . | -6.1/-2.0/-3.4 | 1.060/1.058/1.058 |
| 22 | mp-24109__mp-504944 | NaP(HO2)2 | 128 | P -1 | P -1 | P -1 | -50.3/-50.8/-48.7 | 1.033/1.035/1.033 |
| 23 | mp-24109__mp-697367 | NaP(HO2)2 | 128 | P -1 | P -1 | P -1 | -47.5/-48.4/-46.3 | 1.033/1.035/1.033 |
| 24 | mp-1181168__mp-24262 | KP(HO2)2 | 128 | P +1 | P +1 | P +1 | 92.1/89.2/91.7 | 1.135/1.132/1.135 |
| 25 | mp-757909__mp-24262 | KP(HO2)2 | 128 | P +1 | P +1 | P +1 | 81.0/76.1/80.6 | 1.135/1.132/1.135 |
| 26 | mp-1181168__mp-24263 | KP(HO2)2 | 128 | P +1 | P +1 | P +1 | 40.6/39.9/39.1 | 1.083/1.083/1.083 |
| 27 | mp-1196113__mp-690711 | TlP(HO2)2 | 128 | P +1 | P +1 | P +1 | 88.5/83.3/81.3 | 1.130/1.129/1.130 |
| 28 | mp-697267__mp-690711 | TlP(HO2)2 | 128 | P +1 | P +1 | P +1 | 91.0/86.3/85.0 | 1.130/1.129/1.130 |
| 29 | mp-1181168__mp-695799 | KP(HO2)2 | 128 | P -1 | P -1 | P -1 | -52.0/-51.9/-52.8 | 1.043/1.043/1.044 |
| 30 | mp-1181168__mp-699437 | KP(HO2)2 | 128 | P -1 | P -1 | P -1 | -26.8/-26.4/-29.5 | 1.043/1.043/1.044 |
| 31 | mp-1181168__mp-757909 | KP(HO2)2 | 128 | P +1 | P +1 | P +1 | 11.1/13.1/11.1 | 1.054/1.056/1.055 |
| 32 | mp-24043__mp-697085 | H2O | 144 | P -1 | P -1 | P -1 | -10.9/-9.9/-9.5 | 0.997/0.999/0.998 |
| 33 | mp-703459__mp-24043 | H2O | 144 | P -1 | P -1 | P -1 | -10.0/-8.0/-8.4 | 1.007/1.007/1.007 |
| 34 | mp-510654__mp-1200251 | Cu2PHO5 | 144 | P +1 | . | . | 7.0/4.1/1.6 | 0.992/0.991/0.986 |
| 35 | mp-1237009__mp-554651 | K3Pu(H3O4)2 | 144 | P -1 | . | . | -5.8/-3.8/-4.8 | 1.000/1.000/0.999 |
| 36 | mp-1194761__mp-557615 | K3Np(H3O4)2 | 144 | . | . | P -1 | -4.4/-3.7/-5.1 | 1.000/1.000/0.999 |
| 37 | mp-696735__mp-697085 | H2O | 144 | P -1 | P -1 | P -1 | -15.3/-13.1/-12.4 | 1.001/1.002/1.001 |
| 38 | mp-703459__mp-696735 | H2O | 144 | P -1 | . | P -1 | -5.6/-4.8/-5.5 | 1.007/1.007/1.007 |
| 39 | mp-703459__mp-697085 | H2O | 144 | P -1 | P -1 | P -1 | -20.9/-17.9/-17.9 | 1.007/1.007/1.007 |
| 40 | mp-703459__mp-2739191 | H2O | 144 | P +1 | P +1 | P +1 | 104.2/103.7/103.8 | 1.111/1.110/1.110 |
| 41 | mp-1198515__mp-766178 | Sr2Sn(HO)8 | 152 | . | . | P +1 | 3.2/4.0/5.9 | 0.994/0.996/0.998 |
| 42 | mp-23963__mp-556216 | HIO3 | 160 | P -1 | . | P -1 | -5.5/-1.4/-9.4 | 1.019/1.016/1.019 |
| 43 | mp-722516__mp-24004 | Zn2PHO5 | 144 | S -1 | S -1 | S -1 | -5.9/-7.3/-7.5 | 0.984/0.984/0.985 |
| 44 | mp-23879__mp-643392 | Ca(HO)2 | 160 | S +1 | S +1 | S +1 | 12.8/11.3/11.0 | 0.985/0.984/0.984 |
| 45 | mp-24595__mp-698170 | Ca2B5H2ClO10 | 160 | S -1 | S -1 | S -1 | -8.9/-8.9/-8.3 | 0.987/0.988/0.987 |
| 46 | mp-24595__mp-721300 | Ca2B5H2ClO10 | 240 | S -1 | S -1 | S -1 | -5.8/-5.9/-5.5 | 0.987/0.988/0.987 |

## 4. Processing order and compute

Fixed before any phonon job. Pairs with at least one primary-eligible row come first (tier 1), then pairs that are only secondary-eligible (tier 2). Inside each tier, decision 08's rule: fewest supercell atoms first (pair cost = the larger of the two members' supercell atom counts, ties by pair ID), and at least 6 formulas covered before a seventh pair from any formula. 46 pairs are ordered. Pairs with no eligible row in any model are not computed.

Phonons: `isoshift.worker.harmonic_job` through the persistent pool (`isoshift/pool.py`) on `results/queue/p10`, screen settings (`screen.prepare`): diagonal supercell with perpendicular heights ≥ 9.5 Å, at most 160 atoms (shared by the three models, computed on the input cell), Γ-centred mesh from `choose_mesh`, 0 to 1000 K grid, fmax 1e-4, 500 steps, H and D variants. Structures whose supercell exceeds 160 atoms are not computed (`shared_supercell_exceeds_160_atoms`, as in the screen): mp-697278, mp-721300, mp-759069, mp-1195120, mp-1195757, mp-1200606, mp-1202160. Jobs are submitted in batches of pairs in the committed order; MACE and ORB run concurrently (memory fraction 0.4 each, OMP_NUM_THREADS=4), MatterSim runs after them in each batch. GPU windows: until 16:30 and 20:00 to 21:30 (TRT); GPU kept under 87 C.

**Pilot:** first, the largest computable ordered pair with a primary row, order 42 (HIO3, mp-23963__mp-556216, 160 supercell atoms), in all three models, timed (order 46 has a 240-atom member and is not computable at screen settings). Batches after the pilot: 4 pairs at a time in committed order. The pilot rows are scored like every other computed pair. If the projected time passes the windows, the list is cut at the committed order; every pair after the cut is listed as not computed in F11, in order.

## 5. Scoring (F11), fixed now

* y = ddF_iso(b - a) per H from the `decompose.py` mode quadrature on a Γ-free mesh (the frozen F01 quantity), at 300 K (primary) and 600 K (secondary), computed into `results/post_freeze/` by `decompose._one` (the frozen function; F09 added only the temperature argument and regression-checked 300 K against the frozen file), called with T = 300 K and T = 600 K. Right = sign(y) equals the committed predicted sign.
* Every evaluated row is scored. A row is **not right** (kept in the denominator) if either member's phonon job failed, either member has imaginary modes in more than 2% of mesh modes (`refine.SOFT_MAX_FRACTION`; unstable), or the quadrature and the direct F_D - F_H differ by 0.01 meV/atom or more in either member (the frozen `clean` rule). Members with imaginary modes in at most 2% of modes are scored with the |ω| treatment of `decompose.py` and flagged `soft_mode_bracketed`. Rows never run (time cut or supercell cap) are listed by name in committed order and not counted.
* Unique-pair majority: per pair, the fraction of its evaluated primary rows that are right; > 0.5 right, 0.5 tie, < 0.5 wrong.
* Structure transfer: rows whose formula is in the frozen F01 population (`rule_cv.load()` families; among the candidates: Al(HO)3, H2O) are counted in the primary and also reported separately; new-formula rows likewise.
* Also reported, not scored against a bar: per-model counts, the per-protocol count (clean rows only), the 1.00 Å sensitivity, the P08 MP-geometry sign agreement, and the weak side (rmax < 0.99 Å) at 300 K.

## 6. Success bars (copied from decision 08, action 4)

* **Primary:** ≥ 30 scored evaluations in ≥ 12 pairs from ≥ 6 formulas, pooled accuracy ≥ 75%, ≥ 15 points above that baseline, and unique-pair majority right in ≥ 80% of scored pairs.
* **Secondary:** ≥ 90% at 600 K with no threshold on all O-H pairs with |Δ| ≥ 5 mÅ.
* Below 30 evaluations or 12 pairs: descriptive only.
* Gibbsite and other known-formula pairs counted and also reported separately as "structure transfer".
* Failed or unstable calculations listed by name and never counted as right.

Processing order (decision 08): fewest supercell atoms first, then ≥ 6 formulas covered before a seventh pair from any formula. A result below the baseline is reported in F11 as a failure of prospective transfer; the frozen headline changes only by a new council decision (decision 08, What would change this, item 5).
