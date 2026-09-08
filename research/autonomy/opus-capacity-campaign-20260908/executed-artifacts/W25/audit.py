"""W25 audit of the W19c/W20b/W19e pair statistic. Read-only. No repository write."""
import json, itertools, math, random, statistics as st
SUP="/home/user/Rare-cancers/research/modalities/gse243553-eno3-overlap-supplement.json"
INV="/home/user/Rare-cancers/research/modalities/gse243553-eno3-overlap.json"
sup=json.load(open(SUP)); inv=json.load(open(INV))
fb=sup['contents']['SPRINGER::3::zip']['first_bytes']
pref={}
for k,v in fb.items():
    if not k.startswith('Supp_Data_1_new/') or not k.endswith('_markers.bed'): continue
    name=k.split('/')[1][:-len('_markers.bed')]
    iv=[]
    lines=v.split('\n')
    for ln in lines[:-1]:                      # discard trailing partial line
        p=ln.split('\t')
        if len(p)>=3 and p[0]=='chr1':
            try: iv.append((int(p[1]),int(p[2])))
            except ValueError: pass
    if iv: pref[name]=iv
names=sorted(pref)
nint={}
for f,e in inv['peakset_inventory'].items():
    if f.startswith('Supp_Data_1_new/') and f.endswith('_markers.bed'):
        nint[f.split('/')[1][:-len('_markers.bed')]]=e['n_intervals']
print("peaksets with chr1 prefixes:",len(names))
print("sorted-ascending all:",all(all(a[0]<b[0] for a,b in zip(v,v[1:])) for v in pref.values()))
print("widths:",sorted({e-s for v in pref.values() for s,e in v}))
print("retained intervals per peakset: min %d median %d max %d"%(min(len(v) for v in pref.values()),
      st.median([len(v) for v in pref.values()]),max(len(v) for v in pref.values())))

def pairstat(a,b):
    W=min(pref[a][-1][1],pref[b][-1][1])
    A={x for x in pref[a] if x[1]<=W}; B={x for x in pref[b] if x[1]<=W}
    if not A or not B: return None
    inter=len(A&B); uni=len(A|B)
    return dict(J=inter/uni, W=W, nA=len(A), nB=len(B), shared=inter,
                mind=min(len(A),len(B)), maxd=max(len(A),len(B)),
                d=abs(math.log10(nint[a])-math.log10(nint[b])))
pairs={}
for a,b in itertools.combinations(names,2):
    s=pairstat(a,b)
    if s: pairs[(a,b)]=s
P=list(pairs); print("non-degenerate pairs:",len(P),"of",len(list(itertools.combinations(names,2))))

