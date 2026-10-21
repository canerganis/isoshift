# Topic decision (Claude, 2026-10-21 ~01:00, delegated by Can)

**Approved by Can on 2026-10-21 morning: go with IsoShift.**

## Chosen: IsoShift — where does heavy water move phase boundaries?

**Headline:** A systematic map of where H/D substitution shifts polymorph free energies in inorganic hydrogen compounds, validated against measured isotope effects, with the limits of harmonic physics stated by mechanism (see PLAN.md P10 to P25).

**Core idea.** Born-Oppenheimer force constants do not depend on nuclear mass, so one set of phonon calculations per structure gives the vibrational free energy for both H and D by re-diagonalizing the dynamical matrix with new masses. For hydrogen-containing polymorph pairs we compute quasi-harmonic free energies for H and D and report the **isotope shift of transition temperature/pressure**, ΔT_iso ≈ ΔΔF_iso / ΔS near a crossing. This shift is largely insensitive to the absolute polymorph energy error that would kill a naive "ground state flips" claim.

**Pipeline.**
1. Agent assembles hydrogen-containing polymorph pairs (hydrides, borohydrides, alanates, ordered hydroxides/oxyhydroxides, ammonium salts) from Materials Project / JARVIS / Alexandria, filters disordered and proton-transfer systems.
2. Phonons and QHA with three universal MLIPs (MACE, ORB, SevenNet) via phonopy on the RTX 4060. Ensemble spread = uncertainty. Only candidates where all three agree on the sign and the shift exceeds the spread are ranked.
3. Spot-check MLIP H phonons against DFT phonon databases (PhononDB/MDR) for H-containing compounds.
4. LLM agent (Opus/Codex/Gemini via harness, Valency MCP Bond for literature) builds the validation set of known isotope effects and checks candidate novelty. Harmonic-tractable known cases = positive validation; KDP-type tunneling/order-disorder cases = declared negative controls.
5. Deliverables: open tool (CIF in → H/D free-energy crossing map, marimo app), ranked ~10 isotope-tunable candidates with error bars, H-phonon MLIP benchmark.

**Fallback inside the same pipeline:** H-phonon benchmark of universal MLIPs vs DFT + isotope ZPE/free-energy atlas for every screened compound (still a validated, reusable tool).

**Hard gates.** Gate at Thu 00:00 with three outcomes (PLAN.md P10, P12). Never headline "ground-state flips".

## Why this over the alternatives
- Round 5 red team (docs/brainstorm/r5-*): Opus ranked it 1st (~25% for 1st place, vs 18% for PackEvolve); Codex and Gemini preferred PackEvolve for verifiability but gave both low odds (Codex 2 to 7%).
- Judges are materials/chemistry people: relevance and impact favour IsoShift; PackEvolve was called "a math result in a materials costume" and its record probability is uncertain (1 to 30% across judges), with a weak fallback.
- Web check: no systematic inorganic isotope-polymorph screen found; molecular isotopomeric polymorphism is documented (ORNL 4-MPPCP), which gives a strong narrative bridge.
- Rejected: GNoME reality check (risky, tens of positives, noisy matching), DataDoctor (risky, quiet), Na conductors (derivative), agent benchmark (MADE, ICML 2026), EigenDrop (VibroML).

## Update after validation research (docs/research/, ~01:30)
- Clean, quantitative, harmonic-tractable experimental H/D transition shifts are rare. Gate is rebuilt on: ice Ih volume isotope effect sign (QHA reproduces it, Pamuk PRL 2012), brucite Mg(OH)2 volume isotope effect (V_H ~0.31% > V_D), LiH/LiD ZPE sanity, ice Ih→XI shift (+4 K exp; functional-sensitive, stretch goal).
- Negative controls: KDP/DKDP, KOH/KOD (+24 K order-disorder), δ-AlOOH/AlOOD (+4.4 GPa), NH4Cl/ND4Cl.
- Closest prior art to cite: Bourgeois et al. 2018 (115 metal hydrides, harmonic H/D/T formation-pressure shifts). Safe novelty claim: first MLIP-based, cross-family map of isotope shifts of polymorph transitions and of harmonic-validity limits. Do not claim "first isotope phonon calculation".
- No benchmark isolates X–H stretch accuracy of universal MLIPs: that benchmark is itself a deliverable and the fallback.
- MLIPs: ORB v3 conservative, SevenNet-MF-ompa, MatterSim v1, MACE as baseline; avoid direct-force models.
- Residual risk acknowledged: validation is thin; the story must lean on ensemble uncertainty, honest negative controls and the benchmark.

## Kept as plan B: PackEvolve (AlphaEvolve-style denser binary sphere packings), see r5 sharpened versions.
