import io,json,hashlib,datetime,urllib.request,urllib.parse,zipfile,xml.etree.ElementTree as ET,re,collections,traceback
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import ndimage,stats,sparse
from scipy.spatial import cKDTree
import tifffile
import mcd_partial_access as mcd
import tiff_partial_access as tpa
import scientific_source_access_followthrough as src
BASE=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis');OUT=BASE/'outputs';OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001;RADII=[10.,20.,40.];FACTORS=[.8,1.,1.2];NULL=99;MARKERS=['CD3','CD8a','CD68','CD163','HLA-DR']
PAIRS=[('CD3','CD3'),('CD68','CD68'),('CD3','CD68'),('CD8a','CD163'),('HLA-DR','CD68')]
AMENDMENT={'dated_utc':'2026-10-01','prior_access_run':36874318874,'selection_before_new_pixel_values':'All clinical-workbook IMC ROI IDs, central128 contiguous raster rows; all exact Panel2/3filelists,9fixedgeometric tiles at normalized .25,.5,.75 positions','parser_fix':'MCD inclusive endpoints carry one surplus byte; records use floor((end-start+1)/208), assert remainder in[0,1]; only exact trailing one byte excluded','segmentation':'Exploratory DNA threshold connected components, Gaussian1um; object area6..250um2; mean marker in nuclear mask; threshold factors0.8/1/1.2','null':'99 joint marker-row permutations per ROI, fixed nuclei coordinates; preserves density and within-object coexpression','endpoints':'Continuous marker rank auto/cross-association at10/20/40um; no negative-marker tumor labels or macrophage/Tcell identity proof','unit':'MeanROI withinL_ID+location then equal meanlocation withinL_ID; clinical patient aggregation; splitROIs never independent inference units','inference':'Five fixed marker pairs x3radii; allreported, BH across15primary histology comparisons; threshold sensitivity descriptive; no survival/clinicalbenefit fit','sampling_limit':'Central strips/geometric tiles can miss tissue; coverage/nuclear counts reported; no whole-slide extrapolation','validation_limit':'Segmentation and marker measurements require comparison to author segmentation before biological publication claim'}
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,np.generic):return clean(x.item())
 if isinstance(x,float) and not np.isfinite(x):return None
 return x
def getfull(url,label,cap=256*1024*1024):
 req=urllib.request.Request(url,headers={'User-Agent':'EMC-public-data-reanalysis/1','Accept-Encoding':'identity'});path=OUT/label;h=hashlib.sha256();n=0
 with urllib.request.urlopen(req,timeout=90) as r,path.open('wb') as f:
  rec={'url':url,'final_url':r.geturl(),'http_status':r.status,'Content_Length':r.headers.get('Content-Length')}
  while True:
   b=r.read(1024*1024)
   if not b:break
   n+=len(b)
   if n>cap:raise RuntimeError('Explicit finite source cap exceeded; not absence')
   h.update(b);f.write(b)
 rec.update(bytes=n,sha256=h.hexdigest(),saved=str(path));return path,rec
def otsu(a):
 good=a[np.isfinite(a)];positive=good[good>0]
 if len(positive)<20:return None
 high=float(np.quantile(positive,.999));hist,edges=np.histogram(np.clip(good,0,high),bins=256,range=(0,high));p=hist.astype(float)/hist.sum();w=np.cumsum(p);m=np.cumsum(p*(edges[:-1]+edges[1:])/2);between=(m[-1]*w-m)**2/(w*(1-w)+1e-15);return float((edges[:-1]+edges[1:])[int(np.argmax(between))]/2)
