# Spec: pool-persistent-gpu-worker

Goal: a file-queue worker pool so the overnight screen pays Python import (~18 s) and model load (MACE ~17 s, ORB ~4 s) once per worker, not once per 3 to 14 s harmonic job. No new physics: jobs run `isoshift.worker.harmonic_job` / `qha_job` unchanged except for an injected calculator.
Owned files: `isoshift/pool.py`, `isoshift/worker.py`, `tests/test_pool.py`. Nothing else is edited (not `cache.py`, `phonons.py`, `calculators.py`).

## 1. worker.py refactor (minimal)
- `harmonic_job(cif, calc_name, device="cuda", ..., steps=500, calc=None)` and `qha_job(cif, calc_name, device="cuda", calc=None, **kw)`.
- Body: `calc = calc if calc is not None else get_calculator(calc_name, device)`. Everything else identical.
- `qha_job`: replace `kw.setdefault("max_atoms", MAX_ATOMS[calc_name])` with `if "max_atoms" not in kw: kw["max_atoms"] = MAX_ATOMS[calc_name]` (setdefault evaluates the lookup eagerly; tests use a non-MLIP calc name).
- `run_job`, `_subprocess`, `main` unchanged. Existing callers pass no `calc`, so behaviour is unchanged.

## 2. Public interface (isoshift/pool.py)
```python
QUEUE_STATES = ("pending", "running", "done", "failed")
HEARTBEAT_S = 30.0; STALE_S = 600.0; MAX_ATTEMPTS = 3; MIN_SHRINK_ATOMS = 50
def submit(queue_dir, kind, cif, calc, out, **kw) -> str | None
def serve(calc_name, queue_dir, device="cuda", idle_exit_s=600.0, poll_s=2.0, mem_fraction=None,
          cache_root=None, worker_id=None, loader=None) -> dict      # returns final heartbeat dict
def launch(calc_name, queue_dir, device="cuda", idle_exit_s=600.0, mem_fraction=None, cache_root=None) -> int  # pid
def requeue_stale(queue_dir, max_age_s=STALE_S) -> list[str]        # requeued job ids
def status(queue_dir) -> dict                                       # counts + heartbeats
def launch_cmd(calc_name, queue_dir, **opts) -> list[str]           # pure, testable
def main(argv=None)                                                 # CLI
```
`loader` (test hook): callable `(calc_name, device) -> calc`; default `isoshift.calculators.get_calculator`. `cache_root` sets `isoshift.cache.CACHE_ROOT = Path(cache_root)` at serve start (cache_dir reads the global at call time, so no cache.py edit).

## 3. Data formats
Queue layout under `queue_dir/`: `pending/`, `running/`, `done/`, `failed/`, `heartbeat/`, `logs/`, optional `STOP`. Created by `submit`/`serve` with `mkdir(parents=True, exist_ok=True)`.
- Job file `pending/<id>.json`: `{"id": str, "kind": "harmonic"|"qha", "cif": abs path, "calc": str, "out": abs path, "kw": {...JSON}, "submitted_at": unix s, "attempts": int, "allow_shrink": bool}`. `id = sha1(json.dumps([kind, cif, calc, out, kw], sort_keys=True))[:12]`. `allow_shrink` is popped from kw (default True) and forced False if kw has `supercell`.
- Running file `running/<id>__<worker>.json`: same content plus `"worker"`, `"started_at"`.
- Done file `done/<id>.json`: plus `"finished_at"`, `"wall_s"`. Failed file `failed/<id>.json`: plus `"error"` (one line), `"traceback"` (full `traceback.format_exc()` text), `"worker"`.
- Result file at job `out`: the dict returned by the worker function, plus `"pool": {"worker", "job_id", "wall_s", "model_load_s", "max_atoms_used", "retried_oom": bool, "started_at", "finished_at"}`. Units as in worker.py: energies eV per cell (`zpe_eV_cell`, `F_eV_cell`, `G_eV`), times s, memory MB, temps K. Serialize with the same `default=` as `worker.main`.
- Heartbeat `heartbeat/<worker>.json`: `{"worker", "pid", "calc", "model", "device", "current_job": id|None, "jobs_done", "jobs_failed", "last_error": str|None, "started_at", "updated_at", "model_load_s", "state": "loading"|"idle"|"busy"|"exited"}`.
- Worker id: `f"{calc}-{socket.gethostname()}-{os.getpid()}"`.
- Log (stdout of a launched worker): `logs/<calc>-<YYYYmmdd-HHMMSS>.log`. Required grep-able lines, one per event:
  `MODEL_LOADED worker=<id> calc=<c> model=<m> load_s=<f>` (exactly once per process),
  `JOB_DONE worker=<id> job=<id> wall_s=<f> retried_oom=<b>`, `JOB_FAILED worker=<id> job=<id> error=<msg>`, `EXIT worker=<id> reason=stop|idle jobs_done=<n>`.
