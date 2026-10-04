"""Exploratory fixed-control/flag sensitivity and technical-batch audit."""
import csv
import hashlib
import json
from pathlib import Path
import statistics as st
import sys
BASE=Path(__file__).resolve().parent
OLD=BASE.parent/'tmem266-prepublication-2026-10-03'
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'.cache/python-deps'))
import numpy as np

def A(x,y):
    return sum((a>b)+.5*(a==b) for a in x for b in y)/(len(x)*len(y))

def summary(rows,field):
    groups={k:[r for r in rows if r['group']==k and r[field] is not None] for k in ['EMC','LGFMS','muscle']}
    vals={k:[r[field] for r in v] for k,v in groups.items()}
    out={'n':{k:len(v) for k,v in vals.items()},'values':vals,
         'median':{k:st.median(v) if v else None for k,v in vals.items()},
         'A':A(vals['EMC'],vals['LGFMS']) if vals['EMC'] and vals['LGFMS'] else None}
    if len(vals['EMC'])==6 and len(vals['LGFMS'])==17:
        rng=np.random.default_rng(20261004)
        boot=[A([float(a) for a in rng.choice(vals['EMC'],6)],
                [float(b) for b in rng.choice(vals['LGFMS'],17)]) for _ in range(2000)]
        out['descriptive_bootstrap_A95']=np.quantile(boot,[.025,.975]).tolist()
    return out

def parameter(node,key):
    matches=[]
    if key in node.get('parameters',{}):matches.append(node['parameters'][key].get('decoded'))
    for child in node.get('parents',[]):matches+=parameter(child,key)
    return sorted(set(x for x in matches if x is not None))

def main():
    raw=json.loads((OLD/'raw-array-results.json').read_text())
    heads=json.loads((BASE/'cel-headers.json').read_text())
    mp=list(csv.DictReader((OLD/'probe-map.csv').open()))
    groups={'upstream':list(range(7985069,7985075)), 'strict':list(range(7985070,7985075))}
    region={int(r['physical_probe_id']):int(r['child_probeset']) for r in mp}
    rows=[]
    for i,(arr,head) in enumerate(zip(raw['arrays'],heads['arrays'])):
        assert arr['acc']==head['accession']
        label='EMC' if i<6 else 'LGFMS' if i<23 else 'muscle'
        dates=parameter(head['header'],'affymetrix-scan-date')
        assert len(dates)==1
        q={'accession':arr['acc'],'group':label,'source_alias':parameter(head['header'],'affymetrix-fusion-experiment-name'),
           'scan_timestamp':dates[0],'scan_day':dates[0][:10],
           'scanner':parameter(head['header'],'affymetrix-scanner-id')}
        for name,rs in groups.items():
            kept={g:[p for p in arr['selected'] if region[p['id']]==g and not(p['mask'] or p['outlier'])] for g in rs}
            q[name+'_retained_probes']=sum(len(v) for v in kept.values())
            q[name+'_incomplete_regions']=[g for g,v in kept.items() if not v]
            q[name+'_unflagged']=st.mean(st.mean(p['percentile'] for p in v) for v in kept.values()) if all(kept.values()) else None
            target=st.mean(st.mean(p['percentile'] for p in arr['selected'] if region[p['id']]==g) for g in rs)
            control=st.mean(st.mean(p['gc_control_mean_percentile'] for p in arr['selected'] if region[p['id']]==g) for g in rs)
            q[name+'_GC_contrast']=target-control
        rows.append(q)
    dates={k:sorted({r['scan_day'] for r in rows if r['group']==k}) for k in ['EMC','LGFMS','muscle']}
    shared=sorted(set(dates['EMC'])&set(dates['LGFMS']))
    assert not shared
    out={'scope':'Post-selection technical sensitivity in reused arrays; no batch correction or new validation',
         'sources':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [OLD/'raw-array-results.json',OLD/'probe-map.csv',BASE/'cel-headers.json']},
         'arrays':rows,'scan_days':dates,'shared_EMC_LGFMS_scan_days':shared,
         'within_scan_day_comparison':'Not identifiable: histology and scan day have no overlap',
         'summary':{f:summary(rows,f) for f in ['upstream_unflagged','strict_unflagged','upstream_GC_contrast','strict_GC_contrast']}}
    (BASE/'array-robustness.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'scan_days':dates,'results':{f:{k:v[k] for k in ['n','A']} for f,v in out['summary'].items()}}))

if __name__=='__main__':main()
