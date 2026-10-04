"""All frozen panel probes and nominated genes; no adaptive substitutions."""
from pathlib import Path
import json, csv, gzip, io, zipfile, hashlib, collections
import numpy as np
from scipy.stats import mannwhitneyu
import openpyxl
P=Path(__file__).resolve().parent
R=Path('C:/Projects/EMC-Research/research/autonomy')
plan=json.loads((P/'PLAN.json').read_text())
tissue=json.loads((P/'tissue-results.json').read_text())
genes=plan['all_extracted_genes']; candidates=tissue['allocated_genes']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
entrez={x['symbol']:x['entrez'] for rows in plan['pathways'].values() for x in rows}
source=R/'atlas-original-array-source-2026-09-06/original-source-recovery.zip'
mapping=[]
with zipfile.ZipFile(source) as z:
    for r in csv.DictReader(io.StringIO(z.read('GPL6244-original-annotation.tsv').decode()),delimiter='\t'):
        parts=[x.split(' // ') for x in r['gene_assignment'].split(' /// ')]
        symbols={x[1].strip() for x in parts if len(x)>=2}
        if not symbols&set(genes):continue
        ids={x[4].strip() for x in parts if len(x)>=5}
        g=next(iter(symbols)) if len(symbols)==1 else None
        accepted=g in genes and (g not in entrez or ids=={entrez[g]})
        mapping.append({'probe':r['ID'],'symbols':sorted(symbols),'entrez_ids':sorted(ids),'accepted':accepted,'gene':g if accepted else None,'annotation':r['gene_assignment']})
keep={r['probe']:r['gene'] for r in mapping if r['accepted']};values={k:{} for k in keep}
array=R/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz'
with gzip.open(array,'rt') as f:
    sample=None;inside=False;columns=None
    for line in f:
        line=line.rstrip('\r\n')
        if line.startswith('^SAMPLE = '):sample=line.split(' = ',1)[1]
        elif line=='!sample_table_begin':inside=True;columns=None
        elif line=='!sample_table_end':inside=False
        elif inside:
            x=line.split('\t')
            if columns is None:columns=x;continue
            if x[0] in values:values[x[0]][sample]=float(x[columns.index('VALUE')])
metadata=R/'atlas-hofvander-validation-2026-09-06/replication-manifest.json'
samples=json.loads(metadata.read_text())['array_samples']
groups=collections.defaultdict(list)
for s in samples:groups[s['diagnosis']].append(s['sample_id'])
emc=groups['Extraskeletal myxoid chondrosarcoma'];assert len(emc)==6
def A(a,b):return float(np.mean((a[:,None]>b[None,:])+.5*(a[:,None]==b[None,:])))
gene_values={}
for g in genes:
    ps=[p for p in keep if keep[p]==g]
    if ps:gene_values[g]={'probes':ps,'values':{s['sample_id']:float(np.median([values[p][s['sample_id']] for p in ps])) for s in samples},'per_probe':{p:values[p] for p in ps}}
results={}
for g in candidates:
    if g not in gene_values:results[g]={'missing':True,'intersection_p':1};continue
    v=gene_values[g]['values'];a=np.array([v[s] for s in emc]);r={}
    for h,ss in groups.items():
        if h=='Extraskeletal myxoid chondrosarcoma':continue
        b=np.array([v[s] for s in ss]);both=np.r_[a,b];mode='exact' if len(set(both))==len(both) else 'asymptotic'
        r[h]={'n_emc':len(a),'n_comparator':len(b),'A':A(a,b),'EMC_median':float(np.median(a)),'comparator_median':float(np.median(b)),'difference':float(np.median(a)-np.median(b)),'two_sided_p':float(mannwhitneyu(a,b,alternative='two-sided',method=mode).pvalue),'p_method':mode}
    results[g]={'missing':False,'contrasts':r,'intersection_p':max(r[h]['two_sided_p'] for h in ('Low-grade fibromyxoid sarcoma','Myxofibrosarcoma'))}
order=sorted(results,key=lambda g:results[g]['intersection_p']);n=len(order)
qs=np.minimum.accumulate(np.array([results[g]['intersection_p']*n/(i+1) for i,g in enumerate(order)])[::-1])[::-1]
for g,q in zip(order,qs):
    r=results[g];r['BH_q_across_five']=min(1.,float(q));r['passes_allocation']=False
    if r['missing']:continue
    direction=tissue['genes'][g]['direction'];cc=[r['contrasts'][h] for h in ('Low-grade fibromyxoid sarcoma','Myxofibrosarcoma')]
    r['passes_allocation']=bool(q<=.05 and all((x['A']>=.8 and x['difference']>0) if direction=='higher' else (x['A']<=.2 and x['difference']<0) for x in cc))
ffpe=R/'tmem266-tissue-2026-10-03/peerj-source-s009.xlsx';w=openpyxl.load_workbook(ffpe,read_only=True,data_only=True)
rows=iter(w.active.values);ids=list(next(rows))[1:];peerj={}
for row in rows:
    if row[0] in genes:peerj[row[0]]={s:float(v) for s,v in zip(ids,row[1:])}
w.close()
archs4=R/'tmem266-all-cultures-2026-10-04/archs4-subset.zip'
with zipfile.ZipFile(archs4) as z:rows=list(csv.reader(io.StringIO(z.read('matrix.tsv').decode()),delimiter='\t'))
cols=rows[0][1:];sums=np.sum(np.array([list(map(int,x[1:])) for x in rows[1:]],dtype=np.int64),axis=0)
culture=[]
for i,row in enumerate(rows[1:],2):
    if row[0] in genes:culture.append({'source_row':i,'gene':row[0],'counts':dict(zip(cols,map(int,row[1:]))),'CPM_reported_counts':{s:float(int(row[j+1])*1e6/sums[j]) for j,s in enumerate(cols)}})
out={'input_hashes':{str(p):sha(p) for p in (source,array,metadata,ffpe,archs4,P/'AMENDMENT-01-array.json')},'mapping':mapping,'array_samples':samples,'array_panel_values':gene_values,'nominated_results':results,'peerj_all12_panel_values':peerj,'peerj_missing':sorted(set(genes)-set(peerj)),'archs4_all_panel_rows':culture,'archs4_column_sums':dict(zip(cols,map(int,sums))),'units':{'array':'Original processed array intensity; multiple unique-gene clusters median with every cluster retained','peerj':'Published filtered log2CPM; missing is not absent expression','ARCHS4':'Rounded estimated counts; CPM is not TPM or original source quantification'},'limits':['Six array specimens are not proven independent of Lund RNA cohort','All source marker rows retained; no gene program or GAG chemistry inferred','One library each for V1-34 and USZ22; no donor replication or stromal localization inference','USZ23 original quantification and broader public evidence pending before claim advancement']}
(P/'validation-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'array_candidates':{g:{'q':r['BH_q_across_five'],'pass':r['passes_allocation'],'contrasts':{h:round(v['A'],3) for h,v in r.get('contrasts',{}).items()}} for g,r in results.items()},'peerj_candidates':{g:peerj.get(g) for g in candidates},'culture_candidates':[r for r in culture if r['gene'] in candidates]}))
