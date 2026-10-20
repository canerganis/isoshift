import requests,re,json
comps=['AlP','TaGaS2','As2S3','SrTiO3','ZnSnP2']
for c in comps:
    r=requests.get('https://api.openalex.org/works',params={'search':f'{c} band gap','per-page':10,'select':'id,title,doi,publication_year,abstract_inverted_index'},timeout=60).json()
    print('##',c,'total',r['meta']['count'])
    hit=0
    for w in r['results']:
        ab=w.get('abstract_inverted_index')
        txt=' '.join(sorted([(p,k) for k,v in ab.items() for p in v]) and [k for p,k in sorted((p,k) for k,v in ab.items() for p in v)]) if ab else ''
        has_c=c.lower() in (w['title']+txt).lower().replace(' ','')
        vals=re.findall(r'(\d\.\d+)\s*eV',txt)
        hit+=has_c and bool(vals)
        print(' ',w['publication_year'],w['title'][:80],'| formula in text:',has_c,'| eV vals:',vals[:3])
    print('  usable (formula+eV in abstract):',hit,'/10')
