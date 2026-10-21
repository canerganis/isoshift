export const meta = {
  name: 'mathcheck',
  description: 'Two independent derivations (Astra xhigh, Opus high), numeric cross-check, reconcile once, else escalate to the board',
  whenToUse: 'Any formula before it goes into IsoShift code. args: {id, task, test_case?}',
  phases: [
    { title: 'Derive', detail: 'Astra and Opus derive blind' },
    { title: 'Check', detail: 'numeric comparison' },
    { title: 'Reconcile', detail: 'one round if they disagree' },
  ],
}

const REPO = 'C:/Users/can02/Projects/osi-hackathon-2026'
const PY = `${REPO}/.venv/Scripts/python.exe`
const a = args || {}
if (!a.id || !a.task) throw new Error('mathcheck needs args.id and args.task')

const DERIVATION = {
  type: 'object',
  properties: {
    formula: { type: 'string' },
    assumptions: { type: 'array', items: { type: 'string' } },
    units: { type: 'string' },
    limiting_cases: { type: 'array', items: { type: 'string' } },
    python_function: { type: 'string', description: 'self-contained Python def implementing the formula' },
    test_case: { type: 'string', description: 'inputs and expected output' },
  },
  required: ['formula', 'assumptions', 'units', 'python_function', 'test_case'],
}
const task = `Derive for IsoShift (H/D isotope effects in solids from mass-independent force constants, harmonic and quasi-harmonic free energies).
Task ${a.id}: ${a.task}
${a.test_case ? `Use this test case: ${a.test_case}` : 'Choose one realistic numeric test case.'}
Give: formula, assumptions, units (state eV, meV/atom, K, THz conventions explicitly), limiting cases, a self-contained Python function, and the test case with its expected output. Answer in English.`

const astraDerive = (extra) => agent(
  `Run gpt-6-astra through the model CLI and return its derivation in the schema, faithfully, without adding your own math.
Write this prompt to a scratchpad file, asking for JSON with keys formula, assumptions, units, limiting_cases, python_function, test_case:
---
${task}${extra || ''}
---
Run: "${PY}" -m harness.cli --model gpt-6-astra --effort xhigh --timeout 2400 --prompt-file <file> --out <reply>  (working dir ${REPO}). Retry once on error.`,
  { label: 'derive:astra', phase: 'Derive', schema: DERIVATION, model: 'haiku', effort: 'low' })

const opusDerive = (extra) => agent(`${task}${extra || ''}`,
  { label: 'derive:opus', phase: 'Derive', schema: DERIVATION, model: 'opus', effort: 'high' })

const VERDICT = {
  type: 'object',
  properties: {
    agree: { type: 'boolean' },
    astra_value: { type: 'string' },
    opus_value: { type: 'string' },
    differences: { type: 'array', items: { type: 'string' } },
  },
  required: ['agree', 'differences'],
}
const compare = (x, y, round) => agent(
  `Compare two independent derivations numerically. Put both python functions in one scratch script, run both on BOTH test cases with ${PY}, and report whether they agree (relative difference < 1e-3, or identical sign and same formula up to notation where a test is not comparable). List every substantive difference (assumption, unit, factor, sign).
A (Astra): ${JSON.stringify(x)}
B (Opus): ${JSON.stringify(y)}`,
  { label: `compare:r${round}`, phase: 'Check', schema: VERDICT, model: 'sonnet', effort: 'medium' })

phase('Derive')
let [x, y] = await parallel([() => astraDerive(), () => opusDerive()])
if (!x || !y) return { id: a.id, status: 'error', astra: x, opus: y }
phase('Check')
let v = await compare(x, y, 1)

if (!v.agree) {
  phase('Reconcile')
  const note = (other) => `\n\nAn independent derivation disagrees with yours on: ${v.differences.join('; ')}.\nOther derivation: ${JSON.stringify(other)}\nRe-derive carefully; keep your answer if you are right and say why, or correct it.`;
  [x, y] = await parallel([() => astraDerive(note(y)), () => opusDerive(note(x))])
  v = await compare(x, y, 2)
}

const status = v.agree ? 'accepted' : 'escalate-to-board'
await agent(
  `Write ${REPO}/docs/math/${a.id}.md: task, status "${status}", the accepted formula (or both if escalated), assumptions, units, limiting cases, test case with both numeric results, the Python function, and the differences list. Source data:
${JSON.stringify({ task: a.task, astra: x, opus: y, verdict: v })}`,
  { label: 'record', phase: 'Check', model: 'haiku', effort: 'low' })
return { id: a.id, status, formula: v.agree ? y.formula : null, verdict: v, astra: x, opus: y }
