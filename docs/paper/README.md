# Paper draft: A short-bond rule for the isotope effect on polymorph stability in hydrogen-bonded crystals

Revised draft (referee round 1), 23 Oct 2026, for ChemRxiv and arXiv (cond-mat.mtrl-sci). Author: Muhammet Can Erganiş (METU, ORCID 0009-0001-1397-6366). Branch `post-hackathon`.

Files:

* `main.tex`: the manuscript (revtex4-2, `aps,prmaterials,reprint`, two columns).
* `refs.bib`: references; every DOI was checked against Crossref, arXiv ids against arxiv.org, the Zenodo DOI against DataCite (23 Oct 2026).
* `figures/`: copies of `figures/fig_headline.png`, `fig4_xh_rule.png`, `fig5_stretch_check.png` from the repo root, and `fig6_accuracy.png` (new in revision, written by `src/isoshift_event/paper_stats.py`). `fig2_pipeline_counts.png` is no longer used in the paper.
* `reviews/`: referee reports (round 1) and `round1_response.md`, the point-by-point response.
* Revision statistics: `src/isoshift_event/paper_stats.py` writes `results/paper_stats.json` (run from the repo root: `.venv/Scripts/python.exe -I -c "import sys; sys.path.insert(0, '.'); import runpy; runpy.run_module('src.isoshift_event.paper_stats', run_name='__main__')"`, about 15 s).
* `main.pdf`: the built draft.

`astra_draft.md` in this folder is an independent draft by GPT-6 Astra. Round 1 of the merge (23 Oct) kept `main.tex` as the base and merged parts of it (see "Merge from astra_draft.md" below). Only numbers and references traced to repo files or verified on Crossref were taken over.

## Build

```
cd docs/paper
latexmk -pdf main.tex
```

MiKTeX with on-the-fly install set to "ask" hangs in a non-interactive shell when a package is missing (latexmk itself hangs without the `latexmk` package). For this build the following MiKTeX packages were installed with `miktex packages install <name>`: revtex, textcase, natbib, booktabs, kvsetkeys, kvdefinekeys, pdfescape, ltxcmds, infwarerr, hycolor, refcount, gettitlestring, kvoptions, stringenc, intcalc, bitset, bigintcalc, rerunfilecheck, uniquecounter, latexmk. A useful check for missing files: `pdflatex --disable-installer -interaction=nonstopmode main.tex`.

Build status on 23 Oct 2026 (after referee round 1 and the Badger 1934 citation): 15 pages, no undefined references, no overfull boxes, one harmless nameref warning and one "A float is stuck" warning (already present before the Badger edit; check that every figure and table appears where expected, or try the `floatfix` class option).

## TODO before submission

