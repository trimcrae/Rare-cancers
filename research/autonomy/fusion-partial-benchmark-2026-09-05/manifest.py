"""Finalize this bounded checkpoint's byte manifest; verify with --verify (read-only)."""
from pathlib import Path
import json,hashlib,datetime,argparse
root=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');a=ap.parse_args()
def files():
 return sorted(p for p in root.rglob('*') if p.is_file() and p.name!='output-manifest.json' and '__pycache__' not in p.parts and '.cache' not in p.parts)
def digest(p):
 b=p.read_bytes();return {'file':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
if a.verify:
 m=json.loads((root/'output-manifest.json').read_text());assert m['files']==[digest(p) for p in files()]
 print(json.dumps({'manifest':'passed','files':len(m['files']),'mode':'read-only'}))
else:
 m={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'algorithm':'sha256','scope':'Exact bytes of all retained output-directory files, including inputs; excludes manifest itself and caches. No external cache is modified or included.','files':[digest(p) for p in files()]}
 (root/'output-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps({'manifest_created':True,'files':len(m['files'])}))