# ---- density quintiles (W19c's residual) ----
order=sorted(P,key=lambda p:pairs[p]['d'])
q={}; n=len(order)
for i,p in enumerate(order): q[p]=min(4,i*5//n)
qm={k:st.mean([pairs[p]['J'] for p in P if q[p]==k]) for k in range(5)}
print("quintile mean J:",{k:round(v,4) for k,v in qm.items()})
for p in P: pairs[p]['res']=pairs[p]['J']-qm[q[p]]

def cls(p):
    a,b=p; a5,a3=a.split('-',1); b5,b3=b.split('-',1)
    if a5==b5: return 'SHARES-5'
    if a3==b3: return 'SHARES-3'
    return 'NEITHER'
FAM={'ETV1':'ETS','ETV4':'ETS','FEV':'ETS','FLI1':'ETS','ERG':'ETS','ATF1':'CREB','CREB1':'CREB'}
def samefam(p):
    a,b=p; a3=a.split('-',1)[1]; b3=b.split('-',1)[1]
    return a3 in FAM and b3 in FAM and FAM[a3]==FAM[b3] and a3!=b3

# ---- 1. DEPENDENCE ----
print("\n=== 1. EXPERIMENTAL UNIT / DEPENDENCE ===")
from collections import Counter
for label,sel in [('SHARES-3',[p for p in P if cls(p)=='SHARES-3']),
                  ('SHARES-5',[p for p in P if cls(p)=='SHARES-5']),
                  ('SAMEFAM-DIFFGENE',[p for p in P if samefam(p)]),
                  ('ALL',P)]:
    ps=Counter(); [ps.update(p) for p in sel]
    print(f"{label:18s} n_pairs={len(sel):3d} distinct_peaksets={len(ps):2d} "
          f"max_pairs_from_one_peakset={max(ps.values()) if ps else 0} "
          f"pairs/peakset={len(sel)/max(1,len(ps)):.2f}")

# ---- 2. WINDOW DEPTH: the uncontrolled driver ----
print("\n=== 2. WINDOW DEPTH min(|A|,|B|) BY CLASS (NOT controlled by the density residual) ===")
for label,sel in [('SHARES-3',[p for p in P if cls(p)=='SHARES-3']),
                  ('SHARES-5',[p for p in P if cls(p)=='SHARES-5']),
                  ('NEITHER',[p for p in P if cls(p)=='NEITHER']),
                  ('SAMEFAM-DIFFGENE',[p for p in P if samefam(p)]),
                  ('ALL',P)]:
    md=[pairs[p]['mind'] for p in sel]
    print(f"{label:18s} n={len(sel):3d} median_min_depth={st.median(md):5.1f} mean={st.mean(md):5.2f} "
          f"mean_J={st.mean([pairs[p]['J'] for p in sel]):.4f} mean_res={st.mean([pairs[p]['res'] for p in sel]):+.4f}")
# J vs min depth across whole panel
bins={}
for p in P: bins.setdefault(min(pairs[p]['mind']//5,4),[]).append(pairs[p]['J'])
print("mean J by min-depth bin (0-4,5-9,10-14,15-19,20+):",
      {k:(len(v),round(st.mean(v),4)) for k,v in sorted(bins.items())})

# ---- 3. residual with min-depth ALSO controlled (quintiles of depth x quintiles of d) ----
print("\n=== 3. RESIDUAL AFTER ALSO CONTROLLING WINDOW DEPTH ===")
dorder=sorted(P,key=lambda p:pairs[p]['mind']); dq={}
for i,p in enumerate(dorder): dq[p]=min(4,i*5//len(dorder))
cell={}
for p in P: cell.setdefault((q[p],dq[p]),[]).append(p)
cm={k:st.mean([pairs[p]['J'] for p in v]) for k,v in cell.items()}
for p in P: pairs[p]['res2']=pairs[p]['J']-cm[(q[p],dq[p])]
for label,fn in [('SHARES-3',lambda p:cls(p)=='SHARES-3'),('SHARES-5',lambda p:cls(p)=='SHARES-5'),
                 ('NEITHER',lambda p:cls(p)=='NEITHER'),('SAMEFAM-DIFFGENE',samefam)]:
    sel=[p for p in P if fn(p)]
    print(f"{label:18s} n={len(sel):3d} mean_res(density only)={st.mean([pairs[p]['res'] for p in sel]):+.4f} "
          f"mean_res(density x depth)={st.mean([pairs[p]['res2'] for p in sel]):+.4f}")

# ---- 4. permutation under BOTH residuals ----
print("\n=== 4. WHOLE-NAME PERMUTATION, both residual definitions (50000 draws, seed 20260908) ===")
def perm_p(fn,key,ndraw=50000,seed=20260908):
    obs=st.mean([pairs[p][key] for p in P if fn(p)])
    rng=random.Random(seed); ge=0
    idx={nm:i for i,nm in enumerate(names)}
    for _ in range(ndraw):
        perm=names[:]; rng.shuffle(perm)
        m={names[i]:perm[i] for i in range(len(names))}
        vals=[pairs[p][key] for p in P if fn((m[p[0]],m[p[1]]))]
        if vals and st.mean(vals)>=obs: ge+=1
    return obs,(1+ge)/(1+ndraw)
for label,fn in [('SHARES-3',lambda p:cls(p)=='SHARES-3'),('SAMEFAM-DIFFGENE',samefam)]:
    for key in ('res','res2'):
        o,pv=perm_p(fn,key)
        print(f"{label:18s} stat={key:5s} obs={o:+.4f} one-sided p={pv:.5f}")
