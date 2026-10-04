"""All frozen screen hits replicated using original uniquely assigned array probes."""
import csv,gzip,io,json,zipfile,datetime
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu
from antigen_pilot import BASE,ROOT,EMC,auc,sha

def main():
    frozen=BASE/'round2-surface-hits-frozen.json'
    genes=sorted(r['gene'] for r in json.loads(frozen.read_text())['hits'])
    aliases={g:g for g in genes}
    with (BASE/'round2-array-alias-source.tsv').open() as f:
        for r in csv.DictReader(f,delimiter='\t'):
            names=r['Gene Names'].split(); assert names[0] in genes
            for name in names:
                assert name not in aliases or aliases[name]==names[0]
                aliases[name]=names[0]
    src=ROOT/'research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip'
    mapping=[]
    with zipfile.ZipFile(src) as z:
        raw=z.read('GPL6244-original-annotation.tsv')
        for r in csv.DictReader(io.StringIO(raw.decode()),delimiter='\t'):
            ss={p.split(' // ')[1].strip() for p in r['gene_assignment'].split(' /// ') if ' // ' in p}
            if not ss&aliases.keys():continue
            can={aliases.get(s,s) for s in ss}; accepted=len(can)==1 and next(iter(can)) in genes
            mapping.append({'probe':r['ID'],'symbols':sorted(ss),'accepted':accepted,'gene':next(iter(can)) if accepted else None})
    keep={r['probe']:r['gene'] for r in mapping if r['accepted']};vals={p:{} for p in keep}
    ar=ROOT/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz'
    table=False;sample=None;col=None
    with gzip.open(ar,'rt') as f:
        for line in f:
            line=line.rstrip('\r\n')
            if line.startswith('^SAMPLE = '):sample=line.split(' = ',1)[1]
            elif line=='!sample_table_begin':table=True;col=None
            elif line=='!sample_table_end':table=False
            elif table:
                r=line.split('\t')
                if col is None:col=r;continue
                if r[0] in vals:vals[r[0]][sample]=float(r[col.index('VALUE')])
    manifest=ROOT/'research/autonomy/atlas-hofvander-validation-2026-09-06/replication-manifest.json'
    rows=json.loads(manifest.read_text())['array_samples']
    hs=sorted({r['diagnosis'] for r in rows if r['diagnosis']!=EMC and r['unit']!='pooled_normal_RNA'})
    ids={h:[r['sample_id'] for r in rows if r['diagnosis']==h] for h in [EMC]+hs}
    assert len(ids[EMC])==6
    def estimates(v):
        e=np.array([v[s] for s in ids[EMC]]);z={}
        for h in hs:
            b=np.array([v[s] for s in ids[h]]); method='exact' if len(set(np.r_[e,b]))==len(e)+len(b) else 'asymptotic'
            z[h]={'n_emc':len(e),'n_comparator':len(b),'A':auc(e,b),'median_difference':float(np.median(e)-np.median(b)),'one_sided_p':float(mannwhitneyu(e,b,alternative='greater',method=method).pvalue),'p_method':method,'single_EMC_deletion_A':[min(auc(np.delete(e,i),b) for i in range(len(e))),max(auc(np.delete(e,i),b) for i in range(len(e)))]}
        return z
    results={}
    for g in genes:
        ps=[p for p in keep if keep[p]==g]
        if not ps:results[g]={'unmapped':True};continue
        assert all(set(vals[p])=={r['sample_id'] for r in rows} for p in ps)
        median={r['sample_id']:float(np.median([vals[p][r['sample_id']] for p in ps])) for r in rows}
        es=estimates(median)
        results[g]={'probe_ids':ps,'contrasts':es,'allocated':all(v['A']>.5 and v['median_difference']>0 for v in es.values()) and es['Low-grade fibromyxoid sarcoma']['A']>=.8,'values':median,'probe_contrasts':{p:estimates(vals[p]) for p in ps}}
    # Multiplicity display across every frozen nominated gene, missing=1.
    pvals=[results[g].get('contrasts',{}).get('Low-grade fibromyxoid sarcoma',{}).get('one_sided_p',1) for g in genes]
    order=np.argsort(pvals);qs=np.minimum.accumulate(np.array([pvals[i]*len(genes)/(j+1) for j,i in enumerate(order)])[::-1])[::-1]
    for i,q in zip(order,qs):results[genes[i]]['LGFMS_BH_q_across_21']=float(min(1,q))
    out={'schema':'round2-surface-replication/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'array_samples':rows,'mapping':mapping,'genes':results,'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [frozen,BASE/'round2-array-alias-source.tsv',src,ar,manifest,Path(__file__),BASE/'ROUND2-PLAN.txt']}}
    (BASE/'round2-surface-replication.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({g:{'allocated':r.get('allocated'),'probe_ids':r.get('probe_ids'),'A':{h:v['A'] for h,v in r.get('contrasts',{}).items()},'q':r['LGFMS_BH_q_across_21']} for g,r in results.items()},indent=2))

if __name__=='__main__':main()
