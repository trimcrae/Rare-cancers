#!/usr/bin/env python3
"""Focused public primary bibliographic source gate. No clinical/analyte outcomes."""
import concurrent.futures,datetime,hashlib,json,urllib.request,urllib.parse,shutil
from pathlib import Path
p=Path(__file__).resolve().parent;cache=p/'source-cache';cache.mkdir(exist_ok=True)
assert shutil.disk_usage(p).free>=10737418240
queries=[
 ('explicit-EMC-blood','("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "extraosseous myxoid chondrosarcoma" OR EMCS) AND (plasma OR serum OR "liquid biopsy" OR circulating OR ctDNA OR cfDNA OR microRNA OR miRNA OR metabolomic)'),
 ('broader-sarcoma-circulating','sarcoma AND ("circulating tumor DNA" OR "circulating tumour DNA" OR ctDNA OR "liquid biopsy")'),
 ('broader-sarcoma-circulating-RNA','sarcoma AND ("circulating microRNA" OR "circulating miRNA" OR "serum microRNA" OR "plasma microRNA" OR "serum biomarkers" OR "plasma biomarkers")')]
def get(row):
 n,query=row;u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':query,'format':'json','resultType':'core','pageSize':'1000'})
 q=cache/n;assert not q.exists();r={'key':n,'query':query,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cap_bytes':12582912}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'EMC-circulating-source-gate/1.0'}),timeout=30) as response:b=response.read(12582913);r['http']=response.status
  if len(b)>12582912:r['status']='cap exceeded; body not retained; query unresolved'
  else:
   q.write_bytes(b);d=json.loads(b);r.update({'status':'metadata returned; not full primary eligibility or outcome analysis','path':'source-cache/'+n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'hit_count':d['hitCount'],'returned':len(d['resultList']['result'])})
 except Exception as e:r['status']='query/access failure; no absence inference';r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:r=list(ex.map(get,queries))
assert sum(x.stat().st_size for x in cache.iterdir() if x.is_file())<=67108864
q=p/'METADATA-QUERY-RECEIPTS.json';assert not q.exists();q.write_text(json.dumps(r,indent=2)+'\n')
for x in r:print(json.dumps({k:v for k,v in x.items() if k not in ['query','url']}))
