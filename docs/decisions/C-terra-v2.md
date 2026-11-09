# C-terra-v2. Terra's 12 weaknesses on v1: which are valid, which v2 fixes are right, what to do next

Council: Opus (chair), Astra, Gemini 4 Argon. Two rounds. Opus and Astra answered both; Argon timed out in round 1 and answered round 2 (reply file `council_terra_reply_r2.txt` in the session scratchpad). Chair re-checks on 9 Nov 2026 with the project `.venv` (scripts `chair_chk.py`, `chair_chk2.py`, `dd3.py` in the session scratchpad; no GPU, no force calls, nothing written to `results/`). Evidence: `docs/paper/reviews/valency_terra_review.md`, `terra_fix_diff.patch`, `w1w3_recount.py`, the working `docs/paper/main.tex` (patch already applied), `results/paper_stats.json`, `results/benchmark/isotope_benchmark.csv`.

## Decision

1. **v2 is not ready.** The patch is mostly right, but three of its sentences are now wrong or contradictory and must be fixed before the PDF is rebuilt: the W2/W7 cutoff residual, the W7 tolerance, and the W6 "sign and size numerically unverified" clause.
2. **Ten of Terra's twelve points are valid** (W1 to W8, W10, W12). **W9 and W11 are wrong against the PDF and `main.tex`.** MatterSim's all-row OLS slope is 0.128 in both the text (line 149) and Table I. 0.126 is the formula-fixed-effects slope, which appears in the same paragraph and in Table I. Eq. 5 and its definition (line 101) both carry w^H_{qν}. Only W9 and W11 go into the feedback to Valency.
3. **The W1 recount is a valid test and not circular. Its scope is narrow.** ΔΔF_str is built from eigenvector projections onto H-to-neighbour bond vectors, integrated over ln m. Δr̄ never enters it, so the sign agreement could have failed. Its limits:
   * It tests the operative condition sign(ΔΔF_str) = sign(Δr̄) inside the MLIPs. It does not test a single shared ν(r) line, and it does not validate anything against nature.
   * The 0, 300 and 600 K counts are one test, not three. The stretch thermal weight changes by about 1% over that range.
   * The cross-structure evidence for one ν(r) relation is the donor stretch-frequency fit (r = −0.99 to −1.00) and the Libowitzky curve. Cite both.
   * "Holds without exception" must carry the |Δr̄| ≥ 5 mÅ eligibility qualifier and the near-zero failures.
4. **The fixes, point by point.**

   | Point | Valid | v2 fix | Required change |
   |---|---|---|---|
   | W1 | yes | overclaims | Add the qualifier and the 480-row extension. Say it is one model-internal test. ΔΔF_quad = ΔΔF_str(1−C) is a definition, so present it as one. |
   | W2 | yes | **wrong** | Split into two cases (below). "Order k_BT ln ρ" is not general. |
   | W3 | yes | adequate | Add the 176/190 pointer at line 69, which still quotes only "198 of 212". |
   | W4 | yes | direction right, imprecise | Write the Clapeyron relation explicitly. The verdict wording depends on the Bridgman read (action 4). |
   | W5 | yes | open | Add the corrected post hoc benchmark paragraph (action 2). It stays a stated gap. |
   | W6 | yes | **self-contradictory** | Drop "sign and size numerically unverified". Use 0.05 to 0.11 GPa as a hypothetical sensitivity, then run the CPU mesh check (action 3). |
   | W7 | yes | **tolerance wrong** | The clean bound is 0.01 meV/atom per structure, so 0.02 per pair. It is checked only at 0, 300 and 600 K. |
   | W8 | yes | adequate | Write the O-H slopes as 0.124 to 0.145. |
   | W9 | **no** | not applicable | Feedback only. |
   | W10 | yes | wording | Say "the next possible term is order 1/T^3 and sets the sign if its coefficient is nonzero". |
   | W11 | **no** | not applicable | Feedback only. Rename the q-point weight w_q to g_q anyway, so the two weights are not confused. |
   | W12 | yes | adequate | Optionally report the exceedance count (action 5). |

   For W2/W7 the corrected physics:
   * **Case A, cut in one phase only.** The mode is cut for both isotopes in phase a and kept in phase b. It leaves −w_q k_BT ln ρ, which is (k_BT/2) ln 2 = 8.96 meV at 300 K and 17.92 meV at 600 K per unit-weight pure-H mode.
   * **Case B, cut separating the isotopes within one phase.** H is kept and D is dropped. It leaves about w_q k_BT ln(k_BT/hν_c), which grows like T ln T: 107 meV at 300 K and 250 meV at 600 K per unit-weight mode at ν_c = 0.1 THz, before q-weight and normalisation.
   * Neither term decays. The clean criterion bounds both at 0, 300 and 600 K only. There is no decomposition and no clean check at 2000 K, so the 211/212 trace test (line 240) is a sign test on direct values with no residual control. Say so.
