from pathlib import Path
import urllib.request,json,hashlib,datetime,concurrent.futures,shutil,xml.etree.ElementTree as ET,re
R=Path(__file__).resolve().parent
assert shutil.disk_usage(R).free>=10*1024**3
S=[('gu2022.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9206606/fullTextXML'),('zhang2022-preprint.pdf','https://assets-eu.researchsquare.com/files/rs-1463611/v1/d194a910-8cb1-46bf-b6e9-c92e306676a9.pdf?c=1651120385'),('rettig1988.pdf','https://pmc.ncbi.nlm.nih.gov/articles/PMC280153/pdf/pnas00261-0239.pdf')]
def f(z):
 n,u=z;r={'file':n,'url':u,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as q:b=q.read(4*1024**2+1);r.update(status=q.status,content_type=q.headers.get('Content-Type'))
  assert len(b)<=4*1024**2
  if n.endswith('.pdf'):assert b[:4]==b'%PDF','notPDF'
  (R/n).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:o=list(pool.map(f,S))
(R/'additional-source-receipts.json').write_text(json.dumps(o,indent=2));print(json.dumps(o,indent=2))
p=R/'gu2022.xml'
if p.exists():
 t=ET.parse(p).getroot()
 for x in t.iter('table-wrap'):
  cap=' '.join(x.find('caption').itertext()) if x.find('caption') is not None else ''
  print(x.attrib.get('id'),cap)
  if any(k in cap.lower() for k in ['patient','clinical','demographic']):print(' '.join(x.itertext())[:7000])
 print('supp',[(x.tag,x.attrib) for x in t.iter() if x.tag in ['supplementary-material','media']])
from pypdf import PdfReader
p=R/'zhang2022-preprint.pdf'
if p.exists():
 rd=PdfReader(p);extract=[]
 for i,pag in enumerate(rd.pages):
  txt=pag.extract_text()
  if 'Summary of Patient Characteristics' in txt or ('Histopathology' in txt and 'Solitary' in txt):extract.append({'page':i+1,'text':txt});print(i+1,txt[:5000])
 (R/'zhang-preprint-eligibility-pages.json').write_text(json.dumps(extract,indent=2))
