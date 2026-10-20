import csv,re,json,time,urllib.request,urllib.parse,sys,collections
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8')))
def canon(f):
    f=re.sub(r'\(([^)]*)\)(\d*)',lambda m:''.join(e+str(int(c or 1)*int(m.group(2) or 1)) for e,c in re.findall(r'([A-Z][a-z]?)(\d*)',m.group(1))),f)
    d=collections.Counter()
    for e,c in re.findall(r'([A-Z][a-z]?)(\d*)',f): d[e]+=int(c or 1)
    return tuple(sorted(d.items()))
idx=collections.defaultdict(list)
for r in rows: idx[canon(r['Reduced Formula'])].append(r)
def get(url):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'osi-feas'}),timeout=30))
        except Exception as e: err=e; time.sleep(2)
    return {'meta':{'count':-1},'results':[]}
cands=['MnFeCo4Si2','Cs2AgBiBr6','Li3YCl6','Li3ScCl6','Li2ZrCl6','Na3SbS4','Cs3Bi2I9','Ba2LuNbO6','Rb2SnI6','Cs2TiBr6','LiZnSb','KMgSb','BaZrS3','Li3InCl6','Cs2ZrCl6','K2PtCl6','NaMnO2','Li3TiCl6','CsCuCl3','Ca3PN','Mg3Sb2','LiMnPO4','KCuSe','NaCuS','Cs2PdBr6','Rb2PdBr6','K2PdBr6','Ba2NaOsO6']
found=[]
for c in cands:
    k=canon(c)
    if k in idx:
        for r in idx[k]: found.append((c,r))
print(len(found))
for c,r in found:
    f=r['Reduced Formula']
    def q(form):
        return get(f"https://api.openalex.org/works?filter=title_and_abstract.search:{urllib.parse.quote(chr(34)+form+chr(34))},publication_year:2024-2026&per-page=3&select=title,doi")
    a=q(f); b=q(c) if c!=f else a
    print(c,'|',f,r['Space Group'],r['Is Train'],r['Decomposition Energy Per Atom MP'],'| GNoMEfmt',a['meta']['count'],'| commonfmt',b['meta']['count'],[x['title'][:70] for x in b['results']][:2],flush=True)
