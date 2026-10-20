import csv,re,sys,collections
p=sys.argv[1]
rows=list(csv.DictReader(open(p,encoding='utf-8')))
print(len(rows)); print(list(rows[0].keys()))
c=collections.Counter(len(re.findall(r'[A-Z][a-z]?',r['Reduced Formula'])) for r in rows)
print(sorted(c.items()))
import statistics
neg=sum(1 for r in rows if float(r['Decomposition Energy Per Atom MP'] or 9)<0)
print('decompMP<0',neg, 'decompAll<=0',sum(1 for r in rows if float(r['Decomposition Energy Per Atom All'] or 9)<=0))
print(collections.Counter(r['Is Train'] for r in rows))
for r in rows[:2000:400]: print({k:r[k] for k in ['MaterialId','Reduced Formula','Space Group','NSites','Decomposition Energy Per Atom MP','Decomposition Energy Per Atom All','Is Train','Bandgap']})
