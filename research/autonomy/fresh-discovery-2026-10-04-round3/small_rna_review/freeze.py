from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
p=Path(__file__).parent
files=[{'path':str(f.relative_to(p)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in sorted(p.rglob('*'))if f.is_file()and f.name!='MANIFEST.json']
assert sum(f['bytes']for f in files)<2*1024**2
(p/'MANIFEST.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'scope':'provisional source-review checkpoint; tracing pending','files':files,'bytes_excluding_manifest':sum(f['bytes']for f in files)},indent=2),encoding='utf8')
print(len(files)+1,sum(f.stat().st_size for f in p.rglob('*')if f.is_file()),hashlib.sha256((p/'MANIFEST.json').read_bytes()).hexdigest())
