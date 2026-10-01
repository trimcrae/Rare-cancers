#!/usr/bin/env python3
import hashlib,json,math,pathlib,re,unicodedata
from collections import Counter
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp
BASE=pathlib.Path(__file__).resolve().parent/'outputs';FULL=BASE/'methylation-full-geo';OUT=BASE/'methylation-external';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(v):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',str(v)).lower())
def sid(v):return re.sub(r'\s+','',str(v)).upper()
meta_path=BASE/'methylation-validation'/'primary-workbooks.json';source=json.loads(meta_path.read_text());full=json.loads((FULL/'results.json').read_text())
wb=next(w for w in source['workbooks'] if w.get('sha256')=='605dd1ba7af9845e53f5db51c11b8d7e36b0076ade3dd5ba97edccbdf32ceb36');sheet=next(s for s in wb['sheets'] if s['n_rows']==429);rows=sheet['rows'];assert len(rows)==429
headers=[str(v) if v is not None else 'ID' for v in rows[0]];df=pd.DataFrame(rows[1:],columns=headers);df['join_ID']=df.ID.map(sid)
assert len(df)==428 and df.join_ID.nunique()==428 and set(df.join_ID)=={'VALIDATION_SAMPLE'+str(k) for k in range(1,429)} and df.IDAT.nunique()==428
npz_path=FULL/'external-reference-and-validation-votes.npz';z=np.load(npz_path,allow_pickle=False);classes=np.asarray(z['classes']).astype(str);ci={c:i for i,c in enumerate(classes)}
rp=np.asarray(z['reference_OOF_votes'],dtype=float);vp=np.asarray(z['validation_votes'],dtype=float);rid=np.asarray(z['reference_ID']).astype(str);ri=np.asarray(z['reference_IDAT']).astype(str);vid=np.asarray(z['validation_ID']).astype(str);qc=np.asarray(z['validation_QC']).astype(bool)
assert len(classes)==65 and len(set(classes))==65 and rp.shape==(len(rid),65) and vp.shape==(428,65) and qc.shape==(428,)
assert len(rid)==1077 and len(set(rid))==1077 and len(set(ri))==1077 and set(map(sid,vid))==set(df.join_ID)
df=df.set_index('join_ID').loc[list(map(sid,vid))].reset_index();df['QC_pass']=qc;assert not set(ri)&set(df.IDAT.astype(str))
for p in (rp,vp):assert np.all(np.isfinite(p)) and np.all((p>=0)&(p<=1)) and np.allclose(p.sum(axis=1),1,atol=1e-6)
ry=np.asarray(z['reference_y'])
if np.issubdtype(ry.dtype,np.number):assert np.all(ry==ry.astype(int));y=ry.astype(int)
else:y=np.array([ci[str(t)] for t in ry],dtype=int)
assert len(y)==len(rp) and np.all((y>=0)&(y<65))
EPS=1e-6;rl=np.log(np.clip(rp,EPS,1));vl=np.log(np.clip(vp,EPS,1))
def transform(logp,T):t=logp/T;return np.exp(t-logsumexp(t,axis=1,keepdims=True))
def objective(logT):t=rl/np.exp(logT);return float(np.mean(logsumexp(t,axis=1)-t[np.arange(len(y)),y]))
opt=minimize_scalar(objective,bounds=(math.log(.05),math.log(10)),method='bounded',options={'xatol':1e-7});assert opt.success;T=float(np.exp(opt.x));tp=transform(vl,T)
raw_score_logp=vl-logsumexp(vl,axis=1,keepdims=True)
temp_score_logp=vl/T-logsumexp(vl/T,axis=1,keepdims=True)
lookup={canon(c):c for c in classes};lookup.update({'ewing':'EWS','csagroupa':'CSA-A','csagroupb':'CSA-B','csaidhgroupa':'CSA-IDH-A','csaidhgroupb':'CSA-IDH-B'})
original=[lookup.get(canon(v)) for v in df['V12.2_MaxCalDiag']];assert all(original);df['original_class_code']=original;oy=np.array([ci[c] for c in original]);df['original_score']=pd.to_numeric(df['V12.2_MaxCalScore'],errors='raise');assert np.sum(df.original_score.to_numpy()>=.9)==322
names=full['class_names'];hist={canon(v.replace('methylation class ','')):{k} for k,v in names.items()}
aliases={'Ewing´s sarcoma':['EWS'],'Clear cell sarcoma of soft tissue':['CCS'],'Rhabdoid tumour':['MRT'],'Small round cell tumour with BCOR alteration':['SBRCT-BCOR'],'Gastroinstestinal stromal tumour':['GIST'],'Liposarcoma (myxoid)':['MLS'],'Liposarcoma (well differentiated)':['WDLS-DDLS'],'Liposarcoma (dedifferentiated)':['WDLS-DDLS'],'Epithelioid sarcoma, proximal type':['ES'],'Chondrosarcoma':['CSA-A','CSA-B','CSA-CC','CSA-IDH-A','CSA-IDH-B','CSA-MES'],'Chordoma':['CHORD','CHORD-DD'],'Endometrial stromal sarcoma':['ESS-HG','ESS-LG']}
for k,v in aliases.items():hist[canon(k)]=set(v)
allowed=[hist.get(canon(v),set()) for v in df['Institutional diagnosis']];assert all(s<=set(classes) for s in allowed)
df['initial_target_codes']=['|'.join(sorted(s)) for s in allowed];df['initial_target_mapping']=['single_class' if len(s)==1 else 'explicit_broad_histotype' if s else 'unmapped_or_ambiguous' for s in allowed]
rwb=next(w for w in source['workbooks'] if w.get('sha256')=='85a148285ef1812d6ca8d68c839a2d64f73cebb6f8ebfa95844e3d85b5c03bb9');rr=next(s['rows'] for s in rwb['sheets'] if s['n_rows']==1078);assert len(rr)==1078
rh=[str(v) if v is not None else 'blank_'+str(i) for i,v in enumerate(rr[0])];rdf=pd.DataFrame(rr[1:],columns=rh);rdf['join_ID']=rdf.ID.map(sid);assert rdf.join_ID.nunique()==1077;rdf=rdf.set_index('join_ID').loc[list(map(sid,rid))]
assert np.array_equal(rdf.IDAT.astype(str).to_numpy(),ri) and all(canon(v)==canon(names[classes[t]]) for v,t in zip(rdf['Methylation Class Name'],y))
pred=classes[np.argmax(vp,axis=1)];score=vp.max(axis=1);tscore=tp.max(axis=1);assert np.array_equal(np.argmax(vp,axis=1),np.argmax(tp,axis=1))
df['our_class']=pred;df['raw_maxvote']=score;df['reference_fitted_temperature_score']=tscore;df['agrees_original_maxclass']=pred==np.asarray(original);df['agrees_initial_mapped_diagnosis']=[bool(p in a) if a else None for p,a in zip(pred,allowed)]
df['initial_target_raw_vote']=[float(sum(vp[i,ci[c]] for c in a)) if a else None for i,a in enumerate(allowed)];df['initial_target_transformed_score']=[float(sum(tp[i,ci[c]] for c in a)) if a else None for i,a in enumerate(allowed)]
def wilson(k,n):
 if not n:return None
 z=1.95996398454;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [c-r,c+r]
