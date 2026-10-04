from pathlib import Path
import urllib.request,hashlib,zipfile,io,json,datetime,shutil
BASE=Path(__file__).parent
rows=[]
for pmc in ['PMC7993298','PMC7489365','PMC6990941']:
 url=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles'
 row={'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  assert shutil.disk_usage(BASE).free>10*1024**3
  with urllib.request.urlopen(url,timeout=35) as f:b=f.read(8*1024**2+1)
  assert len(b)<=8*1024**2,'Bounded archive exceeds 8 MiB'
  row.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  z=zipfile.ZipFile(io.BytesIO(b));row['members']=[]
  for n in z.namelist():
   if n.lower().endswith(('.xlsx','.pdf','.docx')):
    v=z.read(n);dest=BASE/(pmc+'-'+Path(n).name)
    assert sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())+len(v)<30*1024**2,'Worker total limit'
    dest.write_bytes(v);row['members'].append({'name':dest.name,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()})
 except Exception as e:row['error']=str(e)
 rows.append(row)
 print(pmc,row.get('bytes'),row.get('error'),row.get('members'))
(BASE/'trial-epmc-supp-receipt.json').write_text(json.dumps(rows,indent=2))
