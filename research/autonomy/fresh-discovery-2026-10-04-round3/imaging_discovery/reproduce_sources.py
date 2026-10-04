"""Verify pinned sources; optionally recover missing inputs without changing them."""
from pathlib import Path
import hashlib,json,shutil,sys,urllib.request
p=Path(__file__).resolve().parent
count=0
for r in json.loads((p/'receipts.json').read_text()):
    if not r.get('file') or not r.get('sha256'): continue
    f=p/r['file']
    if not f.exists():
        assert '--fetch-missing' in sys.argv,f'Missing source: {f.name}'
        assert shutil.disk_usage(p).free>10*2**30+r['bytes']
        b=urllib.request.urlopen(r['url'],timeout=45).read(r['bytes']+1)
        assert hashlib.sha256(b).hexdigest()==r['sha256'],f'Changed remote source: {r["url"]}'
        f.write_bytes(b)
    assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],f.name
    count+=1
print(f'Verified {count} pinned source files')
