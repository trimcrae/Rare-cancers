import json,hashlib,subprocess,datetime,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
checks=[]
for name in ['source-receipts.json','candidate-receipts.json','closure-receipts.json','geo-search-receipts.json']:
 for r in json.loads((ROOT/name).read_text(encoding='utf-8')):
  if 'sha256' in r:
   p=ROOT/r['file'];b=p.read_bytes()
   assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],p
   checks.append({'source_receipt':name,'file':r['file'],'hash_pass':True})
for r in json.loads((ROOT/'prior-evaluation-reuse.json').read_text(encoding='utf-8')):
 p=Path(r['path']);b=p.read_bytes()
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],p
 checks.append({'reused_file':r['path'],'hash_pass':True})
for p in ROOT.glob('*.json'):json.loads(p.read_text(encoding='utf-8'))
ids=json.loads((ROOT/'bo112-library-identities.json').read_text(encoding='utf-8'))
assert len(ids)==12 and len({x['gsm'] for x in ids})==12
m=json.loads((ROOT/'metadata-verification.json').read_text(encoding='utf-8'))
assert (m['bo112_donors'],m['bo112_donor_timepoint_combinations'])==(7,11)
assert m['new_eligible_emc_measurements_authenticated']==0 and not m['biological_pilot_performed']
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Offline source receipt hashes, prior-evaluation bindings, JSON syntax and library identity arithmetic; not biological validation or a complete public evidence audit.','checks':checks,'all_checks_pass':True,'source_hash_checks':len(checks),'bo112_libraries':12,'bo112_donors':7,'bo112_donor_timepoints':11,'free_bytes':shutil.disk_usage(ROOT).free,'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'commit_made':False,'push_performed':False}
(ROOT/'VALIDATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
