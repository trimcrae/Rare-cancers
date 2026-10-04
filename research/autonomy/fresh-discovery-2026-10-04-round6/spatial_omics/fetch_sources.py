import json, hashlib, shutil, urllib.request, urllib.error, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FLOOR=10*1024**3
CAP=16*1024**2
SOURCES={
 'ngo2025.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12728484/fullTextXML',
 'cassis-report.html':'https://cordis.europa.eu/project/id/101064303/reporting',
 'cassis-results.html':'https://cordis.europa.eu/project/id/101064303/results',
 'cassis-project.html':'https://cordis.europa.eu/project/id/101064303',
 '3ca-sarcoma.html':'https://www.weizmann.ac.il/sites/3CA/sarcoma',
 'cellsarctx.html':'https://jitc.bmj.com/content/12/Suppl_2/A376',
}
def fetch(name,url):
 before=shutil.disk_usage(ROOT).free
 used=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
 row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'file':name,'free_before':before,'packet_bytes_before':used}
 try:
  if before<FLOOR+3*1024**2 or used>CAP-3*1024**2: raise RuntimeError('Storage gate')
  req=urllib.request.Request(url,headers={'User-Agent':'EMCResearch-source-audit/1.0'})
  with urllib.request.urlopen(req,timeout=40) as response:
   data=response.read(3*1024**2+1)
   if len(data)>3*1024**2: raise RuntimeError('Per-source 3 MiB limit')
   row.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
  (ROOT/name).write_bytes(data)
  row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e: row['error']=str(e)
 return row
if __name__=='__main__':
 rows=[fetch(k,v) for k,v in SOURCES.items()]
 (ROOT/'source-receipts.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 print(json.dumps([{k:v for k,v in x.items() if k in ['file','status','bytes','error']} for x in rows],indent=2))
