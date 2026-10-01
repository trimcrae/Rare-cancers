import json,hashlib,datetime,itertools
from pathlib import Path
import numpy as np,pandas as pd
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT;ROOTS=[Path('restored-artifacts'),Path('restored-artifacts-extra'),OUT];SEED=20261001
SENS=['human_UMI_ge500','all_source_barcodes','all_reference_UMI_ge500'];ENDS=['fraction_detected','fraction_summed_human_UMI']
def rc(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def bh(records,key,total,out):
 order=sorted([(i,r[key]) for i,r in enumerate(records) if r.get(key) is not None],key=lambda x:x[1]);q=1.
 for k in range(len(order)-1,-1,-1):i,p=order[k];q=min(q,p*total/(k+1));records[i][out]=q
def paired(frame,sens,endpoint,gene,human_assay,seed,inference):
 s=frame[(frame.barcode_sensitivity==sens)&(frame.gene==gene)].dropna(subset=[endpoint]);h=s[(s.source_class=='human_tumor')&(s.assay==human_assay)].groupby('literal_model_root')[endpoint].mean();p=s[(s.source_class=='baseline_PDX')&(s.assay=='scRNA')].groupby('literal_model_root')[endpoint].mean();z=pd.concat([h.rename('human'),p.rename('PDX')],axis=1).dropna();n=len(z);diff=(z.human-z.PDX).to_numpy(float);r={'gene':gene,'endpoint':endpoint,'barcode_sensitivity':sens,'human_assay':human_assay,'PDX_assay':'scRNA','n_matched_literal_model_roots':n,'matched_values':z.reset_index().to_dict(orient='records'),'human_minus_PDX_mean':float(diff.mean()) if n else None,'human_minus_PDX_median':float(np.median(diff)) if n else None,'clinical_patient_identity_verified':False}
 if inference and n>=6:
  assert n<=16;signs=np.array(list(itertools.product([-1.,1.],repeat=n)));null=signs@diff/n;point=float(diff.mean());rng=np.random.default_rng(seed);boot=diff[rng.integers(0,n,(2000,n))].mean(axis=1);r.update(descriptive_exact_paired_sign_flip_p=float(np.mean(np.abs(null)>=abs(point)-1e-14)),literal_model_root_bootstrap95=np.quantile(boot,[.025,.975]).tolist(),interpretation='Human-sn/PDX-sc confoundedsource/assay; nottreatment/cellstate/verifiedpatients')
 else:r['interpretation']='Descriptivesmallrootcount/noinferentialclaim'
 return r
def main():
 OUT.mkdir(parents=True,exist_ok=True);paths=sorted({p for root in ROOTS for p in root.rglob('RMS-full42-count-batch-*.json')});assert paths;libs={};receipts=[];expected=None;amendment=None;compact_libs=[]
 for path in paths:
  d=json.loads(path.read_text());assert d['schema']=='emc-RMS-full42-count-batch/1' and d['complete'] and d['errors']==0;ids=d['all42_accessions'];assert len(ids)==42 and len(set(ids))==42
  if expected is None:expected=ids;amendment=d['amendment']
  assert ids==expected and d['amendment']==amendment;receipts.append(rc(path));a,b=d['range'];assert{r['global_library_index'] for r in d['libraries']}==set(range(a,b))
  for r in d['libraries']:
   assert r['status']=='measured';i=r['global_library_index'];assert r['GSM']==expected[i]
   if i in libs:assert libs[i]==r,'Conflictingduplicate'
   else:libs[i]=r
 assert set(libs)==set(range(42));rows=[];audit=[]
 for i,r in sorted(libs.items()):
  identity=r['identity_audit'];m=r['measured_counts'];prefix=m.get('human_symbol_prefix_amendments',[]);pp=OUT/(r['GSM']+'-human-symbol-prefix-audit.tsv');pd.DataFrame(prefix).to_csv(pp,sep='\t',index=False);bounded={**m,'human_symbol_prefix_amendments':{'n':len(prefix),'first20':prefix[:20],'complete_table':rc(pp)}};compact_libs.append({'GSM':r['GSM'],'source_metadata':r['source_metadata'],'identity_audit':identity,'member_receipts':r['member_receipts'],'measured_counts':bounded})
  audit.append({'GSM':r['GSM'],**identity,'matrix_shape':m['matrix_shape'],'feature_species_counts':m['feature_species_counts'],'UMI_totals':m['UMI_totals']})
  for s in m['all_frozen_target_summaries']:rows.append({'GSM':r['GSM'],**identity,**s})
 summarypath=OUT/'RMS-all42-measured-targets-compact.json';summarypath.write_text(json.dumps(sm.clean({'schema':'emc-RMS-all42-measured-targets/1','batch_receipts':receipts,'libraries':compact_libs}),allow_nan=False))
 f=pd.DataFrame(rows);assert set(f.barcode_sensitivity)==set(SENS);genes=sorted(f.gene.unique());assert len(genes)==86;assert f[['GSM','gene','barcode_sensitivity']].drop_duplicates().shape[0]==42*86*3;f.to_csv(OUT/'RMS-all42-frozen-target-library-summaries.tsv',sep='\t',index=False);keys=['literal_model_root','source_class','assay','gene','barcode_sensitivity'];groups=f.groupby(keys)[ENDS].mean().reset_index();groups.to_csv(OUT/'RMS-literal-model-root-source-assay-summaries.tsv',sep='\t',index=False);tests=[]
 for si,sens in enumerate(SENS):
  family=[paired(f,sens,endpoint,gene,'snRNA',SEED+24000+si*1000+ei*100+gi,True) for ei,endpoint in enumerate(ENDS) for gi,gene in enumerate(genes)];bh(family,'descriptive_exact_paired_sign_flip_p',172,'BH_q_fixed172_descriptive');tests.extend(family)
 same=[paired(f,sens,e,g,'scRNA',SEED,False) for sens in SENS for e in ENDS for g in genes];special=f[f.source_class.isin(['treated_PDX','organoid'])].copy();special.to_csv(OUT/'RMS-treated-single-model-and-organoid-descriptive.tsv',sep='\t',index=False);counts=pd.DataFrame(audit).groupby(['source_class','assay']).GSM.count().to_dict();primary=[r for r in tests if r['barcode_sensitivity']=='human_UMI_ge500'];result={'schema':'emc-RMS-full42-frozen-aggregate/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':{'dated_utc':'2026-10-01','selection':'All42/86genes×2endpoints; humanUMI500primary plus2sensitivities','aggregation':'Equallibrarymean/root/source/assay, rootsnotverifiedpatients','tests':'All172human-sn/PDX-sc signflip/rootbootstrap/BH172; source&assayinseparable','same_assay':'Twohuman-sc/PDX-sc roots descriptiveonly','special_sources':'ThreetreatedPDXsn timepoints one literalmodel, no00026vs000026 harmonization; oneorganoid','limits':'No cellidentity/protein/function/drugvalidation'},'batch_receipts':receipts,'all42_library_identity_and_species_audit':audit,'library_counts_by_source_assay':[{'source_class':k[0],'assay':k[1],'libraries':int(v)} for k,v in counts.items()],'all516_cross_assay_endpoint_sensitivities':tests,'same_assay_small_root_descriptive':same,'single_model_treatment_and_organoid_summary':special.to_dict(orient='records'),'primary_measured_endpoint_counts':{'fixed_tests':172,'successful_paired_tests':sum(r.get('descriptive_exact_paired_sign_flip_p') is not None for r in primary),'BH_below_05':sum(r.get('BH_q_fixed172_descriptive',1)<.05 for r in primary)},'compact_library_measurements':rc(summarypath),'tables':[str(OUT/'RMS-all42-frozen-target-library-summaries.tsv'),str(OUT/'RMS-literal-model-root-source-assay-summaries.tsv'),str(OUT/'RMS-treated-single-model-and-organoid-descriptive.tsv')]};dest=OUT/'RMS-full42-frozen-aggregate-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_RMS_FULL42_AGGREGATE_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_RMS_FULL42_AGGREGATE_END')
 # Preserve every measured library/target value in a bounded positional payload.
 columns=sorted({k for lib in compact_libs for row in lib['measured_counts']['all_frozen_target_summaries'] for k in row})
 payload={'schema':'emc-RMS-all42-measured-target-values/1','summary_columns':columns,'libraries':[]}
 for lib in compact_libs:
  measured=lib['measured_counts']
  payload['libraries'].append({**{k:v for k,v in lib.items() if k!='measured_counts'},'count_audit':{k:v for k,v in measured.items() if k!='all_frozen_target_summaries'},'target_value_rows':[[row.get(k) for k in columns] for row in measured['all_frozen_target_summaries']]})
 print('EMC_RMS_ALL42_VALUES_BEGIN');print(json.dumps(sm.clean(payload),allow_nan=False,separators=(',',':')));print('EMC_RMS_ALL42_VALUES_END')

if __name__=='__main__':main()
