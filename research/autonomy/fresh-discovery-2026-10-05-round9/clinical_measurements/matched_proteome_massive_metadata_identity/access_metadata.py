#!/usr/bin/env python3
from pathlib import Path
import sys,json,datetime,hashlib,urllib.request,urllib.error
P=Path(__file__).resolve().parent
stage=sys.argv[1];plan=json.loads((P/('PLAN-FROZEN.json' if stage=='01' else 'ROUTE-'+stage+'-FROZEN.json')).read_text());route=plan['before_access_branch'] if stage=='01' else plan['route']
a={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'url':route['url'],'purpose':route['purpose'],'cap':route['cap'],'timeout_seconds':10,'auth':'anonymous;no credentials/cookies/tokens'}
try:
 req=urllib.request.Request(route['url'],headers={'User-Agent':'EMC-public-source-review/1.0'})
 with urllib.request.urlopen(req,timeout=10) as r:
  a.update(status=r.status,content_type=r.headers.get('Content-Type'),final_url=r.url)
  data=r.read(route['cap']+1)
  if len(data)>route['cap']:a['error']='cap exceeded;0acceptedbytes'
  elif r.status!=200:a['error']='unexpected response;stopped'
  elif any(x in r.url.lower() for x in ['/login','/signin','/challenge']):a['error']='login/challenge;stopped'
  else:
   f=P/'raw-cache'/('stage-'+stage+'.source');f.write_bytes(data);a.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),cache_path=str(f))
except urllib.error.HTTPError as e:a.update(status=e.code,error='HTTP Error;no retry')
except Exception as e:a['error']=type(e).__name__+';no retry'
(P/('ACCESS-'+stage+'.json')).write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
