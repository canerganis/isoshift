"""CPU-only pool contracts; no model downloads or subprocess MLIP jobs."""
import importlib
import inspect
import json
import os
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from ase.build import bulk
from ase.calculators.lj import LennardJones
from ase.io import write

from isoshift import cache, worker


@pytest.fixture
def pool():
    assert importlib.util.find_spec("isoshift.pool") is not None, "pool module is missing"
    return importlib.import_module("isoshift.pool")


@pytest.fixture
def jobs(tmp_path, monkeypatch):
    class CountingLJ(LennardJones):
        evaluations = 0

        def calculate(self, *args, **kw):
            self.evaluations += 1
            return super().calculate(*args, **kw)

    calc = CountingLJ(sigma=3.4, epsilon=0.0104, rc=8.0)
    calc.isoshift_info = {"name": "lj", "model": "lj", "device": "cpu"}
    cif = tmp_path / "ar.cif"
    write(cif, bulk("Ar", "fcc", a=5.26, cubic=True))
    loads = []

    def loader(name, device):
        loads.append((name, device))
        return calc

    monkeypatch.setattr(cache, "CACHE_ROOT", tmp_path / "original-cache")
    return SimpleNamespace(
        queue=tmp_path / "queue", cif=cif, calc=calc, loads=loads,
        kw=dict(max_atoms=32, mesh=[2, 2, 2], min_length=6, fmax=0.01, temps=[300]),
        options=dict(device="cpu", loader=loader, cache_root=tmp_path / "cache",
                     idle_exit_s=0, poll_s=0.001, worker_id="lj-test"),
    )


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def enqueue(pool, jobs, name="a", **overrides):
    out = jobs.queue / "out" / f"{name}.json"
    kw = dict(jobs.kw, **overrides)
    jid = pool.submit(jobs.queue, "harmonic", jobs.cif, "lj", out, **kw)
    return jid, out


def test_submit_idempotent(pool, jobs):
    jid, out = enqueue(pool, jobs)
    assert enqueue(pool, jobs)[0] == jid
    assert len(list((jobs.queue / "pending").glob("*.json"))) == 1
    job = read(jobs.queue / "pending" / f"{jid}.json")
    assert Path(job["cif"]).is_absolute() and Path(job["out"]).is_absolute()
    assert job["attempts"] == 0 and job["allow_shrink"] is True
    assert job["kw"] == jobs.kw
    out.parent.mkdir()
    out.write_text("{}")
    assert enqueue(pool, jobs)[0] is None


@pytest.mark.parametrize("state", ["running", "done", "failed"])
def test_submit_existing_state(pool, jobs, state):
    jid, _ = enqueue(pool, jobs)
    pending = jobs.queue / "pending" / f"{jid}.json"
    target = jobs.queue / state / (f"{jid}__other.json" if state == "running" else pending.name)
    pending.rename(target)
    assert enqueue(pool, jobs)[0] == jid
    assert pending.exists() == (state == "failed")
    assert target.exists() == (state != "failed")


@pytest.mark.parametrize("kw", [{"allow_shrink": False}, {"supercell": [1, 1, 1]}])
def test_submit_shrink_policy(pool, jobs, kw):
    jid, _ = enqueue(pool, jobs, **kw)
    job = read(jobs.queue / "pending" / f"{jid}.json")
    assert job["allow_shrink"] is False
    assert "allow_shrink" not in job["kw"]


@pytest.mark.parametrize("race_error", [FileNotFoundError, PermissionError])
def test_claim_race_and_calc_filter(pool, jobs, monkeypatch, race_error):
    orb = pool.submit(jobs.queue, "harmonic", jobs.cif, "orb", jobs.queue / "orb.json")
    taken, _ = enqueue(pool, jobs, "taken")
    good, out = enqueue(pool, jobs, "good")
    pending = jobs.queue / "pending" / f"{taken}.json"
    real_rename = os.rename

    def racing_rename(src, dst):
        if Path(src) == pending:
            real_rename(src, jobs.queue / "running" / f"{taken}__winner.json")
            raise race_error("another worker won")
        return real_rename(src, dst)

    monkeypatch.setattr(pool.os, "rename", racing_rename)
    monkeypatch.setattr(worker, "harmonic_job", lambda *a, **kw: {"ok": True})
    (jobs.queue / "pending" / "broken.json").write_text("{")
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    assert hb["jobs_done"] == 1 and out.exists()
    assert (jobs.queue / "done" / f"{good}.json").exists()
    assert (jobs.queue / "pending" / f"{orb}.json").exists()
    assert (jobs.queue / "running" / f"{taken}__winner.json").exists()


