export const meta = {
  name: 'board',
  description: 'Advisory board (Opus xhigh chair, Astra xhigh, Gemini 4 Argon) answers a hard decision blind, chair writes docs/decisions',
  whenToUse: 'Hard physics, architecture, gate or claim decisions in IsoShift. args: {id, topic, question, evidence: [repo-relative paths], options?: [..]}',
  phases: [
    { title: 'Members', detail: 'three blind answers' },
    { title: 'Chair', detail: 'Opus xhigh decides and writes the record' },
  ],
}

const REPO = 'C:/Users/can02/Projects/osi-hackathon-2026'
const PY = `${REPO}/.venv/Scripts/python.exe`
const a = args || {}
if (!a.id || !a.question) throw new Error('board needs args.id and args.question')
const evidence = (a.evidence || []).join(', ') || '(none)'
const options = a.options ? `\nOptions under consideration: ${a.options.join(' | ')}` : ''

const MEMBER = {
  type: 'object',
  properties: {
    decision: { type: 'string' },
    rationale: { type: 'string' },
    key_numbers: { type: 'array', items: { type: 'string' } },
    risks: { type: 'array', items: { type: 'string' } },
    would_change_my_mind: { type: 'string' },
    confidence: { type: 'number' },
  },
  required: ['decision', 'rationale', 'risks', 'confidence'],
}

const brief = `You sit on the advisory board of IsoShift (H/D isotope shifts of polymorph transitions in inorganic hydrogen compounds, universal MLIP ensemble + harmonic/QHA free energies, hackathon deadline Fri 23 Oct 02:00 Turkey time).
Decision ${a.id}: ${a.topic || ''}
Question: ${a.question}${options}
Evidence files (repo ${REPO}): ${evidence}
Answer independently. Be concrete and quantitative, check units and signs, say what would change your mind. Answer in English.`

// External members run through harness.cli; the runner inlines the evidence so the model needs no file access.
const external = (model, effort) => agent(
  `Run one advisory-board member through the model CLI and return its answer as structured data.
1. Read these evidence files from ${REPO}: ${evidence}. Build a prompt file in the scratchpad: the brief below, then each evidence file under a "### <path>" heading (truncate any single file to 12000 chars and say so).
2. Ask for the answer as JSON with keys decision, rationale, key_numbers (list), risks (list), would_change_my_mind, confidence (0..1).
3. Run: "${PY}" -m harness.cli --model ${model}${effort ? ` --effort ${effort}` : ''} --timeout 2400 --prompt-file <file> --out <reply file>  (working dir ${REPO}).
4. Return the member's answer faithfully in the schema. Do not add your own opinion. If the call fails twice, return decision "NO ANSWER" with the error as rationale and confidence 0.
BRIEF:
${brief}`,
  { label: `member:${model}`, phase: 'Members', schema: MEMBER, model: 'haiku', effort: 'low' })

phase('Members')
const [opus, astra, gemini] = await parallel([
  () => agent(`${brief}\nRead the evidence files yourself. Run small Python checks with ${PY} if a number needs verifying.`,
    { label: 'member:opus', phase: 'Members', schema: MEMBER, model: 'opus', effort: (args && args.effort) || 'xhigh' }),
  () => external('gpt-6-astra', 'xhigh'),
  () => external('gemini-4-argon', null),
])

phase('Chair')
const members = { opus, astra, gemini }
const record = await agent(
  `You chair the IsoShift advisory board and hold final authority. Decide ${a.id}.
Question: ${a.question}${options}
Evidence files: ${evidence}
Member answers (blind, independent):
${JSON.stringify(members, null, 2)}
Weigh arguments, not votes. Astra is the strongest member on physics and math; Gemini is consultative. Re-check any number the decision depends on (Python at ${PY} if needed).
Write ${REPO}/docs/decisions/${a.id}.md with: Decision, Why, Member positions (one line each), Dissent, What would change this, Follow-up tasks. Then return the schema.`,
  {
    label: 'chair', phase: 'Chair', model: 'opus', effort: (args && args.effort) || 'xhigh',
    schema: {
      type: 'object',
      properties: {
        decision: { type: 'string' },
        followups: { type: 'array', items: { type: 'string' } },
        unanimous: { type: 'boolean' },
        record_path: { type: 'string' },
      },
      required: ['decision', 'followups', 'unanimous', 'record_path'],
    },
  })
return { id: a.id, record, members }
