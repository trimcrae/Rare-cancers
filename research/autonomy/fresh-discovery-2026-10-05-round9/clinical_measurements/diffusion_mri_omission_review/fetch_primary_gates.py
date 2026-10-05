#!/usr/bin/env python3
"""New-source quiet retrieval/identity-schema gate, never show case ADC values."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json,hashlib,datetime,xml.etree.ElementTree as ET,re
b=Path(__file__).resolve().parent
ids=['PMC10231763','PMC10342739','PMC10797984','PMC5820899']
def one(k):
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/'+k+'/fullTextXML';r={'source':k,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':u,'scope':'Methods/diagnosis/schema only; no caseADC outcomes or images'}
 try:
  with urllib.request.urlopen(u,timeout=20) as z:d=z.read(3000000);r.update(status=z.status,bytes=len(d),sha256=hashlib.sha256(d).hexdigest())
  (b/'source-cache'/(k+'.xml')).write_bytes(d);root=ET.fromstring(d)
  r['title']=' '.join(root.find('.//article-title').itertext());r['doi']=[p.text for p in root.findall('.//article-id') if p.get('pub-id-type')=='doi']
  r['methods']=[]
  for sec in root.findall('.//body/sec'):
   title=sec.findtext('title') or ''
   if 'method' in title.lower() or sec.get('sec-type') in ['materials|methods','methods']:
    for p in sec.findall('.//p'):
     text=' '.join(p.itertext())
     if not re.search('hla|fap',text,re.I):r['methods'].append(text)
  r['table_schema']=[]
  for t in root.findall('.//table-wrap'):
   caption=' '.join(t.find('caption').itertext()) if t.find('caption') is not None else ''
   headers=[' '.join(e.itertext()) for e in t.findall('.//thead/tr')]
   diag=[]
   for tr in t.findall('.//tr'):
    vals=[' '.join(e.itertext()) for e in tr if e.tag in ['td','th']]
    if any(re.search('chondrosarcoma|extraskeletal|ESMC|myxoid|sarcoma',v,re.I) for v in vals):
     # Retain diagnosis strings only, not neighbouringcase ADC cells.
     diag.extend([v for v in vals if re.search('chondrosarcoma|extraskeletal|ESMC|myxoid|sarcoma',v,re.I) and not re.search('ADC|diffusion',v,re.I)])
   r['table_schema'].append({'id':t.get('id'),'caption':caption,'headers':headers,'diagnosis_cells_only':diag})
  body=' '.join(root.find('body').itertext())
  r['explicit_EMC_body_terms']=bool(re.search(r'extraskeletal\s+myxoid\s+chondrosarcoma|extra-skeletal\s+myxoid\s+chondrosarcoma',body,re.I))
  r['ADC_DWI_body_terms']=bool(re.search(r'\bADC\b|diffusion.weighted',body,re.I))
 except Exception as e:r['error']=repr(e)
 return r
with ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(one,ids))
(b/'source-cache/method-schema-full.json').write_text(json.dumps(rows,indent=2)+'\n')
compact=[{k:v for k,v in r.items() if k!='methods'} for r in rows]
(b/'NEW-PRIMARY-METHOD-SCHEMA.json').write_text(json.dumps(compact,indent=2)+'\n')
for r in rows:print(json.dumps({k:v for k,v in r.items() if k not in ['methods']},ensure_ascii=False))
