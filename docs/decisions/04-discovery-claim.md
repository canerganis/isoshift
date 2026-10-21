# 04. Discovery claim: F01 stays the headline, narrowed to a regime-limited O-H result; F02 is reported as a separate mixed blind test

Chair: Opus, 21 Oct ~21:30 TRT. Members: Opus (high), Astra (high), Gemini 4 Argon (high, round 1 only; round 2 call failed, see the last section). Weighed by argument, not by vote. Every number this decision depends on was recomputed by the chair from `results/decompose_pairs.csv`, `results/decompose_structures.csv` and `results/stretch_check.csv` with `scratchpad/chair04_check.py` and `scratchpad/chair04_real.py` (session scratchpad, paths at the end).

## Decision

1. **F01 is a real computational regularity and stays the central finding**, but the headline is restated. It is a result for O-H-bearing solids (178 of 197 unique pairs), and it has predictive skill only when at least one polymorph has a moderate or strong hydrogen bond. Its stretch ingredient now has experimental support from measured O-H spectra. Its bend/libration compensation does not.
2. **F02 does not validate F01.** F02 passed in the weak-H-bond and hydride regime, where F01 has no skill, and missed in the strong-H-bond regime that carries F01. The phrase "tested blind against measured H/D crystal data" is removed from the F01 headline. F02 is reported on its own as a mixed blind test. S4 is marked "blind test done, mixed; does not test F01".
3. **The decisive test for question (2) is the stretch-frequency check against the Libowitzky ν(OH) vs d(O...O) correlation.** It has run. In the 2.50 to 2.80 Å window the three models reproduce the measured slope to within 10% (f = 0.91, 0.92, 0.95 by OLS; 0.98, 0.93, 0.98 by Theil-Sen). F01 changes sign only if the models over-steepen the stretch slope by f ≈ 1.9 to 2.3. MDR/phonondb is dropped as a test (1 PBEsol donor in the window, and it shares the PBE bias). Restricting to weak H bonds is rejected: the rule fails there.
4. **The one remaining experimental test before freeze** is a predeclared matched differential spectroscopy comparison (stretch and OH bend) on one or two real oxyhydroxide polymorph pairs that are already cached. It is the only test of the compensation term that fits the time. D/H fractionation is optional and exploratory.
5. **The user-facing predictor becomes mean d(O...O)**, which X-ray gives without locating H. O-H length stays the mechanism variable. This also removes the model-derived O-H vs O...O map from the experimentally anchored part of the claim.

### Wording to use

**Headline (replaces the GOAL target headline):**
"Deuteration favours the polymorph with the shorter O-H bonds once hydrogen bonds are moderate to strong: in three universal ML potentials over 197 hydrogen-compound polymorph pairs, a stretch term is half cancelled by bend and libration, and the stretch ingredient reproduces the measured O-H frequency vs O...O correlation."

**F01 (Result paragraph):**
"In three universal MLIPs, the harmonic H/D free-energy difference between polymorphs rises by 0.12 to 0.15 meV/H per mÅ increase in mean X-H length (197 unique pairs, 341 model evaluations, 178 pairs O-H bearing). A stretch term (+0.24 to +0.26) is about half cancelled by bend/libration (-0.11 to -0.13). The models' O-H stretch frequencies follow the slope of the measured Libowitzky ν(OH) vs O...O correlation within 10%, at a roughly uniform offset. When at least one polymorph has a mean model O-H length of 0.99 Å or more, the sign of the length change predicts the sign of the isotope shift in 128 of 134 model evaluations (65 of 70 unique pairs by model majority, 5 ties, constant-sign baseline 84/134). When both polymorphs are below that threshold the rule has no skill (1 of 16, 13 unique pairs). The threshold was found after looking at the data. Non-O-H support is anecdotal (19 pairs, 6 sign tests, 6 right). Experimental polymorph isotope free energies remain untested."

