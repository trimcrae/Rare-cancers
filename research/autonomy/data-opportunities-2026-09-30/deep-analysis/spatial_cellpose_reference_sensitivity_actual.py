import os,io,json,hashlib,re,datetime,urllib.request,collections
from pathlib import Path
import numpy as np
from scipy import ndimage,sparse
from scipy.spatial import cKDTree
from scipy.stats import rankdata
import tifffile
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
OUT=sm.OUT;OUT.mkdir(parents=True,exist_ok=True)
os.environ['CELLPOSE_LOCAL_MODELS_PATH']=str(OUT/'cellpose-models')
SEED=20261001;FILES=['EWS02a.tif','EWS09a.tif','EWS101a.tif'];GRID=[.25,.5,.75]
AMENDMENT={'dated_utc':'2026-10-01','fixed_subset':FILES,'n_panels':2,'n_tiles':54,'source_groovy_blob':'b24dfb51b96d6f0599427f9233add2162f7fc540','cellpose_version':'2.3.2','source_settings':{'diameter_pixels':14,'cellprob_threshold':-1,'flow_threshold':.7,'pixel_um':.5001,'normalization_percentiles':[.1,99.8],'normalization_downsample':10,'max_nucleus_um2':180,'positive_DNA_mean':True},'model_ambiguity':'Source calls nuc; explicit nuclei primary and cyto sensitivity do not establish which author runtime model was used.','normalization':'Each fixed tile is our ROI; nearest-grid downsample10 approximates QuPath ROI readRegion interpolation.','limit':'Mask/count/continuous geometry agreement; no author classifier, expanded compartments, cell phenotype or clinical truth replay.'}
class RangeFile(io.RawIOBase):
 def __init__(self,url,size):self.url=url;self.size=int(size);self.pos=0;self.cache=collections.OrderedDict();self.receipts=[];self.downloaded=0
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,offset,whence=0):
  self.pos=int(offset if whence==0 else self.pos+offset if whence==1 else self.size+offset)
  if self.pos<0:raise ValueError('Negative seek')
  return self.pos
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  n=min(n,self.size-self.pos)
  if n<=0:return b''
  if n>8*1024**2:raise RuntimeError('Single read exceeds bounded range cap')
  out=[];end=self.pos+n;block=1024**2
  while self.pos<end:
   k=self.pos//block
   if k not in self.cache:
    a=k*block;b=min(self.size-1,a+block-1)
    if self.downloaded+b-a+1>512*1024**2:raise RuntimeError('Per-file range budget exceeded')
    req=urllib.request.Request(self.url,headers={'Range':f'bytes={a}-{b}','User-Agent':'EMC-published-data-reanalysis/1'})
    with urllib.request.urlopen(req,timeout=120) as r:
     status=r.status;content_range=r.headers.get('Content-Range');body=r.read(b-a+2)
     if status!=206 or len(body)!=b-a+1:raise RuntimeError(f'Range not exact: status={status}, bytes={len(body)}, requested={a}:{b}')
     if content_range!=f'bytes {a}-{b}/{self.size}':raise RuntimeError(f'Content-Range mismatch: {content_range}')
     self.receipts.append({'start':a,'stop_inclusive':b,'bytes':len(body),'status':status,'final_url':r.url,'sha256':hashlib.sha256(body).hexdigest()})
    self.downloaded+=len(body);self.cache[k]=body
    while len(self.cache)>32:self.cache.popitem(last=False)
   q=self.pos-k*block;take=min(end-self.pos,len(self.cache[k])-q);out.append(self.cache[k][q:q+take]);self.pos+=take
  return b''.join(out)
 def readinto(self,b):raw=self.read(len(b));b[:len(raw)]=raw;return len(raw)
