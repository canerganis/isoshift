# harness

Generic, topic-agnostic infrastructure: LLM CLI wrapper, parallel runner, literature client.

## Provenance

Prepared before the event (night of 2026-10-20/21, before the 4th Open Scientific Intelligence Hackathon kickoff). It contains no project-specific logic. All topic-specific code is written after kickoff.

## Setup

```
C:\Users\can02\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest            # unit tests (+ one live OpenAlex call)
.venv\Scripts\python.exe -m harness.smoke     # live model smoke test -> prep/harness_smoke.md
```

## LLM

```python
from harness import ask, ask_json
r = ask("opus-5.5", "Say hi", system=None, json_schema=None, timeout=600, cache=True)
r.text, r.model, r.latency_s, r.cached, r.prompt_hash, r.error   # r.ok is True when error is None

class Verdict(BaseModel): label: str; confidence: float
obj, r = ask_json("gpt-6-astra", "Classify ...", Verdict)          # pydantic class or JSON-schema dict
```

Models: `gpt-6-astra` (codex exec, prompt on stdin), `gemini-4-argon` and `opus-5.5` (agy, high effort).
`ask(..., effort="xhigh")` sets codex reasoning effort (low/medium/high/xhigh); ignored for agy models.

Shell entry for agents: `python -m harness.cli --model gpt-6-astra --effort xhigh --prompt-file p.md --out reply.md`.

* `ask` never raises on CLI failure: check `r.error`. Errors are not cached.
* Cache: `.cache/llm/<sha256(model, system, prompt, schema)>.json` (holds the full prompt and reply). Call log: `logs/llm_calls.jsonl` (model, hash, latency, ok, cached, error, timestamp). Both are gitignored.
* `ask_json` extracts raw or fenced JSON (or a JSON value embedded in prose), validates, and re-asks once with the error on failure.
* agy has no stdin mode: prompts up to 30,000 chars go in argv. Longer prompts are written to a temp file and the model is asked to read it, which works for gemini but opus-5.5 is denied the shell tool in headless mode and errors out. Keep opus prompts under 30k chars.

## Parallel

```python
from harness.parallel import run_many
results = run_many([{"model": "opus-5.5", "prompt": p} for p in prompts], max_per_model=2, retries=3)
```

Per-model semaphore (int or dict), tenacity exponential backoff on failed calls, tqdm progress, results in input order.

## Literature

```python
from harness.literature import OpenAlexSource
papers = OpenAlexSource().search("query", year_from=2024, year_to=2026, limit=25,
                                 extra_filter="cited_by_count:>5", sort="cited_by_count:desc")
```

Returns `Paper(id, doi, title, year, abstract, cited_by_count)`. Abstracts are rebuilt from `abstract_inverted_index`. Rate limited, disk cached in `.cache/openalex/`, no email sent. To add another backend (for example Valency MCP Bond), subclass `LiteratureSource` (`ValencyBondSource` is a stub).
