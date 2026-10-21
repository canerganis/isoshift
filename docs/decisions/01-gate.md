# 01. Gate (hour 7): conditional pass, narrowed framing

Chair: Opus (xhigh, final authority), Wed 21 Oct 16:35 TRT. Board: Opus member (xhigh), Astra gpt-6-astra (xhigh), Gemini 4 Argon (no answer). Evidence: PLAN.md, results/validation/volume_isotope.csv, results/validation/tier_a.csv, data/isoshift/validation.csv, docs/decisions/00-brucite-imaginary-modes.md, docs/math/M01-isotope-formulas.md, plus chair re-runs from cached force constants (scripts listed at the end).

## Decision

**Conditional pass.** The framing is P12's wording, not the bare P1 phrase:

> H/D vibrational free energies validated against measured volume/lattice isotope effects (brucite, LiH). Polymorph ΔΔF_iso and transition shifts are exploratory ensemble predictions with model spread.

The screen, analysis, app and story proceed on this framing now. The word "validated" may appear in a figure, the README, the write-up or the video only after conditions G1 to G5 below are closed. Deadline: Thu 12:00 compute freeze. If any condition fails, or is still open at the freeze, the fallback framing (P10(b): X-H benchmark + isotope free-energy atlas) applies automatically, with no new board.

Governing text: PLAN.md line 4 makes P10 to P25 override P1 and the block tables. P12 redefines tier B: brucite volume sign is mandatory, LiH lattice sign is the second observable, ice is reported only, "right in ≥3 of the models that ran", and portlandite becomes a null check, not a sign test. The gate row in the Block 2 table (brucite + portlandite sign) is superseded.

Rulings on the three judgement calls:

1. **Portlandite does not count as a fail, and it does not count as validation.** It has no same-condition H/D pair. The +0.67% is cross-lab (XRD at 0.5 GPa vs interpolated neutron data), and the Busing-Levy vs Xu inter-lab offset alone is 1.8%. P12 calls it a null check but sets no tolerance. The chair does not set one after seeing the data, so the null check is ruled **uninformative**: reported, never called pass or fail. Portlandite also carries undiagnosed imaginary H modes in all four models (0.15 to 1.0% of modes, down to -5.8 THz) and a supercell switch inside the QHA grid for three models (P4 violation), which is a second reason it cannot validate anything.
2. **The brucite imaginary branch is diagnosed and bounded, so it is not "unresolved" for this gate.** It is not fixed, and the record says so. Decision 00 diagnosed it as physical (H off the three-fold axis, P11 eigenvector following gives a √3×√3 P31m minimum only 0.07 to 0.26 meV/atom lower). The chair re-ran the QHA from cached force constants with four treatments of the imaginary modes across the whole volume grid: brucite VIE stays positive in 16 of 16 model × treatment cases, and the per-model treatment spread is at most 0.055 percentage points against a measured +0.31% (table below). SevenNet, whose brucite is harmonically stable (imaginary fraction ≤ 0.01%) at its own QHA volume, gives the same sign. Two deviations are logged, not hidden: the PLAN 1.4 done criterion (min optical > -0.5 THz in ≥3 models) is not met (min frequency -1.7 to -5.3 THz at most QHA volumes for mace, orb and mattersim), and the QHA path omits the imaginary modes where M01 (1) would stop.
3. **Three models are enough to call tier A for the code path; SevenNet is pending, not passed.** Equal-mass and swap-sign run the same code (phonopy 4.8.3, ase 3.29.0, numpy 2.5.4 in both venvs). The model-specific check is the LiH Γ TO frequency. SevenNet stays out of every "validated" statement until its tier A rows exist (G1). The framing does not depend on it: without SevenNet, tier B is brucite 3/3 and LiH 3/3.

## Why

**Tier B under P12 passes with margin.** `VIE = 100 * (V_H/V_D - 1)`, positive means the H compound is larger.

Brucite, 295 K row (QHA grid point 290 K), measured +0.31% (Chakoumakos 2013, abstract; sign also in Horita 2010):

| model | stored (Γ acoustic modes in) | Γ-free, imaginary omitted | Γ-free, \|ω\| | Γ-free, 2\|ω\| | Γ-free, fixed 3 THz | ratio to exp |
|---|---|---|---|---|---|---|
| mace | +0.255 | +0.292 | +0.321 | +0.335 | +0.280 | 0.82 to 1.08 |
| orb | +0.237 | +0.278 | +0.309 | +0.305 | +0.283 | 0.76 to 1.00 |
| mattersim | +0.215 | +0.192 | +0.194 | +0.193 | +0.193 | 0.62 to 0.69 |
| sevenn | +0.338 | +0.394 | +0.438 | +0.413 | +0.413 | 1.09 to 1.41 |