1. Author review of every section, the AI-use statement and the acknowledgements wording. The AI-use statement says the manuscript was drafted by Claude Opus 5.5 with parts merged from an independent GPT-6 Astra draft.
2. Corresponding-author email is not in the manuscript (add `\email{}` if wanted). ORCID is given through `\homepage`.
4. Figures 1, 2 and 4 keep their submitted versions; referee round 1 asked for capitalised model names, panel letters, a neutral Fig. 1 title, window n in the Fig. 3 legend and binned means in Fig. 2 (middle). Captions were corrected instead; regenerate with the repository figure scripts. `fig2_pipeline_counts.png` (38 vs 40 candidates mismatch) was dropped from the paper.
5. Ford et al.: the paper and bib use 2011 (Crossref: Chem. Eur. J. 17 (52), 14942, 2011); `docs/story/prior_art_recheck_2026-10-22.md` still says 2012 and should be corrected there. The paper describes the work only by its title ("changes the phase transition"); the recheck's phrase about vibrational free energy was not verified from the paper.
6. Merz and Kupka 2015 and Ikeda et al. 2025 are cited at abstract or snippet level (prior-art recheck); full texts were not read.
7. MLIP citations: MACE is cited with the MACE-MP foundation-model paper (arXiv:2401.00096), not a specific paper for the `medium-mpa-0` checkpoint; SevenNet `7net-mf-ompa` is cited with Park et al. 2024 (SevenNet) and Kim et al. 2024 (multi-fidelity training). Confirm the preferred citations with each project's documentation. MACE, ORB, MatterSim and the multi-fidelity SevenNet paper are cited as arXiv preprints; check for journal versions.
8. Pamuk et al. 2012 is cited for the measured negative volume isotope effect of ice (from `docs/research/validation_set.md`); confirm it is the right source for the ice XI comparison in `results/validation/volume_isotope.csv`.
9. Graham, Sheppard and Heaton 1980 numbers come from the Chacko, Cole and Horita 2001 compilation (F12); the primary paper was not read.
10. F05 measured fractionation values are from secondary sources (see F05 caveats); not checked against primary papers.
11. Valency Bond and marimo have no citable reference in the repo; they are acknowledged only.
12. Prior-art counts: 20 prior-art queries before submission are in `logs/bond_queries.jsonl` (README "How AI was used"); both later rounds ran after submission (about 55 on 22 Oct and about 150 on 23 Oct, `docs/story/prior_art_recheck_2026-10-22.md`). The suggested wording "about 55 before and about 150 after submission" is not supported, so the paper gives 20 before and the two later rounds separately, without a total.
13. Goethite band values (Liu et al. 2013) and the F05 fractionation equations (Xu and Zheng 1999, Yapp 1987, Hariya and Tsutsumi 1981) are cited as attributed in the repo data files; none of these primary papers was read in full.
15. Items needing new computation are listed at the end of `reviews/round1_response.md` (PIMD or SSCHA control, DFT double differences, re-relaxation, mesh convergence, AlOOH pressure detail, dilute-D supercells, 250 and 350 K).
16. Title: both referees suggest narrowing it ("trend", "inorganic"); kept as the working title pending the author's decision.
14. Consider moving Table II next to Sec. IV (float placement put it on page 9) and enlarging Fig. 1 to full width if the journal style allows.

Nothing in the paper relies on an unverified DOI.

## Number-to-source table

Abbreviations: D07 = `docs/decisions/07-freeze-wording.md`, D08 = `docs/decisions/08-post-freeze-science.md`, FR = `docs/freeze/FREEZE_REPORT.md`, JSON = `results/F01_cv.json`. Findings are in `docs/findings/`, math notes in `docs/math/`.

