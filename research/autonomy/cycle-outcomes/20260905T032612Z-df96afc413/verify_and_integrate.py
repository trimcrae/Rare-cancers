from pathlib import Path
import hashlib,json,subprocess,sys,time,shutil
from datetime import datetime,timezone

root=Path('C:/Projects/EMC-Research')
sys.path.insert(0,str(root/'.cache'))
sys.path.insert(0,str(root/'research/autonomy'))
from full_preflight_runtime import environment
from local_ownership import Coordinator
_,env=environment()
owner='01a06e21-2d00-7070-be0b-208dc2bb6ccd'
run=root/'.cache/research-runs/20260905T032612Z-df96afc413'
receipt=json.loads((run/'receipt.json').read_text())
assert receipt['status']=='completed',receipt['status']
worker=Path(receipt['worktree'])
plan=json.loads((root/'.cache/research-cycle/plan.json').read_text())
outputs=plan['contract']['outputs']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p:digest(worker/p) for p in outputs}
checks=[]
def check(label,command,cwd):
    log=root/f'.cache/research-cycle/{label}.log'
    result=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True)
    log.write_text(result.stdout+result.stderr,encoding='utf-8',newline='\n')
    checks.append({'command':command,'cwd':str(cwd),'exit_code':result.returncode,'log':str(log),'log_sha256':digest(log)})
    print(label,result.returncode,flush=True)
    if result.returncode:
        print(result.stdout+result.stderr)
        raise SystemExit(result.returncode)
check('coordinator-decimal-compare',[sys.executable,'-X','utf8',str(root/'.cache/research-cycle/compare_output.py'),str(worker)],root)
check('coordinator-behavior-tests',[sys.executable,'-X','utf8','-m','pytest','-q','research/modalities/tests/test_surface_address_sensitivity.py','--basetemp=.cache/coordinator-surface-tests-20260905','--tb=short','-p','no:cacheprovider'],worker)
for n in (1,2):
    check(f'coordinator-regeneration-{n}',[sys.executable,'-X','utf8','research/modalities/surface_address_sensitivity.py'],worker)
    assert before=={p:digest(worker/p) for p in outputs},'regeneration changed frozen output bytes'
changed=subprocess.check_output(['git','diff','--name-only',receipt['base_commit']],cwd=worker,text=True).splitlines()
changed+=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=worker,text=True).splitlines()
assert set(changed)==set(outputs),(changed,outputs)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=worker,text=True).strip()==receipt['base_commit']
verification={'run_id':receipt['run_id'],'verified_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'artifact_sha256':before,'time_to_verified_output_seconds':(datetime.now(timezone.utc)-datetime.fromisoformat('2026-09-05T03:25:08.907+00:00')).total_seconds(),'substantive_defects_found':0,'repair_induced_defects':0,'review_scope':'All 19 readable baselines, 195 eligible deletion rows, 3 unreadable combinations, source/missingness provenance, behavioral edge cases, exact allowed file set, and deterministic regeneration. Independent expectations computed before worker output. No raw-data or probe-choice validation.','source_access':'GEO accession identities corroborated by official NCBI search results. Direct live pages returned browser checks; no fresh raw data retrieved.','next_action':'Reuse this verified sensitivity analysis. FAP comparator dependence and unstable small-cohort directions warrant explicit interpretation in future surface-target work. No manuscript rewrite or publication authorized by this cycle.'}
with Coordinator(root) as ownership:
    ownership.require(owner)
    for p in outputs:
        dest=root/p
        assert not dest.exists(),'Refuse to overwrite existing coordinator output'
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(worker/p,dest)
    (root/'.cache/research-cycle/verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(verification,indent=2))
