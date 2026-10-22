"""EXPLORATORY, PARKED (council 08): not a finding, not part of the frozen headline. Incomplete run:
GaOOH/Ca(OH)2/CrOOH QHA jobs partly done, rest parked in results/queue/deep/parked/; no P07 or finding written.
results/deep_earth.json holds only the AlOOH/FeOOH reanalysis of the card raw files (AlOOH reproduces the card).

P07 addendum (planned): isotope shift of hydrous polymorph boundaries and inter-phase D/H fractionation (post-freeze).

Same-composition, H-ordered polymorph pairs only (both phases from Materials Project or JARVIS, <= 64 atoms).
Per pair and model: QHA G(T, P) for H and D at 3 pressures bracketing the boundary (isoshift.qha via the
persistent pool), rebuilt Gamma-free on a 0 to 1550 K grid exactly as card_temperature.py, with the decision 02
imaginary-mode bracket (omit vs |w|). Per T:
    P_t^X = root of a linear fit of dG_X(P) = G_high - G_low (per atom) through the 3 pressures, X in {H, D};
    dP_iso = P_t^D - P_t^H;
    M02 bridge: n_H kT ln alpha(low-high) = ddG_iso = [G_D - G_H]_high - [G_D - G_H]_low per f.u.,
    evaluated at P_t^H(T) by linear interpolation of ddG_iso(P) over the pressures run.
alpha(low-high) > 1 (positive 1000 ln alpha) means deuterium prefers the low-pressure phase.

    python -m src.isoshift_event.deep_earth fetch      # MP structures + provenance CSV
    python -m src.isoshift_event.deep_earth scan --model mace   # static H(P) crossings, picks pressures
    python -m src.isoshift_event.deep_earth submit --models mace,orb
    python -m src.isoshift_event.deep_earth analyze    # results/deep_earth.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STRUCTS = ROOT / "data" / "isoshift" / "structs"
RAW_CARD = ROOT / "results" / "raw" / "qha_pressure"
RAW_DEEP = ROOT / "results" / "raw" / "qha_deep"
QUEUE = ROOT / "results" / "queue" / "deep"
PROV = ROOT / "data" / "isoshift" / "deep_earth_structures.csv"
SCAN = ROOT / "results" / "deep_earth_static.json"
OUT = ROOT / "results" / "deep_earth.json"
KB = 8.617333262145e-5
EV_A3_GPA = 160.21766208
TEMPS = np.arange(0.0, 1601.0, 50.0)
REPORT_T = (300, 1000, 1500)
SCAN_P = (0, 2, 5, 8, 10, 15, 20, 25, 30, 40, 50, 60)

# low = low-pressure phase, high = high-pressure (denser) phase; fu = atoms per formula unit, nH per f.u.
PAIRS = {
    "AlOOH": {"low": "mp-625152", "high": "mp-23807", "fu": 4, "nH": 1, "P": (10, 15, 20), "raw": RAW_CARD,
              "names": ("diaspore", "delta-AlOOH (InOOH-type, P2_1nm)")},
    "FeOOH": {"low": "mp-605437", "high": "JVASP-92228", "fu": 4, "nH": 1, "P": (3, 6, 9), "raw": RAW_CARD,
              "names": ("goethite", "epsilon-FeOOH (InOOH-type)")},
    "GaOOH": {"low": "mp-634326", "high": "mp-23803", "fu": 4, "nH": 1, "P": (3, 7, 11), "raw": RAW_DEEP,
              "names": ("alpha-GaOOH (diaspore-type)", "InOOH-type GaOOH (P2_1nm)")},
    "Ca(OH)2": {"low": "mp-23879", "high": "mp-643392", "fu": 5, "nH": 2, "P": (2, 5, 8), "raw": RAW_DEEP,
                "names": ("portlandite (P-3m1)", "high-pressure Ca(OH)2 (P2_1/c, ICSD 84867)")},
    # excluded from QHA: static scan shows Pm relaxing continuously into P2/m above about 20 GPa (H-bond
    # symmetrisation, dH -> 0), so there is no first-order boundary to shift (results/deep_earth_static.json)
    "MgSiO4H2": {"low": "mp-1078877", "high": "mp-1078468", "fu": 8, "nH": 2, "P": None, "raw": RAW_DEEP,
                 "names": ("phase H model, Pm (asymmetric H bond)", "phase H model, P2/m")},
    "CrOOH": {"low": "mp-23910", "high": "mp-24040", "fu": 4, "nH": 1, "P": (0, 2, 4), "raw": RAW_DEEP,
              "names": ("grimaldiite-type (R3m)", "InOOH-type CrOOH (P2_1nm)")},
}
QHA_KW = {"n_vol": 11, "min_length": 9.5, "max_atoms": 160, "temps": [0, 100, 200, 300, 400]}


# ---------------------------------------------------------------- fetch
def fetch():
    """Write missing CIFs (primitive MP structure) and a provenance row for every structure used."""
    from mp_api.client import MPRester

    from .fetch_mp import _api_key

    ids = sorted({p[k] for p in PAIRS.values() for k in ("low", "high") if p[k].startswith("mp-")})
    rows = []
    with MPRester(_api_key()) as m:
        dbv = m.get_database_version()
        docs = m.materials.summary.search(material_ids=ids, fields=[
            "material_id", "formula_pretty", "symmetry", "nsites", "energy_above_hull", "volume", "theoretical",
            "database_IDs", "structure"])
    for d in docs:
        sid = str(d.material_id)
        cif = STRUCTS / f"{sid}.cif"
        new = not cif.exists()
        if new:
            d.structure.to(filename=str(cif))
        icsd = ";".join(str(x) for x in (d.database_IDs or {}).get("icsd", []))
        rows.append({"struct_id": sid, "source": "materials_project", "mp_database_version": dbv,
                     "formula": d.formula_pretty, "spg": d.symmetry.symbol, "spg_number": d.symmetry.number,
                     "nsites": d.nsites, "e_above_hull_eV_atom": round(d.energy_above_hull, 4),
                     "volume_A3_atom": round(d.volume / d.nsites, 4), "theoretical": d.theoretical, "icsd_ids": icsd,
                     "cif": f"data/isoshift/structs/{sid}.cif", "cif_written_now": new,
                     "fetched": time.strftime("%Y-%m-%d")})
    rows.append({"struct_id": "JVASP-92228", "source": "jarvis dft_3d (data/isoshift/dft_3d.pkl)", "mp_database_version": "",
                 "formula": "FeHO2", "spg": "Pmn2_1", "spg_number": 31, "nsites": 8, "e_above_hull_eV_atom": "",
                 "volume_A3_atom": "", "theoretical": False, "icsd_ids": "420002;420003;87325",
                 "cif": "data/isoshift/structs/JVASP-92228.cif", "cif_written_now": False,
                 "fetched": "pre-existing (CARD-AlOOH)"})
    with open(PROV, "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["struct_id"]))
    for r in rows:
        print(r["struct_id"], r["formula"], r["spg"], r["nsites"], r["e_above_hull_eV_atom"], r["theoretical"], r["icsd_ids"])


# ---------------------------------------------------------------- static scan
def scan(model: str, device: str = "cuda", pairs=None):
    """Static enthalpy H(P) per atom along SCAN_P (symmetry-fixed relax), crossing per pair."""
    from ase.io import read

    from isoshift.calculators import get_calculator
    from isoshift.relax import relax

    calc = get_calculator(model, device)
    res = json.loads(SCAN.read_text()) if SCAN.exists() else {}
    for name, p in PAIRS.items():
        if pairs and name not in pairs:
            continue
        hh = {}
        for side in ("low", "high"):
            a = read(STRUCTS / f"{p[side]}.cif")
            n = len(a)
            hs, vs = [], []
            for P in SCAN_P:
                a, info = relax(a, calc, fmax=5e-3, steps=800, scalar_pressure=P / EV_A3_GPA)
                hs.append((info["energy"] + P / EV_A3_GPA * info["volume"]) / n * 1000)
                vs.append(info["volume"] / n)
            hh[side] = {"H_meV_atom": hs, "V_A3_atom": vs}
        dh = np.array(hh["high"]["H_meV_atom"]) - np.array(hh["low"]["H_meV_atom"])
        cross = None
        for i in range(len(SCAN_P) - 1):
            if dh[i] > 0 >= dh[i + 1]:
                cross = SCAN_P[i] + (SCAN_P[i + 1] - SCAN_P[i]) * dh[i] / (dh[i] - dh[i + 1])
                break
        res[f"{name}/{model}"] = {"P_GPa": list(SCAN_P), "dH_meV_atom": dh.round(3).tolist(), "static_Pt_GPa": cross,
                                  **{f"V_{s}": hh[s]["V_A3_atom"] for s in hh}}
        print(name, model, "static Pt", cross, "dH", dh.round(2).tolist(), flush=True)
        SCAN.write_text(json.dumps(res, indent=1))


# ---------------------------------------------------------------- submit
def submit(models, pressures: dict, vol_ranges: dict):
    """pressures/vol_ranges: pair -> (P1, P2, P3) / [lo, hi] relative to the 0 GPa relaxed volume."""
    from isoshift import pool

    for name, P3 in pressures.items():
        p = PAIRS[name]
        for model in models:
            for side in ("low", "high"):
                sid = p[side]
                for P in P3:
                    out = RAW_DEEP / model / f"{sid}_P{P}.json"
                    kw = dict(QHA_KW, vol_range=list(vol_ranges[name]), pressure_GPa=float(P))
                    jid = pool.submit(QUEUE, "qha", STRUCTS / f"{sid}.cif", model, out, **kw)
                    print(name, model, sid, P, jid)


# ---------------------------------------------------------------- analysis
def _qha_one(args):
    """Gamma-free QHA for one raw file, both imaginary treatments: G (eV/atom), V(T), in_range per isotope."""
    raw_dir, model, sid, P = args
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    from phonopy import PhonopyQHA

    from ase import Atoms

    from isoshift import phonons as PH
    from src.isoshift_event import validate as V

    V.PRIM = STRUCTS
    V.V_TOL = 1e-3
    r = json.loads((Path(raw_dir) / model / f"{sid}_P{P}.json").read_text())
    vols, e0 = np.array(r["volumes"]), np.array(r["E0"])
    fcs = V._qha_fcs(sid, r)
    uc0 = fcs[int(np.argmin(np.abs(vols - r["V0_relaxed"])))][0].unitcell
    a0 = Atoms(uc0.symbols, cell=uc0.cell, scaled_positions=uc0.scaled_positions, pbc=True)
    mesh = PH.choose_mesh(a0)
    res = {"n_atoms_cell": r["n_atoms_cell"], "vol_min": float(vols.min()), "vol_max": float(vols.max()), "variants": {}}
    for iso, sub in (("H", {}), ("D", {"H": "D"})):
        masses = PH.make_masses(a0, sub, default="light")
        spec = [V._spectrum(ph, masses, mesh) for ph, _m in fcs]
        for treat in ("omit", "abs"):
            th = [V._thermo(f, w, k, treat, TEMPS) for f, w, k, _a in spec]
            fe, se, cv = (np.array(x).T for x in zip(*th))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                q = PhonopyQHA(volumes=vols, electronic_energies=e0, temperatures=TEMPS, free_energy=fe, cv=cv,
                               entropy=se, eos="vinet", pressure=float(P), t_max=float(TEMPS[-1]))
            g, v = np.array(q.gibbs_temperature), np.array(q.volume_temperature)
            d = {"T": TEMPS[:len(g)].tolist(), "G_eV_atom": (g / r["n_atoms_cell"]).tolist(),
                 "V_A3_atom": (v / r["n_atoms_cell"]).tolist(),
                 "in_range": ((v >= vols.min() - 1e-9) & (v <= vols.max() + 1e-9)).tolist()}
            res["variants"][f"{iso}_{treat}"] = d
        if iso == "H":
            res["imag_frac_pct_max"] = max(round(100 * float((((f < PH.IMAG_TOL_THZ) & k) * w[:, None]).sum() / f.shape[1]), 4)
                                           for f, w, k, _a in spec)
            res["min_freq_THz"] = float(min(f[k].min() for f, w, k, _a in spec))
    return (model, sid, P), res


def _fit(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(y)
    if ok.sum() < 2:
        return None, None, None
    k, b = np.polyfit(x[ok], y[ok], 1)
    root = -b / k
    resid = float(np.max(np.abs(np.polyval([k, b], x[ok]) - y[ok]))) if ok.sum() > 2 else 0.0
    return float(root), bool(not (x[ok].min() <= root <= x[ok].max())), resid


def _pair_T(done, p, model, T, treat):
    it = int(np.argmin(np.abs(TEMPS - T)))
    Ps = p["P"]
    row = {}
    g = {}
    for iso in ("H", "D"):
        dg, rng = [], True
        for P in Ps:
            lo = done[(model, p["low"], P)]["variants"][f"{iso}_{treat}"]
            hi = done[(model, p["high"], P)]["variants"][f"{iso}_{treat}"]
            if it >= len(lo["T"]) or it >= len(hi["T"]):
                dg.append(np.nan)
                continue
            dg.append((hi["G_eV_atom"][it] - lo["G_eV_atom"][it]) * 1000)
            rng &= lo["in_range"][it] and hi["in_range"][it]
        g[iso] = np.array(dg)
        root, extrap, resid = _fit(Ps, dg)
        row[f"dG_meV_atom_{iso}"] = [round(x, 4) for x in dg]
        row[f"Pt_{iso}_GPa"] = None if root is None else round(root, 3)
        row[f"Pt_{iso}_extrapolated"] = extrap
        row[f"fit_resid_meV_atom_{iso}"] = None if resid is None else round(resid, 4)
        row[f"in_range_{iso}"] = bool(rng)
    if row["Pt_H_GPa"] is None or row["Pt_D_GPa"] is None:
        return row
    row["dP_iso_GPa"] = round(row["Pt_D_GPa"] - row["Pt_H_GPa"], 3)
    # M02: ddG_iso per atom at each P = dG_D - dG_H; interpolate (linear fit) to P_t^H
    dd = g["D"] - g["H"]
    ok = np.isfinite(dd)
    k, b = np.polyfit(np.array(Ps, float)[ok], dd[ok], 1)
    ddg_atom = float(k * row["Pt_H_GPa"] + b)  # meV/atom
    ddg_H = ddg_atom * p["fu"] / p["nH"] / 1000  # eV per H
    row["ddG_iso_meV_atom_at_PtH"] = round(ddg_atom, 4)
    row["1000lnalpha_low_high"] = round(1000 * ddg_H / (KB * T), 2) if T > 0 else None
    # boundary volume change per atom on the H boundary (for the first-order bridge check)
    vlo = [done[(model, p["low"], P)]["variants"][f"H_{treat}"]["V_A3_atom"][it] for P in Ps]
    vhi = [done[(model, p["high"], P)]["variants"][f"H_{treat}"]["V_A3_atom"][it] for P in Ps]
    dv = np.polyval(np.polyfit(Ps, np.array(vhi) - np.array(vlo), 1), row["Pt_H_GPa"])
    row["dV_A3_atom_at_PtH"] = round(float(dv), 4)
    row["dP_bridge_first_order_GPa"] = round(-ddg_atom / 1000 * EV_A3_GPA / dv, 3)
    row["D_prefers"] = "low" if ddg_atom > 0 else "high"
    return row


def analyze(workers: int = 2):
    from concurrent.futures import ProcessPoolExecutor

    jobs = []
    for p in PAIRS.values():
        if not p["P"]:
            continue
        for model in ("mace", "orb", "mattersim"):
            for sid in (p["low"], p["high"]):
                for P in p["P"]:
                    if (p["raw"] / model / f"{sid}_P{P}.json").exists():
                        jobs.append((str(p["raw"]), model, sid, P))
    done = {}
    with ProcessPoolExecutor(workers) as ex:
        for key, res in ex.map(_qha_one, jobs):
            done[key] = res
    out = {}
    for name, p in PAIRS.items():
        if not p["P"]:
            continue
        for model in ("mace", "orb", "mattersim"):
            if not all((model, s, P) in done for s in (p["low"], p["high"]) for P in p["P"]):
                continue
            e = {"pair": name, "low": p["low"], "high": p["high"], "names": p["names"], "pressures_GPa": list(p["P"]),
                 "n_H_per_fu": p["nH"], "atoms_per_fu": p["fu"], "treatment": "Gamma-free; omit (primary) and |w| bracket",
                 "imag_frac_pct_max": {s: max(done[(model, s, P)]["imag_frac_pct_max"] for P in p["P"]) for s in (p["low"], p["high"])},
                 "min_freq_THz": {s: round(min(done[(model, s, P)]["min_freq_THz"] for P in p["P"]), 3) for s in (p["low"], p["high"])},
                 "T": {}}
            for T in REPORT_T:
                om = _pair_T(done, p, model, T, "omit")
                ab = _pair_T(done, p, model, T, "abs")
                om["bracket_abs"] = {k: ab.get(k) for k in ("Pt_H_GPa", "dP_iso_GPa", "1000lnalpha_low_high")}
                if om.get("dP_iso_GPa") is not None and ab.get("dP_iso_GPa") is not None:
                    om["bracket_dP_iso_GPa"] = round(abs(om["dP_iso_GPa"] - ab["dP_iso_GPa"]), 3)
                    om["bracket_1000lnalpha"] = round(abs(om["1000lnalpha_low_high"] - ab["1000lnalpha_low_high"]), 2)
                e["T"][str(T)] = om
                print(name, model, T, {k: om.get(k) for k in ("Pt_H_GPa", "Pt_D_GPa", "dP_iso_GPa", "1000lnalpha_low_high",
                                                              "dP_bridge_first_order_GPa", "in_range_H", "Pt_H_extrapolated",
                                                              "bracket_dP_iso_GPa")}, flush=True)
            out[f"{name}/{model}"] = e
    OUT.write_text(json.dumps(out, indent=1))


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    s = sub.add_parser("scan")
    s.add_argument("--model", required=True)
    s.add_argument("--device", default="cuda")
    s.add_argument("--pairs", default="")
    s = sub.add_parser("submit")
    s.add_argument("--models", required=True)
    s.add_argument("--plan", required=True, help="JSON {pair: {P: [..], vol_range: [lo, hi]}}")
    sub.add_parser("analyze")
    a = ap.parse_args(argv)
    if a.cmd == "fetch":
        fetch()
    elif a.cmd == "scan":
        scan(a.model, a.device, [x for x in a.pairs.split(",") if x])
    elif a.cmd == "submit":
        plan = json.loads(Path(a.plan).read_text()) if Path(a.plan).exists() else json.loads(a.plan)
        submit(a.models.split(","), {k: v["P"] for k, v in plan.items()}, {k: v["vol_range"] for k, v in plan.items()})
    else:
        analyze()


if __name__ == "__main__":
    main()
