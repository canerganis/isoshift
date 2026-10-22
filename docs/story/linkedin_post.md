LinkedIn post (Can posts it himself; paste the video link where marked)

---

Swap hydrogen for deuterium in a hydrogen-bonded crystal. Which crystal form does the deuterated material prefer?

For OSI Hackathon 2026 I built IsoShift to answer that for 63 carbon-free hydrogen compounds. One phonon calculation per crystal gives both the H and the D free energy, so the static energy gap between polymorphs, where ML potentials err most, drops out of the isotope difference; errors in the vibrations remain.

What came out, across 220 polymorph pairs and three universal ML potentials (MACE, ORB, MatterSim):

Where hydrogen bonds are moderate or strong, deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 model evaluations. A constant guess gets 131.
The effect scales with O-H bond length, 0.11 to 0.13 meV per hydrogen per thousandth of an angstrom. The O-H stretch drives it, and bending and libration cancel about half.
With weak hydrogen bonds the rule fails, 2 of 20. Among the strong-bond pairs, 74 are right by model majority and 10 are wrong, and all 10 contain one Al(OH)3 structure; our predeclared explanation for them failed.
Why it matters: neutron groups use deuterated delta-AlOOD as a stand-in for a possible deep-Earth water carrier, and deuteration moves a measured transition in it from 9.0 to 13.4 GPa (Sano-Furukawa et al. 2018). For the diaspore to delta-AlOOH transition our exploratory model prediction is about 1 GPa higher for AlOOD (1.13 GPa ORB, 1.33 GPa MACE). Matched AlOOH and AlOOD runs can check the sign.

How it was done matters as much as what came out. An AI team did the work under my direction: literature agents on Valency Bond (182 logged queries), three-model councils for the hard calls, and prediction files committed to git before their data (one scoring rule, P04, was committed with its result). Some of those predictions failed, including a prospective test on new pairs, and the repo reports them with the same weight as the successes. This is a computational result; nobody has measured a polymorph isotope free energy yet, and the repo names the experiment that would.

Video: [VIDEO LINK]
Code, data, interactive marimo app and every decision: https://github.com/canerganis/isoshift

#materialsscience #machinelearning #isotopes #crystallography #OSIHackathon
