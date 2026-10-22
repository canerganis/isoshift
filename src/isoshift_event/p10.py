"""P10 prospective held-out test of the frozen F01 rule (post-freeze addendum, decision 08 actions 4 and 5).

Subcommands, in the binding order of decision 08:
    candidates   pairs never screened, both phases experimental, <= 64 atoms (CPU, .venv)
    relax        relax-only, one persistent calculator per model (GPU; mattersim runs in .venv-sevenn)
    predict      mean model O-H per relaxed structure, eligibility, predicted signs, processing order (CPU)
    submit       harmonic phonon jobs, screen settings, in the committed order, into results/queue/p10
    decompose    mode-resolved ddF at 300 and 600 K into results/post_freeze/ (CPU)
    score        F11 scoring against the predeclared bars (CPU)

Nothing here writes to a frozen file. Inputs: data/isoshift/mp_h.json, results/atlas.csv (candidate listing only, every
quantity used is recomputed), data/isoshift/pairs.csv and results/screen_structures.csv (screened set).
Outputs: results/post_freeze/P10_*, results/post_freeze/structs/, results/raw/p10/ (raw JSON, git-ignored).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "post_freeze"
STRUCTS = OUT / "structs"
RAW = ROOT / "results" / "raw" / "p10"
QUEUE = ROOT / "results" / "queue" / "p10"
MODELS = ("mace", "orb", "mattersim")
MAX_NSITES = 64
THR, THR_SENS, MIN_DXH = 0.99, 1.00, 5.0  # A, A, mA (frozen F01)
COVALENT_CUT = 1.3  # A, decompose.COVALENT_CUT
RELAX = dict(fmax=1e-4, steps=500, relax_cell=True)  # screen.prepare settings
SC_MIN_LENGTH, SC_MAX_ATOMS = 9.5, 160  # screen.prepare settings
SOFT_MAX_FRACTION = 0.02  # refine.SOFT_MAX_FRACTION


def _id_key(sid):
    return (0 if sid.startswith("mp-") else 1, int(sid.rsplit("-", 1)[1]))


def _write_csv(path, rows, fields=None):
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ----------------------------------------------------------------------------------------------------------- candidates
def candidates():
    """Recompute the atlas grouping for the formulas concerned and apply the decision 08 pool definition."""
    from pymatgen.core import Composition, Structure
    from pymatgen.io.cif import CifWriter

    from .atlas import DE_MAX, structure_row
    from .pairs import _matches, _primitive, make_matcher, structure_flags

    entries = json.loads((ROOT / "data" / "isoshift" / "mp_h.json").read_text())
    atlas = _read_csv(ROOT / "results" / "atlas.csv")
    formulas = sorted({r["formula"] for r in atlas})
    screened_pairs = {r["pair_id"] for r in _read_csv(ROOT / "data" / "isoshift" / "pairs.csv")}
    screened = {r["struct_id"] for r in _read_csv(ROOT / "results" / "screen_structures.csv")}
    struct_rows = {r["struct_id"]: r for r in _read_csv(ROOT / "data" / "isoshift" / "structures.csv")}
    groups = {}
    for e in entries:
        f = Composition(e["formula"]).reduced_formula
        if f in formulas:
            groups.setdefault(f, []).append(e)
    matcher = make_matcher()
    rows, structs = [], {}
    for formula in formulas:
        reps = []
        # atlas.py order and dedup (pairs.py matcher and space-group gate), so the pool matches decision 08
        for e in sorted(groups.get(formula, []), key=lambda e: (e["e_per_atom_eV"], int(e["mp_id"].split("-")[1]))):
            prim = _primitive(Structure.from_dict(e["structure"]))
            r = structure_row(e, prim)
            if r["n_donors"] == 0:
                continue
            dup = next((q for q in reps if len(q["prim"]) == len(prim) and _matches(matcher, prim, q["prim"])), None)
            if dup is not None:
                dup["members"].append(e["mp_id"])
                dup["experimental"] = dup["experimental"] or not e["theoretical"]
                continue
            reps.append({"row": r, "prim": prim, "members": [e["mp_id"]], "experimental": not e["theoretical"], "entry": e})
        # screened structures of this formula, for a structural (not only ID) never-screened check
        scr = []
        for sid, sr in struct_rows.items():
            if sid in screened and sr["formula"] == formula:
                p = ROOT / sr["cif"]
                if p.exists():
                    scr.append((sid, Structure.from_file(p)))
        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                A, B = reps[i], reps[j]
                dE = 1000 * (B["row"]["e_per_atom_eV"] - A["row"]["e_per_atom_eV"])
                if abs(dE) > DE_MAX:
                    continue
                if not (A["experimental"] and B["experimental"]):
                    continue
                if len(A["prim"]) > MAX_NSITES or len(B["prim"]) > MAX_NSITES:
                    continue
                ida, idb = A["row"]["mp_id"], B["row"]["mp_id"]
                pid = "__".join(sorted((ida, idb), key=_id_key))
                if pid in screened_pairs:
                    continue
                matched = {}
                for X in (A, B):
                    hit = [m for m in X["members"] if m in screened]
                    hit += [sid for sid, s in scr if len(s) == len(X["prim"]) and _matches(matcher, X["prim"], s)]
                    matched[X["row"]["mp_id"]] = sorted(set(hit))
                if matched[ida] and matched[idb]:
                    continue  # both phases already screened (decision 08: at least one unscreened structure)
                # orientation: pairs.py convention, a = lower MP corrected formation energy, ties by numeric ID
                a, b = sorted((A, B), key=lambda X: (X["entry"]["e_form_eV"], _id_key(X["row"]["mp_id"])))
                for X in (a, b):
                    sid = X["row"]["mp_id"]
                    structs[sid] = X
                fl = set()
                for X in (a, b):
                    fl |= structure_flags(X["prim"])
                rows.append({"pair_id": pid, "formula": formula, "struct_a": a["row"]["mp_id"], "struct_b": b["row"]["mp_id"],
                             "nsites_a": len(a["prim"]), "nsites_b": len(b["prim"]),
                             "spg_a": a["row"]["spg_symbol"], "spg_b": b["row"]["spg_symbol"],
                             "dE_form_meV_atom": round(1000 * (b["entry"]["e_form_eV"] - a["entry"]["e_form_eV"]), 3),
                             "mp_mean_OH_a": round(a["row"]["mean_OH"], 5), "mp_mean_OH_b": round(b["row"]["mean_OH"], 5),
                             "mp_dOH_mA": round(1000 * (b["row"]["mean_OH"] - a["row"]["mean_OH"]), 2),
                             "mp_mean_OO_a": round(a["row"]["mean_OO"], 4), "mp_mean_OO_b": round(b["row"]["mean_OO"], 4),
                             "screened_match_a": ";".join(matched[a["row"]["mp_id"]]),
                             "screened_match_b": ";".join(matched[b["row"]["mp_id"]]),
                             "members_a": ";".join(a["members"]), "members_b": ";".join(b["members"]),
                             "flags": ";".join(sorted(fl))})
    rows.sort(key=lambda r: (r["formula"], r["pair_id"]))
    (STRUCTS / "input").mkdir(parents=True, exist_ok=True)
    srows = []
    for sid, X in sorted(structs.items(), key=lambda kv: _id_key(kv[0])):
        path = STRUCTS / "input" / f"{sid}.cif"
        if not path.exists():
            path.write_text(str(CifWriter(X["prim"], symprec=None, significant_figures=10)))
        srows.append({"struct_id": sid, "formula": Composition(X["entry"]["formula"]).reduced_formula,
                      "nsites": len(X["prim"]), "spg": X["row"]["spg_symbol"], "mp_mean_OH": round(X["row"]["mean_OH"], 5),
                      "members": ";".join(X["members"]), "cif": str(path.relative_to(ROOT)).replace("\\", "/")})
    _write_csv(OUT / "P10_candidates.csv", rows)
    _write_csv(OUT / "P10_structures.csv", srows)
    nf = len({r["formula"] for r in rows})
    print(f"candidate pairs {len(rows)} in {nf} formulas; unique structures {len(srows)}")


# ---------------------------------------------------------------------------------------------------------------- relax
def relax(model, device="cuda"):
    """One persistent calculator per model; relax every candidate structure with the screen's settings."""
    from ase.io import read, write

    sys.path.insert(0, str(ROOT))
    from isoshift.calculators import calculator_info, get_calculator
    from isoshift.relax import relax as do_relax

    import torch

    if torch.cuda.is_available():
        frac = float(os.environ.get("P10_MEM_FRACTION", "0.4"))
        torch.cuda.set_per_process_memory_fraction(frac, device="cuda:0")
    t0 = time.time()
    calc = get_calculator(model, device)
    info = calculator_info(calc)
    print(f"loaded {model} in {time.time() - t0:.1f} s", flush=True)
    out = STRUCTS / "relaxed" / model
    out.mkdir(parents=True, exist_ok=True)
    todo = _read_csv(OUT / "P10_structures.csv")
    if os.environ.get("P10_REVERSE"):  # second worker per model walks the list from the end; results are per structure
        todo = todo[::-1]
    for s in todo:
        sid = s["struct_id"]
        meta = out / f"{sid}.json"
        if meta.exists():
            continue
        while (QUEUE / "PAUSE").exists():  # thermal guard (GPU at 87 C or above) or time window
            time.sleep(10)
        t = time.time()
        try:
            a, rinfo = do_relax(read(ROOT / s["cif"]), calc, **RELAX)
            write(out / f"{sid}.extxyz", a, format="extxyz")
            rinfo.update(status="ok", wall_s=time.time() - t, calc=info, n_atoms=len(a))
        except Exception as exc:  # recorded and reported, never silently dropped
            rinfo = {"status": "failed", "error": " ".join(str(exc).splitlines())[:500], "wall_s": time.time() - t, "calc": info}
        meta.write_text(json.dumps(rinfo, default=float))
        print(f"{model} {sid} {rinfo['status']} {rinfo.get('steps', '')} steps {rinfo['wall_s']:.1f} s "
              f"conv={rinfo.get('converged', '')}", flush=True)
    print(f"done {model} {time.time() - t0:.1f} s", flush=True)


