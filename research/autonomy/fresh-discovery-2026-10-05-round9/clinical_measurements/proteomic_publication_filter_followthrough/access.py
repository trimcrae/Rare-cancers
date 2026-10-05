#!/usr/bin/env python3
from pathlib import Path
import json,urllib.request,urllib.error,datetime,hashlib,time,sys
P=Path(__file__).resolve().parent;stage=sys.argv[1];plan=json.loads((P/('ROUTE-'+stage+'-FROZEN.json')).read_text());r=plan['route'];rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'url':r['url'],'method':r.get('method','GET'),'purpose':r['purpose'],'cap':r['cap'],'timeout_seconds':10,'anonymous':True,'automatic_redirects':False};start=time.monotonic()
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
try:
 if datetime.datetime.now(datetime.timezone.utc).isoformat()>='2026-10-05T21:44:02+00:00':raise TimeoutError('strictsourcecutoff')
 req=urllib.request.Request(r['url'],method=r.get('method','GET'),headers={'User-Agent':'EMC-public-source-review/1.0'});op=urllib.request.build_opener(NoRedirect)
 with op.open(req,timeout=10) as res:
  rec.update(status=res.status,content_type=res.headers.get('Content-Type'));b=res.read(r['cap']+1)
  if len(b)>r['cap']:raise RuntimeError('capexceeded;0acceptedbytes')
  if time.monotonic()-start>10:raise TimeoutError('overall10secondbound')
  f=P/'raw-cache'/('stage-'+stage+'.source');f.write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),cache_path=str(f),complete_response=True)
except urllib.error.HTTPError as e:rec.update(status=e.code,location=e.headers.get('Location'),error='HTTP Error;no retry/autoredirect',complete_response=False)
except Exception as e:rec.update(error=type(e).__name__+':'+str(e),complete_response=False)
rec['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(P/('ACCESS-'+stage+'.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
