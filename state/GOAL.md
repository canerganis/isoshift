# GOAL (Can, 21 Oct 20:30): a real scientific discovery, shown with evidence a materials scientist accepts

Submit by Fri 23 Oct 00:30 TRT (hard stop 02:00). Every work decision is checked against this file; the conductor updates the status column after each step.

## The discovery we claim (target headline)
"Deuteration favours the crystal polymorph with shorter X-H bonds: a stretch/bend compensation law for isotope effects on polymorph stability, found by an ML-potential ensemble over hundreds of hydrogen-compound polymorph pairs, transferable across chemical families, and tested blind against measured H/D crystal data."

## Success criteria (all must hold to use the headline; otherwise fall back as noted)
| # | Criterion | Evidence | Status |
|---|---|---|---|
| S1 | Physics validated on measured isotope effects | brucite 4/4, LiH 4/4 (01-gate) | done |
| S2 | Law holds in >= 3 independent MLIPs with consistent slope | F01: slopes 0.12/0.12/0.15 meV/H per mA, r 0.78 to 0.89 | done (sevenn pending) |
| S3 | Law transfers to unseen chemical families | leave-family-out R2 0.62, sign 86% vs 67% baseline; structure-only with database geometry r 0.65, sign 69% | done |
| S4 | Blind test against measured H/D data, predictions committed first | F02: hydrides and brucite right sign, strong-H-bond oxyhydroxides wrong (low-quality data); F03: stretch-geometry relation matches measured spectra (Libowitzky) in all 3 MLIPs | partial, council 04 deciding framing |
| S5 | Mechanism explained and tied to prior theory | stretch +0.25 vs bend -0.12 meV/H per mA; McKenzie 2014/2015 | done |
| S6 | Survives a multi-model red team (final-claims board) | docs/decisions/04-final-claims.md | todo |
| S7 | One concrete experimental prediction on a real material | best real-phase pair (candidate card, P24) or NaBH4 pressure shift | todo |

Fallbacks: S4 fails -> claim the law as a computational result with the blind miss reported; S6 finds a blocking flaw -> P10(c) negative-result framing plus validated volume isotope effects and benchmark.

## Remaining plan (owner Opus unless noted)
1. Compare P01 blind predictions with measured values (S4); write docs/findings/F02-blind-test.md.
2. NaBH4 tetragonal to Pnma pressure shift prediction, then compare (S7 option).
3. SevenNet results in (GPU chain), rerun refine/decompose/analysis/rule_cv; update F01 numbers.
4. Apply the rule structure-only to all H polymorph pairs (database map) and the real-phase candidate card (S7).
5. Final-claims board (Opus, Astra, Gemini) on F01, F02 and the candidate card (S6).
6. Freeze compute Thu 12:00. Figures final, README results, write-up, video script final (story centred on F01).
7. Can: public repo go-ahead, video recording Thu ~19:00, Moment submission.