def agreement(mask):
 idx=np.flatnonzero(mask);n=len(idx)
 if not n:return {'n':0}
 ok=(pred[idx]==np.asarray(original)[idx]);labels=np.unique(oy[idx]);out={'n':n,'agreements':int(ok.sum()),'agreement_rate':float(ok.mean()),'profile_wilson95':wilson(int(ok.sum()),n),'macro_recall_original_maxclass':float(np.mean([np.mean(ok[oy[idx]==c]) for c in labels]))}
 for name,p in [('raw',vp),('reference_temperature',tp)]:
  q=p[idx];target=oy[idx];oh=np.zeros_like(q);oh[np.arange(n),target]=1;accepted=q.max(axis=1)>=.9;na=int(accepted.sum());ka=int(ok[accepted].sum())
  out[name]={'Brier_vs_original_maxclass':float(np.mean(np.sum((q-oh)**2,axis=1))),'NLL_vs_original_maxclass_input_smoothed':float(-np.mean((raw_score_logp if name=='raw' else temp_score_logp)[idx,target])),'score_0.9_assigned':na,'coverage':na/n,'assigned_agreements':ka,'assigned_agreement_rate':ka/na if na else None,'assigned_profile_wilson95':wilson(ka,na)}
 return out
mapped=np.array([bool(a) for a in allowed]);initialok=np.array([p in a for p,a in zip(pred,allowed)])
def initial_metrics(mask):
 included=mask&mapped;n=int(included.sum());k=int(initialok[included].sum());out={'eligible_profiles':int(mask.sum()),'mapped_profiles':n,'unmapped_or_ambiguous_profiles':int(np.sum(mask&~mapped)),'concordances':k,'concordance_rate':k/n if n else None,'profile_wilson95':wilson(k,n)}
 for name,p in [('raw',vp),('reference_temperature',tp)]:
  a=included&(p.max(axis=1)>=.9);na=int(a.sum());ka=int(initialok[a].sum());out[name]={'assigned_mapped_profiles':na,'assigned_concordances':ka,'assigned_concordance_rate':ka/na if na else None}
 return out
