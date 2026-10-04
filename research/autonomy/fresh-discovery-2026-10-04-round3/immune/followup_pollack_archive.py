"""Lead-authorized completion of relevant Pollack supplement; keep no archive copy."""
from pathlib import Path
import urllib.request,hashlib,zipfile,io,json,datetime,shutil
B=Path(__file__).parent
u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7489365/supplementaryFiles'
r={'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'max_archive_bytes':40*1024**2,'retained_worker_cap_bytes':60*1024**2}
try:
 assert shutil.disk_usage(B).free>10*1024**3
 with urllib.request.urlopen(u,timeout=45) as f:b=f.read(r['max_archive_bytes']+1)
 assert len(b)<=r['max_archive_bytes'],'Archive exceeds bounded40MiB'
 r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 z=zipfile.ZipFile(io.BytesIO(b));r['members']=[{'name':i.filename,'bytes':i.file_size} for i in z.infolist()]
 r['retained']=[]
 for n in z.namelist():
  if 's002' in n and n.lower().endswith('.pdf'):
   v=z.read(n);p=B/('PMC7489365-'+Path(n).name)
   assert sum(x.stat().st_size for x in B.rglob('*') if x.is_file())+len(v)<60*1024**2
   p.write_bytes(v);r['retained'].append({'name':p.name,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()})
except Exception as e:r['error']=str(e)
(B/'pollack-archive-followup.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
