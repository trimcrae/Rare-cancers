from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,datetime,shutil
R=Path(__file__).resolve().parent
broader=json.loads((R/'broader-title-metadata.json').read_text(encoding='utf-8'))
query=json.loads((R/'queries.json').read_text(encoding='utf-8'))['new-broader-functional.json']
mini=json.loads((R/'minopoli-metadata.json').read_text(encoding='utf-8'))['resultList']['result'][0]
urls={'broader-title-page2.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':query,'resultType':'lite','format':'json','pageSize':1000,'cursorMark':broader['nextCursorMark']}),
'minopoli2020.xml':f"https://www.ebi.ac.uk/europepmc/webservices/rest/{mini['pmcid']}/fullTextXML",
'precision2025.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11929909/fullTextXML',
'hdac2025.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12667636/fullTextXML',
'shared2026.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13273627/fullTextXML',
'shh2025.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12830980/fullTextXML',
'biomaterials2025-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':'EXT_ID:40652802 AND SRC:MED','resultType':'core','format':'json'}),
'bone2026.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13601131/fullTextXML'}
def f(it):
 n,u=it;o={'file':n,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  assert shutil.disk_usage(R).free>10*1024**3+4*1024**2
  with urlopen(Request(u,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=30) as x:b=x.read(768*1024+1);assert len(b)<=768*1024,'source exceeds768KiB';o['status']=x.status
  (R/n).write_bytes(b);o.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:o['error']=str(e)
 return o
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(f,urls.items()))
(R/'new-source-retrieval.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
for x in rows:print({k:v for k,v in x.items() if k!='url'})