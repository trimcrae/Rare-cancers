import argparse,json,hashlib,re,datetime
from pathlib import Path
import numpy as np
from scipy import ndimage,sparse
from scipy.spatial import cKDTree
from scipy.stats import rankdata
import tifffile
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
import spatial_cellpose_reference_sensitivity_actual as ref
OUT=sm.OUT;OUT.mkdir(parents=True,exist_ok=True);SEED=20261001;PAIRS=[('CD68','CD68'),('HLA-DR','CD68'),('CD68','MRC1'),('CD68','NKX2.2'),('NKX2.2','PSMA3')]
AMENDMENT={'dated_utc':'2026-10-01','trigger':'Declared54tile reference run36889297723 measured41nondegenerate masks and showed threshold/nuclei disagreement; fullfrozenPanel3cohort nuclei replay follows before biological draft','selection':'All26actualPanel3manifestfiles,9fixedgeometric tiles each, samepre-existingcoordinates','settings':ref.AMENDMENT,'model':'Cellpose2.3.2 explicit nuclei,CPU, source-setting replay; version/ROI differences retained, no author classifier/clinicaltruth','marker_specificity':'Computational HLA-DR alias is published source-reportedHLADR channel, anti-HLAII reagent; not independently specific HLA-DR. PSMA3proteasomealpha3,notFOLH1.'}
def measure(mask,stack,names,pixel,label,seed):
 n=int(mask.max());out={'label':label,'pixel_um':pixel,'shape':list(mask.shape),'analyses':[{'threshold_factor':1,'nuclear_components':n,'spatial':[]}],'cellpose_model':'nuclei'};core=out['analyses'][0]
 if n<20:core['reason']='Fewer than20reference nuclearobjects';return out,[]
 ids=np.arange(1,n+1);coords=np.array(ndimage.center_of_mass(np.ones(mask.shape),mask,ids))*pixel;means=np.column_stack([ndimage.mean(np.nan_to_num(stack[:,:,j]),mask,ids) for j in range(len(names))]);path=OUT/(label+'.objects.npz');np.savez_compressed(path,coordinates_um=coords,marker_means=means,marker_labels=np.asarray(names));core['objects_saved']=str(path);ranks=np.column_stack([rankdata(means[:,j],method='average') for j in range(len(names))]);sd=ranks.std(axis=0);z=(ranks-ranks.mean(axis=0))/np.where(sd>0,sd,1);tree=cKDTree(coords);density=tree.query_ball_point(coords,40.,return_length=True);bins=np.minimum(4,(rankdata(density,method='average')/n*5).astype(int));groups=[np.flatnonzero(bins==i) for i in range(5)];rng=np.random.default_rng(seed);comparison=[]
 for radius in [10.,20.,40.]:
  edges=tree.query_pairs(radius,output_type='ndarray');ne=len(edges);r={'radius_um':radius,'undirected_edges':ne};core['spatial'].append(r)
  if not ne:continue
  rows=np.r_[edges[:,0],edges[:,1]];cols=np.r_[edges[:,1],edges[:,0]];graph=sparse.csr_matrix((np.ones(2*ne),(rows,cols)),shape=(n,n));observed=z.T@(graph@z)/(2*ne);unconditional=[];conditional=[]
  for unused in range(99):zp=z[rng.permutation(n)];unconditional.append(zp.T@(graph@zp)/(2*ne))
  for unused in range(199):
   p=np.arange(n)
   for group in groups:p[group]=rng.permutation(group)
   zp=z[p];conditional.append(zp.T@(graph@zp)/(2*ne))
  unconditional=np.asarray(unconditional);conditional=np.asarray(conditional);r['pairs']=[]
  for left,right in PAIRS:
   i=names.index(left);j=names.index(right);raw=float(observed[i,j]);u=unconditional[:,i,j];v=conditional[:,i,j];const=bool(sd[i]==0 or sd[j]==0);r['pairs'].append({'left':left,'right':right,'raw_rank_association':raw,'joint_mark_null_mean':float(u.mean()),'excess_association':float(raw-u.mean()),'null_central95':np.quantile(u,[.025,.975]).tolist(),'exploratory_null_upper_p':float((1+np.sum(u>=raw))/100),'constant_marker':const});comparison.append({'radius_um':radius,'left':left,'right':right,'raw':raw,'original_unconditional_excess':float(raw-u.mean()),'density_conditioned_excess':float(raw-v.mean()),'density_conditioned_upper_p':float((1+np.sum(v>=raw))/200),'constant_marker':const})
 core.update(local_density40um_includes_self_quantiles=np.quantile(density,[0,.25,.5,.75,1]).tolist(),density_bin_counts=[len(g) for g in groups]);return out,comparison
