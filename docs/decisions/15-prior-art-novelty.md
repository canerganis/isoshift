# 15. Prior art and novelty: keep the edits with wording fixes that narrow every absence statement; no withdrawal of F01

Council: Opus (chair, hostile referee), Astra, Argon. Two rounds, all three answered both. Chair re-checks run on 23 Oct with the project venv against the frozen CSVs. These are post-submission corrections on branch post-hackathon; the submitted snapshot stays untouched.

## Decision

1. **Option chosen: Keep with specific wording fixes.** The fixes are substantive. They narrow the absence statements; they do not withdraw F01. F01 as a quantified result (220 inorganic pairs, all-row slopes 0.112, 0.117, 0.128 meV/H/mÅ, strong-regime O-H slopes 0.132 to 0.147, compensation 0.50 to 0.56, post hoc 0.99 Å boundary, three universal MLIPs) was found published by nobody, within a search that did not read three key full texts.
2. **Four new sentences in the uncommitted diff are wrong and must change before commit.**
   * "we found no comparison between polymorphs of one formula" and "We found no published comparison of polymorph pairs across inorganic O-H...O solids" are refuted by the paper's own tests: F12 uses measured boehmite against diaspore D/H fractionation (Graham 1980) and F07 uses measured D₂O ice boundaries (Bridgman 1935). Pamuk, Allen and Fernández-Serra 2015 also computed the H₂O/D₂O ice XI/Ih shift with DFT plus QHA.
   * The β sentence calls an energy "a difference of reduced partition function ratios". It is kT times a difference of logarithms, per H, and a dilute-D measurement carries the R term of Eq. bridge.
   * "it makes no claim for proton-disorder systems such as KH₂PO₄ and NaOH" contradicts Sec. weak, where NaOH is counted in the 18 of 20, and reads as a new post hoc exclusion.
   * The O...O hedge says O-H and O...O "move together". They are inversely correlated, and "not tested on hydrogen-bonded ferroelectrics, which are outside the screen" contradicts F11, where KH₂PO₄-type pairs entered and were lost to imaginary modes.
3. **Two existing sentences are also wrong given the new citations.** Line 262 and Limitation (6) say no polymorph isotope free energy has been measured; F07 and F12 in the same section use measured related quantities. The abstract's "no cross-compound statement of its direction" conflicts with the intro's "The direction itself is expected".
4. **Schaack 2023 (NaOD) is related context, not agreement.** Argon's claim that the screen's NaOH pairs are Schaack's PE and AFE phases is false (re-check below). The paper may say the D-favoured phase there has the longer O-H, the direction of the weak-side reversal, and must say the phases were not matched.
5. **Not adopted as paper text:** KDP "agrees with the rule in the O-H variable" (argon R1, withdrawn by argon in R2); Vitali 2001 as a polymorph-comparison precedent (abstract calibrates on pure gibbsite, per astra); Novak 1974 with -18 to -22 cm⁻¹/mÅ (value not located in the source); Pamuk2012 as the ice-polymorph cite (that paper is the volume isotope anomaly of ice Ih, not XI/Ih).

## Why

