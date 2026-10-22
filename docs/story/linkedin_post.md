LinkedIn post (Can approves before it is posted; video: isoshift_final_v13_subs.mp4, captions burned in; tags are added in LinkedIn with @)

---

Does replacing hydrogen with deuterium change which crystal structure of a compound is stable?

At the OSI Hackathon 2026 I worked on this question with a team of AI agents under my direction. We computed harmonic H and D free energies for 220 polymorph pairs of carbon-free hydrogen compounds with three universal ML potentials (MACE, ORB, MatterSim).

What we found at this hackathon is a simple sign rule, the short-bond rule: in crystals with moderate-to-strong hydrogen bonds, deuteration favours the polymorph with the shorter O-H bonds. It holds in 185 of 212 model evaluations, against 131 for a constant-sign baseline. Behind it is a correlation we did not find in earlier work: the isotope free-energy difference between two polymorphs changes by 0.11 to 0.13 meV per H for each mÅ change in mean O-H bond length. The rule fails for weak hydrogen bonds, and we report where.

It also makes a prediction that can be checked: deuteration should raise the diaspore to δ-AlOOH transition pressure by about 1 GPa (1.13 GPa with ORB, 1.33 GPa with MACE). D/H partitioning between coexisting polymorphs would test the rule directly.

How the work was done: Claude Opus 5.5 ran the screen and the analysis, Claude Sonnet agents searched the literature on Valency Bond (182 logged queries), every formula was derived twice by GPT-6 Astra and Claude Opus, and hard calls went to a council of Claude Opus, GPT-6 Astra and Gemini 4 Argon that recorded its dissent. Predictions were committed to git before the data, and the failed blind tests are reported next to the ones that passed. The results are in an open marimo app that runs without a GPU.

Thanks to Ben Blaiszik and the organizing team for running the hackathon.

Video: https://youtu.be/X8ckZ7dV40Y
Code, data, marimo app and decision records: https://github.com/canerganis/isoshift

#materialsscience #machinelearning #isotopes #crystallography #AIforScience #OSIHackathon
