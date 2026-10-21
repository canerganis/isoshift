"""Persistent calculator workers consuming an atomic file queue.

Each worker keeps one calculator in memory. Force constants use the existing
isoshift.cache keys; result JSON files provide job idempotency.

RTX 4060 Laptop (8 GB) sharing estimates, including separate CUDA contexts:

    Configuration           Peak job memory       Recommendation
    mace / orb / mattersim  2--3.3 GB each         Context adds 0.4--0.5 GB each
    mace + orb              5--6 GB typical,       --mem-fraction 0.45 each
                            about 7.6 GB worst
    sevenn (100 atoms)      5--7 GB                Run alone

Memory fractions make contention an in-process OOM, eligible for one outer
atom-cap shrink retry. These estimates are not guarantees of available memory.
Use ``python -m isoshift.pool --help`` for queue and worker commands.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import socket
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

from . import worker
from .calculators import MAX_ATOMS, calculator_info, get_calculator

ROOT = worker.ROOT
QUEUE_STATES = ("pending", "running", "done", "failed")
HEARTBEAT_S = 30.0
STALE_S = 600.0
MAX_ATTEMPTS = 3
MIN_SHRINK_ATOMS = 50


def _queue(queue_dir):
    queue = Path(queue_dir)
    for state in (*QUEUE_STATES, "heartbeat", "logs"):
        (queue / state).mkdir(parents=True, exist_ok=True)
    return queue


REPLACE_RETRIES = 20
REPLACE_BACKOFF_S = 0.05


def _write_json(path, data):
    """Same numerical serialization as worker.main, published by atomic replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    try:
        tmp.write_text(json.dumps(data, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)),
                       encoding="utf-8")
        # Windows refuses to replace a file another process has open (status() and
        # requeue_stale() read these files); the reader closes quickly, so retry.
        for attempt in range(REPLACE_RETRIES):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if attempt == REPLACE_RETRIES - 1:
                    raise
                time.sleep(REPLACE_BACKOFF_S)
    finally:
        tmp.unlink(missing_ok=True)


def _read_json(path):
    try:
        data = path.read_text(encoding="utf-8")
        result = json.loads(data)
        return result if isinstance(result, dict) else None
    except (OSError, ValueError):
        return None


def submit(queue_dir, kind, cif, calc, out, **kw) -> str | None:
    """Enqueue once, or return None when the result already exists."""
    out = Path(out).resolve()
    if out.exists():
        return None
    if kind not in ("harmonic", "qha"):
        raise ValueError(f"unknown job kind: {kind}")
    queue = _queue(queue_dir)
    cif = str(Path(cif).resolve())
    allow_shrink = bool(kw.pop("allow_shrink", True)) and "supercell" not in kw
    key = json.dumps([kind, cif, calc, str(out), kw], sort_keys=True)
    jid = hashlib.sha1(key.encode()).hexdigest()[:12]
    if ((queue / "pending" / f"{jid}.json").exists()
            or (queue / "done" / f"{jid}.json").exists()
            or any((queue / "running").glob(f"{jid}__*.json"))):
        return jid
    (queue / "failed" / f"{jid}.json").unlink(missing_ok=True)
    _write_json(queue / "pending" / f"{jid}.json", {
        "id": jid, "kind": kind, "cif": cif, "calc": calc, "out": str(out), "kw": kw,
        "submitted_at": time.time(), "attempts": 0, "allow_shrink": allow_shrink,
    })
    return jid


def _claim(queue, calc_name, worker_id):
    candidates = []
    for path in (queue / "pending").glob("*.json"):
        job = _read_json(path)
        if job is not None and job.get("calc") == calc_name:
            candidates.append((job.get("submitted_at", 0), path.name, path, job))
    for _, _, path, job in sorted(candidates):
        running = queue / "running" / f"{job['id']}__{worker_id}.json"
        try:
            os.rename(path, running)
        except (FileNotFoundError, PermissionError):
            continue
        return running, job
    return None


def _move_job(running, destination, job):
    _write_json(running, job)
    os.replace(running, destination)


def _pending_job(job):
    return {k: v for k, v in job.items() if k not in ("worker", "started_at")}


def _is_oom(exc, torch):
    torch = torch or sys.modules.get("torch")
    return ((torch is not None and isinstance(exc, torch.cuda.OutOfMemoryError))
            or (isinstance(exc, RuntimeError) and "out of memory" in str(exc).lower()))