def measurements(images,dna,pixel_um,label,seed):
 assert dna.ndim==2 and all(v.shape==dna.shape for v in images.values());smooth=ndimage.gaussian_filter(np.maximum(np.nan_to_num(dna),0),sigma=1/pixel_um);threshold=otsu(smooth);out={'label':label,'pixel_um':pixel_um,'shape':list(dna.shape),'DNA_threshold':threshold,'DNA_nonzero_fraction':float(np.mean(dna>0)),'marker_quantiles':{k:np.quantile(v[np.isfinite(v)],[0,.5,.9,.99,1]).tolist() if np.isfinite(v).any() else None for k,v in images.items()},'analyses':[]}
 if threshold is None:out['reason']='Too few finite positive DNA pixels';return out
 names=list(images);selected=[p for p in PAIRS if all(k in names for k in p)];rng=np.random.default_rng(seed)
 for factor in FACTORS:
  binary=smooth>threshold*factor;labels,n=ndimage.label(binary);area=np.bincount(labels.ravel())*pixel_um**2;keep=np.flatnonzero((area>=6)&(area<=250));keep=keep[keep!=0];mapping=np.zeros(n+1,dtype=np.int32);mapping[keep]=np.arange(1,len(keep)+1);labels=mapping[labels];n=len(keep);rec={'threshold_factor':factor,'nuclear_components':n,'threshold_mask_fraction':float(binary.mean()),'retained_mask_fraction':float(np.mean(labels>0)),'segmentation_limit':'Connected nuclei may merge or fragment; exploratoryobjects, no validatedcell phenotypes','spatial':[]};out['analyses'].append(rec)
  if n<20:rec['reason']='Fewer than20 nuclearcomponents';continue
  ids=np.arange(1,n+1);centers=np.array(ndimage.center_of_mass(np.ones_like(dna),labels,ids))*pixel_um;values=np.column_stack([ndimage.mean(np.nan_to_num(images[k]),labels,ids) for k in names]);ranks=np.column_stack([stats.rankdata(values[:,k],method='average') for k in range(len(names))]);sd=ranks.std(axis=0);z=(ranks-ranks.mean(axis=0))/np.where(sd>0,sd,1);tree=cKDTree(centers)
  if factor==1:
   dest=OUT/(re.sub('[^A-Za-z0-9_.-]','_',label)+'.objects.npz');np.savez_compressed(dest,coordinates_um=centers,marker_means=values,marker_labels=np.array(names));rec['objects_saved']=str(dest)
  for radius in RADII:
   edges=tree.query_pairs(radius,output_type='ndarray');e=len(edges);rr={'radius_um':radius,'undirected_edges':e};rec['spatial'].append(rr)
   if not e:rr['reason']='No neighbors';continue
   rows=np.r_[edges[:,0],edges[:,1]];cols=np.r_[edges[:,1],edges[:,0]];a=sparse.csr_matrix((np.ones(2*e),(rows,cols)),shape=(n,n));observed=z.T@(a@z)/(2*e);null=[]
   for unused in range(NULL):
    p=rng.permutation(n);zp=z[p];null.append(zp.T@(a@zp)/(2*e))
   null=np.asarray(null);rr['pairs']=[]
   for left,right in selected:
    i=names.index(left);j=names.index(right);raw=float(observed[i,j]);v=null[:,i,j];rr['pairs'].append({'left':left,'right':right,'raw_rank_association':raw,'joint_mark_null_mean':float(v.mean()),'excess_association':float(raw-v.mean()),'null_central95':np.quantile(v,[.025,.975]).tolist(),'exploratory_null_upper_p':float((1+np.sum(v>=raw))/(NULL+1)),'constant_marker':bool(sd[i]==0 or sd[j]==0)})
 return out
def mcd_schema(name,size):
 url=mcd.BASE+name;footer,receipt=mcd.get_range(url,size-mcd.FOOTER,size-1,size,mcd.FOOTER);start=footer.rfind('<MCDSchema'.encode('utf-16-le'));end=footer.rfind('</MCDSchema>'.encode('utf-16-le'));assert start>=0 and end>=start;xml=footer[start:end+len('</MCDSchema>'.encode('utf-16-le'))].decode('utf-16-le');root=ET.fromstring(xml);ac={str(x['ID']):x for e in root.iter() if mcd.local(e.tag)=='Acquisition' for x in [mcd.fields(e)]};ch=[mcd.fields(e) for e in root.iter() if mcd.local(e.tag)=='AcquisitionChannel'];return url,ac,ch,{'name':name,'suffix':receipt,'schema_sha256':hashlib.sha256(xml.encode()).hexdigest()}
