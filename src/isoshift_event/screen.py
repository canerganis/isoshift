"""Restartable per-structure harmonic screen; see each subcommand's --help.

CSV contract: one row per structure/model and pair/model, including unavailable
members. F_H_meV_atom_json and F_D_meV_atom_json are arrays on temps_K_json;
energies are per input cell before normalization by the worker's n_atoms and
formula (primitive_matrix='P'). S(300) uses a five-point derivative, step 5 K.
Any frequency below -0.1 THz in either variant quarantines the result. The worker
cannot distinguish optical modes from acoustic noise: no optical classification
is claimed. Its positive-mode-only thermodynamics are retained for audit but
never used for a quarantined pair. Mode-band/anharmonic-sensitive classification
is unavailable. Relaxed coordinates are also absent from worker output: P5/P11
identity checks are explicitly flagged as unavailable, never inferred from E/V.

Pair mathematics is isolated in pair_quantities pending acceptance of M01.
Crossings are exploratory, not transition shift predictions validated by an
offset sweep. Every root is reported (M01: exact roots are primary); a root with
|dS| < 0.01 meV/atom/K is flagged, not dropped. That guard only gates linear
delta-T estimates, and no delta-T estimate is emitted.

Two retries means at most three attempts, counting stale claims. Pool results
are never overwritten. Input/config/commit provenance is stored in the queue
manifest, since the unchanged pool does not put it in raw JSON (P19 limitation).
GPU scheduling coordinates screen-managed queues via one OS-locked registry;
independently launched GPU processes are outside this scheduler's control.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

import numpy as np

from isoshift import pool
from isoshift.calculators import DEFAULT_MODELS, MAX_ATOMS

ROOT = Path(__file__).resolve().parents[2]
TEMPS = tuple(range(0, 1001, 5))
IMAG_THRESHOLD = -0.1
RETRIES = 2
IDENTITY_FLAG = "relaxed_identity_unchecked_worker_has_no_coordinates"
STRUCTURE_FIELDS = ["E_eV_atom", "V_A3_atom", "relax_converged", "fmax_final_eV_A",
                    "min_freq_THz", "temps_K_json", "wall_s", "worker", "model_load_s"]
for _iso in ("H", "D"):
    STRUCTURE_FIELDS.extend([f"F_{_iso}_meV_atom_json", f"ZPE_{_iso}_meV_atom",
                             f"S_{_iso}_300K_meV_atom_K"])
    STRUCTURE_FIELDS.extend(f"{key}_{_iso}" for key in
                            ("min_freq_THz", "has_imaginary", "n_imag_modes", "imag_fraction"))
    STRUCTURE_FIELDS.extend(f"F_{_iso}_{t}K_meV_atom" for t in (0, 300, 600))


def _read(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def _atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp." + uuid.uuid4().hex)
    try:
        tmp.write_text(json.dumps(value, allow_nan=False, default=str), encoding="utf-8")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


@contextmanager
def _lock(path):
    """OS releases the lock after a crash; no stale lock-file deletion race."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def _safe_id(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", str(value)):
        raise ValueError(f"unsafe structure/model identifier: {value!r}")
    return str(value)


