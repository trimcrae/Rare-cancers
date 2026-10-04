from pathlib import Path
import json,hashlib,datetime,shutil
from urllib.request import urlopen,Request
from urllib.parse import urlencode
root=Path(__file__).resolve().parent
assert shutil.disk_usage(root).free>10*1024**3+2*1024**2
url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':'DOI:10.1016/j.cancergencyto.2003.11.011','resultType':'core','format':'json'})
rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'name':'six3-contrary2004.json'}
try:
 with urlopen(Request(url,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=30) as r:b=r.read(512*1024);rec['status']=r.status
 (root/rec['name']).write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 for x in json.loads(b)['resultList']['result']: print(json.dumps({k:x.get(k) for k in ['id','doi','title','abstractText','fullTextUrlList']},ensure_ascii=False))
except Exception as e:rec['error']=str(e)
(root/'six3-contrary-retrieval.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rec))