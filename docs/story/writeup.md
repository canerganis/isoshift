# The short-bond rule: deuteration and polymorph stability in hydrogen-bonded crystals

The short-bond rule: in crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds. We found it in a screen of 220 polymorph pairs with three universal ML potentials (MACE, ORB, MatterSim), where it holds in 185 of 212 model evaluations against 131 for a constant-sign baseline, and it rests on a correlation we did not find in earlier work: the isotope free-energy difference between two polymorphs follows the change in their mean O-H bond length, by 0.11 to 0.13 meV per H for each mÅ. Deuterium replaces hydrogen in neutron experiments, isotope tracing and synthesis, yet a logged literature search found no general rule for whether the swap changes which crystal structure is stable. The rule predicts that deuteration raises the diaspore to δ-AlOOH transition by about 1 GPa (δ-AlOOH is a candidate carrier of water into the deep Earth). Neither the rule nor the prediction has been tested experimentally yet.

https://youtu.be/X8ckZ7dV40Y

## What we found at this hackathon

1. The short-bond rule. In crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds: 185 of 212 model evaluations, against 131 for a constant-sign baseline.
2. A quantitative correlation behind it. The isotope free-energy difference between two polymorphs changes by 0.11 to 0.13 meV per H for each mÅ change in mean O-H length; the O-H stretch drives it and bending and libration cancel about half.
3. Where the rule stops. It fails for weak hydrogen bonds (2 of 20), and in one Al(OH)3 structure bend and libration outweigh the stretch.
4. A testable prediction. Deuteration raises the diaspore to δ-AlOOH transition by +1.13 to +1.33 GPa at 300 K (exploratory sign prediction).

## Why it matters

Neutron crystallographers deuterate samples to reduce incoherent background and often treat the deuterated phase as a stand-in for the hydrogenous one, yet in δ-AlOOH deuteration moves a measured proton-disorder transition from 9.0 to 13.4 GPa (Sano-Furukawa et al. 2018). Isotope effects on stability can be large, and the short-bond rule says in which polymorph pairs to expect them and in which direction.

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

Below the boundary the rule fails (2 of 20 evaluations). In the pairs with mp-985293, bend and libration cancel 95 to 132% of the stretch term instead of about half, which marks where bond length alone stops predicting the sign. The model O-H stretch frequencies follow the measured Libowitzky correlation for O...O distances of 2.50 to 2.80 Å (slope ratios 0.91 to 0.92), which checks the stretch term but not the free energies.

## Prediction for diaspore and δ-AlOOH

