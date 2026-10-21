# 03. Headline candidates come only from pairs of two experimentally known, ordered phases

Decision (Opus, 21 Oct ~20:00, from the candidate literature sweep `state/sweeps/candidate-lit.jsonl`; P16).

Evidence: the Bond/OpenAlex check of the 11 interim candidate families returned no headline candidate. 7 involve a hypothetical phase (JARVIS structures without an experimental match: the R3m FeOOH and AlOOH partners, BaH, LaHO, ZrH, Ti2H, cubic AlH3), 3 are dominated by H disorder or order-disorder (GaOOH Fdd2 partner unidentified, Ba(OH)2.H2O, NH4Br). The large |ddF_iso| values sit mostly on hypothetical structures, which is expected: unphysical polymorphs often have unusual H environments.

Rules:
1. Headline and candidate cards only for pairs where both members are experimentally observed (`data/isoshift/experimental.csv`) and literature does not report H disorder dominating either phase.
2. Hypothetical pairs stay in `results/candidates*.csv` with a `hypothetical` label and are shown in the candidate map as background, never named in the write-up as predictions.
3. The real-phase pairs most relevant are AlH3 (alpha, alpha', beta, gamma), MnOOH (manganite, groutite), CrOOH, InOOH, GaOOH (alpha vs Pmn2_1), Ca(BH4)2, NaBH4, LiAlH4, Zn(OH)2, Al(OH)3 (gibbsite, bayerite, nordstrandite, doyleite), MgH2 alpha/gamma. Most are tier 32 and still in the queue; they get all four models.
4. If no real-phase pair clears P14, the deliverable is P10(c): a map of where isotope tuning is and is not resolvable with today's universal MLIPs, with the validated volume isotope effects and the benchmark.
