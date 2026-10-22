# The short-bond rule: deuterium tips hydrogen-bonded crystals toward shorter O-H bonds

**The short-bond rule.** Swap hydrogen for deuterium in a crystal with moderate-to-strong hydrogen bonds, and it favours the polymorph with the shorter O-H bonds. We derived this rule from a screen of 220 polymorph pairs with three ML potentials: it holds in 185 of 212 evaluations (constant-sign baseline 131), fails with weak hydrogen bonds (2 of 20), and has one named Al(OH)₃ counterexample. It predicts that deuterium raises the diaspore to δ-AlOOH transition by about 1 GPa (exploratory sign). No measurement has tested it yet; D/H partitioning between coexisting polymorphs would ([M02](https://github.com/canerganis/isoshift/blob/main/docs/math/M02-bigeleisen-bridge.md)), as would matched reversed-bracket AlOOH/AlOOD runs.

Video (3:30): https://youtu.be/3gE5nxhLo80

**Why it stands out.**

1. **One testable sentence for a meV-scale effect.** Earlier work treated isotope effects on stability one system at a time; this screen counts every evaluation across 220 pairs and states where the rule holds and where it breaks.
2. **A method that removes the models' largest error.** The static energy gap cancels in the isotope double difference, and one phonon run per structure gives both isotopes, so cheap universal potentials can rank the effect.
3. **A falsifiable prediction for a deep-Earth water carrier.** Deuterium raises the diaspore to δ-AlOOH boundary by +1.13 (ORB) and +1.33 GPa (MACE) at 300 K, a number a high-pressure lab can check.
4. **Honest by construction.** Predictions were committed to git before the data, the boundary choice is disclosed, and the failed blind tests (F07, F11) are reported.

**Result (F01).** Across 220 hydrogen-compound polymorph pairs screened with three universal ML potentials, the harmonic H/D free-energy difference at 300 K changes by 0.11 to 0.13 meV per H for each mÅ difference in mean X-H length, a stretch term about half cancelled by bend and libration. When at least one polymorph has a mean model O-H length of 0.99 Å or more (a model-derived boundary for moderate to strong hydrogen bonds, chosen after inspecting the data), deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 O-H model evaluations with |Δ mean O-H| ≥ 5 mÅ (84 pairs, 28 formulas), against 131 of 212 for a constant-sign baseline fitted on leave-one-formula-out training folds. By model majority 74 pairs are right and 10 are wrong, and all 10 wrong pairs contain one Al(OH)3 structure, mp-985293.

![Headline figure](https://raw.githubusercontent.com/canerganis/isoshift/main/figures/fig_headline.png)

*O-H pairs with |Δ mean O-H| ≥ 5 mÅ. Regime by the larger mean model O-H of the pair; the 0.99 Å boundary was chosen after inspecting the data (nested re-choice picks 1.00 Å in 30 of 31 folds). Open markers: evaluations involving Al(OH)3 mp-985293, kept in the counts. Evaluations share structures and models.*

**Limits.** Re-choosing the boundary inside training folds gives 183 of 210 held-out evaluations right against 131; the fold holding out Al(OH)3 scores 8 of 28 against 19, so no sharp boundary is established, and cross-validation covers the threshold, not the choice of regime variable or eligibility cuts. F11, a post-freeze prospective test on pairs never computed before, failed its predeclared bar: 87 of 111 rows were lost to the predeclared numerical rules, and on the 24 clean rows the rule (16 right) did not beat a constant guess (19), so transfer to new pairs is not shown. The three potentials share PBE-level training data, so their agreement is not a validation; the DFT benchmark is per structure, and no DFT value of the double difference was computed. Free energies are harmonic or quasi-harmonic, without anharmonicity, tunnelling or proton disorder; the harmonic brucite to goethite D/H fractionation is 5 to 10 times larger than measured (F05). The stretch check covers O...O 2.50 to 2.80 Å, while the regime reaches about 2.93 Å. Experimental usefulness is untested, and drug or organic polymorphs lie outside this carbon-free screen.

**What is new.** McKenzie et al. showed the stretch-bend competition; Du et al. (arXiv:2610.11325) treat single systems by path integrals. New here: the short-bond rule, the polymorph-stability version of that competition, with its slope and its failure boundary. Unlike per-polymorph free energies, the double difference drops the static energy gap, where the models err most, and one phonon run per structure gives both isotopes. A literature search (logged) found no earlier survey of H/D free-energy differences across polymorph pairs of the same compound.

**What it is for.** Neutron groups use δ-AlOOD as a stand-in for hydrous mantle phases, yet deuteration moves its measured proton-disorder transition from 9.0 to 13.4 GPa (Sano-Furukawa et al. 2018), physics our harmonic models omit. For the diaspore to δ-AlOOH boundary the models put AlOOD about 1 GPa higher (exploratory sign). Isotope geochemists can run the D/H test above.

**What we learned.** Bend and libration cancel about half of the O-H stretch term, so bond length predicts the sign only where hydrogen bonds are strong. On new structures most harmonic phonons failed (F11), so transfer needs better phonons first.

**Beyond the headline (post-freeze, 22 Oct).** The predeclared explanation of the 10 wrong pairs failed (F09), F08 failed, F12 (boehmite vs diaspore) agrees in sign but is inconclusive, and F10 is an untested map.

**How the AI worked.** Valency Bond agents found validation data (182 logged queries; extraction audit: [agent_extraction_audit.md](https://github.com/canerganis/isoshift/blob/main/docs/story/agent_extraction_audit.md)). Formulas passed two-model mathchecks. Ten prediction files were committed before their data, except the P04 scoring rule, committed with its result; F07, F08, F09 (H1) and F11 failed and are reported. Three-model councils logged hard calls and dissent ([decisions](https://github.com/canerganis/isoshift/tree/main/docs/decisions)). Codex reimplemented ΔΔF_iso blind to 1e-9 meV/atom on nine rows (F06, an implementation check). A marimo app inspects the cached results without a GPU; it computes no new phonons.

**Built before vs during the event.** Before (git tag `pre-event-baseline`): the generic LLM harness and the `isoshift/` GPU job pool. During 21 and 22 Oct: all of `src/isoshift_event/` and `app/`, every finding, prediction and decision; two event-time fixes to pre-event code are disclosed in [PROVENANCE.md](https://github.com/canerganis/isoshift/blob/main/docs/PROVENANCE.md).

Evidence: [docs/INDEX.md](https://github.com/canerganis/isoshift/blob/main/docs/INDEX.md).
