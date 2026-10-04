import json,hashlib,datetime,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (ROOT/'FREEZE.json').exists(), 'Frozen packet must not be silently rewritten'
rows=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name not in ['MANIFEST.json','FREEZE.json']]
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All retained lane files excluding this manifest and FREEZE.json; original source bytes preserved.','files':rows,'files_count':len(rows),'bytes':sum(x['bytes'] for x in rows),'access_limitations':'CASSIS expanded roster unresolved; BO-112 010/011/012 histology unresolved; Luthria S1 and scTumor S1 returned HTML; BO-112 full XML HTTP500 and later PMC browser check; CellSARCTx403; unsuitable measurement not inferred from failed access.'}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_outputs_final':True,'no_owned_process_running':True,'owned_sessions':[{'id':50758,'status':'terminal','exit_code':0}],'other_commands':'All returned terminal; no background/UI/browser/render tasks launched.','decision':'Shelve standalone candidate at source/value gate. No new authenticated eligible EMC cell-resolved dataset or consequential feasible next comparison emerged from this lane.','biological_conclusion':None,'coverage_complete':False,'independent_review':'Lead will independently challenge statuses after this freeze; not yet complete.','manifest_sha256':sha(ROOT/'MANIFEST.json'),'manifest_files':len(rows),'manifest_payload_bytes':manifest['bytes'],'git_head':'373a430957178c1ce76cab89b3ae21b337cb3fc0','commit_made':False,'push_performed':False,'free_bytes':shutil.disk_usage(ROOT).free,'retained_cap_bytes':16*1024**2}
(ROOT/'FREEZE.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
for x in rows:
 p=ROOT/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
files=[p for p in ROOT.rglob('*') if p.is_file()]
print(json.dumps({'manifest_sha256':sha(ROOT/'MANIFEST.json'),'freeze_sha256':sha(ROOT/'FREEZE.json'),'file_count':len(files),'bytes':sum(p.stat().st_size for p in files),'free_bytes':shutil.disk_usage(ROOT).free},indent=2))
