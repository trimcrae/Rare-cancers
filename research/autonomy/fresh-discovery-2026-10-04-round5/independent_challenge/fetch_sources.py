from pathlib import Path
import urllib.request,json,hashlib,datetime,concurrent.futures,shutil,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent
assert shutil.disk_usage(R).free>=10*1024**3
sources=[('fap2009.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2784039/fullTextXML'),('rettig1988.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC280153/fullTextXML'),('yang2022-pubmed.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:35025783&resultType=core&format=json'),('rettig1988.html','https://pmc.ncbi.nlm.nih.gov/articles/PMC280153/')]
def run(z):
 n,u=z;r={'file':n,'url':u,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as f:b=f.read(2*1024**2+1);r.update(status=f.status,content_type=f.headers.get('Content-Type'))
  assert len(b)<=2*1024**2
  if b'Checking your browser' in b:raise ValueError('challenge HTML not source')
  (R/n).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:o=list(pool.map(run,sources))
(R/'source-receipts.json').write_text(json.dumps(o,indent=2));print(json.dumps(o,indent=2))
for n in ['fap2009.xml','rettig1988.xml']:
 p=R/n
 if p.exists():
  t=ET.fromstring(p.read_bytes()); print(n,' '.join(t.find('.//article-title').itertext()));print('tables',[(x.attrib.get('id'),' '.join(x.itertext())[:4500]) for x in t.iter('table-wrap')]);print('links',[(x.tag,x.attrib) for x in t.iter() if x.tag in ['supplementary-material','media','self-uri']])
