from pathlib import Path
import urllib.request,hashlib,json,datetime,zipfile,xml.etree.ElementTree as E
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
def fetch(i):
 ext='pdf'if i<6 else'docx';name=f'NIHMS2150030-supplement-{i}.{ext}';url=f'https://pmc.ncbi.nlm.nih.gov/articles/instance/13014529/bin/{name}';out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'filename':name}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30)as r:
   b=r.read(3*1024*1024+1);assert len(b)<=3*1024*1024;out.update(status=r.status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest());(P/name).write_bytes(b)
 except Exception as e:out['error']=str(e)
 return out
with ThreadPoolExecutor(max_workers=4)as ex:out=list(ex.map(fetch,range(1,9)))
(P/'fetch-immune-supplement-receipts.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
