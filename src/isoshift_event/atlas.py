"""Isotope atlas (post-freeze addendum, F10): predicted sign of ddF_iso for every same-composition polymorph pair of
O-H-bearing compounds in data/isoshift/mp_h.json, from database geometry only (no phonons, no ML relaxation).

Population. Every MP entry in mp_h.json (no C, E_hull <= 50 meV/atom) with at least one O-H donor (an H whose nearest
O is within 1.15 A). No atom-count cap. Same reduced composition = one group. Inside a group the structures are reduced
to primitive cells and deduplicated exactly as src/isoshift_event/pairs.py does (StructureMatcher ltol 0.2, stol 0.15,
angle_tol 5, ElementComparator, plus the space-group gate at symprec 0.05), keeping the lowest-energy entry as the
representative. Every pair of representatives with |dE| <= 50 meV/atom (MP energies only) is an atlas pair.

Geometry per structure (MP DFT structure as stored). For each donor H: O-H = distance to its nearest O; acceptor =
nearest O other than the donor O with H...O < 2.6 A; O...O = donor-acceptor distance (same definition as
stretch_check._donors, but with full periodic neighbour search). mean_OO is over donors with an acceptor (as in
rule_oo.structure_table); mean_OH is over all donors; mean_OH_hb over the donors with an acceptor.

Prediction (F01 convention). ddF_iso(b - a) = [F_D - F_H]_b - [F_D - F_H]_a per H. F01: sign(ddF_iso) = sign(dO-H) =
-sign(dO...O); positive means deuteration favours a. The primary sign is from dO-H (b - a) of the database structures;
dO...O is the consistency check. Confidence:
  high      |dO-H| >= 5 mA and |dO...O| >= 0.03 A, and the two agree (longer O...O with shorter O-H)
  medium    one of the two above its cut, the other agrees in sign or is undefined
  low       both below their cuts, signs agree or one undefined
  conflict  dO-H and dO...O both nonzero with opposite implied signs (sign still from dO-H)
Regime: strong if either polymorph has mean_OO <= the translated threshold in results/F01_oo.json
(threshold_translation_summary.median_OO_A, 2.929 A); weak if both have mean_OO above it; undefined if neither has an
H-bonded donor.

    python -m src.isoshift_event.atlas
writes results/atlas.csv and results/atlas_summary.json
"""
from __future__ import annotations

import json
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.core import Composition, Structure

from .pairs import _matches, _primitive, make_matcher

ROOT = Path(__file__).resolve().parents[2]
OH_MAX = 1.15  # A, donor O-H cut (stretch_check._donors)
HO_MAX = 2.6  # A, H...O acceptor cut (stretch_check._donors)
MIN_DOH = 0.005  # A, headline eligibility |d mean O-H| >= 5 mA
MIN_DOO = 0.03  # A, rule_oo.MIN_DOO
DE_MAX = 50.0  # meV/atom
OO_THRESHOLD = json.loads((ROOT / "results" / "F01_oo.json").read_text())["threshold_translation_summary"]["median_OO_A"]


def donor_geometry(s: Structure) -> list[tuple[float, float]]:
    """(d_OH, d_OO or nan) per O-H donor H."""
    out = []
    for i, site in enumerate(s):
        if site.specie.symbol != "H":
            continue
        nb = sorted((n for n in s.get_neighbors(site, HO_MAX + 0.01) if n.specie.symbol == "O"), key=lambda n: n.nn_distance)
        if not nb or nb[0].nn_distance > OH_MAX:
            continue
        don = nb[0]
        if len(nb) > 1 and nb[1].nn_distance <= HO_MAX:
            d_oo = float(np.linalg.norm(nb[1].coords - don.coords))
        else:
            d_oo = np.nan
        out.append((float(don.nn_distance), d_oo))
    return out


def structure_row(e: dict, prim: Structure) -> dict:
    g = donor_geometry(prim)
    oh = np.array([x[0] for x in g])
    oo = np.array([x[1] for x in g])
    hb = np.isfinite(oo)
    nH = sum(1 for x in prim if x.specie.symbol == "H")
    return {"mp_id": e["mp_id"], "spg": e["spg"], "spg_symbol": e["spg_symbol"], "nsites_prim": len(prim),
            "e_per_atom_eV": e["e_per_atom_eV"], "e_hull_meV": 1000 * e["e_hull_eV"], "experimental": not e["theoretical"],
            "n_H": nH, "n_donors": int(len(g)), "n_hb_donors": int(hb.sum()),
            "mean_OH": float(oh.mean()) if len(oh) else np.nan,
            "mean_OH_hb": float(oh[hb].mean()) if hb.any() else np.nan,
            "mean_OO": float(oo[hb].mean()) if hb.any() else np.nan}


