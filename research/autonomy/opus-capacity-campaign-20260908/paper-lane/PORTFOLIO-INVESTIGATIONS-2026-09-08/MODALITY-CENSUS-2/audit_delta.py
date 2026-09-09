import json,os
old=json.load(open('research/modalities/census-novelty-audit.json'))
new=json.load(open('research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/MODALITY-CENSUS-2/census-novelty-audit.REGENERATED.json'))
print("SCALAR KEYS")
for k in old:
    if k=='findings': continue
    print(f"  {k}: {'SAME' if old[k]==new[k] else repr(old[k])+'  ->  '+repr(new[k])}")
o,n=set(old['findings']),set(new['findings'])
print(f"\nFINDINGS: {len(o)} -> {len(n)}")
print(f"  dropped ({len(o-n)}): {sorted(o-n)}")
print(f"  added   ({len(n-o)}): {sorted(n-o)}")
same=sorted(o&n)
ch=[k for k in same if old['findings'][k]!=new['findings'][k]]
print(f"  present in both: {len(same)}; of those CHANGED: {len(ch)}; byte-identical: {len(same)-len(ch)}")
print("\n  n_files movement for every retained id:")
for k in sorted(same,key=lambda k:-new['findings'][k]['n_files']):
    a,b=old['findings'][k]['n_files'],new['findings'][k]['n_files']
    if a!=b: print(f"    {k:<30} n_files {a:>4} -> {b:>4}")
print("\n  retained ids whose n_files did NOT move:",[k for k in same if old['findings'][k]['n_files']==new['findings'][k]['n_files']])
# which dropped ids are dropped because they are no longer never_searched
rows={r['id']:r for r in json.load(open('systems/graph/modalities.json'))}
print("\n  reason each dropped id left:")
for k in sorted(o-n):
    r=rows.get(k)
    print(f"    {k:<30} prior_coverage={'ABSENT FROM REGISTRY' if r is None else r['prior_coverage']}")
