import argparse,json,zipfile,hashlib,datetime,re,collections
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import rankdata
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT;SEED=20261001
PAIRS=[('CD68','CD68'),('HLA-DR','CD68'),('CD68','MRC1'),('CD68','NKX2.2'),('NKX2.2','PSMA3')];EPS=[(r,l+'__'+q) for r in [10.,20.,40.] for l,q in PAIRS]
PINS={'41467_2026_70449_MOESM4_ESM.xlsx':(18803408,'6cbdcfce4c6e64c79b09611f97a6bec30205eea3bc130cfc4ebafd79c653f2e0'),'41467_2026_70449_MOESM6_ESM.xlsx':(20023510,'bfe009bbe5e000e661cf93fd846e2f7a1090a8b265d288b35a735cb89c6e3d89')}
def rc(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def sid(s):
 m=re.fullmatch(r'EWS(\d+)(?:a\d*)?',str(s).strip(),re.I);assert m,'Unknown study ID '+str(s);return 'EWS'+str(int(m[1]))
def clinical(roots):
 found={}
 for name,(size,pin) in PINS.items():
  pp=sorted({p for root in roots for p in root.rglob(name)})
  for p in pp:assert p.stat().st_size==size and rc(p)['sha256']==pin
  if pp:found[name]=pp[0]
 container=None
 if len(found)<2:
  p,container=sm.getfull('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13111610/supplementaryFiles','Ewing-exact-case-workbooks.zip',256*1024**2)
  with zipfile.ZipFile(p) as z:
   for name,(size,pin) in PINS.items():
    if name in found:continue
    hits=[v for v in z.namelist() if Path(v).name==name];assert len(hits)==1;raw=z.read(hits[0]);assert len(raw)==size and hashlib.sha256(raw).hexdigest()==pin;dest=OUT/name;dest.write_bytes(raw);found[name]=dest
 c=pd.read_excel(found['41467_2026_70449_MOESM4_ESM.xlsx'],sheet_name='5',header=None,dtype=object);assert c.iloc[3,:5].tolist()==['Study.ID','Consensus cluster','Met at diagnosis (Y/N)','Relapse (Y/N)','3 years evet free survival (Y/N)'];rows=[]
 for row in c.iloc[4:,:5].values.tolist():
  if pd.isna(row[0]):continue
  cluster=int(row[1]);assert cluster in [1,2,3];rows.append({'study_id':sid(row[0]),'literal_Study_ID':str(row[0]),'source_cluster':cluster,'met_at_diagnosis_literal':str(row[2]),'relapse_literal':str(row[3]),'three_year_EFS_literal':str(row[4]),'three_year_EFS_usable_binary':str(row[4]).upper() in ['Y','N']})
 cl=pd.DataFrame(rows);assert len(cl)==28 and cl.study_id.is_unique;a=pd.read_excel(found['41467_2026_70449_MOESM6_ESM.xlsx'],sheet_name='6dg',header=None,dtype=object);measured=[]
 for endpoint,start in [('author_CD68_percent',0),('author_HLAII_percent',25)]:
  for row in a.values.tolist():
   literal=row[start] if len(row)>start else None
   if not isinstance(literal,str) or not re.fullmatch(r'EWS\d+(?:a\d*)?',literal,re.I):continue
   values=[(j,float(row[start+j])) for j in [1,2,3] if len(row)>start+j and pd.notna(row[start+j])];assert len(values)==1;k,v=values[0];key=sid(literal);assert 0<=v<=100 and int(cl.loc[cl.study_id==key,'source_cluster'].iloc[0])==k;measured.append({'study_id':key,'endpoint':endpoint,'value_percent':v,'literal_author_specimen_ID':literal,'source_cluster_column':k})
 m=pd.DataFrame(measured);assert len(m)==50 and not m.duplicated(['study_id','endpoint']).any();wide=m.pivot(index='study_id',columns='endpoint',values='value_percent').reset_index();assert len(wide)==25;return cl.merge(wide,on='study_id',how='left',validate='one_to_one'),{'workbook_receipts':[rc(p) for p in found.values()],'container_receipt':container,'all28_clinical_rows':rows,'all50_author_abundance_rows':measured,'identity_rule':'Case-insensitive exact numeric EWS key and declared a/a1/a2 suffix only; raw strings retained; no invented survival times'}
def endpoints(roots):
 sources={};receipts=[]
 for name in ['spatial-marker-followthrough-cellpose-actual.json','spatial-marker-followthrough-cellwindow-actual.json']:
  for p in sorted({p for root in roots for p in root.rglob(name)}):
   d=json.loads(p.read_text());assert d['schema']=='emc-spatial-marker-followthrough/1';w=0. if 'cellpose' in name else float(re.fullmatch(r'cellwindow-(2\.5|5\.0)um',p.parent.name)[1]);assert float(d.get('cell_window_um',w))==w;dp=p.parent/('spatial-density-cellpose-actual.json' if w==0 else 'spatial-density-cellwindow-actual.json');dd=json.loads(dp.read_text());assert dd['schema']=='emc-spatial-density-sensitivity/1';sig=(rc(p)['sha256'],rc(dp)['sha256'])
   if w in sources:assert sources[w][2]==sig
   else:sources[w]=(d,dd,sig)
   receipts.extend([rc(p),rc(dp)])
 assert set(sources)=={0.,2.5,5.};f5={f['global_panel3_index']:f for f in sources[5.][0]['TIFF']};rows=[];coverage=[];metadata_repairs=[]
 for w,(d,dd,sig) in sorted(sources.items()):
  files=d['TIFF'];assert len(files)==26 and {f['global_panel3_index'] for f in files}==set(range(26));density={r['label']:r for r in dd['records'] if r.get('kind')=='Ewing'};assert len(density)==sum(r.get('kind')=='Ewing' for r in dd['records'])
  for f in files:
   assert len(f['tiles'])==9;i=f['global_panel3_index'];key=sid(Path(f['path']).stem);same={(t['tile_row'],t['tile_column']):t for t in f5[i]['tiles']};vals=collections.defaultdict(list);areas=[];objects=[];ta=[]
   for t in f['tiles']:
    assert 'error' not in t;core=next((a for a in t.get('analyses',[]) if a['threshold_factor']==1),None);n=int(core.get('nuclear_components',0)) if core else 0;other=same[(t['tile_row'],t['tile_column'])];assert t['pixels_masks_sha256']==other['pixels_masks_sha256'];shape=t.get('shape');pixel=t.get('pixel_um')
    if shape is None or pixel is None:shape=shape if shape is not None else other['shape'];pixel=pixel if pixel is not None else other['pixel_um'];metadata_repairs.append({'window_um':w,'label':t['label'],'same_tile5um_label':other['label'],'frozen_raw_pixels_SHA256':t['pixels_masks_sha256'],'shape':shape,'pixel_um':pixel})
    assert len(shape)==2 and float(pixel)>0;areas.append(float(shape[0])*float(shape[1])*float(pixel)**2);objects.append(n);ta.append({'label':t['label'],'nuclear_objects':n,'reference_status':t.get('reference_status'),'analyzable':bool(core and n>=20)})
    if not core or n<20:continue
    dr=density[t['label']];lookup={(float(c['radius_um']),c['left'],c['right']):c for c in dr.get('comparisons',[])}
    for s in core['spatial']:
     for p in s.get('pairs',[]):
      k=(float(s['radius_um']),p['left'],p['right'])
      if (k[1],k[2]) not in PAIRS or p.get('constant_marker'):continue
      q=lookup[k];assert not q.get('constant_marker');assert abs(q['raw']-p['raw_rank_association'])<1e-10 and abs(q['original_unconditional_excess']-p['excess_association'])<1e-10;vals[(k[0],k[1]+'__'+k[2])].append((q['density_conditioned_excess'],q['original_unconditional_excess']))
   assert len(areas)==9;den=sum(objects)/sum(areas)*1e6;coverage.append({'window_um':w,'study_id':key,'path':f['path'],'requested_tiles':9,'tile_audit':ta,'objects_per_mm2_all9_geometric_tiles':den})
   for radius,pair in EPS:
    v=np.asarray(vals.get((radius,pair),[]),float);rows.append({'window_um':w,'study_id':key,'source_file':f['path'],'radius_um':radius,'pair':pair,'density_conditioned_excess':float(v[:,0].mean()) if len(v) else None,'unconditional_excess':float(v[:,1].mean()) if len(v) else None,'n_analyzable_tiles':len(v),'objects_per_mm2':den})
 return pd.DataFrame(rows),coverage,receipts,metadata_repairs
def bh(tests,total,name):
 order=sorted([(i,t['source_case_Freedman_Lane_permutation_p']) for i,t in enumerate(tests) if t.get('source_case_Freedman_Lane_permutation_p') is not None],key=lambda z:z[1]);q=1.
 for k in range(len(order)-1,-1,-1):i,p=order[k];q=min(q,p*total/(k+1));tests[i][name]=q
def basis(x):u,s,v=np.linalg.svd(x,full_matrices=False);r=int(np.sum(s>1e-10));return u[:,:r],r
def fit(y,cov,cl):
 n=len(y);y=rankdata(y)/n;y-=y.mean();x=np.column_stack([np.ones(n)]+[rankdata(cov[:,j])/n-.5 for j in range(cov.shape[1])]);h=np.column_stack([x,cl==2,cl==3]);q0,r0=basis(x);q1,r1=basis(h);s0=max(0.,float(y@y-np.sum((q0.T@y)**2)));s1=max(0.,float(y@y-np.sum((q1.T@y)**2)));sst=float(y@y);dfn=r1-r0;dfd=n-r1
 if dfn<1 or dfd<1 or sst<=1e-12 or s1<=1e-12:return None
 coef=np.linalg.lstsq(h,y,rcond=1e-10)[0];return {'y':y,'q0':q0,'q1':q1,'F':float(max(0.,(s0-s1)/dfn/(s1/dfd))),'dfn':dfn,'dfd':dfd,'delta_R2':float(max(0.,(s0-s1)/sst)),'cluster2_minus1_adjusted_rank':float(coef[-2]),'cluster3_minus1_adjusted_rank':float(coef[-1])}
def test(frame,endpoint,adjust,seed):
 fields=[endpoint,'source_cluster']+(['author_CD68_percent','author_HLAII_percent','objects_per_mm2'] if adjust else []);g=frame.dropna(subset=fields).copy()
 if adjust:g=g[g.objects_per_mm2>0].copy()
 g=g.sort_values('study_id');n=len(g);counts=g.source_cluster.value_counts().to_dict();r={'n_source_study_cases':n,'source_cluster_case_counts':{str(k):int(v) for k,v in counts.items()},'included_study_cases':g.study_id.tolist(),'excluded_study_cases':sorted(set(frame.study_id)-set(g.study_id)),'nuisance_adjustment':adjust,'endpoint':endpoint,'clinical_patient_identity_verified':False}
 if n<12 or set(counts)!={1,2,3} or min(counts.values())<2:return {**r,'status':'insufficient_source_case_coverage'}
 y=g[endpoint].to_numpy(float);cl=g.source_cluster.to_numpy(int);cov=g[['author_CD68_percent','author_HLAII_percent']].to_numpy(float) if adjust else np.empty((n,0))
 if adjust:cov=np.column_stack([cov,np.log(g.objects_per_mm2.to_numpy(float))])
 f=fit(y,cov,cl)
 if f is None:return {**r,'status':'constant_or_degenerate_frozen_model'}
 rng=np.random.default_rng(seed);indices=np.array([rng.permutation(n) for z in range(10000)]);yf=f['q0']@(f['q0'].T@f['y']);res=f['y']-yf;ys=yf[:,None]+res[indices].T;square=np.sum(ys*ys,axis=0);s0=np.maximum(0,square-np.sum((f['q0'].T@ys)**2,axis=0));s1=np.maximum(1e-15,square-np.sum((f['q1'].T@ys)**2,axis=0));null=np.maximum(0,(s0-s1)/f['dfn']/(s1/f['dfd']));p=float((1+np.sum(null>=f['F']-1e-12))/10001);strata=[np.flatnonzero(cl==k) for k in [1,2,3]];boot=[];keys=['delta_R2','cluster2_minus1_adjusted_rank','cluster3_minus1_adjusted_rank']
 for unused in range(2000):
  ind=np.concatenate([rng.choice(z,len(z),replace=True) for z in strata]);b=fit(y[ind],cov[ind],cl[ind])
  if b is not None:boot.append([b[k] for k in keys])
 loo=[]
 for j in range(n):
  ind=np.delete(np.arange(n),j);b=fit(y[ind],cov[ind],cl[ind]);loo.append({'excluded_study_case':g.study_id.iloc[j],**({k:b[k] for k in keys} if b else {'status':'degenerate'})})
 r.update(status='measured',observed_F=f['F'],df_numerator=f['dfn'],df_denominator=f['dfd'],incremental_source_cluster_R2=f['delta_R2'],cluster2_minus1_adjusted_rank=f[keys[1]],cluster3_minus1_adjusted_rank=f[keys[2]],source_case_Freedman_Lane_permutation_p=p,bootstrap_finite_draws=len(boot),bootstrap_discarded_draws=2000-len(boot),leave_one_source_case_out=loo,raw_cluster_mean_excess={str(k):float(y[cl==k].mean()) for k in [1,2,3]},permutation_interpretation='Approximate conditional residual permutation; source-case exchangeability assumption, inherited clusters not independent validation')
 if boot:
  ci=np.quantile(boot,[.025,.975],axis=0);r['stratified_source_case_reranked_bootstrap95']={k:ci[:,j].tolist() for j,k in enumerate(keys)}
 return r
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',action='append');args=ap.parse_args();roots=[Path(s) for s in (args.input_root or ['restored-artifacts','restored-artifacts-extra',str(OUT)])];OUT.mkdir(parents=True,exist_ok=True);cl,cr=clinical(roots);f,cov,sr,repair=endpoints(roots);joined=f.merge(cl,on='study_id',how='left',validate='many_to_one',indicator=True);assert (joined['_merge']=='both').all();joined=joined.drop(columns='_merge');assert joined.study_id.nunique()==26;joined.to_csv(OUT/'Ewing-all-window-source-case-endpoints.tsv',sep='\t',index=False);tests=[];families=[]
 for wi,w in enumerate([0.,2.5,5.]):
  for vi,(ep,adj) in enumerate([('density_conditioned_excess',True),('unconditional_excess',True),('density_conditioned_excess',False)]):
   family=[]
   for ei,(rad,pair) in enumerate(EPS):
    g=joined[(joined.window_um==w)&(joined.radius_um==rad)&(joined.pair==pair)];assert len(g)==26 and g.study_id.is_unique;t=test(g,ep,adj,SEED+22000+wi*1000+vi*100+ei);t.update(window_um=w,radius_um=rad,pair=pair,primary=bool(w==5. and ep=='density_conditioned_excess' and adj));family.append(t)
   bh(family,15,'BH_q_fixed_family15');families.append({'window_um':w,'endpoint':ep,'nuisance_adjustment':adj,'measured_tests':sum(t['status']=='measured' for t in family),'BH_below05':sum(t.get('BH_q_fixed_family15',1)<.05 for t in family),'primary':bool(w==5. and ep=='density_conditioned_excess' and adj)});tests.extend(family)
 bh(tests,135,'BH_q_all135_descriptive');primary=[t for t in tests if t['primary']];assert len(primary)==15;result={'schema':'emc-Ewing-finalized-source-case-geometry/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':{'dated_utc':'2026-10-01','input':'All26Panel3files/234fixedtiles;0/2.5/5um marker windows from same saved rawpixels/nuclei, no new pixels/model inference','primary':'5um follows source QuPath code;2.5um reflects paper5pixel ambiguity. Density-conditioned marker excess,15fixed pair/radius source-cluster omnibus tests, authorCD68/HLAIIpercent+log geometricobjectdensity rank nuisances;10000casepermutations/BH15/2000stratifiedrerankedcasebootstrap/LOO','unit':'Equal analyzabletile means within sourcefile/studycase; no tile/object independence or provenclinicalpatientIDs','geometry':'All9sampledgeometrictileareas including blankmask tiles in object-density denominator;0um missingmetadata repaired only from exactsame frozenrawtile5um counterpart','limits':'No author phenotype classifier, survival/prognosis/treatment claim. HLA-DR alias broadantiHLAII;PSMA3proteasomealpha3 notFOLH1. EWS105missingabundance excluded only adjustedanalyses, neverzeroimputed','multiplicity':'15primary and135total fixed endpoint/window/nuisance comparisons; primary5um predefined, allsecondary families andglobalBH135 retained'},'clinical_source_audit':cr,'finalized_endpoint_receipts':sr,'same_raw_tile_metadata_repairs':repair,'all_window_tile_case_coverage':cov,'clinical_cases_without_frozen_Panel3_file':sorted(set(cl.study_id)-set(joined.study_id)),'all_source_case_endpoint_values':joined.to_dict(orient='records'),'primary15_source_case_tests':primary,'all135_primary_sensitivity_tests':tests,'all9_fixed_families':families,'endpoint_table':str(OUT/'Ewing-all-window-source-case-endpoints.tsv')};dest=OUT/'Ewing-finalized-source-case-geometry-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_EWING_FINALIZED_CASE_GEOMETRY_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_EWING_FINALIZED_CASE_GEOMETRY_END')
if __name__=='__main__':main()