**F02:** Astra's wording, plus one line.
"Prediction-first volume-isotope comparisons show mixed transferability: α-AlH3 has the correct sign with a 1.3 to 1.5x overestimated magnitude; GaOOH and β-CrOOH disagree in sign with references of limited comparability. Earlier brucite and LiH checks reproduce the measured sign, while ice shows a large quantitative error. The misses lie in the strong-H-bond regime, where harmonic quasi-harmonic treatment omits Ubbelohde-type proton anharmonicity. These results do not identify a unique failure mechanism."

**Fallback (if the spectroscopy test challenges the mechanism or the final-claims board rejects the regime framing):**
"A reproducible ML-potential ensemble trend in polymorph isotope free energies of hydroxides, with a stretch-frequency ingredient consistent with measured O-H spectra. Prediction-first volume-isotope tests show where today's universal MLIPs transfer (hydrides, weak H bonds) and where they do not (strong H bonds)." This is GOAL fallback "S4 fails" in substance; P10(c) applies only if S6 finds a blocking flaw.

## Why

**(1) Real result or shared MLIP artefact.** A shared bias could produce F01 only by distorting the slope of stretch frequency against H-bond geometry, since F01's stretch term is that slope times the isotope ZPE factor (structure-level stretch slope 0.22 to 0.26 equals the pair-level 0.24 to 0.26). A uniform overbinding moves points along the curve and leaves the slope alone. The stretch check measures exactly that slope against experiment and finds f ≈ 0.9 to 1.0. The sign margin is about 2x: holding the perpendicular term fixed, the total slope reaches zero at q = 0.52 (MACE), 0.53 (ORB), 0.43 (MatterSim), the ratios of the fitted perpendicular to stretch slopes (chair recompute: 0.128/0.244, 0.133/0.253, 0.110/0.257).

Astra's objection was weighed and partly upheld. Libowitzky correlates frequency with O...O, not O-H length, so the check validates dν/d(O...O), and F01's coefficient per mÅ of O-H still inherits the model's O-H vs O...O relation. Hence the switch of the user-facing predictor to d(O...O) (Decision 5). A second caveat the chair adds: the comparison is model harmonic against measured fundamentals, and the harmonic-minus-fundamental gap grows with H-bond strength. Across the window the Libowitzky curve spans about 1640 cm-1 (≈1760 at 2.50 Å to ≈3400 at 2.80 Å). A gap growing from 150 to 300 cm-1 makes the true harmonic slope about 0.91 of the fundamental slope; even a 400 cm-1 change gives 0.76, so the model over-steepening would be at most about 1.25x. That is well inside the 2x margin. The near-zero median residual (-39, -10, -58 cm-1) then means the models sit roughly 100 to 250 cm-1 below the true harmonic stretch at fixed O...O, the overbinding seen in F02 and ice.

What the check does not settle: the per-structure RMS residual (152 to 197 cm-1, about 2.6 to 3.3 meV/H in a one-stretch estimate, Astra) is larger than one 10 mÅ step of F01. Part of it is scatter of the cross-mineral Libowitzky fit itself, and offsets cancel in pairs, but individual pair ddF values are not experimentally pinned. Only the trend is. The bend/libration term that halves the slope has no experimental anchor.

**(2) Why the weak-H-bond restriction is rejected.** It was the natural fallback in round 1 (Astra, Argon). The data contradict it. Chair recompute at |dX-H| ≥ 5 mÅ and |ddF| > 0.1 meV/H:

| Max model mean X-H of the pair | Strong side right | Weak side right |
|---|---|---|
| 0.98 Å | 128/148 (81 pairs) | 1/2 |
| 0.99 Å | 128/134 (70 pairs) | 1/16 (13 pairs) |
| 1.01 Å | 111/114 (60 pairs) | 18/36 (26 pairs) |
| 1.03 Å | 80/80 (42 pairs) | 49/70 (44 pairs) |