Sign 4/4 under every treatment. The 0 K stored values are reproduced to three digits by the re-run, which confirms the re-implementation. Model spread (about 0.2 pp) is four times the treatment spread.

LiH, 300 K: VIE +1.07 (sevenn), +1.12 (mace), +1.14 (orb), +1.21% (mattersim). Measured +0.81% (Loubeyre a values) or +1.04% (Smith-Leider 0.014 Å shift); the two sources disagree. Lattice constant effect +0.35 to +0.40% vs +0.27 or +0.34%. Overestimate 1.03 to 1.50×. Sign 4/4.

Ice XI proxy, 100 K (reported only): VIE -0.32 to -0.79%, anomalous negative sign 4/4. The measured 100 K values in validation.csv are -0.075 and -0.078%, not the -0.15% used in volume_isotope.csv, so the overestimate is 4 to 11×, not 2 to 5×. All four MLIPs make ice 6.5 to 7.9% too dense, which fits overbound H-bonds.

**Tier A for mace, orb, mattersim passes as specified:** equal-mass and swap-sign residuals exactly 0.0; classical decay |ΔΔF(2000 K)|/|ΔΔF(0 K)| = 0.26, 0.032, 0.093 (< 0.5); LiH Γ TO errors +12.8/+11.9% (mace), +6.7/+5.8% (orb), -7.0/-7.8% (mattersim) for H/D, all inside 15%. The H/D TO ratio is 1.3319 in all three, the harmonic reduced-mass ratio for natural Li (1.3318), so the D mass enters the dynamical matrix correctly. Equal-mass and swap-sign are algebraic identities of the implementation and only catch wiring errors; the TO ratio is the non-trivial mass test. Two P1/P13 tier A items have no rows: LiH absolute ΔZPE per f.u. vs experiment, and the supercell-doubling test on ΔΔF_iso. Missing evidence does not count as passing, hence G4 and G5.

**Why not an unconditional pass.** (a) The stored finite-T VIEs include near-zero Γ acoustic modes (GammaAcousticWarning in results/validation_run.log), contrary to M01 (1). It moves brucite by up to 0.06 pp and portlandite by up to 0.08 pp; figures must not be built from the current CSV. (b) Tier A is incomplete (SevenNet, ΔZPE, supercell doubling). (c) The ice reference is wrong in the CSV. (d) Volume isotope effects test the volume derivative of `F_H - F_D` in one phase, not polymorph double differences. The only double difference in the evidence, α/γ MgH2, gives ΔΔF_iso(0 K) = +0.49 (mace), -0.13 (orb), -0.39 (mattersim) meV/atom: a three-model sign split with 0.88 meV/atom spread, nine times the P14 floor. So the validation wording must name the observable.

**Why not fail.** Every tier B criterion in force (P12) is met in 4/4 models, under five numerical treatments, with magnitudes within 0.6 to 1.4× of the measured brucite value and 1.0 to 1.5× for LiH. Astra's central objection, that the omitted modes were not bounded, is answered by the bracket above, which is the bound Astra named as the condition to change position. Failing now would discard a defensible result that the binding criteria accept.

## Claims under this decision

The write-up MAY say (once G1 to G5 close):
* Implementation checks pass: exact zero for equal masses, exact antisymmetry under H↔D swap, classical decay of ΔΔF_iso, LiH Γ TO errors of 6 to 13% with the harmonic reduced-mass H/D ratio.
* QHA with an MLIP ensemble reproduces the sign of the measured volume isotope effect of brucite (4/4 models, +0.19 to +0.44% across models and imaginary-mode treatments vs +0.31%) and LiH (4/4, 1.0 to 1.5× too large).
* The anomalous negative sign of ice is reproduced in an ice XI proxy, magnitude 4 to 11× too large.
* Brucite has a shallow H multi-well; its imaginary H branch (up to 0.8% of modes) is excluded from F_vib, and the brucite result is insensitive to how it is treated.
* Portlandite has no clean experimental H/D pair; the ensemble gives |VIE| ≤ 0.3% with an unresolved sign.
* Screen ΔΔF_iso and ΔT_c are exploratory ensemble predictions with model spread (P6, P14, P15).