5. **W4 stays scored as failed**, because P05 rule 3 predeclared the triple-point comparison. Whether the fixed-temperature verdict is "wrong in sign" or "inconclusive" is decided by data from the primary source, not by either member's recall (action 4).
6. **Nothing is sent, pushed or submitted by the conductor.** Can sends the Valency feedback himself.

## Why

All numbers below were recomputed by the chair this session.

* **W1.**
  * `w1w3_recount.py` reproduces 212/212 at 0, 300 and 600 K and 232/232 O-H rows with |Δr̄| ≥ 5 mÅ at 300 K.
  * Extension to all 480 decomposed O-H rows at 300 K: 413/415 agree for |Δr̄| ≥ 1 mÅ, 229/248 for |Δr̄| < 5 mÅ, 48/65 for |Δr̄| < 1 mÅ.
  * So the assumption fails only near Δr̄ = 0, which is outside the scored set. That is Terra's mechanism, confined to where the rule makes no claim.
* **W3.**
  * 190 rows are clean at both 0 and 600 K. C falls in 176 of them. Medians are 0.645, 0.580 and 0.402.
  * H1 is met in 81/190 and still fails.
  * The rule is right in 188/190 at 600 K. All 24 clean mp-985293 rows have C0 > 1 and C600 < 1.
* **W7.**
  * The largest pair |direct − quadrature| over all 212 rows is 0.0009, 0.0091 and 0.0181 meV/atom at 0, 300 and 600 K.
  * On the 190 rows clean at both endpoints it is 0.0006, 0.0050 and 0.0099.
  * 0.018 is above 0.01, which confirms that the pair bound is 0.02 and the patch's "0.01" is wrong for pairs.
* **W6.**
  * The stored secant slopes are 1.765 (MACE) and 1.917 (ORB) meV/atom/GPa, so effective |ΔV| is 0.283 and 0.307 Å^3/atom.
  * An error of 0.1 to 0.2 meV/atom then gives 0.052 to 0.113 GPa, which is 4 to 10% of the 1.13 to 1.33 GPa shift.
  * The goethite number is a different quantity in a different compound, so this is a sensitivity, not an error bar.
  * Saying "unverified" next to the ~1 GPa result in the abstract and conclusion is an internal contradiction.
  * `validate._qha_fcs` rebuilds the QHA from cached force constants (3179 cache entries in `.cache/isoshift`), so a mesh check is CPU post-processing with no relaxation or force calls.
* **W5.** Recomputed with `dF300_*_meV`, which `benchmark.py` already stores per H. Opus's round-1 result (46/46, MAE 0.27) divided by n_H twice and is withdrawn.
  * Correct numbers over 12 same-formula pairs at 300 K: double-difference MAE 0.486 meV/H at DFT geometry (max 2.02) and 0.677 relaxed (max 2.28).
  * Sign agreement is 36/46 and 31/46 overall, and 22/24 where |ΔΔF_DFT| ≥ 0.1 meV/H.
  * Seven pairs are supercell or polytype near-duplicates with |ΔΔF_DFT| ≤ 0.06 meV/H, where sign is noise. RbOH mp-626620/mp-626721 is one structure.
  * Only KHS (0.41 meV/H, 4/4 models right) and NaHS (0.22 meV/H, 2/4 right: ORB and MatterSim reversed at DFT geometry, MACE and MatterSim reversed relaxed) are DFT-stable with a non-trivial ΔΔF.
  * The three O-H pairs with large ΔΔF (Ca(OH)2, NaOH, RbOH with mp-643043) all have DFT imaginary modes.
  * Conclusion: the paragraph bounds the MLIP double-difference error at about 0.5 meV/H, against a screen median |ΔΔF| of 2.4 meV/H. It does not validate any O-H screen row.
