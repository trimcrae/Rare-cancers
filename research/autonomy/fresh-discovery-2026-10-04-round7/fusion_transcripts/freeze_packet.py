from pathlib import Path
import json,hashlib,datetime,shutil,subprocess
D=Path(__file__).resolve().parent
files=[]
for p in sorted(D.iterdir()):
 if p.is_file() and p.name not in ['MANIFEST.json','FREEZE.json']:
  b=p.read_bytes();files.append({'path':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest={'utc':now,'scope':str(D),'files':files,'manifested_bytes':sum(x['bytes'] for x in files),'excluded':['MANIFEST.json','FREEZE.json'],'source_access_limitations':['ACC three processed supplement requests returned ordinary browser challenges; not bypassed or evaluated.','ACC PRJNA608250 ENA metadata request returnedHTTP500.','Brenca underlying RNA alias/condition map and raw junction analysis remain pending.','No complete-public-evidence or biological-absence claim.']}
mp=D/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf8')
freeze={'utc':now,'all_outputs_final':True,'no_owned_process_running':True,'owned_process_status':'All invoked command cells returned terminal exit status; no retained session handles, background jobs or UI automation.','decision':'SHELVE scoped standalone contribution; no new finding or biological negative.','manifest_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'manifested_file_count':len(files),'manifested_bytes':manifest['manifested_bytes'],'disk_free_at_freeze':shutil.disk_usage(D).free,'git_head':'373a430957178c1ce76cab89b3ae21b337cb3fc0','git_commit_push':'No commit or push performed; outputs local/uncommitted pending lead integration.','payload_cap_bytes':8*1024**2}
assert freeze['disk_free_at_freeze']>=10*1024**3
fp=D/'FREEZE.json';fp.write_text(json.dumps(freeze,indent=2),encoding='utf8')
for row in files:
 p=D/row['path'];assert p.stat().st_size==row['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
print(json.dumps({'manifest_sha256':freeze['manifest_sha256'],'freeze_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'total_files':len(list(D.iterdir())),'total_bytes':sum(p.stat().st_size for p in D.iterdir() if p.is_file()),'disk_free':shutil.disk_usage(D).free,'all_outputs_final':True,'no_owned_process_running':True}))