def channels(tf):
 import xml.etree.ElementTree as ET
 root=ET.fromstring(tf.ome_metadata);px=next(x for x in root.iter() if x.tag.split('}')[-1]=='Pixels');ch=[x.attrib.get('Name',x.attrib.get('ID','')) for x in px if x.tag.split('}')[-1]=='Channel'];return ch,float(px.attrib['PhysicalSizeX'])
def tile(page,index,rf):
 a=int(page.dataoffsets[index]);n=int(page.databytecounts[index]);rf.seek(a);raw=rf.read(n);decoded=page.decode(raw,index,jpegtables=page.jpegtables)[0]
 x=np.squeeze(decoded)
 if x.ndim==2:x=x[:,:,None]
 if x.ndim!=3:raise RuntimeError('Unexpected decoded segment shape '+str(x.shape))
 return x,{'offset':a,'bytes':n,'sha256':hashlib.sha256(raw).hexdigest()}
def original_mask(dna,pixel,factor):
 x=ndimage.gaussian_filter(np.maximum(np.nan_to_num(dna),0),1/pixel);threshold=sm.otsu(x)
 if threshold is None:return np.zeros(dna.shape,np.int32)
 labels,n=ndimage.label(x>threshold*factor);counts=np.bincount(labels.ravel());keep=(counts*pixel**2>=6)&(counts*pixel**2<=250);keep[0]=False;out=np.zeros(n+1,np.int32);out[np.flatnonzero(keep)]=np.arange(1,int(keep.sum())+1);return out[labels]
def filter_mask(mask,dna,pixel):
 ids=np.unique(mask);ids=ids[ids>0];result=np.zeros(mask.shape,np.int32);next_id=0
 for i in ids:
  sel=mask==i
  if sel.sum()*pixel**2<=180 and float(dna[sel].mean())>0:next_id+=1;result[sel]=next_id
 return result
def agreement(a,b):
 na=int(a.max());nb=int(b.max());fa=a>0;fb=b>0;den=fa.sum()+fb.sum();dice=2*(fa&fb).sum()/den if den else None;both=fa&fb
 if not both.any():return {'n_original':na,'n_reference':nb,'foreground_dice':dice,'matched_IoU_05':0,'fraction_original_matched':0 if na else None,'fraction_reference_matched':0 if nb else None}
 codes=a[both].astype(np.int64)*(nb+1)+b[both];u,c=np.unique(codes,return_counts=True);ia=u//(nb+1);ib=u%(nb+1);ca=np.bincount(a.ravel());cb=np.bincount(b.ravel());iou=c/(ca[ia]+cb[ib]-c);order=np.argsort(-iou);ua=set();ub=set();matches=[]
 for k in order:
  if iou[k]<.5:break
  i=int(ia[k]);j=int(ib[k])
  if i not in ua and j not in ub:ua.add(i);ub.add(j);matches.append(float(iou[k]))
 return {'n_original':na,'n_reference':nb,'foreground_dice':dice,'matched_IoU_05':len(matches),'fraction_original_matched':len(matches)/na if na else None,'fraction_reference_matched':len(matches)/nb if nb else None,'matched_iou_median':float(np.median(matches)) if matches else None}
def geometry(mask,stack,names,pixel):
 n=int(mask.max());ids=np.arange(1,n+1)
 if n<3:return {'nuclear_components':n,'pairs':[]}
 yx=np.asarray(ndimage.center_of_mass(np.ones(mask.shape),mask,ids));coords=yx[:,::-1]*pixel;means=np.column_stack([ndimage.mean(stack[:,:,j],mask,ids) for j in range(len(names))]);z=np.column_stack([rankdata(means[:,j]) for j in range(len(names))]);z-=z.mean(axis=0);sd=z.std(axis=0);z=np.divide(z,sd,out=np.zeros_like(z),where=sd>0);tree=cKDTree(coords);pairs=[('CD68','CD68'),('HLA-DR','CD68'),('CD68','MRC1'),('CD68','NKX2.2'),('NKX2.2','PSMA3')] if 'CD68' in names else [(v,v) for v in names];out=[]
 for radius in [10,20,40]:
  edges=tree.query_pairs(radius,output_type='ndarray');ne=len(edges)
  for left,right in pairs:
   if left not in names or right not in names:continue
   i=names.index(left);j=names.index(right);value=float(np.sum(z[edges[:,0],i]*z[edges[:,1],j]+z[edges[:,1],i]*z[edges[:,0],j])/(2*ne)) if ne else None;out.append({'left':left,'right':right,'radius_um':radius,'n_edges':ne,'rank_neighbor_covariance':value,'constant_marker':bool(sd[i]==0 or sd[j]==0)})
 return {'nuclear_components':n,'pairs':out}
