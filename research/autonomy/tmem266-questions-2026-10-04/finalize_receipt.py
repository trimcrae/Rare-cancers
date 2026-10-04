"""Freeze this local investigation checkpoint; no repository/public mutation."""
import datetime,hashlib,json,shutil,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
verification=json.loads((BASE/'verification.json').read_text())
assert verification['status']=='passed'
assert json.loads((BASE/'normal-preflight-receipt.json').read_text())['exit_code']==1
out={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
     'scope':'Completed bounded remaining-question investigation and revised local draft; not submission readiness',
     'lead':'01a10371-956e-7f20-abe2-712c15d8cd9c',
     'workers':{'emc_clinical':'complete; read-only','emc_genomics':'complete; read-only','emc_measurements':'complete; read-only'},
     'max_concurrent_agents_including_lead':4,
     'local_processes_running':[],
     'remote_jobs_unresolved':[{'service':'NCBI BLAST','RID':'C4DCYTNP014','last_status':'WAITING','last_checked_utc_approx':'2026-10-04T11:48:00Z','local_polling':False}],
     'normal_preflight':'exit1; existing three shared-registry classifications in earlier packet',
     'scientific_and_preservation_checks':'passed within recorded scope',
     'earlier_manifest_entries_preserved':sum(r['verified_files'] for r in verification['earlier_packets_unchanged'].values()),
     'draft_sha256':sha(BASE/'DRAFT.md'),'supplement_sha256':sha(BASE/'SUPPLEMENT.md'),
     'retained_budget_bytes':2000000,'destination_free_bytes':shutil.disk_usage(ROOT).free,
     'prohibited_actions_performed':[],'published':False,'committed':False,
     'remaining_questions':['Patient-tissue cell localization','Full-length transcript identity','Protein and function','Diagnostic increment','Genome-wide probe specificity'],
     'handoff':'HANDOFF.txt'}
(BASE/'COMPLETION.json').write_text(json.dumps(out,indent=2)+'\n')
files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(BASE.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
manifest={'utc':out['completed_utc'],'scope':out['scope'],'files':files}
(BASE/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
total=sum(p.stat().st_size for p in BASE.iterdir() if p.is_file())
assert total<out['retained_budget_bytes']
for n,r in files.items():assert sha(BASE/n)==r['sha256']
print(json.dumps({'files_bound':len(files),'total_packet_bytes':total,'free_bytes':out['destination_free_bytes'],'manifest_sha256':sha(BASE/'MANIFEST.json'),'local_processes_running':[],'unresolved_remote_RID':'C4DCYTNP014'},indent=2))
