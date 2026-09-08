exec(open('audit.py').read().split('# ---- 1. DEPENDENCE ----')[0])
import statistics as st, random
def cls(p):
    a,b=p; a5,a3=a.split('-',1); b5,b3=b.split('-',1)
    if a5==b5: return 'SHARES-5'
    if a3==b3: return 'SHARES-3'
    return 'NEITHER'
FAM={'ETV1':'ETS','ETV4':'ETS','FEV':'ETS','FLI1':'ETS','ERG':'ETS','ATF1':'CREB','CREB1':'CREB'}
def samefam(p):
    a3=p[0].split('-',1)[1]; b3=p[1].split('-',1)[1]
    return a3 in FAM and b3 in FAM and FAM[a3]==FAM[b3] and a3!=b3

# quintile membership + within-quintile density imbalance
print("=== quintile membership and within-quintile |dlog10 n| imbalance ===")
for label,fn in [('SHARES-3',lambda p:cls(p)=='SHARES-3'),('SAMEFAM-DIFFGENE',samefam)]:
    sel=[p for p in P if fn(p)]
    from collections import Counter
    print(f"{label}: quintile counts {dict(sorted(Counter(q[p] for p in sel).items()))}")
    for k in range(5):
        cl=[pairs[p]['d'] for p in sel if q[p]==k]
        al=[pairs[p]['d'] for p in P if q[p]==k]
        if cl: print(f"   Q{k}: class mean|dlog n|={st.mean(cl):.4f} (n={len(cl)}) vs quintile mean={st.mean(al):.4f}")

# density of the peaksets carrying each class
print("\n=== n_intervals of the peaksets in each class ===")
for label,fn in [('SHARES-3',lambda p:cls(p)=='SHARES-3'),('SAMEFAM-DIFFGENE',samefam)]:
    ps=sorted({x for p in P if fn(p) for x in p})
    print(f"{label}: {len(ps)} peaksets -> "+", ".join(f"{x}={nint[x]}" for x in ps))
print("panel n_intervals quartiles:", [round(x) for x in st.quantiles([nint[n] for n in names],n=4)])

# ---- DENSITY-STRATIFIED PERMUTATION: permute labels only within density quartiles ----
print("\n=== STRATIFIED NULL: labels permuted only WITHIN n_intervals quartiles (50000 draws) ===")
srt=sorted(names,key=lambda n:nint[n])
strata={}
for i,n in enumerate(srt): strata.setdefault(min(3,i*4//len(srt)),[]).append(n)
print("strata sizes:",{k:len(v) for k,v in strata.items()})
def strat_p(fn,key='res',ndraw=50000,seed=20260908):
    obs=st.mean([pairs[p][key] for p in P if fn(p)])
    rng=random.Random(seed); ge=0
    for _ in range(ndraw):
        m={}
        for k,mem in strata.items():
            perm=mem[:]; rng.shuffle(perm)
            for a,b in zip(mem,perm): m[a]=b
        vals=[pairs[p][key] for p in P if fn((m[p[0]],m[p[1]]))]
        if vals and st.mean(vals)>=obs: ge+=1
    return obs,(1+ge)/(1+ndraw)
for label,fn in [('SHARES-3',lambda p:cls(p)=='SHARES-3'),('SAMEFAM-DIFFGENE',samefam),
                 ('SHARES-5',lambda p:cls(p)=='SHARES-5')]:
    for key in ('res',):
        o,pv=strat_p(fn,key); print(f"{label:18s} stat={key:5s} obs={o:+.4f} stratified p={pv:.5f}")
