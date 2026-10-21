# IsoShift video script (v3, Opus, 21 Oct; wording per decisions 05 and 06)

Target 3:40, hard limit 4:00. Can narrates in English over an OBS screen recording; captions come from an SRT made from the narration column. About 130 words per minute. Claim wording follows [05-final-claims.md](../decisions/05-final-claims.md); scope and order follow [06-strategy-to-submission.md](../decisions/06-strategy-to-submission.md) item 5 and its judge sentence. F01 is a regime-limited computational rule; the AlOOH card is an exploratory sign prediction. Goethite, temperature dependence, F02/F05/F06 details stay out of the video.

Numbers in `{{...}}` come from the Thu 12:00 freeze and are filled by the freeze script; the value inside the braces is the current one, so the script can be rehearsed as written. All other numbers are fixed.

## Shot list

| Time | Screen | Narration |
|---|---|---|
| 0:00 to 0:21 | Title card: two AlOOH polymorphs side by side, H atoms turning into D. Caption: "IsoShift" | Swap hydrogen for deuterium in a hydrogen-bonded crystal and it leans toward the polymorph with the shorter O-H bonds. Three machine-learned potentials agree in {{123}} of {{130}} cases where the hydrogen bonds are moderate or strong, and the rule says where it stops working. |
| 0:21 to 0:48 | Slide: one set of force constants, two masses, H and D free energies; ensemble logos MACE, ORB, MatterSim, plus SevenNet greyed "sign votes only" | Polymorph energy gaps are a few meV per atom, smaller than any machine-learned potential's error. So we compute only the isotope difference. Force constants do not depend on mass, so one phonon calculation gives both hydrogen and deuterium free energies, and the static energy gap cancels. Three universal potentials do the work; SevenNet only votes on signs. |
| 0:48 to 1:37 | `figures/fig4_xh_rule.png` (headline). Zoom on the count box, then on the weak-bond side | We screened {{197}} polymorph pairs. The isotope free-energy difference follows the change in mean O-H length, {{0.12 to 0.15}} meV per hydrogen per thousandth of an angstrom. The O-H stretch drives it, and bending and libration cancel about half. Where hydrogen bonds are moderate or strong, deuteration favours the shorter O-H bonds in {{123}} of {{130}} model evaluations. A baseline that always guesses one sign gets {{82}}. Counted per pair, {{62}} are right, {{5}} are ties, and {{0}} are called the wrong way. With weak hydrogen bonds it fails, {{1}} of {{16}}. We chose that boundary after seeing the data, and we say so. |
| 1:37 to 1:55 | `figures/fig5_stretch_check.png`: model stretch frequencies on the Libowitzky curve, window 2.50 to 2.80 Å highlighted | Is this a shared model bias? Their O-H stretch frequencies follow the slope measured from real mineral spectra, for O to O distances between 2.5 and 2.8 angstrom. That checks the main ingredient, not the free energies. |
| 1:55 to 2:23 | `docs/findings/CARD-AlOOH.md` in the app or editor. Banner on screen: "Exploratory sign prediction, 300 K: +1.13 GPa (ORB), +1.33 GPa (MACE)". No goethite card | Diaspore turns into delta-AlOOH, a possible deep-Earth water carrier. The measured boundary near 18 gigapascal is at high temperature. Our 300 kelvin models put it at 9 to 14 gigapascal, and both say deuteration raises it, by 1.13 and 1.33 gigapascal. It is an exploratory sign prediction, because delta-AlOOH has proton disorder there that harmonic physics leaves out. |
| 2:23 to 2:39 | Slide: one line, "boundary isotope shift = D/H fractionation between the two phases" (`docs/math/M02-bigeleisen-bridge.md`) | Nobody has measured this directly, but the isotope shift of a phase boundary equals the D/H fractionation between the two phases, so measuring how deuterium splits between coexisting polymorphs is a direct test. |
| 2:39 to 3:08 | Screen tour: `logs/bond_queries.jsonl`, `docs/predictions/` with its commit hash, `docs/decisions/`, the F06 replication note in `docs/findings/` | An AI team ran the work. Literature agents on Valency Bond pulled the measured values, and every query is logged. Predictions were committed to git before the data were read. Councils of three models argued each claim, and every decision is written down with its dissent. A second model rewrote the calculation without reading our code and matched our numbers. |
| 3:08 to 3:21 | marimo app: "Check a pair" tab, pick delta-AlOOH vs diaspore, then the Bond provenance trace | Everything runs in an open marimo app. Pick a pair and see the model numbers, the rule's call, and the Bond query behind each measured value. |
| 3:21 to 3:40 | Slide: limits, then repository URL | Limits. One blind test came out mixed. The physics is harmonic, with no proton tunnelling. The potentials are trained on similar data, so three models agreeing is not three validations. Code, data and every decision are public. |