def prepare(structures, pairs, models, raw_dir, *, tier=None, steps=500):
    """Choose geometry once per unique referenced structure, before model loops."""
    from ase.io import read
    from isoshift.phonons import choose_mesh, supercell_for_min_length

    if steps <= 0:
        raise ValueError("steps must be positive")
    models = list(dict.fromkeys(models))
    if not models or any(m not in DEFAULT_MODELS for m in models):
        raise ValueError("models must be a nonempty subset of " + ",".join(DEFAULT_MODELS))
    selected = [p for p in pairs if tier is None or int(p["tier"]) <= tier]
    referenced = {p[k] for p in selected for k in ("struct_a", "struct_b")}
    by_id = {}
    for row in structures:
        sid = _safe_id(row["struct_id"])
        if sid in by_id:
            raise ValueError(f"duplicate structure id: {sid}")
        by_id[sid] = row
    missing = referenced - by_id.keys()
    if missing:
        raise ValueError("pairs reference undefined structures: " + ", ".join(sorted(missing)))
    plan = []
    for sid in sorted(referenced):
        source = by_id[sid]
        path = Path(source["cif"])
        path = (path if path.is_absolute() else ROOT / path).resolve()
        base = dict(struct_id=sid, cif=str(path), n_atoms=0, H_count=0,
                    input_sha256="", supercell_atoms=0, skip_reason="", kw={})
        try:
            base["input_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            atoms = read(path)
            n = len(atoms)
            if n != int(source["nsites"]):
                raise ValueError("CIF atom count differs from structures.csv nsites")
            sc = supercell_for_min_length(atoms, min_length=9.5, max_atoms=160)
            count = int(round(abs(np.linalg.det(sc)))) * n
            base.update(n_atoms=n, H_count=atoms.get_chemical_symbols().count("H"),
                        supercell_atoms=count,
                        kw=dict(supercell=sc.astype(int).tolist(), mesh=list(choose_mesh(atoms)),
                                temps=list(TEMPS), subs={"H": {}, "D": {"H": "D"}},
                                fmax=1e-4, relax_cell=True, steps=int(steps), max_atoms=160,
                                min_length=9.5))
            # The upstream helper stops shrinking at 6 A, even if still > cap.
            if count > 160:
                base["skip_reason"] = "shared_supercell_exceeds_160_atoms"
        except (OSError, ValueError, RuntimeError, AssertionError, IndexError) as exc:
            base["skip_reason"] = "invalid_input: " + str(exc)
        for model in models:
            entry = dict(base, model=model, out=(Path(raw_dir) / model / f"{sid}.json").resolve())
            if not entry["skip_reason"] and entry["supercell_atoms"] > MAX_ATOMS[model]:
                entry["skip_reason"] = f"skipped_model_cap_{MAX_ATOMS[model]}_shared_supercell_{entry['supercell_atoms']}"
            plan.append(entry)
    return plan


def _job_id(entry):
    value = ["harmonic", entry["cif"], entry["model"], str(entry["out"]), entry["kw"]]
    return hashlib.sha1(json.dumps(value, sort_keys=True).encode()).hexdigest()[:12]


def _commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def _retry_failed_job(failed, queue):
    """Atomically expose a retry, with its attempt already persisted."""
    job = _read(failed)
    attempts = int(job.get("attempts", 0))
    if attempts >= RETRIES:
        return False
    job.update(attempts=attempts + 1, submitted_at=time.time())
    for key in ("worker", "started_at", "finished_at", "error", "traceback", "wall_s"):
        job.pop(key, None)
    _atomic_json(failed, job)
    os.replace(failed, queue / "pending" / f"{job['id']}.json")
    return True


def submit_jobs(plan, queue_dir):
    """Idempotent submission with persisted attempt counts (never reset on retry)."""
    queue = Path(queue_dir).resolve()
    counts = dict(submitted=0, existing=0, active=0, quarantined=0)
    with _lock(queue / "screen.lock"):
        manifest_path = queue / "screen_manifest.json"
        manifest = _read(manifest_path) if manifest_path.exists() else {}
        commit = _commit()
        active_outputs = set()
        for state in ("pending", "running"):
            for path in (queue / state).glob("*.json"):
                try:
                    active_outputs.add(str(Path(_read(path)["out"]).resolve()))
                except FileNotFoundError:
                    pass  # worker moved the job while we enumerated it
        for entry in plan:
            jid = _job_id(entry)
            old = manifest.get(jid)
            if old and old["input_sha256"] != entry["input_sha256"]:
                counts["quarantined"] += 1
                continue
            if old is None:
                manifest[jid] = dict(input_sha256=entry["input_sha256"], code_commit=commit,
                                     model_id=DEFAULT_MODELS[entry["model"]],
                                     config=entry["kw"], out=str(entry["out"]),
                                     provenance="preexisting_result_unverified" if entry["out"].exists() else "submitted")
            if entry["skip_reason"]:
                counts["quarantined"] += 1
                continue
            if entry["out"].exists():
                counts["existing"] += 1
                continue
            if (str(entry["out"]) in active_outputs
                    or (queue / "pending" / f"{jid}.json").exists()
                    or any((queue / "running").glob(f"{jid}__*.json"))):
                counts["active"] += 1
                continue
            failed = queue / "failed" / f"{jid}.json"
            if failed.exists():
                if not _retry_failed_job(failed, queue):
                    counts["quarantined"] += 1
                    continue
            else:
                if (queue / "done" / f"{jid}.json").exists():
                    counts["quarantined"] += 1  # orphaned done record, never invent a result
                    continue
                # Save provenance before exposing a new job to the pool.
                _atomic_json(manifest_path, manifest)
                pool.submit(queue, "harmonic", entry["cif"], entry["model"], entry["out"], **entry["kw"])
            counts["submitted"] += 1
        _atomic_json(manifest_path, manifest)
    return counts


def _pid_alive(pid):
    """Permission denied means possibly alive: err on the side of no launch."""
    if not pid or int(pid) <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return ctypes.get_last_error() == 5
        try:
            code = wintypes.DWORD()
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def status(queue_dir, *, control_dir=None):
    data = pool.status(queue_dir)
    live = [h for h in data["heartbeats"] if h.get("state") != "exited" and _pid_alive(h.get("pid"))]
    control = Path(control_dir or ROOT / ".cache" / "screen_control") / "workers.json"
    reservations = _read(control) if control.exists() else []
    known = {h.get("pid") for h in live}
    live.extend(r for r in reservations if r["queue"] == str(Path(queue_dir).resolve())
                and r.get("pid") not in known and _pid_alive(r.get("pid")))
    data["live_workers"] = live
    failures = []
    for path in sorted((Path(queue_dir) / "failed").glob("*.json")):
        job = _read(path)
        failures.append(dict(job_id=job["id"], model=job["calc"], error=job.get("error", ""),
                             attempts=min(RETRIES + 1, int(job.get("attempts", 0)) + 1),
                             quarantined=int(job.get("attempts", 0)) >= RETRIES))
    data["failures"] = failures
    return data


def run(queue_dir=ROOT / "results" / "queue", *, device="cuda", idle_exit_s=10,
        cache_root=None, control_dir=None):
    """Nonblocking, watchdog-safe scheduling: mace+orb, then sevenn, then mattersim.

    Live PIDs are respected even before a first heartbeat or after a stale one.
    A dead launch is released; an uncertain launch intent blocks for 600 seconds.
    Pools outside screen's registry must be coordinated by their caller.
    """
    queue = Path(queue_dir).resolve()
    control = Path(control_dir or ROOT / ".cache" / "screen_control")
    launched = []
    with _lock(control / "gpu.lock"):
        registry_file = control / "workers.json"
        registry = _read(registry_file) if registry_file.exists() else []
        queues = {str(queue), *(r["queue"] for r in registry)}
        live = [r for r in registry if (_pid_alive(r.get("pid")) if r.get("pid") else
                                        time.time() - r["started_at"] < pool.STALE_S)]
        for q in sorted(queues):
            data = pool.status(q)
            for hb in data["heartbeats"]:
                if hb.get("state") != "exited" and _pid_alive(hb.get("pid")):
                    if not any(r.get("pid") == hb["pid"] for r in live):
                        live.append(dict(queue=q, calc=hb["calc"], pid=hb["pid"], started_at=hb["started_at"]))
            # Other queues are observed only for GPU exclusion. In particular,
            # dryrun must not requeue or otherwise write into real results/.
            if q != str(queue):
                continue
            # Never recover a claim out from under a live, unresponsive process.
            live_stale = any(h.get("state") != "exited" and h["age_s"] > pool.STALE_S
                             and _pid_alive(h.get("pid")) for h in data["heartbeats"])
            with _lock(Path(q) / "screen.lock"):
                if not live_stale:
                    pool.requeue_stale(q)
                manifest_file = Path(q) / "screen_manifest.json"
                manifest = _read(manifest_file) if manifest_file.exists() else {}
                for failed in (Path(q) / "failed").glob("*.json"):
                    if failed.stem in manifest:
                        _retry_failed_job(failed, Path(q))
        _atomic_json(registry_file, live)
        if (queue / "STOP").exists():
            return launched
        counts = pool.status(queue)["counts"]["pending"]
        active = {r["calc"] for r in live}
        if "sevenn" in active or "mattersim" in active:
            candidates = []
        elif active:
            candidates = [m for m in ("mace", "orb") if m not in active and counts.get(m)]
        elif any(counts.get(m) for m in ("mace", "orb")):
            candidates = [m for m in ("mace", "orb") if counts.get(m)]
        else:
            candidates = [m for m in ("sevenn", "mattersim") if counts.get(m)][:1]
        for model in candidates:
            intent = dict(queue=str(queue), calc=model, pid=None, started_at=time.time(), state="launching")
            live.append(intent)
            _atomic_json(registry_file, live)
            try:
                pid = pool.launch(model, queue, device=device, idle_exit_s=idle_exit_s,
                                  mem_fraction=0.45 if model in ("mace", "orb") else None,
                                  cache_root=cache_root)
            except Exception:
                live.remove(intent)
                _atomic_json(registry_file, live)
                raise
            intent["pid"] = pid
            _atomic_json(registry_file, live)
            launched.append(dict(model=model, pid=pid))
    return launched


def entropy_300(f_meV_atom):
    """Fourth-order central derivative: error << 0.01 meV/atom/K at 300 K."""
    i = TEMPS.index(300)
    f = np.asarray(f_meV_atom, dtype=float)
    return float((f[i+2] - 8*f[i+1] + 8*f[i-1] - f[i-2]) / 60.0)


def _composition(result):
    from ase.formula import Formula
    counts = Formula(result["formula"]).count()
    n = int(result["n_atoms"])
    if n <= 0 or sum(counts.values()) != n:
        raise ValueError("worker formula does not describe its input cell")
    return n, int(counts.get("H", 0)), {s: c/n for s, c in counts.items()}


def pair_quantities(a, b):
    """P13 beta-minus-alpha formulas, isolated until M01 acceptance.

    ddF = (F_D(b)/N_b - F_H(b)/N_b) - (F_D(a)/N_a - F_H(a)/N_a).
    Per-H normalization divides the per-atom double difference by H/N for
    matched compositions. Crossings solve E_b/N_b - E_a/N_a + F_b/N_b - F_a/N_a.
    """
    na, ha, ca = _composition(a)
    nb, hb, cb = _composition(b)
    if ca != cb:
        raise ValueError("pair composition mismatch")
    temps = np.asarray(a["temps"], dtype=float)
    if not np.array_equal(temps, b["temps"]) or not np.array_equal(temps, TEMPS):
        raise ValueError("pair temperature grid mismatch")
    fa = {s: np.asarray(a["variants"][s]["F_eV_cell"], dtype=float)*1000/na for s in ("H", "D")}
    fb = {s: np.asarray(b["variants"][s]["F_eV_cell"], dtype=float)*1000/nb for s in ("H", "D")}
    if any(v.shape != temps.shape or not np.isfinite(v).all() for v in (*fa.values(), *fb.values())):
        raise ValueError("invalid pair free-energy array")
    dd = (fb["D"] - fb["H"]) - (fa["D"] - fa["H"])
    de = 1000*(float(b["relax"]["energy"])/nb - float(a["relax"]["energy"])/na)
    if not np.isfinite(de):
        raise ValueError("nonfinite static energy")
    out = dict(dE_static_meV_atom=de)
    flags = [IDENTITY_FLAG, "crossings_exploratory_no_offset_sweep"]
    if abs(de) > 25:
        flags.append("static_gap_gt_25_meV_atom")
    for t in (0, 300, 600):
        value = float(dd[TEMPS.index(t)])
        out[f"ddF_iso_{t}K_meV_atom"] = value
        out[f"ddF_iso_{t}K_meV_H"] = value * na/ha if ha else ""
    if not ha or not hb:
        flags.append("no_hydrogen")
    # M01 (3): exact roots are primary and always reported. The 0.01 meV/atom/K
    # guard only gates linear delta-T estimates (none emitted here), so a small
    # |dS| at a root is flagged, never used to drop the root.
    gibbs = {s: de + fb[s] - fa[s] for s in ("H", "D")}
    entropy = {s: np.gradient(g, temps) for s, g in gibbs.items()}
    for isotope in ("H", "D"):
        g = gibbs[isotope]
        roots = []
        zero = np.abs(g) <= 1e-9
        if zero.all() or (zero[:-1] & zero[1:]).any():
            # identically zero (or zero over an interval): degenerate, not a set of transitions
            flags.append(f"degenerate_{isotope}")
            out[f"crossings_{isotope}_K"] = ""
            continue
        # isolated exact zeros at T > 0 count only when the sign changes across them (M01: T > 0 roots)
        candidates = [(float(temps[i]), abs(float(entropy[isotope][i]))) for i in np.flatnonzero(zero)
                      if 0 < i < len(g) - 1 and temps[i] > 0 and g[i-1] * g[i+1] < 0]
        g = np.where(zero, 0.0, g)
        for i in np.flatnonzero(g[:-1] * g[1:] < 0):
            slope = (g[i+1]-g[i])/(temps[i+1]-temps[i])
            candidates.append((float(temps[i]-g[i]/slope), abs(float(slope))))
        for root, slope in sorted(candidates):
            if roots and abs(root-roots[-1]) <= 1e-7:
                continue
            roots.append(root)
            if slope < 0.01:
                flags.append(f"crossing_{isotope}_small_slope_guard")
            if isotope == "H":
                other = abs(float(np.interp(root, temps, entropy["D"])))
                if slope < 0.01 or other < 0.01:
                    flags.append("linear_dT_blocked_slope_guard")
        out[f"crossings_{isotope}_K"] = ";".join(f"{r:.8g}" for r in roots)
        if any(r > 600 + 1e-7 for r in roots):
            flags.append(f"crossing_{isotope}_above_600K")
    out["flags"] = ";".join(dict.fromkeys(flags))
    return out


def _validate_result(entry, result):
    if result.get("status", "ok") != "ok":
        raise ValueError("raw_result_status_not_ok")
    result_job = result.get("pool", {}).get("job_id")
    if result_job is not None and result_job != _job_id(entry):
        raise ValueError("job_config_mismatch")
    if result["calc"]["name"] != entry["model"] or result["calc"]["model"] != DEFAULT_MODELS[entry["model"]]:
        raise ValueError("model_checkpoint_mismatch")
    if result["temps"] != list(TEMPS):
        raise ValueError("temperature_grid_mismatch")
    if result["mesh"] != entry["kw"]["mesh"]:
        raise ValueError("mesh_mismatch")
    sc = np.asarray(result["fc_meta"]["supercell"])
    if sc.shape == (3,):
        sc = np.diag(sc)
    if not np.array_equal(sc, entry["kw"]["supercell"]):
        raise ValueError("supercell_mismatch")
    n, h, _ = _composition(result)
    if n != entry["n_atoms"] or h != entry["H_count"]:
        raise ValueError("relaxed_cell_composition_mismatch")
    if result["fc_meta"]["natoms_supercell"] != entry["supercell_atoms"]:
        raise ValueError("supercell_atom_count_mismatch")
    numbers = [result["relax"][k] for k in ("energy", "volume", "fmax_final")]
    for iso in ("H", "D"):
        variant = result["variants"][iso]
        f = np.asarray(variant["F_eV_cell"], dtype=float)
        if f.shape != (len(TEMPS),):
            raise ValueError("free_energy_grid_length_mismatch")
        numbers.extend(f)
        numbers.extend([variant["zpe_eV_cell"], variant["imag"]["min_freq_THz"],
                        variant["imag"]["n_imag_modes"], variant["imag"]["imag_fraction"]])
    if not np.isfinite(np.asarray(numbers, dtype=float)).all():
        raise ValueError("nonfinite_result")
    return n, h


def _structure_row(entry, queue, manifest):
    row = dict.fromkeys(STRUCTURE_FIELDS, "")
    row.update(struct_id=entry["struct_id"], model=entry["model"], status="missing", reason="no_result",
               n_atoms=entry["n_atoms"], H_count=entry["H_count"],
               supercell=json.dumps(entry["kw"].get("supercell", [])),
               input_sha256=entry["input_sha256"], model_id=DEFAULT_MODELS[entry["model"]],
               model_version="", imaginary_rule="any_variant_min_freq_THz < -0.1; no optical/acoustic separation",
               limitations="mode_band_split_unavailable;raw_P19_provenance_unavailable;" + IDENTITY_FLAG)
    jid = _job_id(entry)
    provenance = manifest.get(jid, {})
    row["code_commit"] = provenance.get("code_commit", "")
    row["provenance"] = provenance.get("provenance", "unverified_pool_result")
    if provenance and provenance["input_sha256"] != entry["input_sha256"]:
        row.update(status="quarantined", reason="input_hash_mismatch")
        return row, None
    if entry["skip_reason"]:
        row.update(status="quarantined", reason=entry["skip_reason"])
        return row, None
    if not entry["out"].exists():
        failed = queue / "failed" / f"{jid}.json"
        if failed.exists():
            job = _read(failed)
            exhausted = int(job.get("attempts", 0)) >= RETRIES
            row.update(status="quarantined" if exhausted else "failed",
                       reason=("retry_budget_exhausted: " if exhausted else "") + job.get("error", "job_failed"))
        elif (queue / "done" / f"{jid}.json").exists():
            row.update(status="quarantined", reason="done_record_without_result")
        return row, None
    try:
        r = _read(entry["out"])
        n, h = _validate_result(entry, r)
        imaginary = any(v["imag"]["min_freq_THz"] < IMAG_THRESHOLD or v["imag"]["has_imaginary"]
                        for v in r["variants"].values())
        row.update(status="quarantined" if imaginary else "ok", reason="imaginary_modes" if imaginary else "",
                   n_atoms=n, H_count=h, E_eV_atom=r["relax"]["energy"]/n,
                   V_A3_atom=r["relax"]["volume"]/n, relax_converged=r["relax"]["converged"],
                   fmax_final_eV_A=r["relax"]["fmax_final"], model_version=r["calc"].get("version", ""),
                   temps_K_json=json.dumps(list(TEMPS)),
                   min_freq_THz=min(r["variants"][s]["imag"]["min_freq_THz"] for s in ("H", "D")),
                   wall_s=r.get("pool", {}).get("wall_s", ""),
                   worker=r.get("pool", {}).get("worker", ""),
                   model_load_s=r.get("pool", {}).get("model_load_s", ""))
        if not row["relax_converged"]:
            row["reason"] = ";".join(filter(None, [row["reason"], "relax_not_converged"]))
        for iso in ("H", "D"):
            v = r["variants"][iso]
            f = np.asarray(v["F_eV_cell"], dtype=float)*1000/n
            row[f"F_{iso}_meV_atom_json"] = json.dumps(f.tolist())
            row[f"ZPE_{iso}_meV_atom"] = v["zpe_eV_cell"]*1000/n
            row[f"S_{iso}_300K_meV_atom_K"] = entropy_300(f)
            for key, value in v["imag"].items():
                row[f"{key}_{iso}"] = value
            for t in (0, 300, 600):
                row[f"F_{iso}_{t}K_meV_atom"] = float(f[TEMPS.index(t)])
        return row, r
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        row.update(status="quarantined", reason="invalid_result: " + str(exc))
        return row, None


def _csv(rows, fields=None):
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _write_csv(path, rows, required):
    fields = list(dict.fromkeys([*required, *(k for r in rows for k in r)]))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp." + uuid.uuid4().hex)
    try:
        tmp.write_text(_csv(rows, fields), encoding="utf-8")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def collect(plan, pairs, queue_dir, output_dir):
    """Collect partial results; rejected members stay present with empty pair values."""
    queue = Path(queue_dir)
    manifest_path = queue / "screen_manifest.json"
    manifest = _read(manifest_path) if manifest_path.exists() else {}
    rows, valid = [], {}
    for entry in plan:
        row, raw = _structure_row(entry, queue, manifest)
        rows.append(row)
        valid[(entry["struct_id"], entry["model"])] = (row, raw)
    pair_rows = []
    for pair in pairs:
        for model in dict.fromkeys(e["model"] for e in plan):
            out = dict(pair_id=pair["pair_id"], struct_a=pair["struct_a"], struct_b=pair["struct_b"],
                       model=model, dE_static_meV_atom="", crossings_H_K="", crossings_D_K="")
            for t in (0, 300, 600):
                for unit in ("atom", "H"):
                    out[f"ddF_iso_{t}K_meV_{unit}"] = ""
            flags = list(filter(None, pair.get("flags", "").split(";")))
            members = [valid.get((pair[k], model), ({"status": "missing", "reason": "not_selected"}, None))
                       for k in ("struct_a", "struct_b")]
            for side, (row, _) in zip(("a", "b"), members):
                if row["status"] != "ok":
                    flags.append(f"{side}_{row['status']}:{row['reason']}")
                elif not row.get("relax_converged", False):
                    flags.append(f"{side}_relax_not_converged")
            if all(row["status"] == "ok" for row, _ in members):
                try:
                    quantities = pair_quantities(members[0][1], members[1][1])
                    flags.extend(quantities.pop("flags").split(";"))
                    out.update(quantities)
                    if pair["struct_a"] == pair["struct_b"]:
                        flags.append("same_input_structure")
                except (ValueError, KeyError, TypeError) as exc:
                    flags.append("invalid_pair:" + str(exc))
            else:
                flags.append(IDENTITY_FLAG)
            out["flags"] = ";".join(dict.fromkeys(flags))
            pair_rows.append(out)
    output = Path(output_dir)
    _write_csv(output / "screen_structures.csv", rows, ["struct_id", "model", "status", "reason"])
    _write_csv(output / "screen_pairs.csv", pair_rows, ["pair_id", "model", "flags"])
    return rows, pair_rows


def validation_pairs(n_pairs=3):
    """Small, deterministic fallback: first two polymorphs in each named family."""
    from ase.io import read

    index_path = ROOT / "data" / "isoshift" / "validation_structures" / "index.json"
    index = _read(index_path)
    structures, pairs = [], []
    for target in ("MgH2", "Mg(OH)2", "Ca(OH)2"):
        group = [r for r in index if r["target"] == target][:2]
        if len(group) != 2:
            raise ValueError(f"validation fallback lacks two polymorphs of {target}")
        for r in group:
            cif = index_path.parent / r["file"]
            # MP's primitive count may differ from the expanded shipped CIF.
            structures.append(dict(struct_id=r["mp_id"], nsites=len(read(cif)),
                                   cif=str(cif)))
        pairs.append(dict(pair_id=f"validation-{group[0]['mp_id']}-{group[1]['mp_id']}",
                          struct_a=group[0]["mp_id"], struct_b=group[1]["mp_id"],
                          tier="16", flags="validation_fallback"))
    pairs = pairs[:n_pairs]
    wanted = {p[k] for p in pairs for k in ("struct_a", "struct_b")}
    return [r for r in structures if r["struct_id"] in wanted], pairs


def _inputs(args, dry=False):
    if dry and (not args.structures.exists() or not args.pairs.exists()):
        structures, pairs = validation_pairs(args.n_pairs)
    else:
        with args.structures.open(encoding="utf-8-sig", newline="") as stream:
            structures = list(csv.DictReader(stream))
        with args.pairs.open(encoding="utf-8-sig", newline="") as stream:
            pairs = list(csv.DictReader(stream))
    if args.tier is not None:
        pairs = [p for p in pairs if int(p["tier"]) <= args.tier]
    if dry:
        pairs = pairs[:args.n_pairs]
    return structures, pairs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("submit", "run", "status", "collect", "dryrun"):
        ap = commands.add_parser(command, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        if command != "dryrun":
            ap.add_argument("--queue", type=Path, default=ROOT / "results" / "queue", help="Pool queue")
        if command in ("submit", "collect", "dryrun"):
            ap.add_argument("--structures", type=Path, default=ROOT / "data/isoshift/structures.csv", help="Structure manifest")
            ap.add_argument("--pairs", type=Path, default=ROOT / "data/isoshift/pairs.csv", help="Pair manifest")
            ap.add_argument("--models", default="mace,orb,sevenn,mattersim", help="Comma-separated calculators")
            ap.add_argument("--tier", type=int, choices=(16, 32), help="Maximum pair tier")
            ap.add_argument("--steps", type=int, default=500, help="Identical relaxation step limit for all models")
            if command != "dryrun":
                ap.add_argument("--output", type=Path, default=ROOT / "results", help="CSV root; raw/screen beneath it")
        if command in ("run", "dryrun"):
            ap.add_argument("--device", default="cuda", help="ASE device; GPU acceptance uses cuda")
            ap.add_argument("--idle-exit", type=float, default=10.0, help="Idle worker lifetime, seconds")
        if command == "run":
            ap.add_argument("--cache-root", type=Path, help="Optional force-constant cache")
        if command == "dryrun":
            ap.add_argument("--n-pairs", type=int, default=3, help="Number of pairs, fallback has at most three")
            ap.add_argument("--timeout", type=float, default=3600, help="Maximum seconds waiting for jobs")
            ap.add_argument("--poll", type=float, default=5, help="Seconds between queue checks")
    args = parser.parse_args(argv)
    if args.command == "status":
        print(json.dumps(status(args.queue), indent=2))
        return 0
    if args.command == "run":
        print(json.dumps(run(args.queue, device=args.device, idle_exit_s=args.idle_exit, cache_root=args.cache_root)))
        return 0
    dry = args.command == "dryrun"
    if dry and (args.n_pairs <= 0 or args.timeout <= 0 or args.poll <= 0):
        parser.error("n-pairs, timeout and poll must be positive")
    structures, pairs = _inputs(args, dry)
    output = ROOT / ".cache" / "screen_dryrun" if dry else args.output.resolve()
    queue = output / "queue" if dry else args.queue.resolve()
    plan = prepare(structures, pairs, [m.strip() for m in args.models.split(",")],
                   output / "raw" / "screen", steps=args.steps)
    if args.command == "submit":
        print(json.dumps(submit_jobs(plan, queue)))
        return 0
    if dry:
        deadline = time.monotonic() + args.timeout
        while True:
            summary = submit_jobs(plan, queue)
            run(queue, device=args.device, idle_exit_s=args.idle_exit, cache_root=output / "fc_cache")
            state = status(queue)
            outstanding = sum(sum(state["counts"][s].values()) for s in ("pending", "running"))
            print(json.dumps(dict(submission=summary, outstanding=outstanding)), flush=True)
            retryable = any(not f["quarantined"] for f in state["failures"])
            if outstanding == 0 and not retryable:
                break
            if time.monotonic() >= deadline or (queue / "STOP").exists():
                collect(plan, pairs, queue, output)
                print("Dryrun interrupted or timed out; partial tables saved, queued jobs retained.")
                return 1
            time.sleep(args.poll)
    rows, pair_rows = collect(plan, pairs, queue, output)
    print("screen_structures.csv")
    print(_csv(rows, ["struct_id", "model", "status", "reason", "F_H_300K_meV_atom", "F_D_300K_meV_atom",
                      "ZPE_H_meV_atom", "ZPE_D_meV_atom", "wall_s", "model_load_s"]), end="")
    print("screen_pairs.csv")
    print(_csv(pair_rows), end="")
    if dry:
        state = pool.status(queue)
        loads = sum(h.get("model") is not None for h in state["heartbeats"])
        print(f"model_loads_total={loads}; per-job wall_s shown above; output={output}")
        return int(not any(r["status"] == "ok" for r in rows) or
                   any(r["status"] in ("missing", "failed") or
                       (r["status"] == "quarantined" and
                        not r["reason"].startswith("imaginary_modes") and
                        not r["reason"].startswith("skipped_model_cap_")) or
                       (r["status"] == "ok" and r["H_count"] > 0 and
                        r["ZPE_D_meV_atom"] >= r["ZPE_H_meV_atom"]) for r in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