δ-AlOOH is a candidate carrier of water in the deep Earth. At 300 K the models place the transition of AlOOD 1.33 GPa (MACE) and 1.13 GPa (ORB) above that of AlOOH (8.76 and 13.00 GPa); near 1000 K the shift is +0.7 to +0.9 GPa in all three models. It is an exploratory sign prediction, because δ-AlOOH has proton disorder in this pressure range that harmonic physics omits ([card](https://github.com/canerganis/isoshift/blob/main/docs/findings/CARD-AlOOH.md)).

## How to test it

No polymorph isotope free energy has been measured. D/H fractionation between two coexisting polymorphs constrains it through $\Delta\Delta G_{\mathrm{iso}} = n_\mathrm{H} k_\mathrm{B} T \ln\alpha + R$, with R = 0 for one H site type such as AlOOH ([M02](https://github.com/canerganis/isoshift/blob/main/docs/math/M02-bigeleisen-bridge.md)). Matched reversed-bracket runs on AlOOH and AlOOD would test the sign of the pressure shift.

## Limits

The 0.99 Å boundary was chosen after inspecting the data; re-choosing it inside training folds still gives 183 of 210 held-out evaluations right against 131. The free energies are harmonic or quasi-harmonic, and the three potentials share PBE-level training data, so the rule is a computational result that awaits measurement. Not every blind test passed: the ice-boundary test (F07) failed, the mineral fractionation test (F02) was mixed, and a follow-up test on newly computed pairs (F11) was limited by phonon quality and did not reach its bar. All are reported in the repository.

## Prior work

McKenzie et al. described the competition between stretch and bend zero-point terms in hydrogen bonds, and Du et al. (arXiv:2610.11325) treat single systems with path integrals. Large-scale harmonic isotope thermodynamics exists for metal hydrides (Bourgeois et al. 2018), without polymorph pairs. What is new here is the link from that competition to the relative stability of polymorph pairs: a quantitative slope against bond length, a sign rule, and the conditions under which it fails. A logged literature search found no earlier survey of H/D free-energy differences across polymorph pairs of the same compound.

## How we used Valency Bond and marimo

Valency Bond was our literature search. Agents queried Bond to find the experimental data each blind test needed: H/D cell volumes for the volume test, mineral-water D/H fractionation for the fractionation test and the H2O and D2O ice boundaries for the ice test. Another 20 Bond queries were the prior-art search, which found no earlier survey of H/D free energies across polymorph pairs and surfaced the closest recent work (Du et al. 2026). Every query is logged with its purpose and what was kept (182 rows in `logs/bond_queries.jsonl`). Bond was good at finding sources; the numbers were then checked by a second reader, who rejected any value without a quote, and by the board, which caught a reference value off by a factor of 2. Some cited values were reached through the papers Bond pointed to rather than a logged Bond result, and the [extraction audit](https://github.com/canerganis/isoshift/blob/main/docs/story/agent_extraction_audit.md) lists which.

marimo is how the results are shown and checked. The app opens on the frozen 185 of 212 result and has five tabs. In "F01 isotope rule" a slider moves the O-H boundary and the counts update, so a reader can see how much the result depends on the 0.99 Å choice; the frozen number stays in the banner. "Check a pair" lets you pick any screened pair and see each model's isotope free energy, the rule's call and the stretch, bend and libration split, with diaspore against δ-AlOOH as the default. "How we know" follows one measured value, brucite, from the Bond queries to the decision that used it. "Benchmark & stretch check" shows the model checks against DFT phonons and measured spectra, and "Legacy explorer" ranks candidate pairs and has a pair viewer with a static energy offset slider, which moves the H and D curves together and leaves the isotope difference unchanged. Everything is precomputed, so `marimo run app/isoshift_app.py` works on a laptop without a GPU.

## How the work was done

AI agents did the work under my direction, and each part had a job. Literature agents on Valency Bond found the measured values (above). Every formula passed two independent derivations. Three-model councils decided the hard calls and recorded their dissent ([decisions](https://github.com/canerganis/isoshift/tree/main/docs/decisions)). A blind Codex reimplementation matched $\Delta\Delta F_{\mathrm{iso}}$ to $10^{-9}$ meV/atom (F06), which checks the code, not the physics.

Every prediction file was committed to git before its data, except the P04 scoring rule, which came with its result. Tests that failed are reported next to the ones that passed. A marimo app shows the cached results without a GPU.

Built before the event (git tag `pre-event-baseline`): the generic LLM harness and the `isoshift/` GPU job pool. Built on 21 and 22 October: `src/isoshift_event/`, `app/`, and every finding, prediction and decision ([PROVENANCE.md](https://github.com/canerganis/isoshift/blob/main/docs/PROVENANCE.md)).

Evidence index: [docs/INDEX.md](https://github.com/canerganis/isoshift/blob/main/docs/INDEX.md).

## References

1. Sano-Furukawa, A., Hattori, T., Komatsu, K. et al. Direct observation of symmetrization of hydrogen bond in δ-AlOOH under mantle conditions using neutron diffraction. Sci. Rep. 8, 15520 (2018). https://doi.org/10.1038/s41598-018-33598-2
2. McKenzie, R. H., Bekker, C., Athokpam, B. et al. Effect of quantum nuclear motion on hydrogen bonding. J. Chem. Phys. 140, 174508 (2014). https://doi.org/10.1063/1.4873352
3. McKenzie, R. H., Athokpam, B., Ramesh, S. G. Isotopic fractionation in proteins as a measure of hydrogen bond length. J. Chem. Phys. 143, 044309 (2015). https://doi.org/10.1063/1.4927391
4. Du et al. Isotope Effects at Classical Cost through Mass-Differentiable Machine Learning. arXiv:2610.11325 (2026). https://arxiv.org/abs/2610.11325
5. Bourgeois, N., Crivello, J.-C., Cenedese, P. et al. Vibration analysis of hydrogen, deuterium and tritium in metals: consequences on the isotope effect. J. Phys.: Condens. Matter 30, 335402 (2018). https://doi.org/10.1088/1361-648X/aad259
6. Libowitzky, E. Correlation of O-H stretching frequencies and O-H...O hydrogen bond lengths in minerals. Monatsh. Chem. 130, 1047 (1999). https://doi.org/10.1007/BF03354882
