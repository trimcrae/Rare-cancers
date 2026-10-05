#!/usr/bin/env python3
from pathlib import Path
import json,datetime,hashlib,urllib.request,urllib.error,sys
P=Path(__file__).resolve().parent;stage=sys.argv[1];plan=json.loads((P/('PLAN-FROZEN.json' if stage=='01' else 'ROUTE-'+stage+'-FROZEN.json')).read_text());r=plan['route']
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'url':r['url'],'purpose':r['purpose'],'cap':r['cap'],'timeout_seconds':10,'anonymous':True,'automatic_redirects':False}
try:
 op=urllib.request.build_opener(NoRedirect);req=urllib.request.Request(r['url'],headers={'User-Agent':'EMC-public-source-review/1.0'})
 with op.open(req,timeout=10) as res:
  rec.update(status=res.status,content_type=res.headers.get('Content-Type'));b=res.read(r['cap']+1)
  if len(b)>r['cap']:rec['error']='capexceeded;0acceptedbytes'
  else:
   f=P/'raw-cache'/('stage-'+stage+'.source');f.write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),cache_path=str(f))
except urllib.error.HTTPError as e:rec.update(status=e.code,location=e.headers.get('Location'),error='HTTPresponse;no retry/autoredirect')
except Exception as e:rec['error']=type(e).__name__+';no retry'
(P/('ACCESS-'+stage+'.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