Spoken words in the narration column: 456 (about 3:30 at 130 words per minute, 3:40 with pauses).

## Turkish reading draft (for Can, not recorded)

Hidrojeni döteryumla değiştirince hidrojen bağlı bir kristal, O-H bağları daha kısa olan polimorfa doğru kayıyor. Üç makine öğrenmesi potansiyeli, hidrojen bağları orta veya güçlü olduğunda 130 değerlendirmenin 123'ünde buna uyuyor; hiçbir çift ters yönde tahmin edilmiyor. Bağlar zayıfsa kural çalışmıyor (16'da 1) ve bunu açıkça söylüyoruz. Sınırı veriye baktıktan sonra seçtik. Kuvvet sabitleri kütleye bağlı olmadığı için tek bir fonon hesabı hem H hem D serbest enerjisini veriyor ve statik enerji farkı sadeleşiyor. Modellerin O-H gerilme frekansları ölçülmüş mineral spektrumlarının eğimini izliyor; bu bir tutarlılık kontrolü, doğrulama değil. Somut tahmin: diaspor ile delta-AlOOH sınırını döteryum 300 K'de 1.13 ile 1.33 GPa yukarı itiyor. Bu araştırma amaçlı bir işaret tahmini, çünkü o basınçta proton düzensizliği var. Doğrudan deney: iki fazın arasındaki D/H ayrımlaşmasını ölçmek. Sınırlar: bir kör test karışık çıktı, fizik harmonik, potansiyeller benzer verilerle eğitildi.

## Open items

Freeze placeholders (fill from the Thu 12:00 freeze, then check `git grep -n "{{" docs/story/video_script.md` is empty before recording):

| Placeholder (current value) | Source |
|---|---|
| {{123}} right, {{130}} evaluations | `results/F01_cv.json` `oh_unfiltered_strong.right`, `.n` |
| {{82}} baseline | `oh_unfiltered_strong.baseline_right` |
| {{197}} pairs screened | `n_unique_pairs.unique_pairs` |
| {{0.12 to 0.15}} meV per H per mÅ | screen-wide all-row slopes, F01 (MACE, ORB, MatterSim) |
| {{62}} right, {{5}} ties, {{0}} wrong pairs | unique-pair majority on the `oh_unfiltered_strong` population (decision 06 recheck) |
| {{1}} of {{16}} weak side | `oh_split.all_eligible` minus `oh_unfiltered_strong` |

Other items:
* If `figures/fig_headline.png` (decision 06 action 9) exists by 17:30, show it in the 0:48 shot instead of fig4; same counts.
* The 3:08 shot needs the marimo "Check a pair" tab and the Bond trace (decision 06 item 5). If they are not ready, show the F01 tab and `logs/bond_queries.jsonl`.
* The Turkish draft is for reading only; the freeze script does not update its numbers.
* Card numbers (+1.13 / +1.33 GPa, 9 to 14 GPa) are fixed and not part of the freeze.
* Rehearsal with a timer Thu 17:30 (Can): 3:50 or less, trim the fig5 shot first. Record 19:00, SRT from the narration column.
