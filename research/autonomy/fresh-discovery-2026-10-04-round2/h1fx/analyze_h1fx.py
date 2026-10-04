"""Targeted test of a published EMC-lineage interpretation; no prognostic model."""
from pathlib import Path
from datetime import datetime,timezone
import csv,gzip,io,zipfile,json,hashlib,collections,urllib.request
import numpy as np
from scipy.stats import mannwhitneyu
P=Path(__file__).resolve().parent
R=Path('C:/Projects/EMC-Research/research/autonomy')
G={'H1FX':{'H1FX','H1-10'},'PXN':{'PXN'},'TYMS':{'TYMS'}}
ENTREZ={'H1FX':'8971','PXN':'5829','TYMS':'7298'}
EMC='Extraskeletal myxoid chondrosarcoma'
MYX=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Myxofibrosarcoma']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fetch(url,name):
    path=P/name
    if not path.exists():
        with urllib.request.urlopen(url,timeout=30) as r:
            b=r.read(2000000)
        assert len(b)<2000000
        path.write_bytes(b)
    return {'url':url,'path':name,'bytes':path.stat().st_size,'sha256':sha(path)},path.read_text(errors='replace')
def A(a,b):return float(np.mean((a[:,None]>b[None,:])+.5*(a[:,None]==b[None,:])))
rng=np.random.default_rng(20261004)
def compare(a,b,unit,boot=False):
    a=np.array(a,float);b=np.array(b,float);mode='exact' if len(set(np.r_[a,b]))==len(a)+len(b) else 'asymptotic'
    r={'n_EMC':len(a),'n_comparator':len(b),'A':A(a,b),'EMC_median':float(np.median(a)),'comparator_median':float(np.median(b)),'median_difference':float(np.median(a)-np.median(b)),'p_two_sided':float(mannwhitneyu(a,b,alternative='two-sided',method=mode).pvalue),'p_method':mode,'units':unit}
    if unit=='TPM':r['log2_1plus_median_difference']=float(np.median(np.log2(1+a))-np.median(np.log2(1+b)))
    if boot:
        bs=[A(rng.choice(a,len(a),replace=True),rng.choice(b,len(b),replace=True)) for _ in range(2000)]
        r['bootstrap_A_95']=list(map(float,np.quantile(bs,[.025,.975])))
    return r
def bh(rows,name):
    rows=sorted(rows,key=lambda r:r['p_two_sided']);n=len(rows)
    qs=np.minimum.accumulate(np.array([r['p_two_sided']*n/(i+1) for i,r in enumerate(rows)])[::-1])[::-1]
    for r,q in zip(rows,qs):r[name]=min(1.,float(q))
