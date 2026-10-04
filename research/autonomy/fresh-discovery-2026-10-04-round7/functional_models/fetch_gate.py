"""Bounded primary repository/abstract discovery; no drug-response values."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,datetime,shutil
R=Path(__file__).resolve().parent
queries={
 'functional-primary.json':'("extraskeletal myxoid" OR "myxoid extraskeletal" OR "USZ20-EMC1" OR "USZ22-EMC2" OR "USZ23-EMC3" OR "NCC-EMC1-C1") AND (drug OR xenograft OR organoid OR screen OR viability OR knockdown)',
 'new-broader-functional.json':'(sarcoma AND (organoid OR "patient derived" OR tumoroid) AND (screen OR pharmacologic OR dependency)) AND FIRST_PDATE:[2025-01-01 TO 2026-10-04]',
 'chen2023-metadata.json':'DOI:10.1016/j.labinv.2022.100039 OR TITLE:"Addressing Modern Diagnostic Pathology for Patient-Derived Soft Tissue Sarcosphere Models"'
}
urls={n:'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':q,'resultType':'core','format':'json','pageSize':1000}) for n,q in queries.items()}
urls['S-CMO9316.json']='https://www.ebi.ac.uk/biostudies/api/v1/studies/S-CMO9316'
receipts=[]
def run(item):
 n,u=item;o={'file':n,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  assert shutil.disk_usage(R).free>10*1024**3+8*1024**2
  with urlopen(Request(u,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=30) as resp:
   b=resp.read(3*1024**2+1);assert len(b)<=3*1024**2;o.update(status=resp.status,final_url=resp.url)
  (R/n).write_bytes(b);o.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if n in queries:
   x=json.loads(b);o.update(hit_count=x['hitCount'],returned=len(x['resultList']['result']))
 except Exception as e:o['error']=str(e)
 return o
with ThreadPoolExecutor(max_workers=3) as pool:receipts=list(pool.map(run,urls.items()))
(R/'queries.json').write_text(json.dumps(queries,indent=2)+'\n',encoding='utf-8')
(R/'retrieval.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
for row in receipts:print({k:v for k,v in row.items() if k not in ['url','final_url']})