| Number in the paper | Where | Source |
|---|---|---|
| Formula-clustered bootstrap slope intervals 0.068 to 0.154, 0.083 to 0.165, 0.090 to 0.169; Theil-Sen 0.061, 0.111, 0.109; LOO-formula ranges; O-H-only slopes 0.124, 0.135, 0.145; 41 non-O-H rows; Al(OH)3 43 of 188 MACE rows | Abstract, III A, Table I | `results/paper_stats.json` `slopes_all_rows` |
| Structure-level fixed-effects slopes 0.120, 0.116, 0.126 with intervals; 167 structures, 55 formulas | III A, Table I | `paper_stats.json` `structure_level_fixed_effects` |
| 27 of 28 formulas (Al(OH)3 wrong); 89 structures; top five formulas 129 rows (39, 31, 28, 16, 15); formula-equal-weight 0.92 (0.85 to 0.98) vs 0.49; pooled 0.87 (0.68 to 0.98) | Abstract, III B, Table I | `paper_stats.json` `headline_check`, `unit` |
| Null mean 106, sd 10.7, max 154 of 2e5 draws, p < 1e-5 | III B | `paper_stats.json` `null_pair_orientation` |
| Density 104 (LOFO 72), MLIP static energy 137, O...O 183/211 vs O-H 184, r -0.80, O...O pairs 73/1/10 | III B | `paper_stats.json` `competitors_headline_rows` |
| 151/159 vs 34/53; 19 of 74 pairs disagree; median spread 1.36 vs median abs ddF 2.37; 81/81, 42/43, 53/78 by spread | Abstract, III B, Fig. 5 | `paper_stats.json` `accuracy_vs_abs_ddF_meV_per_H`, `model_spread` |
| Flags: classical limit 17/42 vs 168/170, 0 K unflagged 153/170; relax-not-converged 119 rows; soft-mode 161 rows | III B, III D, III G | `paper_stats.json` `flags_headline_rows` |
| Coverage curve: 185/229 at 0.98, 114/114 at 1.02 | III B, Fig. 5 | `paper_stats.json` `accuracy_coverage_rmax` |
| Multiverse: rmin 138/144 (100; 56/0/0), rmean 177/188 (114; 74/5/0), O...O 185/222 (141), 3 mÅ 203/232 (141), 10 mÅ 165/188 (120) | III B | `paper_stats.json` `multiverse` |
| Cleaner subset: converged 86/93 (pairs 45/7/0, baseline 66); converged and no imaginary 35/36 (27/0/1, 9 formulas, baseline 28); slopes 0.206 (MACE, 30), 0.146 (MatterSim, 24) | III D | `paper_stats.json` `physically_cleaner_subset` |
| Weak side 18 of 20 reversed; pairs 1/0/12; formulas 1 right, 6 wrong; slopes -0.27, -0.058, -0.014; prospective 2/9 | Abstract, III E | `paper_stats.json` `weak_side`; F11 section 5 |
| AlOOH QHA isotope term 2.30/2.42/2.22 and 1.86/2.30/2.50 meV/atom; MatterSim Pt 15.14 GPa; conditional 265 to 363 and 66 to 90 per mil | III I, Discussion | `paper_stats.json` `alooh`; `results/card_alooh_pressure.json`; `results/card_alooh_temperature.json` |
| Three-model volume isotope effects brucite +0.19 to +0.33% (290 K), LiH +1.03 to +1.27% (300 K) | II C | `paper_stats.json` `volume_isotope_three_models_pct` |
| 569 (three models) and 572 (with SevenNet) pairs with a screen result | II D | `paper_stats.json` `pairs_with_screen_result` |
| mp-985293 MatterSim compensation 0.95 to 1.02; partner volumes 7.53 to 7.88 | III B | `paper_stats.json` `mp985293` |
| One-mode estimate 4 to 34% high; 1/sqrt2 overstates by 8% (zero point), about 6% (high-T slope) | III H, Conclusion | `paper_stats.json` `analytic`; Astra report item 32 for the 6% |
| 1.5e-4 relative accuracy of the 300 K bracket | III H | Astra report minor item (1.47e-4 relative at 3000 cm⁻¹) |
| SevenNet LiH TO(H) 20.41 vs 17.7 THz (15.3%), MACE 19.97 THz (12.8%) | II C | `results/validation/tier_a.csv` |
| Mesh rule about 60/a points, even, 4 to 16 | II C | `src/isoshift_event/refine.py` lines 29, 55 |
| F11 clean rows pair majority 5/1/4 | Table II, IV, Conclusion | `results/post_freeze/F11_prospective.json` `primary_per_protocol_clean_only` |
| F12 at 380 °C: +42.5/+30.3/+41.3 per mil; 2 and 4 kbar | IV | F12 |
| Database-geometry sign agreement 69% vs 86% (pre-freeze) | Discussion | F01 superseded section "Structure-only use with database geometries" |
| 220 pairs, 63 formulas, 521 clean covalent rows (MACE 188, ORB 163, MatterSim 170) | Abstract, Methods D, Table I | F01 Details; FR table ("Clean covalent rows per model", "unique_pairs") |
| 0.112 / 0.117 / 0.128 all-row slopes; 0.11 to 0.13; r 0.76 / 0.83 / 0.84 | Abstract, III A, Table I | D07 headline and "Slopes" row; F01 Details; FR |
| All-row compensation 54 / 55 / 49 %, "49 to 55%" | III A, Table I | FR ("Screen-wide compensation"); F01 Details |
| All-row stretch +0.245/+0.259/+0.252, bend/libration -0.133/-0.142/-0.124 (n 188/163/170) | III A, Table I | `results/decompose_pairs.csv`, rows clean==True and covalent_XH==True, OLS of ddF/H_per_atom (ddF_total, ddF_str, ddF_perp) on 1000·dXH_mean_A; recomputed by the conductor and re-checked here (same values, total 0.112/0.117/0.128) |
| Median |dO-H| between MP O-H polymorphs 4.1 mÅ (database geometries) | III A | F10 Counts paragraph |
| m_H 1.00782503 u, m_D 2.01410178 u | Methods A | `src/isoshift_event/decompose.py` line 31 |
| 500 relaxation steps | Methods C | `src/isoshift_event/screen.py` lines 110, 661 |
| 600 K quadrature check 190/212, 24 of 28 mp-985293 rows; sign agreement 212/212 at every T | III E | F09 Results |
| ħω/kT about 2.5 at 2000 K, stretch near 5000 K | III E | F09 H4 |
| F04 comparator: 2600 to 3100 band midpoint; Mashino two maxima 2800 to 2900 and 3300 to 3400 cm⁻¹ | IV | F04 (Interval on the stretch); F04-source-audit (b) |
| F05: 2 scored pairs; ratios 1.6 and 0.7 for manganite pairs | IV | F05 Result and Scores (iii) |
| F06: 20 rows, 9 referenced, 11 not | IV | F06 Numbers |
| F11 precommitted baseline 5/24 on clean rows | IV | F11 section 1 |
| 1.1 to 1.3 meV per H for 10 mÅ | III A | derived: 10 × 0.112 to 0.128 |
| Strong-regime slopes 0.132/0.136/0.147, stretch 0.277/0.308/0.293, perp -0.145/-0.171/-0.146, compensation 0.52/0.56/0.50 (0.524/0.557/0.498), n 97/97/99 | III A, Table I, Fig. 1 caption | JSON `oh_strong_slopes`; D07 |
| 185/212, 84 pairs, 28 formulas, baseline 131/212 | Abstract, III B, Table I, Conclusion | JSON `oh_unfiltered_strong`; D07 headline |
| Per model 52/68, 64/73, 69/71 | III B, Table I | JSON `oh_unfiltered_strong.per_model` |
| Pair majority 74 right, 0 ties, 10 wrong; all contain mp-985293 | Abstract, III B | JSON `unique_pair_majority`; D07 |
| SevenNet 10/10 (baseline 7/10); 195/222 vs 138; 75 pairs right, 10 wrong; 23 rows, slope 0.10 | III A, III B | D07 SevenNet slot; FR SevenNet line; fig4 legend |
| No threshold 187/232 (81%) | III B | D07 statistics sentence; JSON `no_threshold` |
| Nested CV 183/210 vs 131; 1.00 Å in 30 of 31 folds; Al(OH)3 fold 8/28 vs 19 | III B, Fig. 1 caption, Methods E | D07; JSON `nested_threshold_cv` |
| Grid 0.97 to 1.03 Å, 0.01 steps, right minus wrong, lowest wins ties | Methods E | F01 Details ("Nested threshold re-choice") |
| O...O ≤ 2.93 Å: 187/241 (78%) vs 61% | III B | D07; F01; FR |
| mp-985293: 28 atoms, P2₁2₁2₁, MP experimental, no imaginary modes; mean O-H 0.996/0.997/0.999 Å; donors 0.987 to 1.005 Å; O...O 2.77 to 2.82 Å; 6.79 to 6.94 vs 7.54 to 7.88 Å³/atom | III B | F01 Details ("The counterexample structure"); D07 |
| Compensation 95 to 132%; MACE 1.19 to 1.32, ORB 1.02 to 1.14, MatterSim 0.95 to 1.03; median 0.50 elsewhere | III B | F01 Details; D07 |
| MACE 0/10, ORB 0/9, MatterSim 8/9; MatterSim |ΔΔF| ≤ 0.26 meV per H | III B | D07; F01 |
| 42 flagged rows, 28 mp-985293 rows; flag definition |ΔΔF(2000 K)| > |ΔΔF(600 K)| | III B | F01 Details ("Numerical quality"); D08 (refine.py line 184) |
| Post hoc 177/184 and 175/182; 28 of 30 rows between 0.99 and 1.00 Å | III B | F01 Details ("Post hoc locator"); JSON `posthoc_locators` |
| Weak side 2/20, 13 pairs, 7 formulas | Abstract, III C, Fig. 2 caption | D07; F01 |
| F03 ratios 0.91/0.92/0.92; CIs 0.67 to 1.07, 0.82 to 1.01, 0.81 to 1.02; donors 52(18), 58(20), 58(17); span 1646 cm⁻¹; corrected 1.00 to 1.22; sign change at 1.9 to 2.3; outer 0.67/2.61/1.46; regime to 2.93 Å | III D, Table I | F03 (current statement and windowed table); `results/stretch_check_summary.json` |
| Libowitzky curve spans 170 cm⁻¹ from 2.80 to 3.10 Å | III C | F03 (sensitivity and limits) |
| Libowitzky formula ν = 3592 - 304e9 exp(-d/0.1321) | Methods F | F03 |
| 27 PBEsol donors | Fig. 3 caption | F03 table; `figures/fig5_stretch_check.png` |
| 153, 185, 210 of 212 at 0, 300, 600 K; per model 44/68, 54/73, 55/71 and 67/68, 73/73, 70/71; baselines 145, 131, 114 | III E, Table I | F09 Results; D08 rank 1 table |
| mp-985293 rows 0, 8, 28 of 28 | III E | F09 Results |
| H1 98/212; C falls in 198/212; median C 0.665, 0.582, 0.406; ~39% drop | III E | F09 H1 |
| H2 28/28; H3 max 2.6e-11 per H; H4 211/212 (bar 202), initial 124/212 | III E, Table II | F09 verdict table and Disclosure |
| Crossovers MACE 431 to 506 K, ORB 317 to 406 K, MatterSim mostly below 300 K | III E | F09 ("Crossover temperatures") |
| Shorter-O-H phase has larger H trace in 212/212 | III E | F09 H4 |
| ρ = 1.373607, 1/ρ = 0.728010, 7% overstatement with 1/√2 | III F | M03 ("One harmonic mode") |
| S_str = 0.016861 s; 5e-5 accuracy for 3000 to 3600 cm⁻¹ | III F | M03 ("Stretch slope") |
| s = 19.0/19.3/19.5 cm⁻¹ per mÅ, r -0.99 to -1.00, 17 to 21 in narrower windows; S_str 0.32 to 0.33; 5 to 30% high | Abstract, III F | M03 |
| s_b ≈ s/4, ~5 cm⁻¹ per mÅ per bend | III F | M03 ("Bends and librations") |
| Weights 1.000/0.988; 0.941/0.687; 0.858/0.556; f 0.50/0.48/0.38; net slope 0.15/0.16/0.19 | III F | M03 ("Temperature") |
| O-H/O-D measured ratio 1.33 to 1.36 | III F | M03 ("Assumptions") |
| δ-AlOOH 9.0 / 13.4 GPa, +4.4 GPa, symmetrization 18.1 GPa | Intro, III G | F04-source-audit Action 2; CARD-AlOOH caveats |
| AlOOH O-H longer by 24 to 32 mÅ, O...O shorter by 60 to 90 mÅ | III G | CARD-AlOOH ("Mechanism") |
| ΔΔF +0.52/+0.77/+0.83 meV/atom; ΔV -0.30 to -0.32 Å³/atom; +0.3 to +0.4 GPa | III G | CARD-AlOOH ("Numbers") |
| P_t 8.76 / 13.00 GPa; ΔP +1.33 (MACE), +1.13 (ORB); 4.2 GPa apart | Abstract (about 1 GPa), III G | CARD-AlOOH table; writeup.md |
| +0.99 GPa MatterSim 300 K; +0.94/+0.81/+0.73 GPa at 1000 K | III G | CARD-AlOOH temperature table; `results/card_alooh_temperature.json` |
| Goethite to ε-FeOOH +0.2 to +0.5 GPa | III G | CARD-AlOOH temperature section |
| 836 structures, 965 pairs, 572 with screen result | Methods D, Fig. 4 | README Method item 3; `figures/fig2_pipeline_counts.png` |
| 4421 MP entries, 21 Oct 2026; JARVIS snapshot 24 Sep 2025, 3436 entries | Methods D | DATA_SOURCES.md; PROVENANCE.md; `data/isoshift/PAIRS.md` |
| StructureMatcher 0.2 / 0.15 / 5°, symprec 0.05, ≤ 25 meV/atom, ≤ 32 atoms | Methods D | `data/isoshift/PAIRS.md` |
| Covalent cut 1.3 Å | Methods D | `src/isoshift_event/decompose.py` (COVALENT_CUT) |
| fmax 1e-4 eV/Å, supercell ≥ 9.5 Å and ≤ 160 atoms, displacement 0.01 Å | Methods C | `src/isoshift_event/screen.py` lines 144 to 150; `isoshift/phonons.py` line 83 |
| Γ-free refined mesh | Methods C | `src/isoshift_event/refine.py` docstring |
| Clean = 0.01 meV/atom; |ω| vs 0.1 THz | Methods C | D07 numerical-quality sentence; F11 section 3 |
| Six-point Gauss-Legendre | Methods B | `src/isoshift_event/decompose.py` line 63; M01 (6) |
| Checkpoints and package versions | Methods C | DATA_SOURCES.md (model checkpoints) |
| SevenNet LiH TO(H) 15.3% off | Methods C | README Method item 2 and Results |
| Benchmark: 40 entries (36 SevenNet); ZPE MAE 0.7/1.1/1.3/1.5; F300 0.5 to 1.1; stretch 28 to 45 cm⁻¹ | Methods C, Table I | README Benchmark; `results/benchmark/summary.csv` |
| Brucite +0.19 to +0.44% vs +0.31%; LiH +1.02 to +1.27% vs +0.81/+1.04%; ice 4 to 11× | Methods C | README Results table |
| 182 Bond queries | Methods H | writeup.md; README "How AI was used" |
| One inequivalent H site in diaspore and δ-AlOOH model phases | Discussion | README "How to test it" ("as in diaspore and δ-AlOOH"); M02 limiting case 5; D08 (one H site in the diaspore and boehmite models, spglib) |
| 20 prior-art queries before submission; about 55 and about 150 in two rounds after | Intro | README "How AI was used"; prior_art_recheck (rounds 1 and 2) |
| 115 metal hydrides | Intro | prior_art_recheck; README Prior work |
| F02: AlH3 1.3 to 1.5× | IV, Table II | F02 |
| F04: -260 (-511 to -11) vs -273; +290 vs +195; ratio 1.1 vs 0.7 | IV | F04 conclusion |
| F05: 118 structures; 6/6 signs; 190 to 300 vs 22 to 46 ‰; 5 to 10×; brucite O-H 0.971 Å | IV, Discussion | F05 |
| F07: models -12 to -140 MPa vs +12 to +15 MPa; II-III factor 2 to 3; ice XI 7 to 9% too dense | IV, Discussion | F07 |
| F11: 111 rows, 42 pairs, 20 formulas; 16 right, baseline 5; 87 lost (69 + 18); ceiling 21.6%; clean 16/24 vs 19/24; slope 0.181, C 0.44; secondary 21/120, 21/21 clean | IV, Table II | F11 sections 1, 6; README addendum |
| F12: +75.6/+37.3/+67.9 ‰; +28.8 ‰ at 380 °C; 25% exchange | IV, Table II | F12 |
| F06: 9 rows, 1e-9 meV/atom, 9/9 | IV, Table II | F06 |
| F08, F10 (1796 pairs, 0 of 26) | Table II | F08 verdict; F10; README scorecard |
| Prediction commits 0fffc54, da560cf, c990f11, f3ac0ac, 90ad4cd, bec68d7, cdb32da, d991991, d03f8d2, eb61ccf, 184fbee | Table II | README "Prediction scorecard" |
| M02 bridge, R = 0 for one H site, R ≈ (n_H k_B T/2)[Var_b - Var_a] | Discussion | M02 ("Trace-D versus full substitution", erratum) |
| +1.2 GPa ↔ +359 ‰ at 300 K | Discussion | M02 test case 1 |
| Zenodo DOI 10.5281/zenodo.23578412, v1.0.0 | Data availability | README; DataCite record |

