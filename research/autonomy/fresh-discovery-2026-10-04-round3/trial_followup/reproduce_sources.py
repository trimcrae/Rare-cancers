"""Optional source reproduction from pinned receipts; the default only verifies.
Use --fetch-missing to recover missing sources, never overwrite a changed source.
A changed remote hash is reported as an error and is not accepted as the pinned input.
"""
from pathlib import Path
import hashlib, json, shutil, sys, urllib.request
p = Path(__file__).resolve().parent
for r in json.loads((p/'receipts.json').read_text(encoding='utf-8-sig')):
    f = p/r['file']
    if not f.exists():
        assert '--fetch-missing' in sys.argv, f'Missing source {f.name}'
        assert shutil.disk_usage(p).free >= 10*2**30 + r['bytes']
        b = urllib.request.urlopen(r['url'],timeout=45).read(r['bytes']+1)
        assert hashlib.sha256(b).hexdigest() == r['sha256'], f'Changed remote input: {r["url"]}'
        f.write_bytes(b)
    assert hashlib.sha256(f.read_bytes()).hexdigest() == r['sha256'], f.name
print('All pinned source hashes verified')
