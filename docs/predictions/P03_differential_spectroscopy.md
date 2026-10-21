# P03. Second predeclared differential O-H spectroscopy pair: manganite -> groutite (MnOOH)

Committed before any band position for these phases was looked up. Model numbers: `docs/predictions/P03_spectro_model.csv` (`src/isoshift_event/spectro.py`, same method as P02 v2: periodic acceptor search, dominant Gamma modes).

Pair: manganite gamma-MnOOH (P2_1/c, mp-29159) -> groutite alpha-MnOOH (Pnma, diaspore type, mp-626270). Both are natural minerals with published IR/Raman spectra. In the models groutite has the weaker hydrogen bond (O...O longer by 9 to 26 mA), so this pair tests the opposite direction to P02: the O-H stretch should go up and the O-H bend should go down.

Model predictions (dominant Gamma modes, groutite minus manganite, mace / orb / mattersim; medians in brackets):
* stretch: +117 / +133 / +119 (+119) cm-1
* highest in-plane delta OH bend: -49 / -136 / -34 (-49) cm-1

Excluded before looking at data: the two Al(OH)3 pairs computed alongside (JVASP-29414 vs 29793 and vs 29833): predicted shifts are below about 60 cm-1, at the resolution of the rules, and the phase identities of the JARVIS structures are not yet confirmed.

Decision rules: identical to P02 v2 (rules 1 to 4, factor-3 window, +/-150 cm-1 stretch bracket, 30 cm-1 resolution), with all signs mirrored: SUPPORT needs Delta stretch > 0 and Delta bend < 0 within the windows; CHALLENGE if Delta stretch < 0 or Delta bend > 0 (both resolved). Measured comparator: main O-H stretching band and highest-frequency assigned delta OH band of each mineral, same technique where possible. Also recorded but not scored: the measured bend/stretch shift ratio (council 05 asked for it).
