"""Bounded public-source retrieval; original bytes, URL, date, status and hash retained."""
from pathlib import Path
import urllib.request, urllib.error, datetime, hashlib, json, shutil, concurrent.futures
BASE=Path(__file__).resolve().parent
SOURCES={
 'gse213065.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE213065&targ=gsm&form=text&view=full',
 'gse212527.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE212527&targ=gsm&form=text&view=full',
 'gse212526.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE212526&targ=gsm&form=text&view=full',
 'subramanian2024.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11058033/fullTextXML',
 'bostongene-patients.html':'https://www.bostongene.com/patients/meet-our-patients',
 'bostongene-jsmo2025.html':'https://bostongene.com/news-and-publications/news/bostongene-to-showcase-multi-modal-ai-powered-platform-at-the-22nd-annual-meeting-of-the-japanese-society-of-medical-oncology',
}
def one(item):
 name,url=item
 if (BASE/name).exists():
  data=(BASE/name).read_bytes();return dict(name=name,url=url,status='local_reuse',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 rec=dict(name=name,url=url,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-research-evidence/1.0'})
  with urllib.request.urlopen(req,timeout=45) as r:
   data=r.read(8*1024*1024+1);rec.update(status=r.status,content_type=r.headers.get('Content-Type'),final_url=r.url)
  if len(data)>8*1024*1024:raise ValueError('Per-source 8MiB limit')
  if shutil.disk_usage(BASE).free-len(data)<10*1024**3:raise ValueError('Headroom gate')
  (BASE/name).write_bytes(data);rec.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e:rec.update(error=str(e))
 return rec
if __name__=='__main__':
 before=shutil.disk_usage(BASE).free
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: rows=list(ex.map(one,SOURCES.items()))
 out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free_before=before,sources=rows)
 (BASE/'retrieval.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps(out,indent=2))
