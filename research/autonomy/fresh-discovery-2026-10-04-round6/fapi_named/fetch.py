#!/usr/bin/env python3
"""Bounded ordinary HTTP requests. Preserve TLS/proxy; no retries or denied-route bypass."""
from pathlib import Path
import urllib.request,urllib.error,hashlib,json,datetime,concurrent.futures,sys
PACKET=Path(__file__).resolve().parent
CACHE=PACKET/'raw-cache'
CACHE.mkdir(exist_ok=True)
(PACKET/'.gitignore').write_text('raw-cache/\n')
BUDGET=64*1024*1024
MAX_FILE=16*1024*1024
JOBS=[
 ('kessler-epmc.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8717183/fullTextXML'),
 ('kratochwil-epmc.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6581228/fullTextXML'),
 ('kessler-ncbi.xml','https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC8717183'),
 ('lanzafame-crossref.json','https://api.crossref.org/works/10.2967/jnumed.123.267248'),
 ('pabst-crossref.json','https://api.crossref.org/works/10.1016/S1470-2045(25)00299-2'),
 ('pabst-epmc-metadata.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1016/S1470-2045(25)00299-2&format=json&resultType=core'),
]
def fetch(job):
 name,url=job; row={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'GET','source_route':'ordinary primary/API retrieval; distinct from recorded R5 failed URLs','user_agent':'EMC-research-evidence/1.0'}
 try:
  request=urllib.request.Request(url,headers={'User-Agent':row['user_agent']})
  try: response=urllib.request.urlopen(request,timeout=45)
  except urllib.error.HTTPError as e: response=e
  data=response.read(MAX_FILE+1)
  if len(data)>MAX_FILE: raise RuntimeError('per-file16MiB cap exceeded')
  row.update(status=response.status,final_url=response.geturl(),content_type=response.headers.get('Content-Type'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
  (CACHE/name).write_bytes(data)
  if response.status!=200: row['error_excerpt']=data[:300].decode('utf8','replace')
 except Exception as e: row['error']=str(e)
 return row
if __name__=='__main__':
 if len(sys.argv)>1: JOBS=json.loads(Path(sys.argv[1]).read_text())
 if sum(p.stat().st_size for p in CACHE.iterdir() if p.is_file())>BUDGET: raise RuntimeError('raw budget already exceeded')
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(fetch,JOBS))
 existing=PACKET/'ACCESS-RECEIPTS.json'
 prev=json.loads(existing.read_text()) if existing.exists() else []
 existing.write_text(json.dumps(prev+rows,indent=2)+'\n')
 for row in rows: print(row['name'],row.get('status'),row.get('bytes'),row.get('error'))
 print('cache_bytes',sum(p.stat().st_size for p in CACHE.iterdir() if p.is_file()))
