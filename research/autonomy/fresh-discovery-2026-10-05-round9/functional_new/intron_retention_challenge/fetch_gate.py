#!/usr/bin/env python3
"""Public supplement and endogenous-RBP primary metadata gate, never intron outcomes."""
import concurrent.futures,datetime,hashlib,json,pathlib,urllib.parse,urllib.request
BASE=pathlib.Path(__file__).resolve().parent;RAW=BASE/'raw-cache';RAW.mkdir(exist_ok=True)
Q='(TITLE:EWSR1 OR TITLE:TAF15 OR TITLE:"EWS protein" OR TITLE:"FET proteins" OR TITLE:"EWS-FLI1") AND (splicing OR "intron retention" OR "RNA binding")'
tasks=[('brenca2019-supp.zip','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6766969/supplementaryFiles'),('endogenous-rbp-metadata.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':Q,'resultType':'core','format':'json','pageSize':1000}))]
def fetch(x):
 n,u=x;r={'file':'raw-cache/'+n,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'primarymetadata/library/case eligibility or priorart only; no EMCIRdata'}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'EMC-native-RNA-source-prior-art/1.0'}),timeout=30) as a:b=a.read(25*1024*1024+1);r.update(status=a.status,content_type=a.headers.get('Content-Type'))
  if len(b)>25*1024*1024:raise ValueError('larger source stage needs lead authorization')
  (RAW/n).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if n.endswith('.json'):
   d=json.loads(b);r.update(hit_count=d.get('hitCount'),returned=len(d.get('resultList',{}).get('result',[])));compact=[{k:y.get(k) for k in ['pmid','pmcid','doi','title','firstPublicationDate','pubTypeList']} for y in d['resultList']['result']];(BASE/'RBP-METADATA.json').write_text(json.dumps(compact,indent=2)+'\n')
 except Exception as e:r['error']=str(e)
 return r
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:r=list(p.map(fetch,tasks))
 (BASE/'RETRIEVAL.json').write_text(json.dumps({'query':Q,'requests':r},indent=2)+'\n');print(json.dumps(r,indent=2))
