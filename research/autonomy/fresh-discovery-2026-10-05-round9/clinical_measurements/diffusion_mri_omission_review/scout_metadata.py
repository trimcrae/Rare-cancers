#!/usr/bin/env python3
"""Metadata-only source discovery; do not display ADC/texture outcome values."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,urllib.parse,datetime,json,hashlib
b=Path(__file__).resolve().parent
queries={
 'disease_DWI':'("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "extraosseous myxoid chondrosarcoma" OR NR4A3) AND (diffusion OR "apparent diffusion coefficient" OR DWI OR ADC)',
 'explicit_EMC_DWI':'("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "extraosseous myxoid chondrosarcoma") AND (diffusion OR "apparent diffusion coefficient" OR DWI)',
 'myxoid_ADC_title':'TITLE:myxoid AND (diffusion OR "apparent diffusion coefficient" OR ADC)'
}
def one(k,q):
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':100})
 rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query_key':k,'query':q,'query_sha256':hashlib.sha256(q.encode()).hexdigest(),'url':u,'scope':'Sourceidentity metadata enumeration only, no abstract/caseADC outcomes displayed'}
 try:
  with urllib.request.urlopen(u,timeout=25) as z:d=z.read(5000000);rec.update(status=z.status,bytes=len(d),sha256=hashlib.sha256(d).hexdigest())
  (b/'source-cache'/(k+'.json')).write_bytes(d);x=json.loads(d);rows=x.get('resultList',{}).get('result',[]);rec.update(hitCount=x.get('hitCount'),returned=len(rows))
  print(json.dumps({'query':k,'hits':x.get('hitCount'),'returned':len(rows),'titles':[{'pmid':v.get('pmid'),'pmcid':v.get('pmcid'),'doi':v.get('doi'),'title':v.get('title')} for v in rows]},ensure_ascii=False))
 except Exception as e:rec['error']=repr(e)
 return rec
existing=json.loads((b/'QUERY-RECEIPTS.json').read_text()) if (b/'QUERY-RECEIPTS.json').exists() else []
known={a['query_key'] for a in existing if a.get('status')==200}
new=[(k,q) for k,q in queries.items() if k not in known]
with ThreadPoolExecutor(max_workers=2) as ex:records=existing+list(ex.map(lambda x:one(*x),new))
(b/'QUERY-RECEIPTS.json').write_text(json.dumps(records,indent=2)+'\n')
