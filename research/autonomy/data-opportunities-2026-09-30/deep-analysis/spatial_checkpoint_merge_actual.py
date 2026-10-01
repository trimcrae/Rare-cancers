import argparse,json,hashlib,datetime
from pathlib import Path
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
OUT=sm.OUT
def unique_imc_for_patient_inference(records):
 seen={};unique=[];duplicates=[]
 for i,r in enumerate(records):
  c=r.get('clinical',{});roi=c.get('ROI_ID')
  if roi is None:unique.append(r);continue
  if roi in seen:
   previous=seen[roi];assert c==previous['clinical'],'Conflicting clinical assignment for one acquisition';duplicates.append({'ROI_ID':roi,'kept_global_index':previous['global_index'],'excluded_duplicate_global_index':i,'clinical':c});continue
  seen[roi]={'clinical':c,'global_index':i};unique.append(r)
 return unique,duplicates
def fixed15(result):
 tests=result.get('primary_histology_tests',[]);order=sorted([(i,r['patient_histology_permutation_p']) for i,r in enumerate(tests) if 'patient_histology_permutation_p' in r],key=lambda x:x[1]);q=1.
 for k in range(len(order)-1,-1,-1):i,p=order[k];q=min(q,p*15/(k+1));tests[i]['BH_q_fixed_primary15']=q
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--input-root',action='append');a=p.parse_args();roots=[Path(x) for x in (a.input_root or ['restored-artifacts'])];paths=sorted({v for root in roots for v in root.rglob('spatial-followthrough-batch-*.json')});assert paths;records={'imc':{},'tiff':{}};receipts=[];amendments=[];metadata=[];schemas=[]
 for path in paths:
  raw=path.read_bytes();b=json.loads(raw);assert b['schema']=='emc-spatial-followthrough-batch/1' and b['complete'];mode=b['mode'];assert mode in records;start,stop=b['range'];assert {r['global_index'] for r in b['records']}==set(range(start,stop));assert b['frozen_total']==(200 if mode=='imc' else 50);receipts.append({'saved':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'mode':mode,'range':[start,stop],'measured':b['measured'],'errors':b['errors']});amendments.append(b['measurement_amendment']);metadata.extend([b['clinical_metadata_receipt']] if 'clinical_metadata_receipt' in b else []);schemas.extend(b.get('schemas',[]))
  for r in b['records']:
   i=r['global_index']
   if i in records[mode]:assert json.dumps(records[mode][i],sort_keys=True)==json.dumps(r,sort_keys=True),'Conflicting duplicate scientific record'
   else:records[mode][i]=r
 assert set(records['imc'])==set(range(200)) and set(records['tiff'])==set(range(50)),'Missing planned indices: no inference';assert all(x==amendments[0] for x in amendments)
 def measured(mode):return [r['result'] if r['status']=='measured' else {k:v for k,v in r.items() if k not in ['result','status']} for i,r in sorted(records[mode].items())]
 result={'schema':'emc-spatial-marker-followthrough/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':amendments[0],'completion_method':'All200metadata rows and50frozenEwingfiles requested in complete checkpoints; explicit access/errors retained','batch_receipts':receipts,'clinical_metadata_receipts':metadata,'MCD_schemas':schemas,'IMC':measured('imc'),'TIFF':measured('tiff')};inference,duplicate_audit=unique_imc_for_patient_inference(result['IMC']);result['duplicate_raw_acquisition_audit']=duplicate_audit;ann=src.author_annotations();baseline=next(x['rows'] for x in ann if Path(x['saved']).name=='IMC_sample_annotation.tsv');result['baseline_annotation_receipt']=[{k:v for k,v in x.items() if k!='rows'} for x in ann if Path(x['saved']).name=='IMC_sample_annotation.tsv']
 try:result['patient_analysis']=fixed15(sm.patient_analysis(inference,baseline))
 except Exception as e:result['patient_analysis']={'error_type':type(e).__name__,'error':str(e),'absence_claim':False}
 counts={'IMC_requested_rows':200,'IMC_unique_raw_acquisitions':len({r['clinical']['ROI_ID'] for r in result['IMC']}),'IMC_measured_rows':sum('error' not in x for x in result['IMC']),'TIFF_requested':50,'TIFF_measured':sum('error' not in x for x in result['TIFF']),'TIFF_tiles_requested':450,'TIFF_tiles_measured':sum(len(x.get('tiles',[])) for x in result['TIFF'])};result['coverage']=counts;dest=OUT/'spatial-marker-followthrough-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));summary={'schema':'emc-spatial-checkpoint-merged/1','executed_utc':result['executed_utc'],'coverage':counts,'batch_receipts':receipts,'duplicate_raw_acquisition_audit':duplicate_audit,'patient_analysis':result['patient_analysis'],'IMC_errors':[x for x in result['IMC'] if 'error' in x],'TIFF_errors':[x for x in result['TIFF'] if 'error' in x],'IMC':list(map(sm.compact_measure,result['IMC'])),'TIFF':[x if 'error' in x else {'path':x['path'],'OME_channels':x['OME_channels'],'range_downloaded_bytes':x['range_downloaded_bytes'],'tiles':list(map(sm.compact_measure,x['tiles']))} for x in result['TIFF']],'full_result':str(dest),'full_result_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()};print('EMC_SPATIAL_CHECKPOINT_MERGED_BEGIN');print(json.dumps(sm.clean(summary),allow_nan=False));print('EMC_SPATIAL_CHECKPOINT_MERGED_END')
if __name__=='__main__':main()
