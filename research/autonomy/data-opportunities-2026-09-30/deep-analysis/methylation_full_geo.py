#!/usr/bin/env python3
import csv,gzip,hashlib,io,json,pathlib,re,time,urllib.request
import numpy as np
import pandas as pd
from sklearn.feature_selection import f_classif
import methylation_transfer as mt
OUT=pathlib.Path(__file__).resolve().parent/'outputs'/'methylation-full-geo';OUT.mkdir(parents=True,exist_ok=True)
CACHE=OUT/'download-cache';CACHE.mkdir(exist_ok=True)
mt.OUT=OUT;mt.CACHE=CACHE
BASE='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140686/'
SIZES={'GPL13534':1707312389,'GPL21145':3581283845}
START=time.time();MAX_ROWS=500000
class Counter:
 def __init__(self,r):self.r=r;self.n=0;self.h=hashlib.sha256()
 def read(self,n=-1):
  b=self.r.read(n);self.n+=len(b);self.h.update(b)
  if self.n>4_000_000_000:raise ValueError('source exceeds declared 4 GB bound')
  return b
 def seekable(self):return False
def get(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-measured-methylation-analysis/1'}),timeout=120)
def label_map(md):return dict(md[['ID','IDAT']].itertuples(index=False,name=None))
def canonical_reference(s):
 m=re.search(r'REFERENCE[ _\.]SAMPLE[ _\.]*(\d+)',s,re.I)
 return 'REFERENCE_SAMPLE '+str(int(m.group(1))) if m else None
def series(platform,idmap):
 url=BASE+'matrix/GSE140686-'+platform+'_series_matrix.txt.gz'
 with get(url) as r:b=r.read(2_000_001)
 if len(b)>2_000_000:raise ValueError('series metadata exceeds bound')
 text=gzip.decompress(b).decode();fields={}
 for line in text.splitlines():
  if line.startswith('!Sample_'):
   v=next(csv.reader([line],delimiter='\t'));fields.setdefault(v[0],[]).append(v[1:])
 gsms=fields['!Sample_geo_accession'][0];mapping={};records=[]
 for k,gsm in enumerate(gsms):
  vals=[v[k] for rows in fields.values() for v in rows if len(v)==len(gsms)]
  refs=set(canonical_reference(v) for v in vals);refs.discard(None)
  ids=set(idmap[z] for z in refs if z in idmap)
  if len(ids)>1:raise ValueError('GEO sample has conflicting reference identities')
  if ids:mapping[gsm]=next(iter(ids))
  records.append({'gsm':gsm,'title':fields.get('!Sample_title',[['']*len(gsms)])[0][k],'reference_ids':sorted(refs),'mapped_IDAT':next(iter(ids)) if ids else None})
 processing=sorted(set(v for row in fields.get('!Sample_data_processing',[]) for v in row))
 return mapping,{'url':url,'compressed_sha256':mt.digest(b),'compressed_bytes':len(b),'sample_mapping':records,'author_data_processing':processing}
def main():
 raw=mt.bounded_get(mt.MD,400000)
 if mt.digest(raw)!=mt.MD_SHA:raise ValueError('metadata digest mismatch')
 md=pd.read_csv(io.BytesIO(raw)).fillna('')
 for c in ['ID','IDAT','Supplier','DNA','Meth_Class']:md[c]=md[c].astype(str)
 if len(md)!=1077 or md.ID.duplicated().any() or md.IDAT.duplicated().any():raise ValueError('reference identity failure')
 if md.Meth_Class.nunique()!=65 or md.groupby('Meth_Class').Methylation_Class_Name.nunique().max()!=1:raise ValueError('class ontology failure')
 md=md.sort_values('IDAT').reset_index(drop=True);md['chip']=md.IDAT.str.split('_').str[0]
 names=dict(md[['Meth_Class','Methylation_Class_Name']].drop_duplicates().itertuples(index=False,name=None))
 splits,panel,support,folds=mt.freeze_splits(md)
 idmap=label_map(md);position={z:i for i,z in enumerate(md.IDAT)}
 position.update({'VALIDATION_SAMPLE '+str(k):1077+k-1 for k in range(1,429)})
 mt.write_json('execution-amendment.json',{'date':'2026-10-01','seed':mt.SEED,'input':'author-processed GEO beta and detection P-values from both array platforms','feature_scope':'common cg-number rows across 450K and EPIC files; training-only selection from all common rows','qc':'beta missing or detection P-value missing/>0.01 becomes missing; exclude reference profile with >5% missing common CpGs; no outcome-informed exclusions','panel':'at least 10 QC-retained profiles and >=5 class training profiles in every metadata-frozen outer fold','scores':'uncalibrated RF votes; no nested calibration or clinical probability claim','model':'200-tree RF, train-only imputation and ANOVA top500; same frozen folds as released pilot','sensitivity':'equal per-class training counts, metadata/QC-defined as minimum across all outer folds/schemes; deterministic sampling','validation_capture':'428 numbered validation profiles retained and QC reported; no reference training/feature selection uses their values; external outcome reconciliation separate','nonreproduction':'Author-processed values are reused. Raw-IDAT QC, original probe exclusion manifests and original 10000-tree classifier are not reproduced.'})
 matrix=np.memmap(CACHE/'reference-common-candidates.dat',dtype=np.float32,mode='w+',shape=(MAX_ROWS,1505));matrix[:]=np.nan
 probes=[];lookup={};seen=None;sources=[];used_profiles=set()
 for turn,platform in enumerate(['GPL13534','GPL21145']):
  gsmmap,srec=series(platform,idmap);url=BASE+'suppl/GSE140686_'+platform+'_matrix_processed.txt.gz'
  t=time.time();nrows=0;kept=0
  with get(url) as response:
   counter=Counter(response)
   with gzip.GzipFile(fileobj=counter) as gz:
    head=next(csv.reader([gz.readline().decode().rstrip('\r\n')],delimiter='\t'))
    beta_cols=[];target=[]
    for j in range(1,len(head)):
     if head[j]=='Detection Pval':continue
     ref=canonical_reference(head[j]);ident=idmap.get(ref) or gsmmap.get(head[j])
     if ident is None and re.fullmatch(r'VALIDATION_SAMPLE\s+([1-9][0-9]*)',head[j]):ident=head[j] if head[j] in position else None
     if ident is None:continue
     if j+1>=len(head) or head[j+1]!='Detection Pval':raise ValueError('beta lacks expected detection P-value column')
     beta_cols.append(j-1);target.append(position[ident])
    if len(target)!=len(set(target)) or used_profiles&set(target):raise ValueError('duplicate profile/platform mapping')
    used_profiles.update(target);beta_cols=np.array(beta_cols,int);target=np.array(target,int)
    if turn:seen=np.zeros(len(probes),bool)
    while True:
     b=gz.readline(2_000_001)
     if not b:break
     if len(b)>2_000_000:raise ValueError('oversized measured row')
     nrows+=1;first,sep,rest=b.partition(b'\t')
     if not sep:raise ValueError('malformed measured row')
     probe=first.decode().strip('"\r\n')
     if not re.fullmatch(r'cg\d{8}',probe):continue
     if turn and probe not in lookup:continue
     if not turn:
      if probe in lookup or len(probes)>=MAX_ROWS:raise ValueError('duplicate/excess CpG rows')
      ri=len(probes);lookup[probe]=ri;probes.append(probe)
     else:
      ri=lookup[probe]
      if seen[ri]:raise ValueError('duplicate common CpG in EPIC')
      seen[ri]=True
     nums=np.fromstring(rest.replace(b'"',b'').replace(b'NA',b'nan').decode(),sep='\t',dtype=np.float32)
     if len(nums)!=len(head)-1:raise ValueError('numeric/header column mismatch')
     beta=nums[beta_cols];pval=nums[beta_cols+1]
     if np.any(np.isinf(beta)) or np.any(beta[np.isfinite(beta)]<0) or np.any(beta[np.isfinite(beta)]>1):raise ValueError('invalid beta')
     if np.any(np.isinf(pval)) or np.any(pval[np.isfinite(pval)]<0) or np.any(pval[np.isfinite(pval)]>1):raise ValueError('invalid detection P-value')
     bad=np.isnan(beta)|np.isnan(pval)|(pval>.01);beta=beta.copy();beta[bad]=np.nan
     matrix[ri,target]=beta;kept+=1
     if nrows%50000==0:print(json.dumps({'full_geo_progress':{'platform':platform,'rows':nrows,'compressed_bytes':counter.n,'seconds':round(time.time()-t,1)}}),flush=True)
   if counter.n!=SIZES[platform]:raise ValueError('full gzip size differs from observed pilot source')
   srec.update(processed_url=url,compressed_bytes=counter.n,compressed_sha256=counter.h.hexdigest(),header_sha256=mt.digest('\t'.join(head).encode()),mapped_reference_count=int(np.sum(target<1077)),mapped_validation_count=int(np.sum(target>=1077)),measurement_rows=nrows,retained_cg_rows=kept,seconds=round(time.time()-t,2))
  sources.append(srec)
 if used_profiles!=set(range(1505)):raise ValueError('not every reference and validation mapped exactly once')
 common=np.flatnonzero(seen);common_probes=[probes[i] for i in common]
 if len(common)<100000:raise ValueError('unexpectedly small common CpG set')
 matrix.flush();missing=np.zeros(1505,int)
 for start in range(0,len(common),4096):missing+=np.isnan(matrix[common[start:start+4096]]).sum(axis=0)
 ref_missing=missing[:1077];qc=ref_missing/len(common)<=.05
 mt.save_tsv('profile-qc.tsv',pd.DataFrame({'ID':md.ID,'IDAT':md.IDAT,'missing_common_cpgs':ref_missing,'common_cpgs':len(common),'missing_fraction':ref_missing/len(common),'QC_pass':qc}))
 mt.save_tsv('validation-profile-qc.tsv',pd.DataFrame({'ID':['VALIDATION_SAMPLE '+str(k) for k in range(1,429)],'missing_common_cpgs':missing[1077:],'common_cpgs':len(common),'missing_fraction':missing[1077:]/len(common),'QC_pass':missing[1077:]/len(common)<=.05}))
 mt.write_json('matrix-cache-index.json',{'cache_file':str(CACHE/'reference-common-candidates.dat'),'dtype':'float32','shape':[MAX_ROWS,1505],'reference_IDAT_order':md.IDAT.tolist(),'validation_ids':['VALIDATION_SAMPLE '+str(k) for k in range(1,429)],'common_row_indices':common.tolist(),'common_probe_ids':common_probes})
 eligible=[];postqc=[]
 for cls in sorted(md.Meth_Class.unique()):
  hit=(md.Meth_Class.to_numpy()==cls)&qc;r={'class':cls,'n_qc':int(hit.sum())};good=hit.sum()>=10
  for scheme,ss in splits.items():
   ns=[int(hit[a].sum()) for a,b in ss];r[scheme+'_train_counts']=ns;good=good and min(ns)>=5
  r['eligible']=bool(good);postqc.append(r)
  if good:eligible.append(cls)
 if len(eligible)<2:raise ValueError('QC leaves too few supported common classes')
 mask=md.Meth_Class.isin(eligible).to_numpy()&qc
 folds['QC_pass']=folds.IDAT.map(dict(zip(md.IDAT,qc)));folds['common_panel']=folds.IDAT.map(dict(zip(md.IDAT,mask)))
 mt.save_tsv('frozen-folds.tsv',folds);mt.write_json('class-support.json',postqc)
 imputation_audits=[]
 def chunk_select(ai,bi,y):
  a=ai.ravel().astype(int);b=bi.ravel().astype(int);scores=np.empty(len(common),float);medians=np.zeros(len(common),np.float32)
  for start in range(0,len(common),4096):
   stop=min(start+4096,len(common));v=np.array(matrix[common[start:stop]][:,a].T,copy=True);has=np.isnan(v).any(axis=0)
   if np.any(has):
    m=np.nan_to_num(np.nanmedian(v[:,has],axis=0),nan=0.0);medians[start:stop][has]=m;rr,cc=np.where(np.isnan(v));v[rr,cc]=medians[start:stop][cc]
   f,_=f_classif(v.astype(np.float64),y);scores[start:stop]=np.nan_to_num(f,nan=-np.inf,posinf=np.finfo(float).max,neginf=-np.inf)
  cols=np.argsort(-scores,kind='stable')[:500];av=np.array(matrix[common[cols]][:,a].T,copy=True);bv=np.array(matrix[common[cols]][:,b].T,copy=True);selected_medians=np.nan_to_num(np.nanmedian(av,axis=0),nan=0.0)
  missing_test=np.isnan(bv);training_complete=~np.isnan(av).any(axis=0);bad=missing_test&training_complete[None,:];changed=bad&(selected_medians[None,:]!=0);affected=b[changed.any(axis=1)]
  imputation_audits.append({'call':len(imputation_audits),'train_n':len(a),'test_n':len(b),'external':bool(np.any(b>=1077)),'selected_test_missing_cells':int(missing_test.sum()),'training_complete_test_missing_cells':int(bad.sum()),'old_zero_imputation_would_change_cells':int(changed.sum()),'old_zero_imputation_would_change_profiles':int(changed.any(axis=1).sum()),'affected_profile_ID':[str(md.iloc[k].ID) if k<1077 else 'VALIDATION_SAMPLE '+str(k-1077+1) for k in affected]})
  for v in [av,bv]:
   rr,cc=np.where(np.isnan(v));v[rr,cc]=selected_medians[cc]
  mt.write_json('imputation-audit.json',imputation_audits)
  print('EMC_METHYLATION_IMPUTATION_AUDIT '+json.dumps(imputation_audits[-1]),flush=True)
  return av,bv,cols
 mt.select_train=chunk_select
 quotas={c:min(int(((md.Meth_Class.to_numpy()==c)&mask)[a].sum()) for ss in splits.values() for a,b in ss) for c in eligible}
 equal={};training_rows=[]
 for scheme,ss in splits.items():
  equal[scheme]=[]
  for k,(a,b) in enumerate(ss):
   rng=np.random.default_rng(mt.SEED+k);chosen=[]
   for cls in eligible:
    pool=a[(md.Meth_Class.to_numpy()[a]==cls)&mask[a]];q=quotas[cls]
    chosen.extend(rng.permutation(pool)[:q].tolist())
   chosen=np.array(sorted(chosen),int);equal[scheme].append((chosen,b))
   for z in chosen:training_rows.append({'scheme':scheme,'fold':k,'IDAT':md.iloc[z].IDAT,'class':md.iloc[z].Meth_Class})
 mt.save_tsv('equal-budget-training.tsv',pd.DataFrame(training_rows));mt.write_json('equal-budget-quotas.json',quotas)
 archive={'probes':common_probes,'votes':{}};rows=[];stub=np.arange(1077).reshape(-1,1)
 result={'schema':'emc-full-processed-methylation-transfer/1','status':'running','input_receipt':{'sources':sources,'metadata_sha256':mt.MD_SHA,'common_cpg_count':len(common),'common_cpg_order_sha256':mt.digest('\n'.join(common_probes).encode()),'profile_order_sha256':mt.digest('\n'.join(md.IDAT).encode()),'QC_retained_profiles':int(qc.sum()),'validation_profiles_captured':428,'validation_QC_retained':int(np.sum(missing[1077:]/len(common)<=.05))},'class_names':names,'common_panel':{'classes':eligible,'profiles':int(mask.sum())},'model':'training-only ANOVA top500 from all common CpGs; RF200 trees; uncalibrated votes','equal_training_budget_per_fold':int(sum(quotas.values())),'limitations':['Author-processed measurements; raw-IDAT and original exclusion-manifest reproduction not performed','No nested calibration; 0.9 refers to uncalibrated RF votes','Supplier/chip differences may reflect biological case mix; no technical causation established','Methylation class is target, not an independently adjudicated diagnosis','Original independent 428-case cohort values captured, external label reconciliation/evaluation separate']}
 def checkpoint(stage):
  result['stage']=stage;result['seconds']=round(time.time()-START,2)
  mt.write_json('results.json',result);mt.save_tsv('per-profile-predictions.tsv',pd.DataFrame(rows));np.savez_compressed(OUT/'class-votes.npz',**archive['votes'])
  print('EMC_METHYLATION_FULL_CHECKPOINT_BEGIN',flush=True);print(json.dumps({'stage':stage,'results':result},separators=(',',':'),ensure_ascii=False,allow_nan=False),flush=True);print('EMC_METHYLATION_FULL_CHECKPOINT_END',flush=True)
 common_result,classes,idx=mt.evaluate('common',mask,splits,stub,md,rows,archive);result['common']=common_result
 index={'common_classes':classes,'common_IDAT':md.iloc[idx].IDAT.tolist(),'array_axes':['profile order in index','sorted class order in index']};mt.write_json('class-votes-index.json',index)
 checkpoint('full common-panel comparison completed')
 counts=md.loc[qc,'Meth_Class'].value_counts();rare_classes=[]
 for c in counts[counts>=5].index:
  hit=(md.Meth_Class.to_numpy()==c)&qc
  if min(int(hit[a].sum()) for a,b in splits['sample'])>=3:rare_classes.append(c)
 raremask=md.Meth_Class.isin(rare_classes).to_numpy()&qc
 rare_result,rclasses,ridx=mt.evaluate('sample_supported',raremask,{'sample':splits['sample']},stub,md,rows,archive);result['sample_supported']=rare_result
 index.update(sample_supported_classes=rclasses,sample_supported_IDAT=md.iloc[ridx].IDAT.tolist());mt.write_json('class-votes-index.json',index)
 checkpoint('rare-class sample comparison completed')
 # Frozen all-reference model; external values never enter ranking/imputation/fitting.
 validation_idx=np.arange(1077,1505,dtype=int)
 training_y=md.iloc[ridx].Meth_Class.to_numpy(dtype=str)
 train500,validation500,external_cols=chunk_select(np.asarray(ridx).reshape(-1,1),validation_idx.reshape(-1,1),training_y)
 final_rf=mt.RandomForestClassifier(n_estimators=200,max_features='sqrt',class_weight='balanced_subsample',n_jobs=2,random_state=mt.SEED+100)
 final_rf.fit(train500,training_y)
 if list(final_rf.classes_)!=rclasses:raise ValueError('external fit class order changed')
 validation_votes=final_rf.predict_proba(validation500)
 reference_oof=archive['votes']['sample_supported__sample__methylation']
 if reference_oof.shape!=(len(ridx),len(rclasses)) or validation_votes.shape!=(428,len(rclasses)):raise ValueError('external vote shape mismatch')
 if not np.isfinite(validation_votes).all() or not np.allclose(validation_votes.sum(1),1):raise ValueError('invalid external probabilities')
 validation_ids=np.array(['VALIDATION_SAMPLE '+str(k) for k in range(1,429)],dtype=str)
 validation_qc=missing[1077:]/len(common)<=.05
 selected_probe_ids=np.array([common_probes[z] for z in external_cols],dtype=str)
 np.savez_compressed(OUT/'external-fit-inputs.npz',training_X500=train500,validation_X500=validation500,training_y=training_y,reference_ID=md.iloc[ridx].ID.to_numpy(dtype=str),reference_IDAT=md.iloc[ridx].IDAT.to_numpy(dtype=str),validation_ID=validation_ids,selected_probe_ids=selected_probe_ids,validation_QC=validation_qc,classes=np.array(rclasses,dtype=str),random_seed=np.array([mt.SEED+100]))
 np.savez_compressed(OUT/'external-reference-and-validation-votes.npz',reference_OOF_votes=reference_oof,reference_y=training_y,reference_ID=md.iloc[ridx].ID.to_numpy(dtype=str),reference_IDAT=md.iloc[ridx].IDAT.to_numpy(dtype=str),validation_votes=validation_votes,validation_ID=validation_ids,validation_QC=validation_qc,classes=np.array(rclasses,dtype=str))
 ext_pred=pd.DataFrame({'ID':validation_ids,'QC_pass':validation_qc,'predicted_class':[rclasses[z] for z in validation_votes.argmax(1)],'max_uncalibrated_vote':validation_votes.max(1),'assigned_vote_0.9':validation_votes.max(1)>=.9})
 mt.save_tsv('external-uncalibrated-predictions.tsv',ext_pred)
 result['external_frozen_fit']={'reference_n':len(ridx),'classes':rclasses,'validation_n':428,'validation_QC_pass_n':int(validation_qc.sum()),'selected_probe_n':len(external_cols),'selected_probe_ids_sha256':mt.digest('\n'.join(selected_probe_ids).encode()),'seed':mt.SEED+100,'vote_0.9_assigned_all':int(np.sum(validation_votes.max(1)>=.9)),'vote_0.9_assigned_QC_pass':int(np.sum((validation_votes.max(1)>=.9)&validation_qc)),'status':'executed predictions; external target reconciliation and reference-only score transform pending','reference_OOF_status':'fivefold training-contained base predictions retained; fitting a transform and scoring these same OOF targets would not be an independent calibration assessment'}
 index.update(external_classes=rclasses,validation_ID=validation_ids.tolist());mt.write_json('class-votes-index.json',index)
 checkpoint('all-reference fit and 428 external predictions saved')
 eq_result,eqclasses,eqidx=mt.evaluate('equal_budget',mask,equal,stub,md,rows,archive);result['equal_budget']=eq_result
 if eqclasses!=classes or not np.array_equal(eqidx,idx):raise ValueError('equal budget comparison panel changed')
 checkpoint('equal training budget fits saved')
 frame=pd.DataFrame(rows)
 result['paired_brier_comparisons']=[mt.paired_bootstrap(frame,md,'Supplier'),mt.paired_bootstrap(frame,md,'chip')]
 eqframe=frame[frame.panel=='equal_budget'].assign(panel='common')
 result['equal_budget_paired_brier_comparisons']=[mt.paired_bootstrap(eqframe,md,'Supplier'),mt.paired_bootstrap(eqframe,md,'chip')]
 result['status']='completed full processed-matrix transfer and equal-budget sensitivity';checkpoint('complete')
 artifacts=[{'file':p.name,'size':p.stat().st_size,'sha256':mt.digest(p.read_bytes())} for p in sorted(OUT.iterdir()) if p.is_file()]
 print('EMC_METHYLATION_FULL_RESULT_BEGIN',flush=True);print(json.dumps({'results':result,'artifacts':artifacts},separators=(',',':'),ensure_ascii=False,allow_nan=False),flush=True);print('EMC_METHYLATION_FULL_RESULT_END',flush=True)
if __name__=='__main__':main()
