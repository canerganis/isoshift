# Paper draft: A short-bond rule for the isotope effect on polymorph stability in hydrogen-bonded crystals

Full draft, 23 Oct 2026, for ChemRxiv and arXiv (cond-mat.mtrl-sci). Author: Muhammet Can Erganiş (METU, ORCID 0009-0001-1397-6366). Branch `post-hackathon`.

Files:

* `main.tex`: the manuscript (revtex4-2, `aps,prmaterials,reprint`, two columns).
* `refs.bib`: references; every DOI was checked against Crossref, arXiv ids against arxiv.org, the Zenodo DOI against DataCite (23 Oct 2026).
* `figures/`: copies of `figures/fig_headline.png`, `fig4_xh_rule.png`, `fig5_stretch_check.png`, `fig2_pipeline_counts.png` from the repo root.
* `main.pdf`: the built draft.

`astra_draft.md` in this folder is an independent draft by another agent. It was not read or used for `main.tex`.

## Build

```
cd docs/paper
latexmk -pdf main.tex
```

MiKTeX with on-the-fly install set to "ask" hangs in a non-interactive shell when a package is missing (latexmk itself hangs without the `latexmk` package). For this build the following MiKTeX packages were installed with `miktex packages install <name>`: revtex, textcase, natbib, booktabs, kvsetkeys, kvdefinekeys, pdfescape, ltxcmds, infwarerr, hycolor, refcount, gettitlestring, kvoptions, stringenc, intcalc, bitset, bigintcalc, rerunfilecheck, uniquecounter, latexmk. A useful check for missing files: `pdflatex --disable-installer -interaction=nonstopmode main.tex`.

Build status on 23 Oct 2026: clean, 12 pages, no undefined references, one harmless nameref warning.

## TODO before submission

1. Author review of every section, the AI-use statement and the acknowledgements wording. The AI-use statement says the manuscript was drafted by Claude Opus 5.5.
2. Corresponding-author email is not in the manuscript (add `\email{}` if wanted). ORCID is given through `\homepage`.
3. The all-row stretch and bend/libration slopes per model in Table I (+0.25/-0.13, +0.26/-0.14, +0.25/-0.12) are read from the legend of `figures/fig4_xh_rule.png`, which `src/isoshift_event/fig_rule.py` computes; `results/F01_cv.json` has no all-row decomposition block. README quotes the range as +0.24 to +0.26 and -0.12 to -0.14. Recompute from `results/decompose_pairs.csv` and print exact values.
4. `figures/fig2_pipeline_counts.png` shows 38 candidates in the bracketed tier, while `docs/freeze/FREEZE_REPORT.md` lists 2 / 40 eligible candidates. The caption says those two bars are not used. Regenerate the figure or drop the two bars.
5. Ford et al. is dated 2012 in `docs/story/prior_art_recheck_2026-10-22.md`; Crossref gives Chem. Eur. J. 17 (52), 2011. The bib uses 2011. The paper describes it only by its title ("changes the phase transition"); the recheck's phrase about vibrational free energy was not verified from the paper.
6. Merz and Kupka 2015 and Ikeda et al. 2025 are cited at abstract or snippet level (prior-art recheck); full texts were not read.
7. MLIP citations: MACE is cited with the MACE-MP foundation-model paper (arXiv:2401.00096), not a specific paper for the `medium-mpa-0` checkpoint; SevenNet `7net-mf-ompa` is cited with Park et al. 2024 (SevenNet) and Kim et al. 2024 (multi-fidelity training). Confirm the preferred citations with each project's documentation. MACE, ORB, MatterSim and the multi-fidelity SevenNet paper are cited as arXiv preprints; check for journal versions.
8. Pamuk et al. 2012 is cited for the measured negative volume isotope effect of ice (from `docs/research/validation_set.md`); confirm it is the right source for the ice XI comparison in `results/validation/volume_isotope.csv`.
9. Graham, Sheppard and Heaton 1980 numbers come from the Chacko, Cole and Horita 2001 compilation (F12); the primary paper was not read.
10. F05 measured fractionation values are from secondary sources (see F05 caveats); not checked against primary papers.
11. Valency Bond and marimo have no citable reference in the repo; they are acknowledged only.
12. The query count "about 200" for the post-submission prior-art search is the sum of about 55 (round 1) and about 150 (round 2) in `docs/story/prior_art_recheck_2026-10-22.md`.
13. Consider moving Table II next to Sec. IV (float placement put it on page 9) and enlarging Fig. 1 to full width if the journal style allows.

Nothing in the paper relies on an unverified DOI.

## Number-to-source table

Abbreviations: D07 = `docs/decisions/07-freeze-wording.md`, D08 = `docs/decisions/08-post-freeze-science.md`, FR = `docs/freeze/FREEZE_REPORT.md`, JSON = `results/F01_cv.json`. Findings are in `docs/findings/`, math notes in `docs/math/`.

| Number in the paper | Where | Source |
|---|---|---|
| 220 pairs, 63 formulas, 521 clean covalent rows (MACE 188, ORB 163, MatterSim 170) | Abstract, Methods D, Table I | F01 Details; FR table ("Clean covalent rows per model", "unique_pairs") |
| 0.112 / 0.117 / 0.128 all-row slopes; 0.11 to 0.13; r 0.76 / 0.83 / 0.84 | Abstract, III A, Table I | D07 headline and "Slopes" row; F01 Details; FR |
| All-row compensation 54 / 55 / 49 %, "49 to 55%" | III A, Table I | FR ("Screen-wide compensation"); F01 Details |
| All-row stretch +0.25/+0.26/+0.25, bend/libration -0.13/-0.14/-0.12 | III A, Table I | `figures/fig4_xh_rule.png` panel b legend (see TODO 3) |
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
| 20 prior-art queries pre-submission; about 55 + 150 later | Intro | README "How AI was used"; prior_art_recheck |
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
