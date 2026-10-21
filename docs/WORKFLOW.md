# IsoShift orchestration design

Goal (Can, 21 Oct): one end-to-end flow that runs from 17:00 to submission without tasks left half done, and where every math and architecture decision is checked before it is used.

## Why not one giant workflow
A single workflow cannot sleep through 8 hours of GPU work, and one crash would lose the whole run. So the flow is a **chain of phase workflows** around two long-lived pieces:
1. **GPU queue** (`src/isoshift_event/screen.py`, background process): the only thing that touches the GPU. Jobs are files in `results/queue/`, results are JSON in `results/`. Resumable: a job is done when its result file exists.
2. **State ledger** (`state/ledger.json` + `state/LEDGER.md`): every task with status (todo, running, verify, done, failed), owner, effort, inputs, outputs, acceptance check, attempts. Every workflow reads it at start and writes it at the end. Any crash restarts from the ledger.

Opus (this session) is the conductor: starts each phase workflow, reads its result, updates the ledger, commits, and starts the next one. Phases overlap (see "Not linear" in PLAN.md).

## Reusable building blocks (sub-workflows)

### `board(question, evidence)`: hard decisions
* Members in parallel, blind to each other: Opus max agent, Astra xhigh (`codex exec -m gpt-6-astra -c model_reasoning_effort=xhigh`, called by a Haiku runner), Gemini 4 Argon high (`harness.ask`, Haiku runner).
* Each returns `{decision, rationale, key_numbers, risks, confidence}`.
* Chair (Opus max) reads all three, writes `docs/decisions/NN-topic.md` with the decision, dissent and what would change it.
* Used for: brucite / imaginary modes, gate, ΔT_iso method and ranking, fallback switch, headline and final claims.

### `mathcheck(derivation_task)`: every formula before it goes into code
1. Astra xhigh derives (formula, assumptions, units, limiting cases, a numeric test case).
2. Opus high derives independently without seeing Astra's answer.
3. A Haiku runner evaluates both on the numeric test case in Python.
4. Agree → accepted into `docs/math/`. Disagree → both see each other's work for one reconcile round. Still disagree → board.
* Used for: harmonic and QHA free energy with mass override, ΔT_iso ≈ ΔΔF_iso / ΔS and its error, volume isotope effect, ensemble uncertainty, ZPE ratio expectation.

### `build(module_spec)`: every code module
1. Opus high writes the spec (interface, inputs, outputs, acceptance tests) unless trivial.
2. Codex (Astra high, `workspace-write`, only its own files) implements with tests.
3. Sonnet runs tests and the acceptance check on real data.
4. Review in parallel: Astra (physics/maths correctness) and Opus high (architecture, edge cases). Each finding is verified by a second reader before it counts.
5. Fix loop up to 2 rounds; then Opus takes the hard part itself. Never mark done without the acceptance check passing.
6. Commit per module.

### `sweep(items, task)`: scans and fetches
Haiku for fetching and file/log scanning, Sonnet for literature and Bond batches, pipeline over items, schema output, a completeness critic at the end that lists what was missed or dropped (no silent caps).

## Phase workflows
| WF | Starts | Contents | Exit check |
|---|---|---|---|
| WF0 Bootstrap | 17:00 | ledger + `src/` scaffold, MP fetch (sweep), Bond connector check | ledger exists, MP count logged |
| WF1 Foundations | ~17:30 | mathcheck(all formulas); build(pairs, screen, validation-runner); sweep(validation literature via Bond, row-by-row DOI check); sweep(DFT phonons for benchmark); board(brucite fix) | 3 modules pass acceptance, validation.csv ≥ 6 rows verified |
| WF2 Validation + gate | when runner passes | GPU validation jobs; benchmark parity; independent reading of results by Astra and Gemini; board(gate) | decision file written |
| GPU overnight | after gate (screen may start earlier) | queue runs; Haiku watchdog every ~60 min via cron restarts the queue if dead and logs progress | queue drained or near |
| WF3 Analysis | ~08:00 | mathcheck(ranking statistics); build(analysis); QHA on top 10 to 20; sweep(Bond novelty per candidate); board(ranking + headline); figures | top-10 table, main figure |
| WF4 Product | from the evening, finished ~13:00 to 17:00 | build(marimo app), README, fresh-clone test, secret scan | clone runs app |
| WF5 Story | drafts overnight, final 17:00 | write-up, video script + slides; adversarial red team (3 refuters per claim, claim survives only if ≥2 fail to refute); board(final claims) | Can records video |
| WF6 Submit | 23:00 | form text, link check in incognito, disclosure | Can submits by 02:00 |

## Authority and consultation
* Can (21 Oct): Opus (this session) holds final decision authority and full control over all agents; Can is not in the loop for technical decisions.
* Gemini 4 Argon is consulted at every phase exit (WF1 to WF5): a short "what is wrong or missing here" read of the phase output, in addition to its board seat. Findings go through the same verify step as other reviews.

## Delegation between strong models (Can, 21 Oct)
When Opus and Astra give each other work, the brief states the problem, why it matters, the limits and constraints, the acceptance check, and the progress already made. It never says how to do it. Prescriptive step lists are only for Sonnet/Haiku workers doing mechanical tasks.

## Never-half-done rules
* A task is only `done` when its acceptance check ran and passed; the check is written before the work starts.
* Every workflow is resumable (`resumeFromRunId`), every module commit is atomic, the GPU queue is idempotent.
* Fail twice → escalate one level (Codex → Opus → board). Board says stuck → cut list in PLAN.md, logged, never silently dropped.
* Opus checkpoints after every workflow: ledger updated, commit, short note in `state/LEDGER.md`. Can gets a push notification only at the gate, in the morning and when his action is needed.
