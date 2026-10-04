"""Finalize the completed bounded lane; do not rerun after integration."""
import datetime, hashlib, json, pathlib, shutil, subprocess
D=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert shutil.disk_usage(D).free>=10*1024**3
review=json.loads((D/'independent-clinical-review.json').read_text())
for name,want in review['input_sha256'].items():
    assert sha(D/name)==want, (name,'reviewed artifact changed')
results=json.loads((D/'eligibility-results.json').read_text())
assert results['gate']['authenticated_EMC_cases']==0 and not results['gate']['numeric_EMC_pilot_run']
root=subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=D,text=True).strip()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=D,text=True).strip()
relative=D.relative_to(pathlib.Path(root)).as_posix()
status=subprocess.check_output(['git','status','--short','--',relative],cwd=root,text=True)
(D/'GIT-STATUS.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'worker_HEAD':head,'scoped_status':status,'commits_by_worker':[],'pushes_by_worker':[],
 'integration_status':'uncommitted worker lane; lead has not yet confirmed integration','git_mutations_by_this_lane':False},indent=2))
files=[{'path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(D.rglob('*')) if p.is_file() and p.name not in ['MANIFEST.json','FREEZE.json']]
assert sum(x['bytes'] for x in files)<16*1024**2
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'R6 clinical_identity','file_count':len(files),'total_bytes':sum(x['bytes'] for x in files),
 'exclusions':['MANIFEST.json','FREEZE.json'],'files':files}
(D/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_outputs_final':True,'no_owned_process_running':True,
 'owned_process_handles':[],'decision':'SHELVE standalone paper; no new demonstrated EMC finding; no exhaustive absence claim',
 'credible_distinct_next_analysis_with_actual_eligible_EMC_measurements':None,
 'independent_review_sha256':sha(D/'independent-clinical-review.json'),
 'reciprocal_regulatory_review_sha256':sha(D/'independent-regulatory-review.json'),
 'MANIFEST_sha256':sha(D/'MANIFEST.json'),'manifest_files':len(files),'manifest_payload_bytes':manifest['total_bytes'],
 'free_volume_bytes':shutil.disk_usage(D).free,'worker_HEAD':head,'committed':False,'pushed':False,
 'ownership':'Only this lane written; older packets and shared coordination unchanged. Lead owns integration.'}
(D/'FREEZE.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
print(json.dumps({'files_with_manifest_freeze':len(files)+2,'total_retained_bytes':sum(p.stat().st_size for p in D.rglob('*') if p.is_file()),
 'manifest_sha256':sha(D/'MANIFEST.json'),'freeze_sha256':sha(D/'FREEZE.json'),'free_volume_bytes':shutil.disk_usage(D).free,'worker_HEAD':head},indent=2))
