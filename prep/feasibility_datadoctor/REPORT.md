# DataDoctor feasibility report (2026-10-20)

Scripts: load.py, sig.py, oa.py in this folder. Data in data/datadoctor (gitignored).

## 1. Datasets and references (critical finding)
| dataset | rows | per-entry source refs? |
|---|---|---|
| expt_gap (Zhuo 2018) | 6354 (formula, gap) | NO |
| matbench_expt_gap | 4604 (unique comps, deduped) | NO |
| expt_gap_kingsbury | 4604 (+likely_mpid for 2481, 2480 unique) | NO |
| expt_formation_enthalpy | 1276 (has mpid, oqmdid, e_form mp, e_form oqmd) | NO (dataset-level DOI only) |
| expt_formation_enthalpy_kingsbury | 2135 (+uncertainty, phaseinfo, likely_mpid) | YES, free text, 213 unique |
| ucsb_thermoelectrics | 1093 | YES, DOI URL per row (src) |
| citrine_thermal_conductivity | 872 | no (conditions only) |
| glass_binary 5959, glass_ternary_landolt 7191, steel_strength 312, heusler_magnetic 1153 | | no / dataset-level |

Kingsbury enthalpy refs: 1135 rows cite Kim et al. 2017 Sci Data (a curated compilation, DOI 10.1038/sdata.2017.162), 765 cite Kubaschewski handbook (book), rest are a few primary papers / JANAF URLs. So references exist but point to compilations, not primary papers. For expt_gap there is no reference at all.

## 2. Quick signals
expt_gap: 4934 raw formulas (4921 reduced); 462 reduced compositions have multiple entries (1895 rows). Spread >0.1 eV: 317, >0.5: 45, >1: 4. Worst: AlP 1.21 (11 entries, 2.42 to 3.63), TaGaS2 1.20, As2S3 1.11 (24 entries), SrTiO3 1.10 (3.0 to 4.1), HgCl 0.96, NaI 0.95, AlSb 0.90, ZnSnP2 0.80, TlBr 0.77, KI 0.77. Many are real condition/polymorph/amorphous differences (As2S3 glass vs crystal, AlP direct vs indirect gap), not errors. Matbench already dedups (keeps the value nearest the mean, drops spread >0.1 per forum report), so the benchmark itself has no duplicate conflicts. The 6354 to 4604 gap is the dedup.

Enthalpy (expt_formation_enthalpy, 643 rows with MP value): |MP - expt| >0.2 eV/atom in 45, >0.1 in 153. OQMD: 69 >0.2 of 685. Examples: TiCoSn expt -0.44 vs MP +0.31 (OQMD -0.38, so MP structure or polymorph problem), HfSnPt -1.02 vs MP -0.28 (OQMD -1.02), MnSnIr, TaPt3, TaRh3 (both DFT agree -0.6, expt -0.15, a likely true expt/identity issue), LuB2. Cases where MP and OQMD disagree with each other vs both disagree with expt give a natural classifier signal. The Kingsbury set has likely_mpid but no DFT values; MP key unavailable, so need the older set's columns or OQMD (public).

## 3. Prior work
- Yang et al. 2023, LLM extraction of experimental band gaps ([arXiv 2311.13778](https://arxiv.org/abs/2311.13778)): built a new database from papers, found only ~52% of overlapping compositions agree within 0.1 eV with the Zhuo set, MAE improved 19%. Compares datasets, but does not release a per-entry corrections ledger for Zhuo/Matbench.
- Known issues documented informally: [matsci.org thread](https://matsci.org/t/references-for-expt-gap-dataset/3516) (no refs, dedup discards data), metals' zero gaps taken from MP, about 17% of nonmetals labelled metal in MP, 53% of benchmark is metals.
- [AGAPI-Agents](https://arxiv.org/pdf/2512.11935): notes residual error is database vs experiment. Not an audit.
- I found no 2025-26 paper that audits matbench_expt_gap or Kingsbury enthalpy with an agent, traces sources and measures benchmark effect. Not exhaustively searched (two web queries); cleanlab-in-materials and Dong & Cole not verified.
- Open: per-entry source tracing, flag classification, corrected benchmark with measured leaderboard effect.

## 4. OpenAlex source tracing (5 conflicts, no email sent)
Search "formula band gap", top 10 abstracts: AlP 3/10 abstracts with formula and eV number, As2S3 3/10, SrTiO3 4/10, ZnSnP2 3/10, TaGaS2 0 results (formula not indexed as written). So 30 to 40% of hits are even plausible, only abstracts (via inverted index) are available, values usually inside full text, and heterostructure/doped/theory papers dominate. Matching a specific dataset value to a specific paper is not achievable from OpenAlex alone. Useful for candidate retrieval; needs full-text access (OA PDFs, Semantic Scholar, Valency MCP Bond) and an LLM reader.

## 5. Verdict: RISKY (go only with a reduced scope)
Anchor dataset: expt_formation_enthalpy (Kim/Meredig set with MP + OQMD columns) joined to Kingsbury set (refs, uncertainty). It has independent DFT signals, small size (about 1300 to 2100), refs to the Kim 2017 compilation (open, Sci Data) and the book. Band gap anchor is weaker: no refs, no DFT in file, conflicts largely condition effects, and Matbench already removed them.

Defensible headline: "Of N flagged entries (both DFT sources disagree with expt by >0.2 eV/atom, e.g. 40 or so), we traced K to the compilation, classified them, and corrected M; benchmark MAE of a baseline model changes from X to Y on the corrected set." Keep it small and fully verified, with an honest unresolved class.

Biggest risks: (1) true source papers hard to reach: Kim 2017 is itself a compilation, and handbooks are not machine-readable; (2) many discrepancies are real physics or DFT structure mismatch, not data errors, so "error" claims are hard to defend without a human check; (3) benchmark effect likely small and noisy; (4) no MP key (OQMD and the dataset's own columns cover this); (5) novelty is moderate. Compared to GNoME check it is safer, but less striking.