## Merge from astra_draft.md (round 1, 23 Oct)

Merged into `main.tex`, rewritten in the paper's voice:

* Methods A: what the static-gap cancellation does not remove (force constants, geometry, anharmonicity); the explicit dynamical matrix and the H and D masses used; the quasi-harmonic minimization G_X(T,P) used for pressure shifts, kept separate from the harmonic screen.
* Methods B: the decomposition written as a sum, the perpendicular term described as an operational component, and C ill conditioned near a zero stretch term.
* Methods C: 500-step relaxation limit, non-convergence flagged not excluded.
* Methods G: the temperature rescoring stated as retrospective, because the 0, 600 and 2000 K free energies predate the hypotheses; prospective test fixed before phonons.
* Results A: slopes are associations across pairs, not derivatives of one structure; covalent O-H length and O...O distance not to be conflated.
* Results E: 600 K quadrature check (190/212, 24/28) and sign agreement of the two routes; 2000 K described as a sign test, not a classical limit.
* Tests: F04 comparator caveats (band midpoint, unconfirmed goethite bands, Mashino's reading); F05 sources, 2 scored pairs, order assembled across windows, 5 to 10 times only for brucite minus goethite; F11 framed as attrition plus insufficient skill on the surviving rows, with the precommitted baseline (5/24) separated from the after-the-fact constant (19/24); F06 20 rows with 11 unreferenced.
* Discussion: the exception and the fixed-geometry temperature change as evidence that bond length cannot stand for the whole free energy; model spread is not a confidence interval; clean is narrower than physical stability; the full M02 treatment of R (trace vs full substitution, conditions for R = 0, the non-additivity term, single H site in AlOOH) and both-direction brackets.
* Data availability: which analyses predate the Zenodo DOI and that M03 does not.
* AI-use statement: merge of two drafts; agent agreement is not validation.

Not taken over: Astra's abstract (it omits the analytic estimate and the test route), her structure for the tests section (main.tex already orders the same tests and keeps Table II), and nothing from her reference list that was not verified (all five new entries, Liu 2013, Mashino 2026, Xu and Zheng 1999, Yapp 1987, Hariya and Tsutsumi 1981, were checked on Crossref on 23 Oct).

### Resolution of Astra's [CHECK] marks

1. Goethite band assignments (F04). The repo cannot settle it: `docs/findings/F04-source-audit.md` read Thompson 2020 and Mashino 2026 in full but not Liu 2013 (paywalled). The paper now states the comparator is a band midpoint, the goethite values are unconfirmed and Mashino's alternative reading would reverse the stretch sign; the comparison is used only at sign level. Open (TODO 13).
2. F05 primary fractionation equations. F05 Caveats confirm that no row was checked against its primary paper. The paper says so and cites the primary papers only as attributed. Open (TODO 10, 13).
3. AlOOH substitution non-additivity. M02 gives R = 0 exactly for one H site type with no H-H coupling (limiting case 5) and lists the conditions (assumption 4); the repo README states one H site type for diaspore and δ-AlOOH, and D08 (spglib) finds one H site in the diaspore and boehmite models, so the variance term vanishes. Nothing in the repo bounds the non-additivity term N. The paper now states that a trace measurement constrains the prediction only once N is bounded. Open as a physics task, resolved as wording.
4. Zenodo contents. DataCite gives issue date 22 Oct 2026 for v1.0.0; F09 (dfacd79, b9832a1, 23b1693), F12 (42a8282) and F11 (2cd8b46, 4ea0552, 393c055) were committed on 22 Oct before the DOI commit 811277a (23 Oct 00:17); M03 (803d1a1, 23 Oct 14:26) is after it. The exact archived commit was not downloaded and checked. The paper says M03 is not in v1.0.0.
5. Author verification of manuscript, references and AI wording. Stays with the author (TODO 1).
6. Abbreviated reference metadata. Resolved: `refs.bib` carries full Crossref author lists and titles (long author lists for the MLIP and JARVIS papers are cut with "others").