def main():
 p=argparse.ArgumentParser();p.add_argument('--start',type=int,required=True);p.add_argument('--stop',type=int,required=True);a=p.parse_args();assert 0<=a.start<a.stop<=26
 import torch,importlib.metadata
 from cellpose import models
 torch.set_num_threads(2);torch.manual_seed(SEED);np.random.seed(SEED);model=models.CellposeModel(gpu=False,model_type='nuclei',net_avg=False);entries=src.actual_filelists()[2]['metadata'];assert len(entries)==26;dest=OUT/f'ewing-cellpose-batch-{a.start}-{a.stop}.json';result={'schema':'emc-ewing-cellpose-batch/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'range':[a.start,a.stop],'frozen_total':26,'files':[],'density_records':[],'complete':False,'weights':[],'versions':{k:importlib.metadata.version(k) for k in ['numpy','scipy','cellpose','torch']}}
 for path in sorted((OUT/'cellpose-models').rglob('*')):
  if path.is_file():result['weights'].append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 def checkpoint():dest.write_text(json.dumps(sm.clean(result),allow_nan=False))
 checkpoint();aliases={'cd68':'CD68','hla2':'HLA-DR','mrc1':'MRC1','nkx2_2':'NKX2.2','psma3':'PSMA3'}
 for i in range(a.start,a.stop):
  row=entries[i];url='https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/'+row['path'];file={'global_panel3_index':i,'path':row['path'],'manifest_bytes':int(row['size']),'tiles':[]};result['files'].append(file)
  try:
   from spatial_tiff_transport_actual import RetryingRangeFile;rf=RetryingRangeFile(url,row['size'])
   with tifffile.TiffFile(rf) as tf:
    pages=list(tf.pages)
    names,pixel=ref.channels(tf);dna_idx=[j for j,v in enumerate(names) if re.fullmatch(r'(dapi|hoechst|nuclei)',v,re.I)];assert len(dna_idx)==1;dna_idx=dna_idx[0];mi=[j for j,v in enumerate(names) if j!=dna_idx and not re.fullmatch(r'(af|autofluorescence)',v,re.I)];mn=[aliases.get(names[j].lower(),names[j]) for j in mi];assert mn==['CD68','HLA-DR','MRC1','NKX2.2','PSMA3'];p0=pages[0];assert len(pages)==len(names);ny=int(np.ceil(p0.imagelength/p0.tilelength));nx=int(np.ceil(p0.imagewidth/p0.tilewidth));positions=sorted({(round((ny-1)*y),round((nx-1)*x)) for y in [.25,.5,.75] for x in [.25,.5,.75]});assert len(positions)==9;file.update(OME_channels=names,physical_pixel_um=pixel,image_shape=[int(p0.imagelength),int(p0.imagewidth)],tile_shape=[int(p0.tilelength),int(p0.tilewidth)],TIFF_pages=len(pages))
    for tile_i,(yi,xi) in enumerate(positions):
     index=yi*nx+xi;label='Panel3-CellposeNuclei-'+Path(row['path']).stem+f'-grid{yi}-{xi}';tile={'label':label,'tile_row':yi,'tile_column':xi,'segments':[],'analyses':[]};file['tiles'].append(tile);print('EMC_EWING_CELLPOSE_TILE '+str(i)+'/'+str(tile_i)+' '+row['path'],flush=True)
     try:
      planes=[]
      for page in pages:one,receipt=ref.tile(page,index,rf);planes.append(one[:,:,0]);tile['segments'].append(receipt)
      raw=np.stack(planes,axis=2);dna=np.asarray(raw[:,:,dna_idx],np.float32);stack=np.asarray(raw[:,:,mi],np.float32);resized=ndimage.zoom(np.nan_to_num(dna),pixel/.5001,order=1);low,high=np.percentile(resized[::10,::10],[.1,99.8]);tile.update(shape=list(dna.shape),pixel_um=pixel,normalization_percentile_values=[float(low),float(high)])
      if not np.isfinite(low+high) or high<=low:mask=np.zeros(dna.shape,np.int32);tile.update(reference_status='normalization_degenerate',reason='Reference mask not inferred for degenerate fixedROI DNA percentile range; retained in coverage',absence_claim=False)
      else:
       normalized=(resized-low)/(high-low);masks,flows,styles=model.eval(normalized,channels=[0,0],normalize=False,diameter=14,cellprob_threshold=-1,flow_threshold=.7,min_size=15,net_avg=False,tile=True);ys=np.clip(np.rint(np.linspace(0,masks.shape[0]-1,dna.shape[0])).astype(int),0,masks.shape[0]-1);xs=np.clip(np.rint(np.linspace(0,masks.shape[1]-1,dna.shape[1])).astype(int),0,masks.shape[1]-1);mask=ref.filter_mask(masks[np.ix_(ys,xs)],dna,pixel);measured,comparisons=measure(mask,stack,mn,pixel,label,SEED+16000+i*20+tile_i);tile.update(measured);tile['reference_status']='measured';core=tile['analyses'][0];result['density_records'].append({'kind':'Ewing','global_index':1000+i*20+tile_i,'label':label,'status':'measured' if comparisons else 'not_analyzable','nuclear_components':core['nuclear_components'],'comparisons':comparisons,'density_bin_counts':core.get('density_bin_counts')})
      saved=OUT/(label+'.reference_pixels_masks.npz');np.savez_compressed(saved,all_channel_pixels=raw,OME_channels=np.asarray(names),nuclei_mask=mask,mask_inferred=np.asarray(tile['reference_status']=='measured'),physical_pixel_um=np.asarray(pixel));tile.update(pixels_masks_saved=str(saved),pixels_masks_bytes=saved.stat().st_size,pixels_masks_sha256=hashlib.sha256(saved.read_bytes()).hexdigest())
     except Exception as e:tile.update(error_type=type(e).__name__,error=str(e),absence_claim=False)
     checkpoint()
   file.update(range_receipts=rf.receipts,range_downloaded_bytes=rf.downloaded,status='measured')
  except Exception as e:file.update(error_type=type(e).__name__,error=str(e),absence_claim=False,status='error')
  checkpoint()
 result.update(complete=True,requested_files=a.stop-a.start,completed_files=sum(f['status']=='measured' for f in result['files']),requested_tiles=9*(a.stop-a.start),attempted_tiles=sum(len(f['tiles']) for f in result['files']),reference_measured_tiles=sum(t.get('reference_status')=='measured' for f in result['files'] for t in f['tiles']),normalization_degenerate_tiles=sum(t.get('reference_status')=='normalization_degenerate' for f in result['files'] for t in f['tiles']));checkpoint();compact=dict(result);compact['files']=[{**{k:v for k,v in f.items() if k not in ['range_receipts','tiles']},'tiles':f['tiles']} for f in result['files']];compact['full_result']=str(dest);compact['full_result_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();print('EMC_EWING_CELLPOSE_BATCH_BEGIN');print(json.dumps(sm.clean(compact),allow_nan=False));print('EMC_EWING_CELLPOSE_BATCH_END')
if __name__=='__main__':main()
