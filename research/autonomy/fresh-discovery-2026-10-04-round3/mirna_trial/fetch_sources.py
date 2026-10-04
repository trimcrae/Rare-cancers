import urllib.request,json,hashlib,pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parent
SOURCES={
 'sponsor-june2026.html':'https://www.sec.gov/Archives/edgar/data/1829635/000110465926075440/tm2618153d1_ex99-1.htm',
 'esmo-oct2025.html':'https://www.sec.gov/Archives/edgar/data/1829635/000110465925099029/tm2528668d1_ex99-2.htm',
 'sponsor-sept2026.html':'https://www.sec.gov/Archives/edgar/data/1829635/000110465926111170/tm2626237d1_ex99-1.htm',
 'trial-NCT06260774.json':'https://clinicaltrials.gov/api/v2/studies/NCT06260774',
 'sponsor-june3-2026.html':'https://www.sec.gov/Archives/edgar/data/1829635/000110465926069810/tm2616719d1_ex99-1.htm',
}
out=[]
for name,url in SOURCES.items():
 r={'file':name,'url':url,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; academic research source evaluation)'})
  with urllib.request.urlopen(req,timeout=45) as response:
   data=response.read(3*1024*1024+1);r.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
  if len(data)>3*1024*1024: raise ValueError('3MiB scoped source limit')
  (ROOT/name).write_bytes(data);r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e:r['error']=str(e)
 out.append(r)
(ROOT/'source-receipts.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
