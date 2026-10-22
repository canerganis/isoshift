LinkedIn post (Can approves before it is posted; video: isoshift_final_v6_subs.mp4, captions burned in)

---

Does replacing hydrogen with deuterium change which crystal structure of a compound is stable?

At OSI Hackathon 2026 I worked on this question with a team of AI agents under my direction. We computed harmonic H and D free energies for 220 polymorph pairs of 63 carbon-free hydrogen compounds with three universal ML potentials (MACE, ORB, MatterSim).

The result is a sign rule, which we call the short-bond rule: in crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds. It holds in 185 of 212 model evaluations, against 131 for a constant-sign baseline. It fails for weak hydrogen bonds (2 of 20), and the 10 pairs the models get wrong all contain one Al(OH)3 structure.

The O-H stretch and the bending and libration modes contribute with opposite signs, and in the strong-bond regime the stretch dominates, with about half of it cancelled. Because polymorph energy gaps are smaller than the errors of the potentials, we computed only the isotope difference: one phonon calculation per structure gives both isotopes, and the static energy gap cancels.

For the diaspore to δ-AlOOH transition the models predict a transition pressure about 1 GPa higher for AlOOD (1.13 GPa with ORB, 1.33 GPa with MACE). This is an exploratory sign prediction. The rule itself has not been tested experimentally; D/H partitioning between coexisting polymorphs would test it.

Literature searches ran on Valency Bond (182 logged queries), predictions were committed to git before the data, and the failed blind tests are reported in the repository.

Video: https://youtu.be/3gE5nxhLo80
Code, data, marimo app and decision records: https://github.com/canerganis/isoshift

#materialsscience #machinelearning #isotopes #crystallography #OSIHackathon
