# GNoME reality check: feasibility report (2026-10-20)

## 1. Data
- Repo: https://github.com/google-deepmind/materials_discovery (DATASET.md). Bucket gs://gdm_materials_discovery, public over HTTPS: https://storage.googleapis.com/gdm_materials_discovery/gnome_data/<file>
- Files (bytes): stable_materials_summary.csv 151,452,777 (downloaded to data/gnome/); stable_materials_r2scan.csv 22 MB; by_id.zip 455 MB, by_composition.zip 468 MB, by_reduced_formula.zip 472 MB (CIF structures, not downloaded); external_data/mp_snapshot_summary.csv 3.1 MB; external_data/external_materials_summary.csv 5.8 MB.
- Summary columns: Composition, MaterialId, Reduced Formula, Elements, NSites, Volume, Density, Point Group, Space Group, Space Group Number, Crystal System, Uncorrected/Corrected Energy, Formation Energy Per Atom, Decomposition Energy Per Atom (+ All, Relative, MP, MP OQMD), Dimensionality Cheon, Bandgap, Is Train, Data Directory. No CIF inside the CSV (structures via by_id.zip). No ICSD or "experimentally observed" flag. No Materials Project ID. "Decomposition Energy Per Atom MP" is E_hull vs a June 2024 MP snapshot (CSV was updated to minimize overlap with MP/OQMD).
- Rows: 554,054 (more than the 381k headline). Decomp Energy All <= 0: 369,029. Decomp vs MP < 0: 544,445.
- By number of elements (parsed from Reduced Formula): binary 1,741; ternary 63,441; quaternary 306,688; quinary 177,392; senary 4,792. Dominated by quaternary/quinary, mostly lanthanide/mixed-site substitution variants (e.g. Pr2Nd2DyUSe10, Nd3HoCu3Bi8).
- Formula gotcha: Reduced Formula is NOT in conventional order (MnFeCo4Si2 is stored as "MnFe(Co2Si)2"). Script: summarize.py.
- Examples: 000006a8c4 Cs(ZrS2)3 C2/m, 10 sites, E_hull_MP -0.163; 003096c96c Dy24Tc7Mo Pm; 005dde30f8 Sm3Si2B4Rh9 P6/mmm; 0089d64481 Pr2Nd2DyUSe10 P2_1; 00b856bae7 Eu3Ho(NiP)4 P-6m2.

## 2. Prior work
- Nature paper itself: 736 GNoME structures later matched ICSD (snapshot March 2021) https://www.nature.com/articles/s41586-023-06735-9
- Cheetham & Seshadri, Chem. Mater. 2024, 36, 3490, doi 10.1021/acs.chemmater.4c00643 (critique: many are not useful/credible, disorder, lanthanide variants). Full text not read.
- A-Lab (Szymanski 2023, 41 of 58 targets, many from GNoME/MP) critiqued by Leeman...Palgrave, PRX Energy 2024 (https://par.nsf.gov/servlets/purl/10532478); Chemistry World coverage: https://chemistryworld.com/news/new-analysis-raises-doubts-over-autonomous-labs-materials-discoveries/4018791.article
- arXiv 2505.09161 (synthesizability filter on the 554,054 candidates, 92,310 pass); a search snippet says 17 GNoME structures were recently synthesized, but I could not verify that in the abstract.
- arXiv 2603.22748: first-principles-to-experiment on MnFeCo4Si2 (a GNoME compound). Energy-GNoME arXiv 2411.10125 (application screening, not validation).
- I found no systematic 2024 to 2026 count of GNoME compounds experimentally reported. The exact question looks open (web search only, not exhaustive).

## 3. Literature recall test (OpenAlex, no key, no mailto; recall_test scripts oa.py, oa2.py, oa3.py)
- 12 random GNoME compounds (6 ternary, 6 quaternary), exact quoted formula, title+abstract, 2024-2026: 0 hits each (also 0 for fulltext on 4). Expected: they are novel.
- Only 1 of 28 well-known compounds I tried exists in GNoME (canonical-formula match): MnFeCo4Si2. Searching GNoME's string "MnFe(Co2Si)2" gives 0 hits; the conventional string "MnFeCo4Si2" finds the 2026 experimental paper. So formula normalization is the critical step, and one query per variant is needed.
- Controls: LiFePO4 2946, BaTiO3 3081, CsPbI3 703 hits in 2024-2026 (title/abstract): for common compounds counts are noisy, genuine synthesis reports would need LLM classification.
- API: ~0.5 to 1 s per call, 12 calls plus 4 fulltext in about 10 s, no throttling. Public pool is roughly 100k calls/day, 10 req/s without a key.
- Estimate: 3 to 6 query variants per compound -> 369k compounds = 1 to 2M calls, not feasible. A 500 to 2000 compound subset = 5 to 10k calls, about 1.5 h. Per-compound with LLM triage of hits: 5 to 30 s.
- Caveat: abstracts rarely contain formulas of novel quaternaries; reported syntheses often hide in full text or SI (OpenAlex fulltext index is partial).

## 4. Verdict: RISKY (feasible only if heavily scoped)
Risks: (a) matching noise from formula variants and polymorphs/disorder (GNoME lists ordered cells of disordered/lanthanide-mixed phases); (b) no ICSD flag, so "known before" must be inferred (MP snapshot, ICSD unavailable); (c) true positives are probably very rare (tens), so the headline is a small-number result with big uncertainty; (d) structure matching needs CIFs (455 MB) and experimental structure data is mostly paywalled.
Scope: ternaries (63k) with E_hull_MP < 0, Is Train False, no lanthanide solid solutions, rank by simplicity, sample a few thousand; or a stratified random sample of ~1000 with a measured recall of the pipeline on the 736 ICSD-matched known compounds as ground truth.
Most defensible headline: "Of N randomly sampled GNoME ternaries not in MP at prediction time, X% have any 2024-2026 experimental report, with precision/recall of the agent validated on known cases (e.g. MnFeCo4Si2 found, others)." Report a lower bound and the recall measured on positives, not an absolute count.
