import urllib.request, json, zipfile, io, hashlib,datetime,shutil
from pathlib import Path
B=Path(__file__).resolve().parent
url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7349923/supplementaryFiles'
limit=5*1024**2
assert shutil.disk_usage(B).free-limit>10*1024**3
r={'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'retained':[]}
try:
    with urllib.request.urlopen(url,timeout=45) as resp: data=resp.read(limit+1);r['status']=resp.status
    assert len(data)<=limit
    r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    def extract(payload,prefix):
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            for info in z.infolist():
                r.setdefault('members',[]).append({'name':prefix+info.filename,'bytes':info.file_size})
                if info.filename.lower().endswith('.zip'): extract(z.read(info),prefix+info.filename+'__')
                elif info.filename.lower().endswith(('.pdf','.docx','.xlsx','.txt','.csv')):
                    raw=z.read(info);name='supp-'+Path(info.filename).name
                    used=sum(p.stat().st_size for p in B.rglob('*') if p.is_file())
                    assert used+len(raw)<10*1024**2
                    (B/name).write_bytes(raw);r['retained'].append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    extract(data,'')
except Exception as e:r['error']=str(e)
(B/'supplement-recovery.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print(json.dumps(r,indent=2))
