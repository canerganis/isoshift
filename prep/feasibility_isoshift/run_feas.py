"""Small feasibility tests: harmonic H vs D for LiH, brucite, MgH2 and AlOOH polymorph pairs.

usage: python prep/feasibility_isoshift/run_feas.py CALC [CALC ...]
Results are appended to prep/feasibility_isoshift/results/harmonic_<calc>.json
"""
import json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from isoshift.worker import run_job

S = ROOT / "data" / "isoshift" / "structs"
STRUCTS = {"LiH": "JVASP-2002", "brucite": "JVASP-4119", "MgH2_rutile": "JVASP-3687", "MgH2_gamma": "JVASP-12557",
           "AlOOH_diaspore": "JVASP-54676", "AlOOH_boehmite": "JVASP-29869"}
OUT = ROOT / "prep" / "feasibility_isoshift" / "results"
OUT.mkdir(exist_ok=True)

for calc in sys.argv[1:]:
    res = {}
    for name, jid in STRUCTS.items():
        t = time.time()
        try:
            r = run_job("harmonic", str(S / f"{jid}.cif"), calc, temps=[300.0], subs={"H": {}, "D": {"H": "D"}})
            r["wall_s"] = time.time() - t
            res[name] = r
            v = r["variants"]
            print(f"{calc:8s} {name:15s} N={r['n_atoms']:3d} sc={r['fc_meta']['supercell']} disp={r['fc_meta']['n_displacements']} "
                  f"relax={r['timing']['relax_s']:.1f}s fc={r['timing']['fc_s']:.1f}s zpeD/H={v['D']['zpe_eV_cell']/v['H']['zpe_eV_cell']:.4f} "
                  f"imag={v['H']['imag']['min_freq_THz']:.2f}THz mem={r.get('gpu_peak_mem_MB', 0):.0f}MB", flush=True)
        except Exception as e:
            res[name] = {"error": repr(e)[:2000]}
            print(calc, name, "FAILED", repr(e)[:300], flush=True)
    (OUT / f"harmonic_{calc}.json").write_text(json.dumps(res, indent=1))
