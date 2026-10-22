# Judge FAQ

**Was the 0.99 Å boundary chosen after seeing the data?**
Yes. Re-chosen inside each leave-one-formula-out fold, it becomes 1.00 Å in 30 of 31 folds and gives 183 of 210 held-out evaluations right against a baseline of 131. The fold that holds out Al(OH)3 keeps 0.99 Å and scores 8 of 28 against 19, so a sharp universal boundary is not established ([F01](findings/F01-xh-length-rule.md)). The prospective test on new pairs failed its predeclared bar: 16 right of 111 rows (87 lost to the predeclared numerical rules, mostly imaginary modes); on the 24 clean rows the rule gets 16 and a constant guess 19 ([F11](findings/F11-prospective-test.md)).

**Are three ML potentials three separate checks?**
No. They share similar DFT training data, so agreement is not validation. Against PBEsol phonons their isotope ZPE error is 0.7 to 1.5 meV per H ([summary.csv](../results/benchmark/summary.csv)). A blind second code (F06) matched ours within 1e-9 meV/atom; that checks the implementation, not the physics ([output](../results/replicate_f01.json)).

**Why harmonic?**
One set of force constants gives both H and D free energies. The cost is anharmonicity: with strong, short hydrogen bonds the blind volume isotope signs were wrong ([F02](findings/F02-blind-test.md)), and the Ih-II and Ih-III ice boundaries came out with the wrong sign in 3 of 3 models ([F07](findings/F07-ice-boundary-test.md)).

**Has anything been measured?**
No polymorph isotope free energy. Stretch slopes match measured spectra at O...O 2.50 to 2.80 Å, a consistency check ([F03](findings/F03-stretch-vs-experiment.md)). Mineral D/H fractionation gives ordering only ([F05](findings/F05-fractionation-test.md)); boehmite against diaspore is inconclusive ([F12](findings/F12-boehmite-diaspore.md)). The direct test is D/H partitioning between coexisting polymorphs, equal to the isotope shift up to a coupling term R ([M02](math/M02-bigeleisen-bridge.md)). Matched AlOOH/AlOOD bracketing runs test the predicted +1.13 to +1.33 GPa shift at 300 K, an exploratory sign prediction ([card](findings/CARD-AlOOH.md)).

**Why does mp-985293 fail?**
Its stretch term keeps the predicted sign; bend and libration flip the total below a model-dependent crossover (MatterSim mostly below 300 K, ORB 317 to 406 K, MACE 431 to 506 K). The predeclared zero-point weighting test failed, so we claim no mechanism ([F09](findings/F09-temperature-crossover.md)).

**What is new compared with prior art?**
McKenzie et al. (2014, 2015) showed the stretch-bend competition for fractionation; Bourgeois et al. (2018) screened 115 metal hydrides harmonically; Du et al. (2026, arXiv:2610.11325) treat single systems by path integrals. A logged search found no earlier survey of H/D free-energy differences across polymorph pairs ([decision 11](decisions/11-positive-framing.md), [query log](../logs/bond_queries.jsonl)). New here is that polymorph-stability version, its slope and where it fails.
