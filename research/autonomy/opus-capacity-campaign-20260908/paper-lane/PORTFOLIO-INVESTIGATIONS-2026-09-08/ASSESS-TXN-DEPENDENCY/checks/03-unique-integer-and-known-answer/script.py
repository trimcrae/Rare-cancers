import json
d=json.load(open('research/modalities/depmap-sarcoma-dependency.json'))
recs={}
def collect(o):
    if isinstance(o,dict):
        if 'gene' in o and 'sarcoma_frac_dependent' in o: recs.setdefault(o['gene'],[]).append(o)
        for v in o.values(): collect(v)
    elif isinstance(o,list):
        for v in o: collect(v)
collect(d)
print('threshold:',d['dependent_threshold'],'n_models_total:',d['n_models_total'],'n_sarcoma_models:',d['n_sarcoma_models'])
print()
print('=== KNOWN-ANSWER CONTROL (independent re-read) ===')
for g in ['CDK7','CDK9']:
    for r in recs[g]:
        print(g, {k:r[k] for k in ('sarcoma_mean','rest_mean','selectivity','sarcoma_frac_dependent','rest_frac_dependent','n_sarcoma')})
ns=set()
for g,rs in recs.items():
    for r in rs: ns.add(r['n_sarcoma'])
print('distinct n_sarcoma across all gene records:',ns,'; n gene records:',sum(len(v) for v in recs.values()))
print()
print('=== UNIQUE-INTEGER SENSITIVITY for the five printed genes ===')
print('For each gene: which integers k in 0..n satisfy round(k/n, p) == stored fraction,')
print('for p = the number of decimals actually stored, and for p-1 (a looser store).')
for g,printed in [('CDK7','91/91'),('CDK9','91/91'),('HSP90AA1','5/91'),('HSP90AB1','17/91'),('CDC37','89/91')]:
    r=recs[g][0]; f=r['sarcoma_frac_dependent']; n=r['n_sarcoma']
    s=repr(f); dec = len(s.split('.')[1]) if '.' in s else 0
    for p in (dec, max(dec-1,0)):
        ks=[k for k in range(n+1) if round(round(k/n,p)-round(f,p),12)==0]
        print(f'  {g:9s} stored={f!r:8s} n={n} printed={printed:6s} decimals={p}: compatible k = {ks}')
    # also: what if the stored value were merely 2-dp
    ks2=[k for k in range(n+1) if abs(k/n - f) <= 0.005]
    print(f'            +/-0.005 band -> k in {ks2}')
print()
print('=== rest_frac_dependent: is a denominator recoverable? ===')
for g in ['CDK7','CDK9','HSP90AA1','HSP90AB1','CDC37']:
    r=recs[g][0]
    print(f'  {g:9s} rest_frac={r["rest_frac_dependent"]}  n_rest key present: {"n_rest" in r}  keys={list(r)}')
