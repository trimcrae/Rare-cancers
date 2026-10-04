import concurrent.futures,datetime,hashlib,json,pathlib,shutil,urllib.request
D=pathlib.Path(__file__).resolve().parent
JOBS={
 'kessler2022.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC8717183.1/PMC8717183.1.xml',
 'kessler2022-s3-list.xml':'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC8717183.1/',
 'lanzafame2024-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.2967/jnumed.123.267248&format=json',
 'koerber2021-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1007/s00259-021-05374-4&format=json'
}
def get(item):
 name,url=item;rec={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};assert shutil.disk_usage(D).free>=10*1024**3
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-evidence/1.0'}),timeout=35) as r:
   b=r.read(3*1024**2+1);rec.update(status=r.status,final_url=r.url)
  if len(b)>3*1024**2:raise ValueError('over3MiB/sourcecap')
  (D/name).write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:rec['error']=str(e)
 return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(get,JOBS.items()))
 (D/'fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
