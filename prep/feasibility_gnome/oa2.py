import csv,re,json,time,urllib.request,urllib.parse,sys,collections
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8')))
byf=collections.defaultdict(list)
for r in rows: byf[r['Reduced Formula']].append(r)
def get(url):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'osi-feas'}),timeout=30))
        except Exception as e: err=e; time.sleep(2)
    return {'meta':{'count':-1},'results':[],'err':str(err)}
def n(f,flt):
    return get(f"https://api.openalex.org/works?filter={flt}:{urllib.parse.quote(chr(34)+f+chr(34))},publication_year:2024-2026&per-page=3&select=title,doi")
print('MnFeCo4Si2' in byf, [ (r['MaterialId'],r['Is Train'],r['Decomposition Energy Per Atom MP']) for r in byf.get('MnFeCo4Si2',[])])
# controls, and GNoME formulas that exist in dataset among well-known-looking ones
cands=['MnFeCo4Si2','Rb2PaBr6','Cs2AgBiBr6','CsSnI3','LiMnPO4','K2NiF4','NaSbF6','Li3YCl6','Li3ScCl6','Li2ZrCl6','Na3SbS4','K3SbS4','Cs3Bi2I9','Ba2LuNbO6','CsCuCl3','Rb2SnI6','Cs2TiBr6','LiZnSb','Mg3Sb2','Ca3PN','KMgSb','NaMnO2','BaZrS3','Li3TiCl6','Li3InCl6','Rb2TiBr6','Cs2ZrCl6','K2PtCl6','Na2LiAlH6','Ba3Si4']
hits=[c for c in cands if c in byf]
print('in gnome:',hits)
for f in hits:
    a=n(f,'title_and_abstract.search'); b=n(f,'fulltext.search')
    print(f,len(byf[f]),'TA',a['meta']['count'],'FT',b['meta']['count'],[x['title'][:70] for x in a['results']][:2],flush=True)
for f in ['LiFePO4','CsPbI3','BaTiO3','Li7La3Zr2O12']:
    a=n(f,'title_and_abstract.search'); print('control',f,a['meta']['count'])
