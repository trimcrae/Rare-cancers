from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json,hashlib,xml.etree.ElementTree as ET
p=Path(__file__).resolve().parent
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def run(q):
 d={'name':q['name'],'url':q['url'],'utc':datetime.now(timezone.utc).isoformat(),'timeout_seconds':10,'redirects':False,'anonymous':True,'cap':q['cap']}
 try:
  with urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(q['url'],headers={'User-Agent':'Codex public source metadata review'}),timeout=10) as f:
   raw=f.read(q['cap']+1);d.update({'status':f.status,'content_type':f.headers.get('Content-Type')})
  if len(raw)>q['cap']:raise ValueError('response cap exceeded; no source accepted')
  name=q['name']+'.source';(p/'raw-cache'/name).write_bytes(raw);d.update({'raw_path':'raw-cache/'+name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
  r=ET.fromstring(raw);d['root_schema']=r.tag;d['accepted']=r.tag in ['article','pmc-articleset','PubmedArticleSet']
 except Exception as e:d.update({'accepted':False,'error':type(e).__name__+': '+str(e)})
 return d
routes=json.loads((p/'ROUTES-FROZEN.json').read_text())['routes']
with ThreadPoolExecutor(max_workers=4) as ex:r=list(ex.map(run,routes))
(p/'SOURCE-ACCESS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