def test_serve_end_to_end(pool, jobs, capsys):
    queued = [enqueue(pool, jobs, name) for name in ("a", "b")]
    hb = pool.serve("lj", jobs.queue, **dict(jobs.options, idle_exit_s=1, poll_s=0.01))
    assert jobs.loads == [("lj", "cpu")]
    assert jobs.calc.evaluations > 0
    assert hb["jobs_done"] == 2 and hb["jobs_failed"] == 0 and hb["state"] == "exited"
    assert read(jobs.queue / "heartbeat" / "lj-test.json") == hb
    assert cache.CACHE_ROOT == jobs.options["cache_root"]
    for jid, out in queued:
        result = read(out)
        meta = result["pool"]
        assert meta["job_id"] == jid and meta["worker"] == "lj-test"
        assert meta["wall_s"] >= 0 and meta["model_load_s"] >= 0
        assert meta["finished_at"] >= meta["started_at"]
        assert meta["max_atoms_used"] == 32 and meta["retried_oom"] is False
        done = read(jobs.queue / "done" / f"{jid}.json")
        assert done["wall_s"] == meta["wall_s"]
    assert not list((jobs.queue / "running").glob("*.json"))
    assert not list(jobs.queue.rglob("*.tmp.*"))
    log = capsys.readouterr().out
    assert log.count("MODEL_LOADED ") == 1 and log.count("JOB_DONE ") == 2
    assert "reason=idle" in log


def test_pool_matches_direct(pool, jobs):
    _, out = enqueue(pool, jobs)
    pool.serve("lj", jobs.queue, **jobs.options)
    direct = worker.harmonic_job(str(jobs.cif), "lj", device="cpu", calc=jobs.calc, **jobs.kw)
    pooled = read(out)
    for isotope in ("H", "D"):
        assert pooled["variants"][isotope]["zpe_eV_cell"] == pytest.approx(
            direct["variants"][isotope]["zpe_eV_cell"], abs=1e-9, rel=0)


def test_failed_job_keeps_serving(pool, jobs):
    bad = pool.submit(jobs.queue, "harmonic", jobs.cif.with_name("missing.cif"), "lj",
                      jobs.queue / "bad.json", **jobs.kw)
    good, out = enqueue(pool, jobs)
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    failed = read(jobs.queue / "failed" / f"{bad}.json")
    assert "Traceback" in failed["traceback"] and failed["worker"] == "lj-test"
    assert "\n" not in failed["error"] and hb["last_error"] == failed["error"]
    assert hb["jobs_failed"] == 1 and hb["jobs_done"] == 1
    assert out.exists() and (jobs.queue / "done" / f"{good}.json").exists()


@pytest.mark.parametrize("always,shrink,supercell,want_calls", [
    (False, True, None, 2), (True, True, None, 2), (True, False, None, 1),
    (True, True, [1, 1, 1], 1),
])
def test_oom_retry_once(pool, jobs, monkeypatch, always, shrink, supercell, want_calls):
    calls = []

    def oom(*args, **kw):
        calls.append(kw["max_atoms"])
        if always or len(calls) == 1:
            raise RuntimeError("CUDA out of memory")
        return {"array": np.array([1.0])}

    monkeypatch.setattr(worker, "harmonic_job", oom)
    extra = {"supercell": supercell} if supercell is not None else {}
    jid, out = enqueue(pool, jobs, max_atoms=200, allow_shrink=shrink, **extra)
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    assert calls == [200, 100][:want_calls]
    if not always:
        result = read(out)
        assert result["pool"]["retried_oom"] is True
        assert result["pool"]["max_atoms_used"] == 100 and result["array"] == [1.0]
        assert hb["jobs_done"] == 1
    else:
        assert not out.exists() and hb["jobs_failed"] == 1
        assert "out of memory" in read(jobs.queue / "failed" / f"{jid}.json")["error"]


