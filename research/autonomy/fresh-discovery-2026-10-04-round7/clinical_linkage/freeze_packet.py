"""Validate independent binding and freeze this completed source-gate packet."""
import datetime, hashlib, json, pathlib, shutil, subprocess
D=pathlib.Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
review=D/'independent-review.json'
assert sha(review)=='e5462b29e003d032fd0695b3b3959f7d0c8a8dbdae25b1a94529af9cc24e30a7'
for path,want in json.loads(review.read_text())['sha256'].items():
    assert sha(pathlib.Path(path))==want, path
assert shutil.disk_usage(D).free>=10*1024**3
json.loads((D/'COVERAGE.json').read_text())
rows=[{'file':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(D.rglob('*')) if p.is_file() and p.name not in ('MANIFEST.json','FREEZE.json')]
assert sum(r['bytes'] for r in rows)<8*1024**2
utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
(D/'MANIFEST.json').write_text(json.dumps({'utc':utc,'excludes':['MANIFEST.json','FREEZE.json'],'files':rows},indent=2))
freeze={'utc':utc,'all_outputs_final':True,'no_owned_process_running':True,'persistent_process_handles':[],
        'process_note':'No background processes launched. All commands complete synchronously; receipt is final after this script exits.',
        'decision':'SHELVE standalone fusion-treatment comparison; no new disease finding; not global exhaustion',
        'manifest_sha256':sha(D/'MANIFEST.json'),'file_count_including_manifest_and_freeze':len(rows)+2,
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=D,text=True).strip(),
        'git_status':'Untracked owned lane; no worker commit or push; parent integrates separately',
        'free_bytes_before_freeze':shutil.disk_usage(D).free}
(D/'FREEZE.json').write_text(json.dumps(freeze,indent=2))
files=[p for p in D.rglob('*') if p.is_file()]
print(json.dumps({'files':len(files),'bytes':sum(p.stat().st_size for p in files),'manifest_sha256':sha(D/'MANIFEST.json'),'freeze_sha256':sha(D/'FREEZE.json'),'free_bytes_after':shutil.disk_usage(D).free},indent=2))
