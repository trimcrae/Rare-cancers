"""Hash the owned packet; does not commit, push, delete, or change shared state."""
from pathlib import Path
import json,hashlib,datetime,shutil,subprocess
B=Path(__file__).parent
rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file() and p.name!='MANIFEST.json':
  v=p.read_bytes();rows.append({'path':p.relative_to(B).as_posix(),'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()})
root=B.parents[3]
r={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_scope':str(B),'decision':'SHELVE standalone; no new EMC immune-state/outcome finding','head':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'commit_created':False,'pushed':False,'owned_processes_running':False,'retained_budget_bytes':60*1024**2,'free_C_bytes':shutil.disk_usage(B).free,'files':rows,'payload_bytes_excluding_manifest':sum(x['bytes'] for x in rows)}
p=B/'MANIFEST.json';p.write_text(json.dumps(r,indent=2),encoding='utf8')
print(json.dumps({'manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'total_bytes_including_manifest':r['payload_bytes_excluding_manifest']+p.stat().st_size,'files_including_manifest':len(rows)+1,'head':r['head'],'free_C_bytes':r['free_C_bytes']},indent=2))
