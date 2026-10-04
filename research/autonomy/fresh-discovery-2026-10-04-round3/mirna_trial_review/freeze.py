import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
files=[]
for p in sorted(B.rglob('*')):
    if p.is_file() and p.name!='MANIFEST.json':
        raw=p.read_bytes()
        if p.suffix=='.json': json.loads(raw)
        files.append(dict(path=p.relative_to(B).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
assert sum(x['bytes'] for x in files)<2*1024**2
assert shutil.disk_usage(B).free>=10*1024**3
out=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),files=files)
p=B/'MANIFEST.json';p.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
for x in files:
    assert hashlib.sha256((B/x['path']).read_bytes()).hexdigest()==x['sha256']
print(json.dumps(dict(files=len(files),bytes_including_manifest=sum(p.stat().st_size for p in B.rglob('*') if p.is_file()),manifest_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),free_bytes=shutil.disk_usage(B).free)))