# -------------------------------------------------------------------------------------------------------------- predict
def xh_geometry(atoms):
    """Frozen decompose.py definition: per H, distance to the nearest non-H atom (fractional minimum image).
    Also the full minimum-image distance and the nearest-neighbour element, for audit."""
    sym = np.array(atoms.get_chemical_symbols())
    H, heavy = np.flatnonzero(sym == "H"), np.flatnonzero(sym != "H")
    cell, frac = np.asarray(atoms.cell), atoms.get_scaled_positions()
    d_dec, d_mic, el = [], [], []
    for i in H:
        d = frac[heavy] - frac[i]
        d -= np.round(d)
        cart = d @ cell
        k = int(np.argmin(np.linalg.norm(cart, axis=1)))
        d_dec.append(float(np.linalg.norm(cart[k])))
        dm = atoms.get_distances(i, heavy, mic=True)
        d_mic.append(float(dm.min()))
        el.append(str(sym[heavy[int(np.argmin(dm))]]))
    return {"XH_mean_A": float(np.mean(d_dec)), "XH_max_A": float(np.max(d_dec)), "XH_mean_mic_A": float(np.mean(d_mic)),
            "covalent_XH": bool(max(d_dec) < COVALENT_CUT), "n_H": int(len(H)), "n_OH": int(sum(e == "O" for e in el)),
            "nn_elements": ";".join(sorted(set(el)))}