def imc_one(row,schemas,seed):
 name,aid=re.fullmatch(r'((?:MFS|USTS)_TMA_[12])_ROI(\d+)',row['ROI_ID']).groups();url,size,ac,ch=schemas[name+'.mcd'];aid=str(int(aid));assert aid in ac,'Clinical ROI absent fromrawschema';a=ac[aid];channel=[x for x in ch if str(x.get('AcquisitionID'))==aid and x.get('ChannelName') not in ['X','Y','Z']];channel.sort(key=lambda x:int(x['OrderNumber']));stride=3+len(channel);unit=stride*4;start=int(a['DataStartOffset']);end=int(a['DataEndOffset']);wire=end-start+1;remainder=wire%unit;assert remainder in[0,1],f'Unexpected MCD trailingbytes{remainder}';n=wire//unit;nx=int(a['MaxX']);ny=(n+nx-1)//nx;first=max(0,(ny-128)//2)*nx;count=min(n-first,128*nx);offset=start+first*unit;payload,receipt=mcd.get_range(url,offset,offset+count*unit-1,size,32*1024*1024);pixels=np.frombuffer(payload,dtype='<f4').reshape(-1,stride);assert np.isfinite(pixels[:,:2]).all();x=pixels[:,0];y=pixels[:,1];assert np.allclose(x,np.round(x),atol=1e-4) and np.allclose(y,np.round(y),atol=1e-4),'Nonintegerrawrastercoordinates';x=np.round(x-x.min()).astype(int);y=np.round(y-y.min()).astype(int);assert x.max()<10010 and y.max()<10010;shape=(y.max()+1,x.max()+1);assert np.unique(np.column_stack([x,y]),axis=0).shape[0]==len(x),'Duplicate rasterpixels';idx={c['ChannelLabel']:k+3 for k,c in enumerate(channel)};assert 'DNA1' in idx and 'DNA2' in idx;wanted=['DNA1','DNA2']+[k for k in MARKERS if k in idx];images={}
 for k in wanted:
  v=np.zeros(shape,dtype=np.float32);v[y,x]=pixels[:,idx[k]];images[k]=v
 dna=images.pop('DNA1')+images.pop('DNA2');result=measurements(images,dna,1.,row['ROI_ID'],seed);result.update(clinical=row,acquisition_id=aid,raw_manifest_bytes=size,range=receipt,full_roi_records=n,retained_records=count,trailing_surplus_bytes=remainder,coordinate_ranges=[[float(pixels[:,k].min()),float(pixels[:,k].max())] for k in range(3)],selection='Central128rasterrows, value-independent');return result
