"""W1/W3 recount for the Terra review (C-terra-v2, 9 Nov 2026). Reads frozen decomposition tables only.
    PYTHONPATH=. .venv/Scripts/python.exe -B scripts/w1w3_recount.py
Expected: W1 212/212 at 0, 300, 600 K; 232/232 O-H |dr|>=5; 480-row bins >=1 mA 413/415, <5 229/248, <1 48/65; W3 190 rows, 176, medians 0.645/0.580/0.402, H1 81, 188/190."""
import numpy as np, pandas as pd, json
from src.isoshift_event import rule_cv as R
from src.isoshift_event.f09_temperature import headline, PF
h = headline()
for T in (0,300,600):
    d = pd.read_csv(PF/f"T{T}"/"decompose_pairs.csv").set_index(["pair_id","model"])
    k = list(zip(h.pair_id,h.model))
    h[f"str{T}"]=d.loc[k,"ddF_str"].values/h.H_per_atom.values
    h[f"perp{T}"]=d.loc[k,"ddF_perp"].values/h.H_per_atom.values
    h[f"tot{T}"]=d.loc[k,"ddF_total"].values/h.H_per_atom.values
    h[f"C{T}"]=-h[f"perp{T}"]/h[f"str{T}"]
    h[f"clean{T}"]=d.loc[k,"clean"].values.astype(bool)
sx=np.sign(h.x)
out={}
# W1: stretch term sign vs O-H difference sign
for T in (0,300,600):
    ok=np.sign(h[f"str{T}"])==sx
    out[f"W1_str_sign_{T}K"]={"n":len(h),"agree":int(ok.sum()),"per_model":{m:[int(ok[q.index].sum()),len(q)] for m,q in h.groupby("model")},
       "pairs_majority_agree":int((ok.groupby(h.pair_id).mean()>0.5).sum()),"n_pairs":int(h.pair_id.nunique()),
       "disagree_rows":[(p,m,round(x,1),round(s,3)) for p,m,x,s,o in zip(h.pair_id,h.model,h.x,h[f"str{T}"],ok) if not o]}
# all clean covalent O-H rows at 300 K (frozen decompose)
c=R.load()
f=pd.read_csv("results/decompose_pairs.csv").set_index(["pair_id","model"])
cc=c[c.OH & (c.x.abs()>=5)].copy()
k=list(zip(cc.pair_id,cc.model))
cc["str"]=f.loc[k,"ddF_str"].values
ok=np.sign(cc["str"])==np.sign(cc.x)
out["W1_allOH_300K"]={"n":len(cc),"agree":int(ok.sum()),
   "weak_side":[int(ok[cc.rmax<0.99].sum()),int((cc.rmax<0.99).sum())],"strong_side":[int(ok[cc.rmax>=0.99].sum()),int((cc.rmax>=0.99).sum())]}
# W3: 600 K on rows clean at 0 and 600 K
both=h.clean0&h.clean600
e1=(h.str0.abs()>=0.1)&(h.str600.abs()>=0.1)
g=h[both&e1]
out["W3"]={"rows_clean_0_and_600":int(both.sum()),"eligible":len(g),
  "C600_lt_C0":int((g.C600<g.C0).sum()),"medC0":round(float(g.C0.median()),3),"medC300":round(float(g.C300.median()),3),"medC600":round(float(g.C600.median()),3),
  "H1_ok":int((g.C600<0.6*g.C0).sum()),
  "all_rows_C600_lt_C0":[int((h[e1].C600<h[e1].C0).sum()),int(e1.sum())]}
s=h[h.pair_id.str.contains("mp-985293")]
sc=s[s.clean0&s.clean600]
out["W3_mp985293_clean"]={"n":len(sc),"C0_gt1":int((sc.C0>1).sum()),"C600_lt1":int((sc.C600<1).sum()),
  "str_sign_ok_0_600":int(((np.sign(sc.str0)==np.sign(sc.x))&(np.sign(sc.str600)==np.sign(sc.x))).sum()),
  "tot600_right":int((np.sign(sc.tot600)==np.sign(sc.x)).sum())}
# 600 K accuracy on clean600 rows
cl=h[h.clean600]
out["acc600_clean"]=[int((np.sign(cl.tot600)==np.sign(cl.x)).sum()),len(cl)]
oh=c[c.OH].copy(); kk=list(zip(oh.pair_id,oh.model)); oh=oh[[q in f.index for q in kk]]
kk=list(zip(oh.pair_id,oh.model)); oh["str"]=f.loc[kk,"ddF_str"].values
ag=np.sign(oh["str"])==np.sign(oh.x); ax=oh.x.abs()
out["W1_all_decomposed_OH_300K"]={"n":len(oh),"ge1":[int(ag[ax>=1].sum()),int((ax>=1).sum())],"lt5":[int(ag[ax<5].sum()),int((ax<5).sum())],"lt1":[int(ag[ax<1].sum()),int((ax<1).sum())]}
print(json.dumps({k:v for k,v in out.items() if "disagree" not in k},indent=0,default=str))
