"""Freeze the owned lane only after source/value review is final; no scientific rerun."""
from pathlib import Path
import json,hashlib,datetime,shutil
R=Path(__file__).resolve().parent
assert (R/'independent-review-binding.json').is_file()
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[{'path':str(p.relative_to(R)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sh(p)} for p in sorted(R.rglob('*')) if p.is_file() and p.name not in {'MANIFEST.json','FREEZE.json'}]
assert sum(x['bytes'] for x in files)<16*1024**2
assert shutil.disk_usage(R).free>=10*1024**3
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'R6 nr4a3_regulatory only; prior packets unchanged','excludes':['MANIFEST.json','FREEZE.json'],'files':files,'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files)}
(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
for f in files:assert sh(R/f['path'])==f['sha256']
freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_outputs_final':True,'no_owned_process_running':True,'process_reconciliation':'All owned exec_command invocations returned terminal exit codes; no background jobs or retained tool handles. This final synchronous freeze invocation terminates on return. No other worker process inspected or stopped.','decision':'SHELVE standalone; no new EMC biological finding; no global exhaustion','independent_review':'independent-review-binding.json','manifest_sha256':sh(R/'MANIFEST.json'),'manifested_file_count':len(files),'retained_total_bytes_including_manifest_and_freeze':0,'free_bytes_before_freeze':shutil.disk_usage(R).free,'committed_by_worker':False,'pushed_by_worker':False}
# Compute stable exact retained-byte total including this final receipt.
for _ in range(5):
 b=(json.dumps(freeze,indent=2)+'\n').encode('utf-8')
 n=sum(p.stat().st_size for p in R.rglob('*') if p.is_file() and p.name!='FREEZE.json')+len(b)
 if n==freeze['retained_total_bytes_including_manifest_and_freeze']:break
 freeze['retained_total_bytes_including_manifest_and_freeze']=n
(R/'FREEZE.json').write_bytes((json.dumps(freeze,indent=2)+'\n').encode('utf-8'))
assert freeze['retained_total_bytes_including_manifest_and_freeze']==sum(p.stat().st_size for p in R.rglob('*') if p.is_file())
print(json.dumps({'files':len(files)+2,'bytes':freeze['retained_total_bytes_including_manifest_and_freeze'],'manifest_sha256':sh(R/'MANIFEST.json'),'freeze_sha256':sh(R/'FREEZE.json')},indent=2))