#!/usr/bin/env python3
from pathlib import Path
import urllib.request,urllib.error,json,hashlib,datetime
P=Path(__file__).resolve().parent
plan=json.loads((P/'PLAN-FROZEN.json').read_text());receipts=[];schema=[]
for i,r in enumerate(plan['routes']):
 rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':r['url'],'cap':r['cap'],'timeout_seconds':10,'request':'anonymous metadata GET'}
 try:
  req=urllib.request.Request(r['url'],headers={'Accept':'application/json','User-Agent':'EMC-public-source-review/1.0'})
  with urllib.request.urlopen(req,timeout=10) as res:
   rec['status']=res.status;rec['content_type']=res.headers.get('Content-Type');data=res.read(r['cap']+1)
   if len(data)>r['cap']:rec['error']='cap exceeded; unaccepted';receipts.append(rec);break
   if res.status!=200 or 'json' not in (rec['content_type'] or '').lower():rec['error']='unexpected shape/content; stopped host';receipts.append(rec);break
  dest=P/'raw-cache'/('exact-query-'+str(i)+'.json');dest.write_bytes(data)
  rec.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),cache_path=str(dest))
  obj=json.loads(data)
  row={'request_index':i,'root_type':type(obj).__name__}
  if isinstance(obj,list):row.update(returned=len(obj),first_record_keys=list(obj[0].keys()) if obj and isinstance(obj[0],dict) else [])
  elif isinstance(obj,dict):row['root_keys']=list(obj.keys())
  schema.append(row)
 except urllib.error.HTTPError as e:
  rec['status']=e.code;rec['error']='HTTP Error';receipts.append(rec)
  if e.code in [401,403]:break
  continue
 except Exception as e:rec['error']=type(e).__name__;receipts.append(rec);continue
 receipts.append(rec)
(P/'ACCESS.json').write_text(json.dumps(receipts,indent=2)+'\n')
(P/'RESPONSE-SCHEMA.json').write_text(json.dumps(schema,indent=2)+'\n')
print(json.dumps(receipts,indent=2));print(json.dumps(schema,indent=2))
