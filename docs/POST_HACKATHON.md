# After the hackathon: corrections

The hackathon submission (branch `main`, the write-up, the video and the posts) is left as submitted. This page records what we learned afterwards and what it changes. Work continues on branch `post-hackathon`.

## Short version

During the hackathon we found a general rule: deuteration favours the polymorph with the shorter O-H bonds when hydrogen bonds are moderate to strong. After submission we found that Graham and co-workers had observed the same direction in 1980, within two mineral groups, as a qualitative remark. The general rule, tested across 220 polymorph pairs and 23 formulas with its size measured and turned into a pressure prediction, is ours; the direction should be credited to them. A referee-style review of the paper also sharpened two details of the claim (sections 2 and 3).

## 1. The direction is prior art

Graham, Sheppard and Heaton (Geochim. Cosmochim. Acta 44, 353 (1980), [doi:10.1016/0016-7037(80)90143-x](https://doi.org/10.1016/0016-7037(80)90143-x)) measured D/H fractionation between water and two groups of hydrogen-bonded minerals: the AlO(OH) dimorphs boehmite and diaspore, and zoisite, clinozoisite and epidote. Their abstract says "the shorter the O-H...O bridge, the more depleted is the mineral in D". A shorter O...O bridge means a stronger hydrogen bond and a longer O-H bond, so this is the direction of F01.

They describe the relation as qualitative, hold it within each mineral group and caution against generalising. They give no slope, no expression in bond length and no mechanism. The mechanism (stretch against bend zero-point energy) is also known (McKenzie et al. 2014, 2015).

We used Graham's boehmite and diaspore values in F12, but read them from a compilation (Chacko et al. 2001) and did not open the primary paper. Our prior-art searches used physics vocabulary (polymorph, phase stability, isotope effect) and missed the geochemistry wording (fractionation, dimorphs, mineral-water).

The write-up and posts say a logged search "found no general rule for when this happens or in which direction". That still holds for a general, tested rule. It should have credited Graham et al. for the direction within those two mineral groups.

## 2. The weak side fails; it does not reverse

The README and the paper draft said the rule reverses for weak hydrogen bonds (2 of 20 right). In all 20 of those evaluations the isotope free-energy difference has the same sign, so a constant guess gets 20 of 20, and 17 of the 18 misses sit just below the post hoc 0.99 Å boundary. A reversed bond-length dependence cannot be told apart from how the pairs happen to be oriented. The correct statement is that the rule fails for weak hydrogen bonds.

## 3. The count depends on the model's bend and libration term

On the 212 headline evaluations the rule is right in 185 against 131 for a constant guess. If the bend and libration term were 10, 20 or 30% stronger than the models give, the count would fall to 167, 155 or 140. If the stretch term were 22% weaker (the upper end allowed by our own comparison with the experimental stretch correlation), it would fall to 150. At the model-relaxed geometries used in the screen, the models' zero-point energy differences are off by 1.4 to 1.9 meV per H against DFT, while the median effect is 2.4 meV per H. No path-integral or DFT calculation of the effect has been done on any headline pair yet (predeclared as P12, not run).

## What we found

* The data set: harmonic H/D free-energy differences for 220 inorganic polymorph pairs in three universal ML potentials.
* Within these models, the free-energy difference follows the change in mean O-H length at 0.11 to 0.15 meV per H per mÅ, and bend and libration cancel about half of the stretch term.
* Within these models, the rule is right in 123 of 124 evaluations where the effect is larger than the spread between models.
* An analytic one-mode estimate gives the sign of the stretch slope and its size within 4 to 34% ([M03 note](https://doi.org/10.5281/zenodo.23600366)).
* Graham's measured boehmite and diaspore difference agrees in sign with all three models (F12; the source gives no uncertainty).
* A testable prediction: deuteration raises the diaspore to δ-AlOOH transition by about 1 GPa at 300 K in the models.

All of it is computational, harmonic and at fixed geometry. The prospective test on new pairs failed.

## Next

P12, a predeclared path-integral check on a few headline pairs, decides whether the slope is a property of the materials or of the models. The paper draft is being revised along decisions 15 and 16.

## Records

* Literature sweep and full-text check: [research/prior_art_sweep/](research/prior_art_sweep/)
* Prior-art wording: [decisions/15-prior-art-novelty.md](decisions/15-prior-art-novelty.md)
* Paper review, round 2: [decisions/16-paper-review-round2.md](decisions/16-paper-review-round2.md)
* P12 plan: [specs/pimd-p12.md](specs/pimd-p12.md)