def _frozen_baseline():
    """Constant sign of ddF_iso/H over the frozen 212 headline rows (decision 07), and over the frozen O-H rows with
    |dX-H| >= 5 mA at 600 K (refined column, decision 08 table), for the secondary rule."""
    import pandas as pd

    from . import rule_cv as R

    c = R.load()
    h = c[(c.x.abs() >= R.MIN_DXH) & c.OH & (c.rmax >= R.MAIN_THR)]
    s300 = R._majority_sign(h.y.values)
    r = pd.read_csv(ROOT / "results" / "screen_pairs_refined.csv").drop_duplicates(["pair_id", "model"], keep="last")
    m = c.merge(r[["pair_id", "model", "ddF_iso_600K_refined_meV_atom"]], on=["pair_id", "model"], how="left")
    o = m[m.OH & (m.x.abs() >= R.MIN_DXH)]
    s600 = R._majority_sign(o["ddF_iso_600K_refined_meV_atom"].values)
    return {"n_headline": int(len(h)), "n_pos_300": int((h.y > 0).sum()), "sign_300K": int(s300),
            "n_oh_600": int(len(o)), "n_pos_600": int((o["ddF_iso_600K_refined_meV_atom"] > 0).sum()), "sign_600K": int(s600)}


def _supercell(cif):
    from ase.io import read

    from isoshift.phonons import supercell_for_min_length

    atoms = read(cif)
    sc = supercell_for_min_length(atoms, min_length=SC_MIN_LENGTH, max_atoms=SC_MAX_ATOMS)
    return sc.astype(int), int(round(abs(np.linalg.det(sc)))) * len(atoms)


