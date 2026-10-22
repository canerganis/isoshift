LinkedIn post (Can posts it himself; paste the video link where marked)

---

Swap hydrogen for deuterium in a hydrogen-bonded crystal. Which crystal form does the deuterated material prefer?

For OSI Hackathon 2026 I built IsoShift to answer that across hundreds of real compounds. One phonon calculation per crystal gives both the H and the D free energy, so the large errors that ML potentials make on polymorph energies cancel out and only the isotope effect is left.

What came out, across 220 polymorph pairs and three universal ML potentials (MACE, ORB, MatterSim):

Where hydrogen bonds are moderate or strong, deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 model evaluations. A constant guess gets 131.
The effect scales with O-H bond length, 0.11 to 0.13 meV per hydrogen per thousandth of an angstrom. The O-H stretch drives it, and bending and libration cancel about half.
With weak hydrogen bonds the rule fails, 2 of 20. All 10 wrong pairs contain one Al(OH)3 structure, and we show why.
A concrete prediction for experimentalists: deuteration should raise the diaspore to delta-AlOOH transition pressure by about 1 GPa. Matched AlOOH and AlOOD runs can check it.

How it was done matters as much as what came out. An AI team did the work under my direction: literature agents on Valency Bond (182 logged queries), councils of three frontier models for every claim, and every prediction committed to git before the data were read. Some of those predictions failed, including a prospective test on new pairs, and the repo reports them with the same weight as the successes. This is a computational result; nobody has measured a polymorph isotope free energy yet, and the repo names the experiment that would.

Video: [VIDEO LINK]
Code, data, interactive marimo app and every decision: https://github.com/canerganis/isoshift

#materialsscience #machinelearning #isotopes #crystallography #OSIHackathon
