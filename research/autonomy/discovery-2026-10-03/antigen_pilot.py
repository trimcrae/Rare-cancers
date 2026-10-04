"""Bounded exploratory EMC bulk-RNA pilot; see PLAN.txt written before values."""
import csv, gzip, hashlib, json, sys
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
SOURCE=ROOT/'research/autonomy/atlas-hofvander-source-2026-09-06'
MANIFEST=ROOT/'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
PROGRAM=['HLA-A','HLA-B','HLA-C','B2M','TAP1','TAP2','TAPBP','NLRC5','PSMB8','PSMB9']
IMMUNE=['PTPRC','CD3D','CD3E','CD8A','CD8B','LST1','FCER1G','AIF1']
GENES=PROGRAM+IMMUNE+['CHRNA6']
EMC='Extraskeletal myxoid chondrosarcoma'
HIST=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def auc(a,b):
    return float(np.mean((a[:,None]>b[None,:])+.5*(a[:,None]==b[None,:]))) if len(a) and len(b) else None

def calculate(groups,values):
    out={}
    for h in HIST:
        e=groups[EMC]; c=groups[h]
        years=sorted(set(x['sequencing_year'] for x in e)&set(x['sequencing_year'] for x in c))
        counts={y:sum(x['sequencing_year']==y for x in e) for y in years}
        den=sum(counts.values())
        by_gene={}
        for g in GENES:
            v=values[g]
            a=np.array([v[x['sample_id']] for x in e]); b=np.array([v[x['sample_id']] for x in c])
            match=sum(counts[y]*auc(np.array([v[x['sample_id']] for x in e if x['sequencing_year']==y]),np.array([v[x['sample_id']] for x in c if x['sequencing_year']==y])) for y in years)/den if den else None
            by_gene[g]={'marginal':auc(a,b),'matched':match}
        out[h]={'n_emc':len(e),'n_comparator':len(c),'matched_emc':den,'years':years,'genes':by_gene,
            'program':{k:float(np.mean([by_gene[g][k] for g in PROGRAM])) if den or k=='marginal' else None for k in ['marginal','matched']},
            'immune_controls':{k:float(np.mean([by_gene[g][k] for g in IMMUNE])) if den or k=='marginal' else None for k in ['marginal','matched']}}
    return out

def compact(est):
    return {h:{'program':z['program'],'immune_controls':z['immune_controls']} for h,z in est.items()}

def run():
    manifest=json.loads(MANIFEST.read_text())
    rows=[r for r in manifest['samples'] if r['eligible'] and r['diagnosis'] in [EMC]+HIST]
    assert len({r['sample_id'] for r in rows})==len(rows)
    groups={h:[r for r in rows if r['diagnosis']==h] for h in [EMC]+HIST}
    assert [len(groups[h]) for h in [EMC]+HIST]==[9,14,13,18]
    values={}; ids={r['sample_id'] for r in rows}
    matrix=SOURCE/'tpm_matrix.tsv.gz'
    with gzip.open(matrix,'rt',encoding='utf-8-sig') as f:
        reader=csv.reader(f,delimiter='\t');header=next(reader)[1:]
        for row in reader:
            if row[0] in GENES:
                assert row[0] not in values
                v=dict(zip(header,map(float,row[1:])))
                values[row[0]]={s:v[s] for s in sorted(ids)}
    assert set(values)==set(GENES)
    assert all(np.isfinite(v) and v>=0 for row in values.values() for v in row.values())
    est=calculate(groups,values)
    deletions={}
    for kind,keys in [('patient',[r['sample_id'] for r in groups[EMC]]),('year',sorted({r['sequencing_year'] for r in rows}))]:
        ds={}
        for key in keys:
            g={h:[r for r in rr if (r['sample_id']!=key if kind=='patient' else r['sequencing_year']!=key)] for h,rr in groups.items()}
            ds[key]=compact(calculate(g,values))
        deletions[kind]=ds
    # Patient bootstrap, shared EMC resamples across comparator contrasts.
    rng=np.random.default_rng(20261003); draws={h:{k:[] for k in ['marginal','matched']} for h in HIST}
    strata={}
    for h,rr in groups.items():
        strata[h]=[[r for r in rr if r['sequencing_year']==y] for y in sorted({r['sequencing_year'] for r in rr})]
    for _ in range(2000):
        g={h:[s[int(i)] for s in ss for i in rng.integers(0,len(s),size=len(s))] for h,ss in strata.items()}
        z=calculate(g,values)
        for h in HIST:
            for k in draws[h]:draws[h][k].append(z[h]['program'][k])
    ci={h:{k:np.quantile(v,[.025,.975]).tolist() for k,v in z.items()} for h,z in draws.items()}
    primary=[est[h]['program'][k] for h in HIST for k in ['marginal','matched']]
    consistent_large_low=all(v<=.30 for v in primary)
    consistent_large_high=all(v>=.70 for v in primary)
    result={'question':'Coordinated antigen-processing bulk RNA difference in EMC',
        'scope':'Expression only; correlated genes; no tumor-cell localization, peptide presentation, immune response or efficacy',
        'source_url':'https://doi.org/10.5281/zenodo.17866629',
        'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [matrix,MANIFEST]},
        'analysis_sha256':sha(Path(__file__)),'seed':20261003,'replicates':2000,
        'samples':rows,'selected_values':values,'estimates':est,'deletions':deletions,'conditional_bootstrap_95':ci,
        'allocation':{'all_six_large_low':consistent_large_low,'all_six_large_high':consistent_large_high,
                      'continue':consistent_large_low or consistent_large_high,
                      'note':'If size criterion fails, no post hoc individual-gene rescue. If passes, deletion review and replication required.'}}
    (BASE/'antigen-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'summary':compact(est),'conditional_bootstrap_95':ci,'allocation':result['allocation']},indent=2))

if __name__=='__main__':run()