* **Screen mesh sentence (Astra's question).** `results/paper_stats.json` `mesh_60a_300K` gives 185/212, 0 sign flips and a maximum change of 0.054 meV/H. The sentence is supported. Write "0.054" or "about 0.05", not "at most 0.05".
* **W12.** None of 2×10^5 draws reaches 185 (maximum 154). The Monte Carlo estimate (r+1)/(N+1) is 5.0×10^-6, which is a valid p-value. The 95% upper bound on the true tail probability is 1.5×10^-5. "p < 10^-5" is defensible as the Monte Carlo p, but the count is cleaner.
* **W10.** The high-temperature expansion F = k_BT ln(ħω/k_BT) + (ħω)^2/24k_BT − (ħω)^4/2880(k_BT)^3 + ... means equal traces remove the 1/T term. The next term, Tr(D^2) in mass-weighted form, includes the H-X off-diagonal blocks and is generically nonzero. Opus's numerical check on Terra's (2,2,2) against (1,3,2) shows T^3 ΔΔF tending to a constant.

## Where the members converged

* All three: W9 and W11 are wrong against the PDF; the other ten are valid. Feedback covers W9 and W11 only, and must not claim a Hub extraction fault that nobody has seen.
* All three: W1 is not circular, is model-internal, and its three temperatures are one test. "Without exception" needs the 5 mÅ qualifier.
* All three, after round 2: the W2/W7 patch text is wrong in two ways (the T ln T case, and the 0.02 pair bound), and there is no 2000 K check.
* All three: the W6 "unverified" clause contradicts the abstract. 0.05 to 0.11 GPa is a sensitivity, not a bound. The force constants are cached, so a mesh check is CPU-only.
* All three, after Argon and Astra caught the n_H double division: the honest W5 paragraph uses the corrected numbers, shows the NaHS reversal and says there is no stable O-H pair.
* All three: keep "C about one half" (slope ratio 0.49 to 0.56, other-row median 0.50). 0.58 is the median of the post hoc 190-row subset only.

## Remaining disagreement

* **W4 wording.** Opus says Ih-II stays wrong in sign after the matched correction (dP/dT)ΔT_t: with an Ih-II slope of about +0.8 MPa/K, reversing the verdict needs |ΔT_t| ≈ 35 K against a few K measured. Ih-III would be inconclusive only for MatterSim (−3 MPa). Astra says to label the fixed-T comparison inconclusive. Chair: Opus's argument is the right form, but its inputs (the Ih-II slope and the D2O triple-point temperature) are from memory. Primary-source rule: read Bridgman 1935 first. Until then, the text keeps "not established at fixed temperature" plus the explicit relation.
* **W12 bound form.** Opus prefers 5×10^-6 (the Monte Carlo p); Astra prefers 1.5×10^-5 (the upper bound on the true p). Both are correct statements of different things. Chair: report the count and the Monte Carlo p, which is low priority.
* **Whether the CPU mesh check counts as compute under the freeze.** Chair: it is a diagnostic post-processing run with no GPU, no relaxation, no force calls, and it does not touch the PIMD queue. It does not change the production method or any frozen number, so no amendment is needed. It is reported as a new, labelled check.

## Ordered action list for the conductor

| # | Action | Owner | Time | Done-check |
|---|---|---|---|---|
| 1 | **Fix the wrong text** in `main.tex` (zero compute, biggest correctness gain). (a) W2 at line 92: Case A and Case B, with the 600 K numbers. (b) W7 at line 101: "per structure 0.01, per pair 0.02 meV/atom; checked at 0, 300 and 600 K only". (c) Line 240: "no consistency check at 2000 K". (d) W6 at line 277: replace "so the sign and size of the shift are numerically unverified" with "a goethite-sized error would move the shift by 0.05 to 0.11 GPa (4 to 10%); convergence was not tested and may be worse near symmetrization". (e) W10: the "if nonzero" wording. | conductor (Opus) | 30 min | `grep -n "order \$k_{\\mathrm{B}}T\\ln\\rho\|numerically unverified" main.tex` returns nothing; "0.02" and "2000~K" appear in the residual text; the PDF builds. |
| 2 | **W1 and W3 text** (zero compute). Line 68: "holds in all 232 eligible O-H evaluations (\|Δr̄\| ≥ 5 mÅ) at 300 K and in 413 of 415 with \|Δr̄\| ≥ 1 mÅ; it fails in 17 of 65 with \|Δr̄\| < 1 mÅ, which the rule does not score". State that 0, 300 and 600 K are one test, call the identity a definition, and cite the donor ν(r) fit and Libowitzky. Line 69: add "176 of 190 on rows clean at both endpoints". Add the 480-row bins to `w1w3_recount.py`. | conductor | 30 min | The recount prints 413/415, 229/248 and 48/65. Line 68 contains "5~m\AA". Line 69 contains "176 of 190". |
| 3 | **W5 paragraph** in Sec. tests, plus a Limitation (2) edit (zero compute, labelled post hoc). Use the numbers in Why/W5: MAE 0.49 and 0.68 meV/H; 22/24 where \|ΔΔF_DFT\| ≥ 0.1; KHS and NaHS the only stable pairs; NaHS reversed by ORB and MatterSim; no O-H pair. Replace "no DFT double difference was computed" with "no DFT double difference was computed for an O-H screen pair". Commit `dd3.py` as `scripts/benchmark_double_difference.py`, with no n_H division and the duplicate RbOH pair excluded. | conductor | 45 min | The script reproduces 0.486/0.677, 36/46, 31/46 and 22/24. The paragraph names NaHS and says "no O-H pair". |
| 4 | **AlOOH q-mesh check, CPU only.** Rebuild the QHA for diaspore and δ-AlOOH (MACE, ORB) from the cached force constants with mesh density 40, 60 and 80/a, the clip raised to 24, Γ-centred and shifted. Recompute the H and D transition pressures at 300 K. First assert that every volume point resolves in `_qha_fcs`. Write the output to a new `results/validation/alooh_mesh.json`; frozen files are untouched. | conductor | 1 h CPU plus 30 min | The JSON holds the shift per mesh and model. If the change is ≤ 0.1 GPa, W6 text says "converged to within X GPa". If it is > 0.1 GPa, the ~1 GPa claim is downgraded in the abstract, AlOOH section and conclusion, not hedged. |
| 5 | **W4 primary read.** Read Bridgman 1935 (D2O) and an H2O source for the Ih-II-III triple point (T, P) and the Ih-II and Ih-III slopes. Write ΔP_t − ΔP_iso(T_t) = (dP/dT)ΔT_t in the text. If \|(dP/dT)ΔT_t\| is well below 29 MPa: "the correction is at most X MPa; Ih-II is wrong in sign for all three models at fixed temperature, and Ih-III for MACE and ORB; MatterSim Ih-III (−3 MPa) is inconclusive". Otherwise: "inconclusive at fixed temperature". The scored verdict stays failed either way. | conductor (literature) | 45 min | The numbers in the text cite a page or table of the primary source; `logs/bond_queries.jsonl` has the query. |
| 6 | **Small edits.** w_q → g_q in Eqs. 4 and 5. O-H slopes "0.124 to 0.145" in the abstract and Sec. III D. Keep "C about one half", optionally adding "(slope ratio 0.49 to 0.56)". Mesh sentence "0.054". W12: "none of 2×10^5 draws reaches 185 (maximum 154), Monte Carlo p ≤ 5×10^-6". | conductor | 20 min | `grep -c "w_q" main.tex` = 0. The PDF builds without warnings about undefined references. |
| 7 | **Valency feedback rewrite.** Rewrite `valency_feedback_draft.md` to state only verified facts: "the PDF gives 0.128 in text (Sec. III D) and Table I; 0.126 in the same paragraph and in Table I is the formula-fixed-effects slope; Eq. 5 and its definition carry w^H_{qν}". Attach PDF crops. Remove the sentences asserting what the Hub text says, unless Can checks the Hub text view first and sees it. | conductor drafts, **Can sends** | 15 min | The draft contains no unverified Hub claim. Can presses Send himself. |
| 8 | **Rebuild and commit.** Rebuild `main.pdf` and commit `main.tex`, `main.pdf`, the recount and benchmark scripts, and this decision locally on `post-hackathon`. No push, no Hub upload (v2 upload is Can's call). | conductor | 15 min | `git log -1` shows the commit. `git status` is clean for these paths. Nothing pushed. |

Score order (Q3): actions 1 and 2 fix text that is wrong today, which hits Correctness 4/10 directly at zero cost. Action 3 turns W5 from "nothing" into a bounded, honest partial check. Action 4 is the only one that can close a major point (W6), at about 1 h of CPU. Action 5 can close W4. Action 6 is hygiene. Do not expect W5 to close without new O-H DFT phonons. That is deferred beyond the freeze and stays a stated limitation.

## What would change this

* If the AlOOH mesh check moves the shift by more than 0.1 GPa, or changes its sign for either model: the ~1 GPa result is downgraded to exploratory in the abstract and conclusion, and the W6 major point stands.
* If the primary sources give |(dP/dT)ΔT_t| comparable to 29 MPa (a larger D2O triple-point temperature shift or a steeper Ih-II line than recalled): the Ih-II fixed-temperature verdict becomes inconclusive, as Astra proposed.
* If Can sees the Hub text view and it really shows 0.126 for the all-row slope and w^H_q without ν: the feedback may then say the Hub text differs from the PDF, with a screenshot.
* If `_qha_fcs` cannot resolve every QHA volume from the cache: action 4 needs new force calls, which is new compute and needs Can's approval. W6 then stays a stated limitation with the sensitivity sentence only.
* If a stable O-H polymorph pair with DFT force constants is found in existing data: add it to the W5 paragraph. Its sign result would matter more than the whole S-H benchmark.
