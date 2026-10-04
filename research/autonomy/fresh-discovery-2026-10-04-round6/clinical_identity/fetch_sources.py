import pathlib,datetime,json,urllib.request,urllib.parse,hashlib,shutil,concurrent.futures
D=pathlib.Path(__file__).resolve().parent
queries={'timepoint':'EXT_ID:PMC11927082','hirmas2023':'DOI:10.2967/jnumed.122.264689','hirmas2024':'EXT_ID:38331453 AND SRC:MED','interobserver':'TITLE:"Interobserver Agreement" AND TITLE:"FAPI"','liver2026':'DOI:10.1007/s44178-026-00295-4'}
def get(item):
 name,url=item;rec={'file':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};assert shutil.disk_usage(D).free>=10*1024**3
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-clinical-source-audit/1.0'}),timeout=35) as r:
   b=r.read(3*1024**2+1);rec.update(status=r.status,final_url=r.url)
  if len(b)>3*1024**2:raise RuntimeError('3MiB per source cap exceeded')
  if sum(p.stat().st_size for p in D.rglob('*') if p.is_file())+len(b)>16*1024**2:raise RuntimeError('16MiB lane cap')
  (D/name).write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:rec['error']=str(e)
 return rec
if __name__=='__main__':
 jobs={k+'-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':v,'format':'json','resultType':'core'}) for k,v in queries.items()}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:out=list(p.map(get,jobs.items()))
 (D/'metadata-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 for x in out:
  print(x)
  if 'sha256' in x:
   j=json.loads((D/x['file']).read_text());print([{k:r.get(k) for k in ['id','pmcid','doi','title','isOpenAccess','hasSuppl']} for r in j.get('resultList',{}).get('result',[])])
