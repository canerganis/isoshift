"""Count JARVIS dft_3d candidate pool of H-containing polymorph pairs. Saves data/isoshift/jarvis_h_pairs.csv."""
import itertools, json, sys
from pathlib import Path
import pandas as pd
from jarvis.db.figshare import data
from jarvis.core.atoms import Atoms

ROOT = Path(__file__).resolve().parents[2]
d = data("dft_3d", store_dir=str(ROOT / "data" / "isoshift"))
df = pd.DataFrame(d)
print("total entries", len(df), "columns", [c for c in df.columns][:60])
df.to_pickle(ROOT / "data" / "isoshift" / "dft_3d.pkl")

def elems(a):
    return sorted(set(a["elements"]))
df["elems"] = df["atoms"].apply(elems)
df["natoms"] = df["atoms"].apply(lambda a: len(a["elements"]))
df["hasH"] = df["elems"].apply(lambda e: "H" in e)
hdf = df[df.hasH]
print("H-containing", len(hdf))
org = hdf["elems"].apply(lambda e: "C" in e)
print("with C (excluded)", int(org.sum()))
h = hdf[~org].copy()
print("H, no C", len(h))
h = h[h["formation_energy_peratom"].apply(lambda x: isinstance(x, (int, float)))].copy()
h["formation_energy_peratom"] = h["formation_energy_peratom"].astype(float)
h["ehull"] = pd.to_numeric(h["ehull"], errors="coerce")
h["reduced"] = h["atoms"].apply(lambda a: Atoms.from_dict(a).composition.reduced_formula)
g = h.groupby("reduced")
multi = {k: v for k, v in g if len(v) >= 2}
print("compositions", g.ngroups, ">=2 polymorphs", len(multi))
rows = []
for k, v in multi.items():
    v = v.sort_values("formation_energy_peratom")
    for (_, a), (_, b) in itertools.combinations(v.iterrows(), 2):
        dE = abs(a.formation_energy_peratom - b.formation_energy_peratom) * 1000
        rows.append(dict(formula=k, jid_a=a.jid, jid_b=b.jid, spg_a=a.spg_number, spg_b=b.spg_number,
                         natoms_a=a.natoms, natoms_b=b.natoms, dEf_meV=dE,
                         ehull_a=a.ehull, ehull_b=b.ehull, ehull_max=max(a.ehull, b.ehull)))
pairs = pd.DataFrame(rows)
pairs = pairs[pairs.spg_a != pairs.spg_b]  # distinct structures only
print("pairs (distinct spacegroups)", len(pairs))
for t in (10, 25):
    s = pairs[pairs.dEf_meV <= t]
    print(f"dEf <= {t} meV/atom: pairs {len(s)}, compositions {s.formula.nunique()}, with natoms<=16 both: {int(((s.natoms_a<=16)&(s.natoms_b<=16)).sum())}, <=32: {int(((s.natoms_a<=32)&(s.natoms_b<=32)).sum())}")
    s2 = s[s.ehull_max <= 0.1]
    print(f"   and ehull both <= 100 meV: pairs {len(s2)}, comps {s2.formula.nunique()}")
pairs = pairs.sort_values("dEf_meV")
pairs.to_csv(ROOT / "data" / "isoshift" / "jarvis_h_pairs.csv", index=False)
print("saved", len(pairs))
