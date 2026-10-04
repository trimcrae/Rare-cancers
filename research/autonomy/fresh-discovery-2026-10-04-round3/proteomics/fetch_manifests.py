"""Bounded public metadata pagination and selected supplements; no protein-value query."""
from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures,zipfile,io,shutil
P=Path(__file__).resolve().parent
assert shutil.disk_usage('C:/').free>10*1024**3+20*1024**2
def getpage(page):
 u=f'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD054790/files?page={page}&pageSize=100'
 try:
  with urllib.request.urlopen(u,timeout=25) as r:b=r.read(200001)
  assert len(b)<=200000
  j=json.loads(b);assert isinstance(j,list)
  return {'url':u,'page':page,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'count':len(j),'rows':j}
 except Exception as e:return {'url':u,'page':page,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:pages=list(ex.map(getpage,range(2,17)))
for i in [0,1]:
 b=(P/f'panatlas-files-page{i}.json').read_bytes();j=json.loads(b)
 pages.append({'page':i,'local_source':f'panatlas-files-page{i}.json','sha256':hashlib.sha256(b).hexdigest(),'count':len(j),'rows':j})
pages.sort(key=lambda r:r['page'])
(P/'panatlas-files-all-pages.json').write_text(json.dumps(pages,indent=2),encoding='utf8')
rows=[r for p in pages for r in p.get('rows',[])]
nonraw=[r for r in rows if not r['fileName'].lower().endswith('.raw')]
(P/'panatlas-nonraw-files.json').write_text(json.dumps(nonraw,indent=2),encoding='utf8')
print('PanAtlas pages',[(p['page'],p.get('count'),p.get('error')) for p in pages])
print('Nonraw',[(r['fileName'],r['fileSizeBytes']) for r in nonraw])
u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12409279/supplementaryFiles'
rec={'url':u}
try:
 with urllib.request.urlopen(u,timeout=45) as r:b=r.read(14*1024**2+1)
 assert len(b)<=14*1024**2,'14MiB supplementary limit'
 rec.update(archive_bytes=len(b),archive_sha256=hashlib.sha256(b).hexdigest())
 with zipfile.ZipFile(io.BytesIO(b)) as z:
  rec['members']=z.namelist();retained=[]
  for n in z.namelist():
   if n.endswith('.docx') or any(x in n for x in ['figure_1_supp','figure_2_supp','figure_3_supp']):
    d=z.read(n);name=Path(n).name;(P/name).write_bytes(d)
    retained.append({'file':name,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()})
  rec['retained']=retained
 print('ProCan supplement retained',[(r['file'],r['bytes']) for r in retained])
except Exception as e:rec['error']=str(e);print('ProCan supplement',str(e))
(P/'procan-supplements-receipt.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
