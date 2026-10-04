"""Bounded metadata retrieval. Does not download mass spectra or inspect proteins."""
from pathlib import Path
import json,urllib.request,hashlib,csv,io,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
def fetch(url,name,cap=5_000_000):
 if (P/name).exists():
  raw=(P/name).read_bytes()
  return raw,{'url':url,'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'verified_local_reuse':True}
 with urllib.request.urlopen(url,timeout=30) as r:
  raw=r.read(cap+1);typ=r.headers.get('Content-Type');final=r.url
 assert len(raw)<=cap,(name,'cap exceeded',len(raw))
 (P/name).write_bytes(raw)
 rec={'url':url,'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'type':typ,'final_url':final}
 return raw,rec
receipts=[]
for url,name in [
 ('https://pathdb.cancerimagingarchive.net/system/files/collectionmetadata/202407/cptac_metadata_07-09-2024.csv','cptac-all-metadata.csv'),
 ('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12409279/fullTextXML','procan-fdl2025.xml'),
 ('https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD054790/files?page=1&pageSize=100','panatlas-files-page1.json')]:
 try:
  raw,rec=fetch(url,name,8_000_000);receipts.append(rec);print(name,len(raw))
 except Exception as e:receipts.append({'url':url,'file':name,'error':str(e)});print(name,str(e))
(P/'retrievals-scout.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
if (P/'cptac-all-metadata.csv').exists():
 rows=list(csv.DictReader(io.StringIO((P/'cptac-all-metadata.csv').read_text(encoding='utf-8-sig'))))
 sar=[r for r in rows if r.get('Tumor')=='SAR']
 (P/'cptac-sar-all-rows.json').write_text(json.dumps(sar,indent=2),encoding='utf8')
 print('CPTAC fields',list(rows[0]));print('SAR rows',len(sar),'cases',len({r.get('Case_ID') for r in sar}))
if (P/'procan-fdl2025.xml').exists():
 r=ET.parse(P/'procan-fdl2025.xml').getroot()
 out=[]
 for e in r.iter():
  if e.tag in ['p','supplementary-material']:
   t=' '.join(' '.join(e.itertext()).split())
   if any(x in t.lower() for x in ['sarcoma','availability','data are','supplementary table 1','pxd']):
    out.append({'text':t,'links':[n.attrib for n in e.iter() if n.tag in ['ext-link','media']]})
 (P/'procan-fdl-source-excerpts.json').write_text(json.dumps(out,indent=2),encoding='utf8')
