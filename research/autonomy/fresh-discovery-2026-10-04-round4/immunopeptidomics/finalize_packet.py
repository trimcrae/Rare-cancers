import datetime,hashlib,json,pathlib,shutil,subprocess
D=pathlib.Path(__file__).resolve().parent
W=D.parents[3]
def git(*args):return subprocess.check_output(['git','-C',str(W),*args],text=True).strip()
audit={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worktree':str(W),'git_head':git('rev-parse','HEAD'),'git_branch':git('branch','--show-current'),'git_status':git('status','--short','--untracked-files=normal'),'worker_commits':0,'worker_pushes':0,'owned_running_processes':[],'disk_free_bytes':shutil.disk_usage(D).free,'retained_cap_bytes':10*1024**2,'floor_free_bytes':10*1024**3,'scope':'Only this immunopeptidomics directory is new owned output; older packet files immutable.'}
assert audit['disk_free_bytes']>=audit['floor_free_bytes']
(D/'FINAL-AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
files=[{'path':str(p.relative_to(D)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(D.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
manifest={'utc':audit['utc'],'files':files,'files_excluding_manifest':len(files),'bytes_excluding_manifest':sum(x['bytes'] for x in files)}
(D/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
total=sum(p.stat().st_size for p in D.rglob('*') if p.is_file());assert total<=audit['retained_cap_bytes']
print(json.dumps({'files_including_manifest':len(files)+1,'total_bytes':total,'manifest_sha256':hashlib.sha256((D/'MANIFEST.json').read_bytes()).hexdigest(),'git_head':audit['git_head'],'free_bytes':audit['disk_free_bytes'],'owned_running_processes':[]},indent=2))