Per model on the strong side at 0.99 Å: MACE 54/59, MatterSim 15/16, ORB 59/59. On the weak side the slopes are -0.27 (MACE, r -0.69, 76 rows), -0.06, -0.02. The weak-side failure rests on 13 pairs, mostly MACE, and Astra identified several as NaOH and Cd(OH)2 polymorphs. "No skill" is safe; "reversed law" is not. The 0.99 Å cut is post hoc and must be reported with the full scan.

**(3) Why F02 cannot be cited for F01.** F02 measures a single-phase volume derivative of F_D - F_H divided by the bulk modulus; F01 is a between-phase difference at fixed geometry (Astra). The two share ingredients but not the observable. The regimes also do not overlap: brucite and the hydrides passed, and they sit where F01 has no skill or does not apply (no H bond in hydrides). The misses (GaOOH, β-CrOOH, ice) sit in the strong regime. Their most likely causes are the frequency offset and proton anharmonicity (Ubbelohde), neither of which changes the stretch slope, but this is inference. Argon's round-1 framing ("blind testing confirms the ensemble in weak H-bonds and defines the domain f_str ≤ 0.70") is rejected: the domain it proposes is the one where F01 fails, and f_str ≤ 0.70 conflicts with the compensation mechanism itself (stretch/total slope ratio 1.7 to 2.3).

**(4) Counts.** 341 is model evaluations, not pairs: 197 unique pairs, 60 formulas; the CV uses 312 evaluations, 187 pairs, 57 formulas; the |dX-H| ≥ 5 mÅ subset has 150 evaluations over 83 pairs (129 right, 86%). "Leave-family-out" means leave-formula-out. "Transferable across chemical families" overstates the evidence for non-O-H bonds.

**(5) Why matched spectroscopy over D/H fractionation.** Mineral-water D/H data are dilute-D, cross-lab, often out of equilibrium (tens of permil scatter), and the phase-phase difference is a difference of two mineral-water values. Mapping dilute fractionation onto fully deuterated ddF per H also needs an isotope-state argument (Astra). The cached AlOOH and FeOOH real-phase pairs have large length changes (|dX-H| 7 to 36 mÅ) and three-model agreement, so the predicted differential shifts are large compared with band uncertainties. Gibbsite/bayerite is out: its Al(OH)3 pairs have |dX-H| < 7 mÅ and the models disagree in sign.

## Where the members converged

1. F01 is a reproducible computational regularity: slopes stay positive on the 19 pairs common to all three models (0.16, 0.14, 0.14) and with a zero-intercept fit (Astra); pair and structure stretch slopes agree (Opus).
2. Drop "tested blind" from the F01 headline; F02 is reported separately as mixed (Opus, Astra; Argon round 1 framed F02 as partly confirming, which round 2 did not defend).
3. The weak-H-bond restriction is not a fallback; the rule fails there (Opus and Astra both recomputed 1/16).
4. Correct counts to 197 pairs / 341 evaluations / formula holdout.
5. The stretch check is the best single test of the shared-bias question, and it validates the stretch ingredient only; the compensation term is untested.
6. MDR/phonondb is not an independent test (shared PBE bias, almost no donors in the window).
7. G1 to G4 and F3 are closed (01-gate ledger); only G5 and F2 remain, and G5 needs no new compute (DFT LiH ZPE_H - ZPE_D 47.466 vs MACE 48.010 at DFT geometry, 46.928 relaxed, meV/H, about 1.1%).
8. NaBH4 is deprioritised for S7: B-H has no H bond and sits outside F01.
9. SevenNet rerun and the full database map only if already finished.

## Remaining disagreement

