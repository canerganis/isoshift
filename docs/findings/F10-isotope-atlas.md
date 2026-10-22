# F10. Isotope atlas: predicted deuteration preference for every O-H polymorph pair in the Materials Project set

Status: ATLAS ONLY, untested. Post-freeze addendum; it does not change the frozen F01 headline (decision 07). Council 08 set the literature test aside as low priority (the boehmite/diaspore literature test is run separately), so this finding reports the map, its counts and its cost, and no verdict on the rule.

## What was built

`src/isoshift_event/atlas.py` reads `data/isoshift/mp_h.json` (Materials Project, no C, E_hull ≤ 50 meV/atom) and, from the stored DFT geometry only (no phonons, no ML relaxation), writes `results/atlas.csv` and `results/atlas_summary.json`. Predictions for the observed strong-regime pairs were committed blind in `docs/predictions/P08_atlas_blind.md` (commit d991991) before any literature lookup.

* Population: structures with at least one O-H donor (H with nearest O ≤ 1.15 Å), no atom-count cap; same reduced composition, primitive cells, deduplicated with StructureMatcher (ltol 0.2, stol 0.15, angle_tol 5) and the space-group gate of `pairs.py`; pairs with |dE| ≤ 50 meV/atom from MP energies.
* Per structure: mean O-H over all donors, mean donor O...O over donors with an acceptor (H...O < 2.6 Å).
* Regime: strong if either polymorph has mean O...O ≤ 2.929 Å (translated threshold in `results/F01_oo.json`).
* Sign: F01 convention; deuteration favours the polymorph with the shorter mean O-H (longer mean O...O). Confidence from |dO-H| (5 mÅ) and |dO...O| (0.03 Å): high, medium, low, or conflict when the two differences disagree.
* Experimentally observed: MP theoretical=False for the phase (or any entry merged into it).

## Counts

| Quantity | Value |
|---|---|
| O-bearing formulas in mp_h.json | 2722 |
| Structures with an O-H donor | 3212 (14 duplicates merged) |
| Polymorph pairs | 1796 in 317 formulas |
| Regime | strong 1488, weak 292, undefined 16 |
| Confidence, all pairs | high 503, medium 386, low 383, conflict 524 |
| Both phases experimentally observed | 218 |
| Strong regime and both observed (P08 list) | 185 pairs, 122 formulas; high 62, medium 29, low 43, conflict 51 |

Where both differences are above their cuts (639 pairs), dO-H and dO...O agree in sign in 79% of pairs (correlation of dO-H with dO...O over all pairs, r = -0.54). Most conflicts sit at small differences (median |dO-H| 2.9 mÅ, |dO...O| 0.028 Å): the median |dO-H| between MP polymorphs is 4.1 mÅ, below the 5 mÅ headline eligibility, so most database pairs are low-signal calls.

## Scalability

The whole set (3402 O-bearing structures read, 3212 with O-H donors, 1796 pairs) runs in 53 s on one CPU core: 0.03 s per pair including deduplication, 8.6 s for the donor geometry. No GPU. The cost is set by StructureMatcher, not by the prediction, so the map scales to any database that stores relaxed structures.

## Caveats

1. The F01 rule was established on ML-relaxed structures with harmonic free energies; the atlas applies it to DFT database geometry, where polymorph O-H differences are often a few mÅ. It is untested on this geometry.
2. The rule is a statement about the vibrational isotope term between fixed, ordered structures. Isotope effects that come from proton order-disorder, tunnelling or kinetics are outside it; P08 predeclares their exclusion.
3. The 0.99 Å O-H boundary was chosen after inspecting the data (decision 07); its O...O translation inherits that.

## Literature step: collected, not scored

Before the council 08 redirect, the blind collection step of P08 ran: a Sonnet agent (`sonnet-atlas-blind`, 27 Bond queries in `logs/bond_queries.jsonl`, then OpenAlex and web) wrote 26 rows to `data/isoshift/atlas_lit.csv`. Most rows are proton order-disorder, ferroelectric, superionic or symmetrisation transitions, which the P08 exclusion rule E1 removes. The CSV is kept as raw input for whoever runs the test. Scoring against P08 was not done, so this finding makes no claim that the rule holds or fails on experiment.
