# The short-bond rule: deuteration and polymorph stability in hydrogen-bonded crystals

The short-bond rule: in crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds. We found it in a screen of 220 polymorph pairs with three universal ML potentials (MACE, ORB, MatterSim), where it holds in 185 of 212 model evaluations against 131 for a constant-sign baseline, and it rests on a correlation we did not find in earlier work: the isotope free-energy difference between two polymorphs follows the change in their mean O-H bond length, by 0.11 to 0.13 meV per H for each mÅ. Deuterium replaces hydrogen in neutron experiments, isotope tracing and synthesis, yet a logged literature search found no general rule for whether the swap changes which crystal structure is stable. The rule predicts that deuteration raises the diaspore to δ-AlOOH transition by about 1 GPa (δ-AlOOH is a candidate carrier of water into the deep Earth). Neither the rule nor the prediction has been tested experimentally yet.

https://youtu.be/X8ckZ7dV40Y

## What we found at this hackathon

1. The short-bond rule. In crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds: 185 of 212 model evaluations, against 131 for a constant-sign baseline.
2. A quantitative correlation behind it. The isotope free-energy difference between two polymorphs changes by 0.11 to 0.13 meV per H for each mÅ change in mean O-H length; the O-H stretch drives it and bending and libration cancel about half.
3. Where the rule stops. It fails for weak hydrogen bonds (2 of 20), and in one Al(OH)3 structure bend and libration outweigh the stretch.
4. A testable prediction. Deuteration raises the diaspore to δ-AlOOH transition by +1.13 to +1.33 GPa at 300 K (exploratory sign prediction).

## Why it matters

Neutron crystallographers deuterate samples to reduce incoherent background and often treat the deuterated phase as a stand-in for the hydrogenous one, yet in δ-AlOOH deuteration moves a measured proton-disorder transition from 9.0 to 13.4 GPa [1]. Isotope effects on stability can be large, and the short-bond rule says in which polymorph pairs to expect them and in which direction.

The result can be checked now. It gives a number for one transition (+1.13 to +1.33 GPa for AlOOD at 300 K) and names the measurement that would test the rule directly, D/H partitioning between coexisting polymorphs.

## Method

Free-energy gaps between polymorphs are often smaller than the errors of universal ML potentials, so we compute only the isotope double difference

$$
\Delta\Delta F_{\mathrm{iso}} = [F_\mathrm{D}(b) - F_\mathrm{H}(b)] - [F_\mathrm{D}(a) - F_\mathrm{H}(a)]
$$

In the harmonic treatment force constants do not depend on mass, so one phonon calculation per structure gives both isotopes and the static energy gap between the polymorphs cancels. This is what makes a screen of hundreds of pairs feasible with fast universal potentials. MACE, ORB and MatterSim give every number; SevenNet is used for sign votes only.

## Result

Across 220 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.11 to 0.13 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds, chosen after inspecting the data), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (84 pairs, 28 formulas), against 131 of 212 for a constant-sign baseline fitted on leave-one-formula-out training folds. By model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293.

