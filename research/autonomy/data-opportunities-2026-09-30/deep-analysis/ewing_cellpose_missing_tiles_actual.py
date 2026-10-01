import argparse,json,copy,hashlib,datetime,re
from pathlib import Path
import numpy as np
from scipy import ndimage
import tifffile
import spatial_marker_followthrough_actual as sm
import spatial_cellpose_reference_sensitivity_actual as ref
import ewing_cellpose_all_patient_actual as cp
from spatial_tiff_transport_actual import RetryingRangeFile
OUT=sm.OUT;SEED=20261001;OLD_SHA='419eaa6870efe3b793a2a5a0d7acd3e8c4a43fa32bcd1e98a7c257e8e1006c63'
MARKERS=['CD68','HLA-DR','MRC1','NKX2.2','PSMA3'];ALIASES={'cd68':'CD68','hla2':'HLA-DR','mrc1':'MRC1','nkx2_2':'NKX2.2','psma3':'PSMA3'}
def valid(tile):return tile.get('reference_status') in['measured','normalization_degenerate'] and 'pixels_masks_sha256' in tile and 'error' not in tile
def header(tf):
 pages=[p.aspage() if isinstance(p,tifffile.TiffFrame) else p for p in list(tf.pages)];names,pixel=ref.channels(tf);p0=pages[0];dna=[j for j,x in enumerate(names) if re.fullmatch(r'(dapi|hoechst|nuclei)',x,re.I)];mi=[j for j,x in enumerate(names) if j not in dna and not re.fullmatch(r'(af|autofluorescence)',x,re.I)];mn=[ALIASES.get(names[j].lower(),names[j]) for j in mi];details={'OME_channels':names,'physical_pixel_um':pixel,'pages_before_series':len(pages),'samples_per_pixel':int(p0.samplesperpixel),'image_shape':[int(p0.imagelength),int(p0.imagewidth)],'tile_shape':[int(p0.tilelength),int(p0.tilewidth)],'candidate_marker_order':mn,'page_shapes':[list(p.shape) for p in pages]};print('EMC_EWING_FAILED_HEADER '+json.dumps(details),flush=True)
 assert len(dna)==1,'Ambiguous DNA '+str(names);assert len(mn)==5 and len(set(mn))==5 and set(mn)==set(MARKERS),'Unsupported marker identity '+str(mn);mi=[mi[mn.index(m)] for m in MARKERS];assert int(p0.samplesperpixel)==len(names) or len(pages)==len(names),'OME mapping '+json.dumps(details);ny=int(np.ceil(p0.imagelength/p0.tilelength));nx=int(np.ceil(p0.imagewidth/p0.tilewidth));positions=sorted({(round((ny-1)*y),round((nx-1)*x)) for y in[.25,.5,.75] for x in[.25,.5,.75]});assert positions and len(positions)<=9;details.update(tile_grid=[ny,nx],expected_coordinate_requests=9,unique_coordinate_positions=len(positions),collapsed_coordinate_requests=9-len(positions));return pages,names,pixel,dna[0],mi,nx,positions,details
