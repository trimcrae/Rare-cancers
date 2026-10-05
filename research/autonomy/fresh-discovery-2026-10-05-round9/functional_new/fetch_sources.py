#!/usr/bin/env python3
"""Bounded ordinary public API authentication scout. No response-value analysis."""
import concurrent.futures, datetime, hashlib, json, pathlib, urllib.parse, urllib.request
BASE = pathlib.Path(__file__).resolve().parent
RAW = BASE / 'raw-cache'
RAW.mkdir(exist_ok=True)
API = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
QUERIES = {
 'emc-functional': '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "NR4A3" OR "CHN-Tec" OR "EWS-TEC") AND (perturbation OR organoid OR proteomic OR phosphoproteomic OR metabolism OR "drug response" OR "ex vivo" OR CRISPR) AND FIRST_PDATE:[2025-01-01 TO 2026-10-05]',
 'sarcoma-functional-new': 'sarcoma AND ("phosphoproteomics" OR "metabolic profiling" OR "functional precision" OR "ex vivo perturbation") AND FIRST_PDATE:[2025-01-01 TO 2026-10-05]',
 'civo-metadata': 'TITLE:"Multiplexed Evaluation of Microdosed"',
}
TASKS = [(name+'.json', API+'search?'+urllib.parse.urlencode({'query':q,'resultType':'core','format':'json','pageSize':1000})) for name,q in QUERIES.items()]
TASKS.append(('qpop2025-supp.zip',API+'PMC11929909/supplementaryFiles'))
def fetch(task):
 name,url=task; rec={'file':'raw-cache/'+name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-research-source-authentication/1.0'})
  with urllib.request.urlopen(req,timeout=35) as r:
   rec.update(status=r.status,content_type=r.headers.get('Content-Type'),content_length=r.headers.get('Content-Length'))
   b=r.read(60*1024*1024+1)
   if len(b)>60*1024*1024: raise RuntimeError('bounded request exceeded60MiB; lead larger-stage decision required')
  (RAW/name).write_bytes(b); rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if name.endswith('.json'):
   d=json.loads(b); rec.update(hit_count=d.get('hitCount'),returned=len(d.get('resultList',{}).get('result',[])))
   compact=[{k:x.get(k) for k in ('id','source','pmid','pmcid','doi','title','firstPublicationDate','isOpenAccess')} for x in d.get('resultList',{}).get('result',[])]
   (BASE/(name.replace('.json','-metadata.json'))).write_text(json.dumps(compact,indent=2)+'\n')
 except Exception as e: rec['error']=str(e)
 return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rec=list(pool.map(fetch,TASKS))
 (BASE/'RETRIEVAL.json').write_text(json.dumps({'queries':QUERIES,'requests':rec},indent=2)+'\n')
 print(json.dumps(rec,indent=2))
