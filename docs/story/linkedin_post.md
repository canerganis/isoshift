LinkedIn post (Can approves before it is posted; video: isoshift_final_v6_subs.mp4, captions burned in)

---

The short-bond rule: swap hydrogen for deuterium in a crystal with moderate-to-strong hydrogen bonds, and it favours the polymorph with the shorter O-H bonds.

At OSI Hackathon 2026, with an AI team working under my direction, I derived this rule from a screen of 220 polymorph pairs of 63 carbon-free hydrogen compounds, using three universal ML potentials (MACE, ORB, MatterSim). It holds in 185 of 212 model evaluations, against 131 for a constant guess. With weak hydrogen bonds it fails (2 of 20), and a single Al(OH)3 structure is the one counterexample.

Why it is not obvious: deuterium pulls two ways. The O-H stretch favours one crystal, bending and libration favour the other, and they cancel about half of each other. Which one wins depends on the hydrogen bond, and for polymorph stability this had not been mapped across a large screen.

The trick that made it possible: polymorph energy gaps are smaller than any ML potential's error, so I computed only the isotope difference. One phonon run per crystal gives both the H and the D free energy, and the static energy gap drops out.

A prediction a lab can check: deuterium raises the diaspore to δ-AlOOH transition, a possible deep-Earth water carrier, by about 1 GPa (1.13 GPa ORB, 1.33 GPa MACE, exploratory sign). D/H partitioning between coexisting polymorphs would test the rule directly. Nobody has measured it yet.

How it was done: literature agents on Valency Bond logged 182 queries, three-model councils argued every claim, and predictions went into git before the data. Some of them failed, and the repo reports those with the same weight as the successes.

Video: https://youtu.be/3gE5nxhLo80
Code, data, interactive marimo app and every decision: https://github.com/canerganis/isoshift

#materialsscience #machinelearning #isotopes #crystallography #OSIHackathon
