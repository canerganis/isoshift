# P06. Predeclared test of a refined F01 rule with the hydrogen-bond angle (post-freeze addendum)

Status: predeclared. Written and committed before any SevenNet score of the refined rule was computed. This is an addendum after the compute freeze. It does not change the frozen F01 headline of decision 07 (185 of 212, baseline 131, pairs 74 right, 0 ties, 10 wrong). Code: `src/isoshift_event/refined_rule.py` (`constants` mode was the only mode run before this file was committed). Geometry table: `results/hbond_geometry.csv`.

## Question

F01 predicts that deuteration favours the polymorph with the shorter O-H bonds, `sign(ddF_iso) = sign(dX-H)`. It fails in the 10 pairs that contain Al(OH)3 mp-985293, where bend and libration cancel 95 to 132% of the stretch term instead of about half. Physical idea (McKenzie et al. 2014, 2015): bend and libration stiffen as a hydrogen bond gets stronger and more linear. mp-985293 has nearly linear hydrogen bonds (mean O-H...O angle 174 to 175 degrees in the three models) while its partners are bent (144 to 162 degrees). F01 sees only the O-H length change. Can one extra geometric input predict when the compensation fraction exceeds 1 and the sign reverses?

## Inputs (geometry only)

Per relaxed structure and model, from the phonopy unit cell in the force-constant cache:

1. O-H donor: an H whose nearest non-H atom is O at 1.15 Å or less.
2. Acceptor: the nearest O other than the donor with H...O below 2.6 Å, found with a periodic neighbour list (same cut as `stretch_check._donors`).
3. θ: the O-H...O angle at H, in degrees (180 is linear). Structure value: mean θ over O-H donors that have an acceptor.

Pair inputs, in the orientation of `decompose.py` (b minus a, with struct_a and struct_b from `results/screen_pairs_refined.csv`):

1. `x = dXH_mean_A * 1000`, the F01 input (mÅ, from `results/decompose_pairs.csv`).
2. `dθ = θ(b) - θ(a)` (degrees).

## Refined rule (exact formula and every constant)

Component model, each term fitted by least squares through the origin on its own mode-resolved component, never on the sign of the total:

    stretch term per H         = s * x
    bend/libration term per H  = p_x * x + p_θ * dθ
    refined sign               = sign((s + p_x) * x + p_θ * dθ) = sign(x - C * dθ)

Constants (MACE, ORB and MatterSim only; fit set: clean covalent O-H rows with rmax ≥ 0.99 Å and finite dθ, any |dX-H|, no cut on the target; 292 rows, the population of `rule_cv.oh_strong_slopes`):

| constant | value | unit |
|---|---|---|
| s | 0.28863621384728644 | meV per H per mÅ |
| p_x | -0.09132948845203431 | meV per H per mÅ |
| p_θ | -0.1372649219565174 | meV per H per degree |
| C = -p_θ / (s + p_x) | 0.6956930722029026 | mÅ per degree |

Read as a predicted compensation fraction: `f = A + B * dθ / x`, with `A = -p_x / s = 0.31641728955173837` and `B = -p_θ / s = 0.4755637559365383` mÅ per degree. The refined rule reverses F01 exactly when the predicted fraction exceeds 1, that is when the polymorph with the longer O-H bonds also gains more than about 1.44 degrees of linearity per mÅ. R² of the bend/libration fit: 0.82. Rows without a finite dθ (no acceptor in one structure) fall back to `sign(x)`.

## How the input was chosen, and what was already seen (three models only)

Five candidate inputs were explored on the three headline models, each with constants from the same component fits: dθ, mean O...O, mean H...O, mean number of acceptors, fraction of bifurcated donors. The H-bond angle is the candidate the physical argument names, and it also gave the best three-model in-sample sign count of the five, so the choice of input is not blind to the three-model outcome. The constants are not fitted to the sign. Numbers already seen before this file was written, on the 212 headline rows:

| rule | in-sample | mp-985293 rows | other rows |
|---|---|---|---|
| F01, sign(x) | 185/212 | 8/28 | 177/184 |
| refined, dθ (C = 0.6957) | 184/212 | 12/28 | 172/184 |
| dO...O, `sign(x + 0.0621 * dOO_mÅ)` | 178/212 | 10/28 | 168/184 |
| dH...O, `sign(x + 0.0482 * dHO_mÅ)` | 181/212 | 12/28 | 169/184 |
| d(number of acceptors) | 183/212 | 8/28 | 175/184 |
| d(bifurcated fraction) | 179/212 | 7/28 | 172/184 |

Leave-one-formula-out on the three models (procedure below) was also run during derivation: refined 182/212, mp-985293 rows 11/28, Al(OH)3 fold 11/28 (F01 8/28, training-fold baseline 19/28). So no candidate improved on F01 on the three models before the held-out test.

## Predeclared held-out test (SevenNet)

Held-out set: the SevenNet evaluations (`model == "sevenn"` rows of `results/decompose_pairs.csv`). SevenNet was never used in any fit here or in F01.

Population: the headline definition applied to SevenNet rows, `rule_cv._headline` (clean covalent, O-H pairs, rmax ≥ 0.99 Å from SevenNet's own mean X-H lengths, |dX-H| ≥ 5 mÅ, no cut on the target).

Constants: the four values above, frozen. Geometry: SevenNet's own relaxed structures, same definitions.

**Success:** refined-rule sign accuracy on the SevenNet rows exceeds F01's accuracy on the same rows by at least 5 percentage points, AND the refined rule gets the mp-985293 pairs right in at least half of SevenNet's rows that contain mp-985293. **Failure otherwise.**

### Known before the test, stated here so the verdict cannot be read as news

1. F01's SevenNet score on this population is already public: 10 of 10 (decision 07, `sevenn_sign_votes.sevenn_only_oh_unfiltered_strong` in `results/F01_cv.json`). An accuracy of 100% cannot be exceeded by 5 points.
2. None of the 10 SevenNet rows contains mp-985293. This was checked from pair ids, dX-H and rmax only, with no ddF value of the refined rule computed. Clause 2 therefore has no rows to satisfy and is counted as not met.

So the predeclared test is failure by construction, whatever the refined rule does on SevenNet. The protocol is kept as given and this is recorded before the score, not after.

### Secondary, descriptive only (not part of the criterion)

1. Non-inferiority: how many of the 10 SevenNet headline rows the refined rule keeps (F01: 10).
2. All clean covalent SevenNet O-H rows with no |dX-H| cut and no regime cut, both rules.

## Predeclared leave-one-formula-out score (three headline models)

For each formula, refit s, p_x and p_θ on the fit set without that formula, and score that formula's headline rows (212 rows, 84 pairs, 28 formulas) with `sign((s + p_x) * x + p_θ * dθ)`, falling back to `sign(x)` without dθ. Report total right, mp-985293 rows, other rows, per model, unique-pair majority and the Al(OH)3 fold, against F01 (185/212, a fixed rule with nothing to refit) and the training-fold constant-sign baseline (131/212). Reading: the refinement counts as an improvement on the three models only if its LOFO count is above 185/212; at or below it, the angle does not rescue F01. The value seen during derivation (182/212) is disclosed above, so this is a cross-validation, not a blind test.

## What this file does not do

It does not edit the F01 headline, README, write-up, video, app, GOAL, LEDGER or any decision file. Whatever the result, F01 stays as frozen in decision 07; the outcome goes into `docs/findings/F08-refined-rule.md` and `results/F08_refined_rule.json`.
