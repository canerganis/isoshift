export const meta = {
  name: 'sweep',
  description: 'Pipeline a task over many items with Haiku or Sonnet workers, structured rows, then a completeness critic',
  whenToUse: 'Fetches, scans, literature/Bond batches. args: {id, task, items: [..], worker: "haiku"|"sonnet", out: repo-relative JSONL path, row_schema?: {...}}',
  phases: [
    { title: 'Work' },
    { title: 'Critic' },
  ],
}

const REPO = 'C:/Users/can02/Projects/osi-hackathon-2026'
const a = args || {}
if (!a.id || !a.task || !a.items) throw new Error('sweep needs id, task, items')
const ROW = a.row_schema || {
  type: 'object',
  properties: {
    item: { type: 'string' },
    status: { type: 'string', enum: ['ok', 'not_found', 'error'] },
    data: { type: 'object' },
    sources: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
  required: ['item', 'status'],
}

phase('Work')
const rows = await pipeline(a.items,
  (item, _o, i) => agent(
    `${a.task}\nItem: ${typeof item === 'string' ? item : JSON.stringify(item)}\nRepo: ${REPO}. Cite sources (DOI or URL) for every number. If you use the Valency Bond MCP, append one line per query to ${REPO}/logs/bond_queries.jsonl: {"sweep":"${a.id}","query":...,"n_results":...}.`,
    { label: `${a.id}:${i}`, phase: 'Work', schema: ROW, model: a.worker || 'sonnet', effort: a.worker === 'haiku' ? 'low' : 'medium' }))

const good = rows.filter(Boolean)
log(`${good.length}/${a.items.length} rows returned, ${good.filter(r => r.status === 'ok').length} ok`)

phase('Critic')
const critic = await agent(
  `Completeness critic for sweep ${a.id}. Task: ${a.task}
Rows: ${JSON.stringify(good).slice(0, 60000)}
Write all rows as JSONL to ${REPO}/${a.out || `state/sweeps/${a.id}.jsonl`}. Then list: items missing or failed, numbers without a source, inconsistent units, and anything the task asked for that no row covers. Return that list.`,
  {
    label: 'critic', phase: 'Critic', model: 'sonnet', effort: 'medium',
    schema: { type: 'object', properties: { gaps: { type: 'array', items: { type: 'string' } }, written: { type: 'string' } }, required: ['gaps', 'written'] },
  })
return { id: a.id, n: a.items.length, ok: good.filter(r => r.status === 'ok').length, gaps: critic.gaps, path: critic.written }
