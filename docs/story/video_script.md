# IsoShift video script (draft v1, Opus, 21 Oct evening)

Target 3:40, hard limit 4:00. Can narrates in English over an OBS screen recording, captions from the SRT made from this text. About 130 words per minute, so roughly 480 spoken words. Placeholders in `{{...}}` are filled from results/candidates.csv after the Thursday 12:00 freeze. Claims follow docs/decisions/01-gate.md: "validated" only for the measured volume isotope effects of brucite and LiH; everything about polymorph pairs is an exploratory ensemble prediction.

## Shot list

| Time | Screen | Narration |
|---|---|---|
| 0:00 to 0:20 | Title slide: a crystal with H atoms turning into D | Swap hydrogen for deuterium and a crystal gets heavier, but its chemistry stays the same. Chemists do this all the time, for neutron scattering and to make metastable phases. The question we asked in two days: where does that swap change which crystal structure wins? |
| 0:20 to 0:50 | Slide 2: the trick (force constants are mass independent; one phonon calculation gives H and D) | The energy differences involved are a few meV per atom, smaller than the errors of any machine-learned potential. So we never trust absolute energies. Force constants do not depend on nuclear mass, so one phonon calculation gives both the hydrogen and the deuterium free energy. We compute only the isotope double difference between two polymorphs, where most model errors cancel, and we use four independent universal potentials as an ensemble. |
| 0:50 to 1:20 | Slide 3: the AI loop (Bond agent, cross-check, mathcheck, ensemble, board decisions) with the docs/decisions folder visible | The work was run by an AI team. A literature agent on Valency Bond pulled measured isotope effects from papers, a second model checked every number, two models derived every formula independently, and a board of three models made the gate decisions, all logged in the repository. {{n_bond}} literature queries, every one recorded. |
| 1:20 to 2:00 | Figure 1 left panel: validation parity | First we checked the physics. Brucite, magnesium hydroxide, is measured to have a 0.31 percent larger volume with hydrogen than with deuterium. All four models get the sign, and land between 0.19 and 0.44 percent. Lithium hydride: right sign in all four, about 30 percent too large. Ice: the anomalous opposite sign is reproduced, but four to ten times too large, so we report ice and do not use it as evidence. |
| 2:00 to 2:50 | Figure 1 right panel: candidate map, then the candidate card | Then we screened {{n_pairs}} polymorph pairs of hydrogen compounds from Materials Project and JARVIS. Most fall below what the ensemble can resolve, and we say so. {{n_clean}} pairs pass every filter with all models agreeing. The strongest experimentally known pair is {{best_formula}}: deuteration shifts the free-energy balance by {{best_ddF}} meV per atom toward {{best_phase}}, with a model spread of {{best_spread}}. {{best_card_sentence}} |
| 2:50 to 3:20 | marimo app: pick the pair, move the static-energy slider | All of this is in an open marimo app. Pick a pair, and you see the hydrogen and deuterium free-energy curves for every model. Move the slider for the static energy offset: the transition temperature itself moves a lot, but the isotope shift stays. That is why we report the shift and not the absolute temperature. |
| 3:20 to 3:40 | Slide: limits and next step | Limits: harmonic and quasi-harmonic only, potentials trained on the same DFT functional, no tunnelling. Next step is one D2O synthesis or a neutron run on {{best_formula}}. Code, data and every decision are public. |

## Turkish draft (for Can's read-through)
Hidrojeni döteryumla değiştirince kristal ağırlaşır ama kimyası aynı kalır. Bu değişimin hangi kristal yapının kazanacağını değiştirdiği yerleri iki günde aradık. Enerji farkları atom başına birkaç meV, yani makine öğrenmesi potansiyellerinin hatasından küçük. Bu yüzden mutlak enerjiye güvenmiyoruz: kuvvet sabitleri kütleye bağlı olmadığı için tek bir fonon hesabı hem H hem D serbest enerjisini veriyor, ve sadece iki polimorf arasındaki izotop çift farkını hesaplıyoruz. Dört bağımsız potansiyel ensemble olarak kullanılıyor. Önce fiziği ölçümlerle sınadık (brucite, LiH), sonra {{n_pairs}} polimorf çiftini taradık ve ensemble'ın ayırt edebildiği adayları raporladık.

## Open items
* Fill placeholders after the 12:00 freeze from results/candidates.csv and the candidate card.
* Make SRT from the final narration.
* Rehearsal at 19:00 Thursday (Can).
