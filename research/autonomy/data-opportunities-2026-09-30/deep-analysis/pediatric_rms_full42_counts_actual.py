import argparse,json,gzip,re,hashlib,datetime,collections
from pathlib import Path
import numpy as np
import pediatric_rms_processed_count_pilot_actual as old
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT;TARGETS=old.TARGETS
AMENDMENT={'dated_utc':'2026-10-01','selection':'All42RNA triplets in frozen GSE174376 TAR, sortedGSM disjointbatches','targets':'Frozen86 symbols, explicitH1FX/H1-10; hg19prefix stripping onlyEnsembl-confirmedhuman','species':'Human/mouse/unknownUMI fromliteralEnsembl; human-normalized withheldwithoutIDevidence','unit':'Library andliteralSJRHBroots, notverifiedpatients; keepsc/sn/baselinePDX/treatedPDX/organoid','endpoints':'Allbarcodes and UMI500sens; targetdetection/summedcounts/humanUMIfractions; zero human denomexcluded','limits':'No protein/celltype/causality. No treatedzero-paddingnormalization. Annotationsseparateaudit.'}
def receipt(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def inventory():
 p=old.sm.BASE/'results/RMS-complete-public-count-inventory-and-pilot.json';d=json.loads(p.read_text());d=d.get('result',d);assert d['schema']=='emc-pediatric-RMS-count-pilot/1';m=d['archive_manifest']['all_members'];meta=d['all_primary_GSM_metadata'];ids=sorted({re.match(r'(GSM\d+)_',r['name']).group(1) for r in m if re.search(r'_features\.tsv\.gz$',r['name'])});assert len(ids)==42;return d,m,meta,ids,receipt(p)
def classify(meta):
 title=meta['title'][0];source=meta['source_name_ch1'][0];protocol=' '.join(meta.get('characteristics_ch1',[]));mode='snRNA' if 'snRNA' in protocol else 'scRNA' if 'scRNA' in protocol else 'unresolved';assert mode!='unresolved';root=re.match(r'(SJRHB\d+)(?:_|$)',title);assert root
 kind='human_tumor' if source=='Patient tumor' else 'organoid' if source=='Organoid' else 'treated_PDX' if '_treat_' in title else 'baseline_PDX' if source=='Orthotopic patient-derived xenograft' else 'unresolved';assert kind!='unresolved';return {'literal_title':title,'literal_model_root':root.group(1),'source_class':kind,'assay':mode,'source_name':source,'clinical_patient_identity_verified':False}
def measured(gsm,fp,bp,mp):
 with gzip.open(fp,'rt') as f:features=[l.rstrip('\n').split('\t') for l in f]
 with gzip.open(bp,'rt') as f:barcodes=[l.rstrip('\n') for l in f]
 assert len(barcodes)==len(set(barcodes));ng,nc=len(features),len(barcodes);species=[];symbols=[];audit=[]
 for i,row in enumerate(features):
  fid=row[0];symbol=row[1] if len(row)>1 else row[0];sp='human' if re.search(r'(?:^|_)(ENSG\d+)',fid) else 'mouse' if re.search(r'(?:^|_)(ENSMUSG\d+)',fid) else 'unknown';species.append(sp);stripped=symbol
  if sp=='human' and symbol.startswith('hg19_'):stripped=symbol[5:]
  symbols.append(stripped)
  if stripped!=symbol:audit.append({'feature_row_0based':i,'gene_id':fid,'literal_symbol':symbol,'audited_symbol':stripped,'rule':'hg19prefixEnsemblhuman'})
 human=np.array(species)=='human';mouse=np.array(species)=='mouse';lookup=collections.defaultdict(list)
 for i,s in enumerate(symbols):
  if human[i]:lookup[s].append(i)
 mapping={};target_rows=collections.defaultdict(list)
 for j,g in enumerate(TARGETS):
  key='H1-10' if g=='H1FX' and g not in lookup and 'H1-10' in lookup else g;rows=lookup.get(key,[]);mapping[g]={'source_symbol':key,'human_feature_rows_0based':rows,'duplicate_symbol_sum':len(rows)>1,'explicit_alias':key!=g}
  for i in rows:target_rows[i+1].append(j)
 counts=np.zeros((len(TARGETS),nc),np.float64);totals=np.zeros((4,nc),np.float64);coordinates=np.zeros(nc,np.int64);seen=0;zeros=0
 with gzip.open(mp,'rt') as f:
  header=f.readline().strip();assert header in ['%%MatrixMarket matrix coordinate integer general','%%MatrixMarket matrix coordinate real general'];line=f.readline()
  while line.startswith('%'):line=f.readline()
  a,b,nnz=map(int,line.split());assert [a,b]==[ng,nc]
  for line in f:
   if not line.strip() or line.startswith('%'):continue
   ff=line.split();assert len(ff)==3;row,col=int(ff[0]),int(ff[1]);v=float(ff[2]);assert 1<=row<=ng and 1<=col<=nc and np.isfinite(v) and v>=0 and v==round(v);seen+=1;totals[0,col-1]+=v;sp=1 if human[row-1] else 2 if mouse[row-1] else 3;totals[sp,col-1]+=v;coordinates[col-1]+=v>0;zeros+=v==0
   for j in target_rows.get(row,[]):counts[j,col-1]+=v
   if seen%10000000==0:print('RMS42_TRIPLETS '+gsm+' '+str(seen)+'/'+str(nnz),flush=True)
  assert seen==nnz
 assert np.allclose(totals[0],totals[1:].sum(axis=0));summary=[]
 for label,mask in [('all_source_barcodes',np.ones(nc,bool)),('all_reference_UMI_ge500',totals[0]>=500),('human_UMI_ge500',totals[1]>=500)]:
  ht=totals[1,mask];at=totals[0,mask];usable=ht>0
  for j,g in enumerate(TARGETS):
   v=counts[j,mask];mapped=bool(mapping[g]['human_feature_rows_0based']);summary.append({'gene':g,'barcode_sensitivity':label,'barcodes':int(mask.sum()),'human_positive_barcodes':int(usable.sum()),'feature_mapped':mapped,'detected_barcodes':int(np.sum(v>0)) if mapped else None,'fraction_detected':float(np.mean(v>0)) if len(v) and mapped else None,'summed_target_UMI':float(v.sum()) if mapped else None,'fraction_summed_human_UMI':float(v.sum()/ht.sum()) if mapped and ht.sum()>0 else None,'fraction_summed_all_reference_UMI':float(v.sum()/at.sum()) if mapped and at.sum()>0 else None,'median_per_barcode_human_UMI_fraction':float(np.median(v[usable]/ht[usable])) if mapped and usable.any() else None,'raw_count_quantiles':np.quantile(v,[0,.25,.5,.75,.9,.99,1]).tolist() if mapped and len(v) else None,'missing_symbol_is_biological_absence':False})
 npz=OUT/(gsm+'-frozen-human-target-counts.npz');np.savez_compressed(npz,targets=np.asarray(TARGETS),barcodes=np.asarray(barcodes),target_counts=counts,all_reference_UMI=totals[0],human_UMI=totals[1],mouse_UMI=totals[2],unknown_species_UMI=totals[3],positive_coordinate_records=coordinates)
 return {'matrix_shape':[ng,nc],'coordinate_entries':[nnz,seen],'zero_coordinate_entries':int(zeros),'feature_species_counts':dict(collections.Counter(species)),'first20_literal_features':features[:20],'human_symbol_prefix_amendments':audit,'target_mapping':mapping,'UMI_totals':dict(zip(['all_reference','human','mouse','unknown'],map(float,totals.sum(axis=1)))),'UMI_quantiles':{k:np.quantile(v,[0,.25,.5,.75,.9,.99,1]).tolist() for k,v in zip(['all_reference','human','mouse','unknown'],totals)},'all_frozen_target_summaries':summary,'target_count_matrix':receipt(npz),'coordinate_records_are_unique_genes':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--start',type=int,required=True);p.add_argument('--stop',type=int,required=True);args=p.parse_args();data,members,meta,ids,ir=inventory();assert 0<=args.start<args.stop<=42;OUT.mkdir(parents=True,exist_ok=True);dest=OUT/f'RMS-full42-count-batch-{args.start}-{args.stop}.json';result={'schema':'emc-RMS-full42-count-batch/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'inventory_receipt':ir,'range':[args.start,args.stop],'all42_accessions':ids,'libraries':[],'complete':False}
 def save():dest.write_text(json.dumps(sm.clean(result),allow_nan=False))
 save()
 for index in range(args.start,args.stop):
  gsm=ids[index];record={'global_library_index':index,'GSM':gsm,'source_metadata':meta[gsm],'identity_audit':classify(meta[gsm]),'member_receipts':[]};result['libraries'].append(record);print('RMS42_LIBRARY '+str(index)+' '+gsm,flush=True)
  try:
   roles={}
   for role,pattern in [('features',r'_(features|genes)\.tsv\.gz$'),('barcodes',r'_barcodes\.tsv\.gz$'),('matrix',r'_matrix\.mtx\.gz$')]:
    hits=[m for m in members if m['type']=='regular' and m['name'].startswith(gsm+'_') and re.search(pattern,m['name'])];assert len(hits)==1,'Missing/ambiguous '+role;roles[role]=hits[0]
   paths={};old.RECEIPTS.clear()
   for role,member in roles.items():paths[role],rec=old.download_member(member);record['member_receipts'].append({'role':role,**rec})
   record['measured_counts']=measured(gsm,paths['features'],paths['barcodes'],paths['matrix']);record['status']='measured';record['range_receipts']=list(old.RECEIPTS)
  except Exception as e:record.update(status='error',error_type=type(e).__name__,error=str(e),absence_claim=False,range_receipts=list(old.RECEIPTS))
  save()
 result.update(complete=True,requested=args.stop-args.start,measured=sum(r.get('status')=='measured' for r in result['libraries']),errors=sum(r.get('status')=='error' for r in result['libraries']));save();compact={**result,'libraries':[{k:v for k,v in r.items() if k!='range_receipts'} for r in result['libraries']],'full_result':receipt(dest)};print('EMC_RMS_FULL42_COUNTS_BEGIN');print(json.dumps(sm.clean(compact),allow_nan=False));print('EMC_RMS_FULL42_COUNTS_END');assert result['errors']==0,'Explicit unresolved library errors'
if __name__=='__main__':main()
