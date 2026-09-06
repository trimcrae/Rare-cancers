import json,pathlib,subprocess,os,time
p=pathlib.Path('research/autonomy/ipd-published-baselines-2026-09-06'); src=pathlib.Path('C:/Users/mcrae/.codex/worktrees/ipd-bounds-20260906/EMC-Research/research/autonomy/ipd-bounds-development-2026-09-06/development-releases.json');(p/'development-releases.json').write_bytes(src.read_bytes()); cases=json.loads(src.read_text())['cases'];d=p/'development';d.mkdir(exist_ok=True);env=os.environ.copy();env['LANG']='English_United States.utf8';recs=[]
for c in cases:
 i=d/(c['case_id']+'-release.json');o=d/(c['case_id']+'-result.json');l=d/(c['case_id']+'.log');i.write_text(json.dumps(c['release'],indent=2)+'\n');cmd=['.cache/R-4.6.1/bin/Rscript.exe','--vanilla',str(p/'runner.R'),'.cache/R-library',str(i),str(o)];start=time.monotonic()
 try:
  z=subprocess.run(cmd,capture_output=True,timeout=45,env=env);l.write_bytes(z.stdout+z.stderr);r={'case_id':c['case_id'],'command':cmd,'exit_code':z.returncode,'elapsed_seconds':time.monotonic()-start}
 except subprocess.TimeoutExpired as e:
  l.write_bytes((e.stdout or b'')+(e.stderr or b''));r={'case_id':c['case_id'],'command':cmd,'status':'timeout','elapsed_seconds':time.monotonic()-start}
 recs.append(r); print(r['case_id'],r.get('exit_code',r.get('status')),flush=True)
(p/'development-runs.json').write_text(json.dumps(recs,indent=2)+'\n')