def classify(doh: float, doo: float) -> tuple[int, str]:
    s_oh = int(np.sign(doh)) if abs(doh) > 0 else 0
    s_oo = -int(np.sign(doo)) if np.isfinite(doo) and abs(doo) > 0 else 0  # sign implied by O...O
    big_oh, big_oo = abs(doh) >= MIN_DOH, np.isfinite(doo) and abs(doo) >= MIN_DOO
    if s_oh and s_oo and s_oh != s_oo:
        return s_oh, "conflict"
    sign = s_oh or s_oo
    if big_oh and big_oo:
        return sign, "high"
    if big_oh or big_oo:
        return sign, "medium"
    return sign, "low"


def main():
    t0 = time.time()
    entries = json.loads((ROOT / "data" / "isoshift" / "mp_h.json").read_text())
    groups = defaultdict(list)
    for e in entries:
        c = Composition(e["formula"])
        if "O" in c.as_dict():
            groups[c.reduced_formula].append(e)
    matcher = make_matcher()
    rows, n_oh_struct, n_dup, t_geo = [], 0, 0, 0.0
    for formula, es in sorted(groups.items()):
        reps = []
        for e in sorted(es, key=lambda e: (e["e_per_atom_eV"], int(e["mp_id"].split("-")[1]))):
            prim = _primitive(Structure.from_dict(e["structure"]))
            tg = time.time()
            r = structure_row(e, prim)
            t_geo += time.time() - tg
            if r["n_donors"] == 0:
                continue
            n_oh_struct += 1
            dup = next((q for q in reps if len(q[1]) == len(prim) and _matches(matcher, prim, q[1])), None)
            if dup is not None:
                n_dup += 1
                dup[2].append(e["mp_id"])
                # a phase counts as observed if any MP entry merged into it is theoretical=False
                dup[0]["experimental"] = dup[0]["experimental"] or not e["theoretical"]
                continue
            reps.append((r, prim, []))
        for (a, _, da), (b, _, db) in combinations(reps, 2):
            dE = 1000 * (b["e_per_atom_eV"] - a["e_per_atom_eV"])
            if abs(dE) > DE_MAX:
                continue
            doh, doo = b["mean_OH"] - a["mean_OH"], b["mean_OO"] - a["mean_OO"]
            sign, conf = classify(doh, doo)
            ooa, oob = a["mean_OO"], b["mean_OO"]
            if not (np.isfinite(ooa) or np.isfinite(oob)):
                regime = "undefined"
            else:
                regime = "strong" if np.nanmin([ooa, oob]) <= OO_THRESHOLD else "weak"
            fav = a["mp_id"] if sign > 0 else b["mp_id"] if sign < 0 else ""
            rows.append({"formula": formula, "mp_a": a["mp_id"], "mp_b": b["mp_id"],
                         "spg_a": a["spg_symbol"], "spg_b": b["spg_symbol"], "spgnum_a": a["spg"], "spgnum_b": b["spg"],
                         "nsites_a": a["nsites_prim"], "nsites_b": b["nsites_prim"], "dE_meV_atom": round(dE, 2),
                         "exp_a": a["experimental"], "exp_b": b["experimental"], "both_experimental": a["experimental"] and b["experimental"],
                         "OH_a": round(a["mean_OH"], 4), "OH_b": round(b["mean_OH"], 4), "OO_a": round(ooa, 4), "OO_b": round(oob, 4),
                         "ndon_a": a["n_donors"], "ndon_b": b["n_donors"], "nhb_a": a["n_hb_donors"], "nhb_b": b["n_hb_donors"],
                         "dOH_mA": round(1000 * doh, 2), "dOO_A": round(doo, 4) if np.isfinite(doo) else np.nan,
                         "regime": regime, "pred_sign_ddF": sign, "D_favours": fav, "confidence": conf,
                         "dups_a": ";".join(da), "dups_b": ";".join(db)})
    p = pd.DataFrame(rows)
    elapsed = time.time() - t0
    p.to_csv(ROOT / "results" / "atlas.csv", index=False)
    exp, strong = p.both_experimental, p.regime == "strong"
    summ = {"OO_threshold_A": OO_THRESHOLD, "o_bearing_formulas": len(groups), "oh_structures": n_oh_struct, "duplicates_merged": n_dup,
            "pairs": int(len(p)), "formulas_with_pairs": int(p.formula.nunique()),
            "regime": {k: int(v) for k, v in p.regime.value_counts().items()},
            "confidence": {k: int(v) for k, v in p.confidence.value_counts().items()},
            "both_experimental": int(exp.sum()), "strong_and_both_experimental": int((exp & strong).sum()),
            "strong_and_both_experimental_formulas": int(p[exp & strong].formula.nunique()),
            "strong_both_exp_confidence": {k: int(v) for k, v in p[exp & strong].confidence.value_counts().items()},
            "time_total_s": round(elapsed, 1), "time_geometry_s": round(t_geo, 1),
            "time_per_pair_s": round(elapsed / max(len(p), 1), 4)}
    (ROOT / "results" / "atlas_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
