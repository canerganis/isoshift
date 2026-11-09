"""Post hoc MLIP vs PBEsol isotope double differences on same-formula pairs of the MDR benchmark (C-terra-v2, 9 Nov 2026).
Reads results/benchmark/isotope_benchmark.csv (dF300 columns are per H). Four models incl. SevenNet; no n_H division.
    PYTHONPATH=. .venv/Scripts/python.exe -B scripts/benchmark_double_difference.py
Expected: a_dftstruct MAE 0.486, sign 36/46, |dft|>=0.1: 22/24; b_relaxed MAE 0.677, sign 31/46, 22/24."""
import pandas as pd, itertools, numpy as np
from pymatgen.core import Composition
d=pd.read_csv('results/benchmark/isotope_benchmark.csv')
d['red']=d.formula.map(lambda f: Composition(f).reduced_formula)
rows=[]
for red,g in d.groupby('red'):
    ents=sorted(g.entry.unique())
    for a,b in itertools.combinations(ents,2):
        for (m,s),h in g.groupby(['model','setting']):
            ra=h[h.entry==a]; rb=h[h.entry==b]
            if ra.empty or rb.empty: continue
            ra=ra.iloc[0]; rb=rb.iloc[0]
            rows.append(dict(red=red,pair=a+'/'+b,model=m,setting=s,dft=ra.dF300_dft_meV-rb.dF300_dft_meV,ml=ra.dF300_mlip_meV-rb.dF300_mlip_meV,
              perr=(abs(ra.dF300_err_meV)+abs(rb.dF300_err_meV))/2,imd=bool(ra.imag_dft or rb.imag_dft),imm=bool(ra.imag_mlip or rb.imag_mlip)))
r=pd.DataFrame(rows); r['err']=r.ml-r.dft
pd.set_option('display.width',250)
print(r.groupby('pair').agg(red=('red','first'),dft=('dft','first'),imd=('imd','first')).to_string())
for s in ['a_dftstruct','b_relaxed']:
    x=r[r.setting==s]
    sg=(np.sign(x.ml)==np.sign(x.dft))
    print(s,'n',len(x),'sign',sg.sum(),'MAE dd',x.err.abs().mean().round(3),'max',x.err.abs().max().round(3),'mean per-struct err',x.perr.mean().round(3))
    print(x[~sg][['pair','red','model','dft','ml','imd','imm']].to_string())
    big=x[x.dft.abs()>=0.1]; print(' |dft|>=0.1:',len(big),'sign',(np.sign(big.ml)==np.sign(big.dft)).sum())
    print(x.groupby('model').err.apply(lambda e:e.abs().mean()).round(3).to_dict())
