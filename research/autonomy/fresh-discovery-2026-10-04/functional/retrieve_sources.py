"""Small, public, read-only source retrieval. No bulk datasets or UI."""
from pathlib import Path
import json, hashlib, urllib.request, urllib.error, datetime, shutil
ROOT=Path(__file__).resolve().parent
URLS={
 'planaspaz2023.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10086583/fullTextXML',
 'planaspaz2026-elsevier.xml':'https://api.elsevier.com/content/article/pii/S0304383526000637?httpAccept=text/xml',
 'planaspaz2026-publisher.html':'https://www.sciencedirect.com/science/article/pii/S0304383526000637',
 'gse299349.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE299349&targ=self&form=text&view=full',
 'planaspaz2023-fig5.zip':'https://pmc.ncbi.nlm.nih.gov/articles/instance/10086583/bin/EMMM-15-e16863-s011.zip',
}
def main():
 receipts=[]
 for name,url in URLS.items():
  row={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if shutil.disk_usage(ROOT).free < 10*1024**3+50*1024**2:raise RuntimeError('Headroom guard')
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-research-public-reanalysis/1.0'}),timeout=30) as r:
    data=r.read(8*1024**2+1)
    if len(data)>8*1024**2:raise ValueError('Scoped source >8MiB, stopped')
    row.update(status=r.status,content_type=r.headers.get('Content-Type'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),final_url=r.url)
    (ROOT/name).write_bytes(data)
  except Exception as exc:row['error']=str(exc)
  receipts.append(row)
  print(json.dumps(row),flush=True)
 (ROOT/'source-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
