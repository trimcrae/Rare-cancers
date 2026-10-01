import hashlib,json,pathlib,re,shutil,base64
from collections import Counter
import numpy as np
import pandas as pd
from scipy.special import logsumexp
BASE=pathlib.Path(__file__).resolve().parent/'outputs'
for name in ['methylation-external','methylation-full-geo','methylation-validation']:
 matches=[p for p in pathlib.Path('restored-artifacts').rglob(name) if p.is_dir()]
 assert len(matches)==1,(name,matches)
 dest=BASE/name
 if dest.exists():shutil.rmtree(dest)
 shutil.copytree(matches[0],dest)
EXT=BASE/'methylation-external';FULL=BASE/'methylation-full-geo';OUT=BASE/'methylation-fusion-audit';OUT.mkdir(parents=True,exist_ok=True)
p=EXT/'per-profile-external-evaluation.tsv';df=pd.read_csv(p,sep='\t').fillna('')
z=np.load(EXT/'external-evaluated-votes.npz',allow_pickle=False);fz=np.load(FULL/'external-reference-and-validation-votes.npz',allow_pickle=False)
def sid(v):return re.sub(r'\s+','',str(v)).upper()
assert len(df)==428 and list(map(sid,df.ID))==list(map(sid,z['validation_ID']))
classes=z['classes'].astype(str);ci={c:i for i,c in enumerate(classes)}
raw=np.asarray(z['raw_votes'],float);trans=np.asarray(z['reference_temperature_votes'],float);qc=z['QC_pass'].astype(bool)
assert raw.shape==trans.shape==(428,65)
input_logp=np.log(np.clip(raw,1e-6,1));raw_score_logp=input_logp-logsumexp(input_logp,axis=1,keepdims=True);T=float(np.asarray(z['temperature']).ravel()[0]);temp_score_logp=input_logp/T-logsumexp(input_logp/T,axis=1,keepdims=True)
assert np.allclose(np.exp(temp_score_logp),trans,atol=1e-12)
rules=[('EWSR1','FLI1','EWS'),('EWSR1','ERG','EWS'),('PAX3','FOXO1','RMS-ALV'),('PAX7','FOXO1','RMS-ALV'),('SS18','SSX1','SYSA'),('SS18','SSX2','SYSA'),('SS18','SSX2B','SYSA'),('EWSR1','WT1','DSRCT'),('ASPSCR1','TFE3','ASPS'),('NAB2','STAT6','SFT'),('FUS','DDIT3','MLS'),('DDIT3','FUS','MLS'),('CIC','DUX4','SBRCT-CIC'),('BCOR','CCNB3','SBRCT-BCOR'),('COL1A1','PDGFB','DFSP'),('EWSR1','NR4A3','EMCS'),('HEY1','NCOA2','CSA-MES')]
rule_re=[(a,b,c,re.compile(r'(?<![A-Z0-9])'+a+r'\s*:\s*'+b+r'(?![A-Z0-9])',re.I)) for a,b,c in rules]
annotation=[];target=np.full(428,-1,dtype=int)
for i,row in df.iterrows():
 note=str(row.Validation);matches=[(a,b,c) for a,b,c,pat in rule_re if pat.search(note)];candidates=set(c for a,b,c in matches)
 if re.search(r'\bno\s+RNA\b|reported|unclear|\bno\s+fusion\b',note,re.I):reason='Historical/unclear/absent assay explicitly noted; excluded'
 elif not re.search(r'\bfusion\b',note,re.I):reason='No explicit reported fusion annotation'
 elif not candidates:reason='Fusion absent from frozen specific mapping or compatible with multiple taxonomic entities'
 elif len(candidates)!=1:reason='Conflicting mapped fusion classes'
 else:reason='Included: explicit reported hallmark fusion';target[i]=ci[next(iter(candidates))]
 annotation.append({'ID':row.ID,'IDAT':row.IDAT,'institutional_diagnosis':row['Institutional diagnosis'],'original_class':row.original_class_code,'original_score':row.original_score,'original_status':row['V12.2 Result'],'published_validation_note':note,'matched_rules':'|'.join(a+':'+b+'->'+c for a,b,c in matches),'fusion_compatible_target':classes[target[i]] if target[i]>=0 else '', 'reason':reason,'QC_pass':bool(qc[i])})
ann=pd.DataFrame(annotation);ann.to_csv(OUT/'all-428-annotation-inventory.tsv',sep='\t',index=False);mask=(target>=0)&qc
assert int(mask.sum())==120 and len(np.unique(target[mask]))==12
ourpred=raw.argmax(1);old=np.array([ci[str(v)] for v in df.original_class_code]);olds=pd.to_numeric(df.original_score).to_numpy()
def concordance(t,pred,scores,mask):
 idx=np.flatnonzero(mask);n=len(idx)
 if not n:return {'n':0}
 ok=pred[idx]==t[idx];high=scores[idx]>=.9;nh=int(high.sum());kh=int(ok[high].sum())
 return {'n':n,'concordant':int(ok.sum()),'concordance_fraction':float(ok.mean()),'macro_class_concordance':float(np.mean([np.mean(ok[t[idx]==c]) for c in np.unique(t[idx])])),'score_0.9_assigned':nh,'coverage':nh/n,'assigned_concordant':kh,'assigned_concordance_fraction':kh/nh if nh else None}
def molecular(mask):
 out={'published_original_classifier':concordance(target,old,olds,mask)};idx=np.flatnonzero(mask)
 for name,v in [('raw',raw),('reference_temperature',trans)]:
  m=concordance(target,ourpred,v.max(1),mask)
  if len(idx):
   tp=v[idx,target[idx]];m['Brier_fusion_compatible_label']=float(np.mean(np.sum(v[idx]**2,axis=1)-2*tp+1));m['NLL_fusion_compatible_label_input_smoothed']=float(-np.mean((raw_score_logp if name=='raw' else temp_score_logp)[idx,target[idx]]))
  out[name]=m
 return out
