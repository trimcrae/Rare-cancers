from fetch_sources import BASE,fetch
import json,urllib.request,zipfile,io,hashlib,datetime,xml.etree.ElementTree as E
rs=[fetch('axists2023-supp.pdf','https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41416-023-02416-6/MediaObjects/41416_2023_2416_MOESM1_ESM.pdf',2*1024**2),fetch('pastuszak2021.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8486571/fullTextXML',250000),fetch('anderson2025.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11658723/fullTextXML',200000)]
url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8486571/supplementaryFiles';r={'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
 with urllib.request.urlopen(url,timeout=30) as resp:data=resp.read(2*1024**2+1)
 assert len(data)<=2*1024**2
 r.update(archive_bytes=len(data),archive_sha256=hashlib.sha256(data).hexdigest(),members=[])
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  for name in z.namelist():
   if name.lower().endswith('.xlsx'):
    raw=z.read(name);(BASE/('pastuszak-'+name)).write_bytes(raw);r['members'].append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
except Exception as e:r.update(error_type=type(e).__name__,error=str(e))
rs.append(r);(BASE/'remaining-receipts.json').write_text(json.dumps(rs,indent=2),encoding='utf8');print(json.dumps(rs,indent=2))
from pypdf import PdfReader
if (BASE/'axists2023-supp.pdf').exists():
 text='\n'.join(p.extract_text() for p in PdfReader(BASE/'axists2023-supp.pdf').pages);(BASE/'axists2023-supp.txt').write_text(text,encoding='utf8')
 print('AXI',len(text),[s for s in text.splitlines() if any(q in s.lower() for q in ['myxoid','chondro','actg','biomarker','crp','patient'])][:40])
for name in ['pastuszak2021','anderson2025']:
 f=BASE/(name+'.xml')
 if f.exists():
  root=E.parse(f).getroot();print(name)
  for s in root.findall('.//p'):
   txt=' '.join(s.itertext())
   if any(q in txt.lower() for q in ['deposited','accession','histolog','myxoid','chondro']):print(txt[:1800])
import openpyxl
for f in BASE.glob('pastuszak-*.xlsx'):
 w=openpyxl.load_workbook(f,read_only=True,data_only=True);out={}
 for sh in w:
  vals=list(sh.values);out[sh.title]=vals
  print('SHEET',sh.title,len(vals),vals[:3]); print('HITS',[row for row in vals if any(q in str(row).lower() for q in ['extra','chondro','nr4a3'])][:12])
 (BASE/'pastuszak-tables.json').write_text(json.dumps(out,indent=2,default=str),encoding='utf8')