* **The novelty sentence must survive a referee who has read our own Sec. tests.** A paper that scores a measured boehmite-diaspore fractionation (F12) and measured D₂O ice boundaries (F07) cannot also say no polymorph comparison exists. All three members found this independently. The defensible claim is the cross-compound fit, its slope and the location of the sign reversal in O-H length, with single systems named as precedents.
* **β equivalence, checked against Eq. ddF.** ddF = [F_D - F_H]_b - [F_D - F_H]_a, positive means D favours a. With ln β = -[(F_D - F_H) - classical]/(n_H kT) per H, and the classical momentum term identical for both polymorphs (paper line 66), ddF per H = kT(ln β_a - ln β_b). Sign right, units need kT and logs. Eq. bridge is per formula unit and R = 0 only for a full-substitution factor; harmonicity does not remove R for a dilute measurement (astra, and the paper's own line 290). Conversion re-check: 1000/25.852 = 38.68 per mil per meV/H at 300 K; 17.77 at 653 K.
* **KDP.** Deuteration lengthens O...O and raises Tc (stabilises the ordered phase over a wider range). The local O-H in the paraelectric phase is a split-site disorder average close to the ordered value; only the centred static saddle has a longer O-H and it has imaginary modes, so no harmonic ddF exists for it. Claiming sign consistency would be representation-dependent. Ichikawa's anti-tunnelling reading is his interpretation; Koval 2002 couples tunnelling and geometry. Tc(R) is Ichikawa 1987; the O-H against O...O correlation and the GIE are Ichikawa 1978.
* **NaOH re-check (chair, data/isoshift/structures.csv and results/decompose_*.csv).** The four clean weak-side NaOH evaluations are all MACE, over four structures: mp-626000 P2₁ (sg 4, MP theoretical=True, O-H 0.9840 Å), mp-23940 P2₁/m (sg 11, 0.9725), mp-626778 Pbcm (sg 57, 0.9776), mp-23891 Cmcm (sg 63, 0.9733). The D-favoured, longer-O-H structure in three of the four is the theoretical P2₁ entry. The 0.984 against 0.975 Å match with Schaack's Table I is a numerical coincidence, not a phase identification. F10 recorded the same thing ("phases not matched"). Astra was right, argon was wrong.
* **Weak-side sensitivity re-check.** Recomputed from the frozen rows (covalent X-H, clean, |Δ mean O-H| ≥ 5 mÅ, O-only donors, r_max < 0.99 Å per model): 20 evaluations, 2 right, 7 formulas (Al(OH)₃ 0/6, Cd(OH)₂ 0/4, NaOH 0/4, RbOH 0/2, Be(OH)₂ 0/1, Zn(OH)₂ 0/1, FeOOH 2/2), matching main.tex. Without NaOH and RbOH: 14 evaluations, 2 right, 12 reversed, 5 formulas. The reversal does not depend on the alkali hydroxides. Stating this count is a sensitivity check, allowed under decision 05 because it adds no law.
* **O...O correlation re-check.** results/F01_oo.json, structure-level mean O-H against mean O...O: r = -0.826 (MACE), -0.850 (ORB), -0.829 (MatterSim). Inverse, as opus and astra said.
* **Chair's own referee attack, beyond the members.** The one pre-emption that would hurt is a cross-mineral plot of ln β against ν(OH) or d(OH) in Méheut 2010 (or Méheut's 2008 thesis), possibly with a bending compensation remark. Through the β identity above, ln β per H does not care whether two phases share a formula, so such a plot would pre-empt the sign and a slope for minerals against water. What would remain new is the polymorph-stability framing, the fit over 220 same-formula pairs and the located reversal. This is why the novelty sentence names the unread full texts, and why reading them is action 9. The sweep's "not covered" list (Scholar full text, Russian and Chinese mineralogy, forward citations of McKenzie 2015 and Li 2011) remains open and is stated as such.
* **Why not withdraw.** No member, and no chair check, found the cross-compound slope, the compensation fraction or a polymorph-pair reversal boundary in O-H length. Withdrawal would discard a bounded claim that survives once the absence statements are narrowed.

## Where the members converged

* Keep with wording fixes; F01 quantified result not found published (3 of 3, both rounds).
* "No comparison between polymorphs of one formula" and "no published comparison of polymorph pairs" must go (3 of 3).
* β sentence needs kT, logarithms, per-H definition and the R caveat; Eq. bridge needs "per formula unit" (3 of 3).
* O...O hedge: inverse correlation, and "outside the screen" contradicts F11 (3 of 3 after R2).
* Ichikawa attributed as interpretation, Koval 2002 as the coupled view; no KDP O-H sign claim (3 of 3 after R2).
* Line 262 and Limitation (6) need qualifying; abstract absence sentence needs "quantitative test" (3 of 3).
* Full texts of Graham 1980, Méheut 2010, Reynard 2009 unread; the search bound must be stated (3 of 3).
* Deadline passed; these are post-submission corrections on post-hackathon (opus, astra).

