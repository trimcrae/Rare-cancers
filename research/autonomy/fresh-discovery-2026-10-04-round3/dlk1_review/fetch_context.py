from pathlib import Path
import urllib.request,hashlib,json,shutil,xml.etree.ElementTree as ET
from datetime import datetime,timezone

base=Path(__file__).parent
assert shutil.disk_usage(base).free>10*1024**3+2*1024**2
sources=[('acc2024.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11482787/fullTextXML'),('neuroblastoma2024-metadata.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:39454577&format=json&resultType=core')]
receipts=[]
for name,url in sources:
 r=urllib.request.urlopen(url,timeout=45);b=r.read()
 assert len(b)<1024**2
 (base/name).write_bytes(b)
 receipts.append({'url':url,'path':name,'status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'retrieved_utc':datetime.now(timezone.utc).isoformat()})
(base/'context-source-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
r=ET.fromstring((base/'acc2024.xml').read_bytes())
out=[]
for p in r.findall('.//p')+r.findall('.//table-wrap'):
 t=' '.join(''.join(p.itertext()).split())
 if any(w in t.casefold() for w in ['sarcoma','metastatic cancer','data availability','hartwig','su2c','normal tissues','neuroendocrine']):out.append(t)
(base/'acc2024-relevant-text.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print([(x['path'],x['bytes'],x['status']) for x in receipts])
print('\n'.join(t[:2400] for t in out[:9]))
