"""Read-only independent numerical/source audit of lead's frozen matrix pilot."""
from pathlib import Path
import json,csv,gzip,zipfile,io,hashlib,collections,datetime
import numpy as np
from scipy.stats import mannwhitneyu
import openpyxl
P=Path(__file__).resolve().parent
L=P.parents[2]/'fresh-discovery-2026-10-04-round2'/'matrix'
L=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-lead/research/autonomy/fresh-discovery-2026-10-04-round2/matrix')
R=Path('C:/Projects/EMC-Research/research/autonomy')
plan=json.loads((L/'PLAN.json').read_text()); t=json.loads((L/'tissue-results.json').read_text()); v=json.loads((L/'validation-results.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
checks=[]
def ck(label,condition):
 checks.append({'check':label,'pass':bool(condition)})
 if not condition:raise AssertionError(label)
def near(a,b):return np.isclose(a,b,atol=1e-11,rtol=1e-10)
def contrast(a,b):
 a=np.asarray(a);b=np.asarray(b);u=sum(float(x>y)+.5*float(x==y)for x in a for y in b)
 method='exact'if len(set(np.r_[a,b]))==len(a)+len(b)else'asymptotic'
 return u/(len(a)*len(b)),mannwhitneyu(a,b,method=method,alternative='two-sided').pvalue
def bh(ps):
 keys=sorted(ps,key=ps.get);last=1.;out={}
 for i in reversed(range(len(keys))):last=min(last,ps[keys[i]]*len(keys)/(i+1));out[keys[i]]=last
 return out
hashes={}
for output in (t,v):
 for file,expected in output['input_hashes'].items():
  got=sha(Path(file));hashes[file]=got;ck('input hash '+file,got==expected)
ck('plan hash',sha(L/'PLAN.json')==t['plan_sha256'])
with gzip.open(R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt',encoding='utf-8-sig')as f:
 rr=csv.reader(f,delimiter='\t');header=next(rr)[1:];mat={r[0]:dict(zip(header,map(float,r[1:])))for r in rr if r[0]in plan['all_extracted_genes']}
ck('all retained RNA panel values equal original',mat==t['all_panel_values'])
meta=json.loads((R/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())['samples'];emc=[s for s in meta if s['diagnosis']=='Extraskeletal myxoid chondrosarcoma'];pri=[s for s in emc if s['eligible']]
ck('all13 metadata and source columns',emc==t['all_EMC_metadata']and len(emc)==13 and all(s['sample_id']in header for s in emc))
ck('primary9 all12 and local recurrence',len(pri)==9 and sum(s['primary_lesion']for s in emc)==12 and [s['sample_id']for s in emc if not s['primary_lesion']]==['5081-14'])
ps={};ncontrasts=0
for gene in plan['enzyme_universe']:
 gr=t['genes'][gene]
 if gene not in mat:ps[gene]=1;continue
 vals=mat[gene]
 for name,ss in [('primary',pri),('all12primary',[s for s in emc if s['primary_lesion']]),('all13',emc)]:
  a=[vals[s['sample_id']]for s in ss];p=[]
  for hist in plan['primary_comparators']:
   other=[s for s in meta if s['diagnosis']==hist and s['primary_lesion']];b=[vals[s['sample_id']]for s in other];ar,pv=contrast(a,b);published=gr[name][hist]
   ck(gene+' '+name+' '+hist,near(ar,published['A'])and near(pv,published['two_sided_p'])and near(np.median(np.log2(1+np.array(a)))-np.median(np.log2(1+np.array(b))),published['log2_median_difference']));p.append(pv);ncontrasts+=1
  if name=='primary':ps[gene]=max(p)
qs=bh(ps);ck('BH all44',all(near(q,t['genes'][g]['BH_q'])for g,q in qs.items())and len(qs)==44)
# Independently authenticate probe symbols with Entrez IDs and read original GEO titles.
entrez={e['symbol']:e['entrez']for rows in plan['pathways'].values()for e in rows};mapped={};annotations={}
with zipfile.ZipFile(R/'atlas-original-array-source-2026-09-06/original-source-recovery.zip')as z:
 for row in csv.DictReader(io.StringIO(z.read('GPL6244-original-annotation.tsv').decode()),delimiter='\t'):
  aa=[a.split(' // ')for a in row['gene_assignment'].split(' /// ')];symbols={a[1].strip()for a in aa if len(a)>=2};ids={a[4].strip()for a in aa if len(a)>=5}
  if len(symbols)==1:
   gene=next(iter(symbols))
   if gene in plan['all_extracted_genes']and(gene not in entrez or ids=={entrez[gene]}):mapped[row['ID']]=gene;annotations[row['ID']]={'symbols':sorted(symbols),'entrez_ids':sorted(ids)}
ck('all accepted probe identities',mapped=={x['probe']:x['gene']for x in v['mapping']if x['accepted']})
array=collections.defaultdict(dict);titles={};chars=collections.defaultdict(list)
with gzip.open(R/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz','rt')as f:
 sample=None;inside=False
 for ln in f:
  ln=ln.rstrip('\r\n')
  if ln.startswith('^SAMPLE = '):sample=ln.split(' = ',1)[1]
  elif ln.startswith('!Sample_title = '):titles[sample]=ln.split(' = ',1)[1]
  elif ln.startswith('!Sample_characteristics_ch1 = '):chars[sample].append(ln.split(' = ',1)[1])
  elif ln=='!sample_table_begin':inside=True;cols=None
  elif ln=='!sample_table_end':inside=False
  elif inside:
   row=ln.split('\t')
   if cols is None:cols=row
   elif row[0]in mapped:array[row[0]][sample]=float(row[cols.index('VALUE')])
emcids=[s for s,title in titles.items()if title.startswith('Extraskeletal myxoid chondrosarcoma')]
ck('six GEO EMC original titles',len(emcids)==6 and set(emcids)=={s['sample_id']for s in v['array_samples']if s['diagnosis']=='Extraskeletal myxoid chondrosarcoma'})
for gene,gr in v['array_panel_values'].items():
 probes=[p for p,g in mapped.items()if g==gene];ck('array panel original values '+gene,set(probes)==set(gr['probes'])and all(near(np.median([array[p][s]for p in probes]),value)for s,value in gr['values'].items()))
aps={};output={}
for gene in t['allocated_genes']:
 gr=v['array_panel_values'][gene];values=gr['values'];a=[values[s]for s in emcids];p=[];out={}
 for hist in ['Low-grade fibromyxoid sarcoma','Myxofibrosarcoma','Skeletal muscle pools']:
  ids=[s['sample_id']for s in v['array_samples']if s['diagnosis']==hist];ar,pv=contrast(a,[values[s]for s in ids]);pr=v['nominated_results'][gene]['contrasts'][hist];ck('array contrast '+gene+' '+hist,near(ar,pr['A'])and near(pv,pr['two_sided_p']));out[hist]={'n':len(ids),'A':ar,'p':pv}
  if hist!='Skeletal muscle pools':p.append(pv)
 aps[gene]=max(p);output[gene]={'probes':{probe:annotations[probe]for probe in gr['probes']},'contrasts':out}
aq=bh(aps)
for gene,q in aq.items():ck('array BH '+gene,near(q,v['nominated_results'][gene]['BH_q_across_five']));output[gene]['q']=q
ck('none passes array frozen gate',not any(row['passes_allocation']for row in v['nominated_results'].values()))
wb=openpyxl.load_workbook(R/'tmem266-tissue-2026-10-03/peerj-source-s009.xlsx',read_only=True,data_only=True);it=iter(wb.active.values);ids=next(it)[1:];peerj={row[0]:dict(zip(ids,map(float,row[1:])))for row in it if row[0]in plan['all_extracted_genes']};wb.close();ck('all12 published processed values',peerj==v['peerj_all12_panel_values']and len(ids)==12)
with zipfile.ZipFile(R/'tmem266-all-cultures-2026-10-04/archs4-subset.zip')as z:rows=list(csv.reader(io.StringIO(z.read('matrix.tsv').decode()),delimiter='\t'))
cols=rows[0][1:];sums=[sum(int(row[j+1])for row in rows[1:])for j in range(len(cols))];ck('culture column denominators',dict(zip(cols,sums))==v['archs4_column_sums'])
expected=[(i,row)for i,row in enumerate(rows[1:],2)if row[0]in plan['all_extracted_genes']]
ck('all culture panel rows retained including duplicates',len(expected)==len(v['archs4_all_panel_rows']))
for (i,row),released in zip(expected,v['archs4_all_panel_rows']):ck('culture row '+str(i),i==released['source_row']and row[0]==released['gene']and dict(zip(cols,map(int,row[1:])))==released['counts']and all(near(int(row[j+1])*1e6/sums[j],released['CPM_reported_counts'][s])for j,s in enumerate(cols)))
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent source extraction/numerical audit; not independent donor authentication or biological validation','reviewed_files':{str(L/n):sha(L/n)for n in ['PLAN.json','AMENDMENT-01-array.json','analyze_matrix.py','validate_matrix.py','tissue-results.json','validation-results.json']},'source_hashes':hashes,'checks':checks,'RNA_contrasts_checked':ncontrasts,'original_GEO_EMC':{s:{'title':titles[s],'characteristics':chars[s]}for s in emcids},'candidate_array_results':output,'decision':'Shelve standalone contribution','scientific_value':'Correct frozen pilot yields candidate bulk transcription differences but none validates its frozen array gate. Known myxoid GAG composition is not a new finding. Bulk RNA, low culture counts and composition correlations do not establish tumor-cell enzyme activity, glycan production, or drug vulnerability. The small historical comparisons cannot establish general absence or refute disease biology.','remaining_gaps':['RNA metadata trusted as prior verified mapping; independent raw clinical donor linkage still unavailable','Six original arrays may overlap RNA specimens; RMA intensities are not absolute expression; two muscle pools are not two matched patients','HS3ST5 lower than normal muscle pools does not refute myxoid-tumor specificity but limits a general tumor-specific interpretation','All12 PeerJ released filtered values do not substitute for suitable missing raw gene counts','Other suitable public EMC evidence incl USZ23 and older GSE6481 must remain pending if a claim reopens; no complete coverage claim']}
(P/'matrix-independent-challenge.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':len(checks),'all_pass':all(c['pass']for c in checks),'RNA_contrasts':ncontrasts,'array_q':aq,'decision':result['decision']}))
