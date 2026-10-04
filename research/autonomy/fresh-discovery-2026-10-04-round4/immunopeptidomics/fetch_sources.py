import concurrent.futures, datetime, hashlib, json, pathlib, shutil, urllib.request, urllib.error
D=pathlib.Path(__file__).resolve().parent
JOBS={
 'chs2026.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC13356665.1/PMC13356665.1.xml',
 'pediatric2021.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC8642810.1/PMC8642810.1.xml',
 'pleural2022.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC9114951.1/PMC9114951.1.xml',
 'jci2023.html':'https://insight.jci.org/articles/view/170324',
 'jci2023-supp.pdf':'https://df6sxcketz7bb.cloudfront.net/manuscripts/170000/170324/jci.insight.170324.sd.pdf',
}
def get(item):
 name,url=item; rec={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 assert shutil.disk_usage(D).free>10*1024**3
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-evaluation/1.0'})
  with urllib.request.urlopen(req,timeout=40) as r:
   b=r.read(3*1024**2+1); rec.update(status=r.status,final_url=r.url)
  if len(b)>3*1024**2: raise ValueError('source exceeds 3MiB source cap')
  (D/name).write_bytes(b); rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e: rec['error']=str(e)
 return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: out=list(pool.map(get,JOBS.items()))
 (D/'fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps(out,indent=2))