def serve(calc_name, queue_dir, device="cuda", idle_exit_s=600.0, poll_s=2.0, mem_fraction=None,
          cache_root=None, worker_id=None, loader=None) -> dict:
    """Load once and serve matching jobs until STOP, interruption, or idle expiry."""
    from . import cache

    queue = _queue(queue_dir)
    if cache_root is not None:
        cache.CACHE_ROOT = Path(cache_root)
    torch = None
    cuda = False
    if device.startswith("cuda"):
        import torch

        cuda = torch.cuda.is_available()
        # torch.cuda memory APIs reject a bare "cuda"; they need an indexed device.
        tdev = device if ":" in device else "cuda:0"
        if cuda and mem_fraction is not None:
            torch.cuda.set_per_process_memory_fraction(mem_fraction, device=tdev)
    worker_id = worker_id or f"{calc_name}-{socket.gethostname()}-{os.getpid()}"
    heartbeat_path = queue / "heartbeat" / f"{worker_id}.json"
    now = time.time()
    heartbeat = {
        "worker": worker_id, "pid": os.getpid(), "calc": calc_name, "model": None,
        "device": device, "current_job": None, "jobs_done": 0, "jobs_failed": 0,
        "last_error": None, "started_at": now, "updated_at": now, "model_load_s": 0.0,
        "state": "loading",
    }
    lock = threading.Lock()
    stopped = threading.Event()
    thread = None

    def publish(**updates):
        # Serialize the writer too: the main loop and heartbeat thread share a
        # PID and therefore the same atomic-write temporary filename.
        # A failed heartbeat write must never fail a job or kill the worker.
        with lock:
            heartbeat.update(updates, updated_at=time.time())
            try:
                _write_json(heartbeat_path, heartbeat)
            except OSError as exc:
                print(f"HEARTBEAT_WRITE_FAILED {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)

    def pulse():
        while not stopped.wait(HEARTBEAT_S):
            publish()

    reason = "stop"
    publish()
    try:
        t = time.time()
        calc = (loader or get_calculator)(calc_name, device)
        model_load_s = time.time() - t
        info = calculator_info(calc)
        assert info.get("name", calc_name) == calc_name, "loaded calculator name does not match worker"
        model = info.get("model", calc_name)
        print(f"MODEL_LOADED worker={worker_id} calc={calc_name} model={model} load_s={model_load_s:.6f}", flush=True)
        publish(model=model, model_load_s=model_load_s, state="idle")
        thread = threading.Thread(target=pulse, name=f"heartbeat-{worker_id}", daemon=True)
        thread.start()
        idle_since = time.monotonic()
        while True:
            if (queue / "STOP").exists():
                break
            claimed = _claim(queue, calc_name, worker_id)
            if claimed is None:
                remaining = idle_exit_s - (time.monotonic() - idle_since)
                if remaining <= 0:
                    reason = "idle"
                    break
                time.sleep(min(poll_s, remaining))
                continue
            running, job = claimed
            started_at = time.time()
            job.update(worker=worker_id, started_at=started_at)
            retried_oom = False
            try:
                _write_json(running, job)
                publish(state="busy", current_job=job["id"])
                out = Path(job["out"])
                kw = dict(job["kw"])
                if not out.exists():
                    fn = {"harmonic": worker.harmonic_job, "qha": worker.qha_job}[job["kind"]]
                    if cuda:
                        torch.cuda.reset_peak_memory_stats(device=tdev)
                    while True:
                        try:
                            res = fn(job["cif"], calc_name, device=device, calc=calc, **kw)
                            break
                        except Exception as exc:
                            if not _is_oom(exc, torch):
                                raise
                            if cuda:
                                torch.cuda.empty_cache()
                            if retried_oom or not job["allow_shrink"] or "supercell" in kw:
                                raise
                            cap = kw.get("max_atoms") or MAX_ATOMS[calc_name]
                            kw["max_atoms"] = max(MIN_SHRINK_ATOMS, cap // 2)
                            retried_oom = True
                    finished_at = time.time()
                    res["pool"] = {
                        "worker": worker_id, "job_id": job["id"], "wall_s": finished_at - started_at,
                        "model_load_s": model_load_s,
                        "max_atoms_used": kw.get("max_atoms") or MAX_ATOMS.get(calc_name),
                        "retried_oom": retried_oom, "started_at": started_at, "finished_at": finished_at,
                    }
                    _write_json(out, res)
                else:
                    finished_at = time.time()
                job.update(finished_at=finished_at, wall_s=finished_at - started_at)
                _move_job(running, queue / "done" / f"{job['id']}.json", job)
                with lock:
                    heartbeat["jobs_done"] += 1
                print(f"JOB_DONE worker={worker_id} job={job['id']} wall_s={job['wall_s']:.6f} "
                      f"retried_oom={retried_oom}", flush=True)
            except (KeyboardInterrupt, SystemExit):
                _move_job(running, queue / "pending" / f"{job['id']}.json", _pending_job(job))
                break
            except Exception as exc:
                error = " ".join(str(exc).splitlines()) or type(exc).__name__
                finished_at = time.time()
                job.update(error=error, traceback=traceback.format_exc(), finished_at=finished_at,
                           wall_s=finished_at - started_at)
                _move_job(running, queue / "failed" / f"{job['id']}.json", job)
                with lock:
                    heartbeat["jobs_failed"] += 1
                    heartbeat["last_error"] = error
                print(f"JOB_FAILED worker={worker_id} job={job['id']} error={error}", flush=True)
            finally:
                gc.collect()
                if cuda:
                    torch.cuda.empty_cache()
                publish(state="idle", current_job=None)
            idle_since = time.monotonic()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as exc:
        publish(last_error=" ".join(str(exc).splitlines()) or type(exc).__name__)
        raise
    finally:
        stopped.set()
        if thread is not None:
            thread.join()
        publish(state="exited", current_job=None)
        print(f"EXIT worker={worker_id} reason={reason} jobs_done={heartbeat['jobs_done']}", flush=True)
    return dict(heartbeat)


def _heartbeat_stale(heartbeat, now, max_age_s):
    if heartbeat is None or heartbeat.get("state") == "exited":
        return True
    try:
        return now - float(heartbeat["updated_at"]) > max_age_s
    except (KeyError, TypeError, ValueError):
        return True


def requeue_stale(queue_dir, max_age_s=STALE_S) -> list[str]:
    """Recover abandoned claims, with a bounded number of stale-worker attempts."""
    queue = _queue(queue_dir)
    now = time.time()
    requeued = []
    for running in sorted((queue / "running").glob("*__*.json")):
        job = _read_json(running)
        if job is None:
            continue
        owner = job.get("worker", running.stem.split("__", 1)[1])
        hb = _read_json(queue / "heartbeat" / f"{owner}.json")
        if not _heartbeat_stale(hb, now, max_age_s):
            continue
        job["attempts"] += 1
        if job["attempts"] >= MAX_ATTEMPTS:
            job.update(error="stale worker, max attempts", worker=owner, finished_at=now, traceback="")
            _move_job(running, queue / "failed" / f"{job['id']}.json", job)
        else:
            _write_json(queue / "pending" / f"{job['id']}.json", _pending_job(job))
            running.unlink(missing_ok=True)
            requeued.append(job["id"])
    return requeued


def status(queue_dir) -> dict:
    """Return counts by state/calculator, heartbeat ages, and sharing warnings."""
    queue = Path(queue_dir)
    counts = {state: {} for state in QUEUE_STATES}
    for state in QUEUE_STATES:
        for path in (queue / state).glob("*.json"):
            job = _read_json(path)
            if job is not None and "calc" in job:
                calc = job["calc"]
                counts[state][calc] = counts[state].get(calc, 0) + 1
    now = time.time()
    heartbeats = []
    for path in sorted((queue / "heartbeat").glob("*.json")):
        hb = _read_json(path)
        if hb is not None:
            try:
                hb["age_s"] = max(0.0, now - float(hb["updated_at"]))
            except (KeyError, TypeError, ValueError):
                continue
            heartbeats.append(hb)
    live = [hb for hb in heartbeats if not _heartbeat_stale(hb, now, STALE_S)]
    warnings = []
    if len(live) > 1 and any(hb.get("calc") == "sevenn" and hb.get("state") == "busy" for hb in live):
        warnings.append("SevenNet is busy alongside another live worker; run SevenNet alone on an 8 GB GPU.")
    return {"counts": counts, "heartbeats": heartbeats, "warnings": warnings}


def launch_cmd(calc_name, queue_dir, **opts) -> list[str]:
    """Build a command without loading a model or touching the queue."""
    if calc_name in worker.SECONDARY_CALCS:
        py = worker.SECONDARY_PY
    else:
        py = ROOT / ".venv" / "Scripts" / "python.exe"
        if not py.exists():
            py = Path(sys.executable)
    cmd = [str(py), "-m", "isoshift.pool", "serve", "--calc", calc_name, "--queue", str(queue_dir)]
    flags = {"device": "--device", "idle_exit_s": "--idle-exit", "mem_fraction": "--mem-fraction",
             "cache_root": "--cache-root"}
    for key, value in opts.items():
        flag = flags[key]
        if value is not None:
            cmd.extend([flag, str(value)])
    return cmd


def launch(calc_name, queue_dir, device="cuda", idle_exit_s=600.0, mem_fraction=None, cache_root=None) -> int:
    """Detach a worker in its calculator's Python environment; return its PID."""
    queue = _queue(Path(queue_dir).resolve())
    cmd = launch_cmd(calc_name, queue, device=device, idle_exit_s=idle_exit_s,
                     mem_fraction=mem_fraction,
                     cache_root=Path(cache_root).resolve() if cache_root is not None else None)
    log = queue / "logs" / f"{calc_name}-{time.strftime('%Y%m%d-%H%M%S')}.log"
    env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONUNBUFFERED="1")
    opts = {"cwd": ROOT, "env": env, "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
    if os.name == "nt":
        opts["creationflags"] = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                                 | subprocess.CREATE_NO_WINDOW)
    else:
        opts["start_new_session"] = True
    with log.open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(cmd, stdout=stream, **opts)
    print(f"log={log}", flush=True)
    return process.pid


def _print_status(data):
    calcs = sorted({calc for counts in data["counts"].values() for calc in counts})
    print("state\t" + "\t".join(calcs))
    for state, counts in data["counts"].items():
        print(state + "\t" + "\t".join(str(counts.get(calc, 0)) for calc in calcs))
    fields = ("worker", "pid", "calc", "state", "current_job", "jobs_done", "jobs_failed", "age_s", "last_error")
    print("\t".join(fields))
    for hb in data["heartbeats"]:
        values = [f"{hb[field]:.1f}" if field == "age_s" else str(hb.get(field)) for field in fields]
        print("\t".join(values) + ("\tSTALE" if hb["age_s"] > STALE_S else ""))
    for warning in data["warnings"]:
        print(f"WARNING: {warning}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    commands = ap.add_subparsers(dest="command", required=True)
    for command in ("serve", "launch"):
        parser = commands.add_parser(command)
        parser.add_argument("--calc", required=True)
        parser.add_argument("--queue", required=True)
        parser.add_argument("--device", default="cuda")
        parser.add_argument("--idle-exit", type=float, default=600.0, dest="idle_exit_s")
        parser.add_argument("--mem-fraction", type=float)
        parser.add_argument("--cache-root")
    parser = commands.add_parser("submit")
    parser.add_argument("--queue", required=True)
    parser.add_argument("--kind", choices=("harmonic", "qha"), required=True)
    parser.add_argument("--cif", required=True)
    parser.add_argument("--calc", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--kw", default="{}")
    parser = commands.add_parser("status")
    parser.add_argument("--queue", required=True)
    parser.add_argument("--json", action="store_true")
    parser = commands.add_parser("requeue")
    parser.add_argument("--queue", required=True)
    parser.add_argument("--max-age", type=float, default=STALE_S)
    args = ap.parse_args(argv)
    if args.command in ("serve", "launch"):
        fn = serve if args.command == "serve" else launch
        result = fn(args.calc, args.queue, device=args.device, idle_exit_s=args.idle_exit_s,
                    mem_fraction=args.mem_fraction, cache_root=args.cache_root)
        if args.command == "launch":
            print(result)
    elif args.command == "submit":
        jid = submit(args.queue, args.kind, args.cif, args.calc, args.out, **json.loads(args.kw))
        print(jid if jid is not None else "exists")
    elif args.command == "requeue":
        print(json.dumps(requeue_stale(args.queue, args.max_age)))
    else:
        data = status(args.queue)
        if args.json:
            print(json.dumps(data))
        else:
            _print_status(data)


if __name__ == "__main__":
    main()
