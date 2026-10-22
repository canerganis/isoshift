# IsoShift video: recording checklist for Can

Target length 3:40. Hard limit 4:00 (YouTube upload, judging cut-off). Narration and shot times come from `docs/story/video_script.md` (v4, frozen numbers). `captions.srt` is built from the same narration column and the same time windows. Slides are 1920x1080 PNGs in this folder (all text 48 px or larger, Okabe-Ito colours, white background).

## Before you record

1. Start the app and leave it running: `.venv/Scripts/python.exe -m marimo run app/isoshift_app.py` from the repo root. Open the URL it prints (normally http://localhost:2718) in a browser window. Everything in it is precomputed, nothing waits on a calculation.
2. Browser zoom 125 percent, bookmarks bar hidden, no other tabs visible. In the app click the "F01 isotope rule" tab once to check the banner reads "185/212 O-H evaluations agree with the rule (87.3%; baseline 131/212). Pair majorities: 74 right, 0 ties, 10 wrong; all 10 involve mp-985293."
3. Open these in an editor or file viewer, one window or tab each, in this order: `logs/bond_queries.jsonl`, a terminal showing `git log --oneline -- docs/predictions` (hash example: f3ac0ac, the blind P04 prediction), the folder `docs/decisions/`, `docs/findings/F06-independent-replication.md`. Optional for the AlOOH shot: `docs/findings/CARD-AlOOH.md`, scrolled to the temperature table.
4. OBS: base and output canvas 1920x1080, 30 fps, mkv or mp4 recording, mic level checked. Add each PNG below as an Image source, one scene per row, and one Window Capture scene for the browser and one for the editor.
5. Rehearse once with a timer. Stop at 3:50 or less. If over, cut the fig5 shot (scene 4) first, then shorten the AI-process tour.

## OBS scene order

| # | Script time | OBS scene | What is on screen | Do |
|---|---|---|---|---|
| 1 | 0:00 to 0:21 | `slide_01_title.png` | IsoShift title, H to D, diaspore and delta-AlOOH | Read the hook. No clicking. |
| 2 | 0:21 to 0:48 | `slide_02_method.png` | One set of force constants, two masses, the three potentials, SevenNet greyed | Read the method paragraph. |
| 3 | 0:48 to 1:37 | `slide_03_headline.png`, then `slide_03b_counts_zoom.png`, then `slide_03c_weak_side_zoom.png` | Headline figure with 185/212 beside it | Start on the full figure. At "185 of 212" cut to 03b (count box). At "With weak hydrogen bonds it fails" cut to 03c. Use only the cuts you rehearsed. |
| 4 | 1:37 to 1:55 | `slide_04_stretch_check.png` | Stretch check figure, window 2.50 to 2.80 A shaded, slope ratios 0.91, 0.92, 0.92 | Read the stretch paragraph. This is the shot to cut if you run long. |
| 5 | 1:55 to 2:23 | `slide_05_alooh_card.png` | "Exploratory sign prediction", 300 K +1.13 GPa (ORB) and +1.33 GPa (MACE), about 1000 K +0.7 to +0.9 GPa | Read the card paragraph. Optional: for the last 5 s cut to `CARD-AlOOH.md` at the temperature table. |
| 6 | 2:23 to 2:39 | `slide_06_m02_bridge.png` | Boundary isotope shift = D/H fractionation between the two phases | Read the bridge paragraph. |
| 7 | 2:39 to 3:08 | `slide_07_ai_process.png` for about 5 s, then the editor window | AI process slide, then screen tour | Cut in this order, about 5 s each: `logs/bond_queries.jsonl`, the `git log` terminal with the commit hashes, `docs/decisions/`, `F06-independent-replication.md`. |
| 8 | 3:08 to 3:21 | Browser window (marimo app) | Banner, Check a pair, How we know | See the click path below. |
| 9 | 3:21 to 3:40 | `slide_08_limits_repo.png` | Limits and https://github.com/canerganis/isoshift | Read the limits paragraph. Hold the slide 2 s after the last word. |

## Click path in the marimo app (scene 8, 13 s)

1. Start on the "F01 isotope rule" tab (banner visible, 2 s). Do not touch the sliders.
2. Click "Check a pair" (3 s). The dropdown already shows the default pair, diaspore (mp-625152) vs delta-AlOOH (mp-23807). Do not change it. Scroll just enough to show the model table, the rule's call and the experimental provenance lines.
3. Click "How we know" (7 s). Scroll slowly through the brucite Bond provenance trace, from the first query to the gate decision.
4. Cut to scene 9.

Do not open "Benchmark & atlas" and do not open the "Post hoc sensitivity" expander on camera.

## Numbers to say as written

185 of 212, baseline 131, 74 pairs right and 10 wrong, 2 of 20 on the weak side, 220 pairs screened, 0.11 to 0.13 meV per hydrogen per thousandth of an angstrom, +1.13 and +1.33 GPa at 300 K. The script says the 300 K boundary is "9 to 14 gigapascal"; `CARD-AlOOH.md` gives the H roots 8.76 (MACE) and 13.00 (ORB) GPa. If you want to match the card exactly, say "9 to 13", and change the matching caption line.

## Captions

`captions.srt` has 44 cues, at most 2 lines of 42 characters, split by character count inside each row's window. Timings follow the script, not your real pace. After the final cut, either re-time in YouTube Studio or give Studio the plain text and use "Auto-sync".

## YouTube upload

1. Upload the final file (3:40 target, under 4:00).
2. Title: `IsoShift: swapping hydrogen for deuterium tips crystals toward shorter O-H bonds`
3. Visibility: Public. Audience: not made for kids. Language: English.
4. Description (paste as is):

```
IsoShift tests a simple rule: in hydrogen-bonded crystals, swapping hydrogen for deuterium tips the balance toward the polymorph with the shorter O-H bonds. In harmonic calculations with three machine-learned potentials the rule gets the sign right in 185 of 212 evaluations, it fails for weak hydrogen bonds, and it gives an exploratory sign prediction for the diaspore to delta-AlOOH boundary. Code, data and every decision: https://github.com/canerganis/isoshift
AI disclosure: the calculations, literature search and drafts were produced by AI agents working under my direction, and every query and decision is logged in the repository.
```

5. Subtitles: Add language English, Upload file, With timing, choose `captions.srt`, Publish.
6. Check the Public link in a private window, confirm captions show, and paste the video URL into the submission form and README.
