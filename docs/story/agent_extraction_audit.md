# How reliable were the literature agents? (PLAN.md P22)

The validation numbers came from a three-stage agent pipeline, each stage logged:
1. Sweep (11 Sonnet workers on Valency Bond, `state/sweeps/validation-lit.jsonl`), one worker per system.
2. Follow-up (one Sonnet agent, primary sources only, `data/isoshift/validation.csv`).
3. Board (Opus, Astra, Gemini read the table blind against the computed results, `docs/decisions/01-gate.md`).

## What each stage got right and wrong

| System | Sweep (stage 1) | Follow-up (stage 2) | Board (stage 3) | Final |
|---|---|---|---|---|
| Brucite V_H/V_D - 1 | "about +0.3%", without a paired lattice table | +0.31%, abstract quote, Chakoumakos 2013 (10.2138/am.2013.4202), sign confirmed by Horita 2010 | accepted | validated target |
| LiH vs LiD | values via Dammak 2012, mixed units (THz and cm-1 in one row) | +0.81% (Loubeyre a values via Dammak), +1.04% alternative from the Smith-Leider shift | flagged that the two sources disagree by 0.22% absolute, so the model overestimate is 1.03 to 1.50x | validated target with two references |
| Ice Ih | value-as-temperature confusion in one row | Pamuk 2012 Table I, -0.09 to -0.21% over 10 to 220 K | caught that the conductor used -0.15% at 100 K; the 100 K value is -0.075% | reported only, models 4 to 10x too large |
| Portlandite | not found | cross-lab estimate +0.67% (XRD vs neutron, different pressures) | ruled uninformative: inter-lab offset is 3x the effect | null check, not a target |
| MgH2 vs MgD2 | marked "ok" without paired H/D numbers | nothing found (paywalled) | not used | dropped |
| KOH/KOD, KDP/DKDP, NaOH/NaOD, delta-AlOOH | numbers via citing papers, primary papers unopened | kept as secondary, harmonic_tractable = no | used as negative controls only | negative controls |

Counts: of 11 sweep items, 9 returned "ok", but only 2 (brucite, LiH) survived as quantitative validation targets after stages 2 and 3; 1 sweep "ok" (MgH2) had no usable number; 1 reference value used by the conductor (ice) was wrong by a factor of 2 and was caught by the board. No number in the final table is unsourced.

## One full trace (brucite)
1. Bond query (logged in `logs/bond_queries.jsonl`) on deuteration and hydroxide volume returns Horita 2010 and Chakoumakos 2013.
2. Stage 1 worker reports "about 0.3%, sign D smaller" without a quote.
3. Stage 2 agent finds the abstract sentence giving 0.31% larger volume for Mg(OH)2 at room temperature and records DOI and quote.
4. GPU: QHA with four models gives +0.22 to +0.34% (`results/raw/validation/`), later +0.19 to +0.44% over four imaginary-mode treatments with Gamma acoustic modes removed (gate follow-up G2).
5. Board ruling (01-gate): brucite sign right in 4/4 models under every treatment, tier B passes.

Lesson for the write-up: single-pass agent extraction was useful for finding sources but not trustworthy for numbers (about 1 in 5 "ok" rows had no usable value, and one reference value was off by 2x). The second-reader and board stages are what made the table usable.
