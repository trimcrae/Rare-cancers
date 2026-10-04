"""Post-result descriptive uncertainty for ALL16 replication-pass genes."""
import json
import numpy as np
from antigen_pilot import BASE,EMC,sha

src=BASE/'round2-surface-replication.json';j=json.loads(src.read_text())
rows=j['array_samples'];hs=sorted({r['diagnosis'] for r in rows if r['unit']!='pooled_normal_RNA'})
ids={h:[r['sample_id'] for r in rows if r['diagnosis']==h] for h in hs}
rng=np.random.default_rng(20261003)
ix={h:rng.integers(0,len(ss),(2000,len(ss))) for h,ss in ids.items()}
out={}
for g,r in j['genes'].items():
    if not r.get('allocated'):continue
    v=r['values'];e=np.array([v[s] for s in ids[EMC]])[ix[EMC]];out[g]={}
    for h in hs:
        if h==EMC:continue
        b=np.array([v[s] for s in ids[h]])[ix[h]]
        a=((e[:,:,None]>b[:,None,:])+.5*(e[:,:,None]==b[:,None,:])).mean(axis=(1,2))
        out[g][h]={'bootstrap_95_A':np.quantile(a,[.025,.975]).tolist(),'bootstrap_95_median_difference':np.quantile(np.median(e,axis=1)-np.median(b,axis=1),[.025,.975]).tolist()}
result={'scope':'Post-result descriptive patient-within-histology bootstrap in array dataset; selected genes, not selection-adjusted simultaneous intervals; unresolved cross-cohort independence. Complete-separation intervals can degenerate and do not show certainty.','replicates':2000,'seed':20261003,'source_sha256':sha(src),'genes':out}
(BASE/'round2-array-uncertainty.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({g:out[g] for g in ['GPR68','TMEM266','ABHD2']},indent=2))