1. **How much the stretch check supports.** Opus: f ≈ 0.9 to 1.0 anchors the stretch slope and so the F01 sign. Astra: it validates dν/d(O...O), not dν/dr(OH), and correlated geometry and frequency errors could cancel. Chair: Astra is right about what is measured; the sign conclusion survives because F01 restated in O...O no longer needs the O-H map, and the monotonic lengthening of O-H as O...O shortens is established by neutron data independent of the models. The coefficient per mÅ of O-H stays a model number.
2. **F03 wording.** Astra judges "F01 is not an artefact" in F03 unsupported and flags selection issues (largest-projection Γ mode above 1500 cm-1, no acceptor-angle criterion, non-robust periodic acceptor search). Chair agrees: F03 is narrowed to "the stretch-frequency vs O...O slope matches measured spectra within 10% in the 2.50 to 2.80 Å window", and the selection issues are disclosed. Re-running F03 with an acceptor-angle criterion is optional.
3. **Quadrature tolerance.** Astra flags decompose.py accepting 0.01 meV/atom vs 0.001 meV/cell in M01; pair residuals reach 0.058 meV/H but none exceeds 20% of |ddF| in the CV subset. Not decision-relevant; reconcile in the docs.
4. **Argon** had no round-2 position. Its round-1 domain statement and "341 polymorph pairs / 57 families including borohydrides and ammonium" wording are overruled by the data above. Its gate block plan is stale.

## Ordered action list for the conductor

| # | Action | Owner | Time | Done-check |
|---|---|---|---|---|
| 1 | Restate claims: update GOAL headline, S3 ("formula holdout, O-H solids"), S4 ("blind test done, mixed; does not test F01"); F01 doc Result/Limits with the wording above; narrow F03 conclusion and disclose its selection issues. Fix counts everywhere (197 pairs, 341 evaluations, leave-formula-out). | Opus (conductor) | 30 min | `git grep -n -e "tested blind" -e "341 polymorph pairs" -e "leave-family-out" -- state docs README.md` returns no claim line except in history or this decision |
| 2 | Extend `rule_cv.py`: threshold scan 0.97 to 1.03 Å on pair max mean X-H, O-H vs non-O-H split, unique-pair counts and model-majority sign, formula-clustered CV inside the strong regime, constant-sign baseline from each training fold, both all-eligible and signal-filtered numbers. | Opus | 60 min | `results/F01_cv.json` has `regime_scan`, `oh_split`, `n_unique_pairs`; at 0.99 Å it reproduces 128/134 and 1/16 |
| 3 | Refit F01 against mean donor d(O...O) (from stretch_check donors), report slope, r, sign accuracy and CV; translate the 0.99 Å model O-H threshold into an O...O threshold. | Opus | 60 min | F01 doc has an O...O table and the domain stated in Å of O...O |
| 4 | Commit `stretch_check.py` windowed analysis: dedup symmetry copies, stretch_weight > 0.5, f_OLS and f_TheilSen per window, median offset, the harmonic-gap bracket (150 to 300/400 cm-1); fig5 with the window shaded. | Opus | 30 min | `stretch_check_summary.json` shows 2.50 to 2.80 Å f_OLS 0.91/0.92/0.95 |
| 5 | Matched differential spectroscopy on AlOOH `mp-23807__mp-625152` and FeOOH (goethite/lepidocrocite among `JVASP-29792__JVASP-54685`, `JVASP-54682__JVASP-92228`; confirm identities and order per decision 03 first). Step A: from cached phonons, write and commit the model differential stretch and OH in-plane/out-of-plane bend shifts (full-mesh projected, degeneracies counted) and the predeclared outcomes: support (measured matched shifts agree in sign and the net stretch minus bend sign survives a ±150 cm-1 anharmonic bracket), challenge (reliable matched spectra reverse a trend or the net sign), inconclusive (missing assignments, phase mismatch, transverse terms unbounded). Step B: source assigned IR/Raman bands (sweep worker, cap 45 min, verify every citation). Step C: compare, write `docs/findings/F04-differential-spectroscopy.md`. Do not plug band averages into a single ZPE formula as an "experimental ddF". | Opus runs, Astra reviews Step A before Step B | 2.5 h cap | Step A commit hash precedes the Step B data commit; F04 states support, challenge or inconclusive |
| 6 | Close G5 with the MDR DFT dZPE substitute (1.1% agreement) and log F2 as a disclosure; append to 01-gate ledger. | Opus | 20 min | row in `tier_a.csv`, ledger line in 01-gate.md |
| 7 | S7 candidate card: one real-phase pair in the strong regime with |dX-H| ≥ 10 mÅ and 3/3 model sign agreement (AlOOH or FeOOH above). Give ddF per H with model range and numerical error, and the falsifying measurement (spectral shifts from item 5, or a D/H fractionation difference at 38.7 permil per meV/H at 300 K). Use dP = -0.1602 ddF[meV/cell]/dV[Å^3/cell] only if |dV| exceeds the model spread. | Opus | 2 h | card file committed, linked from GOAL S7 |
| 8 | Only if item 5 is inconclusive and time remains before Thu 10:00: D/H fractionation comparison for the same pairs, labelled exploratory. | Opus, sweep worker | ≤ 2 h | result in F04 with an "exploratory" label, or logged skip |
| 9 | Final-claims board (04-final-claims) on the headline, F01, F02 and the card. Embed all evidence text in the Argon prompt so it needs no file reads; do not change permission settings. If the user wants Argon to read files, that is the user's call. | Opus chairs, Astra, Argon | 1 h, before Thu 11:00 | `docs/decisions/04-final-claims.md` exists; S6 status updated |
| 10 | Compute freeze Thu 12:00. Figures: F01 panel coloured by regime with the scan, stretch-check panel, F02 table. Then write-up and video. SevenNet and the database map enter only if already finished. | Opus, Can | after freeze | figures committed, README results match decision wording |