def test_existing_result_skips_execution(pool, jobs, monkeypatch):
    jid, out = enqueue(pool, jobs)
    out.parent.mkdir()
    out.write_text('{"preserved": true}')

    def forbidden(*args, **kw):
        pytest.fail("existing result must skip execution")

    monkeypatch.setattr(worker, "harmonic_job", forbidden)
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    assert hb["jobs_done"] == 1 and read(out) == {"preserved": True}
    assert (jobs.queue / "done" / f"{jid}.json").exists()


def test_stop_file(pool, jobs, capsys):
    jid, out = enqueue(pool, jobs)
    (jobs.queue / "STOP").touch()
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    assert hb["state"] == "exited" and hb["jobs_done"] == 0
    assert not out.exists() and (jobs.queue / "pending" / f"{jid}.json").exists()
    assert "reason=stop" in capsys.readouterr().out


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit])
def test_interrupted_job_returns_to_pending(pool, jobs, monkeypatch, interrupt):
    jid, out = enqueue(pool, jobs)

    def interrupted(*args, **kw):
        raise interrupt()

    monkeypatch.setattr(worker, "harmonic_job", interrupted)
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    assert hb["state"] == "exited" and hb["current_job"] is None
    assert not out.exists() and (jobs.queue / "pending" / f"{jid}.json").exists()
    assert not list((jobs.queue / "running").glob("*.json"))


def test_requeue_stale(pool, jobs):
    ids = {}
    for name in ("old", "fresh", "exhausted", "missing", "unreadable", "exited"):
        jid, _ = enqueue(pool, jobs, name)
        ids[name] = jid
        pending = jobs.queue / "pending" / f"{jid}.json"
        job = read(pending)
        job.update(worker=name, started_at=1, attempts=2 if name == "exhausted" else 0)
        pending.write_text(json.dumps(job))
        pending.rename(jobs.queue / "running" / f"{jid}__{name}.json")
        if name == "missing":
            continue
        hb = {"updated_at": time.time() if name in ("fresh", "exited") else 0,
              "state": "exited" if name == "exited" else "busy"}
        (jobs.queue / "heartbeat" / f"{name}.json").write_text(
            "{" if name == "unreadable" else json.dumps(hb))
    assert set(pool.requeue_stale(jobs.queue)) == {ids[n] for n in ("old", "missing", "unreadable", "exited")}
    assert read(jobs.queue / "pending" / f"{ids['old']}.json")["attempts"] == 1
    assert (jobs.queue / "running" / f"{ids['fresh']}__fresh.json").exists()
    failed = read(jobs.queue / "failed" / f"{ids['exhausted']}.json")
    assert failed["attempts"] == 3 and failed["error"] == "stale worker, max attempts"


@pytest.mark.parametrize("name,venv", [("sevenn", ".venv-sevenn"), ("mattersim", ".venv-sevenn"),
                                       ("mace", ".venv"), ("orb", ".venv")])
def test_launch_cmd_venv(pool, jobs, name, venv):
    cmd = pool.launch_cmd(name, jobs.queue, device="cpu", idle_exit_s=10,
                          mem_fraction=0.45, cache_root=jobs.options["cache_root"])
    assert Path(cmd[0]) == worker.ROOT / venv / "Scripts" / "python.exe"
    assert cmd[1:4] == ["-m", "isoshift.pool", "serve"]
    assert cmd[cmd.index("--calc") + 1] == name
    assert cmd[cmd.index("--idle-exit") + 1] == "10"
    assert cmd[cmd.index("--mem-fraction") + 1] == "0.45"
    assert not jobs.queue.exists()  # command construction is pure


def test_worker_default_calc_none():
    for fn in (worker.harmonic_job, worker.qha_job):
        assert "calc" in inspect.signature(fn).parameters
        assert inspect.signature(fn).parameters["calc"].default is None


def test_qha_injected_calculator(pool, jobs, monkeypatch):
    from isoshift import qha

    def qha_result(atoms, calc, cid, variants, **kw):
        assert calc is jobs.calc and cid == "lj-lj"
        assert kw["max_atoms"] == 32 and variants == {"H": {}, "D": {"H": "D"}}
        return {"n_atoms_cell": len(atoms)}

    monkeypatch.setattr(qha, "qha_gibbs", qha_result)
    out = jobs.queue / "qha.json"
    jid = pool.submit(jobs.queue, "qha", jobs.cif, "lj", out, max_atoms=32)
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    assert hb["jobs_done"] == 1 and read(out)["n_atoms_cell"] == 4
    assert (jobs.queue / "done" / f"{jid}.json").exists()