- All JSON writes are atomic: write `<path>.tmp.<pid>` then `os.replace`. Ensure the parent dir of `out` exists.

## 4. Algorithms
submit: if `Path(out).exists()` return None. Compute id. If `<id>.json` exists in pending, done, or running (glob `<id>__*.json`) return id without writing. A previous failed/<id>.json is removed and the job resubmitted. Else write pending atomically, return id.

serve:
1. Set `cache_root` if given. If `device` starts with cuda and `torch.cuda.is_available()`: if `mem_fraction` set, `torch.cuda.set_per_process_memory_fraction(mem_fraction)`. Write heartbeat state=loading.
2. `t=time.time(); calc = loader(calc_name, device)`; print `MODEL_LOADED`. This is the only model load in the process. Assert `calculator_info(calc).get("name", calc_name) == calc_name`.
3. Start a daemon thread that rewrites the heartbeat every `HEARTBEAT_S` from a shared state dict guarded by a `threading.Lock`; main loop also writes it after every job.
4. Loop: if `queue_dir/STOP` exists, exit (reason stop). List `pending/*.json` sorted by (submitted_at, name). For each: read JSON (skip on JSONDecodeError/OSError, file may be mid-write by another process); skip if `job["calc"] != calc_name`; claim with `os.rename(pending/<id>.json, running/<id>__<worker>.json)`; on `FileNotFoundError` or `PermissionError` another worker won, continue. Run the first claimed job, then rescan (STOP is checked between jobs, never mid-job).
5. Run: `fn = {"harmonic": worker.harmonic_job, "qha": worker.qha_job}[kind]`; if out already exists, move to done without running. On cuda call `torch.cuda.reset_peak_memory_stats()` so `gpu_peak_mem_MB` stays per job. `res = fn(cif, calc_name, device=device, calc=calc, **kw)`.
6. OOM handling: catch `torch.cuda.OutOfMemoryError` or `RuntimeError` whose text contains "out of memory". `empty_cache()`. If `allow_shrink` and not yet retried: `kw["max_atoms"] = max(MIN_SHRINK_ATOMS, (kw.get("max_atoms") or MAX_ATOMS[calc_name]) // 2)`, retry once, set `retried_oom=True`. Otherwise fail. (phonons.get_force_constants already shrinks min_length internally; the pool retry is the outer guard for relax and QHA paths.)
7. Success: write result to `out` atomically, move running file to `done/<id>.json`, `jobs_done += 1`, print `JOB_DONE`. Any other exception: move to `failed/<id>.json` with traceback, `jobs_failed += 1`, `last_error`, print `JOB_FAILED`, keep serving. `KeyboardInterrupt`/`SystemExit`: move the job back to pending, then exit.
8. After every job: `gc.collect()`; on cuda `torch.cuda.empty_cache()`.
9. No claimable job: sleep `poll_s`; if idle for `idle_exit_s`, exit (reason idle). On exit write heartbeat state=exited and print `EXIT`.

requeue_stale: for each `running/<id>__<worker>.json`, heartbeat = `heartbeat/<worker>.json`. Stale if heartbeat missing, unreadable, state exited, or `now - updated_at > max_age_s`. Stale job: `attempts += 1`; if `attempts >= MAX_ATTEMPTS` move to failed with error "stale worker, max attempts" else write to `pending/<id>.json` and delete the running file. Return the requeued ids.

launch: `launch_cmd` returns `[py, "-m", "isoshift.pool", "serve", "--calc", c, "--queue", q, ...opts]`, `py = worker.SECONDARY_PY` if `calc in worker.SECONDARY_CALCS` else `ROOT/".venv"/"Scripts"/"python.exe"` (fall back to `sys.executable` if missing). `Popen(cmd, cwd=ROOT, env=PYTHONPATH=ROOT plus PYTHONUNBUFFERED=1, stdout=log file, stderr=STDOUT, stdin=DEVNULL)`; on Windows `creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW`, elsewhere `start_new_session=True`. Return `p.pid` and print the log path.

CLI (`python -m isoshift.pool`): `serve --calc C --queue Q [--device cuda] [--idle-exit 600] [--mem-fraction F] [--cache-root D]`; `submit --queue Q --kind harmonic|qha --cif F --calc C --out F [--kw JSON]` prints id or "exists"; `launch` (serve options) prints pid; `status --queue Q [--json]`; `requeue --queue Q [--max-age 600]`. `status` prints a table of state x calc counts, then one row per heartbeat: worker, pid, calc, state, current_job, jobs_done, jobs_failed, age_s, last_error, and STALE when age_s > 600.

