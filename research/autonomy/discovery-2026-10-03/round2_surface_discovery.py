"""Exploratory frozen-universe tissue screen; ROUND2-PLAN.txt predates results."""
import csv, gzip, json, hashlib, datetime
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu
from antigen_pilot import BASE, ROOT, SOURCE, MANIFEST, EMC, HIST, auc, sha

def main():
    universe=BASE/'round2-surface-universe.tsv'
    with universe.open(encoding='utf-8') as f:
        ur=list(csv.DictReader(f,delimiter='\t'))
    ambiguous=[r for r in ur if ';' in r['Gene Names (primary)']]
    symbols=sorted({r['Gene Names (primary)'].strip() for r in ur if r['Gene Names (primary)'].strip() and ';' not in r['Gene Names (primary)']})
    assert all(' ' not in s for s in symbols), 'Ambiguous primary symbol'
    samples=[r for r in json.loads(MANIFEST.read_text())['samples'] if r['eligible'] and r['diagnosis'] in [EMC]+HIST]
    groups={h:[r for r in samples if r['diagnosis']==h] for h in [EMC]+HIST}
    assert [len(groups[h]) for h in [EMC]+HIST]==[9,14,13,18]
    matrix=SOURCE/'tpm_matrix.tsv.gz'; vals={}; ss=set(symbols)
    with gzip.open(matrix,'rt',encoding='utf-8-sig') as f:
        rd=csv.reader(f,delimiter='\t'); head=next(rd)[1:]
        ix={h:[head.index(r['sample_id']) for r in groups[h]] for h in groups}
        for row in rd:
            if row[0] not in ss: continue
            assert row[0] not in vals
            v=np.array(row[1:],dtype=float)
            vals[row[0]]={h:v[ix[h]] for h in groups}
    out=[]
    for g,v in sorted(vals.items()):
        e=v[EMC]; r={'gene':g,'median_EMC_TPM':float(np.median(e)),'minimum_EMC_TPM':float(min(e))}
        for h in HIST:
            b=v[h]; allv=np.r_[e,b]; method='exact' if len(set(allv))==len(allv) else 'asymptotic'
            p=float(mannwhitneyu(e,b,alternative='greater',method=method).pvalue)
            years=sorted({s['sequencing_year'] for s in groups[EMC]} & {s['sequencing_year'] for s in groups[h]})
            ma=[]
            for y in years:
                a=e[[s['sequencing_year']==y for s in groups[EMC]]]
                c=b[[s['sequencing_year']==y for s in groups[h]]]
                ma.extend([auc(a,c)]*len(a))
            r[h+'_A']=auc(e,b); r[h+'_matched_A']=float(np.mean(ma)); r[h+'_p']=p
            r[h+'_p_method']=method; r[h+'_median_TPM']=float(np.median(b))
            r[h+'_median_log2_contrast']=float(np.median(np.log2(1+e))-np.median(np.log2(1+b)))
        r['intersection_union_p']=max(r[h+'_p'] for h in HIST);out.append(r)
    order=np.argsort([r['intersection_union_p'] for r in out]); n=len(out)
    qs=np.minimum.accumulate(np.array([out[i]['intersection_union_p']*n/(j+1) for j,i in enumerate(order)])[::-1])[::-1]
    for i,q in zip(order,qs):out[i]['BH_q']=float(min(1,q))
    for r in out:
        r['allocated']=bool(r['BH_q']<=.05 and r['median_EMC_TPM']>=5 and r['minimum_EMC_TPM']>=1 and all(r[h+'_A']>=.85 and r[h+'_matched_A']>=.85 and r[h+'_median_log2_contrast']>=1 for h in HIST))
    dst=BASE/'round2-surface-discovery.tsv'
    with dst.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
    hits=[r for r in out if r['allocated']]
    receipt={'schema':'round2-surface-discovery/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Exploratory tissue RNA, not localization/dependency/clinical validity','ambiguous_uniprot_entries_excluded':ambiguous,'universe_symbols':len(symbols),'tested':n,'missing_symbols':sorted(ss-set(vals)),'samples':samples,'hits':hits,'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [universe,matrix,MANIFEST,Path(__file__),BASE/'ROUND2-PLAN.txt',dst]}}
    (BASE/'round2-surface-hits-frozen.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tested':n,'universe':len(symbols),'hits':hits},indent=2))

if __name__=='__main__': main()