def _same_phase(a1, a2):
    from pymatgen.io.ase import AseAtomsAdaptor

    from .refine import _same_phase as same

    def r(a):
        s = AseAtomsAdaptor.get_structure(a)
        return {"cell": s.lattice.matrix.tolist(), "symbols": [x.specie.symbol for x in s], "frac": s.frac_coords.tolist()}

    return same(r(a1), r(a2))


def order_pairs(pairs, cost):
    """Decision 08: fewest supercell atoms first; at least 6 formulas covered before a seventh pair from any formula."""
    queue = sorted(pairs, key=lambda p: (cost[p["pair_id"]], p["pair_id"]))
    done, per_formula, deferred = [], {}, []
    for p in queue:
        covered = len(per_formula)
        if per_formula.get(p["formula"], 0) >= 6 and covered < 6:
            deferred.append(p)
            continue
        done.append(p)
        per_formula[p["formula"]] = per_formula.get(p["formula"], 0) + 1
        while deferred and len(per_formula) >= 6:
            q = deferred.pop(0)
            done.append(q)
            per_formula[q["formula"]] += 1
    return done + deferred


def predict():
    from ase.io import read

    cand = _read_csv(OUT / "P10_candidates.csv")
    sinfo = {s["struct_id"]: s for s in _read_csv(OUT / "P10_structures.csv")}
    atlas = {}
    for r in _read_csv(ROOT / "results" / "atlas.csv"):
        atlas[(r["mp_a"], r["mp_b"])] = int(r["pred_sign_ddF"])
        atlas[(r["mp_b"], r["mp_a"])] = -int(r["pred_sign_ddF"])
    base = _frozen_baseline()
    geo, relaxed, srows = {}, {}, []
    for sid, s in sorted(sinfo.items(), key=lambda kv: _id_key(kv[0])):
        sc, nsc = _supercell(ROOT / s["cif"])
        s["supercell"], s["supercell_atoms"] = json.dumps(np.diag(sc).tolist()), nsc
        for m in MODELS:
            meta_p = STRUCTS / "relaxed" / m / f"{sid}.json"
            row = {"struct_id": sid, "model": m, "formula": s["formula"], "nsites": s["nsites"], "supercell_atoms": nsc}
            if not meta_p.exists():
                row["relax_status"] = "missing"
            else:
                meta = json.loads(meta_p.read_text())
                row["relax_status"] = meta["status"]
                if meta["status"] == "ok":
                    a = read(STRUCTS / "relaxed" / m / f"{sid}.extxyz")
                    relaxed[(m, sid)] = a
                    g = xh_geometry(a)
                    geo[(m, sid)] = g
                    row.update(relax_converged=meta["converged"], relax_steps=meta["steps"],
                               fmax_final=f"{meta['fmax_final']:.3g}", E_eV_atom=meta["energy"] / len(a),
                               V_A3_atom=meta["volume"] / len(a), **{k: (round(v, 6) if isinstance(v, float) else v) for k, v in g.items()})
            srows.append(row)
    _write_csv(OUT / "P10_relaxed_structures.csv", srows)
    rows = []
    for p in cand:
        a, b = p["struct_a"], p["struct_b"]
        for m in MODELS:
            r = {"pair_id": p["pair_id"], "formula": p["formula"], "model": m, "struct_a": a, "struct_b": b}
            ga, gb = geo.get((m, a)), geo.get((m, b))
            flags = [f for f in p["flags"].split(";") if f]
            if ga is None or gb is None:
                r.update(eligible_primary=False, eligible_secondary=False, status="relax_failed")
                rows.append(r)
                continue
            x = 1000 * (gb["XH_mean_A"] - ga["XH_mean_A"])
            rmax = max(ga["XH_mean_A"], gb["XH_mean_A"])
            same = _same_phase(relaxed[(m, a)], relaxed[(m, b)])
            cov = ga["covalent_XH"] and gb["covalent_XH"]
            for side, sid in (("a", a), ("b", b)):
                meta = json.loads((STRUCTS / "relaxed" / m / f"{sid}.json").read_text())
                if not meta.get("converged", False):
                    flags.append(f"{side}_relax_not_converged")
            if same:
                flags.append("same_relaxed_structure")
            if not cov:
                flags.append("not_covalent_XH")
            ok = (not same) and cov
            big = abs(x) >= MIN_DXH
            prim = ok and big and rmax >= THR
            sign = int(np.sign(x)) if x != 0 else 0
            atl = atlas.get((a, b))
            r.update(status="same_relaxed_structure" if same else ("not_covalent" if not cov else "ok"),
                     XH_mean_a=round(ga["XH_mean_A"], 5), XH_mean_b=round(gb["XH_mean_A"], 5), rmax_A=round(rmax, 5),
                     dXH_mean_mA=round(x, 3),
                     eligible_primary=bool(prim), eligible_primary_1p00=bool(ok and big and rmax >= THR_SENS),
                     eligible_secondary=bool(ok and big),
                     pred_sign_ddF_300K_primary=sign if prim else "",
                     pred_sign_ddF_600K_secondary=sign if (ok and big) else "",
                     D_favours=(a if sign > 0 else b) if (ok and big) else "",
                     baseline_sign_300K=base["sign_300K"], baseline_sign_600K=base["sign_600K"],
                     P08_mp_geometry_sign=atl if atl is not None else "",
                     supercell_atoms_a=sinfo[a]["supercell_atoms"], supercell_atoms_b=sinfo[b]["supercell_atoms"],
                     flags=";".join(dict.fromkeys(flags)))
            rows.append(r)
    # processing order: pairs with a primary-eligible row first, then secondary-only pairs; within each tier the
    # decision 08 rule (fewest supercell atoms first, >= 6 formulas before a seventh pair from any formula)
    by_pair = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)
    cost = {p: max(int(sinfo[q[0]["struct_a"]]["supercell_atoms"]), int(sinfo[q[0]["struct_b"]]["supercell_atoms"]))
            for p, q in by_pair.items()}
    tier1 = [p for p in cand if any(r["eligible_primary"] for r in by_pair[p["pair_id"]])]
    tier2 = [p for p in cand if p not in tier1 and any(r["eligible_secondary"] for r in by_pair[p["pair_id"]])]
    order = {}
    for p in order_pairs(tier1, cost) + order_pairs(tier2, cost):
        order[p["pair_id"]] = len(order) + 1
    for r in rows:
        r["order"] = order.get(r["pair_id"], "")
        r["tier"] = 1 if r["pair_id"] in {p["pair_id"] for p in tier1} else (2 if r["order"] else "")
        r["pair_cost_supercell_atoms"] = cost[r["pair_id"]]
    rows.sort(key=lambda r: (r["order"] if r["order"] != "" else 10**6, r["pair_id"], MODELS.index(r["model"])))
    fields = ["order", "tier", "pair_id", "formula", "model", "struct_a", "struct_b", "status", "XH_mean_a", "XH_mean_b",
              "rmax_A", "dXH_mean_mA", "eligible_primary", "eligible_primary_1p00", "eligible_secondary",
              "pred_sign_ddF_300K_primary", "pred_sign_ddF_600K_secondary", "D_favours", "baseline_sign_300K",
              "baseline_sign_600K", "P08_mp_geometry_sign", "supercell_atoms_a", "supercell_atoms_b",
              "pair_cost_supercell_atoms", "flags"]
    _write_csv(OUT / "P10_predictions.csv", rows, fields)
    (OUT / "P10_baseline.json").write_text(json.dumps(base, indent=1))
    pe = [r for r in rows if r["eligible_primary"]]
    se = [r for r in rows if r["eligible_secondary"]]
    print(f"primary-eligible rows {len(pe)} in {len({r['pair_id'] for r in pe})} pairs, "
          f"{len({r['formula'] for r in pe})} formulas; secondary rows {len(se)} in {len({r['pair_id'] for r in se})} pairs; "
          f"ordered pairs {len(order)}; baseline {base}")