The write-up MAY NOT say:
* "Validated isotope free energies" without naming the observable (volume/lattice isotope effect) and the systems (brucite, LiH).
* That ΔΔF_iso double differences or transition shifts are validated.
* That portlandite is a validation, a pass or a fail.
* That ice agrees quantitatively.
* That structures are accurate (brucite QHA volumes are 5.4 to 7.2% above experiment, ice 6.5 to 7.9% too dense).
* That brucite or portlandite are dynamically stable in the harmonic sense.
* That model spread is a confidence interval, or that four related PBE-trained models are four independent validations.
* That SevenNet passed tier A before G1 closes.

## Member positions

* **Opus member (xhigh, 0.78):** conditional pass under P12; brucite 4/4 and LiH 4/4 pass, portlandite unvalidated, imaginary branch resolved by omit vs |ω| sensitivity; conditions on SevenNet tier A, Γ-free regeneration, ice reference, decision 00 amendment, ΔZPE and supercell doubling.
* **Astra (xhigh, 0.97):** fail at hour 7, fallback framing; brucite instability not bounded, tier A incomplete (SevenNet, ΔZPE, supercell doubling), portlandite null-check tolerance undefined; would accept "validated against selected measured volume/lattice isotope effects" once those are resolved.
* **Gemini 4 Argon:** no answer; the headless run was denied the read_file permission twice and was not retried, since a permission change needs Can's approval.

## Dissent

Astra dissents (fail now). The chair agrees with Astra on four points and adopts them as binding: volume isotope effects do not validate absolute free energies or double differences, so the wording is narrowed; missing tier A items do not count as passing (G4, G5); SevenNet is pending, not passed; the portlandite null check gets no post-hoc tolerance. The chair overrules Astra on two points. First, the omitted-mode bound: Astra did not have the four-treatment bracket over the full QHA grid, which shows sign invariance and a treatment effect below a quarter of the model spread. It is a sensitivity bracket, not an anharmonic calculation, and is disclosed as such. Second, the M01 stop rule: M01 governs the screen's isoshift() path; the QHA validation path follows the exception in decision 00, now logged here as a deviation. The practical gap between the two positions is small: the screen runs either way, and under this decision the word "validated" is withheld until the items Astra listed are closed.

P21 applies: each of Astra's substantiated blockers maps to a condition below and must be closed regardless of votes.

## What would change this

Toward fail (fallback framing, automatic):
* After G2, brucite or LiH sign is wrong in more than one of the models that ran under any imaginary-mode treatment.
* SevenNet tier A shows a code-path failure (equal-mass nonzero, swap not antisymmetric). By P10(a) this also stops the screen until fixed.
* The primary Chakoumakos 2013 text gives a non-positive brucite volume difference at room temperature.
* Any of G1 to G5 open at the Thu 12:00 freeze.

Toward unconditional pass: G1 to G5 close clean.

Toward a stronger framing that covers double differences: a polymorph pair with a measured H/D free-energy or transition shift where the ensemble agrees in sign. α/γ MgH2 is a counterexample today.

## Follow-up tasks

Conditions on the word "validated" (deadline Thu 12:00):

| id | task | owner | done when |
|---|---|---|---|
| G1 | SevenNet tier A in `.venv-sevenn` (`python -m src.isoshift_event.sanity sevenn`), validation GPU priority (P18), about 10 GPU min | C (GPU) | 6 rows in tier_a.csv; code-path failure triggers P10(a); LiH TO > 15% off only removes SevenNet from quantitative claims |
| G2 | Regenerate volume_isotope.csv Γ-free (drop the 3 Γ acoustic modes, M01 (1)) on CPU from cached FCs, with the four imaginary-mode treatments as the error bar; move the logic from the scratchpad into `src/isoshift_event/validate.py` | C, S runs | CSV has VIE per treatment; brucite and LiH sign right in ≥3 of the models that ran under every treatment |
| G3 | Fix the ice reference to the Pamuk Table I 100 K values (-0.075/-0.078%) and the LiH TO note in validation.csv (harmonic Γ TO ratio is the reduced-mass ratio 1.332, measured 1.321) | S | CSVs corrected, commit |
| G4 | P13 supercell-doubling test on ΔΔF_iso for α/γ MgH2 (mace, orb), threshold 0.01 meV/atom; a larger change is not a code failure, it enters the P14 numerical-error term | C (GPU) | rows in tier_a.csv |
| G5 | LiH absolute ΔZPE per f.u.: source an experimental value via Bond, or use the MDR DFT dZPE from `benchmark.py` as substitute, or drop it with the reason logged here | X (Bond), S | row in tier_a.csv or logged drop |

