# IsoShift: 34-hour plan

Times are Turkey time. Official schedule (Moment): hacking may begin any time on Oct 21 anywhere on Earth, so we can start as soon as Can is ready (no need to wait for 17:00). Deadline Fri 23 Oct 03:00. Submit by 02:00 to keep a buffer. Block times below shift earlier accordingly.
Extra platform credits are listed in Slack #resources.

## Morning checklist for Can (before 17:00, ~30 min)
1. Materials Project API key: materialsproject.org → Dashboard → API key. Put it in `.env` as `MP_API_KEY=...` (never commit).
2. Valency MCP Bond: sign up at valency.io, connect to Claude Code (setup guide in #valency). Needed for the Valency prize and literature checks.
3. Join the hackathon Slack; read the kickoff video/notes when posted; check the submission form fields.
4. Read DECISION.md (10 min) and say go / no-go. Plan B is PackEvolve if you veto.

## Submission (Slack #general, Ben Blaiszik, 21 Oct)
- Submitted on the new OSI platform **Moment**: sign up early at scientificintelligence.org/onboarding?campaign=osi-hackathon-2026 (Globus preferred, Google login works via Globus; Auth0 fallback), create a team (solo = team of one).
- Fields: (1) link to social media post (the video goes here), (2) brief write-up with optional figure, (3) code repository link, (4) checkboxes for platforms used (tick Valency Bond, marimo).
- Code must be enough to show the work is real (Ben in #random); reusability is a bonus.
- Valency prize: use Bond in the project; help in #valency.

## Execution plan (v3, agreed with Can 21 Oct afternoon, work starts Wed 21 Oct 17:00)

Planning and accounts before 17:00 (0.3, 0.4); event work from 17:00 (hour 0). Gate at **Thu 00:00** (hour 7, pulled in from hour 10 so the overnight screen starts before Can sleeps). Submit by **Fri 02:00**, hard deadline 03:00.

Owners: **C** = Claude (orchestration, physics code in `src/`, gates). **X** = Codex gpt-6-astra (bulk code, Bond literature queries, code review; via `codex exec` or `harness.ask`). **G** = Gemini 4 Argon (consultation and review only, via `harness.ask`). **S** = Sonnet subagent (mechanical work: scripts, tables, formatting). **Can** = decisions, domain sanity, accounts, video, submission.
Claude budget (Can, 21 Oct): up to 95% of Can's Claude limit may go to this hackathon. **Opus (high effort) is the architecture decision maker**: design of `src/` modules, physics choices, gate and scope calls, final review of every workflow's output. Opus subagents also take hard code (pairs/screen core, QHA fixes) when Codex output fails review. Codex stays the main bulk coder, Gemini 4 Argon consultation only, Sonnet/Haiku for mechanical work. Budget check at the gate and at 13:00 Thursday; if usage is ahead of schedule, shift reviews back to Codex+Gemini.
Effort policy (Claude assigns, per task): **max** for physics/architecture decisions with no easy check (gate call, ΔT_iso method, brucite imaginary-mode diagnosis, red team of final claims); **high** for core code and reviews (pairs, screen, QHA, analysis, app); **medium/low** for mechanical work (fetching, formatting, README, fresh-clone test). Codex effort via `-c model_reasoning_effort=xhigh|high|medium`, Opus/Sonnet via the agent `effort` setting.
**Advisory board (Can, 21 Oct)** for hard decisions: Opus max (chair), Codex gpt-6-astra xhigh, Gemini 4 Argon high. Each member gets the same brief with the data and answers independently (no shared drafts), then the chair writes the decision with dissent and rationale to `docs/decisions/NN-<topic>.md`. Convened for: brucite/imaginary-mode handling (1.4), the gate (2.x), ΔT_iso method and ranking criteria (4.1), fallback switch, final claims and headline (4.5, 6.1). Not convened for routine code or formatting.
**Final authority:** Opus (this orchestrating session, high/max effort) makes all task assignments, owner and effort choices at the start of each block, and is the final decision maker on every gate, scope and claim; the board advises, Opus decides. The owner tables above are the starting assignment and Opus may reassign.
**Physics and math (Can, 21 Oct):** gpt-6-astra (xhigh) is the preferred model for physics and math work: deriving and checking the ΔT_iso ≈ ΔΔF_iso / ΔS estimate and its error propagation, QHA/thermodynamics checks, imaginary-mode diagnosis, unit and sign audits of validation numbers. Opus integrates and decides.
**Workers and scans (Can, 21 Oct):** worker agents and scans go to Sonnet and Haiku, not Opus. Haiku: fetching (MP/JARVIS/PhononDB), log and result scanning, file checks, overnight watchdog. Sonnet: literature scans and Bond query batches, table building, running scripts and tests, figures, README. Opus agents only for design and decisions.
**Not linear (Can, 21 Oct):** blocks are a skeleton, work runs as parallel tracks whenever inputs exist:
* GPU track: the harmonic mace+orb screen starts as soon as `screen.py` passes its dry run (~20:00), interleaved with validation jobs; the gate only decides framing, not whether the screen runs.
* Benchmark track (2.3): DFT phonon fetch and parity run from 17:30, independent of validation.
* Product track: marimo app skeleton, README and write-up skeleton start in the evening with placeholder data (Codex + Sonnet), filled when results land.
* Story track: video script, slides and figure layout drafted overnight and Thursday morning, not left to Block 6.
* Literature track: Bond novelty checks run on candidates as they enter the ranking, not only for the final top 10.
Opus re-plans at every result checkpoint and moves work forward whenever a track is idle.
**Orchestration:** see `docs/WORKFLOW.md` (phase workflows WF0 to WF6, building blocks board / mathcheck / build / sweep, state ledger, GPU queue, never-half-done rules).
**Minimal human in the loop (Can, 21 Oct):** Claude runs blocks autonomously with workflows (Workflow tool, Sonnet/Codex workers, Codex+Gemini reviewers) and orchestra skills. Can is needed only for: public repo go-ahead, video recording, Moment submission, and any account login. Gate and scope decisions follow the written criteria; Can gets a short status note at the gate and in the morning.
Hardware: RTX 4060 laptop. Overnight: plugged in, Windows sleep off, lid-close action "do nothing".

### Block 0. Setup (before 17:00: 0.3, 0.4 only; 17:00–17:30: 0.1, 0.2)
| # | Task | Owner | Done when |
|---|---|---|---|
| 0.1 | Create `src/isoshift_event/` package, `results/`, `figures/`; disclosure line in README stub | C | committed |
| 0.2 | Pull MP H-compound structures with the API key (all H entries without C, E_hull ≤ 50 meV/atom) to `data/isoshift/mp_h.json` | X | file + count logged |
| 0.3 | Bond: Can enables the Valency connector for Claude on claude.ai, Claude reconnects and runs `list_sources`. Bulk Bond queries still go through Codex (`valency` MCP) to save Claude quota. Log every Bond query to `logs/bond_queries.jsonl` (Valency prize story) | Can, C, X | `list_sources` OK in Claude + one test query logged |
| 0.4 | Laptop power settings for overnight runs | Can | done |

### Block 1. Pools in parallel (17:30–20:00)
| # | Task | Owner | Done when |
|---|---|---|---|
| 1.1 | Validation set: for brucite, ice Ih, LiH/LiD, portlandite Ca(OH)2, AlOOH, KOH, KDP, NH4Cl collect experimental H vs D numbers (lattice/volume isotope effect, transition T/P shifts) with DOIs via Bond + OpenAlex → `data/isoshift/validation.csv` (value, unit, T, P, DOI, harmonic-tractable yes/no) | X (Bond), C reviews | ≥6 cases with DOIs |
| 1.2 | Independent cross-check of every validation row against its DOI (value, unit, sign); disagreements resolved by Claude. Can only sees the final table | G + X via `harness.ask` | all rows confirmed or dropped |
| 1.3 | Pair builder `src/isoshift_event/pairs.py`: merge MP + JARVIS, same composition, different structure (StructureMatcher), ΔE ≤ 25 meV/atom, ≤ 16 atoms (≤ 32 second tier), drop partial occupancy, flag proton-transfer/H-bond-disordered families → `data/isoshift/pairs.csv` | X writes, C reviews | ≥ 100 pairs |
| 1.4 | Fix brucite imaginary modes before trusting QHA: symmetry-constrained relax (FixSymmetry), tighter fmax, check supercell size; same for AlOOH | C | brucite min freq > -0.5 THz in ≥3 models |
| 1.5 | Batch runner `src/isoshift_event/screen.py`: job queue over pairs × models, resumable, per-job JSON in `results/`, OOM retry, writes ΔF_H, ΔF_D, ΔΔF_iso(T), min freq | X writes, C reviews | dry run on 3 pairs |

### Block 2. Validation first (20:00–00:00) → GATE
| # | Task | Owner | Done when |
|---|---|---|---|
| 2.1 | QHA H and D for brucite, portlandite, ice Ih (proton-ordered XI proxy), LiH with 4 MLIPs; volume isotope effect at 0 and 300 K | C runs, GPU | numbers in `results/validation/` |
| 2.2 | Harmonic ΔΔF_iso for negative controls (KDP, KOH, δ-AlOOH, NH4Cl): expect failure or model disagreement; label "outside harmonic validity" | C | table |
| 2.3 | X–H stretch benchmark: MLIP Γ-point H stretch / phonon DOS vs DFT phonons (Togo PhononDB / MDR) for 10 to 20 H compounds | X fetches DFT data, S compares | parity table |
| 2.4 | Review of validation logic and numbers (independent read) | G + X via `harness.ask` | no blocking issue |
| **GATE Thu 00:00** | Three tiers (see Pre-flight decisions P1). **Pass** = tier A all green and tier B brucite + portlandite volume isotope sign right in ≥3/4 models with no unresolved imaginary optical modes → "validated isotope free energies" framing; transition shifts stay labelled exploratory. **Fail** → fallback framing (X–H benchmark + isotope free-energy atlas), screen still runs. Opus decides via board | C (board) | decision in docs/decisions/ |

### Block 3. Overnight screen (00:00–08:00, Can sleeps)
| # | Task | Owner | Done when |
|---|---|---|---|
| 3.1 | Harmonic H/D screen, mace + orb, all pairs (~300 pairs, ~5 h) | GPU, unattended | results cached |
| 3.2 | Queue sevenn + mattersim on pairs where mace and orb agree on sign (auto-chained) | GPU | done by ~08:00 |
| 3.3 | Watchdog: one `ScheduleWakeup`/check every ~60 min that restarts the runner if it died (no other work) | C (cheap) | log clean |

### Block 4. Analysis (08:00–13:00)
| # | Task | Owner | Done when |
|---|---|---|---|
| 4.1 | Ensemble filter: 4/4 sign agreement and |ΔΔF_iso| > ensemble spread; ΔT_iso ≈ ΔΔF_iso / ΔS for pairs with a crossing below 1000 K; rank | C | ranked table |
| 4.2 | QHA on top 10 to 20 | GPU | done |
| 4.3 | Novelty + experimental context for top 10 via Bond (is the polymorph pair known, any deuteride data, feasible D2O/D2 synthesis) | X (Bond) | table with DOIs |
| 4.4 | Main figure (left validation parity, right candidate map) + benchmark figure | S drafts, C checks | PNG/SVG in `figures/` |
| 4.5 | Red team of the claims (overclaim, physics errors) | G + X | fixes applied |

### Block 5. Tool + repo (13:00–17:00)
| # | Task | Owner | Done when |
|---|---|---|---|
| 5.1 | marimo app `app/isoshift_app.py`: CIF/MP id in → H/D free energy vs T for a pair, crossing, ΔT_iso, ensemble band; cached demo pairs so it runs without GPU | X writes, C checks | runs locally |
| 5.2 | README: what/why/results/how to run, prior work vs event work section, Bond and marimo usage | S drafts, C edits | done |
| 5.3 | Create public GitHub repo (Can's go-ahead), push, fresh-clone test | Can approves, S tests | clone runs app |

### Block 6. Write-up + video (17:00–23:00)
| # | Task | Owner | Done when |
|---|---|---|---|
| 6.1 | One-page summary with main figure | C drafts, G reviews, Can approves | final |
| 6.2 | Video script (TR draft + EN final, ≤ 4 min), 5 slides, demo steps | C | Can reads it |
| 6.3 | Rehearse once, record with OBS, captions, upload unlisted YouTube | Can | public link, no login |
| 6.4 | Social post text (if Can wants one) | C | ready |

### Block 7. Submit (23:00–02:00)
| # | Task | Owner | Done when |
|---|---|---|---|
| 7.1 | Moment form: post/video link, write-up + figure, repo link, tick Valency Bond and marimo, prior-work disclosure | Can submits, C prepares text | submitted |
| 7.2 | Final check: links open in incognito, repo README renders | Can | done by 02:00 |

### Pre-flight decisions (Opus, 21 Oct, after independent Astra xhigh + Gemini reviews)
Raw reviews: `docs/preflight/astra.md`, `docs/preflight/gemini.md`. Both flagged the same core risks; these rules are binding for all event work.
* **P1 Gate in three tiers.** A. Implementation sanity (must all pass): equal masses give exactly zero shift; swapping H↔D flips the sign; classical high-T limit of ΔF_iso cancels; LiH absolute ΔZPE(LiH−LiD) per f.u. and Γ optical frequency vs experiment (the D/H ZPE ratio alone is a mass identity, not a test). B. Observable validation: brucite and portlandite QHA volume isotope effect sign in ≥3/4 models. Ice Ih is reported, not gating (anomalous effect, functional sensitive). C. Transition validation: no credible harmonic-tractable experimental transition shift exists, so transition shifts are always labelled exploratory predictions.
* **P2 Imaginary modes.** Never trust a structure with imaginary optical modes. Relax cell + positions together (FrechetCellFilter, fmax 1e-4 eV/Å) without FixSymmetry first; if imaginary modes remain, displace along the eigenvector, re-relax, re-symmetrize with spglib. Structures still unstable are quarantined and listed, never silently dropped or absolute-valued. Small acoustic noise near Γ is tolerated only below a documented threshold.
* **P3 Method contract.** Compute per unique structure (not per pair): relaxed volume, F_vib^H(T), F_vib^D(T), S, min freq, mode-band split (≤1800 cm⁻¹ vs X–H stretch). Pair quantities in post-processing. ΔΔF_iso(T) is the primary, static-energy-independent result. Transition shifts by root-finding T_c separately for H and D on ΔG(T) with a slope guard (|ΔS| ≥ 0.01 meV/atom/K) and a sweep of plausible static ΔE offsets; if T_c is unstable, report ΔΔF_iso only. Also report ΔP_iso(300 K) ≈ −ΔΔF_iso/ΔV. Ambient-pressure T claims capped at 600 K unless literature shows higher stability. Flag "anharmonic-sensitive" when >70% of ΔΔF_iso comes from X–H stretches. QHA: force constants at every volume, bracketed minimum with ≥5 clean volumes, else `qha_invalid`.
* **P4 Numerics.** Same supercell for all models per structure (min length ~9.5 Å, ≤160 atoms), so model spread is not supercell spread. Convergence is checked on ΔΔF_iso, not frequencies. Cell normalisation explicit (meV/atom, meV/H). MACE in float64 where memory allows for validation structures.
* **P5 Pairs.** Distinct structures only: deduplicate before and after MLIP relaxation (pairs that collapse to one phase are dropped). Never subtract MP and JARVIS energies from each other. Keep energy provenance.
* **P6 Reporting.** Ensemble bands are "model spread", not confidence intervals. Keep failures and audit some rejected pairs. Negative controls test stated physics limits; they are not required to fail. Claims cite Bourgeois 2018 and existing MLIP phonon benchmarks; no "first isotope phonon calculation", no "provably".
* **P7 Orchestration trimmed.** One batched mathcheck for all formulas. build: one parallel review round, loop only on failed acceptance or a verified blocking finding. Full board only for imaginary-mode policy if contested, the gate, and final claims. Opus is the only ledger writer and integrator. Reviews are timeboxed (20 min).
* **P8 Provenance.** Tag `pre-event-baseline` on the last pre-event commit before work starts; all event code in `src/` and `app/`.
* **P9 Submission.** Check the Moment "social media post" field before work starts: if an unlisted YouTube link is not accepted, decide on a public post. Internal target: submitted by 00:30, hard stop 02:00.

### Cut list if behind (in order)
1. QHA on top candidates → harmonic only with stated caveat. 2. mattersim from the screen. 3. ≤ 32-atom second tier. 4. App upload widget → cached demo only. Never cut: validation table, negative controls, honest disclosure.

## Main figure (draft)
Left: validation (computed vs measured isotope shift for known cases, negative controls marked). Right: candidate map (polymorph gap vs ΔΔF_iso, ensemble error bars, top candidates labelled).

## Video outline (≤4 min)
Publishing: default is an unlisted YouTube video (no face, screen only) whose link goes in the Moment form; Can does not want to post it on LinkedIn/X for now and may decide later.
Format (Can's choice): screen recording with OBS, Can narrates in his own voice. Claude prepares the script (Turkish draft + English final), slides/figures and demo steps beforehand; one rehearsal, then record.
1. Hook (20 s): "Swap H for D and a crystal can choose a different structure. Where does that happen?"
2. Why it's hard (30 s): effect is meV, model errors are larger; trick: isotope shift from mass-independent force constants, ensemble of AI potentials.
3. Validation (60 s): known cases reproduced, negative controls honestly flagged.
4. Discovery (60 s): top isotope-tunable candidates, predicted transition shifts with error bars, cheap D2O experiments to test.
5. Tool demo (40 s): marimo app.
6. Close (10 s): open code, what's next.

## Disclosure for the form
Organizer guidance (Slack #2026-event, 18 Oct): pre-existing code/datasets are allowed but must be explicitly stated; judging is based on what was implemented during the hackathon. So the write-up must clearly separate pre-event infrastructure from event work.
Before event: generic LLM harness (harness/), topic harness (isoshift/: MLIP calculators, phonon mass override, QHA, comparison utilities), environment, feasibility tests, brainstorm docs. During event: candidate curation, validation, screening, analysis, app, write-up.
