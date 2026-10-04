from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,datetime,shutil
R=Path(__file__).resolve().parent
q=json.loads((R/'queries.json').read_text(encoding='utf-8'))['new-broader-functional.json']
urls={'broader-title-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':q,'resultType':'lite','format':'json','pageSize':1000}),
'ala2022.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8761327/fullTextXML',
'inbrx2023.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10425732/fullTextXML',
'minopoli-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':'EXT_ID:32344648 AND SRC:MED','resultType':'core','format':'json'})}
def f(it):
 n,u=it;out={'file':n,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  assert shutil.disk_usage(R).free>10*1024**3+4*1024**2
  with urlopen(Request(u,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=30) as r:
   b=r.read(1024**2+1);assert len(b)<=1024**2,'bounded source exceeds1MiB';out['status']=r.status
  (R/n).write_bytes(b);out.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:out['error']=str(e)
 return out
with ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(f,urls.items()))
(R/'followup-retrieval.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))