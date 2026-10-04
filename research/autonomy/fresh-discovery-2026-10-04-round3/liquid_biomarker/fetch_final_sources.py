from fetch_sources import BASE,fetch
import json,urllib.request,zipfile,io,hashlib,datetime,xml.etree.ElementTree as E
rs=[fetch('asano2019-supp.pdf','https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-019-09143-8/MediaObjects/41467_2019_9143_MOESM2_ESM.pdf',2*1024**2),fetch('GSE124158-meta.txt','https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE124158&targ=gsm&form=text&view=brief',2*1024**2),fetch('dr62012.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3342254/fullTextXML'),fetch('axists2023.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10628187/fullTextXML')]
# S2 XLS was not retained by the first extension whitelist. Retrieve same public archive once and retain that only.
url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7352477/supplementaryFiles';r={'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
 with urllib.request.urlopen(url,timeout=45) as resp:data=resp.read(2*1024**2+1)
 assert len(data)<=2*1024**2
 r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  inner=z.read('cancers-12-01372-s001.zip')
 with zipfile.ZipFile(io.BytesIO(inner)) as z:
  raw=z.read('Table S2.xls');(BASE/'heinhuis2020-Table S2.xls').write_bytes(raw);r.update(retained_bytes=len(raw),retained_sha256=hashlib.sha256(raw).hexdigest())
except Exception as e:r['error']=str(e)
rs.append(r);(BASE/'final-source-receipts.json').write_text(json.dumps(rs,indent=2),encoding='utf8');print(json.dumps(rs,indent=2))
from pypdf import PdfReader
f=BASE/'asano2019-supp.pdf'
if f.exists():
 text='\n'.join(p.extract_text() for p in PdfReader(f).pages);(BASE/'asano2019-supp.txt').write_text(text,encoding='utf8')
 print('ASANO identity lines',[s for s in text.splitlines() if 'chondro' in s.lower() or 'myxoid' in s.lower()])
for n in ['dr62012','axists2023']:
 f=BASE/(n+'.xml')
 if f.exists():
  root=E.parse(f).getroot();print(n)
  for s in root.findall('.//supplementary-material'):print('SUPP',E.tostring(s,encoding='unicode'))
