from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import urllib.request,urllib.parse,json,hashlib
p=Path(__file__).resolve().parent
plan=json.loads((p/'PLAN-FROZEN.json').read_text())
def run(v):
 i,q=v;url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'lite','pageSize':100})
 receipt={'query_index':i,'query':q,'url':url,'utc':datetime.now(timezone.utc).isoformat(),'timeout_seconds':10}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex public research source review'}),timeout=10) as f:
   raw=f.read(8*1024*1024+1);receipt['status']=f.status
  if len(raw)>8*1024*1024:raise ValueError('metadata response cap exceeded')
  name=f'query-{i}.json';(p/'raw-cache'/name).write_bytes(raw);data=json.loads(raw)
  receipt.update({'raw_path':'raw-cache/'+name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'hit_count':data.get('hitCount'),'returned':len(data.get('resultList',{}).get('result',[]))})
  cards=[{k:r.get(k) for k in plan['metadata_fields_only'] if k in r} for r in data.get('resultList',{}).get('result',[])]
  return receipt,cards
 except Exception as e:
  receipt.update({'access_error':type(e).__name__+': '+str(e),'decision':'No retry; metadata source gap retained.'});return receipt,[]
with ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(run,enumerate(plan['queries'],1)))
(p/'QUERY-RECEIPTS.json').write_text(json.dumps([x[0] for x in out],indent=2)+'\n')
(p/'raw-cache'/'safe-title-projection.json').write_text(json.dumps([{'query_index':x[0]['query_index'],'rows':x[1]} for x in out],indent=2)+'\n')
for receipt,cards in out:
 print(json.dumps(receipt))
 for r in cards:print(json.dumps(r))
