"""Create and verify a scoped source/evaluation manifest; no scientific claims generated."""
from pathlib import Path
import json, hashlib, datetime, shutil
B = Path(__file__).resolve().parent
paths = sorted(p for p in B.rglob('*') if p.is_file() and p.name != 'MANIFEST.json')
assert shutil.disk_usage(B).free >= 10 * 1024**3
rows = []
for p in paths:
    data = p.read_bytes()
    if p.suffix == '.json': json.loads(data)
    rows.append({'path':p.relative_to(B).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
manifest = {'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'decision':'Shelve standalone mature DLK1-DIO3 EMC paper; no demonstrated new biological finding',
            'retained_ceiling_bytes':10*1024**2, 'files':rows}
p = B/'MANIFEST.json'
p.write_text(json.dumps(manifest,indent=2),encoding='utf8')
total = sum(x['bytes'] for x in rows)+p.stat().st_size
assert total <= 10*1024**2
for x in rows:
    q=B/x['path']; assert q.stat().st_size==x['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256']
print(json.dumps({'files_including_manifest':len(rows)+1,'total_bytes':total,
                  'manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                  'free_bytes':shutil.disk_usage(B).free},indent=2))
