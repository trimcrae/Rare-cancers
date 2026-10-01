import io,json,gzip,hashlib,datetime,re,time,urllib.request,urllib.error,http.client,tarfile,collections
from pathlib import Path
import numpy as np
import pediatric_and_ewing_processed_exports_actual as exp
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT;URL='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE174nnn/GSE174376/suppl/GSE174376_RAW.tar';SIZE=13723596800;GSM='GSM5293229';TARGETS=sorted(exp.TARGETS)
AMENDMENT={'dated_utc':'2026-10-01','source':'Verified existing GSE174376 human/PDX RMS source','selection':'Complete TAR headers/primary GSM metadata; first accession GSM5293229 fixed before count values','analysis':'All pilot barcodes; frozen86symbols/explicit H1-10 alias; raw counts and totalUMI>=500 sensitivity, no invented annotations','limits':'RNA counts not protein/drug evidence; pilot not replication or route closure when further cohort work is feasible'}
RECEIPTS=[]
def request(url,start=None,stop=None,total=None,cap=None):
 headers={'User-Agent':'EMC-published-measured-data-reanalysis/1','Accept-Encoding':'identity'}
 if start is not None:headers['Range']=f'bytes={start}-{stop}'
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=120) as r:
    wanted=stop-start+1 if start is not None else cap;body=r.read(wanted+1);rec={'url':url,'final_url':r.url,'http_status':r.status,'requested_range':[start,stop] if start is not None else None,'Content_Range':r.headers.get('Content-Range'),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
    if start is not None:
     if r.status!=206 or rec['Content_Range']!=f'bytes {start}-{stop}/{total}' or len(body)!=wanted:raise RuntimeError('Nonexact range response')
    elif len(body)>cap:raise RuntimeError('Metadata cap exceeded')
   RECEIPTS.append(rec);return body,rec
  except (urllib.error.HTTPError,urllib.error.URLError,http.client.RemoteDisconnected,TimeoutError,ConnectionResetError,RuntimeError) as e:
   if isinstance(e,RuntimeError) and str(e)!='Nonexact range response':raise
   if isinstance(e,urllib.error.HTTPError) and e.code not in[403,408,429,500,502,503,504]:raise
   RECEIPTS.append({'url':url,'transport_rejection':type(e).__name__,'error':str(e),'attempt':attempt+1,'absence_claim':False})
   if attempt==2:raise
   time.sleep(2*(attempt+1))
def metadata():
 url='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174376&targ=gsm&form=text&view=full';b,r=request(url,cap=16*1024**2);path=OUT/'GSE174376-all-primary-metadata.soft.txt';path.write_bytes(b);samples={};current=None
 for line in b.decode('utf-8').splitlines():
  if line.startswith('^SAMPLE = '):current=line.split(' = ',1)[1];samples[current]=collections.defaultdict(list)
  elif line.startswith('^'):current=None
  elif current and line.startswith('!Sample_') and ' = ' in line:k,v=line.split(' = ',1);samples[current][k.removeprefix('!Sample_')].append(v)
 assert GSM in samples;return {k:dict(v) for k,v in samples.items()},{**r,'saved':str(path)}
def manifest():
 position=0;entries=[];long_name=None
 while position+512<=SIZE:
  raw,r=request(URL,position,position+511,SIZE)
  if not raw.strip(b'\0'):break
  item=tarfile.TarInfo.frombuf(raw,'utf-8','strict');data_offset=position+512;name=long_name or item.name;long_name=None
  if item.type==tarfile.GNUTYPE_LONGNAME:
   assert item.size<=65536;payload,_=request(URL,data_offset,data_offset+item.size-1,SIZE);long_name=payload.rstrip(b'\0').decode('utf-8')
  elif item.type in[tarfile.REGTYPE,tarfile.AREGTYPE]:entries.append({'name':name,'header_offset':position,'data_offset':data_offset,'bytes':item.size,'type':'regular','header_sha256':r['sha256']})
  else:entries.append({'name':name,'header_offset':position,'data_offset':data_offset,'bytes':item.size,'type':repr(item.type),'header_sha256':r['sha256']})
  position=data_offset+512*((item.size+511)//512);assert position<=SIZE;assert len(entries)<5000
  if len(entries)%50==0:print('EMC_RMS_TAR_HEADERS '+str(len(entries))+' '+str(position),flush=True)
 assert entries;return entries,position
def download_member(member):
 assert 0<member['bytes']<=2*1024**3;path=OUT/Path(member['name']).name;h=hashlib.sha256();written=0;first=len(RECEIPTS)
 with path.open('wb') as out:
  while written<member['bytes']:
   length=min(8*1024**2,member['bytes']-written);start=member['data_offset']+written;b,r=request(URL,start,start+length-1,SIZE);out.write(b);h.update(b);written+=len(b)
   if written%(128*1024**2)<8*1024**2:print('EMC_RMS_MEMBER '+Path(member['name']).name+' '+str(written)+'/'+str(member['bytes']),flush=True)
 return path,{**member,'saved':str(path),'downloaded_bytes':written,'sha256_compressed_member':h.hexdigest(),'range_receipt_indices':[first,len(RECEIPTS)],'whole_archive_hash':False}
def measured_counts(selected,features_path,barcodes_path,matrix_path):
 with gzip.open(features_path,'rt') as f:features=[line.rstrip('\n').split('\t') for line in f]
 with gzip.open(barcodes_path,'rt') as f:barcodes=[line.rstrip('\n') for line in f]
 assert len(barcodes)==len(set(barcodes));symbols=[r[1] if len(r)>1 else r[0] for r in features];index=collections.defaultdict(list)
 for i,symbol in enumerate(symbols):index[symbol].append(i)
 mapped={};aliases={}
 for gene in TARGETS:
  key='H1-10' if gene=='H1FX' and gene not in index and 'H1-10' in index else gene;mapped[gene]=index.get(key,[]);aliases[gene]={'source_symbol':key,'feature_rows':mapped[gene],'mapping':'explicit_alias' if key!=gene else 'exact_symbol','duplicate_symbol_sum':len(mapped[gene])>1}
 row_targets=collections.defaultdict(list)
 for j,gene in enumerate(TARGETS):
  for feature in mapped[gene]:row_targets[feature+1].append(j)
 counts=np.zeros((len(TARGETS),len(barcodes)),dtype=np.float64);totals=np.zeros(len(barcodes));positive_records=np.zeros(len(barcodes),dtype=np.int64);seen=0;zero_entries=0
 with gzip.open(matrix_path,'rt') as f:
  header=f.readline().strip();assert header in['%%MatrixMarket matrix coordinate integer general','%%MatrixMarket matrix coordinate real general'];line=f.readline()
  while line.startswith('%'):line=f.readline()
  ng,nc,nnz=map(int,line.split());assert ng==len(features) and nc==len(barcodes)
  for line in f:
   if not line.strip() or line.startswith('%'):continue
   fields=line.split();assert len(fields)==3;row,col=int(fields[0]),int(fields[1]);value=float(fields[2]);assert 1<=row<=ng and 1<=col<=nc and np.isfinite(value) and value>=0 and value==round(value);seen+=1;totals[col-1]+=value
   if value>0:positive_records[col-1]+=1
   else:zero_entries+=1
   for j in row_targets.get(row,[]):counts[j,col-1]+=value
   if seen%10000000==0:print('EMC_RMS_COUNT_TRIPLETS '+str(seen)+'/'+str(nnz),flush=True)
  assert seen==nnz
 masks={'all_source_barcodes':np.ones(nc,dtype=bool),'barcode_total_UMI_ge500':totals>=500};summary=[]
 for gene_i,gene in enumerate(TARGETS):
  for label,mask in masks.items():
   v=counts[gene_i,mask];den=totals[mask];positive=den>0;summary.append({'gene':gene,'barcode_sensitivity':label,'barcodes':int(mask.sum()),'mapped_feature_rows':mapped[gene],'detected_barcodes':int(np.sum(v>0)),'fraction_detected':float(np.mean(v>0)) if len(v) else None,'raw_count_quantiles':np.quantile(v,[0,.25,.5,.75,.9,.99,1]).tolist() if len(v) else None,'median_fraction_total_UMI':float(np.median(v[positive]/den[positive])) if positive.any() else None,'missing_symbol_is_biological_absence':False})
 npz=OUT/(GSM+'-frozen-target-measured-counts.npz');np.savez_compressed(npz,targets=np.asarray(TARGETS),barcodes=np.asarray(barcodes),target_counts=counts,barcode_total_UMI=totals,positive_coordinate_records=positive_records);return {'matrix_header':header,'matrix_shape':[ng,nc],'declared_and_measured_coordinate_entries':[nnz,seen],'zero_count_entries':zero_entries,'positive_coordinate_records_are_distinct_genes':'Not independently assumed; coordinate records, not uniquegenes','barcode_total_UMI_quantiles':np.quantile(totals,[0,.25,.5,.75,.9,.99,1]).tolist(),'frozen_target_alias_audit':aliases,'measured_target_summaries':summary,'saved_target_count_matrix':{'saved':str(npz),'bytes':npz.stat().st_size,'sha256':hashlib.sha256(npz.read_bytes()).hexdigest()}}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 try:samples,mrec=metadata()
 except Exception as e:samples={};mrec={'error_type':type(e).__name__,'error':str(e),'absence_claim':False,'join_pending':True}
 members,last=manifest();mfile=OUT/'GSE174376-complete-range-TAR-manifest.json';mfile.write_text(json.dumps({'url':URL,'archive_bytes':SIZE,'members':members,'metadata':samples,'manifest_last_offset':last}));chosen=[m for m in members if m['name'].startswith(GSM+'_') and m['type']=='regular'];roles={}
 for role,pattern in [('features',r'_(features|genes)\.tsv\.gz$'),('barcodes',r'_barcodes\.tsv\.gz$'),('matrix',r'_matrix\.mtx\.gz$')]:
  hits=[m for m in chosen if re.search(pattern,m['name'])];assert len(hits)==1,'Missing/ambiguous pilot '+role;roles[role]=hits[0]
 paths={};member_receipts=[]
 for role,m in roles.items():paths[role],r=download_member(m);member_receipts.append({'role':role,**r})
 measured=measured_counts(roles,paths['features'],paths['barcodes'],paths['matrix']);result={'schema':'emc-pediatric-RMS-count-pilot/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'metadata_receipt':mrec,'all_primary_GSM_metadata':samples,'archive_manifest':{'saved':str(mfile),'bytes':mfile.stat().st_size,'sha256':hashlib.sha256(mfile.read_bytes()).hexdigest(),'archive_bytes':SIZE,'regular_members':sum(m['type']=='regular' for m in members),'all_members':members},'fixed_pilot':GSM,'pilot_source_metadata':samples.get(GSM,{'metadata_join_pending':True}),'member_receipts':member_receipts,'measured_counts':measured,'range_receipts':RECEIPTS,'next_finite_action':'Audit actual human18/PDX18 donor/assay join and published annotations; analyze verified available cohorts before closure'};dest=OUT/'pediatric-rms-processed-count-pilot-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_RMS_COUNT_PILOT_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_RMS_COUNT_PILOT_END')
if __name__=='__main__':main()
