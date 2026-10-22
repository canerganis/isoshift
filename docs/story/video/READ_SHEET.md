# IsoShift video: read sheet (audio and screen recorded separately)

Can records the pieces below; Claude assembles the video with ffmpeg (slides held for the length of each audio file, marimo clip under segment 12), cuts the YouTube and LinkedIn versions, and re-times both caption files to the real audio. Narration is `video_script.md` word for word (decision 09), split at the slide changes of `RECORDING.md`.

## What to record

1. **Audio, 13 files.** One file per segment, in order. Windows Sound Recorder (Ses Kaydedici) is enough; same mic and room for all. Leave about half a second of silence at the start and end. A mistake: stop, delete that file, record that segment again.
2. **Screen, one silent clip, about 20 s.** The marimo app at 125 percent zoom, click path of `RECORDING.md` scene 8 (F01 tab 2 s, Check a pair, scroll to the model table, How we know, slow scroll). OBS Display or Window Capture, or Win+Alt+R.
3. **Face, one clip, about 6 s, with sound.** Windows Camera (Kamera), video mode, segment 00. LinkedIn version only.

Put everything in one folder and send Claude the path.

## Pronunciation

Turkish-letter reading, stressed syllable in capitals. American English; "aluminium" and "favours" are British spellings in the script, read as written below.

| Word | Read as | Segment |
|---|---|---|
| deuterium | dyu-Tİİ-ri-ım | 01 |
| deuteration | dyu-tı-REY-şın | 04, 07 |
| hydrogen-bonded | HAY-drı-cın BAN-dıd | 01 |
| polymorph, polymorphs | PA-li-morf, PA-li-morfs | 01, 02, 03 |
| potential, potentials | pı-TEN-şıl, pı-TEN-şılz | 01, 02, 13 |
| machine-learned | mı-ŞİİN lörnd | 01 |
| phonon | FOU-nan | 02 |
| SevenNet | SE-vın-net | 02 |
| isotope | AY-sı-toup | 02, 03, 08 |
| angstrom | ENG-strım | 03, 06 |
| thousandth | TAU-zıntθ (th dili dişe değerek) | 03 |
| libration | lay-BREY-şın | 03, 04 |
| evaluations | i-vel-yu-EY-şınz | 04 |
| aluminium | el-yu-Mİ-ni-ım | 04 |
| hydroxide | hay-DRAK-sayd | 04 |
| favours | FEY-vırz | 04 |
| bias | BAY-ıs | 06 |
| frequencies | FRİİ-kwın-siz | 06 |
| spectra | SPEK-trı | 06 |
| diaspore | DAY-ı-spor | 07 |
| delta-AlOOH | DEL-tı ey-el-ou-ou-EYÇ | 07 |
| deep-Earth | diip-ÖRθ | 07 |
| gigapascal | Gİ-gı-pas-kal | 07 |
| kelvin | KEL-vin | 07 |
| harmonic | har-MA-nik | 07, 13 |
| D/H fractionation | dii-EYÇ frek-şı-NEY-şın | 08 |
| partitioning | par-Tİ-şı-nıng | 08 |
| coexisting | kou-ig-Zİ-sting | 08 |
| Valency | VEY-lın-si | 10 |
| councils | KAUN-sılz | 11 |
| dissent | di-SENT | 11 |
| marimo | mı-Rİİ-mou | 12 |
| tunnelling | TA-nı-ling | 13 |
| validations | ve-li-DEY-şınz | 13 |
| O-H | ou-EYÇ | 01, 03, 04, 06 |
| meV | em-ii-Vİİ | 03 |

Numbers:

| Written | Read as |
|---|---|
| 185 of 212 | a hundred and eighty-five of two hundred and twelve |
| 131 | a hundred and thirty-one |
| 220 | two hundred and twenty |
| 0.11 to 0.13 | zero point one one to zero point one three |
| 74, 10 | seventy-four, ten |
| 2 of 20 | two of twenty |
| 2.5 and 2.8 | two point five and two point eight |
| 300 kelvin | three hundred kelvin |
| 9 to 13 | nine to thirteen |
| 1.13 and 1.33 | one point one three and one point three three |