def test_cli_submit_status_requeue(pool, jobs, capsys):
    args = ["submit", "--queue", str(jobs.queue), "--kind", "harmonic", "--cif", str(jobs.cif),
            "--calc", "lj", "--out", str(jobs.queue / "cli.json"), "--kw", '{"max_atoms": 32}']
    pool.main(args)
    jid = capsys.readouterr().out.strip()
    assert (jobs.queue / "pending" / f"{jid}.json").exists()
    pool.main(["status", "--queue", str(jobs.queue), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["counts"]["pending"]["lj"] == 1 and data["heartbeats"] == []
    pool.main(["requeue", "--queue", str(jobs.queue), "--max-age", "1"])
    assert (jobs.queue / "pending" / f"{jid}.json").exists()


def test_heartbeat_during_job_and_stop_between_jobs(pool, jobs, monkeypatch):
    first, out = enqueue(pool, jobs, "first")
    second, second_out = enqueue(pool, jobs, "second")
    # Explicit timestamps make execution order independent of clock resolution.
    for submitted, jid in enumerate((first, second)):
        path = jobs.queue / "pending" / f"{jid}.json"
        job = read(path)
        job["submitted_at"] = submitted
        path.write_text(json.dumps(job))
    monkeypatch.setattr(pool, "HEARTBEAT_S", 0.01)
    updated = threading.Event()
    observed = []
    real_write = pool._write_json

    def observe(path, data):
        real_write(path, data)
        if (Path(path).parent.name == "heartbeat" and data["state"] == "busy"
                and threading.current_thread() is not threading.main_thread()):
            observed.append(dict(data))
            updated.set()

    monkeypatch.setattr(pool, "_write_json", observe)

    def long_job(*args, **kw):
        assert updated.wait(timeout=2), "heartbeat did not refresh while job was busy"
        (jobs.queue / "STOP").touch()
        return {"completed": True}

    monkeypatch.setattr(worker, "harmonic_job", long_job)
    hb = pool.serve("lj", jobs.queue, **jobs.options)
    assert hb["jobs_done"] == 1 and read(out)["completed"] is True
    assert observed[0]["current_job"] == first
    assert not second_out.exists() and (jobs.queue / "pending" / f"{second}.json").exists()
    assert read(jobs.queue / "heartbeat" / "lj-test.json")["state"] == "exited"


@pytest.mark.parametrize("device", ["cpu", "cuda", "cuda:0"])
def test_cuda_memory_hooks_and_typed_oom(pool, jobs, monkeypatch, device):
    events = []

    class OutOfMemoryError(RuntimeError):
        pass

    cuda = SimpleNamespace(
        is_available=lambda: True, OutOfMemoryError=OutOfMemoryError,
        set_per_process_memory_fraction=lambda fraction, device: events.append(("fraction", fraction, device)),
        reset_peak_memory_stats=lambda device: events.append(("reset", device)),
        empty_cache=lambda: events.append(("empty",)),
    )
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=cuda))
    calls = []

    def fake_job(*args, **kw):
        calls.append(kw["max_atoms"])
        if len(calls) == 1:
            raise OutOfMemoryError("allocation failed")
        return {"gpu_peak_mem_MB": 1.0}

    monkeypatch.setattr(worker, "harmonic_job", fake_job)
    _, out = enqueue(pool, jobs, max_atoms=200)
    pool.serve("lj", jobs.queue, mem_fraction=0.45, **dict(jobs.options, device=device))
    assert calls == [200, 100] and read(out)["pool"]["retried_oom"] is True
    expected = [("fraction", 0.45, "cuda:0"), ("reset", "cuda:0"), ("empty",), ("empty",)]
    assert events == (expected if device.startswith("cuda") else [])


@pytest.mark.parametrize("cap,expected", [(60, 50), (None, 200)])
def test_oom_shrink_floor_and_default(pool, jobs, monkeypatch, cap, expected):
    jobs.calc.isoshift_info["name"] = "mace"
    calls = []

    def fake_job(*args, **kw):
        calls.append(kw["max_atoms"])
        if len(calls) == 1:
            raise RuntimeError("out of memory")
        return {}

    monkeypatch.setattr(worker, "harmonic_job", fake_job)
    out = jobs.queue / "mace.json"
    pool.submit(jobs.queue, "harmonic", jobs.cif, "mace", out, max_atoms=cap)
    hb = pool.serve("mace", jobs.queue, **jobs.options)
    assert hb["jobs_done"] == 1 and calls == [cap, expected]
    assert read(out)["pool"]["max_atoms_used"] == expected


