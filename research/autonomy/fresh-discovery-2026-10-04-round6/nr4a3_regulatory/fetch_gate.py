"""Bounded primary metadata/fulltext retrieval for the frozen regulatory gate."""
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json, hashlib, datetime, shutil
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
queries={
 'epmc-emc-regulatory.json':'("extraskeletal myxoid chondrosarcoma" OR "EWS-TEC" OR "EWS/TEC") AND (chromatin OR knockdown OR silencing OR transcriptional OR ChIP OR perturbation)',
 'epmc-fusion-regulatory.json':'(NR4A3 OR NOR1 OR CHN) AND (EWSR1 OR EWS OR TAF15) AND (chromatin OR knockdown OR silencing OR CRISPR OR ATAC OR ChIP)',
 'epmc-authentic-models.json':'("USZ20" OR "USZ22" OR "USZ23" OR "NCC-EMC1-C1" OR "H-EMC-SS" OR "V1-3") AND (NR4A3 OR chondrosarcoma)',
}
targets={n:'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':q,'format':'json','resultType':'core','pageSize':1000}) for n,q in queries.items()}
targets['frenkel-prodatac.xml']='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13105821/fullTextXML'
def fetch(it):
 name,url=it; out={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  assert shutil.disk_usage(ROOT).free > 10*1024**3+4*1024**2
  with urlopen(Request(url,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=45) as r:
   b=r.read(4*1024**2+1);assert len(b)<=4*1024**2
   out.update(status=r.status,final_url=r.url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  (ROOT/name).write_bytes(b)
 except Exception as e:out['error']=str(e)
 return out
with ThreadPoolExecutor(max_workers=4) as pool: receipts=list(pool.map(fetch,targets.items()))
(ROOT/'retrieval.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
(ROOT/'queries.json').write_text(json.dumps(queries,indent=2)+'\n',encoding='utf-8')
for x in receipts:print({k:v for k,v in x.items() if k not in ['url','final_url']})