![Headline figure](https://raw.githubusercontent.com/canerganis/isoshift/main/figures/fig_headline.png)

*O-H pairs with |Δ mean O-H| ≥ 5 mÅ. Regime by the larger mean model O-H of the pair; the 0.99 Å boundary was chosen after inspecting the data (nested re-choice picks 1.00 Å in 30 of 31 folds). Open markers: evaluations involving Al(OH)3 mp-985293, kept in the counts. Evaluations share structures and models.*

Below the boundary the rule fails (2 of 20 evaluations). In the pairs with mp-985293, bend and libration cancel 95 to 132% of the stretch term instead of about half, which marks where bond length alone stops predicting the sign. The model O-H stretch frequencies follow the measured Libowitzky correlation [6] for O...O distances of 2.50 to 2.80 Å (slope ratios 0.91 to 0.92), which checks the stretch term but not the free energies.

## Prediction for diaspore and δ-AlOOH

δ-AlOOH is a candidate carrier of water in the deep Earth. At 300 K the models place the transition of AlOOD 1.33 GPa (MACE) and 1.13 GPa (ORB) above that of AlOOH (8.76 and 13.00 GPa); near 1000 K the shift is +0.7 to +0.9 GPa in all three models. It is an exploratory sign prediction, because δ-AlOOH has proton disorder in this pressure range that harmonic physics omits ([card](https://github.com/canerganis/isoshift/blob/main/docs/findings/CARD-AlOOH.md)).

## How to test it

No polymorph isotope free energy has been measured. D/H fractionation between two coexisting polymorphs constrains it through $\Delta\Delta G_{\mathrm{iso}} = n_\mathrm{H} k_\mathrm{B} T \ln\alpha + R$, with R = 0 for one H site type such as AlOOH ([M02](https://github.com/canerganis/isoshift/blob/main/docs/math/M02-bigeleisen-bridge.md)). Matched reversed-bracket runs on AlOOH and AlOOD would test the sign of the pressure shift.

## Limits

The 0.99 Å boundary was chosen after inspecting the data; re-choosing it inside training folds still gives 183 of 210 held-out evaluations right against 131. The free energies are harmonic or quasi-harmonic, and the three potentials share PBE-level training data, so the rule is a computational result that awaits measurement. Not every blind test passed: the ice-boundary test (F07) failed, the mineral fractionation test (F02) was mixed, and a follow-up test on newly computed pairs (F11) was limited by phonon quality and did not reach its bar. All are reported in the repository.

## Prior work

McKenzie et al. [2], [3] described the competition between stretch and bend zero-point terms in hydrogen bonds, and Du et al. [4] treat single systems with path integrals. Large-scale harmonic isotope thermodynamics exists for metal hydrides [5], without polymorph pairs. What is new here is the link from that competition to the relative stability of polymorph pairs: a quantitative slope against bond length, a sign rule, and the conditions under which it fails. A logged literature search found no earlier survey of H/D free-energy differences across polymorph pairs of the same compound.

## How we used Valency Bond and marimo

Agents queried Valency Bond for the experimental data behind each blind test (H/D cell volumes, mineral D/H fractionation, ice phase boundaries) and for the prior-art search, which surfaced Du et al. [4]. All 182 queries are logged with their purpose in `logs/bond_queries.jsonl`. Bond found the sources; a second reader and the board checked the numbers, and the [extraction audit](https://github.com/canerganis/isoshift/blob/main/docs/story/agent_extraction_audit.md) lists values reached by other routes.

The results are a marimo app. A slider on the F01 tab moves the 0.99 Å boundary and recounts the rule while the frozen result stays in the banner; Check a pair shows each model's isotope free energy and its stretch and bend split for any screened pair; How we know traces a measured value from the Bond queries to the decision that used it. Everything is precomputed, so `marimo run app/isoshift_app.py` runs on a laptop without a GPU.

## How the work was done

AI agents did the work under my direction, each with a fixed role, and I set the question, approved each step and made the calls that needed a person.

1. Conductor: Claude Opus 5.5 planned the work, ran the GPU screen with MACE, ORB, MatterSim and SevenNet, wrote the analysis and kept a ledger of every step.
2. Literature and blind-test agents: Claude Sonnet instances queried Valency Bond, each with one task (a validation value, an ice boundary, a fractionation factor); the blind-test agents never saw our predictions.
3. Math checks: every formula was derived twice, independently, by GPT-6 Astra and Claude Opus, and the code used it only after the two agreed.
4. Councils: hard calls (the freeze, what to claim, what to drop) went to a council of Claude Opus, GPT-6 Astra and Gemini 4 Argon. Each member answered blind, then read and challenged the others; the chair (Claude Opus) decided by argument, not vote, and recorded the dissent ([decisions](https://github.com/canerganis/isoshift/tree/main/docs/decisions)).
5. Independent check: GPT-6 Astra, through Codex and without our code, rewrote the calculation from the equations and matched $\Delta\Delta F_{\mathrm{iso}}$ to $10^{-9}$ meV/atom (F06), which checks the code, not the physics.

Every prediction file was committed to git before its data, except the P04 scoring rule, which came with its result. Tests that failed are reported next to the ones that passed. A marimo app shows the cached results without a GPU.

Built before the event (git tag `pre-event-baseline`): the generic LLM harness and the `isoshift/` GPU job pool. Built on 21 and 22 October: `src/isoshift_event/`, `app/`, and every finding, prediction and decision ([PROVENANCE.md](https://github.com/canerganis/isoshift/blob/main/docs/PROVENANCE.md)).

Evidence index: [docs/INDEX.md](https://github.com/canerganis/isoshift/blob/main/docs/INDEX.md).

Archived release: [doi:10.5281/zenodo.23578412](https://doi.org/10.5281/zenodo.23578412).

## References

[1] A. Sano-Furukawa et al., "Direct observation of symmetrization of hydrogen bond in δ-AlOOH under mantle conditions using neutron diffraction," *Sci. Rep.*, vol. 8, no. 1, Art. no. 15520, 2018, doi: [10.1038/s41598-018-33598-2](https://doi.org/10.1038/s41598-018-33598-2).

[2] R. H. McKenzie, C. Bekker, B. Athokpam, and S. G. Ramesh, "Effect of quantum nuclear motion on hydrogen bonding," *J. Chem. Phys.*, vol. 140, no. 17, Art. no. 174508, 2014, doi: [10.1063/1.4873352](https://doi.org/10.1063/1.4873352).

[3] R. H. McKenzie, B. Athokpam, and S. G. Ramesh, "Isotopic fractionation in proteins as a measure of hydrogen bond length," *J. Chem. Phys.*, vol. 143, no. 4, Art. no. 044309, 2015, doi: [10.1063/1.4927391](https://doi.org/10.1063/1.4927391).

[4] M.-Z. Du et al., "Isotope effects at classical cost through mass-differentiable machine learning," 2026, [arXiv:2610.11325](https://arxiv.org/abs/2610.11325).

[5] N. Bourgeois, J.-C. Crivello, P. Cenedese, V. Paul-Boncour, and J.-M. Joubert, "Vibration analysis of hydrogen, deuterium and tritium in metals: Consequences on the isotope effect," *J. Phys.: Condens. Matter*, vol. 30, no. 33, Art. no. 335402, 2018, doi: [10.1088/1361-648X/aad259](https://doi.org/10.1088/1361-648X/aad259).

[6] E. Libowitzky, "Correlation of O-H stretching frequencies and O-H...O hydrogen bond lengths in minerals," *Monatsh. Chem.*, vol. 130, no. 8, pp. 1047-1059, 1999, doi: [10.1007/BF03354882](https://doi.org/10.1007/BF03354882).
