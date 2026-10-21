"""Overnight GPU watchdog (PLAN block 3.3): relaunch a dead pool worker when its model still has pending jobs.

Never launches when the GPU is at or above 87 C; runs sevenn only when no other main-queue worker is busy.
    python -m src.isoshift_event.watchdog      (loops every 10 min, logs to results/watchdog.log)
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUES = {"results/queue": ("mace", "orb", "mattersim", "sevenn"), "results/queue/qha_top": ("mace", "orb", "mattersim")}
THREADS = {"mace": "4", "orb": "4", "mattersim": "4", "sevenn": "6"}
MEM = {"mace": "0.4", "orb": "0.4", "mattersim": "0.35", "sevenn": None}


def _gpu_temp():
    try:
        return int(subprocess.check_output(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"], text=True).split()[0])
    except Exception:
        return 0


def _log(msg):
    with open(ROOT / "results" / "watchdog.log", "a") as fh:
        fh.write(time.strftime("%H:%M ") + msg + "\n")


def check():
    from isoshift import pool

    for q, models in QUEUES.items():
        st = pool.status(ROOT / q)
        counts = st["counts"] if isinstance(st, dict) and "counts" in st else {}
        live = {hb.get("calc") for hb in (st.get("heartbeats") or []) if hb.get("state") in ("busy", "idle", "loading")}
        for m in models:
            pending = counts.get("pending", {}).get(m, 0) if isinstance(counts.get("pending"), dict) else 0
            if pending and m not in live:
                if m == "sevenn" and live & {"mace", "orb", "mattersim"}:
                    continue
                t = _gpu_temp()
                if t >= 87:
                    _log(f"skip {m} {q}: GPU {t} C")
                    continue
                env = dict(os.environ, OMP_NUM_THREADS=THREADS[m], MKL_NUM_THREADS=THREADS[m], OPENBLAS_NUM_THREADS=THREADS[m])
                cmd = pool.launch_cmd(m, ROOT / q, idle_exit_s=900, mem_fraction=MEM[m])
                subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
                _log(f"launched {m} on {q} ({pending} pending, GPU {t} C)")


if __name__ == "__main__":
    while True:
        try:
            check()
        except Exception as exc:  # keep looping; the log says why
            _log(f"error {exc}")
        time.sleep(600)
