# IsoShift feasibility (pre-event, 2026-10-21 night)

## Environment
- `.venv`: MACE 0.3.16 (medium-mpa-0), orb-models 0.5.5 (orb_v3_conservative_inf_mpa), phonopy 4.8.3, jarvis-tools, torch 2.6.0+cu124.
- `.venv-sevenn`: SevenNet 0.13 (7net-mf-ompa), MatterSim 1.2.5, e3nn 0.6 (split because MACE pins e3nn 0.4.4). `isoshift.worker.run_job` routes jobs automatically. All weights downloaded.

## Gotchas fixed in isoshift/
- phonopy 4 `primitive_matrix='auto'` → forced `'P'`.
- ORB force constants violate the acoustic sum rule → force-constant symmetrization on by default. ORB needs `compile=False`.
- SevenNet MF-ompa: 5 to 7 GB at ~100 atoms; supercell cap 100 atoms (400 for mace/orb), OOM retry. Smaller supercells = systematic uncertainty.
- MACE float32 (float64 OOM ~960 atoms).
- QHA window default changed to (-3%, +7%); hydrides need up to +12%. Out-of-range volumes flagged.

## Results (harmonic, 300 K, D vs H from the same force constants)
| System | mace | orb | sevenn | mattersim | Note |
|---|---|---|---|---|---|
| LiH ZPE ratio D/H | 0.785 to 0.790 across models | | | | > 1/√2 as expected (Li moves) |
| MgH2 rutile vs γ, ΔΔF_iso meV/atom | -0.50 | +0.07 | +0.31 | +0.24 | mean +0.03 ± 0.36, sign not robust |
| AlOOH diaspore vs boehmite, meV/atom | | | | | **+0.39 ± 0.07 (all 4 agree), +1.58 ± 0.28 meV per H** |
Imaginary-mode flags about -1 to -2 THz for AlOOH in some models (recorded in results/).

## Brucite Mg(OH)2 QHA volume isotope effect (V_H/V_D - 1), experiment ≈ +0.31%
0 K: +0.24 to +0.43%. 300 K: mace +0.17%, orb -0.03% (partly out of window), sevenn +0.48%, mattersim +0.19%. Caveat: brucite shows imaginary modes in every model (orb -37 THz), so treat as provisional.

## Timings (RTX 4060, ≤16-atom cells)
Relax + force constants: 3 to 14 s (mace/orb/mattersim), 7 to 29 s (sevenn). 7-volume QHA: 53 to 136 s. Peak GPU 2 to 3.3 GB, sevenn up to 7.1 GB.

## Candidate pool (JARVIS dft_3d, no key)
4,388 H entries; 3,436 after excluding C; 507 compositions with ≥2 entries; 1,589 unique formula/space-group pairs. Within 10 meV/atom (formation energy): 310 unique pairs (136 compositions), 181 with both ≤16 atoms. Within 25 meV/atom: 505 unique (186 compositions), 319 with both ≤16 atoms. JARVIS ehull unusable for H compounds; use formation energy (and MP hull once the key exists). List: data/isoshift/jarvis_h_pairs.csv.

## Throughput and recommended event plan
Harmonic, 3 models: ~35 pairs/h (sevenn bottleneck). Full QHA, 3 models: ~8 pairs/h. Plan: harmonic screen of ~300 pairs with mace+orb first (~5 h), sevenn/mattersim on survivors, QHA on top 10 to 20.