Not gating, before Block 4.4 figures:

| id | task | owner |
|---|---|---|
| F1 | Amend decision 00 with the four-model imaginary-fraction table (brucite mace 0.36 to 0.83%, orb 0.24 to 0.71%, mattersim 0.11 to 0.33%, sevenn 0.73% falling to 0 for V ≥ 43.9 Å^3; portlandite 0.15 to 1.01%, all models) and the PLAN 1.4 deviation | C |
| F2 | P4 supercell consistency: SevenNet used 3×3×2 (90 atoms) for brucite and portlandite and 3×3×3 (54) for LiH vs 160/128 for the others; portlandite (1-based volume index: mace vol 9, orb vols 8 to 9, mattersim vols 6 to 9) and ice XI switch supercell inside the QHA grid. Rerun portlandite and ice on one supercell per structure if GPU time allows, else disclose | C (GPU, low priority) |
| F3 | Stronger classical-limit check: T·ΔΔF_iso → constant over 1000 to 3000 K instead of one 2000 K ratio | S |
| F4 | Main figure validation panel uses G2 values with treatment error bars, portlandite shown as "no clean experimental pair", ice marked "reported only" | S drafts, C checks |
| F5 | Can decides whether to allow read_file for headless Gemini so it can review the final claims (4.5, 6.1) | Can |

Chair re-run scripts (temporary, session scratchpad; G2 moves this logic into the repo):
* `C:\Users\can02\AppData\Local\Temp\claude\C--Users-can02--claude-spares-spare-MvrxRR\6cbef617-8c25-4b42-bf3b-8e15cd3cc49b\scratchpad\chair_qha_brackets.py` (brucite, four imaginary-mode treatments)
* `C:\Users\can02\AppData\Local\Temp\claude\C--Users-can02--claude-spares-spare-MvrxRR\6cbef617-8c25-4b42-bf3b-8e15cd3cc49b\scratchpad\chair_qha_sens.py` (brucite and portlandite, omit and |ω|)
* `C:\Users\can02\AppData\Local\Temp\claude\C--Users-can02--claude-spares-spare-MvrxRR\6cbef617-8c25-4b42-bf3b-8e15cd3cc49b\scratchpad\imag_scan.py` (imaginary fraction per volume)
* `C:\Users\can02\AppData\Local\Temp\claude\C--Users-can02--claude-spares-spare-MvrxRR\6cbef617-8c25-4b42-bf3b-8e15cd3cc49b\scratchpad\chair_sc_check.py` (supercell size per volume)

## Follow-up status (Opus, 21 Oct ~17:30)
* G1 closed: SevenNet tier A code path passes (equal mass 0, swap sign exact, classical decay 0.19). LiH TO(H) 20.41 THz vs 17.7 THz exp (+15.3%) fails the 15% band by 0.3 pp, TO(D) passes. Per this decision SevenNet stays in ensemble sign votes and model spread but out of quantitative validated claims.
* G2, G3, F1, F4 closed (cbfb528, 9129ab6): brucite and LiH sign right in 4/4 models under all four imaginary-mode treatments.
* Open: G4 (supercell doubling on MgH2 ddF_iso), G5 (LiH dZPE via DFT benchmark), F2 (supercell consistency disclosure), F3 (T x ddF_iso classical check).
* G4 closed (convergence.py, MgH2 alpha/gamma): MACE ddF_iso changes by 0.014 meV/atom (0/300 K) from 9.5 A to 14 A supercells, slightly above the P13 0.01 target and far below the 0.1 meV/atom P14 floor; carried as a supercell term in the numerical error. ORB is converged at the screen supercell (300 K diff 0.002) but its 14 A supercell grows imaginary modes.
* F3 closed and turned into a screen-wide check: MACE T x ddF_iso -> 264 meV K/atom (1/T decay). ORB at 14 A shows ddF growing linearly with T, the signature of omitted imaginary modes leaving an uncancelled kT ln(w_D/w_H). refine.py now flags `classical_limit_violation` when |ddF(2000 K)| > |ddF(600 K)|, and analysis rejects those pairs (12 of 90 checked rows so far).
