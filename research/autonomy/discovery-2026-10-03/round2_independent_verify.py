"""Independent reviewer replay supplied by emc_clinical; rank-sum A, no analysis helper imports."""
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,'.cache/python-deps')
import csv,gzip,json,io,zipfile,pathlib
import numpy as np
from scipy.stats import rankdata,mannwhitneyu
P=pathlib.Path('research/autonomy/discovery-2026-10-03');R=pathlib.Path('research/autonomy');E='Extraskeletal myxoid chondrosarcoma'
H=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
def A(a,b):
 return float((rankdata(np.r_[a,b])[:len(a)].sum()-len(a)*(len(a)+1)/2)/(len(a)*len(b)))
D=list(csv.DictReader((P/'round2-surface-discovery.tsv').open(),delimiter='\t'));targets={r['gene'] for r in D}
M=json.loads((R/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())['samples'];G={h:[r for r in M if r['eligible'] and r['diagnosis']==h] for h in {r['diagnosis'] for r in M}};V={}
with gzip.open(R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt',encoding='utf-8-sig') as f:
 rr=csv.reader(f,delimiter='\t');hd=next(rr)[1:]
 for row in rr:
  if row[0] in targets:V[row[0]]=dict(zip(hd,map(float,row[1:])))
errors=[];pp=[]
for r in D:
 v=V[r['gene']];a=[v[x['sample_id']] for x in G[E]];ps=[]
 for h in H:
  b=[v[x['sample_id']] for x in G[h]];method='exact' if len(set(a+b))==len(a)+len(b) else 'asymptotic';p=mannwhitneyu(a,b,alternative='greater',method=method).pvalue;ps.append(p)
  cc=[]
  for x in G[E]:
   yy=[v[y['sample_id']] for y in G[h] if y['sequencing_year']==x['sequencing_year']]
   if yy:cc.append(A([v[x['sample_id']]],yy))
  for key,z in [(h+'_A',A(a,b)),(h+'_matched_A',np.mean(cc)),(h+'_p',p),(h+'_median_log2_contrast',np.median(np.log2(1+np.array(a)))-np.median(np.log2(1+np.array(b))))]:
   if abs(float(r[key])-z)>1e-10:errors.append([r['gene'],key,r[key],z])
 pp.append(max(ps))
order=np.argsort(pp);q=np.empty(len(pp));last=1.
for k in range(len(pp)-1,-1,-1):
 i=order[k];last=min(last,pp[i]*len(pp)/(k+1));q[i]=last
for r,x in zip(D,q):
 if abs(float(r['BH_q'])-x)>1e-10:errors.append([r['gene'],'BH_q'])
print('DISCOVERY_ROWS',len(D),'ERRORS',errors)
rep=json.loads((P/'round2-surface-replication.json').read_text());names=list(rep['genes']);alias={g:g for g in names}
for r in csv.DictReader((P/'round2-array-alias-source.tsv').open(),delimiter='\t'):
 for x in r['Gene Names'].split():alias[x]=r['Gene Names'].split()[0]
MP={}
with zipfile.ZipFile(R/'atlas-original-array-source-2026-09-06/original-source-recovery.zip') as z:
 for r in csv.DictReader(io.StringIO(z.read('GPL6244-original-annotation.tsv').decode()),delimiter='\t'):
  symbols={s.split(' // ')[1].strip() for s in r['gene_assignment'].split(' /// ') if ' // ' in s};canon={alias.get(x,x) for x in symbols}
  if len(canon)==1 and next(iter(canon)) in names:MP[r['ID']]=next(iter(canon))
AV={p:{} for p in MP};rows=rep['array_samples'];table=False;s=None;head=None
with gzip.open(R/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz','rt') as f:
 for line in f:
  line=line.rstrip('\n\r')
  if line.startswith('^SAMPLE = '):s=line.split(' = ')[1]
  elif line=='!sample_table_begin':table=True;head=None
  elif line=='!sample_table_end':table=False
  elif table:
   row=line.split('\t')
   if head is None:head=row;continue
   if row[0] in AV:AV[row[0]][s]=float(row[head.index('VALUE')])
for gene,result in rep['genes'].items():
 ps=[p for p,g in MP.items() if g==gene]
 if sorted(ps)!=sorted(result.get('probe_ids',[])):errors.append([gene,'probe_map'])
 if not ps:continue
 vv={r['sample_id']:float(np.median([AV[p][r['sample_id']] for p in ps])) for r in rows}
 for s,x in vv.items():
  if abs(x-result['values'][s])>1e-10:errors.append([gene,s,'array_value'])
 for h,z in result['contrasts'].items():
  a=[vv[r['sample_id']] for r in rows if r['diagnosis']==E];b=[vv[r['sample_id']] for r in rows if r['diagnosis']==h]
  if abs(A(a,b)-z['A'])>1e-10:errors.append([gene,h,'array_A'])
print('ARRAY_GENES',len(names),'UNIQUE_PROBES',len(MP),'TOTAL_ERRORS',errors)
context=list(csv.DictReader((P/'round2-surface-context.tsv').open(),delimiter='\t'))
for gene in ['GPR68','ABHD2','TMEM266']:
 v=V[gene];a=[v[r['sample_id']] for r in G[E] if r['sample_id']!='5241-06'];orig=[v[r['sample_id']] for r in G[E]]
 cs={h:A(orig,[v[r['sample_id']] for r in rr]) for h,rr in G.items() if len(rr)>=5 and h!=E}
 for r in context:
  if r['gene']==gene and abs(float(r['A'])-cs[r['histology']])>1e-10:errors.append([gene,r['histology'],'context_A'])
 print(gene,json.dumps({'median_without5241':float(np.median(a)),'A_without5241':{h:A(a,[v[r['sample_id']] for r in G[h]]) for h in H},'RNA_min_A_allcase_LOO':{h:min(A(orig[:i]+orig[i+1:],[v[r['sample_id']] for r in G[h]]) for i in range(9)) for h in H},'fullcontext_minA':min(cs.values()),'fullcontext_nA1':sum(x==1 for x in cs.values()),'fullcontext_n':len(cs),'array':{h:{'A':z['A'],'median_difference':z['median_difference'],'LOO':z['single_EMC_deletion_A']} for h,z in rep['genes'][gene]['contrasts'].items()},'array_probes':rep['genes'][gene]['probe_ids']}))
assert not errors,errors
print('PASS: no discrepancies; numerical replay is not a scientific novelty or independence certificate.')