## Remaining disagreement

* **Schaack as agreement.** Argon wants it cited as the same reversal in matched phases. Rejected on the structure check above. Opus and astra: related context only. Adopted: direction stated, non-match stated.
* **Strength of the novelty rewrite.** Astra wants the abstract opening replaced and "logged, non-exhaustive search ... post hoc dataset partition" language throughout. Adopted only in part: the abstract already says "(a post hoc boundary)" and "A prospective test on new pairs failed", so the minimal abstract fix plus an explicit search bound in the Discussion is enough.
* **Graham 1980 content.** Argon says it plots fractionation against ν(OH) and O...O and concludes D prefers the weaker-bonded polymorph. Nobody has read it; the paper reads Graham through Chacko 2001. Not used as a claim until action 9.
* **McKenzie 2.8 Å.** Astra: a solvent reference distance, not a polymorph crossover. Argon: the single-bond crossover is real prior art. Both points are kept by citing Li 2011 and McKenzie 2014 for the single-bond sign change without equating any distance with our 0.99 Å.
* **600 K sentence** (pre-existing, astra): "at 600 K and above our rule reduces to it" overstates; ħω/kT for a 3000 cm⁻¹ stretch at 600 K is 7.2. Opus and argon did not take it up. Adopted as optional action 7.

## Ordered action list for the conductor

All edits in docs/paper/main.tex unless stated. Replace exactly; LaTeX as written.

1. **Abstract (line 25).** Owner: conductor. 2 min. Replace "found no cross-compound statement of its direction" with "found no cross-compound quantitative test of its direction across polymorph pairs". Done-check: `grep -c "quantitative test of its direction" docs/paper/main.tex` = 1 and `grep -c "cross-compound statement of its direction"` = 0.

2. **Intro (line 36).** Owner: conductor. 5 min.
   * In "Hydrogen bonding is known qualitatively to control D/H fractionation between OH-bearing minerals and water~\cite{Suzuoki1976,Meheut2010,Reynard2009}" change the cite to `\cite{Suzuoki1976,Graham1980,Meheut2010,Reynard2009}`.
   * Replace the sentence beginning "In hydrogen-bonded ferroelectrics of the KH$_2$PO$_4$ type" with:
     > In hydrogen-bonded ferroelectrics of the KH$_2$PO$_4$ type, H and D crystals of one isostructural family follow a single relation between transition temperature and O$\cdots$O distance, which Ichikawa and co-workers interpreted through the geometric isotope effect rather than proton tunnelling~\cite{Ichikawa1987}; first-principles work couples tunnelling and proton delocalisation to the lattice geometry~\cite{Koval2002}.

   Done-check: `grep -c "is attributed to the geometric isotope effect rather than" docs/paper/main.tex` = 0; Graham1980 appears in the intro paragraph.

3. **Sec. weak (line 194).** Owner: conductor. 5 min. Replace the last sentence "Hydroxides such as NaOH, where a quantum paraelectric transition is driven by isotope and pressure~\cite{Schaack2023}, belong to this regime, outside the rule's domain." with:
   > Without NaOH and RbOH the weak side is right in 2 of 14 evaluations (5 formulas), so the reversal does not rest on the alkali hydroxides. In NaOD, path-integral simulations find that deuteration restores the weak hydrogen bonds and drives antiferroelectric order~\cite{Schaack2023}; the deuterium-favoured phase there has the longer O-H, the direction of the reversal here, but the screen's four NaOH structures, one of them a theoretical database entry, were not matched to those phases, and the mechanism there is anharmonic.

   Done-check: `grep -c "2 of 14 evaluations" docs/paper/main.tex` = 1; `grep -c "outside the rule's domain\." ` no longer matches in line 194.

