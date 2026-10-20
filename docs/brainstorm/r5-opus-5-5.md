# Senior judge verdict

## 1. Finalist-by-finalist

**F1 IsoSwitch**
- **Is the science sound?** Yes. In the Born–Oppenheimer picture, changing the isotope only changes the masses, not the force constants. Treating vibrations as harmonic oscillators (the harmonic approximation) is standard.
- **First attack:** "Your effect is ~1 meV/atom and your energy error is ~10 meV/atom, so your 'flips' are noise." Second attack: "The famous isotope effects are tunneling and order-disorder physics. A harmonic model can't see them."
- **Positive headline in 34 h:** 70% for a candidate list. About 30% that it survives scrutiny.
- **P(1st place):** about 25%, after sharpening (see section 4).

**F2 PackEvolve**
- **Is the math sound?** Yes, and density is exactly checkable. That's its big strength.
- **First attack:** "Did the LLM beat plain random search or floppy-box Monte Carlo at the same compute?" Second attack: "Larger-cell searches after 2012 exist." I believe the Smallenburg/Filion/Foffi groups ran floppy-box searches with larger cells around 2023–24. I'd distrust your web check that no record has fallen since 2012.
- **Positive headline:** about 25% for a real binary record.
- **P(1st place):** about 18%.

**F3 GNoME reality check**
- **Is the question sound?** Yes, but the measurement isn't. With tens of true positives, unknown recall and formula-matching headaches, the confidence interval swallows the headline.
- **Already done:** Cheetham & Seshadri (2024) published a critique of GNoME. A-Lab was critiqued too (Leeman et al. 2024). So yours is a follow-up, not a first.
- **Positive headline:** 35%.
- **P(1st place):** about 8%.

**F4 Fast Na-ion conductors**
- **Is the science sound?** Yes, but it's derivative. Many universal-MLIP conductor screens exist.
- **First attack:** high-temperature Arrhenius extrapolation, MLIP softening that overestimates diffusion, and no experimental validation.
- **Positive headline:** 60%.
- **P(1st place):** about 8%. Nobody will call it new.

**F5 DataDoctor**
- **Is it sound?** Yes, and it's useful, but quiet.
- **P(1st place):** about 5%.

## 2. F1 deep dive

**How big is the effect?** Per O–H hydrogen:
- Zero-point energy (ZPE) is roughly 0.3 eV: the stretch (~3600 cm⁻¹) gives ~0.22 eV and the librations/bends add the rest.
- Deuteration removes about 1 − 1/√2 ≈ 29% of that, roughly 90 meV per H.
- What matters is the **difference between polymorphs**. With similar hydrogen bonding, their H-ZPEs differ by about 1–5%. The isotope shift is then about 0.3–1.5 meV per H, or about 0.1–0.6 meV/atom once diluted over all atoms.
- The exception is when the polymorphs have very different hydrogen-bond strengths. A 500 cm⁻¹ red-shift of the stretch gives about 9 meV per H.

So flips are only realistic for nearly degenerate pairs, gaps below about 1–2 meV/atom. That is below what universal MLIPs, and even PBE, can resolve. **Don't headline "flips."**

**Is a universal MLIP accurate enough for H phonons?**
- Known weaknesses: systematic softening (Deng et al. 2024) and frequency errors of tens of cm⁻¹ on general phonon benchmarks (Loew et al. 2024). Errors on hydrogen stretches are likely worse, around 50–150 cm⁻¹.
- PBE's own hydrogen-bond errors are baked into the training data.
- The isotope *shift* benefits partly from error cancellation. But you must prove that, not assert it.

**Known inorganic examples:**
- KDP → DKDP: the ferroelectric transition jumps from about 123 K to 229 K. This is tunneling/order-disorder, so **out of scope for a harmonic model**.
- Ammonium halides and NH₄H₂PO₄ (ADP) phase differences on deuteration.
- Ice: the VII/VIII → X hydrogen-symmetrization pressure shifts with D, and the ice Ih/XI ordering temperature differs slightly.
- The Ubbelohde geometric isotope effect: hydrogen bonds lengthen on deuteration.
- Pd–H/D (anharmonic).
- Pyridine-d5 gives a new phase (Crawford 2009), but that is molecular.

**The validation that would actually work:** the anomalous isotope volume effect in ice (D₂O ice has a larger volume). Pamuk et al. (PRL 2012) captured it with the quasi-harmonic approximation (QHA). If your pipeline reproduces that sign and magnitude, judges will listen. Use KDP-type cases as **declared negative controls**: "here the harmonic model correctly says it can't explain this."

## 3. F2 deep dive

**Chance to beat a record:**
- Beating a tabulated binary density at some point in size ratio α and composition x, using cells larger than 12 spheres, is about 25–30%.
- Beating it at a "famous" point (α ≈ 0.4–0.6, the AlB₂/NaZn₁₃-like region) is under 10%. That region is heavily mined.
- Ternary "records" are hollow when nothing is tabulated. Any number wins, and judges know it.

**Credibility:** high if verified exactly *and* compared against a random-search baseline. Without that baseline, the LLM is decoration.

**Relevance to materials judges:** moderate. The densest packing is the infinite-pressure limit. Real colloidal and nanoparticle superlattices are governed by entropy, softness and ligands. Chemists will call it a math result in a materials costume.

## 4. Ranking for 1st place

**F1 > F2 > F3 ≈ F4 > F5**

F1 wins on relevance, novelty ("a new control knob for polymorphism") and noise. F2 is the more *verifiable* result but less materials-relevant, and it risks a "someone already did larger cells" moment.

**Sharpened F1:** Don't claim ground-state flips. Claim **isotope shifts of polymorph transition temperatures and pressures**:
- Use the quasi-harmonic free energy for each polymorph pair.
- Near a crossing, ΔT_iso ≈ ΔΔF_iso / ΔS. This shift is largely insensitive to the absolute energy-gap error that kills the flip framing.
- Run the H/D comparison with three universal MLIPs (MACE, ORB, SevenNet). Report the ensemble spread as uncertainty, and only rank candidates where all three agree on the sign and the shift exceeds the spread.
- Spot-check against PhononDB/MDR phonons for H-containing compounds.
- Validate on the ice isotope-volume anomaly, and on any harmonic-tractable known T/P shifts. Show KDP as a negative control.
- Deliverable: an open tool (CIF in → H/D/T free-energy crossing map) plus a ranked list of about 10 "isotope-tunable polymorph" candidates with error bars.
- Headline: *"First systematic map of where deuteration moves phase boundaries in inorganic hydrogen compounds, and where harmonic physics provably can't."*

**Fallback in the same pipeline:** if no candidate survives the ensemble filter, pivot to the **H-phonon benchmark plus an isotope atlas**. That means:
1. Quantify how badly universal MLIPs reproduce hydrogen modes versus DFT.
2. Show whether the isotope shift cancels those errors.
3. Publish ZPE/free-energy isotope shifts for every screened compound.

That's still a working, validated tool, which is what won in 2025. You'd present it as the benchmark the field needs before anyone trusts MLIP nuclear-quantum-effect screening.

**Hard rule for F1:** set the time box for the ice QHA validation to hour 10 at the latest. If the sign comes out wrong, go straight to the fallback.
