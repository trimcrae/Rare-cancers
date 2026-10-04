"""Independent worker implementation: original cohort, order statistics, kernels."""
import csv,gzip,json,hashlib,bisect,statistics,math,collections,itertools,urllib.request,xml.etree.ElementTree as E
from pathlib import Path
import numpy as np
import openpyxl
R=Path(r'C:\Projects\EMC-Research');B=R/'research/autonomy/discovery-2026-10-03';S=R/'research/autonomy/atlas-hofvander-source-2026-09-06'
o=json.loads((B/'antigen-results.json').read_text());reported={x['sample_id']:x for x in o['samples']}
H=['Extraskeletal myxoid chondrosarcoma','Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma'];EMC=H[0]
P=['HLA-A','HLA-B','HLA-C','B2M','TAP1','TAP2','TAPBP','NLRC5','PSMB8','PSMB9'];I=['PTPRC','CD3D','CD3E','CD8A','CD8B','LST1','FCER1G','AIF1'];G=P+I+['CHRNA6']
meta={x['lab_no']:x for x in csv.DictReader((S/'meta_data.txt').open(),delimiter='\t')};rows={};excluded={}
w=openpyxl.load_workbook(S/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx',read_only=True,data_only=True)
for n,x in enumerate(w.active.iter_rows(values_only=True),1):
 if len(x)<2 or x[1] not in H:continue
 s=x[0].split('_')[0];h=x[1]
 if x[12] is not None or (h==EMC and x[21] is not None):excluded[s]=[h,x[12],x[21]];continue
 rows[s]={'diagnosis':h,'year':meta[s]['sequencing_year'],'s1_row':n}
assert set(rows)==set(reported)
assert all(r['diagnosis']==reported[s]['diagnosis'] and r['year']==reported[s]['sequencing_year'] and r['s1_row']==reported[s]['s1_row'] for s,r in rows.items())
V={}
with gzip.open(S/'tpm_matrix.tsv.gz','rt',encoding='utf-8-sig') as f:
 rd=csv.reader(f,delimiter='\t');head=next(rd);ix={s:head.index(s) for s in rows}
 for x in rd:
  if x[0] in G:V[x[0]]={s:float(x[k]) for s,k in ix.items()}
assert V==o['selected_values']
def a(es,cs,g):
 if not es or not cs:return None
 comp=sorted(V[g][s] for s in cs)
 return sum((bisect.bisect_left(comp,V[g][s])+bisect.bisect_right(comp,V[g][s]))/2 for s in es)/(len(es)*len(cs))
def calc(rr,h,g,matched):
 es=[s for s in rr if rows[s]['diagnosis']==EMC];cs=[s for s in rr if rows[s]['diagnosis']==h]
 if not matched:return a(es,cs,g)
 use=[s for s in es if any(rows[c]['year']==rows[s]['year'] for c in cs)]
 return sum(a([s],[c for c in cs if rows[c]['year']==rows[s]['year']],g) for s in use)/len(use) if use else None
errors=[];summary={}
for h in H[1:]:
 summary[h]={}
 for kind in ['marginal','matched']:
  z={g:calc(rows,h,g,kind=='matched') for g in G}
  errors.extend(abs(v-o['estimates'][h]['genes'][g][kind]) for g,v in z.items())
  summary[h][kind]=statistics.mean(z[g] for g in P)
  for label,gs in [('program',P),('immune_controls',I)]:assert math.isclose(statistics.mean(z[g] for g in gs),o['estimates'][h][label][kind],abs_tol=1e-14)
for typ,entries in o['deletions'].items():
 for key,res in entries.items():
  rr=[s for s in rows if (s!=key if typ=='patient' else rows[s]['year']!=key)]
  for h,z in res.items():
   for kind in ['marginal','matched']:
    for label,gs in [('program',P),('immune_controls',I)]:
     vec=[calc(rr,h,g,kind=='matched') for g in gs];v=statistics.mean(vec) if all(x is not None for x in vec) else None
     if v is None:assert z[label][kind] is None
     else:errors.append(abs(v-z[label][kind]))
assert max(errors)<1e-12
print(json.dumps({'arithmetic_checks':len(errors),'max_error':max(errors),'primary':summary,'EMC_IDs':[s for s in rows if rows[s]['diagnosis']==EMC],'excluded_EMC':{s:r for s,r in excluded.items() if r[0]==EMC}}))
# Independent bootstrap using precomputed per-pair 10-gene ordering kernels.
groups={h:[x for x in o['samples'] if x['diagnosis']==h] for h in H};ids={h:[x['sample_id'] for x in rr] for h,rr in groups.items()};yr={h:np.array([x['sequencing_year'] for x in rr]) for h,rr in groups.items()}
K={}
for h in H[1:]:
 K[h]=np.zeros((len(ids[EMC]),len(ids[h])))
 for g in P:
  e=np.array([V[g][s] for s in ids[EMC]])[:,None];c=np.array([V[g][s] for s in ids[h]])[None,:];K[h]+=(e>c)+.5*(e==c)
 K[h]/=len(P)
strata={h:[np.flatnonzero(yr[h]==y) for y in sorted(set(yr[h]))] for h in H};rng=np.random.default_rng(20261003);draws={h:{'marginal':[],'matched':[]} for h in H[1:]}
for _ in range(2000):
 index={h:np.concatenate([s[rng.integers(len(s),size=len(s))] for s in ss]) for h,ss in strata.items()}
 for h,k in K.items():
  e,c=index[EMC],index[h];draws[h]['marginal'].append(k[np.ix_(e,c)].mean());vec=[]
  for ei in e:
   cy=c[yr[h][c]==yr[EMC][ei]]
   if len(cy):vec.append(k[ei,cy].mean())
  draws[h]['matched'].append(np.mean(vec))
ci={h:{kind:np.quantile(x,[.025,.975]).tolist() for kind,x in d.items()} for h,d in draws.items()}
ce=max(abs(ci[h][k][j]-o['conditional_bootstrap_95'][h][k][j]) for h in H[1:] for k in ['marginal','matched'] for j in [0,1]);assert ce<1e-12
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==s for p,s in o['source_hashes'].items())
assert hashlib.sha256((B/'antigen_pilot.py').read_bytes()).hexdigest()==o['analysis_sha256']
print(json.dumps({'bootstrap_replicates':2000,'max_CI_error':ce,'CI':ci,'source_and_code_hashes':'match'}))
# CT exact sign enumeration, independent of producer binomial-tail formula.
b=urllib.request.urlopen('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4110079/fullTextXML',timeout=25).read();r=E.fromstring(b);ct=json.loads((B/'ct-results.json').read_text())
t=next(t for t in r.iter('table-wrap') if 'Hounsfield units' in ''.join(t.itertext()))
printed=[[(''.join(c.itertext()).strip() or None) for c in tr.findall('td')] for tr in t.findall('./table/tbody/tr')];assert printed==ct['printed_rows'];d=[]
for row in printed:
 vals=[float(x) for i,x in enumerate(row) if x is not None and i in (3,4,5,7,8)]
 if vals and row[6] is not None:d.append((row[0],statistics.median(vals)-float(row[6])))
k=sum(v>0 for _,v in d);n=len(d);p=sum(sum(bits)<=min(k,n-k) or sum(bits)>=max(k,n-k) for bits in itertools.product([0,1],repeat=n))/2**n
assert hashlib.sha256(b).hexdigest()==ct['raw_xml_sha256'];assert p==ct['sign_test_two_sided_p'];assert statistics.median(v for _,v in d)==ct['median_delta_HU'];assert d==[(x['case'],x['delta_HU']) for x in ct['pairs']]
print(json.dumps({'CT_source_hash':hashlib.sha256(b).hexdigest(),'CT_printed_cells':sum(map(len,printed)),'CT_pair_deltas':d,'median':statistics.median(v for _,v in d),'exact_sign_p':p,'status':'PASS'}))