# --------------------------------------------------------------------------------------------------------------- submit
def plan_jobs(max_order=None, min_order=1):
    """(order, model, sid, cif, out, kw) per structure-model, in the committed pair order, each structure once."""
    from .screen import TEMPS

    rows = _read_csv(OUT / "P10_predictions.csv")
    sinfo = {s["struct_id"]: s for s in _read_csv(OUT / "P10_structures.csv")}
    jobs, seen = [], set()
    for r in rows:
        if not r["order"] or (max_order is not None and int(r["order"]) > max_order) or int(r["order"]) < min_order:
            continue
        for sid in (r["struct_a"], r["struct_b"]):
            key = (r["model"], sid)
            if key in seen:
                continue
            seen.add(key)
            cif = STRUCTS / "relaxed" / r["model"] / f"{sid}.extxyz"
            if not cif.exists():
                continue
            sc, nsc = _supercell(ROOT / sinfo[sid]["cif"])
            kw = dict(supercell=sc.tolist(), mesh=None, temps=list(TEMPS), subs={"H": {}, "D": {"H": "D"}},
                      fmax=RELAX["fmax"], relax_cell=True, steps=RELAX["steps"], max_atoms=SC_MAX_ATOMS, min_length=SC_MIN_LENGTH)
            from ase.io import read

            from isoshift.phonons import choose_mesh

            kw["mesh"] = list(choose_mesh(read(ROOT / sinfo[sid]["cif"])))  # screen: mesh from the input structure
            skip = "shared_supercell_exceeds_160_atoms" if nsc > SC_MAX_ATOMS else ""
            jobs.append(dict(order=int(r["order"]), model=r["model"], sid=sid, cif=str(cif), out=str(RAW / r["model"] / f"{sid}.json"),
                             kw=kw, supercell_atoms=nsc, skip=skip))
    return jobs