def patient_analysis(imc,baseline):
 rows=[]
 for x in imc:
  if 'error' in x:continue
  c=x['clinical'];core=next((v for v in x['analyses'] if v['threshold_factor']==1),None)
  if not core:continue
  for s in core['spatial']:
   for p in s.get('pairs',[]):
    if not p['constant_marker']:rows.append({**c,'radius_um':s['radius_um'],'pair':p['left']+'__'+p['right'],'excess':p['excess_association'],'raw':p['raw_rank_association']})
 if not rows:return {'status':'No analyzable nuclear spatial endpoints'}
 f=pd.DataFrame(rows);key=['L_ID','Pat_ID','Diagnosis','Sample_Type','Grade','Treatment','ROI_location','radius_um','pair'];f['Treatment']=f['Treatment'].fillna('None');f=f.groupby(key,dropna=False)[['excess','raw']].mean().reset_index();key2=[k for k in key if k!='ROI_location'];f=f.groupby(key2,dropna=False)[['excess','raw']].mean().reset_index();f.to_csv(OUT/'imc-spatial-specimen-endpoints.tsv',sep='\t',index=False)
 b=pd.DataFrame(baseline);b=b[['L_ID','Pat_ID','grade_numeric']].rename(columns={'Pat_ID':'source_baseline_patient'});primary=f.merge(b,on='L_ID',how='inner',validate='many_to_one');assert (primary.Pat_ID==primary.source_baseline_patient).all();primary=primary[(primary.Treatment=='None')&(primary.Sample_Type=='Primary')];primary['grade_numeric']=pd.to_numeric(primary.grade_numeric);primary=primary[primary.grade_numeric>=2];tests=[];rng=np.random.default_rng(SEED+700)
 def ci_mean(v):
  if not len(v):return None
  return np.quantile(np.mean(v[rng.integers(0,len(v),(2000,len(v)))],axis=1),[.025,.975]).tolist()
 for (radius,pair),g in primary.groupby(['radius_um','pair']):
  pat=g.groupby(['Pat_ID','Diagnosis'])['excess'].mean().reset_index();u=pat[pat.Diagnosis=='USTS'].excess.to_numpy();m=pat[pat.Diagnosis=='MFS'].excess.to_numpy();rec={'radius_um':radius,'pair':pair,'n_UPS_patients':len(u),'n_highgrade_MFS_patients':len(m),'UPS_mean_excess':float(u.mean()) if len(u) else None,'MFS_mean_excess':float(m.mean()) if len(m) else None,'UPS_patient_bootstrap95':ci_mean(u),'MFS_patient_bootstrap95':ci_mean(m)}
  if len(u)>=3 and len(m)>=3:
   observed=float(u.mean()-m.mean());v=np.r_[u,m];null=np.array([np.mean((p:=rng.permutation(v))[:len(u)])-np.mean(p[len(u):]) for unused in range(10000)]);rec.update(UPS_minus_MFS=observed,patient_histology_permutation_p=float((1+np.sum(np.abs(null)>=abs(observed)))/10001))
  tests.append(rec)
 finite=[(i,x['patient_histology_permutation_p']) for i,x in enumerate(tests) if 'patient_histology_permutation_p' in x];order=sorted(finite,key=lambda x:x[1]);q=1.
 for rank in range(len(order)-1,-1,-1):
  i,p=order[rank];q=min(q,p*len(order)/(rank+1));tests[i]['BH_q_across_all_available_primary15']=q
 paired=[];unt=f[(f.Treatment=='None')&(f.Sample_Type=='Primary')];post=f[(f.Treatment=='RT')&(f.Sample_Type=='Primary')]
 for (radius,pair),g in f.groupby(['radius_um','pair']):
  pre=unt[(unt.radius_um==radius)&(unt.pair==pair)].groupby(['Pat_ID','Diagnosis']).excess.mean();after=post[(post.radius_um==radius)&(post.pair==pair)].groupby(['Pat_ID','Diagnosis']).excess.mean();joined=pd.concat([pre.rename('pre'),after.rename('post')],axis=1).dropna()
  for diag,sub in joined.groupby(level='Diagnosis'):
   d=(sub.post-sub.pre).to_numpy();paired.append({'radius_um':radius,'pair':pair,'diagnosis':diag,'n_paired_patients':len(d),'mean_RT_minus_untreated':float(d.mean()),'paired_patient_bootstrap95':ci_mean(d),'interpretation':'Observational biopsy/resection sampling andRT association; no causal response claim'})
 return {'status':'Measured exploratorymarker organization','source_baseline_patients':len({x['Pat_ID'] for x in baseline}),'baseline_LIDs_missing_from_successful_pixels':sorted(set(b.L_ID)-set(f.L_ID)),'eligible_primary_highgrade_patients':int(primary.Pat_ID.nunique()),'specimen_endpoint_table':str(OUT/'imc-spatial-specimen-endpoints.tsv'),'primary_histology_tests':tests,'paired_RT_descriptive':paired,'unit':'ROI mean withinlocation then location mean withinspecimen; repeated specimen means withinpatient; no ROI/tile independence','multiplicity':'Fivepairs x3radii primary15; all3thresholds retained in fullresults, sensitivity not used to selectmain'}
