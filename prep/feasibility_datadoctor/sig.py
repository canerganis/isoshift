import pandas as pd, numpy as np, os
D=os.environ.get('DD','C:/Users/can02/Projects/osi-hackathon-2026/data/datadoctor')
g=pd.read_pickle(f'{D}/expt_gap.pkl')
from pymatgen.core import Composition
g['red']=g.formula.map(lambda f: Composition(f).reduced_formula)
print('unique raw formula',g.formula.nunique(),'unique reduced',g.red.nunique())
for key in ['formula','red']:
    s=g.groupby(key)['gap expt'].agg(['count','min','max'])
    m=s[s['count']>1]; m=m.assign(spread=m['max']-m['min'])
    print(key,'multi groups',len(m),'rows in them',int(m['count'].sum()),[ (t,int((m.spread>t).sum())) for t in (0.1,0.5,1)])
    if key=='red': worst=m.sort_values('spread',ascending=False).head(10); print(worst)
# matbench
mb=pd.read_pickle(f'{D}/matbench_expt_gap.pkl'); print('matbench unique comps',mb.composition.nunique(), len(mb))
mb['red']=mb.composition.map(lambda f: Composition(f).reduced_formula); print('matbench unique reduced',mb.red.nunique())
# kingsbury gap
k=pd.read_pickle(f'{D}/expt_gap_kingsbury.pkl'); print(k.likely_mpid.notna().sum(),'with mpid of',len(k), 'nunique mpid',k.likely_mpid.nunique())
# enthalpy
e=pd.read_pickle(f'{D}/expt_formation_enthalpy.pkl')
for c in ['e_form mp','e_form oqmd']:
    d=(e[c]-e['e_form expt']).abs(); print(c,'n>0.2',int((d>0.2).sum()),'>0.1',int((d>0.1).sum()),'of',d.notna().sum())
e['d']=(e['e_form mp']-e['e_form expt']).abs(); print(e.sort_values('d',ascending=False).head(10)[['formula','mpid','e_form expt','e_form mp','e_form oqmd']].to_string())
kb=pd.read_pickle(f'{D}/expt_formation_enthalpy_kingsbury.pkl')
print(kb.reference.nunique(),'unique refs of',len(kb)); print(kb.reference.value_counts().head(8).to_string()); print(kb.reference.isna().sum(),'null; DOI-containing',kb.reference.astype(str).str.contains('doi|10\.\d{4}',case=False).sum())
print(kb.formula.duplicated().sum(),'dup formulas')
print(kb.uncertainty.describe())
