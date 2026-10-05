from pathlib import Path
from datetime import datetime
import json,hashlib,shutil
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'PLAN.json')=='d724ed89e7a6e5d1f13b3d5c94c87a8df9421b30add918f4030fe63a6b0d224b'
assert sha(P/'GPNMB-FOCUSED-PUBLICATION-VALUE-REASSESSMENT.json')=='7554b54eb522718281657c728490d415e2a712e315e3d00892379e8d8ddb5f4d'
stop=json.loads((P/'SCIENTIFIC-STOP.json').read_text())
a=datetime.fromisoformat(stop['scientific_stop_utc']);b=datetime.fromisoformat(stop['strict_deadline_utc'])
assert a<b and stop['deadline_check']=='PASS'
assert (b-a).total_seconds()==stop['seconds_before_deadline']==3.121585
bindings=json.loads((P/'INPUT-BINDINGS.json').read_text())['bindings']
for row in bindings:
 assert sha(Path(row['cache_or_worktree_local_path']))==row['sha256'],row['role']
for f in P.glob('*.json'):json.loads(f.read_text())
manifest=json.loads((P/'MANIFEST.json').read_text())
for row in manifest['files']:
 f=P/row['path'];assert sha(f)==row['sha256'];assert f.stat().st_size==row['bytes']
freeze=json.loads((P/'SCIENCE-FREEZE.json').read_text())
assert sha(P/'MANIFEST.json')==freeze['manifest_sha256']
assert sha(P/'FINAL-DISPOSITION.json')==freeze['final_disposition_sha256']
assert sum(row['bytes'] for row in manifest['files'])<=4*1024**2
assert shutil.disk_usage(P).free>=10*1024**3
print(json.dumps({'input_freeze_hashes':len(bindings),'export_hashes':len(manifest['files']),'json_hash_budget_and_strict_stop_checks':'PASS','new_network_originals_statistics':0,'scientific_stop':stop['scientific_stop_utc']}))