## 5. GPU sharing and memory (RTX 4060 Laptop, 8 GB)
Each worker is its own process with its own CUDA context (~0.4 to 0.5 GB). Measured peak per job (REPORT.md): mace/orb/mattersim 2 to 3.3 GB at the 400 atom cap. Expected peak for mace + orb together: about 2 x (0.5 + 3.3) = 7.6 GB worst case, typical 5 to 6 GB. Recommended: launch both with `--mem-fraction 0.45` (~3.6 GB each) so contention surfaces as an in-process OOM, handled by the shrink retry, instead of one worker starving the other. SevenNet (5 to 7 GB at 100 atoms) must run alone: `status` warns if a sevenn heartbeat is busy alongside another live worker. Document this table in the pool.py module docstring.

## 6. What is cached
In-process: the calculator object (one `loader` call per serve; `get_calculator` also memoizes). On disk: force constants via the existing `isoshift.cache` (unchanged keys), result JSON at `out` (idempotency for submit and serve). Nothing else.

## 7. Unit tests (tests/test_pool.py, CPU only, no MLIP, < 60 s)
Fixture: fcc Ar CIF written to tmp_path; `loader` returns a counting `LennardJones(sigma=3.4, epsilon=0.0104, rc=8.0)` with `isoshift_info={"name": "lj", "model": "lj", ...}`; job kw `max_atoms=32, mesh=[2,2,2], min_length=6, fmax=0.01, temps=[300]`; `cache_root=tmp_path/"cache"`; `device="cpu"`.
1. `test_submit_idempotent`: same args twice gives one pending file and same id; existing `out` returns None.
2. `test_claim_race_and_calc_filter`: a job for calc "orb" is never claimed by an "lj" serve; a second `os.rename` claim of a taken job raises and is skipped.
3. `test_serve_end_to_end`: 2 jobs, `idle_exit_s=1`: both results exist, both in done/, loader called once, heartbeat jobs_done == 2 and state exited, result has `pool.wall_s`.
4. `test_pool_matches_direct`: pool zpe_eV_cell for H and D equals `harmonic_job(..., calc=same_calc)` within 1e-9 eV.
5. `test_failed_job_keeps_serving`: missing CIF goes to failed/ with "Traceback" in traceback text; a following good job is done.
6. `test_oom_retry_once`: monkeypatch the job table with a fake raising `RuntimeError("CUDA out of memory")` once: done with `retried_oom` true and max_atoms halved; always raising: failed; `allow_shrink=False`: failed without retry.
7. `test_stop_file`: STOP present gives immediate exit with reason stop and no jobs claimed.
8. `test_requeue_stale`: old heartbeat gives job back in pending with attempts 1; fresh heartbeat untouched; attempts reaching 3 goes to failed.
9. `test_launch_cmd_venv`: sevenn/mattersim use `.venv-sevenn` python, mace/orb use `.venv`.
10. `test_worker_default_calc_none`: `harmonic_job` signature has `calc=None` (existing tests cover physics).

## 8. Acceptance (judged by the orchestrator from command output)
Q = fresh temp dir. `.venv/Scripts/python.exe -m isoshift.pool launch --calc mace --queue Q --mem-fraction 0.45 --cache-root Q/cache --idle-exit 120`, same for orb. Submit 4 harmonic jobs (JVASP-2002, JVASP-3687 x mace, orb; default H/D subs, `--kw '{"temps":[300]}'`, out `Q/out/<calc>_<jid>.json`). Poll `status` until pending + running == 0, then:
- PASS needs all of: (a) 4 result files exist, `done` = 4, `failed` = 0; (b) each worker log has exactly one `MODEL_LOADED` line; (c) per-job `pool.wall_s` printed for all 4, and steady-state jobs avoid the ~35 s startup (wall_s of a worker's second job is under its `model_load_s` + 18 s); (d) for JVASP-2002 mace, a separate direct process (`.venv` python, `isoshift.cache.CACHE_ROOT = Q/cache`, `harmonic_job(cif, "mace", temps=(300,))`, no pool) gives `|zpe_eV_cell` diff| < 1e-6 eV for both H and D; print its `fc_cached` flag. Informational only: the same direct run with an empty cache root, diff printed (float32 GPU noise may exceed 1e-6 there); (e) both workers ran concurrently (overlapping started_at/finished_at or both heartbeats busy at once) with no OOM failure; print `gpu_peak_mem_MB` per job.
- `.venv/Scripts/python.exe -m pytest -q tests/test_isoshift.py tests/test_pool.py` passes with no failures.
- Clean up: `touch Q/STOP`, both heartbeats reach state exited.
