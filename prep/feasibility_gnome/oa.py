import csv,random,re,json,time,urllib.request,urllib.parse,sys
random.seed(1)
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8')))
def nel(r): return len(re.findall(r'[A-Z][a-z]?',r['Reduced Formula']))
def get(url):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'osi-feas'}),timeout=30))
        except Exception as e: err=e; time.sleep(2)
    return {'meta':{'count':-1},'results':[],'err':str(err)}
tern=[r for r in rows if nel(r)==3 and r['Is Train']=='False']
quat=[r for r in rows if nel(r)==4]
known=[ 'Cs(ZrS2)3']
sel=random.sample(tern,6)+random.sample(quat,6)
out=[]
t0=time.time()
for r in sel:
    f=r['Reduced Formula']
    q=urllib.parse.quote('"%s"'%f)
    u=f"https://api.openalex.org/works?filter=title_and_abstract.search:{q},publication_year:2024-2026&per-page=5&select=id,title,publication_year,doi"
    j=get(u)
    out.append((f,r['Space Group'],j['meta']['count'],[x['title'] for x in j['results']][:3]))
    print(out[-1],flush=True)
# fulltext
for r in sel[:4]:
    f=r['Reduced Formula']
    u=f"https://api.openalex.org/works?filter=fulltext.search:{urllib.parse.quote(chr(34)+f+chr(34))},publication_year:2024-2026&per-page=3&select=title"
    j=get(u); print('FT',f,j['meta']['count'],[x['title'] for x in j['results']],flush=True)
print('sec',time.time()-t0)
