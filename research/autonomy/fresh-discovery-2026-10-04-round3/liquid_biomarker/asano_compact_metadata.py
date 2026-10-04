from fetch_sources import BASE
import urllib.request,gzip,json,hashlib,datetime,collections,shutil
url='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE124nnn/GSE124158/matrix/GSE124158-GPL21263_series_matrix.txt.gz'
r={'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'stream every metadata line; retain all sample identities/characteristics, discard repeated protocol text; stop before expression table'}
keep={b'!Sample_title',b'!Sample_geo_accession',b'!Sample_source_name_ch1',b'!Sample_characteristics_ch1',b'!Sample_relation',b'!Sample_platform_id'}
try:
 assert shutil.disk_usage(BASE).free-1024**2>=10*1024**3
 h=hashlib.sha256(); total=0; retained=[];stop=False
 with urllib.request.urlopen(url,timeout=30) as resp:
  for line in gzip.GzipFile(fileobj=resp):
   if line.startswith(b'!series_matrix_table_begin'):stop=True;break
   h.update(line);total+=len(line)
   if total>8000000:raise RuntimeError('metadata exceeds8MB streamed bound')
   if line.split(b'\t')[0] in keep:retained.append(line)
 data=b''.join(retained);assert len(data)<1024**2
 (BASE/'GSE124158-GPL21263-identity-metadata.txt').write_bytes(data)
 r.update(metadata_stream_bytes=total,metadata_stream_sha256=h.hexdigest(),retained_bytes=len(data),retained_sha256=hashlib.sha256(data).hexdigest(),stop_before_expression=stop)
 rows={}
 for line in data.decode().splitlines():
  v=line.split('\t');rows.setdefault(v[0],[]).append([s.strip('"') for s in v[1:]])
 ids=rows['!Sample_geo_accession'][0];labels=collections.Counter();hits=[]
 for i,sample in enumerate(ids):
  meta={k:[v[i] for v in vals] for k,vals in rows.items()};ch=meta.get('!Sample_characteristics_ch1',[])
  for s in ch:
   if any(q in s.lower() for q in ['diagnosis','histolog','disease']):labels[s]+=1
  if any(q in json.dumps(meta).lower() for q in ['extraskeletal','chondrosarcoma','nr4a3','myxoid']):hits.append({'sample':sample,'metadata':meta})
 out={'n':len(ids),'diagnoses':dict(labels),'hits':hits,'fields':[v[0] for v in rows.get('!Sample_characteristics_ch1',[])]}
 (BASE/'asano-compact-eligibility.json').write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps({'n':len(ids),'diagnoses':dict(labels),'hit_count':len(hits),'fields':out['fields']},indent=2))
 print(json.dumps(hits,indent=2)[:6000])
except Exception as e:r.update(error_type=type(e).__name__,error=str(e))
(BASE/'asano-compact-receipt.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
