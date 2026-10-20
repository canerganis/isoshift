# Final red-team: pick the topic that wins 1st place

You are a harsh senior judge (computational materials scientist + ML). No tools, no file edits. English, under 900 words.

Event: Open Scientific Intelligence Hackathon 2026 (MDRI). Criteria: impact, innovativeness, scalability, relevance to materials science/chemistry. Organizer: "is two days to a real discovery possible?". Solo, 34 h, RTX 4060 8 GB laptop, subscription CLIs to Opus 5.5 / GPT-6 Astra / Gemini 4 Argon (10 to 60 s per call), no wet lab. Goal: FIRST place and maximum noise, but the result must survive expert scrutiny. 2025 winners were validated working tools.

## Finalists

F1. IsoSwitch (H/D isotope polymorph switching). Born-Oppenheimer force constants are mass independent, so phonons of a structure can be recomputed for any isotope by re-diagonalizing the dynamical matrix with new masses. Screen hydrogen-containing inorganic polymorph pairs (hydroxides, hydrides, hydrates, ammonium/borohydride salts) from Materials Project / Alexandria, compute harmonic (and if time, quasi-harmonic) ZPE and free energy with a universal MLIP (MACE/ORB) for H and D, and find pairs where deuteration shifts relative stability by more than the polymorph energy gap, i.e. candidates for isotope-controlled polymorph selection. Validation: reproduce known isotope-dependent phase behaviour (literature set gathered by an agent: e.g. deuteration-induced phase differences in KDP-type, ammonium salts, ice-like systems); MLIP vs DFT phonon check on a subset (PhononDB). Concern: DFT/MLIP polymorph energy errors (~5 to 20 meV/atom) can exceed the baseline gap; the isotope SHIFT itself is more robust than the absolute ordering. Web check: no systematic inorganic screen found; molecular isotopomeric polymorphism is documented.

F2. PackEvolve (AlphaEvolve-style search for denser binary sphere packings). LLMs evolve Python generator programs that propose periodic binary sphere packings (size ratio alpha, composition); a deterministic optimizer (overlap-penalty + cell compression) polishes, an exact checker verifies non-overlap and density. Target: match then beat the best-known densities in the Hopkins-Stillinger-Torquato 2012 binary phase diagram (exhaustive up to ~12 spheres per cell), especially at larger cells or unexplored alpha/composition regions; extend to ternary packings where almost nothing is tabulated. Relevance: binary nanoparticle superlattices, colloids, intermetallic/ionic structure types (AlB2, NaZn13). Web check: no new binary packing record since 2012 found; AlphaEvolve (Tao et al. 2025) did 67 math problems incl. some packings but no binary sphere packings found in summaries.

F3. GNoME reality check: fraction of GNoME predicted stable ternaries (not in MP at prediction) experimentally reported 2024 to 2026, via OpenAlex/Bond literature search + LLM classification, with recall measured on known positives. Feasibility check: risky, true positives likely tens, formula normalization hard, abstracts rarely mention novel quaternaries.

F4. Fast sodium-ion conductors: MLIP molecular dynamics on ~2000 stable Na compounds, calibrated on known conductors (NASICON, Na3PS4, Na3SbS4), two potentials must agree, literature check that top 5 to 10 are untested. Similar Li screens exist.

F5. DataDoctor (safe fallback): agent audits matbench/matminer experimental datasets (expt_gap has no per-entry references), corrections ledger, benchmark impact.

## Task
1. For each finalist: is the core scientific claim physically/mathematically sound? What would an expert judge attack first? Probability it yields a positive headline result in 34 h. Probability of 1st place given the field.
2. For F1 specifically: is H/D ZPE large enough to flip realistic inorganic polymorph pairs, and is a universal MLIP accurate enough for H phonons? Known inorganic examples?
3. For F2 specifically: realistic chance to beat any 2012 record; is the "AI found denser packings" headline credible and relevant enough to materials judges?
4. Rank F1 to F5 for 1st place. Give a one-paragraph sharpened version of your winner and a fallback inside the same pipeline.