shared={str(v).split('_')[0] for v in fz['reference_IDAT']} & {str(v).split('_')[0] for v in df.IDAT}
unshared=qc&~df.IDAT.astype(str).str.split('_').str[0].isin(shared).to_numpy()
agreement={name:concordance(old,ourpred,v.max(1),unshared) for name,v in [('raw',raw),('reference_temperature',trans)]};prep=df['DNA preparation'].astype(str).str.strip().to_numpy()
sel=ann.loc[mask].copy();ii=np.flatnonzero(mask);sel['our_class']=classes[ourpred[ii]];sel['raw_maxvote']=raw.max(1)[ii];sel['temperature_score']=trans.max(1)[ii];sel['raw_fusion_target_vote']=raw[ii,target[ii]];sel['temperature_fusion_target_score']=trans[ii,target[ii]];sel['our_fusion_concordance']=ourpred[ii]==target[ii];sel['original_fusion_concordance']=old[ii]==target[ii];sel['DNA_preparation']=prep[ii]
sel.to_csv(OUT/'fusion-supported-profile-predictions.tsv',sep='\t',index=False)
pp=FULL/'per-profile-predictions.tsv'
if pp.exists():
 internal=pd.read_csv(pp,sep='\t');internal.groupby(['panel','scheme','model','truth','predicted'],dropna=False).size().rename('profiles').reset_index().to_csv(OUT/'internal-confusion-counts.tsv',sep='\t',index=False)
mp=BASE/'methylation-validation'/'primary-workbooks.json';primary=json.loads(mp.read_text());rwb=next(w for w in primary['workbooks'] if w['sha256']=='85a148285ef1812d6ca8d68c839a2d64f73cebb6f8ebfa95844e3d85b5c03bb9');rr=next(s['rows'] for s in rwb['sheets'] if s['n_rows']==1078);assert len(rr)==1078
result={'schema':'emc-published-fusion-annotation-audit/1','status':'executed','rule_freeze':'2026-10-01 before inspection of our428 external predictions','target':'Concordance with published hallmark-fusion-compatible methylation label, not adjudicated clinical accuracy','logscore_definition':'Normalized INPUT-smoothed votes epsilon1e-6; temperature in logspace, no output clipping','rules':[{'fusion':a+':'+b,'class':c} for a,b,c in rules],'annotation_inventory_counts':dict(Counter(ann.reason)),'fusion_subset':{'profiles':int(mask.sum()),'classes':len(np.unique(target[mask])),'class_support':{classes[c]:int(np.sum(mask&(target==c))) for c in np.unique(target[mask])}},'molecular_annotation_concordance':molecular(mask),'molecular_by_class':{classes[c]:molecular(mask&(target==c)) for c in np.unique(target[mask])},'molecular_original_score_below_0.9':molecular(mask&(olds<.9)),'molecular_excluding_shared_physical_chip':molecular(mask&unshared),'preparation_counts':{'reference':dict(Counter(str(row[6]).strip() for row in rr[1:])),'validation':dict(Counter(prep))},'molecular_by_DNA_preparation':{s:molecular(mask&(prep==s)) for s in sorted(set(prep))},'shared_chip_sensitivity':{'shared_chip_prefixes':sorted(shared),'excluded_validation_ids':df.loc[qc&~unshared,'ID'].tolist(),'remaining_QC_profiles':int(unshared.sum()),'algorithm_agreement':agreement},'limitations':['Molecular findings are author-reported supplemental annotations; raw genomic assays and blinded patient-level adjudication are unavailable','Testing/workup may have been prompted by methylation or morphology; ascertainment and incorporation effects cannot be removed','Fusion-to-class rules use specific hallmark events and omit shared/unclear/historical findings; finite subset is not representative of all sarcoma','Only one NR4A3-fusion-compatible EMC profile exists; neither one case nor ten reference profiles establishes diagnostic sensitivity','All score transformations were fitted to reference OOF only; no external fusion annotation entered feature selection, forest fitting or temperature fitting','Existing taxonomy and author-processed methylation values are reused; results are retrospective robustness/annotation audits, not newly discovered tumour entities'],'input_sha256':{str(path.relative_to(BASE)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [p,EXT/'external-evaluated-votes.npz',FULL/'external-reference-and-validation-votes.npz',mp]},'artifact_sha256':{path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in OUT.iterdir() if path.is_file()}}
(OUT/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('EMC_METHYLATION_FUSION_AUDIT_BEGIN');print(json.dumps(result,allow_nan=False));print('EMC_METHYLATION_FUSION_AUDIT_END')
interest=sel[(sel.ID.map(sid)=='VALIDATION_SAMPLE405')|(~sel.our_fusion_concordance)|(~sel.original_fusion_concordance)]
print('EMC_METHYLATION_FUSION_CASES_BEGIN');print(json.dumps({'fusion_audit_selected_profiles':interest.to_dict(orient='records')},default=str));print('EMC_METHYLATION_FUSION_CASES_END')
for f in [EXT/'external-evaluated-votes.npz',FULL/'external-reference-and-validation-votes.npz',FULL/'per-profile-predictions.tsv']:
 if not f.exists():continue
 b=f.read_bytes();v=base64.b64encode(b).decode();parts=[v[i:i+500000] for i in range(0,len(v),500000)]
 for i,part in enumerate(parts):
  print('EMC_DURABLE_FILE_BEGIN');print(json.dumps({'path':str(f.relative_to(BASE)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'encoding':'base64','chunk_index':i,'chunk_count':len(parts),'data':part}));print('EMC_DURABLE_FILE_END')
