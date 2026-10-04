from pathlib import Path
import urllib.request, hashlib, json, shutil, datetime, xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
URL='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7175964/fullTextXML'
free=shutil.disk_usage(D).free
assert free>10*1024**3+2*1024**2,free
p=D/'racanelli2020.xml'
if not p.exists():
 response=urllib.request.urlopen(URL,timeout=45)
 data=response.read(2*1024**2+1)
 r=type('Response',(),{'status_code':response.status,'content':data,'text':data.decode('utf8',errors='replace')})()
 receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':URL,'status':r.status_code,'bytes':len(r.content),'disk_free_before':free}
 if r.status_code==200 and len(r.content)<2*1024**2 and '<article' in r.text:
  p.write_bytes(r.content);receipt['sha256']=hashlib.sha256(r.content).hexdigest()
 (D/'racanelli-receipt.json').write_text(json.dumps(receipt,indent=2))
 if not p.exists(): raise SystemExit('Unavailable; stop source retrieval')
root=E.parse(p).getroot()
text=lambda x:' '.join(''.join(x.itertext()).split())
paras=[text(x) for x in root.findall('.//p') if any(q in text(x).lower() for q in ['nr4a3','extraskeletal','nfd','data availab','archer'])]
tables=[]
for t in root.findall('.//table-wrap'):
 rows=[[text(c) for c in row] for row in t.findall('.//tr')]
 emc=[row for row in rows if any(('NR4A3' in c or 'EMC'==c or 'Extraskeletal myxoid' in c) for c in row)]
 if emc: tables.append({'id':t.get('id'),'headers':rows[:2],'emc_rows':emc})
supp=[{'text':text(x),'links':[a.attrib for a in x.iter() if any('href' in k for k in a.attrib)]} for x in root.findall('.//supplementary-material')]
output={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'paragraphs':paras,'tables':tables,'supplements':supp}
(D/'racanelli-extraction.json').write_text(json.dumps(output,indent=2),encoding='utf8')
print(json.dumps(output,indent=2))

