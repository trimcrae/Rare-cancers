import pathlib,json,urllib.request,urllib.parse,hashlib,datetime,concurrent.futures
P=pathlib.Path(__file__).resolve().parent;C=P/'source-cache'
queries={'emc_syndrome':'("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "NR4A3 sarcoma" OR "chondromyxoid sarcoma") AND (hypoglycemia OR hypoglycaemia OR "non-islet" OR "big IGF" OR "IGF-II" OR insulin-like)','historical_syndrome':'("myxoid chondrosarcoma" OR "chondromyxoid sarcoma" OR "chondrosarcoma") AND (hypoglycemia OR hypoglycaemia OR "non-islet" OR "big IGF")','emc_ligand':'("extraskeletal myxoid chondrosarcoma" OR "EWS/TEC" OR "EWS-TEC" OR "NR4A3 sarcoma") AND (IGF2 OR "IGF-II" OR "insulin-like growth factor 2" OR "insulin-like growth factor II")','syndrome_identity':'TITLE_ABS:(chondrosarcoma) AND (hypoglycemia OR hypoglycaemia OR "non-islet" OR "IGF-II")'}
def epmc(item):
 name,q=item;cur='*';pages=[];allrows=[]
 for i in range(12):
  url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':1000,'cursorMark':cur})
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-clinical-source-gate/1.0'})
  try:
   with urllib.request.urlopen(req,timeout=30)as r:b=r.read();status=r.status
   d=json.loads(b);f=C/f'{name}-{i}.json';f.write_bytes(b);rows=d.get('resultList',{}).get('result',[]);allrows+=rows;pages.append({'url':url,'status':status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'path':str(f.relative_to(P))});nxt=d.get('nextCursorMark')
   if not rows or nxt==cur or not nxt:break
   cur=nxt
  except Exception as e:pages.append({'url':url,'error':str(e)});break
 return {'name':name,'query':q,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hit_count':d.get('hitCount')if 'd'in locals()else None,'returned':len(allrows),'pages':pages,'results':allrows}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:out=list(pool.map(epmc,queries.items()))
(P/'SEARCH-RECEIPTS.json').write_text(json.dumps([{k:v for k,v in r.items()if k!='results'}for r in out],indent=2)+'\n')
for r in out:
 print(r['name'],r['hit_count'],r['returned'])
 for x in r['results']:
  title=x.get('title','');ab=x.get('abstractText','')
  if r['name']=='syndrome_identity' or (r['name']=='historical_syndrome' and any(a in title.lower()for a in ['hypogly','chondro','insulin','non-islet'])) or (r['name'].startswith('emc')and any(a in (title+' '+ab).lower()for a in ['hypogly','igf2','igf-ii','insulin-like'])):
   print(x.get('id'),x.get('pmcid'),x.get('doi'),title)
