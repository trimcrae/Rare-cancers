import urllib.request,urllib.parse,json,pathlib,datetime,hashlib,concurrent.futures
P=pathlib.Path(__file__).parent
C=P.parents[3]/'.cache'/'emc-r6-challenge'
C.mkdir(parents=True,exist_ok=True)
queries={
'physiology':'("extraskeletal myxoid chondrosarcoma" OR "NR4A3 sarcoma") AND (hypoglycemia OR IGF2 OR glucose OR lactate OR metabolomics OR metabolic OR ACTH OR Cushing OR catecholamine OR hormone)',
'kinetics':'("extraskeletal myxoid chondrosarcoma" OR "NR4A3 sarcoma") AND ("doubling time" OR "growth rate" OR untreated OR observation OR "spontaneous regression" OR "natural history")',
'historical_metabolic':'("myxoid chondrosarcoma" OR "chondromyxoid sarcoma") AND (hypoglycemia OR ACTH OR Cushing OR metabolomics OR catecholamine)',
}
def fetch(k,q):
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':1000})
 r=urllib.request.urlopen(url,timeout=45)
 b=r.read();(C/(k+'-search.json')).write_bytes(b)
 return {'key':k,'query':q,'url':url,'status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'date':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e: rows=list(e.map(lambda x:fetch(*x),queries.items()))
(P/'search-receipts.json').write_text(json.dumps(rows,indent=2)+'\n')
for k in queries:
 j=json.load(open(C/(k+'-search.json'))); print(k,'hits',j.get('hitCount'))
 for r in j.get('resultList',{}).get('result',[]):
  print(r.get('id'),r.get('pmcid'),r.get('doi'),r.get('title')); print((r.get('abstractText') or '')[:550])
