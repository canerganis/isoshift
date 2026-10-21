export const meta = {
  name: 'build',
  description: 'Spec (Opus) -> implement (Codex Astra) -> acceptance (Sonnet) -> physics + architecture review (Astra, Opus) -> fix loop -> Opus takeover -> commit',
  whenToUse: 'Every IsoShift code module. args: {id, goal, files: [owned repo-relative paths], acceptance: "shell command run from repo root", spec_path?, context?: [paths]}',
  phases: [
    { title: 'Spec' },
    { title: 'Implement' },
    { title: 'Accept' },
    { title: 'Review' },
    { title: 'Fix' },
    { title: 'Commit' },
  ],
}

const REPO = 'C:/Users/can02/Projects/osi-hackathon-2026'
const PY = `${REPO}/.venv/Scripts/python.exe`
const a = args || {}
if (!a.id || !a.goal || !a.files || !a.acceptance) throw new Error('build needs id, goal, files, acceptance')
const owned = a.files.join(', ')
const ctx = (a.context || []).join(', ') || '(none)'
const specPath = a.spec_path || `docs/specs/${a.id}.md`

phase('Spec')
if (!a.spec_path) {
  await agent(
    `Write the implementation spec for IsoShift module ${a.id} to ${REPO}/${specPath}.
Goal: ${a.goal}
Owned files (the only files the implementer may create or edit): ${owned}
Context files to read first: ${ctx}, plus isoshift/ (pre-event harness: calculators, relax, phonons with mass override, qha, worker, cache) and docs/math/ (accepted formulas: use them, do not re-derive).
Acceptance command: ${a.acceptance}
Spec must contain: public interface (signatures), data formats (file paths, JSON/CSV columns with units), algorithm steps, error handling, what to cache, the unit tests to write, and how acceptance is judged. Keep it under 150 lines. Prefer reusing isoshift/ functions over new physics code.`,
    { label: 'spec', phase: 'Spec', model: 'opus', effort: 'high' })
}

const RUN = {
  type: 'object',
  properties: { ok: { type: 'boolean' }, summary: { type: 'string' }, output_tail: { type: 'string' } },
  required: ['ok', 'summary'],
}
const codex = (instruction, label) => agent(
  `Run Codex (gpt-6-astra) as the implementer and report what happened. Do not write code yourself.
Write this instruction to a scratchpad prompt file:
---
You are implementing part of IsoShift in the repo at ${REPO}. Read ${specPath} first.
${instruction}
Edit ONLY these files: ${owned}. Do not touch any other file, do not commit, do not print secrets from .env.
Use ${PY} for Python (sevenn/mattersim jobs go through isoshift.worker.run_job). Run the unit tests you write and fix failures before stopping.
---
Then run from ${REPO}: codex exec --skip-git-repo-check -s workspace-write -m gpt-6-astra -c model_reasoning_effort=high -o <scratch reply file> - < <prompt file>
(allow up to 40 minutes; run it in the background and wait for it if your shell times out). Afterwards run \`git status --short\` and report any changed file outside the owned list.
Return ok=true if Codex finished without error, a summary of its reply, and the git status tail.`,
  { label, phase: label.startsWith('fix') ? 'Fix' : 'Implement', schema: RUN, model: 'sonnet', effort: 'low' })

const accept = (round) => agent(
  `From ${REPO} run the unit tests for ${owned} (pytest on the matching tests) and then the acceptance command:
${a.acceptance}
Judge against the acceptance section of ${specPath}. Return ok=true only if tests pass AND acceptance is met; put the decisive output lines in output_tail (max 60 lines).`,
  { label: `accept:r${round}`, phase: 'Accept', schema: RUN, model: 'sonnet', effort: 'medium' })

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' }, line: { type: 'number' },
          severity: { type: 'string', enum: ['blocking', 'minor'] },
          issue: { type: 'string' }, fix: { type: 'string' },
        },
        required: ['file', 'severity', 'issue'],
      },
    },
  },
  required: ['findings'],
}
const review = () => parallel([
  () => agent(
    `Get a physics and math review from gpt-6-astra. Build a prompt file with: the spec ${specPath}, the full content of ${owned}, and the relevant docs/math/ files; ask Astra to review for physics/math errors only (units, signs, mass handling for H/D, free-energy formulas, numerical stability, phonon/QHA misuse) and to answer as JSON {"findings":[{"file","line","severity":"blocking"|"minor","issue","fix"}]}. Run "${PY}" -m harness.cli --model gpt-6-astra --effort xhigh --timeout 2400 --prompt-file <file> --out <reply> from ${REPO}. Return Astra's findings faithfully.`,
    { label: 'review:astra', phase: 'Review', schema: FINDINGS, model: 'haiku', effort: 'low' }),
  () => agent(
    `Review ${owned} against ${specPath} for architecture, correctness, edge cases (missing structures, imaginary modes, OOM, resumability, partial results) and test quality. Run code if useful. Only report real problems; mark blocking only if it would give wrong results or break the pipeline.`,
    { label: 'review:opus', phase: 'Review', schema: FINDINGS, model: 'opus', effort: 'high' }),
]).then(rs => rs.filter(Boolean).flatMap(r => r.findings))

phase('Implement')
await codex(`Implement the module and its unit tests as specified.`, 'implement')

let acc = await accept(1)
let blocking = []
let round = 1
while (true) {
  phase('Review')
  const found = await review()
  blocking = found.filter(f => f.severity === 'blocking')
  log(`round ${round}: acceptance ${acc.ok ? 'pass' : 'FAIL'}, ${blocking.length} blocking, ${found.length - blocking.length} minor`)
  if (acc.ok && blocking.length === 0) break
  if (round >= 3) break
  phase('Fix')
  const todo = `Acceptance ${acc.ok ? 'passed' : 'FAILED'}: ${acc.summary}\n${acc.output_tail || ''}\nBlocking review findings:\n${JSON.stringify(blocking, null, 1)}\nFix all of them.`
  if (round < 2) {
    await codex(todo, `fix:codex:r${round}`)
  } else {
    // Escalation: Opus takes the hard part itself.
    await agent(`You are taking over module ${a.id} after Codex could not close these issues. Read ${specPath} and ${owned}, fix the problems directly (edit only ${owned}), run the tests.\n${todo}`,
      { label: `fix:opus:r${round}`, phase: 'Fix', model: 'opus', effort: 'high' })
  }
  round++
  acc = await accept(round)
}

const done = acc.ok && blocking.length === 0
phase('Commit')
if (done) {
  await agent(`In ${REPO}: git add ${a.files.map(f => `"${f}"`).join(' ')} "${specPath}" plus any new test files for this module, then commit with message "src: ${a.id}" followed by a blank line and "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". Commit nothing else. Return the commit hash.`,
    { label: 'commit', phase: 'Commit', model: 'haiku', effort: 'low' })
}
return { id: a.id, status: done ? 'done' : 'needs-conductor', rounds: round, acceptance: acc, open_blocking: blocking }
