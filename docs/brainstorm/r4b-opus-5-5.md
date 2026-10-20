# Round 4b: two bolder ideas

## Idea 1: MissingMinerals: "Earth's undiscovered minerals are already sitting in DFT databases"

**Headline:** We name about 200 specific minerals that should exist in nature but have never been described. Each comes with a computed powder pattern and a likely geological setting. A retrospective test then shows how many recently approved minerals this screen would have flagged years earlier.

**Steps (34 h)**
* **H0 to 5:** Parse the IMA/RRUFF mineral list (about 6,000 species, each with formula and approval year) using pymatgen. Reduce solid solutions to end members.
* **H5 to 11:** Pull Materials Project and Alexandria phases within 50 meV/atom of the hull, restricted to crustal elements and mineral anion chemistries. StructureMatcher links each phase to any known mineral.
* **H11 to 19:** Train a mineral likeness ranker (gradient boosting) on minerals approved before 2016 versus synthetic only compounds. Features: element co occurrence network (Hazen style), crustal abundance, anion type, hull energy, density.
* **H19 to 25:** Time split test. For minerals approved from 2016 to 2025, check whether a database analog existed and what rank it got. Report recall at K and enrichment over random.
* **H25 to 31:** Build the forward list with simulated XRD, a predicted paragenesis (oxidation zone, fumarole, pegmatite) and suggested localities from co occurrence data.
* **H31 to 34:** Interactive map and writeup.

**Hard result:** "X% of new minerals approved after 2016 were already in DFT databases, and our ranker put Y% of them in the top 1%." Plus a falsifiable list.

**Why new:** Hazen et al. (2015 to 2016) estimated the *number* of missing minerals with LNRE statistics. The Carbon Mineral Challenge and Morrison's mineral association analysis predicted chemistries and localities. Nobody has turned stable phase databases into a structure level, time validated mineral forecast.

**Verification:** Run a strict holdout on the latest CNMNC newsletters, which are excluded from training.

**Main risk:** Many new minerals are complex hydrated sulfates that DFT databases lack, so recall may be low. Even then, that is a quantified, publishable finding.

**1st place odds:** 25%

## Idea 2: NextInSpace: "Predicting which molecules astronomers will detect next"

**Headline:** A model given only interstellar detections before 2018 recovers a measurable share of the roughly 120 molecules found from 2018 to 2025 (the GOTHAM and QUIJOTE haul in TMC-1). It then releases a ranked target list with rotational constants that observers can use directly.

**Steps**
* **H0 to 3:** Encode the CDMS "Molecules in Space" list (about 330 entries with detection years) as SMILES.
* **H3 to 9:** Generate about 50k candidates as single edit neighbours of detected species: add C or CN, swap O and S, protonate, isomerize. Limit to 13 heavy atoms of C, H, N, O, S, Si and P.
* **H9 to 19:** Run GFN2 xTB on CPU for geometries, relative isomer energies, dipoles and rotational constants.
* **H19 to 26:** Fit a learning to rank model on pre 2018 data. Evaluate recall at 100 on later detections.
* **H26 to 34:** Spot check the top 30 with PySCF DFT dipoles, publish the list and write up.

**Hard result:** Recall at 100 against the real later detections, compared with the minimum energy principle baseline.

**Why new:** Prior work is Lattelais's minimum energy principle (2009) and Lee et al. (2021), who used ML embeddings to rank abundances in TMC-1. Neither ran a strict prospective time split or shipped spectroscopy ready predictions.

**Main risk:** Detection depends on whether a lab spectrum exists, which confounds what the model learns. Report this bias openly.

**1st place odds:** 18%

## Boldest feasible pick: MissingMinerals

My pick is MissingMinerals. It turns a vague statistical claim, that Earth hides about 1,500 undiscovered minerals, into named, checkable predictions. Anyone with a field kit or a museum drawer can test them against a real powder diffractometer. It also answers the judges' question directly: the time split shows the method *would have* made real discoveries. The organizer can retweet a map of where to find a new mineral, which is hard to say about benchmarks or audits. It fits the scoring well. It is relevant to materials data, it scales to any planetary chemistry (Mars and meteorites come next), and the angle is new.

Feasibility is my rough estimate, not a measurement:
* **Time split recall number:** about 75% chance of finishing solo in 34 h. Formula parsing of mineral names is the main time sink.
* **Clean prospective list with XRD and paragenesis:** about 60%.
* **A striking recall above 20% at the top 1%:** only about 35%.

Even a weak recall number is still an honest discovery claim with real data behind it.
