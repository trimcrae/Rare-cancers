from pathlib import Path
import urllib.request,hashlib,json,datetime,shutil
D=Path(__file__).resolve().parent
R=D.parents[1]/'fresh-discovery-2026-10-04-round2'/'genomics'
def fetch(url,name,limit=10000000):
 rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'name':name}
 try:
  assert shutil.disk_usage('C:/').free>=10*1024**3+limit
  assert sum(p.stat().st_size for p in D.rglob('*') if p.is_file())+limit<30*1024**2
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-public-evidence-research'})
  with urllib.request.urlopen(req,timeout=40) as f:b=f.read(limit+1);rec['status']=f.status
  if len(b)>limit:raise ValueError('Response exceeds bounded source budget; not saved')
  (D/name).write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:rec['error']=str(e)
 with (D/'receipts.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(rec)+'\n')
 return rec
