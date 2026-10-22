# F08. The O-H...O angle does not rescue F01 where bend and libration outweigh the stretch

**Status: predeclared test failed (post-freeze addendum; the frozen F01 headline of decision 07 is unchanged).** Predeclared in `docs/predictions/P06_refined_rule.md` (commit cdb32da, pushed before any SevenNet score of the refined rule). Code: `src/isoshift_event/refined_rule.py`. Numbers: `results/F08_refined_rule.json`. Geometry: `results/hbond_geometry.csv`.

## Question

F01 says deuteration favours the polymorph with the shorter O-H bonds. It fails in the 10 pairs that contain Al(OH)3 mp-985293, where bend and libration cancel 95 to 132% of the stretch term instead of about half. Bend and libration stiffen as hydrogen bonds get stronger and more linear (McKenzie et al. 2014, 2015), and mp-985293 has nearly linear hydrogen bonds (mean O-H...O 174 to 175 degrees) while its partners are bent (144 to 162 degrees). The question was whether one extra geometric input can predict the compensation fraction, and with it the sign, beyond the change in mean O-H length.

## Method

Inputs per relaxed structure and model: O-H donors (nearest non-H atom O within 1.15 Å), acceptor = nearest other O with H...O below 2.6 Å, θ = O-H...O angle at H, averaged over donors. Pair inputs: x = change in mean X-H length (mÅ, the F01 input) and dθ = change in mean angle (degrees), both b minus a as in `decompose.py`.

The rule comes from fits to the two mode-resolved components, not to the sign of the total. The stretch term per H is fitted as s·x and the bend/libration term as p_x·x + p_θ·dθ, both through the origin, on the 292 clean O-H rows of MACE, ORB and MatterSim with rmax ≥ 0.99 Å. The refined prediction is `sign(x - C * dθ)` with C = -p_θ/(s + p_x) = 0.6957 mÅ per degree (s = 0.2886, p_x = -0.0913, p_θ = -0.1373; bend/libration R² 0.82). Read as a compensation fraction, f = 0.316 + 0.476·dθ/x, and the rule reverses F01 when f > 1. Five inputs were explored on the three models with the same component fits (angle, O...O, H...O, number of acceptors, bifurcated fraction). The angle is the one the physical argument names, and it also had the best three-model sign count of the five, so the choice was not blind to that outcome.

## Predeclared test

Held out: SevenNet rows of the headline population (O-H pairs, rmax ≥ 0.99 Å, |dX-H| ≥ 5 mÅ, no target cut), constants frozen. Success: refined accuracy at least 5 points above F01 on those rows AND mp-985293 pairs right in at least half of SevenNet's rows that contain it. Failure otherwise. P06 recorded before scoring that this could not succeed: F01 was already 10 of 10 on these rows (decision 07), and none of them contains mp-985293. Leave-one-formula-out on the three models counts as an improvement only above F01's 185 of 212.

## Result

| set | F01 | refined (angle) | notes |
|---|---|---|---|
| SevenNet headline rows (held out) | 10/10 | 10/10 | gain 0 points; 0 rows contain mp-985293 |
| SevenNet, all 14 O-H rows, no cuts (secondary) | 12/14 | 12/14 | same rows wrong |
| Three models, in-sample | 185/212 | 184/212 | mp-985293 rows 8/28 to 12/28, other rows 177/184 to 172/184 |
| Three models, leave one formula out | 185/212 | 182/212 | baseline 131/212; C 0.647 to 0.755 across folds |
| Al(OH)3 fold | 8/28 | 11/28 | baseline 19/28 |
| Unique-pair majority, three models | 74 / 0 / 10 | 73 / 1 / 10 | right / tie / wrong |

Per model in-sample (refined): MACE 53/68, ORB 64/73, MatterSim 67/71 (F01: 52, 64, 69).

The angle carries real information about the compensation. Its predicted fraction ranks the computed one with Spearman 0.65 over 211 headline rows (0.54 without mp-985293), and it places the mp-985293 rows higher than the rest (predicted median 0.84 against 0.48). It does not place them above 1: their computed fraction has median 1.09 (0.95 to 1.32). In the other 184 rows, 5 are predicted above 1 and 7 are computed above 1, with no overlap. The angle turns five mp-985293 rows right (MACE and ORB rows with the partners that change angle most, mp-37836, mp-554883 and JVASP-29414) and costs one MatterSim mp-985293 row and five rows elsewhere (Co(OH)2, CsHSO4, ScOOH, two YOOH), where a large gain in linearity does not reverse the sign. No mp-985293 pair changes its majority.

## Verdict

The predeclared test failed, and it was certain to fail before scoring because F01 already scores 10 of 10 on the held-out SevenNet rows, none of which involve mp-985293. The informative part is the three-model check: no geometry-only refinement with at most two inputs tried here beats F01. The physically motivated angle rule is one row worse in sample, three rows worse in leave-one-formula-out, and leaves all 10 wrong pairs wrong. The mp-985293 failure is consistent with "more linear hydrogen bonds, more bend/libration compensation", but the mean angle explains only part of its excess, so the cause stays unexplained and the F01 rule and its stated counterexample stand as frozen. A held-out set that contains mp-985293 or other high-compensation pairs would be needed for a test that could succeed.
