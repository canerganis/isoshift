"""Tabulate harmonic feasibility results -> prints markdown tables."""
import json, re, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from isoshift.compare import ensemble
R = ROOT / "prep" / "feasibility_isoshift" / "results"
calcs = ["mace", "orb", "sevenn", "mattersim"]
res = {c: json.load(open(R / f"harmonic_{c}.json")) for c in calcs}

def nH(f):
    m = re.search(r"H(\d*)", f); return int(m.group(1) or 1)

print("| structure | N | " + " | ".join(f"{c} ZPE D/H, minfreq THz, t_tot s" for c in calcs) + " |")
for s in res["mace"]:
    row = [s, str(res["mace"][s].get("n_atoms"))]
    for c in calcs:
        r = res[c][s]
        if "error" in r: row.append("FAIL"); continue
        v = r["variants"]
        row.append(f"{v['D']['zpe_eV_cell']/v['H']['zpe_eV_cell']:.4f}, {v['H']['imag']['min_freq_THz']:.2f}, {r['timing']['relax_s']+r['timing']['fc_s']:.0f}")
    print("| " + " | ".join(row) + " |")

def dF(r):  # F_D - F_H at 300 K per cell, eV
    return r["variants"]["D"]["F_eV_cell"][0] - r["variants"]["H"]["F_eV_cell"][0]
def per(r):
    n = r["n_atoms"]; h = nH(r["formula"].replace(" ", "")) if False else sum(1 for _ in range(0))
    return n
for a, b in [("MgH2_rutile", "MgH2_gamma"), ("AlOOH_diaspore", "AlOOH_boehmite")]:
    print(f"\n{a} - {b}, 300 K harmonic, ddF_iso = dF(a) - dF(b)")
    vals_atom, vals_H = {}, {}
    for c in calcs:
        ra, rb = res[c][a], res[c][b]
        if "error" in ra or "error" in rb: continue
        na, nb = ra["n_atoms"], rb["n_atoms"]
        ha, hb = nH(ra["formula"]), nH(rb["formula"])
        vals_atom[c] = 1000 * (dF(ra) / na - dF(rb) / nb)
        vals_H[c] = 1000 * (dF(ra) / ha - dF(rb) / hb)
        imag = (ra["variants"]["H"]["imag"]["min_freq_THz"], rb["variants"]["H"]["imag"]["min_freq_THz"])
        print(f"  {c:9s} ddF = {vals_atom[c]:+.3f} meV/atom, {vals_H[c]:+.2f} meV/H, "
              f"dF_D-H {1000*dF(ra)/na:.2f} / {1000*dF(rb)/nb:.2f} meV/atom, minfreq {imag[0]:.2f}/{imag[1]:.2f} THz")
    print("  ensemble meV/atom:", ensemble(vals_atom))
    print("  ensemble meV/H   :", ensemble(vals_H))
