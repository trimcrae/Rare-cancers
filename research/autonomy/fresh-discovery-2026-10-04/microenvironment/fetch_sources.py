"""Bounded public source retrieval; records exact bytes, SHA256 and URL."""
from pathlib import Path
import urllib.request, hashlib, json, zipfile, io, xml.etree.ElementTree as ET
from datetime import datetime, timezone
BASE=Path(__file__).resolve().parent
SOURCES={
 'dancsok2020.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7153829/fullTextXML',
 'dancsok2020-public-supplements.zip':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7153829/supplementaryFiles'
}
def main():
 receipts=[]
 for name,url in SOURCES.items():
  p=BASE/name
  if not p.exists():
   with urllib.request.urlopen(url,timeout=45) as r:b=r.read(8000001)
   assert len(b)<=8000000
   p.write_bytes(b)
  b=p.read_bytes();receipts.append({'file':name,'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 z=zipfile.ZipFile(BASE/'dancsok2020-public-supplements.zip')
 for name in ['koni-09-01-1747340-g002.jpg','koni-09-01-1747340-g004.jpg']:
  (BASE/name).write_bytes(z.read(name))
 s=zipfile.ZipFile(io.BytesIO(z.read('koni-09-01-1747340-s001.zip')))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 out={}
 for name in s.namelist():
  if name.endswith('.docx'):
   d=ET.fromstring(zipfile.ZipFile(io.BytesIO(s.read(name))).read('word/document.xml'))
   out[name]={'paragraphs':[''.join(e.itertext()) for e in d.findall('.//w:p',ns)],
    'tables':[[[''.join(c.itertext()) for c in row.findall('w:tc',ns)] for row in t.findall('w:tr',ns)] for t in d.findall('.//w:tbl',ns)]}
 (BASE/'dancsok-supplement-extracted.json').write_text(json.dumps(out,indent=2,ensure_ascii=True)+'\n')
 (BASE/'source-receipts.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'sources':receipts},indent=2)+'\n')
 print(json.dumps({'sources':receipts,'extracted_documents':list(out)}))
if __name__=='__main__':main()
