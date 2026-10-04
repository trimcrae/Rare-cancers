"""Freeze this worker-owned packet; no Git writes or external mutations."""
from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
D=Path(__file__).resolve().parent
W=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics')
F=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04-round3/dlk1_review')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(D/'PLAN.json')=='3b517dba103da51bd022a19d628a62cef042a189219c317d2cee2f20ba6786d9'
r=json.loads((D/'retained-results.json').read_text());q=json.loads((D/'followup-results.json').read_text())
assert r['tissue']['primary']['median']==.18 and r['tissue']['primary']['n_ge10']==2
assert not r['tissue']['primary']['passes_operational_abundance_gate']
assert len(q['GSE4303']['all_eligible_emc_metadata'])==10
assert q['USZ23']['summed_TPM_of_mapped_rows']==0
inputs={**r['input_hashes'],**q['input_hashes']}
for p,h in inputs.items():assert sha(Path(p))==h,p
review={str(F/n):sha(F/n)for n in ['REVIEW.txt','numeric-crosscheck.json','followup-crosscheck.json','file-manifest.json']if(F/n).exists()}
assert str(F/'REVIEW.txt')in review
(D/'independent-review-receipt.json').write_text(json.dumps({'review_files':review,'review_decision':'SHELVE','scope':'Independent source-level numeric/probe/denominator checks and biological/prior-art challenge; complete original Salmon index reconciliation remains open.','owner_final_results':{n:sha(D/n)for n in ['retained-results.json','followup-results.json','RESULTS.txt','COVERAGE.txt','HANDOFF.txt']},'note':'Owner followup schema/wording was clarified after numerical review to say mapped rows only; all measured values unchanged.'},indent=2)+'\n')
scope=str(D.relative_to(W)).replace('\\','/')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()
status=subprocess.check_output(['git','status','--porcelain=v1','--',scope],cwd=W,text=True)
free=shutil.disk_usage(D).free;assert free>=10*1024**3
(D/'freeze-status.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worktree':str(W),'HEAD':head,'owned_scope':scope,'git_status_exact':status,'commit_performed':False,'push_performed':False,'PR_or_merge_performed':False,'free_bytes':free,'owned_background_processes':[],'source_input_hashes_verified':len(inputs),'plan_hash_unchanged':True,'decision':'SHELVE standalone DLK1 paper; no global campaign completion'},indent=2)+'\n')
manifest=D/'file-manifest.json';assert not manifest.exists(),'Packet already frozen'
files=[{'path':str(p.relative_to(D)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(D.rglob('*'))if p.is_file()]
manifest.write_text(json.dumps({'date':'2026-10-04','files':files,'file_count_excluding_manifest':len(files),'total_bytes_excluding_manifest':sum(x['bytes']for x in files)},indent=2)+'\n')
total=sum(p.stat().st_size for p in D.rglob('*')if p.is_file());assert total<=10*1024**2
print(json.dumps({'HEAD':head,'git_status':status,'files_including_manifest':len(files)+1,'total_bytes_including_manifest':total,'manifest_sha256':sha(manifest),'free_bytes':free,'owned_background_processes':[]}))
