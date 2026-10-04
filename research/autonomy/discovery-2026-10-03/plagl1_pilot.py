"""Worker pilot replay; protocol and missing-control amendment in PLAN.txt."""
import pathlib,sys,json,csv,gzip,zipfile,io,hashlib,collections
sys.path.insert(0,'C:/Projects/EMC-Research/.cache/python-deps')
import numpy as np
B=pathlib.Path('C:/Projects/EMC-Research/research/autonomy');V=B/'atlas-hofvander-validation-2026-09-06';H=B/'atlas-hofvander-source-2026-09-06';A=B/'atlas-primary-provenance-2026-09-06'
genes=['PLAGL1','NR4A3','CHRNA6','PLAG1','PLAGL2'];emc='Extraskeletal myxoid chondrosarcoma';hs=['Low-grade fibromyxoid sarcoma','Myxoid liposarcoma','Synovial sarcoma']
md=json.loads((V/'metadata-manifest.json').read_text());am=json.loads((V/'replication-manifest.json').read_text());rows=[r for r in md['samples'] if r['eligible'] and r['diagnosis'] in [emc]+hs]
assert len([r for r in rows if r['diagnosis']==emc])==9
with gzip.open(H/'tpm_matrix.tsv.gz','rt') as f:
 reader=csv.reader(f,delimiter='\t');head=next(reader)[1:];tv={r[0]:dict(zip(head,map(float,r[1:]))) for r in reader if r[0] in genes}
assert set(tv)==set(genes)
def auc(x,y):
 if not len(x) or not len(y):return None
 return sum((a>b)+.5*(a==b) for a in x for b in y)/(len(x)*len(y))
assert auc([0,1],[0,2])==.375
def ev(rs,vs,h):
 e=[r for r in rs if r['diagnosis']==emc];c=[r for r in rs if r['diagnosis']==h];cells=[]
 for yr in sorted({r['sequencing_year'] for r in e+c}):
  es=[r for r in e if r['sequencing_year']==yr];cs=[r for r in c if r['sequencing_year']==yr]
  if es and cs:cells.append({'year':yr,'ne':len(es),'nc':len(cs),'A':auc([vs[r['sample_id']] for r in es],[vs[r['sample_id']] for r in cs])})
 n=sum(x['ne'] for x in cells)
 return {'n_emc':len(e),'n_comparator':len(c),'A':auc([vs[r['sample_id']] for r in e],[vs[r['sample_id']] for r in c]),'matched_A':sum(x['ne']*x['A'] for x in cells)/n if n else None,'cells':cells}
results={}
for g in genes:
 vs=tv[g];results[g]={h:ev(rows,vs,h) for h in hs}
 if g=='PLAGL1':
  for h in hs:
   dels=[ev([r for r in rows if r['sample_id']!=s['sample_id']],vs,h) for s in rows if s['diagnosis']==emc]
   for k in ['A','matched_A']:results[g][h]['single_emc_deletion_'+k]=[min(x[k] for x in dels),max(x[k] for x in dels)]
  rng=np.random.default_rng(20261003);grp=collections.defaultdict(list)
  for r in rows:grp[r['diagnosis'],r['sequencing_year']].append(r)
  boots={h:{k:[] for k in ['A','matched_A']} for h in hs}
  for _ in range(2000):
   draw=[pool[i] for pool in grp.values() for i in rng.integers(0,len(pool),len(pool))]
   for h in hs:
    z=ev(draw,vs,h)
    for k in boots[h]:boots[h][k].append(z[k])
  for h in hs:results[g][h]['conditional_bootstrap_95']={k:np.quantile(v,[.025,.975]).tolist() for k,v in boots[h].items()}
with zipfile.ZipFile(B/'atlas-original-array-source-2026-09-06/original-source-recovery.zip') as z:
 raw=z.read('GPL6244-original-annotation.tsv');annotation_sha=hashlib.sha256(raw).hexdigest();mapping=[]
 for r in csv.DictReader(io.StringIO(raw.decode()),delimiter='\t'):
  s=set(p.split(' // ')[1].strip() for p in r['gene_assignment'].split(' /// ') if ' // ' in p)
  if s&set(genes):mapping.append({'probe':r['ID'],'symbols':sorted(s),'accepted':len(s)==1,'gene':next(iter(s)) if len(s)==1 else None})
keep={r['probe']:r['gene'] for r in mapping if r['accepted']};av={p:{} for p in keep};sample=None;table=False;columns=None
with gzip.open(A/'GSE24369.soft.gz','rt') as f:
 for line in f:
  line=line.rstrip('\r\n')
  if line.startswith('^SAMPLE = '):sample=line.split(' = ',1)[1]
  elif line=='!sample_table_begin':table=True;columns=None
  elif line=='!sample_table_end':table=False
  elif table:
   r=line.split('\t')
   if columns is None:columns=r;continue
   if r[0] in av:av[r[0]][sample]=float(r[columns.index('VALUE')])
ars=am['array_samples'];ae=[r['sample_id'] for r in ars if r['diagnosis']==emc];array={}
for p,vs in av.items():
 assert len(vs)==len(ars)
 array[p]={'gene':keep[p],'contrasts':{},'EMC_values':{s:vs[s] for s in ae},'normal_muscle_pool_values':{r['sample_id']:vs[r['sample_id']] for r in ars if r['unit']=='pooled_normal_RNA'}}
 for h in hs:
  cs=[r['sample_id'] for r in ars if r['diagnosis']==h]
  if cs:array[p]['contrasts'][h]={'n_emc':len(ae),'n_comparator':len(cs),'A':auc([vs[s] for s in ae],[vs[s] for s in cs]),'single_emc_deletion_A':[min(auc([vs[s] for s in ae if s!=d],[vs[s] for s in cs]) for d in ae),max(auc([vs[s] for s in ae if s!=d],[vs[s] for s in cs]) for d in ae)]}
out={'schema':'plagl1-expression-pilot/1','protocol':'primary PLAGL1; controls NR4A3 CHRNA6 PLAG1 PLAGL2; prespecified RPLP0 absent and omitted; 3 fixed histologies; seed20261003;2000bootstraps','cohort_Hofvander':results,'Hofvander_EMC_values':{r['sample_id']:{'year':r['sequencing_year'],**{g:tv[g][r['sample_id']] for g in genes}} for r in rows if r['diagnosis']==emc},'Hofvander_medians':{g:{h:float(np.median([tv[g][r['sample_id']] for r in rows if r['diagnosis']==h])) for h in [emc]+hs} for g in genes},'array_mapping':mapping,'cohort_GSE24369':array,'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [V/'metadata-manifest.json',V/'replication-manifest.json',H/'tpm_matrix.tsv.gz',A/'GSE24369.soft.gz',B/'atlas-original-array-source-2026-09-06/original-source-recovery.zip']},'annotation_sha256':annotation_sha}
pathlib.Path(__file__).with_name('plagl1-results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'primary':results['PLAGL1'],'array':{k:v for k,v in array.items() if v['gene']=='PLAGL1'}},indent=2))
