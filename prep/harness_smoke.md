# Harness live smoke test

Run: 2026-10-20 23:54:45

| model | tiny latency (s) | tiny ok | ~2k-token latency (s) | big ok | big prompt chars | errors |
|---|---|---|---|---|---|---|
| gpt-6-astra | 15.941 | True | 9.711 | True | 9325 | none |
| gemini-4-argon | 11.111 | True | 13.554 | True | 9325 | none |
| opus-5.5 | 12.607 | True | 8.942 | True | 9325 | none |

## Raw replies

### gpt-6-astra
tiny:
```
{"ok": true, "model": "gpt-6-astra"}
```
big:
```
{"ok": true, "words_seen": "many"}
```

### gemini-4-argon
tiny:
```
{"ok": true, "model": "gemini-4-argon"}
```
big:
```
{"ok": true, "words_seen": "many"}
```

### opus-5.5
tiny:
```
{"ok": true, "model": "opus-5.5"}
```
big:
```
{"ok": true, "words_seen": "many"}
```

## CLI quirks

* agy `-p` takes no stdin and must be written `-p=<prompt>` (otherwise it swallows the next flag as the prompt). Prompts are passed in argv (Windows limit about 32k chars; harness caps at 30k).
* Longer prompts via a temp file: gemini-4-argon reads it fine, opus-5.5 fails headless ("command permission auto-denied", empty output). Tested: 27k chars in argv works on opus (7.3 s); 32k chars via file fails on opus, works on gemini (14 s).
* codex exec reads the prompt on stdin and writes the final message to the -o file cleanly; no auth errors or rate limits seen.
* Parallel run_many (2 per model, 4 calls over opus and gpt) finished in about 11 s total, no throttling.
* Latency is dominated by fixed startup, about 8 to 16 s per call regardless of a ~2k-token prompt.
