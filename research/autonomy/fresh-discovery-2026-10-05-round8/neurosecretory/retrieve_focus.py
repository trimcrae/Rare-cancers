"""Ordinary file/API retrieval of distinct neurosecretory prior-art sources, bounded cache."""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,urllib.request,xml.etree.ElementTree as ET,re
ROOT=Path(__file__).resolve().parent
SOURCES={
'PMC1868116':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC1868116/fullTextXML',
'PMC1402209':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC1402209/fullTextXML',
'PMC7102354':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7102354/fullTextXML',
'PMC7102355':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7102355/fullTextXML',
'PMC5929452':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5929452/fullTextXML',
'Barresi2025':'https://link.springer.com/article/10.1007/s00428-025-04352-7'
}
def one(x):
 k,url=x;rec={'id':k,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'ordinary permitted API/file request, default TLS/proxy; no browser'}
 try:
  with urllib.request.urlopen(url,timeout=35) as r:raw=r.read(12000001);rec.update(http_status=r.status,response_url=r.url)
  if len(raw)>12000000:rec.update(status='pending_larger_source',bytes_read=len(raw));return rec
  ROOT.joinpath('raw-cache',k+'.xml' if k.startswith('PMC') else k+'.html').write_bytes(raw);rec.update(status='retrieved',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  if k.startswith('PMC'):
   tree=ET.fromstring(raw);paras=[]
   for e in tree.iter():
    if e.tag in ['p','table-wrap']:
     t=' '.join(''.join(e.itertext()).split())
     if re.search(r'SLC18A|SLC6A2|VMAT[12]|vesicular monoamine|myxoid chondrosarcoma|SSTR2|somatostatin|MIBG|DOTATATE',t,re.I):paras.append({'element':e.tag,'id':e.get('id'),'text':t[:7500],'truncated':len(t)>7500})
   rec['focused_extracts']=paras
 except Exception as e:rec.update(status='unavailable',error=type(e).__name__+':'+str(e))
 return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(one,SOURCES.items()))
 ROOT.joinpath('FOCUSED-SOURCE-EXTRACTS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([{k:r.get(k) for k in ['id','status','bytes','error']} for r in rows]))
