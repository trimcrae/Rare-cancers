from pathlib import Path
import urllib.request,json,hashlib,datetime,concurrent.futures
R=Path(__file__).resolve().parent
S=[('liu2026-pubmed.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:42128000&resultType=core&format=json'),('zhang2022-pubmed.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:36075176&resultType=core&format=json'),('liu2026-oup.html','https://academic.oup.com/bjr/article/99/1184/1598/8677614')]
def f(z):
 n,u=z;r={'file':n,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as q:b=q.read(1024**2+1);r.update(status=q.status,content_type=q.headers.get('Content-Type'))
  assert len(b)<=1024**2
  (R/n).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:o=list(pool.map(f,S))
(R/'clinical-metadata-receipts.json').write_text(json.dumps(o,indent=2));print(json.dumps(o))