4. **Sec. tests opening (line 262) and Limitation (6) (line 284).** Owner: conductor. 3 min.
   * Line 262, replace "No polymorph isotope free energy has been measured, so none of the tests below scores the rule directly." with:
     > Isotope effects on polymorph free energies have been measured only through related quantities, the D$_2$O shifts of ice boundaries and the mineral-water D/H fractionation of boehmite and diaspore (F07, F12); neither is a measurement of $\ddF$ at the model's conditions, so none of the tests below scores the rule directly.
   * Limitation (6): replace "(6) No polymorph isotope free energy has been measured." with "(6) No polymorph isotope free energy has been measured directly; F07 and F12 use related quantities."

   Done-check: `grep -c "No polymorph isotope free energy has been measured[,.]" docs/paper/main.tex` = 0.

5. **Discussion, "Known physics and the new part" (line 282).** Owner: conductor. 15 min. Four replacements inside the paragraph.
   * (a) Replace from "The harmonic quantity computed here is, for full substitution," through "we found no comparison between polymorphs of one formula." with:
     > For full substitution, $\ddF$ per H equals $k_{\mathrm{B}}T(\ln\beta_a-\ln\beta_b)$, with $\beta$ the full-substitution reduced partition function ratio per H of each polymorph, the formalism first-principles studies use for D/H fractionation between hydrous minerals and water~\cite{Meheut2010,Reynard2009}; a measured dilute-D fractionation between the polymorphs differs from it by the term $R$ of Eq.~\eqref{eq:bridge}, which is written per formula unit and which harmonicity alone does not remove. At 300~K, 1~meV per H corresponds to 38.7 per mil in $1000\ln\alpha$.
   * (b) Replace from "In KH$_2$PO$_4$-type crystals deuteration lengthens" through "such as KH$_2$PO$_4$ and NaOH." with:
     > In KH$_2$PO$_4$-type crystals deuteration lengthens the O$\cdots$O distance and raises the ordering temperature, which Ichikawa and co-workers trace to the geometric isotope effect~\cite{Ichikawa1978,Ichikawa1987}, an anharmonic change of geometry that our model omits because D is evaluated at the H geometry. The static analogue of the paraelectric phase has imaginary modes, so no harmonic $\ddF$ exists for that comparison, and the KH$_2$PO$_4$-type pairs of the prospective test were lost to imaginary modes (Sec.~\ref{sec:tests}). NaOH lies on the weak side, outside the rule's domain (Sec.~\ref{sec:weak}).
   * (c) Replace "We found no published comparison of polymorph pairs across inorganic O-H$\cdots$O solids, no slope against the O-H difference and no regime boundary." with:
     > Isotope effects on polymorph stability have been measured or computed for single systems: the H$_2$O and D$_2$O ice boundaries~\cite{Bridgman1935,Herrig2018}, the ice XI to Ih transition~\cite{Pamuk2015}, and D/H fractionation between the AlOOH polymorphs boehmite and diaspore and in the zoisite and epidote system~\cite{Graham1980}; the net quantum effect on a single hydrogen bond is known to change sign with bond strength~\cite{Li2011,McKenzie2014}. In the abstracts and texts we could read (the full texts of Refs.~\cite{Graham1980,Meheut2010,Reynard2009} were not accessible), we found no study that compares polymorph pairs across many inorganic O-H$\cdots$O compounds, fits the polymorph isotope free-energy difference against the O-H length difference, or locates in O-H length where the sign of that comparison reverses; our boundary at 0.99~\AA{} was set after inspecting the data.
   * (d) Replace "The O$\cdots$O form is a proxy that holds where O-H and O$\cdots$O move together along the Ichikawa correlation~\cite{Ichikawa1978}; it was not tested on hydrogen-bonded ferroelectrics, which are outside the screen." with:
     > The O$\cdots$O form rests on the inverse correlation between mean O-H and mean O$\cdots$O lengths across structures ($r = -0.83$ to $-0.85$ in the three models)~\cite{Ichikawa1978}, not on the isotope-induced change of either distance within a phase; it was scored only on the screen's pairs and is not established for proton-disordered phases or bent hydrogen bonds.

   Done-check: `grep -c "move together\|outside the screen\|difference of reduced partition function ratios\|makes no claim for proton-disorder\|no comparison between polymorphs of one formula" docs/paper/main.tex` = 0.