def submit(max_order=None, models=MODELS, dry=False, min_order=1):
    sys.path.insert(0, str(ROOT))
    from isoshift import pool

    jobs = [j for j in plan_jobs(max_order, min_order) if j["model"] in models]
    n = 0
    for j in jobs:
        if j["skip"]:
            continue
        if not dry:
            pool.submit(QUEUE, "harmonic", j["cif"], j["model"], j["out"], **j["kw"])
            time.sleep(0.002)  # distinct submitted_at keeps the claim order equal to the committed order
        n += 1
    print(f"submitted {n} jobs (order {min_order} to {max_order}), skipped {sum(1 for j in jobs if j['skip'])}")


# ------------------------------------------------------------------------------------------------------------ decompose
def _dec_one(args):
    t, job = args
    from . import decompose

    decompose.T = t
    r = decompose._one(job)
    if r:
        r["T_K"] = t
    return r


def decompose_all(workers=6):
    from concurrent.futures import ProcessPoolExecutor

    from . import refine

    idx = refine._cache_index()
    jobs, missing = [], []
    for m in MODELS:
        for f in sorted((RAW / m).glob("*.json")) if (RAW / m).exists() else []:
            r = json.loads(f.read_text())
            calc = "{name}-{model}".format(**r["calc"])
            safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in calc)
            key = (safe, round(r["fc_meta"]["energy_eV"], 6), round(r["fc_meta"]["volume_A3"], 4))
            if key in idx:
                jobs.append((m, f.stem, str(idx[key])))
            else:
                missing.append(f"{m}/{f.stem}")
    res = []
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(_dec_one, [(t, j) for t in (300.0, 600.0) for j in jobs], chunksize=1):
            if r:
                res.append(r)
    _write_csv(OUT / "P10_decompose_structures.csv", res)
    print(f"decomposed {len(res)} structure-temperature rows; no cache match: {missing}")


# ---------------------------------------------------------------------------------------------------------------- score
def _phonon_status(model, sid):
    """ok | soft_mode_bracketed | unstable:<reason> | failed:<reason> | not_computed, from the raw pool output."""
    out = RAW / model / f"{sid}.json"
    if out.exists():
        r = json.loads(out.read_text())
        fr = max(r["variants"][s]["imag"]["imag_fraction"] for s in ("H", "D"))
        mn = min(r["variants"][s]["imag"]["min_freq_THz"] for s in ("H", "D"))
        if mn < -0.1 or any(r["variants"][s]["imag"]["has_imaginary"] for s in ("H", "D")):
            if fr <= SOFT_MAX_FRACTION:
                return "soft_mode_bracketed", r
            return f"unstable:imag_fraction_{fr:.3g}", r
        return "ok", r
    for f in (QUEUE / "failed").glob("*.json"):
        j = json.loads(f.read_text())
        if j.get("calc") == model and Path(j["out"]).name == f"{sid}.json":
            return "failed:" + j.get("error", "")[:200], None
    return "not_computed", None


