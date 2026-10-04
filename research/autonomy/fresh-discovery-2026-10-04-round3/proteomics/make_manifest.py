"""Hash every retained packet file; the manifest itself is excluded to avoid a cycle."""
from pathlib import Path
import hashlib,json,datetime,shutil
P=Path(__file__).resolve().parent
items=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(P.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files_excluding_manifest':len(items),'bytes_excluding_manifest':sum(x['bytes'] for x in items),'files':items,'free_volume_bytes':shutil.disk_usage(P).free}
assert out['bytes_excluding_manifest']<30*2**20 and out['free_volume_bytes']>=10*2**30
m=P/'MANIFEST.json';m.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({'files_including_manifest':len(items)+1,'bytes_including_manifest':out['bytes_excluding_manifest']+m.stat().st_size,'manifest_sha256':hashlib.sha256(m.read_bytes()).hexdigest(),'free_volume_bytes':out['free_volume_bytes']}))
