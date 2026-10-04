"""Pin final worker packet without a recursive self-hash."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or p.name=='packet-manifest.json':continue
 raw=p.read_bytes();rows.append({'path':p.relative_to(D).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
out={'date':'2026-10-04','worker_head':'373a430957178c1ce76cab89b3ae21b337cb3fc0','scope':'genomics pilot and independent cross-campaign challenge','file_count_excluding_manifest':len(rows),'total_bytes_excluding_manifest':sum(r['bytes'] for r in rows),'self_exclusion':'packet-manifest.json is excluded from its own hash inventory','files':rows}
(D/'packet-manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'files_including_manifest':len(rows)+1,'bytes_including_manifest':sum(r['bytes'] for r in rows)+(D/'packet-manifest.json').stat().st_size}))
