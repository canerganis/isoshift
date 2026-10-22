# The short-bond rule: deuteration and polymorph stability in hydrogen-bonded crystals

In crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds. We call this the short-bond rule. Harmonic H and D free energies of 220 polymorph pairs from three universal ML potentials (MACE, ORB, MatterSim) follow it in 185 of 212 model evaluations, against 131 for a constant-sign baseline. The rule fails for weak hydrogen bonds, and it predicts that deuteration raises the diaspore to δ-AlOOH transition pressure by about 1 GPa. Neither the rule nor the prediction has been tested experimentally.

https://youtu.be/T007LHdLUjk

## Method

Free-energy gaps between polymorphs are often smaller than the errors of universal ML potentials, so we compute only the isotope double difference

$$\Delta\Delta F_{\mathrm{iso}} = [F_\mathrm{D}(b) - F_\mathrm{H}(b)] - [F_\mathrm{D}(a) - F_\mathrm{H}(a)].$$

Force constants do not depend on mass, so one phonon calculation per structure gives both isotopes, and the static energy gap between the polymorphs cancels. SevenNet is used for sign votes only.

## Result

Across 220 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.11 to 0.13 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds, chosen after inspecting the data), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (84 pairs, 28 formulas), against 131 of 212 for a constant-sign baseline fitted on leave-one-formula-out training folds. By model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293.

![Headline figure](https://raw.githubusercontent.com/canerganis/isoshift/main/figures/fig_headline.png)

*O-H pairs with |Δ mean O-H| ≥ 5 mÅ. Regime by the larger mean model O-H of the pair; the 0.99 Å boundary was chosen after inspecting the data (nested re-choice picks 1.00 Å in 30 of 31 folds). Open markers: evaluations involving Al(OH)3 mp-985293, kept in the counts. Evaluations share structures and models.*

Below the boundary the rule fails (2 of 20 evaluations). In the pairs with mp-985293, bend and libration cancel 95 to 132% of the stretch term instead of about half. The model O-H stretch frequencies follow the measured Libowitzky correlation for O...O distances of 2.50 to 2.80 Å (slope ratios 0.91 to 0.92), which checks the stretch term but not the free energies.

## Prediction for diaspore and δ-AlOOH

δ-AlOOH is a candidate carrier of water in the deep Earth. At 300 K the models place the transition of AlOOD 1.33 GPa (MACE) and 1.13 GPa (ORB) above that of AlOOH (8.76 and 13.00 GPa); near 1000 K the shift is +0.7 to +0.9 GPa in all three models. It is an exploratory sign prediction, because δ-AlOOH has proton disorder in this pressure range that harmonic physics omits ([card](https://github.com/canerganis/isoshift/blob/main/docs/findings/CARD-AlOOH.md)).

## How to test it

No polymorph isotope free energy has been measured. D/H fractionation between two coexisting polymorphs constrains it through $\Delta\Delta G_{\mathrm{iso}} = n_\mathrm{H} k_\mathrm{B} T \ln\alpha + R$, with R = 0 for one H site type such as AlOOH ([M02](https://github.com/canerganis/isoshift/blob/main/docs/math/M02-bigeleisen-bridge.md)). Matched reversed-bracket runs on AlOOH and AlOOD would test the sign of the pressure shift.

## Limits

The 0.99 Å boundary was chosen after inspecting the data. Re-choosing it inside training folds gives 183 of 210 held-out evaluations right against 131, but the fold holding out Al(OH)3 scores 8 of 28 against 19, so no sharp boundary is established. F11, a post-freeze test on new pairs, failed: most rows did not pass the numerical quality rules, and on the 24 clean rows the rule (16 right) did not beat a constant guess (19). The three potentials share PBE-level training data, so their agreement is not a validation. The physics is harmonic or quasi-harmonic, without anharmonicity, tunnelling or proton disorder, and the harmonic brucite to goethite D/H fractionation is 5 to 10 times larger than measured (F05).

## Prior work

McKenzie et al. described the competition between stretch and bend zero-point terms in hydrogen bonds, and Du et al. (arXiv:2610.11325) treat single systems with path integrals. Large-scale harmonic isotope thermodynamics exists for metal hydrides (Bourgeois et al. 2018), without polymorph pairs. What is new here is the polymorph-stability version of the stretch-bend competition, with its slope and its failure boundary. A logged literature search found no earlier survey of H/D free-energy differences across polymorph pairs of the same compound.

## Who could use it

Neutron groups use δ-AlOOD as a stand-in for hydrous mantle phases, yet deuteration moves its measured proton-disorder transition from 9.0 to 13.4 GPa (Sano-Furukawa et al. 2018). Isotope geochemists measuring D/H partitioning between coexisting minerals can run the test above.

## How the work was done

AI agents did the work under my direction: literature agents on Valency Bond (182 logged queries, [extraction audit](https://github.com/canerganis/isoshift/blob/main/docs/story/agent_extraction_audit.md)), two-model mathchecks for every formula, three-model councils that recorded their dissent ([decisions](https://github.com/canerganis/isoshift/tree/main/docs/decisions)), and a blind Codex reimplementation that matched ΔΔF_iso to 1e-9 meV/atom (F06). Prediction files were committed to git before their data, except the P04 scoring rule, which came with its result; F07, F08, F09 (H1) and F11 failed and are reported. A marimo app shows the cached results without a GPU.

Built before the event (git tag `pre-event-baseline`): the generic LLM harness and the `isoshift/` GPU job pool. Built on 21 and 22 October: `src/isoshift_event/`, `app/`, and every finding, prediction and decision ([PROVENANCE.md](https://github.com/canerganis/isoshift/blob/main/docs/PROVENANCE.md)).

Evidence index: [docs/INDEX.md](https://github.com/canerganis/isoshift/blob/main/docs/INDEX.md).
