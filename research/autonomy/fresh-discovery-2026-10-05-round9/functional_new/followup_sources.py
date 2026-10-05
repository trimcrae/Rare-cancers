#!/usr/bin/env python3
"""Identity and assay fields only; no new response analysis."""
import concurrent.futures,datetime,hashlib,json,pathlib,urllib.request
BASE=pathlib.Path(__file__).resolve().parent;RAW=BASE/'raw-cache';API='https://www.ebi.ac.uk/europepmc/webservices/rest/'
TASKS=[('integration2026.xml',API+'PMC13275902/fullTextXML'),('integration2026-supp.zip',API+'PMC13275902/supplementaryFiles'),('qpop2025.xml',API+'PMC11929909/fullTextXML'),('living2026-metadata.json',API+'search?query=EXT_ID%3A42333717%20AND%20SRC%3AMED&resultType=core&format=json'),('serum2025.xml',API+'PMC11817886/fullTextXML')]
def fetch(task):
 n,u=task;r={'file':'raw-cache/'+n,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'EMC-source-eligibility/1.0'}),timeout=30) as x:
   r.update(status=x.status,content_type=x.headers.get('Content-Type'));b=x.read(20*1024*1024+1)
   if len(b)>20*1024*1024:raise ValueError('larger-stage decision required')
  (RAW/n).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:r=list(pool.map(fetch,TASKS))
 (BASE/'FOLLOWUP-RETRIEVAL.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
