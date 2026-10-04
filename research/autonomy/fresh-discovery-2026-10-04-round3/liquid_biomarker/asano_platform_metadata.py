from fetch_sources import BASE
import urllib.request,gzip,json,hashlib,datetime,shutil,collections
receipts=[]; summary=[]
for platform in ['GPL18941','GPL21263']:
 url=f'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE124nnn/GSE124158/matrix/GSE124158-{platform}_series_matrix.txt.gz'
 r={'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'all sample metadata only, no expression values read'}
 try:
  assert shutil.disk_usage(BASE).free-2*1024**2>=10*1024**3
  with urllib.request.urlopen(url,timeout=30) as resp:
   f=gzip.GzipFile(fileobj=resp); lines=[];total=0
   for line in f:
    if line.startswith(b'!series_matrix_table_begin'): break
    total+=len(line)
    if total>1800000:raise RuntimeError('metadata exceeds bounded prefix')
    lines.append(line)
  data=b''.join(lines); (BASE/f'GSE124158-{platform}-metadata.txt').write_bytes(data)
  r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),hash_scope='decompressed metadata prefix only')
  rows={}
  for line in data.decode().splitlines():
   vs=line.split('\t')
   if vs[0].startswith('!Sample'):rows.setdefault(vs[0],[]).append([v.strip('"') for v in vs[1:]])
  samples=rows['!Sample_geo_accession'][0];hits=[];labels=collections.Counter()
  for i,sample in enumerate(samples):
   meta={k:[v[i] for v in vv] for k,vv in rows.items()}
   ch=meta.get('!Sample_characteristics_ch1',[])
   for s in ch:
    if any(q in s.lower() for q in ['histolog','diagnosis','disease','cancer type']):labels[s]+=1
   if any(q in json.dumps(meta).lower() for q in ['extraskeletal','chondrosarcoma','nr4a3','myxoid']):hits.append({'sample':sample,'characteristics':ch,'title':meta.get('!Sample_title')})
  summary.append({'platform':platform,'n':len(samples),'histologies':dict(labels),'hits':hits,'characteristics_fields':[v[0] for v in rows.get('!Sample_characteristics_ch1',[])]})
 except Exception as e:r.update(error_type=type(e).__name__,error=str(e))
 receipts.append(r)
(BASE/'asano-platform-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
(BASE/'asano-eligibility.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(receipts,indent=2));print(json.dumps(summary,indent=2)[:10000])
