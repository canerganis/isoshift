export const meta = {
  name: 'council',
  description: 'Council (Opus high, Astra high, Gemini 4 Argon high): blind answers, then a deliberation round where members read and answer each other, then the chair writes an actionable decision',
  whenToUse: 'When the conductor is stuck on a science or claim question (Can, 21 Oct). args: {id, topic, question, evidence: [repo-relative paths], options?: [..]}',
  phases: [
    { title: 'Round 1', detail: 'blind, independent answers' },
    { title: 'Round 2', detail: 'each member reads the others and responds' },
    { title: 'Chair', detail: 'decision and action list' },
  ],
}

const REPO = 'C:/Users/can02/Projects/osi-hackathon-2026'
const PY = `${REPO}/.venv/Scripts/python.exe`
const a = args || {}
if (!a.id || !a.question) throw new Error('council needs args.id and args.question')
const evidence = (a.evidence || []).join(', ') || '(none)'
const options = a.options ? `\nOptions under consideration: ${a.options.join(' | ')}` : ''

const ANSWER = {
  type: 'object',
  properties: {
    position: { type: 'string' },
    rationale: { type: 'string' },
    key_numbers: { type: 'array', items: { type: 'string' } },
    proposed_actions: { type: 'array', items: { type: 'string' }, description: 'concrete steps that can be run in the remaining hackathon time' },
    risks: { type: 'array', items: { type: 'string' } },
    questions_for_others: { type: 'array', items: { type: 'string' } },
    changed_my_mind: { type: 'string', description: 'round 2 only: what changed after reading the others, or "nothing" and why' },
    confidence: { type: 'number' },
  },
  required: ['position', 'rationale', 'proposed_actions', 'confidence'],
}

const brief = `You are on the IsoShift science council (H/D isotope effects on polymorph stability of inorganic hydrogen compounds, universal ML-potential ensemble with harmonic/QHA free energies; hackathon, submission Fri 23 Oct 00:30 Turkey time, compute freeze Thu 12:00). The team goal is a real, defensible scientific discovery (state/GOAL.md).
Item ${a.id}: ${a.topic || ''}
Question: ${a.question}${options}
Evidence files (repo ${REPO}): ${evidence}
Be concrete and quantitative, check units and signs, separate what the data show from what you infer, and propose actions that fit the remaining time. Answer in English.`

const SCHEMA_TEXT = 'JSON with keys position, rationale, key_numbers (list), proposed_actions (list), risks (list), questions_for_others (list), changed_my_mind, confidence (0..1)'

const external = (model, effort, label, prompt, phaseName) => agent(
  `Run one council member through the model CLI and return its answer as structured data.
1. Read these evidence files from ${REPO}: ${evidence}. Write a prompt file in the scratchpad: the text between PROMPT START and PROMPT END below, then each evidence file under a "### <path>" heading (truncate any single file to 12000 chars and say so).
2. Ask for the answer as ${SCHEMA_TEXT}.
3. Run: "${PY}" -m harness.cli --model ${model}${effort ? ` --effort ${effort}` : ''} --timeout 2400 --prompt-file <file> --out <reply file>  (working dir ${REPO}).
4. Return the member's answer faithfully in the schema. Do not add your own opinion. If the call fails twice, return position "NO ANSWER" with the error as rationale and confidence 0.
PROMPT START
${prompt}
PROMPT END`,
  { label, phase: phaseName, schema: ANSWER, model: 'haiku', effort: 'low' })

const opusAgent = (prompt, label, phaseName) => agent(
  `${prompt}\nRead the evidence files yourself. Run small Python checks with ${PY} if a number needs verifying.`,
  { label, phase: phaseName, schema: ANSWER, model: 'opus', effort: 'high' })

phase('Round 1')
const r1 = await parallel([
  () => opusAgent(brief, 'r1:opus', 'Round 1'),
  () => external('gpt-6-astra', 'high', 'r1:astra', brief, 'Round 1'),
  () => external('gemini-4-argon', null, 'r1:argon', brief, 'Round 1'),
])
const names = ['opus', 'astra', 'argon']
const round1 = Object.fromEntries(names.map((n, i) => [n, r1[i]]))

phase('Round 2')
const r2prompt = me => `${brief}

This is round 2 of the council. You are ${me}. Your round 1 answer and the other members' round 1 answers are below. Read them, answer their questions_for_others addressed to you or to everyone, say where you agree, push back with numbers where you disagree, and give your updated position. Fill changed_my_mind.
${JSON.stringify(round1, null, 2)}`
const r2 = await parallel([
  () => opusAgent(r2prompt('opus'), 'r2:opus', 'Round 2'),
  () => external('gpt-6-astra', 'high', 'r2:astra', r2prompt('astra'), 'Round 2'),
  () => external('gemini-4-argon', null, 'r2:argon', r2prompt('argon'), 'Round 2'),
])
const round2 = Object.fromEntries(names.map((n, i) => [n, r2[i]]))

phase('Chair')
const record = await agent(
  `You chair the IsoShift science council and the conductor will implement your decision. Decide ${a.id}.
Question: ${a.question}${options}
Evidence files: ${evidence}
Round 1 (blind): ${JSON.stringify(round1, null, 2)}
Round 2 (after reading each other): ${JSON.stringify(round2, null, 2)}
Weigh arguments, not votes; Astra is strongest on physics and math, Gemini is consultative. Re-check any number the decision depends on (Python at ${PY}).
Write ${REPO}/docs/decisions/${a.id}.md with: Decision; Why; Where the members converged; Remaining disagreement; Ordered action list for the conductor (each with owner, time estimate and a done-check); What would change this. Then return the schema.`,
  {
    label: 'chair', phase: 'Chair', model: 'opus', effort: 'high',
    schema: {
      type: 'object',
      properties: {
        decision: { type: 'string' },
        actions: { type: 'array', items: { type: 'string' } },
        converged: { type: 'boolean' },
        record_path: { type: 'string' },
      },
      required: ['decision', 'actions', 'converged', 'record_path'],
    },
  })
return { id: a.id, record, round1, round2 }
