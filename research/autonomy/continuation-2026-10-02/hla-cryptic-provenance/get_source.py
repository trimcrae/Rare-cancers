import sys,urllib.request,hashlib,json,datetime
from pathlib import Path
p=Path(__file__).parent
name,url=sys.argv[1:3]
r={'name':name,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
    with urllib.request.urlopen(url,timeout=25) as response:
        b=response.read(3000001);r.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
    if len(b)>3000000: raise ValueError('3MB response cap exceeded')
    (p/name).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
except Exception as e:r['error']=repr(e)
with (p/'retrievals.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(r)+'\n')
print(json.dumps(r))