def main():
 p=argparse.ArgumentParser();p.add_argument('--input-root',action='append');a=p.parse_args();roots=[Path(x) for x in (a.input_root or ['restored-artifacts'])];paths=sorted({p for root in roots for p in root.rglob('ewing-cellpose-batch-7-14.json')});assert paths;assert all(hashlib.sha256(p.read_bytes()).hexdigest()==OLD_SHA for p in paths),'Wrong old checkpoint';old=json.loads(paths[0].read_bytes());assert old['schema']=='emc-ewing-cellpose-batch/1' and old['complete'];result=copy.deepcopy(old);result.update(complete=False,executed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repair_replaces_original_batch_sha256=OLD_SHA,repair_source={'saved':str(paths[0]),'sha256':OLD_SHA},repair_amendment={'dated_utc':'2026-10-01','selection':'Only missing fixed tiles cases32/35/36; retain measured masks/pixels; exact sourceposition formula','technical_fixes':'Fullpages before series, strict3attempt range, exactmarker reorder, collapsedcoordinate audit','no_selection_by_results':True});OUT.mkdir(parents=True,exist_ok=True);dest=OUT/'ewing-cellpose-batch-7-14-repaired.json'
 def checkpoint():dest.write_text(json.dumps(sm.clean(result),allow_nan=False))
 checkpoint()
 import torch
 from cellpose import models
 torch.set_num_threads(2);torch.manual_seed(SEED);np.random.seed(SEED);model=models.CellposeModel(gpu=False,model_type='nuclei',net_avg=False);weights=[p for p in (OUT/'cellpose-models').rglob('nucleitorch_0') if p.is_file()];assert weights and all(hashlib.sha256(p.read_bytes()).hexdigest()=='89ca45e4a45048d5010d29621466b1274b91b3dcb9714dce9f9e90a9a8671303' for p in weights)
 for file in result['files']:
  i=file['global_panel3_index']
  if i not in[7,8,9]:continue
  retained={(t['tile_row'],t['tile_column']):t for t in file['tiles'] if valid(t)};failed_old=[t for t in file['tiles'] if not valid(t)];file['original_failed_tile_receipts']=failed_old;file['original_file_error']={k:file[k] for k in['error_type','error'] if k in file};url='https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/'+file['path'];rf=RetryingRangeFile(url,file['manifest_bytes'])
  try:
   with tifffile.TiffFile(rf) as tf:
    pages,names,pixel,dna_idx,mi,nx,positions,details=header(tf);file['repair_header']=details;assert set(retained)<=set(positions),'Valid tiles outside frozen grid';file.update(OME_channels=names,physical_pixel_um=pixel);file['tiles']=[]
    for tile_i,(y,x) in enumerate(positions):
     if (y,x) in retained:file['tiles'].append(retained[(y,x)]);continue
     label='Panel3-CellposeNuclei-'+Path(file['path']).stem+f'-grid{y}-{x}';tile={'label':label,'tile_row':y,'tile_column':x,'segments':[],'analyses':[]};file['tiles'].append(tile);print('EMC_EWING_CELLPOSE_REPAIR_TILE '+str(i)+'/'+str(tile_i)+' '+file['path'],flush=True)
     try:
      segment=y*nx+x
      if int(pages[0].samplesperpixel)==len(names):raw,r=ref.tile(pages[0],segment,rf);tile['segments'].append(r)
      else:
       planes=[]
       for page in pages:one,r=ref.tile(page,segment,rf);planes.append(one[:,:,0]);tile['segments'].append(r)
       raw=np.stack(planes,axis=2)
      dna=np.asarray(raw[:,:,dna_idx],np.float32);stack=np.asarray(raw[:,:,mi],np.float32);resized=ndimage.zoom(np.nan_to_num(dna),pixel/.5001,order=1);low,high=np.percentile(resized[::10,::10],[.1,99.8]);tile.update(shape=list(dna.shape),pixel_um=pixel,normalization_percentile_values=[float(low),float(high)])
      if not np.isfinite(low+high) or high<=low:mask=np.zeros(dna.shape,np.int32);tile.update(reference_status='normalization_degenerate',reason='Degenerate fixedROI DNA normalization; retained coverage',absence_claim=False)
      else:
       normalized=(resized-low)/(high-low);masks,flows,styles=model.eval(normalized,channels=[0,0],normalize=False,diameter=14,cellprob_threshold=-1,flow_threshold=.7,min_size=15,net_avg=False,tile=True);ys=np.clip(np.rint(np.linspace(0,masks.shape[0]-1,dna.shape[0])).astype(int),0,masks.shape[0]-1);xs=np.clip(np.rint(np.linspace(0,masks.shape[1]-1,dna.shape[1])).astype(int),0,masks.shape[1]-1);mask=ref.filter_mask(masks[np.ix_(ys,xs)],dna,pixel);measured,comparisons=cp.measure(mask,stack,MARKERS,pixel,label,SEED+16000+i*20+tile_i);tile.update(measured);tile['reference_status']='measured';core=tile['analyses'][0];result['density_records']=[r for r in result['density_records'] if r['label']!=label];result['density_records'].append({'kind':'Ewing','global_index':1000+i*20+tile_i,'label':label,'status':'measured' if comparisons else 'not_analyzable','nuclear_components':core['nuclear_components'],'comparisons':comparisons,'density_bin_counts':core.get('density_bin_counts')})
      path=OUT/(label+'.reference_pixels_masks.npz');np.savez_compressed(path,all_channel_pixels=raw,OME_channels=np.asarray(names),nuclei_mask=mask,mask_inferred=np.asarray(tile['reference_status']=='measured'),physical_pixel_um=np.asarray(pixel));tile.update(pixels_masks_saved=str(path),pixels_masks_bytes=path.stat().st_size,pixels_masks_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
     except Exception as exc:tile.update(error_type=type(exc).__name__,error=str(exc),absence_claim=False)
     checkpoint()
   file.update(status='measured',repair_range_receipts=rf.receipts,repair_range_downloaded_bytes=rf.downloaded)
   for key in['error_type','error']:file.pop(key,None)
  except Exception as exc:file.update(status='error',error_type=type(exc).__name__,error=str(exc),absence_claim=False,repair_range_receipts=rf.receipts,repair_range_downloaded_bytes=rf.downloaded)
  checkpoint()
 result.update(complete=True,requested_files=7,completed_files=sum(f['status']=='measured' for f in result['files']),requested_tiles=63,attempted_tiles=sum(len(f['tiles']) for f in result['files']),reference_measured_tiles=sum(t.get('reference_status')=='measured' for f in result['files'] for t in f['tiles']),normalization_degenerate_tiles=sum(t.get('reference_status')=='normalization_degenerate' for f in result['files'] for t in f['tiles']),tile_errors=sum('error' in t for f in result['files'] for t in f['tiles']));checkpoint();summary={k:v for k,v in result.items() if k not in['density_records','files']};summary['files']=[{k:v for k,v in f.items() if k not in['range_receipts','repair_range_receipts']} for f in result['files']];summary.update(full_result=str(dest),full_result_sha256=hashlib.sha256(dest.read_bytes()).hexdigest());print('EMC_EWING_CELLPOSE_MISSING_REPAIR_BEGIN');print(json.dumps(sm.clean(summary),allow_nan=False));print('EMC_EWING_CELLPOSE_MISSING_REPAIR_END')
if __name__=='__main__':main()