def tiff_file(row,seed):
 global PAIRS
 path=row['path'];url='https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/'+path;size=int(row['size']);tpa.BUDGET=512*1024*1024;stream=tpa.RangeIO(url,size);out={'path':path,'manifest_bytes':size,'selection':'Fixed3x3grid at25%,50%,75%tile coordinates','clinical_unit':'Source filename/specimen key; human patientidentity requires sourceSupplementaryData5join','tiles':[]};aliases={'cd68':'CD68','hla2':'HLA-DR','mrc1':'MRC1','nkx2_2':'NKX2.2','psma3':'PSMA3'}
 with tifffile.TiffFile(stream) as tf:
  root=ET.fromstring(tf.ome_metadata);pixels=next(x for x in root.iter() if x.tag.split('}')[-1]=='Pixels');channels=[x.attrib.get('Name',x.attrib.get('ID')) for x in pixels if x.tag.split('}')[-1]=='Channel'];channels=[aliases.get(x.lower(),x) for x in channels];um=float(pixels.attrib['PhysicalSizeX']);assert pixels.attrib.get('PhysicalSizeXUnit','µm') in['µm','um'];page0=tf.pages[0];nx=(page0.imagewidth+page0.tilewidth-1)//page0.tilewidth;ny=(page0.imagelength+page0.tilelength-1)//page0.tilelength;coords=sorted({(round((ny-1)*v),round((nx-1)*w)) for v in[.25,.5,.75] for w in[.25,.5,.75]});out.update(OME_channels=channels,physical_pixel_um=um,series_axes=tf.series[0].axes,series_shape=list(tf.series[0].shape),TIFF_pages=len(tf.pages))
  old=PAIRS;PAIRS=old+[('CD68','MRC1'),('CD68','NKX2.2'),('NKX2.2','PSMA3')]+[(k,k) for k in channels if k.startswith('Opal')]
  try:
   for tile_i,(y,x) in enumerate(coords):
    segment=y*nx+x;images={};receipts=[]
    if page0.samplesperpixel==len(channels):
     off=int(page0.dataoffsets[segment]);n=int(page0.databytecounts[segment]);stream.seek(off);b=stream.read(n);tile=np.asarray(page0.decode(b,segment,jpegtables=page0.jpegtables)[0]).reshape(page0.tilelength,page0.tilewidth,len(channels));images={c:tile[:,:,i] for i,c in enumerate(channels)};receipts.append({'page':0,'segment':segment,'offset':off,'bytes':n,'sha256':hashlib.sha256(b).hexdigest()})
    else:
     assert len(tf.pages)==len(channels),'UnsupportedTIFF channel/page organization'
     for i,(page,c) in enumerate(zip(tf.pages,channels)):
      assert page.tilewidth==page0.tilewidth and page.tilelength==page0.tilelength;off=int(page.dataoffsets[segment]);n=int(page.databytecounts[segment]);stream.seek(off);b=stream.read(n);tile=np.asarray(page.decode(b,segment,jpegtables=page.jpegtables)[0]);images[c]=tile.reshape(page.tilelength,page.tilewidth);receipts.append({'page':i,'segment':segment,'offset':off,'bytes':n,'sha256':hashlib.sha256(b).hexdigest()})
    dna_names=[k for k in images if k.lower() in['dapi','hoechst','nuclei']];assert len(dna_names)==1,'Nuclear channel identity unresolved';dna=images.pop(dna_names[0]);images={k:v for k,v in images.items() if k.lower() not in['af','autofluorescence']};r=measurements(images,dna,um,Path(path).parent.name+'-'+Path(path).stem+f'-grid{y}-{x}',seed+tile_i);r.update(tile_row=y,tile_column=x,segments=receipts);out['tiles'].append(r)
  finally:PAIRS=old
 out.update(range_receipts=stream.receipts,range_downloaded_bytes=stream.downloaded,PSMA3_warning='PSMA3 is proteasomealpha3, not FOLH1/PSMA receptor',Panel2_identity='Generic Opal channels remain fluorophore labels; antibody assignment not inferred');return out
def finite_primary_followthrough():
 result={}
 for label,fn in [('Ewing-primary-supplements',lambda:getfull('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13111610/supplementaryFiles','Ewing-primary-supplements.zip')),('pediatric-primary-DOI',lambda:getfull('https://doi.org/10.21203/rs.3.rs-10374394/v1','pediatric-primary.html',16*1024*1024)),('ScPCA-Ewing-corrected-label',lambda:src.jsonget('https://api.scpca.alexslemonade.org/v1/samples/?limit=2000&diagnosis=Ewing+sarcoma&has_single_cell_data=true&includes_anndata=true','scpca-Ewing-corrected.json'))]:
  try:
   r=fn()
   if label=='ScPCA-Ewing-corrected-label':
    data=r['metadata'];samples=data.get('results',[]);result[label]={'receipt':{k:v for k,v in r.items() if k!='metadata'},'reported_samples':data.get('count'),'metadata_samples':len(samples),'next':data.get('next'),'project_counts':dict(collections.Counter(x['project'] for x in samples)),'xenograft_counts':dict(collections.Counter(str(x.get('is_xenograft')) for x in samples)),'participant_IDs':sorted({x.get('additional_metadata',{}).get('participant_id') for x in samples if x.get('additional_metadata',{}).get('participant_id')}),'scope':'Publicmetadataonly; no email/token request'};continue
   path,receipt=r;record={'receipt':receipt};result[label]=record
   if label.startswith('Ewing'):
    with zipfile.ZipFile(path) as z:
     record['members']=[{'name':x.filename,'bytes':x.file_size,'compressed_bytes':x.compress_size} for x in z.infolist()];record['clinical_source_workbooks']=[]
     for x in z.infolist():
      if x.filename.endswith('.xlsx') and x.file_size<40*1024*1024:
       b=z.read(x);table=src.xlsx_tables(b);p=OUT/Path(x.filename).name;p.write_bytes(b);record['clinical_source_workbooks'].append({'name':x.filename,'sha256':hashlib.sha256(b).hexdigest(),'saved':str(p),'sheets':[{'sheet':s['sheet'],'rows':s['n_rows'],'first20rows':s['rows'][:20]} for s in table['tables']]})
   else:
    html=path.read_text(errors='replace');links=sorted(set(re.findall(r'(?:href|src)=[\"\']([^\"\']+)[\"\']',html)));record['primary_candidate_links']=[urllib.parse.urljoin(receipt['final_url'],x) for x in links if re.search('pdf|supp|data|github|zenodo|geo|ega|dbgap',x,re.I)];record['data_availability_snippets']=re.findall(r'.{0,160}(?:data availability|controlled.access|supplementary|GSE\d+|EGAS\d+).{0,400}',html,re.I)[:30]
  except Exception as e:result[label]={'error_type':type(e).__name__,'error':str(e),'absence_claim':False}
 return result
