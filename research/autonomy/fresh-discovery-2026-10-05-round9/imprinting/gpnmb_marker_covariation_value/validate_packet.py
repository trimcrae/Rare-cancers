from pathlib import Path
from datetime import datetime
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
originals={
 'PLAN.json':'cc51b4ef79d49a01050e3bfa8c7c7add3611fa984799c6a1032b3034bc12f201',
 'PLAN-FREEZE.json':'442a52c1ebb01232fb07f2b7cee3a58e66bbfcd917c67d38a638fb5bf4ec5a03',
 'FINAL-DISPOSITION.json':'342360cdb290ff842858ab0cb905cda38227fbaac1876b5bb3ce6492ee453df2',
 'SOURCE-STAGE-CLOSED.json':'8f7f7d30b76b3f4262a443240f0eefbdd4f3148784bd28c82238649c2637c081'}
for name,expected in originals.items(): assert sha(ROOT/name)==expected,name
for row in json.loads((ROOT/'INPUT-BINDINGS.json').read_text())['bindings']:
 path=Path(row['reviewed_local_path'])
 assert sha(path)==row['sha256'],row['role']
 assert path.stat().st_size==row['bytes'],row['role']
timing=json.loads((ROOT/'TIMING-EXCEPTION.json').read_text())
assert timing['deadline_check']=='FAIL'
elapsed=(datetime.fromisoformat(timing['recorded_disposition_and_closure_utc'])-datetime.fromisoformat(timing['fixed_science_deadline_utc'])).total_seconds()
assert elapsed==timing['seconds_after_deadline']==24.200968
assert timing['last_individual_source_field_inspection_utc'] is None
for path in ROOT.glob('*.json'): json.loads(path.read_text())
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
for row in manifest['files']:
 path=ROOT/row['path']
 assert sha(path)==row['sha256'],row['path']
 assert path.stat().st_size==row['bytes'],row['path']
freeze=json.loads((ROOT/'SCIENCE-FREEZE.json').read_text())
assert sha(ROOT/'MANIFEST.json')==freeze['manifest_sha256']
assert freeze['timing_check']=='FAIL'
assert shutil.disk_usage(ROOT).free>=10*1024**3
print(json.dumps({'original_hashes':len(originals),'input_hashes':3,'export_hashes':len(manifest['files']),'json_and_hash_checks':'PASS','deadline_check':'FAIL; preserved 24.200968-second exception','new_network_raw_values_statistics':0}))
