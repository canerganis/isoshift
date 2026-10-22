# F12. Boehmite vs diaspore against measured D/H fractionation: INCONCLUSIVE (sign agrees, not scorable)

**Status: post-freeze addendum.** The frozen F01 headline of decision 07 (185 of 212, baseline 131, pairs 74 right, 0 ties, 10 wrong) is unchanged. Prediction and rule: `docs/predictions/P11_boehmite_diaspore.md`, commit 184fbee, pushed before the literature agent started. Measured rows: `data/isoshift/polymorph_fractionation.csv` (7 AlOOH rows appended by the blind agent `sonnet-p11-blind`). Queries: `logs/bond_queries.jsonl` (3 Valency Bond queries, none relevant). This is the case decision 08 calls "P11 inside F10".

## Verdict

**INCONCLUSIVE** under the predeclared rule. The only shared temperature (380 °C) has a measured difference with the predicted sign, but the source gives no uncertainty and the diaspore value comes from 25% exchange, so zero cannot be excluded at two combined standard uncertainties and the rule's incomplete-exchange clause applies.

## Prediction (from P11)

1000 ln α(boehmite - diaspore) is positive at every temperature from 25 to 450 °C in all three models: D prefers boehmite, the shorter O-H phase (mean model O-H 1.003 to 1.006 Å against 1.013 to 1.016 Å). At 300 K: +75.6, +37.3, +67.9 ‰ (MACE, ORB, MatterSim). Linear interpolation of the P11 grid to 380 °C: +42.5, +30.3, +41.3 ‰.

## Sources actually read

* Chacko, Cole and Horita 2001, RiMG 43, Appendix 4 (hydrogen isotope fractionation factors), printed p. 78, rows 25 to 27. Read by the agent from the chapter PDF as a page image. Secondary compilation of Graham, Sheppard and Heaton 1980 (and of Suzuoki and Epstein 1976 for one boehmite row).
* Graham, Sheppard and Heaton 1980, GCA 44, 353 (doi 10.1016/0016-7037(80)90143-x): **not read**. Publisher page returned 403; no open copy, no abstract in Semantic Scholar, OpenAlex or Crossref. Only abstract-level search snippets were seen.
* Alkali hydroxides (NaOH, KOH, LiOH): not attempted. Nothing to report under the E1 gate.

## Measured values (1000 ln α, mineral-water, ‰, as listed in the compilation)

| mineral | T (°C) | value | exchange | P | attribution in compilation |
|---|---|---|---|---|---|
| boehmite | 150 | -37.4 | 77 to 100% (range for the set) | 2 kbar | Graham et al. 1980 |
| boehmite | 200 | -36.2 | same | 2 kbar | Graham et al. 1980 |
| boehmite | 280 | -53.5 | same | 2 kbar | Graham et al. 1980 |
| boehmite | 380 | -49.9 | same | 2 kbar | Graham et al. 1980 |
| boehmite | 400 | -66.2 | 93% | 1 kbar | Suzuoki and Epstein 1976 |
| diaspore | 380 | -78.7 | 25% | 4 kbar | Graham et al. 1980 |

No uncertainty is stated for any row. The four Graham boehmite values are printed in one row with four temperatures; the agent paired them in listed order, which is not verified against the primary paper.

## Scoring

Only 380 °C is shared (both minerals measured at the same temperature). The Suzuoki boehmite value at 400 °C is a different study and pressure and is not paired with diaspore at 380 °C (rule clarification 2 requires a shared temperature).

Δ_meas(380 °C) = -49.9 - (-78.7) = **+28.8 ‰**, boehmite D-enriched relative to diaspore. That is the predicted sign in 3 of 3 models.

It is not scored as CONSISTENT, for two predeclared reasons:

1. No uncertainty is given, so "excludes zero at two combined standard uncertainties" cannot be evaluated (P11 clarification 1 and 2).
2. Diaspore exchange is 25%. The rule makes incomplete exchange INCONCLUSIVE unless an extrapolated equilibrium value with an uncertainty is given (clarification 3). The abstract snippet says Graham used an interpolation method for slowly exchanging minerals at 450 °C and below, so the diaspore number is probably such an estimate, but the compilation does not say how it was obtained or how uncertain it is.

The sign of Δ_meas at 380 °C does not depend on the unverified pairing: every boehmite value in the compilation (-36.2 to -66.2) lies above the diaspore value.

Magnitude ratio (reported, not scored): predicted over measured at 380 °C is 1.47 (MACE), 1.05 (ORB), 1.44 (MatterSim). That is much closer than the 4.6 to 10 overestimate F05 found for brucite minus goethite, but it rests on one unverified, uncertainty-free point with a partially exchanged diaspore.

## Honest caveats

* Secondary source only. Every number comes from a compilation page read as an image by the agent; nobody on this side has checked the page or the primary tables. Decision 08 asks for a source "actually read and checked" before any wider use; that has not happened.
* The diaspore value is the weak link: 25% exchange at 4 kbar, method of reaching equilibrium not stated in the compilation.
* Pressures differ (boehmite 2 kbar, diaspore 4 kbar). Pressure effects on D/H mineral-water fractionation of a few permil are reported for brucite at higher P; small against +28.8 ‰ but unquantified here.
* The boehmite model is MP theoretical Cmc2_1 with ordered H; real boehmite H positions are disordered or debated. ORB's boehmite relaxation did not converge. Harmonic only.
* The abstract snippet (not read in full) reportedly says that a shorter O-H...O bridge gives a more D-depleted mineral. That is the same direction F01 encodes (diaspore, stronger hydrogen bond and longer O-H, is D-depleted), but it is a qualitative statement from Graham's own paper and is not an independent number.
* The model temperature trend is monotonic (Δ falls from 25 to 450 °C); the boehmite measurements are not monotonic in temperature (-37, -36, -54, -50, -66), so no trend comparison is possible.

## What would change this

A read of Graham, Sheppard and Heaton 1980 tables (library copy) that gives the diaspore equilibrium value at one or more shared temperatures with an uncertainty, or a boehmite-diaspore calibration equation with stated error. If that difference excludes zero at 2 u_c with the positive sign, this case becomes CONSISTENT under the unchanged P11 rule.