6. **Eq. bridge lead-in (line 286) and refs.bib.** Owner: conductor. 10 min.
   * Replace "For polymorphs $a$ and $b$ of one composition with $n_{\mathrm{H}}$ hydrogens per formula unit," with "For polymorphs $a$ and $b$ of one composition with $n_{\mathrm{H}}$ hydrogens per formula unit, the double difference per formula unit is".
   * Add `Pamuk2015` to refs.bib after confirming the record on Crossref (expected: Pamuk, Allen, Fernández-Serra, Phys. Rev. B 92, 134105 (2015), doi 10.1103/PhysRevB.92.134105, arXiv 1506.02009). Do not reuse Pamuk2012. Do not add Vitali2001 or Novak1974 now.
   * Done-check: Crossref title and authors match the bib entry; `grep -c "@article{Pamuk2015" docs/paper/refs.bib` = 1.

7. **Optional, Discussion first sentence.** Owner: conductor. 2 min. Replace "at 600~K and above our rule reduces to it (211 of 212 at 2000~K)" with "at high temperature the rule's sign agrees increasingly with this limit (211 of 212 at 2000~K)". Done-check: `grep -c "600~K and above our rule reduces" docs/paper/main.tex` = 0.

8. **Build, check, commit.** Owner: conductor. 10 min. `latexmk -pdf main.tex` in docs/paper; `grep -i "undefined\|Citation .* undefined\|Reference .* undefined" main.log` returns nothing; confirm Bridgman1935, Herrig2018, Pamuk2015, Graham1980, Koval2002, Schaack2023, Ichikawa1978, Ichikawa1987, Li2011, McKenzie2014 and labels sec:tests, sec:weak, eq:bridge resolve; page count noted. Also update docs/research/prior_art_sweep/SUMMARY.md "Wording" to the action 5(c) text and add Pamuk 2015, Graham 1980 (polymorph data, used in F12), Jodin-Caumon 2009 and the Vitali 2001 author correction (Vitali, Longstaffe, Bird, Gage, Caldwell) to the threat list. Commit on post-hackathon with a message that says "post-submission correction"; do not push. Done-check: `git log -1` on post-hackathon; submitted tag or commit unchanged; build log clean.

9. **Full-text check of the three unread sources.** Owner: Can (library access), conductor greps. 30 to 60 min once PDFs exist. Get Méheut et al. 2010 (GCA 74, 3874), Graham et al. 1980 (GCA 44, 353), Reynard and Caracas 2009 (Chem. Geol. 262, 159); conductor may first try Méheut's thesis (HAL tel-00231076) in the browser pane without downloading. Grep for "hydrogen bond", "O-H", "stretching", "bending", "libration", "boehmite", "zoisite", "β" against frequency or distance figures. Done-check: a short note per source in docs/research/prior_art_sweep/ stating whether a cross-mineral ln β against ν(OH) or d(OH) plot or fit exists and whether Graham ties the boehmite-diaspore sign to H-bond strength. If yes for either, apply "What would change this".

## What would change this

* **Méheut 2010 or the thesis plots or fits ln β against ν(OH) or d(OH) across minerals.** Add one sentence conceding a cross-mineral correlation for mineral-water β, cite it beside the novelty sentence, and move the claim to polymorph stability over 220 same-formula pairs plus the located reversal. Still keep, not withdraw.
* **Graham 1980 states that the boehmite-diaspore (or zoisite-clinozoisite) sign follows H-bond strength.** Add "as Graham and co-workers noted for that pair" to action 5(c) and to F12. No change to the option.
* **Any source reports a polymorph-pair isotope free energy fitted against O-H length across several compounds, or a polymorph sign boundary in O-H length.** Then option 3: withdraw the novelty claim and present F01 as a replication at scale.
* **A structure match shows mp-626000 or mp-23940 is Schaack's AFE or PE phase.** Then the Schaack sentence may say the screen reproduces the direction in those phases, still as harmonic analogy.
* **Crossref does not confirm Pamuk 2015 as cited.** Drop that clause from action 5(c) and keep the ice boundaries alone.