def main():
    sources=[]
    for target,name in [('self','GSE6481-series.txt'),('gsm','GSE6481-samples.txt')]:
        s,t=fetch('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE6481&targ='+target+'&view=brief&form=text',name);sources.append(s)
        if target=='gsm':raw=t
    rows=[]
    for block in raw.split('^SAMPLE = ')[1:]:
        ls=block.splitlines();r={'sample':ls[0].strip(),'metadata':{}}
        for line in ls[1:]:
            if ' = ' in line:
                k,v=line.split(' = ',1);r['metadata'].setdefault(k,[]).append(v)
        r['histology']=[v.split(':',1)[1].strip() for v in r['metadata'].get('!Sample_characteristics_ch1',[]) if v.startswith('Histology:')]
        rows.append(r)
    assert len(rows)==105
    identity={'sources':sources,'all105_samples':rows,'histology_counts':dict(collections.Counter(x for r in rows for x in r['histology'])),'EMC_explicit_matches':[r['sample'] for r in rows if any('extraskeletal' in v.lower() or 'chondrosarcoma' in v.lower() for v in r['histology'])], 'limit':'No relabelling from sample name. Cannot identify an alternative intended accession without a public crosswalk.'}
    (P/'GSE6481-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    mp=R/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json';xp=R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
    samples=json.loads(mp.read_text())['samples'];emc=[s for s in samples if s['diagnosis']==EMC]
    groups={h:[s for s in samples if s['diagnosis']==h and s['primary_lesion']] for h in MYX}
    groups['all_primary_nonEMC_mixed_context']=[s for s in samples if s['primary_lesion'] and s['diagnosis']!=EMC]
    scopes={'primary9':[s for s in emc if s['eligible']],'all12primary':[s for s in emc if s['primary_lesion']],'all13':emc}
    assert [len(v) for v in scopes.values()]==[9,12,13]
    values={};symbols={}
    with gzip.open(xp,'rt',encoding='utf-8-sig') as f:
        rd=csv.reader(f,delimiter='\t');head=next(rd)[1:]
        for row in rd:
            for g,aliases in G.items():
                if row[0] in aliases:
                    assert g not in values
                    symbols[g]=row[0];values[g]=dict(zip(head,map(float,row[1:])))
    assert set(values)==set(G)
    rna={}
    for g in G:
        rna[g]={}
        for scope,es in scopes.items():
            rna[g][scope]={}
            for h,ss in groups.items():
                a=[values[g][s['sample_id']] for s in es];b=[values[g][s['sample_id']] for s in ss]
                r=compare(a,b,'TPM',scope=='primary9')
                ys=sorted({s['sequencing_year'] for s in es}&{s['sequencing_year'] for s in ss})
                r['same_year']={y:compare([values[g][s['sample_id']] for s in es if s['sequencing_year']==y],[values[g][s['sample_id']] for s in ss if s['sequencing_year']==y],'TPM') for y in ys}
                rna[g][scope][h]=r
    bh([r for g in G for r in rna[g]['primary9'].values()],'BH_q_over12')
    ap=R/'atlas-original-array-source-2026-09-06/original-source-recovery.zip';sp=R/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz';amp=R/'atlas-hofvander-validation-2026-09-06/replication-manifest.json'
    mapping=[]
    with zipfile.ZipFile(ap) as z:
        for r in csv.DictReader(io.StringIO(z.read('GPL6244-original-annotation.tsv').decode()),delimiter='\t'):
            parts=[x.split(' // ') for x in r['gene_assignment'].split(' /// ')]
            ids={x[4].strip() for x in parts if len(x)>=5}
            for g,e in ENTREZ.items():
                if e in ids:mapping.append({'gene':g,'probe':r['ID'],'ids':sorted(ids),'accepted':ids=={e},'annotation':r['gene_assignment']})
    keep={r['probe']:r['gene'] for r in mapping if r['accepted']};av={p:{} for p in keep}
    with gzip.open(sp,'rt') as f:
        current=None;inside=False;cols=None
        for line in f:
            line=line.rstrip('\r\n')
            if line.startswith('^SAMPLE = '):current=line.split(' = ',1)[1]
            elif line=='!sample_table_begin':inside=True;cols=None
            elif line=='!sample_table_end':inside=False
            elif inside:
                x=line.split('\t')
                if cols is None:cols=x;continue
                if x[0] in av:av[x[0]][current]=float(x[cols.index('VALUE')])
    asm=json.loads(amp.read_text())['array_samples'];ags=collections.defaultdict(list)
    for s in asm:ags[s['diagnosis']].append(s['sample_id'])
    ga={};ar={}
    for g in G:
        ps=[p for p in keep if keep[p]==g];assert ps
        ga[g]={'probes':ps,'values':{s['sample_id']:float(np.median([av[p][s['sample_id']] for p in ps])) for s in asm}}
        v=ga[g]['values'];ar[g]={h:compare([v[s] for s in ags[EMC]],[v[s] for s in ss],'original processed array intensity',h in MYX) for h,ss in ags.items() if h!=EMC}
    bh([ar[g][h] for g in G for h in MYX[1:]],'BH_q_over6_myxo_comparisons')
    out={'utc':datetime.now(timezone.utc).isoformat(),'contract_sha256':sha(P.parent/'H1FX-FOLLOWUP-CONTRACT.json'),'amendment_sha256':sha(P/'AMENDMENT-01.json'),'input_hashes':{str(p):sha(p) for p in [mp,xp,ap,sp,amp]},'RNA_symbols':symbols,'RNA_all_EMC_metadata':emc,'RNA_comparator_metadata':groups,'RNA_all_source_gene_values':values,'RNA_results':rna,'array_mapping':mapping,'array_all_sample_metadata':asm,'array_per_probe_values':av,'array_gene_values':ga,'array_results':ar,'limits':['Targeted exploratory reanalysis of published marker candidates; not preregistered clinical validation','No outcomes in comparator cohorts, no prognostic or efficacy inference','Overlap between historicalarray andLundRNA unknown; no pooledn','Source accession mismatch is not proof of fabricated results or of H1FX biological absence','Mixedcontext includes benign/intermediate tumors; it is not a malignant-only contrast']}
    (P/'expression-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'identity_histologies':identity['histology_counts'],'RNA_H1FX':rna['H1FX']['primary9'],'array_H1FX':ar['H1FX']}))
if __name__=='__main__':main()
