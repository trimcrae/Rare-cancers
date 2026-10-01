import argparse,json,hashlib,datetime,re
from pathlib import Path
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
import mcd_partial_access as mcd
SEED=20261001;OUT=sm.OUT;OUT.mkdir(parents=True,exist_ok=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['imc','tiff'],required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--stop',type=int,required=True);p.add_argument('--resume-json');a=p.parse_args();lists=src.actual_filelists();clinical=[];schemas={};metadata=None
 if a.mode=='imc':
  metadata=src.imc_metadata();assert metadata['sha256']=='966a15b9eddd7457a3792fff225c858e9899545cf0098e9b6b0512c16a541ab8';t=metadata['tables'][0];header=t['rows'][0];clinical=[dict(zip(header,r+[None]*(len(header)-len(r)))) for r in t['rows'][1:]];items=clinical
 else:items=[r for x in lists[1:] for r in x['metadata']]
 assert 0<=a.start<a.stop<=len(items);name=f'spatial-followthrough-batch-{a.mode}-{a.start}-{a.stop}.json';dest=OUT/name;result={'schema':'emc-spatial-followthrough-batch/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initial_run':36879244424,'mode':a.mode,'range':[a.start,a.stop],'frozen_total':len(items),'measurement_amendment':sm.AMENDMENT,'records':[],'complete':False,'scientific_limit':'Partialbatch; allbatchrecords mustmerge before patientinference'}
 if a.resume_json:
  old=json.loads(Path(a.resume_json).read_text());assert old['schema']==result['schema'] and old['mode']==a.mode and old['range']==result['range'];result['records']=old['records'];result['resume_source_sha256']=hashlib.sha256(Path(a.resume_json).read_bytes()).hexdigest()
 done={x['global_index'] for x in result['records']};assert len(done)==len(result['records']) and done<=set(range(a.start,a.stop))
 if metadata:result['clinical_metadata_receipt']={k:v for k,v in metadata.items() if k!='tables'}
 if a.mode=='imc':
  needed={re.fullmatch(r'((?:MFS|USTS)_TMA_[12])_ROI\d+',items[i]['ROI_ID']).group(1)+'.mcd' for i in range(a.start,a.stop) if i not in done};result['schemas']=[]
  for name,size in mcd.FILES:
   if name in needed:url,ac,ch,receipt=sm.mcd_schema(name,size);schemas[name]=(url,size,ac,ch);result['schemas'].append(receipt)
 for i in range(a.start,a.stop):
  if i in done:continue
  row=items[i];print('EMC_SPATIAL_BATCH '+a.mode+' '+str(i)+'/'+str(len(items)),flush=True)
  try:
   measured=sm.imc_one(row,schemas,SEED+i) if a.mode=='imc' else sm.tiff_file(row,SEED+1000+i*20);record={'global_index':i,'status':'measured','result':measured}
  except Exception as e:record={'global_index':i,'status':'error','clinical':row if a.mode=='imc' else None,'path':row.get('path'),'error_type':type(e).__name__,'error':str(e),'absence_claim':False}
  result['records'].append(record);dest.write_text(json.dumps(sm.clean(result),allow_nan=False))
 result['records'].sort(key=lambda x:x['global_index']);result.update(complete=True,requested=a.stop-a.start,measured=sum(x['status']=='measured' for x in result['records']),errors=sum(x['status']=='error' for x in result['records']));dest.write_text(json.dumps(sm.clean(result),allow_nan=False));summary={k:v for k,v in result.items() if k not in['records','schemas','clinical_metadata_receipt']};summary['records']=[{'global_index':r['global_index'],'status':r['status'],'summary':sm.compact_measure(r['result']) if a.mode=='imc' and r['status']=='measured' else {'path':r['result']['path'],'OME_channels':r['result']['OME_channels'],'range_downloaded_bytes':r['result']['range_downloaded_bytes'],'tiles':list(map(sm.compact_measure,r['result']['tiles']))} if r['status']=='measured' else r} for r in result['records']];summary.update(full_result=str(dest),full_result_sha256=hashlib.sha256(dest.read_bytes()).hexdigest());print('EMC_SPATIAL_BATCH_BEGIN');print(json.dumps(sm.clean(summary),allow_nan=False));print('EMC_SPATIAL_BATCH_END')
if __name__=='__main__':main()
