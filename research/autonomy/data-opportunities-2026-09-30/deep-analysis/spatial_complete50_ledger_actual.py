import json,hashlib,copy,datetime,collections
from pathlib import Path
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT
ROOTS=[Path('restored-artifacts'),Path('restored-artifacts-extra'),Path('restored-artifacts-third'),OUT]
P2={3,4,5,6,8,9,18}
def rec(p):
 b=p.read_bytes();return {'saved':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def main():
 OUT.mkdir(parents=True,exist_ok=True);sources=[]
 for p in sorted({p for root in ROOTS for p in root.rglob('spatial-marker-followthrough-actual.json')}):
  d=json.loads(p.read_bytes())
  if d.get('schema')=='emc-spatial-marker-followthrough/1' and len(d.get('TIFF',[]))==50 and len(d.get('IMC',[]))==200:sources.append((p,d))
 assert sources,'Restore original complete50 request/full threshold source'
 assert len({rec(p)['sha256'] for p,d in sources})==1,'Conflicting original complete source'
 original_path,original=sources[0];selected={};owners={};initial_errors=[];initial_measured=[]
 for i,v in enumerate(original['TIFF']):
  assert v.get('path')
  if 'error' in v:r={'global_index':i,'status':'error',**copy.deepcopy(v)};initial_errors.append({'global_index':i,'source_receipt':rec(original_path),'scientific_error':copy.deepcopy(v)})
  else:r={'global_index':i,'status':'measured','result':copy.deepcopy(v)};initial_measured.append(i)
  selected[i]=r;owners[i]=rec(original_path)
 assert set(initial_measured)==set(range(24))-P2 and {x['global_index'] for x in initial_errors}==P2|set(range(24,50))
 batches=[];replacements=[];same=[]
 paths=sorted({p for root in ROOTS for p in root.rglob('spatial-followthrough-batch-tiff-*.json')})
 for p in paths:
  d=json.loads(p.read_bytes());assert d['schema']=='emc-spatial-followthrough-batch/1' and d['mode']=='tiff' and d['complete'] and d['frozen_total']==50
  a,b=d['range'];assert {r['global_index'] for r in d['records']}==set(range(a,b));receipt=rec(p);batches.append({**receipt,'range':d['range'],'requested':d['requested'],'measured':d['measured'],'errors':d['errors'],'repair_amendment':d.get('repair_amendment')})
  for r in d['records']:
   i=r['global_index'];assert 0<=i<50;old=selected[i];oldpath=old['result']['path'] if old['status']=='measured' else old['path'];newpath=r['result']['path'] if r['status']=='measured' else r['path'];assert oldpath==newpath,'Frozen source path changed'
   if r['status']=='measured':
    assert len(r['result']['tiles'])==9 and all('error' not in t for t in r['result']['tiles'])
    if old['status']=='measured':assert canonical(old['result'])==canonical(r['result']),'Conflicting measured duplicate';same.append({'global_index':i,'receipt':receipt})
    else:
     assert i in P2 or 24<=i<50
     replacements.append({'global_index':i,'frozen_path':newpath,'previous_source':owners[i],'previous_error':copy.deepcopy(old),'successful_source':receipt});selected[i]=copy.deepcopy(r);owners[i]=receipt
 assert set(selected)==set(range(50)) and all(r['status']=='measured' for r in selected.values()),'Unresolved finite source errors'
 assert {r['global_index'] for r in replacements}==P2|set(range(24,50))
 for i in initial_measured:assert canonical(selected[i]['result'])==canonical(original['TIFF'][i]),'Original successful source changed'
 files=[selected[i]['result'] for i in range(50)];assert len({v['path'] for v in files})==50 and sum(len(v['tiles']) for v in files)==450
 audit=[];factor_counts=collections.Counter();unanalysable=[]
 for i,f in enumerate(files):
  assert len({(t['tile_row'],t['tile_column']) for t in f['tiles']})==9;ts=[]
  for t in f['tiles']:
   aa=t.get('analyses',[]);factors=[float(v['threshold_factor']) for v in aa]
   if aa:assert factors==[.8,1.,1.2],'Full frozen three-factor analyses required'
   else:assert t.get('reason'),'Blank/unanalysable tile requires source reason';unanalysable.append({'global_index':i,'path':f['path'],'label':t['label'],'reason':t['reason']})
   for a in aa:factor_counts[str(a['threshold_factor'])]+=1
   ts.append({'label':t['label'],'tile_row':t['tile_row'],'tile_column':t['tile_column'],'shape':t.get('shape'),'pixel_um':t.get('pixel_um'),'DNA_threshold':t.get('DNA_threshold'),'DNA_nonzero_fraction':t.get('DNA_nonzero_fraction'),'reason':t.get('reason'),'analyses':[{'threshold_factor':a['threshold_factor'],'nuclear_components':a['nuclear_components'],'reason':a.get('reason'),'spatial_neighbor_counts':[{'radius_um':v['radius_um'],'undirected_edges':v['undirected_edges']} for v in a.get('spatial',[])]} for a in aa]})
  audit.append({'global_index':i,'panel':'Panel2' if i<24 else'Panel3','path':f['path'],'OME_channels':f['OME_channels'],'source_receipt':owners[i],'fixed_tiles':len(f['tiles']),'tiles':ts})
 result=copy.deepcopy(original);result.update(executed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),TIFF=files,completion_method='Original full source plus only seven P2 transport repairs and26P3 frozen-pixel threshold replays; all50/450acquired; no pixel/model rerun',complete50_source_assembly={'original_source_receipt':rec(original_path),'native_checkpoint_receipts':batches,'all_initial_errors_preserved':initial_errors,'exact_error_supersessions':replacements,'identical_measured_duplicates':same,'all_original_successes_preserved':True,'all50_source_receipts':owners});dest=OUT/'spatial-marker-followthrough-complete50-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));summary={'schema':'emc-spatial-complete50-ledger/1','executed_utc':result['executed_utc'],'coverage':{'frozen_files':50,'measured_files':50,'Panel2_files':24,'Panel3_files':26,'fixed_tiles':450,'initial_successes':17,'initial_errors':33,'exact_errors_repaired':33,'remaining_errors':0,'threshold_factor_tile_counts':dict(factor_counts),'tiles_without_finite_DNA_threshold':len(unanalysable)},'original_source_receipt':rec(original_path),'native_checkpoint_receipts':batches,'exact_error_supersessions':replacements,'all_original_successes_preserved':True,'all50_file_and450_tile_audit':audit,'unanalysable_DNA_threshold_tiles':unanalysable,'full_scientific_source':rec(dest),'limits':'Panel2 genericOpal channels retained; no invented marker/cell identity. This complete raw-threshold sourceledger is not independent26case Cellpose/sourcecluster inference. OriginalIMCpatientanalysis inherited, notrerun.'};p=OUT/'spatial-complete50-ledger-actual.json';p.write_text(json.dumps(sm.clean(summary),allow_nan=False));print('EMC_SPATIAL_COMPLETE50_LEDGER_BEGIN');print(json.dumps(sm.clean(summary),allow_nan=False));print('EMC_SPATIAL_COMPLETE50_LEDGER_END');print('EMC_SPATIAL_COMPLETE50_SOURCE_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False,separators=(',',':')));print('EMC_SPATIAL_COMPLETE50_SOURCE_END')
if __name__=='__main__':main()
