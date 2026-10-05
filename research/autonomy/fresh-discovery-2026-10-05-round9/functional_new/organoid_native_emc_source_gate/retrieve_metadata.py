import pathlib,json,hashlib,datetime,concurrent.futures,urllib.request,urllib.parse,urllib.error
p=pathlib.Path(__file__).resolve().parent
queries={'exact_emc_organoid':'("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "extraosseous myxoid chondrosarcoma") AND (organoid OR tumoroid OR "living biobank")','recent_sarcoma_organoid':'TITLE_ABS:(sarcoma) AND TITLE_ABS:(organoid OR tumoroid OR "living biobank") AND FIRST_PDATE:[2024-01-01 TO 2026-10-05]'}
def run(q):
 key,value=q;url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':value,'format':'json','resultType':'core','pageSize':100})
 try:
  with urllib.request.urlopen(url,timeout=30) as resp:status=resp.status;body=resp.read(4*1024*1024+1)
 except urllib.error.HTTPError as err:status=err.code;body=err.read(4*1024*1024+1)
 raw=p/'raw-cache'/f'{key}.json';raw.write_bytes(body);j=json.loads(body) if status==200 else{};rows=j.get('resultList',{}).get('result',[])
 rec={'key':key,'query':value,'url':url,'status':status,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'hit_count':j.get('hitCount'),'returned':len(rows),'cache':str(raw),'scope':'Titles/DOIs/PMID/PMC/year/source links only; abstracts and outcomes not evaluated.'}
 titles=[{'pmid':x.get('id'),'pmcid':x.get('pmcid'),'doi':x.get('doi'),'title':x.get('title'),'year':x.get('pubYear')} for x in rows]
 return rec,titles
out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for rec,titles in ex.map(run,queries.items()):out.append(rec);print(rec['key'],json.dumps(titles))
(p/'METADATA-SEARCH-RECEIPTS.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queries':out},indent=2)+'\n')
