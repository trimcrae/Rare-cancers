#!/usr/bin/env python3
"""Quiet ordinary public source retrieval; bounded bytes, no array expression analysis."""
import argparse,concurrent.futures,datetime,hashlib,json,pathlib,urllib.request,urllib.error
P=pathlib.Path(__file__).resolve().parent; C=P/'.cache';C.mkdir(exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['initial','supplement','urls']);ap.add_argument('--url');ap.add_argument('--name');ap.add_argument('--cap',type=int,default=2*1024*1024);args=ap.parse_args()
def get(job):
 name,url,method,cap=job;utc=datetime.datetime.now(datetime.timezone.utc).isoformat();rec={'name':name,'url':url,'method':method,'utc':utc,'cap':cap}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,method=method,headers={'User-Agent':'EMC-research-source-gate/1'}),timeout=40) as r:
   rec.update(status=r.status,final_url=r.geturl(),headers={k:v for k,v in r.headers.items() if k.lower() in ['content-type','content-length','content-disposition','last-modified','etag','x-ratelimit-remaining']})
   if method=='HEAD':rec['retained_bytes']=0;return rec
   size=0;chunks=[]
   while True:
    part=r.read(65536)
    if not part:break
    size+=len(part)
    if size>cap:rec['status_note']='bounded body exceeded cap; no complete-source claim';rec['seen_bytes']=size;return rec
    chunks.append(part)
   b=b''.join(chunks);f=C/name
   if f.exists():raise RuntimeError('Preserve existing original; choose a distinct request name')
   f.write_bytes(b);rec.update(retained_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),cache_path=str(f))
 except Exception as e:rec['error']=str(e)
 return rec
if args.phase=='initial':jobs=[('supplement-head','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11443197/supplementaryFiles','HEAD',0),('GSE243380-self.txt','https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE243380&targ=self&form=text&view=full','GET',1048576),('github-repo.json','https://api.github.com/repos/IzarLab/sarcoma-sn','GET',1048576),('github-contents.json','https://api.github.com/repos/IzarLab/sarcoma-sn/contents','GET',1048576)]
elif args.phase=='supplement':jobs=[('supplementaryFiles.zip','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11443197/supplementaryFiles','GET',args.cap)]
else:jobs=[(args.name,args.url,'GET',args.cap)]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:receipts=list(ex.map(get,jobs))
f=P/f'{args.phase}-receipts.json'
if f.exists():f=P/f'{args.phase}-receipts-{datetime.datetime.now().timestamp()}.json'
f.write_text(json.dumps(receipts,indent=2)+'\n')
for r in receipts:print(json.dumps({k:v for k,v in r.items() if k!='cache_path'}))
