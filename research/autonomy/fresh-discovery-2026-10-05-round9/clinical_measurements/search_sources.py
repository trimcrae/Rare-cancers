"""Ordinary quiet EPMC source discovery; detailed raw responses ignored, compact citations exported."""
from pathlib import Path
import urllib.request,urllib.parse,json,datetime,hashlib,concurrent.futures
ROOT=Path(__file__).resolve().parent
QUERIES={
 'numeric_fulltext':'"extraskeletal myxoid chondrosarcoma" AND (RECIST OR "target lesion" OR "tumor burden" OR rechallenge OR discontinuation OR discordant OR "growth rate")',
 'broader_trials':'"extraskeletal myxoid chondrosarcoma" AND ("phase I" OR "phase 1" OR basket OR precision OR "dose escalation" OR "targeted therapy")',
 'titleabstract_trajectory':'TITLE_ABS:("extraskeletal myxoid chondrosarcoma") AND (response OR treatment OR serial OR progression OR imaging)',
 'historical_aliases':'TITLE_ABS:("myxoid chondrosarcoma") AND ("phase I" OR "phase 1" OR basket OR precision OR rechallenge OR "target lesion" OR RECIST)',
}
def fetch(item):
 name,query=item;cursor='*';rows=[];receipts=[]
 for page in range(12):
  params={'query':query,'format':'json','resultType':'core','pageSize':100,'cursorMark':cursor};url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(params);rec={'query':query,'name':name,'page':page,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url}
  try:
   with urllib.request.urlopen(url,timeout=35) as response:b=response.read(8000001);rec['http_status']=response.status
   assert len(b)<8000001
   path=ROOT/'source-cache'/f'{name}-{page}.json';path.write_bytes(b);j=json.loads(b);rec.update(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),hitCount=j['hitCount'],returned=len(j['resultList']['result']));rows.extend(j['resultList']['result']);receipts.append(rec)
   nxt=j.get('nextCursorMark');
   if not nxt or nxt==cursor or len(rows)>=j['hitCount']:break
   cursor=nxt
  except Exception as e:rec['error']=type(e).__name__+':'+str(e);receipts.append(rec);break
 compact=[{k:r.get(k) for k in ['id','source','pmid','pmcid','doi','title','authorString','pubYear','journalTitle','isOpenAccess','inPMC','hasSuppl','firstPublicationDate']} for r in rows]
 return name,compact,receipts
if __name__=='__main__':
 assert hashlib.sha256((ROOT/'PLAN-FROZEN.json').read_bytes()).hexdigest()=='643d2a1d3638d22c447a87aa9a047181ff600a4d86aafc59b54741dec92b7b60'
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,QUERIES.items()))
 catalog={};receipts=[]
 for name,rows,rs in results:
  receipts.extend(rs)
  for r in rows:
   key=(r['source'],r['id']);x=catalog.setdefault(key,{**r,'query_families':[]});x['query_families'].append(name)
 ROOT.joinpath('SOURCE-DISCOVERY.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queries':QUERIES,'citations':list(catalog.values()),'query_receipts':receipts,'not_evaluation':'Citation metadata/discovery is not full-source or individual-condition evaluation.'},indent=2)+'\n')
 print(json.dumps({'counts':{n:len(rr) for n,rr,_ in results},'unique':len(catalog),'receipts':[{k:r.get(k) for k in ['name','page','hitCount','returned','error']} for r in receipts]}))
