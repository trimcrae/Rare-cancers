from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,xml.etree.ElementTree as E,shutil
P=Path(__file__).resolve().parent
assert shutil.disk_usage(P).free>=10*2**30
sources={'ucla2024':'PMC12318355','dst2019':'PMC6462037','JCI72124':'PMC4348951','tumoroid2025':'PMC12370961','biobank2025':'PMC12371069'}
def get(item):
 name,pmc=item;url=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML'
 try:
  with urllib.request.urlopen(url,timeout=30) as r:b=r.read(1_500_001)
  assert len(b)<=1_500_000
  (P/(name+'.xml')).write_bytes(b)
  root=E.fromstring(b);rows=[];links=[]
  for el in root.iter():
   if el.tag in ['p','tr','table-wrap','supplementary-material']:
    t=' '.join(el.itertext())
    if any(x in t.lower() for x in ['chondrosarcoma','nr4a3','nr4a2','emc','sarcoma','data availab']):rows.append({'tag':el.tag,'text':t})
   if el.tag in ['supplementary-material','media','ext-link'] and el.attrib:links.append({'tag':el.tag,'attributes':el.attrib,'text':' '.join(el.itertext())[:300]})
  (P/(name+'-eligibility-excerpts.json')).write_text(json.dumps(rows,indent=2),encoding='utf8')
  (P/(name+'-source-links.json')).write_text(json.dumps(links,indent=2),encoding='utf8')
  return {'url':url,'file':name+'.xml','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 except Exception as e:return {'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:out=list(e.map(get,sources.items()))
(P/'primary-retrievals.json').write_text(json.dumps(out,indent=2))
for x in out: print(x)
