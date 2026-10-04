"""DLK1 prospective one-gene pilot; no selection/replacement of genes."""
from pathlib import Path
import json,csv,gzip,io,zipfile,hashlib,collections
import numpy as np
import openpyxl
from scipy.stats import spearmanr
D=Path(__file__).resolve().parent;R=Path('C:/Projects/EMC-Research/research/autonomy')
plan=json.loads((D/'PLAN.json').read_text());genes=['DLK1']+plan['composition_context_genes']
meta=R/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json';samples=json.loads(meta.read_text())['samples'];byid={s['sample_id']:s for s in samples}
source=R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz';vals={};hits=collections.Counter()
with gzip.open(source,'rt') as f:
    hdr=next(f).rstrip().split('\t')[1:]
    for line in f:
        x=line.rstrip().split('\t')
        if x[0] in genes:hits[x[0]]+=1;vals[x[0]]=dict(zip(hdr,map(float,x[1:])))
assert all(hits[g]==1 for g in genes),hits
v=vals['DLK1'];prim=plan['primary']['sample_ids'];rng=np.random.default_rng(41026)
def summary(ids):
    a=np.array([v[s]for s in ids]);return {'ids':ids,'n':len(a),'median':float(np.median(a)),'range':[float(a.min()),float(a.max())],'n_ge10':int(sum(a>=10)),'values':dict(zip(ids,map(float,a)))}
def A(a,b):return float(np.mean((a[:,None]>b[None,:])+.5*(a[:,None]==b[None,:])))
def contrast(ids):
    a=np.array([v[s] for s in prim]);b=np.array([v[s]for s in ids]);bs=[A(rng.choice(a,len(a),replace=True),rng.choice(b,len(b),replace=True))for _ in range(2000)]
    common=sorted({byid[s]['sequencing_year']for s in prim}&{byid[s]['sequencing_year']for s in ids});yy={}
    for y in common:
        aa=np.array([v[s]for s in prim if byid[s]['sequencing_year']==y]);bb=np.array([v[s]for s in ids if byid[s]['sequencing_year']==y]);yy[y]={'n_emc':len(aa),'n_control':len(bb),'A':A(aa,bb)}
    return {'n_control':len(b),'EMC_median':float(np.median(a)),'control_median':float(np.median(b)),'A':A(a,b),'A_bootstrap95_percentile':list(map(float,np.percentile(bs,[2.5,97.5]))),'leave_one_EMC_out_A_range':[min(A(np.delete(a,i),b)for i in range(len(a))),max(A(np.delete(a,i),b)for i in range(len(a)))],'by_year':yy,'same_year_EMC_weighted_A':sum(x['n_emc']*x['A']for x in yy.values())/sum(x['n_emc']for x in yy.values()) if yy else None}
primary=summary(prim);primary['median_bootstrap95_percentile']=list(map(float,np.percentile([np.median(rng.choice([v[s]for s in prim],len(prim),replace=True))for _ in range(2000)],[2.5,97.5])));primary['passes_operational_abundance_gate']=primary['n_ge10']>=8 and primary['median']>=10
contrasts={h:contrast(ids)for h,ids in plan['comparisons']['same_study_primary_ids_by_histology'].items()}
composition={g:{'spearman_rho':float(spearmanr([v[s]for s in prim],[vals[g][s]for s in prim]).statistic),'n':len(prim),'interpretation':'Exploratory bulk-composition association; neither adjustment nor cell localization.'}for g in genes if g!='DLK1'}
ann=R/'atlas-original-array-source-2026-09-06/original-source-recovery.zip';mapping=[]
with zipfile.ZipFile(ann)as z:
    with z.open('GPL6244-original-annotation.tsv')as ff:
        for row in csv.DictReader(io.TextIOWrapper(ff),delimiter='\t'):
            parts=[x.split(' // ')for x in row['gene_assignment'].split(' /// ')];sy={x[1].strip()for x in parts if len(x)>=2};ids={x[4].strip()for x in parts if len(x)>=5}
            if 'DLK1' in sy or '8788'in ids:mapping.append({'probe':row['ID'],'symbols':sorted(sy),'entrez':sorted(ids),'accepted':sy=={'DLK1'}and ids=={'8788'},'annotation':row['gene_assignment']})
av={r['probe']:{}for r in mapping if r['accepted']};arr=R/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz'
with gzip.open(arr,'rt')as f:
    inside=False;sid=None
    for line in f:
        line=line.rstrip('\r\n')
        if line.startswith('^SAMPLE = '):sid=line.split(' = ',1)[1]
        elif line=='!sample_table_begin':inside=True;header=None
        elif line=='!sample_table_end':inside=False
        elif inside:
            x=line.split('\t')
            if header is None:header=x;continue
            if x[0]in av:av[x[0]][sid]=float(x[header.index('VALUE')])
am=plan['array_metadata'];groups=collections.defaultdict(list)
for s in am:groups[s['diagnosis']].append(s['sample_id'])
geneav={s['sample_id']:float(np.median([av[p][s['sample_id']]for p in av]))for s in am}if av else{}
array_contrasts={}
if av:
    ea=np.array([geneav[s]for s in groups['Extraskeletal myxoid chondrosarcoma']])
    for h,ss in groups.items():
        if h=='Extraskeletal myxoid chondrosarcoma':continue
        bb=np.array([geneav[s]for s in ss]);array_contrasts[h]={'n_emc':len(ea),'n_control':len(bb),'EMC_median':float(np.median(ea)),'control_median':float(np.median(bb)),'A':A(ea,bb)}
peer=R/'tmem266-tissue-2026-10-03/peerj-source-s009.xlsx';w=openpyxl.load_workbook(peer,read_only=True,data_only=True);rows=iter(w.active.values);ph=list(next(rows))[1:];pv=[]
for row in rows:
    if row[0]=='DLK1':pv.append(dict(zip(ph,row[1:])))
w.close()
culture=R/'tmem266-all-cultures-2026-10-04/archs4-subset.zip'
with zipfile.ZipFile(culture)as z:rr=list(csv.reader(io.StringIO(z.read('matrix.tsv').decode()),delimiter='\t'))
ch=rr[0][1:];sums=np.sum(np.array([list(map(int,x[1:]))for x in rr[1:]],dtype=np.int64),axis=0);cv=[]
for i,row in enumerate(rr[1:],2):
    if row[0]=='DLK1':cv.append({'row':i,'counts':dict(zip(ch,map(int,row[1:]))),'CPM_rounded_estimates':{s:float(int(row[j+1])*1e6/sums[j])for j,s in enumerate(ch)}})
out={'plan_sha256':hashlib.sha256((D/'PLAN.json').read_bytes()).hexdigest(),'input_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [meta,source,ann,arr,peer,culture]},'tissue':{'all_requested_genes_values':vals,'primary':primary,'all13':summary(plan['sensitivities']['all13_ids']),'historical9':summary(plan['sensitivities']['historical_no_known_discovery_overlap_ids']),'contrasts':contrasts,'composition_context':composition},'array':{'mapping':mapping,'all_probe_values':av,'gene_values':geneav,'contrasts':array_contrasts},'PeerJ12':{'sample_ids':ph,'DLK1_rows':pv,'missing_interpretation':'If empty: absent from filtered published matrix, not zero expression.'},'cultures':{'column_sums':dict(zip(ch,map(int,sums))),'DLK1_rows':cv,'units':'ARCHS4 rounded estimated-count CPM; not TPM; one library/model'}}
(D/'retained-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'primary':primary,'contrasts':contrasts,'array_contrasts':array_contrasts,'peerj':pv,'cultures':cv},indent=2))
