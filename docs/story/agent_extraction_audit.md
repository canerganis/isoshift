# How reliable were the literature agents? (PLAN.md P22)

The validation numbers came from a three-stage agent pipeline, each stage logged:
1. Sweep (11 Sonnet workers on Valency Bond, `state/sweeps/validation-lit.jsonl`), one worker per system.
2. Follow-up (one Sonnet agent, primary sources only, `data/isoshift/validation.csv`).
3. Board (Opus, Astra, Gemini read the table blind against the computed results, `docs/decisions/01-gate.md`).

## What each stage got right and wrong

| System | Sweep (stage 1) | Follow-up (stage 2) | Board (stage 3) | Final |
|---|---|---|---|---|
| Brucite V_H/V_D - 1 | "about +0.3%", without a paired lattice table | +0.31%, abstract quote, Chakoumakos 2013 (10.2138/am.2013.4202), sign confirmed by Horita 2010 | accepted | validated target |
| LiH vs LiD | values via Dammak 2012, mixed units (THz and cm-1 in one row) | +0.81% (Loubeyre a values via Dammak), +1.04% alternative from the Smith-Leider shift | flagged that the two sources disagree by 0.23% absolute (1.04 minus 0.81), so the model overestimate is 1.03 to 1.50x | validated target with two references |
| Ice Ih | value-as-temperature confusion in one row | Pamuk 2012 Table I, -0.09 to -0.21% over 10 to 220 K | caught that the conductor used -0.15% at 100 K; the 100 K value is -0.075% | reported only, models 4 to 10x too large |
| Portlandite | not found | cross-lab estimate +0.67% (XRD vs neutron, different pressures) | ruled uninformative: inter-lab offset is 3x the effect | null check, not a target |
| MgH2 vs MgD2 | marked "ok" without paired H/D numbers | nothing found (paywalled) | not used | dropped |
| KOH/KOD, KDP/DKDP, NaOH/NaOD, delta-AlOOH | numbers via citing papers, primary papers unopened | kept as secondary, harmonic_tractable = no | used as negative controls only | negative controls |

Counts: of 11 sweep items, 9 returned "ok", but only 2 (brucite, LiH) survived as quantitative validation targets after stages 2 and 3; 1 sweep "ok" (MgH2) had no usable number; 1 reference value used by the conductor (ice) was wrong by a factor of 2 and was caught by the board. No number in the final table is unsourced.

## One full trace (brucite)
1. Two Bond sweep queries on brucite (`logs/bond_queries.jsonl` lines 2 and 3; sweep rows record only the query and the result count, not the papers returned).
2. Stage 1 worker reports "about 0.3%, sign D smaller" without a quote; its note names Horita 2010 but saw abstracts only (`state/sweeps/validation-lit.jsonl` line 1).
3. Stage 2 agent finds the abstract sentence giving 0.31% larger volume for Mg(OH)2 at room temperature and records DOI and quote. Chakoumakos 2013 has no matching row in the Bond log, so this step is not traced to a Bond query.
4. GPU: QHA with four models gives +0.22 to +0.34% (`results/raw/validation/`), later +0.19 to +0.44% over four imaginary-mode treatments with Gamma acoustic modes removed (gate follow-up G2).
5. Board ruling (01-gate): brucite sign right in 4/4 models under every treatment, tier B passes.

Lesson for the write-up: single-pass agent extraction was useful for finding sources but not trustworthy for numbers (1 of the 9 "ok" rows, MgH2, had no usable value, only 2 of the 9 became quantitative targets, and one reference value was off by 2x). The second-reader and board stages are what made the table usable.

## Bond log breakdown and provenance (decision 13 action 5)

Counts recomputed by `python -m src.isoshift_event.bond_counts` from `logs/bond_queries.jsonl`: 182 rows = 85 sweep rows (27 validation-lit, 58 candidate-lit; no timestamp or purpose) + 97 agent rows with a purpose: 20 prior-art check for the "first" claim (council 11), 26 atlas test plus 1 re-log of an atlas query, 9 ice boundaries, 41 other validation, band, fractionation and novelty lookups.

Not every measured value came through Bond. The table gives, for each cited measurement, the log lines whose text contains its DOI or author name (searched by the script above); "no matching log row" means the source was reached another way (sweep output, follow-up agent, web or publisher page) or the query was logged without the paper it returned.

| finding | measured value | source (DOI) | Bond log line |
|---|---|---|---|
| gate (brucite) | V_H/V_D - 1 = +0.31% | Chakoumakos 2013 (10.2138/am.2013.4202) | no matching log row (brucite sweep queries: lines 2, 3) |
| gate (LiH) | +0.81% via Dammak 2012 | 10.1088/0953-8984/24/43/435402 | 1, 30 |
| F02 | alpha-AlH3 +1.08% | Turley and Rinn 1969 (10.1021/ic50071a005) | no matching log row |
| F02 | beta-CrOOH +0.06%, alpha-CrOOH -1.21% | 10.1016/0022-4596(76)90180-8, 10.1016/0022-4596(77)90130-x | no matching log row |
| F03 | ν(OH) vs O...O correlation | Libowitzky | no matching log row |
| F04 | ε-FeOOH bands | Thompson et al. 2020 (10.2138/am-2020-7468) | 112 (query logged, nothing kept; not indexed) |
| F04 | goethite bands 3111, 885 cm⁻¹ | Liu et al. 2013 (10.1016/j.saa.2013.06.102); Ruan 2002 cross-check | 109, 113 |
| F04 | δ-AlOOH, no IR stretch above 2500 cm⁻¹ | Kagi et al. 2010 (10.1088/1742-6596/215/1/012052) | no matching log row |
| F05 | goethite, brucite, manganite mineral-water 1000 ln α | Yapp 1987 (10.1016/0016-7037(87)90247-x, quoted via 10.1016/j.chemgeo.2017.10.025), Xu and Zheng 1999 (10.1016/s0016-7037(99)00047-2), Hariya and Tsutsumi 1981 (10.1016/0009-2541(81)90070-x) | no matching log row (fractionation queries without these papers: 117 to 122) |
| F07 | D2O ice triple points | Bridgman 1935 (10.1063/1.1749561), Herrig et al. 2018 (10.1063/1.5053993) | no matching log row (ice queries: 124 to 132; Mishima 2000, PMID 10991276, at 129) |
| F12 | boehmite and diaspore mineral-water 1000 ln α | Graham, Sheppard and Heaton 1980 (10.1016/0016-7037(80)90143-x) via Chacko, Cole and Horita 2001 | no matching log row (P11 queries 160 to 162 kept nothing) |
| CARD-AlOOH | δ-AlOOD neutron work, 9.0 / 13.4 / 18.1 GPa | Sano-Furukawa et al. 2018 (10.1038/s41598-018-33598-2) | 107, 110, 111, 135, 144, 159 |
| CARD-AlOOH | ε-FeOOD neutron work | Ikeda et al. 2025 (10.1021/jacs.4c11982) | 108, 110, 157 |
| prior-art check | McKenzie 2014, 2015 | 10.1063/1.4873352, 10.1063/1.4927391 | 105 (also by name 168, 170) |
| prior-art check | Bourgeois 2018 | 10.1088/1361-648X/aad259 | 1 (paper id query 169) |
| prior-art check | Du et al. 2026 | arXiv:2610.11325 | 171, 174 |

Bond extraction accuracy was not benchmarked; the counts above are screening outcomes.
