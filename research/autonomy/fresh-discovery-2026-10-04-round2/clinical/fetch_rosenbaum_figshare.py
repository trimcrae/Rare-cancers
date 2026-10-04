from pathlib import Path
import urllib.request,hashlib,json,datetime
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
def f(a):
 u=f'https://api.figshare.com/v2/articles/{a}';o={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'api':u,'id':a,'files':[]}
 try:
  b=urllib.request.urlopen(u,timeout=30).read();d=json.loads(b);(P/f'rosenbaum-figshare-{a}.json').write_bytes(b)
  o['title']=d['title']
  for x in d['files']:
   if x['size']>2*1024*1024:continue
   with urllib.request.urlopen(x['download_url'],timeout=30)as r:body=r.read(2*1024*1024+1)
   filename='rosenbaum-'+x['name'];(P/filename).write_bytes(body);o['files'].append({'name':filename,'url':x['download_url'],'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
 except Exception as e:o['error']=str(e)
 return o
with ThreadPoolExecutor(max_workers=3)as ex:out=list(ex.map(f,[32712453,32712450,32712447]))
(P/'rosenbaum-figshare-receipts.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
