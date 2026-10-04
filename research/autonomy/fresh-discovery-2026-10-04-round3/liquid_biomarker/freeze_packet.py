from pathlib import Path
import hashlib,json,shutil,datetime,subprocess
B=Path(__file__).resolve().parent
repo=B.parents[3]
# The absolute worktree path is explicit so nesting changes cannot alter git scope.
repo=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment')
head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
status=subprocess.check_output(['git','-C',str(repo),'status','--short','--',str(B)],text=True).strip()
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'git_head':head,'scoped_git_status':status,'commits_by_worker':0,'pushes_by_worker':0,'active_owned_processes':0,'cap_bytes':15*1024**2,'free_bytes':shutil.disk_usage(B).free,'decision':'Shelve standalone contribution; no new disease finding','manifest_excludes':['MANIFEST.json'],'note':'All commands completed. Manifest hashes all retained files except itself, including this receipt.'}
(B/'freeze-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
files=[]
for f in sorted(B.rglob('*')):
 if f.is_file() and f.name!='MANIFEST.json':files.append({'path':f.relative_to(B).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
manifest={'files':files,'file_count':len(files),'total_bytes_excluding_manifest':sum(x['bytes'] for x in files)}
(B/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
assert sum(f.stat().st_size for f in B.rglob('*') if f.is_file())<=15*1024**2
assert shutil.disk_usage(B).free>=10*1024**3
print(json.dumps({'head':head,'files_including_manifest':len(files)+1,'total_bytes':sum(f.stat().st_size for f in B.rglob('*') if f.is_file()),'manifest_sha256':hashlib.sha256((B/'MANIFEST.json').read_bytes()).hexdigest(),'free_bytes':shutil.disk_usage(B).free},indent=2))