def compact_measure(x):
 if 'error' in x:return x
 core=next((a for a in x.get('analyses',[]) if a['threshold_factor']==1),{})
 return {k:x.get(k) for k in['label','clinical','shape','DNA_threshold','DNA_nonzero_fraction','marker_quantiles']}|{'nuclei_by_threshold':{str(a['threshold_factor']):a['nuclear_components'] for a in x.get('analyses',[])},'primary_spatial':core.get('spatial',[])}
def main():
 (OUT/'spatial-marker-amendment.json').write_text(json.dumps(AMENDMENT,indent=2));result={'schema':'emc-spatial-marker-followthrough/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'IMC':[],'TIFF':[]};meta=src.imc_metadata();assert meta['sha256']=='966a15b9eddd7457a3792fff225c858e9899545cf0098e9b6b0512c16a541ab8';s=meta['tables'][0];header=s['rows'][0];clinical=[dict(zip(header,r+[None]*(len(header)-len(r)))) for r in s['rows'][1:]];result['clinical_metadata_receipt']={k:v for k,v in meta.items() if k!='tables'};lists=src.actual_filelists();annotations=src.author_annotations();baseline=next(x['rows'] for x in annotations if Path(x['saved']).name=='IMC_sample_annotation.tsv');schemas={};result['MCD_schemas']=[]
 for name,size in mcd.FILES:
  url,ac,ch,receipt=mcd_schema(name,size);schemas[name]=(url,size,ac,ch);result['MCD_schemas'].append(receipt)
 for i,row in enumerate(clinical):
  print('EMC_SPATIAL_IMC '+str(i+1)+'/'+str(len(clinical))+' '+row['ROI_ID'],flush=True)
  try:result['IMC'].append(imc_one(row,schemas,SEED+i))
  except Exception as e:result['IMC'].append({'clinical':row,'error_type':type(e).__name__,'error':str(e),'absence_claim':False})
 try:result['patient_analysis']=patient_analysis(result['IMC'],baseline)
 except Exception as e:result['patient_analysis']={'error_type':type(e).__name__,'error':str(e),'absence_claim':False}
 ew=[row for item in lists[1:] for row in item['metadata']]
 for i,row in enumerate(ew):
  print('EMC_SPATIAL_TIFF '+str(i+1)+'/'+str(len(ew))+' '+row['path'],flush=True)
  try:result['TIFF'].append(tiff_file(row,SEED+1000+i*20))
  except Exception as e:result['TIFF'].append({'path':row['path'],'error_type':type(e).__name__,'error':str(e),'absence_claim':False})
 result['primary_source_followthrough']=finite_primary_followthrough();result=clean(result);dest=OUT/'spatial-marker-followthrough-actual.json';dest.write_text(json.dumps(result,allow_nan=False));summary={'schema':result['schema'],'executed_utc':result['executed_utc'],'amendment':AMENDMENT,'IMC_requested':len(clinical),'IMC_success':sum('error' not in x for x in result['IMC']),'IMC':list(map(compact_measure,result['IMC'])),'patient_analysis':result['patient_analysis'],'TIFF_requested':len(ew),'TIFF_success':sum('error' not in x for x in result['TIFF']),'TIFF':[x if 'error' in x else {'path':x['path'],'OME_channels':x['OME_channels'],'range_downloaded_bytes':x['range_downloaded_bytes'],'tiles':list(map(compact_measure,x['tiles']))} for x in result['TIFF']],'primary_source_followthrough':result['primary_source_followthrough'],'full_result':str(dest),'full_result_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()};print('EMC_SPATIAL_MARKER_FOLLOWTHROUGH_BEGIN');print(json.dumps(clean(summary),allow_nan=False));print('EMC_SPATIAL_MARKER_FOLLOWTHROUGH_END')
if __name__=='__main__':main()
