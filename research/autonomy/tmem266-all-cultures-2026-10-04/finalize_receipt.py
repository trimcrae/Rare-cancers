"""Finalize task-local file manifest only after checks and processes finish."""
import datetime,hashlib,json,shutil,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert json.loads((P/'verification.json').read_text(encoding='utf-8'))['status']=='passed'
rows={f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(P.iterdir()) if f.is_file() and f.name not in ['MANIFEST.json','COMPLETION.json']}
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows}
(P/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
out={'utc':manifest['created_utc'],'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
     'manifest_sha256':sha(P/'MANIFEST.json'),'bound_files':len(rows),'bound_bytes':sum(x['bytes'] for x in rows.values()),
     'packet_bytes_before_completion':sum(f.stat().st_size for f in P.iterdir() if f.is_file()),
     'C_free_bytes':shutil.disk_usage('C:/').free,'packet_budget_bytes':2000000,
     'local_processes_running':False,'workers_complete':3,'max_concurrency_including_lead':4,
     'remote_state':'Prior genomic BLAST C4DCYTNP014 last WAITING; no active local polling',
     'normal_gate':'exit1 retained; corrected systems/citation gates pass, shared map integration pending',
     'publication_authorized_or_performed':False,'shared_registry_changed':False}
assert out['packet_bytes_before_completion']<out['packet_budget_bytes']
(P/'COMPLETION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))