def test_loader_failure_and_wrong_model_exit_heartbeat(pool, jobs):
    def broken_loader(*args):
        loading = read(jobs.queue / "heartbeat" / "lj-test.json")
        assert loading["state"] == "loading"
        raise ValueError("model load failed")

    with pytest.raises(ValueError, match="model load failed"):
        pool.serve("lj", jobs.queue, **dict(jobs.options, loader=broken_loader))
    hb = read(jobs.queue / "heartbeat" / "lj-test.json")
    assert hb["state"] == "exited" and hb["last_error"] == "model load failed"
    with pytest.raises(AssertionError, match="calculator name"):
        pool.serve("orb", jobs.queue, **jobs.options)
    assert read(jobs.queue / "heartbeat" / "lj-test.json")["state"] == "exited"


def test_status_warns_only_for_live_sevenn_overlap(pool, jobs, capsys):
    enqueue(pool, jobs)
    now = time.time()
    for name, calc, state, age in (("seven", "sevenn", "busy", 0), ("orb", "orb", "idle", 0),
                                   ("old", "mace", "busy", 700)):
        hb = dict(worker=name, pid=123, calc=calc, model="fake", device="cuda", current_job=None,
                  jobs_done=0, jobs_failed=0, last_error=None, started_at=now - 800,
                  updated_at=now - age, model_load_s=1.0, state=state)
        (jobs.queue / "heartbeat" / f"{name}.json").write_text(json.dumps(hb))
    data = pool.status(jobs.queue)
    assert data["counts"]["pending"] == {"lj": 1}
    assert len(data["heartbeats"]) == 3 and len(data["warnings"]) == 1
    pool.main(["status", "--queue", str(jobs.queue)])
    text = capsys.readouterr().out
    assert "STALE" in text and "SevenNet" in text and "WARNING" in text
    orb = jobs.queue / "heartbeat" / "orb.json"
    hb = read(orb)
    hb["state"] = "exited"
    orb.write_text(json.dumps(hb))
    assert pool.status(jobs.queue)["warnings"] == []


def test_launch_detaches_and_logs(pool, jobs, monkeypatch, capsys):
    captured = {}

    def popen(cmd, **kw):
        captured.update(cmd=cmd, **kw)
        kw["stdout"].write("worker output\n")
        return SimpleNamespace(pid=456)

    monkeypatch.setattr(pool.subprocess, "Popen", popen)
    pid = pool.launch("mace", jobs.queue, device="cpu", idle_exit_s=10, mem_fraction=0.45,
                      cache_root=jobs.options["cache_root"])
    assert pid == 456
    assert captured["cwd"] == worker.ROOT
    assert captured["env"]["PYTHONPATH"] == str(worker.ROOT)
    assert captured["env"]["PYTHONUNBUFFERED"] == "1"
    assert captured["stdin"] == pool.subprocess.DEVNULL and captured["stderr"] == pool.subprocess.STDOUT
    if os.name == "nt":
        assert captured["creationflags"] == (pool.subprocess.DETACHED_PROCESS
                                               | pool.subprocess.CREATE_NEW_PROCESS_GROUP
                                               | pool.subprocess.CREATE_NO_WINDOW)
    else:
        assert captured["start_new_session"] is True
    logs = list((jobs.queue / "logs").glob("mace-*.log"))
    assert len(logs) == 1 and logs[0].read_text() == "worker output\n"
    assert str(logs[0]) in capsys.readouterr().out


def test_atomic_write_preserves_destination_on_failure(pool, tmp_path, monkeypatch):
    out = tmp_path / "result.json"
    out.write_text('{"old": true}')
    real_replace = os.replace

    def interrupted_replace(src, dst):
        if Path(dst) == out:
            assert Path(src).name == f"result.json.tmp.{os.getpid()}"
            assert read(out) == {"old": True}
            raise OSError("interrupted write")
        return real_replace(src, dst)

    monkeypatch.setattr(pool.os, "replace", interrupted_replace)
    with pytest.raises(OSError, match="interrupted write"):
        pool._write_json(out, {"new": np.array([2.0])})
    assert read(out) == {"old": True} and not list(tmp_path.glob("*.tmp.*"))
