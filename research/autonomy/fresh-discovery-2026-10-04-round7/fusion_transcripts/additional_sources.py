from pathlib import Path
import urllib.request,urllib.parse,json,datetime,hashlib,shutil,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
sources={
'fusion-microarray2013.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3742753/fullTextXML',
'acc2020-ena-metadata.json':'https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA608250&result=read_run&fields=study_accession,sample_accession,experiment_accession,run_accession,sample_alias,library_name,library_layout,library_strategy,library_source,library_selection&format=json',
}
receipts=[]
for name,url in sources.items():
 free=shutil.disk_usage(D).free
 assert free>10*1024**3+3*1024**2
 p=D/name
 try:
  if not p.exists():
   r=urllib.request.urlopen(url,timeout=40);b=r.read(2*1024**2+1)
   assert len(b)<2*1024**2
   p.write_bytes(b)
  b=p.read_bytes();receipts.append({'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'free_before':free})
 except Exception as e: receipts.append({'name':name,'url':url,'error':str(e)})
(D/'bounded-source-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
p=D/'fusion-microarray2013.xml'
if p.exists():
 root=E.parse(p).getroot();text=lambda x:' '.join(''.join(x.itertext()).split())
 out={'paragraphs':[text(x) for x in root.findall('.//p') if any(t in text(x).lower() for t in ['extraskeletal','nr4a3','splice','emc'])], 'tables':[]}
 for t in root.findall('.//table-wrap'):
  rows=[[text(c) for c in r] for r in t.findall('.//tr')]
  selected=[r for r in rows if any(any(q in c.lower() for q in ['extraskeletal','nr4a3','emc']) for c in r)]
  if selected: out['tables'].append({'id':t.get('id'),'header':rows[:2],'eligible':selected})
 (D/'fusion-microarray-extraction.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
p=D/'acc2020-ena-metadata.json'
if p.exists():
 j=json.loads(p.read_text());print('ENA count',len(j));print(json.dumps(j[:4],indent=2));print('aliases',sorted(set(x['sample_alias'] for x in j)))
print('receipts',json.dumps(receipts))
