#!/usr/bin/env python3
from pathlib import Path
import json,urllib.request,urllib.error,datetime,hashlib,time
P=Path(__file__).resolve().parent;plan=json.loads((P/'PLAN-FROZEN.json').read_text());a={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':plan['route'],'anonymous':True,'socket_timeout_seconds':10,'overall_seconds':10,'cap':33554432,'requests':1};terms=[b'10.1002/prca.201900054',b'31419061'];size=0;found=set();digest=hashlib.sha256();tail=b'';start=time.monotonic()
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
try:
 req=urllib.request.Request(plan['route'],headers={'Accept':'application/json','User-Agent':'EMC-public-source-review/1.0'});op=urllib.request.build_opener(NoRedirect)
 with op.open(req,timeout=10) as r:
  a.update(status=r.status,content_type=r.headers.get('Content-Type'))
  if r.status!=200 or 'json' not in (a['content_type'] or '').lower():raise RuntimeError('unexpectedresponse;stop')
  f=P/'raw-cache'/'metadata.source'
  with f.open('wb') as out:
   while True:
    if time.monotonic()-start>10:raise TimeoutError('overall10secondbound')
    if datetime.datetime.now(datetime.timezone.utc).isoformat()>='2026-10-05T20:47:00+00:00':raise TimeoutError('strictdeadline')
    b=r.read(65536)
    if not b:break
    size+=len(b)
    if size>33554432:raise RuntimeError('rawcap;stop')
    out.write(b);digest.update(b);scan=tail+b
    for term in terms:
     if term in scan:found.add(term.decode())
    tail=scan[-80:]
  a.update(bytes=size,sha256=digest.hexdigest(),cache_path=str(f),literal_citations_observed=sorted(found),complete_response=True)
except urllib.error.HTTPError as e:a.update(status=e.code,error='HTTP Error;no retry',complete_response=False)
except Exception as e:a.update(error=type(e).__name__+':'+str(e),complete_response=False,partial_bytes=size)
(P/'ACCESS.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