def main():
 import torch,importlib.metadata
 from cellpose import models
 torch.set_num_threads(2);torch.manual_seed(SEED);np.random.seed(SEED);cp={name:models.CellposeModel(gpu=False,model_type=name,net_avg=False) for name in ['nuclei','cyto']};dest=OUT/'spatial-cellpose-reference-sensitivity-actual.json';result={'schema':'emc-spatial-cellpose-reference-sensitivity/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'versions':{k:importlib.metadata.version(k) for k in ['numpy','scipy','tifffile','cellpose','torch']},'weights':[],'files':[],'tiles':[],'complete':False}
 for path in sorted((OUT/'cellpose-models').rglob('*')):
  if path.is_file():result['weights'].append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 def checkpoint():dest.write_text(json.dumps(sm.clean(result),allow_nan=False))
 checkpoint();lists=src.actual_filelists();panels=[('Panel2',lists[1]['metadata']),('Panel3',lists[2]['metadata'])];aliases={'cd68':'CD68','hla2':'HLA-DR','mrc1':'MRC1','nkx2_2':'NKX2.2','psma3':'PSMA3'}
 for panel,entries in panels:
  for filename in FILES:
   selected=[r for r in entries if Path(r['path']).name.lower()==filename.lower()];file_result={'panel':panel,'filename':filename,'planned_tiles':9}
   try:
    if len(selected)!=1:raise RuntimeError('Frozen file missing or ambiguous: '+filename)
    row=selected[0];url='https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/'+row['path'];rf=RangeFile(url,row['size']);file_result.update(url=url,bytes=int(row['size']))
    with tifffile.TiffFile(rf) as tf:
     names,pixel=channels(tf);dna_indices=[i for i,v in enumerate(names) if re.fullmatch(r'(dapi|hoechst|nuclei)',v,re.I)]
     if len(dna_indices)!=1:raise RuntimeError('DNA channel ambiguous: '+str(names))
     dna_idx=dna_indices[0];marker_idx=[i for i,v in enumerate(names) if i!=dna_idx and not re.fullmatch(r'(af|autofluorescence)',v,re.I)];marker_names=[aliases.get(names[i].lower(),names[i]) for i in marker_idx];p0=tf.pages[0];ny=int(np.ceil(p0.imagelength/p0.tilelength));nx=int(np.ceil(p0.imagewidth/p0.tilewidth));file_result.update(OME_channels=names,pixel_um=pixel,image_shape=[int(p0.imagelength),int(p0.imagewidth)],tile_shape=[int(p0.tilelength),int(p0.tilewidth)])
     for gy in GRID:
      for gx in GRID:
       yi=round((ny-1)*gy);xi=round((nx-1)*gx);idx=yi*nx+xi;rec={'panel':panel,'filename':filename,'grid':[gy,gx],'tile_row':yi,'tile_column':xi,'tile_index':idx,'segments':[],'models':{}}
       print('EMC_CELLPOSE_TILE '+panel+' '+filename+' '+str([gy,gx]),flush=True)
       try:
        if int(p0.samplesperpixel)==len(names):raw,receipt=tile(p0,idx,rf);rec['segments'].append(receipt)
        elif len(tf.pages)==len(names):
         planes=[]
         for page in tf.pages:one,receipt=tile(page,idx,rf);planes.append(one[:,:,0]);rec['segments'].append(receipt)
         raw=np.stack(planes,axis=2)
        else:raise RuntimeError('OME channels do not map one-to-one to TIFF samples/pages')
        dna=np.asarray(raw[:,:,dna_idx],np.float32);stack=np.asarray(raw[:,:,marker_idx],np.float32);original={str(f):original_mask(dna,pixel,f) for f in [.8,1.,1.2]};rec.update(original={k:geometry(v,stack,marker_names,pixel) for k,v in original.items()},marker_labels=marker_names);saved={'DNA':dna,'marker_pixels':stack,'marker_labels':np.asarray(marker_names),'original_08':original['0.8'],'original_10':original['1.0'],'original_12':original['1.2']};resized=ndimage.zoom(dna,pixel/.5001,order=1);low,high=np.percentile(resized[::10,::10],[.1,99.8]);rec['normalization_percentile_values']=[float(low),float(high)]
        if not np.isfinite(low+high) or high<=low:raise RuntimeError('Degenerate ROI DNA normalization')
        normalized=(resized-low)/(high-low)
        for model_name,model in cp.items():
         try:
          masks,flows,styles=model.eval(normalized,channels=[0,0],normalize=False,diameter=14,cellprob_threshold=-1,flow_threshold=.7,min_size=15,net_avg=False,tile=True);ys=np.clip(np.rint(np.linspace(0,masks.shape[0]-1,dna.shape[0])).astype(int),0,masks.shape[0]-1);xs=np.clip(np.rint(np.linspace(0,masks.shape[1]-1,dna.shape[1])).astype(int),0,masks.shape[1]-1);mapped=masks[np.ix_(ys,xs)];filtered=filter_mask(mapped,dna,pixel);saved[model_name+'_mask']=filtered;rec['models'][model_name]={'status':'measured','unfiltered_components':int(np.unique(mapped[mapped>0]).size),'geometry':geometry(filtered,stack,marker_names,pixel),'threshold_agreement':{k:agreement(v,filtered) for k,v in original.items()}}
         except Exception as e:rec['models'][model_name]={'status':'error','error_type':type(e).__name__,'error':str(e),'absence_claim':False}
        npz=OUT/f'{panel}-{Path(filename).stem}-grid{yi}-{xi}.reference_pixels_masks.npz';np.savez_compressed(npz,**saved);rec.update(status='measured',pixels_masks_saved=str(npz),pixels_masks_sha256=hashlib.sha256(npz.read_bytes()).hexdigest(),pixels_masks_bytes=npz.stat().st_size)
       except Exception as e:rec.update(status='error',error_type=type(e).__name__,error=str(e),absence_claim=False)
       result['tiles'].append(rec);checkpoint()
    file_result.update(status='measured',range_downloaded_bytes=rf.downloaded,range_receipts=rf.receipts)
   except Exception as e:file_result.update(status='error',error_type=type(e).__name__,error=str(e),absence_claim=False)
   result['files'].append(file_result);checkpoint()
 result.update(complete=True,planned_tiles=54,attempted_tiles=len(result['tiles']),measured_tiles=sum(r['status']=='measured' for r in result['tiles']),reference_model_successes={name:sum(r.get('models',{}).get(name,{}).get('status')=='measured' for r in result['tiles']) for name in cp});checkpoint();compact=dict(result);compact['files']=[{k:v for k,v in r.items() if k!='range_receipts'} for r in result['files']];compact['full_result']=str(dest);compact['full_result_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();print('EMC_SPATIAL_CELLPOSE_REFERENCE_BEGIN');print(json.dumps(sm.clean(compact),allow_nan=False));print('EMC_SPATIAL_CELLPOSE_REFERENCE_END')
if __name__=='__main__':main()
