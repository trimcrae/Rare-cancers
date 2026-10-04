from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
p=Path(__file__).parent
files=[{'path':str(f.relative_to(p)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(p.rglob('*')) if f.is_file() and f.name!='MANIFEST.json']
(p/'MANIFEST.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'files':files,'bytes_excluding_manifest':sum(f['bytes'] for f in files)},indent=2),encoding='utf8')
allfiles=[f for f in p.rglob('*') if f.is_file()]
print(len(allfiles),sum(f.stat().st_size for f in allfiles),hashlib.sha256((p/'MANIFEST.json').read_bytes()).hexdigest())