def _known_formulas():
    """Formulas present in the frozen F01 population (rule_cv.load(), three models): 'structure transfer' subset."""
    from . import rule_cv as R

    return set(R.load().family.unique())


def _pair_value(dec, model, a, b, t):
    """ddF_iso(b - a) per H from the decompose quadrature (frozen F01 y), plus the clean flag (decompose.py rule)."""
    ra, rb = dec.get((model, a, t)), dec.get((model, b, t))
    if ra is None or rb is None:
        return None, None, "decompose_missing"
    qa, qb = float(ra["dF_quad_meV_atom"]), float(rb["dF_quad_meV_atom"])
    clean = abs(qa - float(ra["dF_direct_meV_atom"])) < 0.01 and abs(qb - float(rb["dF_direct_meV_atom"])) < 0.01
    h_per_atom = int(ra["n_H"]) / int(ra["n_atoms"])
    return (qb - qa) / h_per_atom, clean, ""


def _block(rows, base_key):
    """Counts for evaluated rows; failed, unstable and unclean rows are in the denominator and never right."""
    n = len(rows)
    right = sum(bool(r["right"]) for r in rows)
    base = sum(bool(r["baseline_right_" + base_key]) for r in rows)
    pairs = {}
    for r in rows:
        pairs.setdefault(r["pair_id"], []).append(bool(r["right"]))
    maj = {"right": sum(np.mean(v) > 0.5 for v in pairs.values()), "tie": sum(np.mean(v) == 0.5 for v in pairs.values()),
           "wrong": sum(np.mean(v) < 0.5 for v in pairs.values())}
    per_model = {}
    for r in rows:
        d = per_model.setdefault(r["model"], {"right": 0, "n": 0})
        d["right"] += int(bool(r["right"]))
        d["n"] += 1
    return {"n": n, "right": int(right), "acc": round(right / n, 4) if n else None, "baseline_right": int(base),
            "baseline_acc": round(base / n, 4) if n else None,
            "points_above_baseline": round(100 * (right - base) / n, 1) if n else None,
            "n_pairs": len(pairs), "n_formulas": len({r["formula"] for r in rows}),
            "unique_pair_majority": {k: int(v) for k, v in maj.items()},
            "pair_majority_right_frac": round(maj["right"] / len(pairs), 4) if pairs else None,
            "n_failures_counted_not_right": sum(1 for r in rows if r["outcome"] != "scored"),
            "per_model": per_model}


