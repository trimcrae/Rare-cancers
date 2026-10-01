import json,hashlib,datetime,copy
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
from scipy.spatial import cKDTree
from scipy import sparse
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
OUT=sm.OUT;ROOTS=[Path('restored-artifacts'),Path('restored-artifacts-extra'),OUT];SEED=20261001
AMENDMENT={'dated_utc':'2026-10-01','selection':'All200IMCmetadata/199uniqueROI, existingfactor1objects no newpixels/endpoints','null':'199joint-marker-row permutations in40um density midrankquintiles; fixed5pairs10/20/40um','unit':'DeduplicateROI beforeequal-location/specimen/patient aggregation; requestledgerretainsduplicate','primary':'UPS vs highgradeMFS fixed15comparisons/BH15; originalunconditional sensitivity','limits':'Thresholdmasks/sourcepartialstrips remain exploratory; densitynull notphenotypevalidation/causaladjustment'}
def rc(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def one_json(name):
 pp=sorted({p for root in ROOTS for p in root.rglob(name)});assert pp,'Missing '+name;assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in pp})==1,'Conflicting '+name;return json.loads(pp[0].read_text()),rc(pp[0])
def object_file(name):
 pp=sorted({p for root in ROOTS for p in root.rglob(Path(name).name)});assert pp,'Missing '+name;assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in pp})==1;return pp[0]
def density_one(record,index):
 core=next(a for a in record['analyses'] if a['threshold_factor']==1);out=copy.deepcopy(record);out['analyses']=[copy.deepcopy(core)];dest=out['analyses'][0];n=core['nuclear_components'];rec={'global_metadata_index':index,'ROI_ID':record['clinical']['ROI_ID'],'nuclear_components':n,'status':'not_analyzable','comparisons':[]}
 if n<20:rec['reason']='Fewer than20objects';return out,rec
 p=object_file(core['objects_saved']);npz=np.load(p,allow_pickle=False);coords=npz['coordinates_um'];values=npz['marker_means'];names=list(map(str,npz['marker_labels']));assert coords.shape==(n,2) and values.shape==(n,len(names)) and np.isfinite(coords).all() and np.isfinite(values).all();ranks=np.column_stack([rankdata(values[:,j],method='average') for j in range(len(names))]);sd=ranks.std(axis=0);z=(ranks-ranks.mean(axis=0))/np.where(sd>0,sd,1);tree=cKDTree(coords);density=tree.query_ball_point(coords,40.,return_length=True);bins=np.minimum(4,(rankdata(density,method='average')/n*5).astype(int));groups=[np.flatnonzero(bins==j) for j in range(5)];rng=np.random.default_rng(SEED+18000+index);spatial=[]
 for radius in sm.RADII:
  edges=tree.query_pairs(radius,output_type='ndarray');ne=len(edges);entry={'radius_um':radius,'undirected_edges':ne,'pairs':[]};spatial.append(entry)
  if not ne:continue
  graph=sparse.csr_matrix((np.ones(2*ne),(np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),shape=(n,n));observed=z.T@(graph@z)/(2*ne);null=[]
  for unused in range(199):
   perm=np.arange(n)
   for group in groups:perm[group]=rng.permutation(group)
   zp=z[perm];null.append(zp.T@(graph@zp)/(2*ne))
  null=np.asarray(null);old=next(s for s in core['spatial'] if s['radius_um']==radius);assert old['undirected_edges']==ne
  for left,right in sm.PAIRS:
   if left not in names or right not in names:continue
   i,j=names.index(left),names.index(right);raw=float(observed[i,j]);oldp=next(p for p in old.get('pairs',[]) if p['left']==left and p['right']==right);assert abs(raw-oldp['raw_rank_association'])<1e-10;v=null[:,i,j];constant=bool(sd[i]==0 or sd[j]==0);excess=float(raw-v.mean());entry['pairs'].append({'left':left,'right':right,'raw_rank_association':raw,'joint_mark_null_mean':float(v.mean()),'excess_association':excess,'null_central95':np.quantile(v,[.025,.975]).tolist(),'exploratory_null_upper_p':float((1+np.sum(v>=raw))/200),'constant_marker':constant});rec['comparisons'].append({'radius_um':radius,'left':left,'right':right,'raw':raw,'original_unconditional_excess':oldp['excess_association'],'density_conditioned_excess':excess,'constant_marker':constant})
 dest['spatial']=spatial;rec.update(status='measured',object_receipt=rc(p),local_density40um_including_self_quantiles=np.quantile(density,[0,.25,.5,.75,1]).tolist(),density_bin_counts=[len(g) for g in groups]);return out,rec
def main():
 OUT.mkdir(parents=True,exist_ok=True);source,srec=one_json('spatial-marker-followthrough-actual.json');assert source['schema']=='emc-spatial-marker-followthrough/1' and len(source['IMC'])==200 and all('error' not in r for r in source['IMC']);records=[];converted=[];computed={}
 for i,r in enumerate(source['IMC']):
  print('IMC_DENSITY '+str(i)+'/200 '+r['clinical']['ROI_ID'],flush=True);roi=r['clinical']['ROI_ID']
  if roi in computed:j=computed[roi];assert r['clinical']==source['IMC'][j]['clinical'];new=copy.deepcopy(converted[j]);rec=copy.deepcopy(records[j]);rec.update(global_metadata_index=i,duplicate_of_metadata_index=j)
  else:new,rec=density_one(r,i);computed[roi]=i
  converted.append(new);records.append(rec)
 unique=[];seen={};duplicates=[]
 for i,r in enumerate(converted):
  roi=r['clinical']['ROI_ID']
  if roi in seen:
   j=seen[roi];assert r['clinical']==converted[j]['clinical'] and r['analyses']==converted[j]['analyses'];duplicates.append({'ROI_ID':roi,'kept_metadata_index':j,'excluded_metadata_index':i});continue
  seen[roi]=i;unique.append(r)
 assert len(unique)==199 and len(duplicates)==1;ann=src.author_annotations();selected=next(a for a in ann if Path(a['saved']).name=='IMC_sample_annotation.tsv');baseline=selected['rows'];pins=[a['sha256'] for a in source.get('baseline_annotation_receipt',[])];assert not pins or selected['sha256'] in pins;endpoint=OUT/'imc-spatial-specimen-endpoints.tsv';old=endpoint.read_bytes() if endpoint.exists() else None;analysis=sm.patient_analysis(unique,baseline)
 if endpoint.exists():new=OUT/'imc-density-conditioned-specimen-endpoints.tsv';new.write_bytes(endpoint.read_bytes());analysis['specimen_endpoint_table']=str(new)
 if old is not None:endpoint.write_bytes(old)
 q=1.;tests=analysis.get('primary_histology_tests',[]);order=sorted([(i,t['patient_histology_permutation_p']) for i,t in enumerate(tests) if 'patient_histology_permutation_p' in t],key=lambda z:z[1])
 for k in range(len(order)-1,-1,-1):i,p=order[k];q=min(q,p*15/(k+1));tests[i]['BH_q_fixed_primary15']=q
 result={'schema':'emc-IMC-density-sensitivity/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'source_receipt':srec,'metadata_rows':200,'unique_acquisitions':199,'duplicate_raw_acquisition_audit':duplicates,'density_records':records,'patient_analysis':analysis,'original_unconditional_patient_analysis':source.get('patient_analysis'),'baseline_annotation_receipt':{k:v for k,v in selected.items() if k!='rows'}};dest=OUT/'imc-density-sensitivity-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_IMC_DENSITY_SENSITIVITY_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_IMC_DENSITY_SENSITIVITY_END')
if __name__=='__main__':main()