unmapped=Counter(str(v) for v,m in zip(df['Institutional diagnosis'],mapped) if not m)
pd.DataFrame([{'institutional_diagnosis':k,'profiles':v,'reason':'No exact reference classname or frozen conservative histotype alias'} for k,v in sorted(unmapped.items())]).to_csv(OUT/'initial-diagnosis-exclusion-ledger.tsv',sep='\t',index=False)
df.to_csv(OUT/'per-profile-external-evaluation.tsv',sep='\t',index=False);np.savez_compressed(OUT/'external-evaluated-votes.npz',validation_ID=vid,classes=classes,raw_votes=vp,reference_temperature_votes=tp,temperature=np.array([T]),original_maxclass_y=oy,QC_pass=qc)
qcmask=qc;certain=qc&(df.original_score.to_numpy()>=.9)
summary={'schema':'emc-external-reanalysis/1','status':'executed','reference_profiles':len(rid),'validation_profiles':428,'validation_QC_pass':int(qc.sum()),'identity':{'unique_reference_IDAT':len(set(ri)),'unique_validation_IDAT':int(df.IDAT.nunique()),'reference_validation_IDAT_overlap':0,'shared_physical_chip_prefixes':len({v.split('_')[0] for v in ri}&{v.split('_')[0] for v in df.IDAT.astype(str)})},'original_validation_status_counts':dict(Counter(df['V12.2 Result'])),'temperature':{'T':T,'epsilon':EPS,'bounds':[.05,10],'optimizer_success':bool(opt.success),'training_targets':'1077 reference fivefold OOFvotes/labels only','performance_on_temperature_fit_targets_reported':False,'clinical_calibration_claim':False,'logscore_definition':'Proper normalized INPUT-smoothed votes (epsilon1e-6) then temperature in logspace; no final probability clipping. Raw Brier and threshold use original votes.'},'algorithm_agreement_all_QC_pass':agreement(qcmask),'algorithm_agreement_original_score_at_least_0.9':agreement(certain),'algorithm_agreement_by_original_status':{str(s):agreement(qcmask&(df['V12.2 Result'].to_numpy()==s)) for s in sorted(df['V12.2 Result'].unique())},'algorithm_agreement_by_supplier':{str(s):agreement(qcmask&(df['Supplier study'].to_numpy()==s)) for s in sorted(df['Supplier study'].unique())},'initial_institutional_diagnosis_concordance':initial_metrics(qcmask),'initial_mapping_counts':dict(Counter(df.initial_target_mapping)),'initial_unmapped_diagnoses':dict(sorted(unmapped.items())),'primary_validation_workbook_sha256':wb['sha256'],'primary_reference_workbook_sha256':rwb['sha256'],'source_files_sha256':{str(p.relative_to(BASE)):sha(p) for p in [meta_path,npz_path,FULL/'results.json']},'artifacts_sha256':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'limitations':['Original maxclass algorithmcomparator,not independentclinicaltruth; lowscores separate','Initialdiagnosis canberevised; concordance notaccuracy','Reference-onlytemperature preservesranking; agreementloss againstoriginalalgorithm','ReferenceOOFfit targets not independenttransformvalidation','Distinctprofiles/arrays; patientIDs insufficientpatientindependence','Wilson intervals descriptive,no sharedgroupadjustment','InitialEMC54 reclassifiedSEF; molecular NR4A3-positive405 inspected separately, not excluded by initialdiagnosis']}
interesting=(df['V12.2 Result'].astype(str).str.contains('misleading')|df['Institutional diagnosis'].astype(str).str.contains('Extraskeletal myxoid',case=False))
summary['selected_published_cases']=df.loc[interesting,['ID','Institutional diagnosis','V12.2 Result','Validation','original_class_code','original_score','our_class','raw_maxvote','reference_fitted_temperature_score']].where(pd.notna(df),None).to_dict(orient='records')
(OUT/'results.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print('EMC_METHYLATION_EXTERNAL_RESULT_BEGIN');print(json.dumps(summary,allow_nan=False));print('EMC_METHYLATION_EXTERNAL_RESULT_END')