def score():
    pred = _read_csv(OUT / "P10_predictions.csv")
    dec = {}
    if (OUT / "P10_decompose_structures.csv").exists():
        for r in _read_csv(OUT / "P10_decompose_structures.csv"):
            dec[(r["model"], r["struct_id"], float(r["T_K"]))] = r
    known = _known_formulas()
    base = json.loads((OUT / "P10_baseline.json").read_text())
    rows, not_computed = [], []
    for p in pred:
        if not p["order"] or p["eligible_secondary"] != "True":
            continue
        st = {side: _phonon_status(p["model"], p["struct_" + side])[0] for side in ("a", "b")}
        r = {k: p[k] for k in ("order", "tier", "pair_id", "formula", "model", "struct_a", "struct_b", "dXH_mean_mA", "rmax_A",
                                "eligible_primary", "eligible_primary_1p00", "eligible_secondary", "P08_mp_geometry_sign")}
        r["known_formula"] = p["formula"] in known
        r["status_a"], r["status_b"] = st["a"], st["b"]
        if "not_computed" in st.values():
            not_computed.append({"order": int(p["order"]), "pair_id": p["pair_id"], "model": p["model"],
                                 "eligible_primary": p["eligible_primary"] == "True", "status_a": st["a"], "status_b": st["b"]})
            continue
        sign = int(np.sign(float(p["dXH_mean_mA"])))
        for t in (300.0, 600.0):
            rr = dict(r, T_K=int(t), pred_sign=sign)
            bad = [v for v in st.values() if v.startswith(("failed", "unstable"))]
            y, clean, why = (None, None, "") if bad else _pair_value(dec, p["model"], p["struct_a"], p["struct_b"], t)
            if bad:
                rr.update(outcome="failed_or_unstable", reason=";".join(bad), right=False)
            elif y is None:
                rr.update(outcome="failed_or_unstable", reason=why, right=False)
            elif not clean:
                rr.update(outcome="not_clean", reason="quadrature_vs_direct_gt_0.01_meV_atom", y_meV_H=round(y, 5), right=False)
            else:
                rr.update(outcome="scored", reason="", y_meV_H=round(y, 5), right=bool(np.sign(y) == sign))
            yv = rr.get("y_meV_H")
            for k in ("300K", "600K"):
                rr["baseline_right_" + k] = bool(yv is not None and rr["outcome"] == "scored" and np.sign(yv) == base["sign_" + k])
            rr["soft_mode_bracketed"] = "soft_mode_bracketed" in st.values()
            rows.append(rr)
    prim = [r for r in rows if r["T_K"] == 300 and r["eligible_primary"] == "True"]
    sec = [r for r in rows if r["T_K"] == 600]
    pb, sb = _block(prim, "300K"), _block(sec, "600K")
    enough = pb["n"] >= 30 and pb["n_pairs"] >= 12 and pb["n_formulas"] >= 6
    bars = {"min_size_30_evals_12_pairs_6_formulas": enough,
            "pooled_acc_ge_0.75": bool(pb["acc"] is not None and pb["acc"] >= 0.75),
            "ge_15_points_above_baseline": bool(pb["points_above_baseline"] is not None and pb["points_above_baseline"] >= 15),
            "pair_majority_right_ge_0.80": bool(pb["pair_majority_right_frac"] is not None and pb["pair_majority_right_frac"] >= 0.80)}
    verdict = ("descriptive only (below 30 evaluations, 12 pairs or 6 formulas)" if not enough else
               "PASS" if all(bars.values()) else "FAIL")
    out = {"status": "post-freeze addendum, prospective",
           "prediction_file": "docs/predictions/P10_prospective.md, results/post_freeze/P10_predictions.csv",
           "baseline": base,
           "primary": {"rule": "frozen F01 at 300 K: sign(ddF_iso(b-a)/H) = sign(d mean model O-H(b-a)); rmax >= 0.99 A, |d| >= 5 mA",
                       **pb, "bars": bars, "verdict": verdict},
           "secondary": {"rule": "600 K, no threshold, all O-H pairs with |d| >= 5 mA", **sb,
                         "bar_acc_ge_0.90": bool(sb["acc"] is not None and sb["acc"] >= 0.90)},
           "primary_per_protocol_clean_only": _block([r for r in prim if r["outcome"] == "scored"], "300K"),
           "primary_sensitivity_1p00": _block([r for r in prim if r["eligible_primary_1p00"] == "True"], "300K"),
           "primary_structure_transfer_known_formula": _block([r for r in prim if r["known_formula"]], "300K"),
           "primary_new_formula": _block([r for r in prim if not r["known_formula"]], "300K"),
           "secondary_per_protocol_clean_only": _block([r for r in sec if r["outcome"] == "scored"], "600K"),
           "weak_side_300K_descriptive": _block([r for r in rows if r["T_K"] == 300 and r["eligible_primary"] != "True"], "300K"),
           "failures": [{k: r[k] for k in ("order", "pair_id", "model", "T_K", "outcome", "reason")} for r in rows if r["outcome"] != "scored"],
           "not_computed_in_committed_order": sorted(not_computed, key=lambda r: (r["order"], r["pair_id"], r["model"]))}
    _write_csv(OUT / "P10_scored_rows.csv", rows)
    (OUT / "F11_prospective.json").write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(json.dumps({k: out[k] for k in ("primary", "secondary")}, indent=1, default=str)[:4000])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("candidates")
    p = sub.add_parser("relax")
    p.add_argument("--model", required=True, choices=MODELS)
    p.add_argument("--device", default="cuda")
    sub.add_parser("predict")
    p = sub.add_parser("submit")
    p.add_argument("--max-order", type=int)
    p.add_argument("--min-order", type=int, default=1)
    p.add_argument("--models", default=",".join(MODELS))
    p.add_argument("--dry", action="store_true")
    p = sub.add_parser("decompose")
    p.add_argument("--workers", type=int, default=6)
    sub.add_parser("score")
    a = ap.parse_args(argv)
    if a.cmd == "candidates":
        candidates()
    elif a.cmd == "relax":
        relax(a.model, a.device)
    elif a.cmd == "predict":
        predict()
    elif a.cmd == "submit":
        submit(a.max_order, tuple(a.models.split(",")), a.dry, a.min_order)
    elif a.cmd == "decompose":
        decompose_all(a.workers)
    else:
        score()


if __name__ == "__main__":
    main()
