import urllib.request, pathlib, json, hashlib, time, datetime, zipfile, io
p=pathlib.Path(__file__).parent
urls=[('ctsd2026.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13429570/fullTextXML'),('ctsd2026-supp.zip','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13429570/supplementaryFiles'),('ohba.html','https://acsjournals.onlinelibrary.wiley.com/doi/full/10.1002/cncr.20468'),('xlrd-pypi.json','https://pypi.org/pypi/xlrd/2.0.2/json')]
for name,url in urls:
 t=time.monotonic();r={'url':url,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=45) as f:b=f.read();r.update(status=f.status,final_url=f.url,content_type=f.headers.get('Content-Type'))
  (p/'sources'/name).write_bytes(b);r.update(path='sources/'+name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if name=='xlrd-pypi.json':
   wheel=next(x for x in json.loads(b)['urls'] if x['filename'].endswith('.whl'))
   with urllib.request.urlopen(wheel['url'],timeout=30) as f:w=f.read()
   assert hashlib.sha256(w).hexdigest()==wheel['digests']['sha256']
   (p/'sources'/wheel['filename']).write_bytes(w)
   r['reader_wheel']={'url':wheel['url'],'path':'sources/'+wheel['filename'],'sha256':hashlib.sha256(w).hexdigest()}
 except Exception as e:r['error']=repr(e)
 r['elapsed_seconds']=time.monotonic()-t
 with (p/'retrieval-log.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(r)+'\n')
 print(json.dumps(r),flush=True)