## Segments

| # | On screen | Read |
|---|---|---|
| 00 | face (camera) | Hi, I'm Can, a metallurgical and materials engineer. This is IsoShift. |
| H0 | slide_00_hook | One extra neutron in hydrogen moves a crystal transition by four gigapascals. We found no rule for which crystals this hits. So we found one. |
| 01 | slide_01_title | Swap hydrogen for deuterium in a hydrogen-bonded crystal and, in our calculations, it leans toward the polymorph with the shorter O-H bonds. Three machine-learned potentials get this sign in 185 of 212 cases where the hydrogen bonds are moderate or strong, and the rule says where it stops working. What we found at this hackathon is a simple rule: deuterium favours the crystal with shorter O-H bonds. |
| 02 | slide_02_method | Polymorph energy gaps are smaller than any machine-learned potential's error. So we compute only the isotope difference. Force constants do not depend on mass, so one phonon calculation gives both hydrogen and deuterium free energies, and the static gap cancels. Three universal potentials do the work; SevenNet only votes on signs. |
| 03 | slide_03_headline | We screened 220 polymorph pairs. The isotope free-energy difference follows the change in mean O-H length, 0.11 to 0.13 meV per hydrogen per thousandth of an angstrom. The O-H stretch drives it, and bending and libration cancel about half. |
| 04 | slide_03b_counts_zoom | Where hydrogen bonds are moderate or strong, deuteration favours the polymorph with the shorter O-H bonds in 185 of 212 model evaluations. A baseline that always guesses one sign gets 131. Counted per pair, 74 are right and 10 are wrong, and all 10 wrong pairs contain the same aluminium hydroxide structure, where bending and libration outweigh the stretch. |
| 05 | slide_03c_weak_side_zoom | With weak hydrogen bonds it fails, 2 of 20. We chose that boundary after seeing the data, and we say so. |
| 06 | slide_04_stretch_check | Is this a shared model bias? Their O-H stretch frequencies follow the slope measured from real mineral spectra, for O to O distances between 2.5 and 2.8 angstrom. That checks the main ingredient, not the free energies. |
| 07 | slide_05_alooh_card | Diaspore turns into delta-AlOOH, a possible deep-Earth water carrier. The measured boundary lies at higher pressure and high temperature. Our 300 kelvin models put it at about 9 to 13 gigapascal, and both say deuteration raises it, by 1.13 and 1.33 gigapascal. It is an exploratory sign prediction, because delta-AlOOH has proton disorder there that harmonic physics leaves out. |
| 08 | slide_06_m02_bridge | Nobody has measured this directly, but the isotope shift of a phase boundary equals the D/H fractionation between the two phases, so deuterium partitioning between coexisting polymorphs is a direct test. |
| 09 | slide_07_ai_process | An AI team ran the work. |
| 10 | slide_07c_bond_trace | Literature agents on Valency Bond pulled the measured values and logged every query. |
| 11 | slide_07b_commit_timeline | Predictions were committed to git before the data were read. Councils of three models argued each claim, and every decision records its dissent. A second model rewrote the calculation blind and matched our numbers. |
| 12 | marimo screen clip | Everything runs in an open marimo app. Pick a pair and see the model numbers, the rule's call, and the Bond query behind each measured value. |
| 13 | slide_08_limits_repo | Limits. Two blind tests did not pass: one came out mixed, one failed. The physics is harmonic, with no proton tunnelling. The potentials are trained on similar data, so three models agreeing is not three validations. Code, data and every decision are public. One measurement, D/H partitioning between coexisting polymorphs, can now test it. |

Target total of 01 to 13: 3:30 to 3:45. Hard limit 4:00.