## What would change this

1. **Item 5 challenges the mechanism** (reliable matched spectra reverse the stretch or bend trend, or the net sign flips under the bracket): switch to the fallback wording, F01 becomes a model-ensemble trend with a disclosed experimental conflict.
2. **The O...O refit (item 3) loses the strong-regime sign skill** (sign accuracy at or below its baseline): the experimentally usable form of the rule fails, the headline drops "once hydrogen bonds are moderate to strong" as a usable criterion and keeps only the model-variable statement.
3. **The threshold scan shows the regime boundary is a few pairs from one formula** (for example the weak-side failures vanish when NaOH and Cd(OH)2 are held out): drop the "no skill when both bonds are weak" sentence and report the weak side as unresolved.
4. **A corrected stretch slope with f > 1.5** after deduplication and the harmonic bracket: the sign margin shrinks below 1.5x and the stretch-support sentence is removed from the headline.
5. **SevenNet arrives and disagrees in the strong regime** (sign accuracy below 75% there): S2 is restated as "three of four models".
6. **The final-claims board finds a blocking flaw**: P10(c) per GOAL.

## Notes

Argon round 2 failed twice with "agy empty output" because headless mode auto-denied a `read_file` permission. The suggested fixes (an allow rule in settings.json or `--dangerously-skip-permissions`) change permissions and were not applied; that needs Can's own approval. Item 9 works around it by embedding evidence in the prompt.

Chair check scripts (session scratchpad):
`C:\Users\can02\AppData\Local\Temp\claude\C--Users-can02--claude-spares-spare-MvrxRR\6cbef617-8c25-4b42-bf3b-8e15cd3cc49b\scratchpad\chair04_check.py` (counts, slopes, regime scan, baseline, O-H split, stretch windows) and
`C:\Users\can02\AppData\Local\Temp\claude\C--Users-can02--claude-spares-spare-MvrxRR\6cbef617-8c25-4b42-bf3b-8e15cd3cc49b\scratchpad\chair04_real.py` (real-phase covalent pairs).
Small differences from member numbers (Opus round 1: 129/136 strong, MACE 54/60, MatterSim 16/17) come from the threshold variable; this decision uses the chair recompute on pair max of per-structure mean X-H.

Erratum (21 Oct, decision 05 action 6): the f_OLS order "0.91, 0.92, 0.95" for mace, orb, mattersim above (and in action 4) is wrong. The correct values are MACE 0.91, ORB 0.95, MatterSim 0.91 (`results/stretch_check_summary.json`).
