import re,json,collections
S='/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad'
ms=open(S+'/ms.md').read().split('\n')
led=json.load(open(S+'/ledger.json'))
blob=json.dumps(led['claims'])
# normalise ledger numeric tokens
lednums=set(re.findall(r'-?\d+\.?\d*', blob))
def norm(t):
    t=t.replace('−','-').replace(' ','').replace(',','').replace('%','').strip()
    return t
cur='front'
rows=[]
numre=re.compile(r'(?<![\w/.\-])[−+-]?\d[\d,]*(?:\.\d+)?')
for i,l in enumerate(ms,1):
    m=re.match(r'^#{1,3} (.*)',l)
    if m: cur=m.group(1)[:44]
    if cur.startswith('9 ·') or cur.startswith('10 ·'): continue
    for t in numre.findall(l):
        n=norm(t)
        try: f=float(n)
        except: continue
        hit = n in lednums or n.lstrip('+-') in lednums or (('%.4g'%f) in lednums)
        rows.append((cur,i,n,hit,l.strip()[:110]))
by=collections.defaultdict(lambda:[0,0])
for cur,i,n,hit,l in rows:
    by[cur][0]+=1
    if hit: by[cur][1]+=1
print('SECTION-LEVEL numeric-token coverage (References/Declarations excluded)')
print(f'{"tokens":>7} {"in-ledger":>9}  section')
for k,(tot,h) in by.items(): print(f'{tot:7d} {h:9d}  {k}')
tt=sum(v[0] for v in by.values()); hh=sum(v[1] for v in by.values())
print(f'{tt:7d} {hh:9d}  TOTAL')
print()
print('TOKENS NOT FOUND ANYWHERE IN LEDGER:')
seen=set()
for cur,i,n,hit,l in rows:
    if not hit and (cur,n) not in seen:
        seen.add((cur,n)); print(f'  L{i:4d} [{cur[:26]:26s}] {n:>10s}   {l}')
