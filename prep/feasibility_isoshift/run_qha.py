"""QHA feasibility: 7 volumes, H and D from the same force constants. usage: run_qha.py STRUCT CALC [CALC...]"""
import json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from isoshift.worker import run_job

S = ROOT / "data" / "isoshift" / "structs"
STR = {"LiH": "JVASP-2002", "brucite": "JVASP-4119"}
OUT = ROOT / "prep" / "feasibility_isoshift" / "results"
name = sys.argv[1]
for calc in sys.argv[2:]:
    t = time.time()
    try:
        r = run_job("qha", str(S / f"{STR[name]}.cif"), calc, temps=list(np.arange(0, 601, 10.0)), n_vol=7, vol_range=[-0.03, 0.07])
    except Exception as e:
        print(calc, name, "FAILED", repr(e)[-500:], flush=True); continue
    r["wall_s"] = time.time() - t
    (OUT / f"qha_{name}_{calc}.json").write_text(json.dumps(r, indent=1))
    v = r["variants"]
    T = np.array(v["H"]["T"])
    i300 = int(np.argmin(abs(T - 300))); i0 = 0
    VH, VD = np.array(v["H"]["V_A3"]), np.array(v["D"]["V_A3"])
    print(f"{calc:9s} {name} wall={r['wall_s']:.0f}s timing={ {k: round(x,1) for k,x in r['timing'].items()} } "
          f"V_H(0K)={VH[0]:.3f} V_D(0K)={VD[0]:.3f} dV/V(0K)={(VH[0]/VD[0]-1)*100:.3f}% "
          f"in_range H/D={v['H']['n_in_range']}/{v['D']['n_in_range']} of {len(T)} V_H(300)={VH[i300]:.3f} dV/V(300)={(VH[i300]/VD[i300]-1)*100:.3f}%", flush=True)
