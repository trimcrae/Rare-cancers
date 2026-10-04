"""Freeze owned R7 lane; metadata/hash operation only after scientific review."""
from pathlib import Path
import json,hashlib,datetime,shutil
R=Path(__file__).resolve().parent
assert (R/'independent-review-binding.json').is_file()
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[{'path':str(p.relative_to(R)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sh(p)} for p in sorted(R.rglob('*')) if p.is_file() and p.name not in ['MANIFEST.json','FREEZE.json']]
assert sum(x['bytes'] for x in files)<8*1024**2
assert shutil.disk_usage(R).free>=10*1024**3
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'R7 functional_models only','excluded':['MANIFEST.json','FREEZE.json'],'files':files,'file_count':len(files),'bytes':sum(x['bytes'] for x in files)}
(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
for f in files:assert sh(R/f['path'])==f['sha256']
freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_outputs_final':True,'no_owned_process_running':True,'owned_processes':[],'reconciliation':'All owned command sessions returned terminal exit codes; no background jobs, browser or tool/session handles. This final synchronous freeze call terminates on return. No other agent process inspected/stopped.','scientific_decision':'SHELVE; no new EMC biological finding and no global exhaustion claim','review_binding':'independent-review-binding.json','manifest_sha256':sh(R/'MANIFEST.json'),'total_files':len(files)+2,'retained_bytes':0,'free_bytes':shutil.disk_usage(R).free,'worker_commit':None,'worker_push':False}
for _ in range(6):
 b=(json.dumps(freeze,indent=2)+'\n').encode('utf-8');total=sum(p.stat().st_size for p in R.rglob('*') if p.is_file() and p.name!='FREEZE.json')+len(b)
 if freeze['retained_bytes']==total:break
 freeze['retained_bytes']=total
(R/'FREEZE.json').write_bytes((json.dumps(freeze,indent=2)+'\n').encode('utf-8'))
assert freeze['retained_bytes']==sum(p.stat().st_size for p in R.rglob('*') if p.is_file())
print(json.dumps({'files':freeze['total_files'],'bytes':freeze['retained_bytes'],'manifest_sha256':sh(R/'MANIFEST.json'),'freeze_sha256':sh(R/'FREEZE.json'),'free_bytes':freeze['free_bytes']},indent=2))