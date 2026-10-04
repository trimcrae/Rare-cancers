"""Freeze completion/provenance only after the final normal gate has finished."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
old=BASE.parent/'discovery-2026-10-03'
manifest=json.loads((old/'MANIFEST-CURRENT.json').read_text())
errors=[]
for name,r in manifest['files'].items():
    f=old/name
    if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=r['sha256']:
        errors.append(name)
assert not errors, errors
gate=json.loads((BASE/'final-normal-preflight-receipt.json').read_text())
assert gate['exit_code']==0
assert json.loads((BASE/'independent-exon-verification.json').read_text())['pass']
assert json.loads((BASE/'probe-specificity-results.json').read_text())['exact_spliced_target_match']
assert subprocess.run(['git','diff','--quiet'],cwd=ROOT).returncode==0
assert subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode==0
now=datetime.now(timezone.utc).isoformat()
completion={'completed_utc':now,
 'objective':'Determine evidence for TMEM266 transcript in published EMC tissue',
 'result':'Published FFPE TMEM266 RNA signal with official splice-junction probe match; supporting low downstream coverage in one EMC-derived culture',
 'not_demonstrated':['malignant-cell localization','full-length coding RNA','specific alternative isoform','membrane protein','dependency or therapeutic window'],
 'biological_counts':{'FFPE_export':12,'EWSR1_positive':8,'EWSR1_negative':4,'culture_biological_samples':1,'culture_technical_runs':2},
 'workers':{'emc_clinical':'completed; no processes','emc_genomics':'completed; no processes','emc_measurements':'completed; no processes'},
 'worker_status_evidence':'Final collaboration list and worker reports checked by lead',
 'owned_processes_running':False,'automation_created':False,
 'normal_preflight':gate,'scientific_checks':'Independent tissue arithmetic, exact probe/reference match, gene/exon sums and per-base replay; explicit FISH crosswalk replay',
 'old_discovery_manifest_preserved_files':len(manifest['files']),
 'preservation_errors':errors,'tracked_tree_modified':False,
 'base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'free_volume_bytes':shutil.disk_usage(ROOT).free,
 'storage_policy':'No new checkouts/runtimes/whole sequencing files; task output below2MB; root sole writer',
 'publication_or_outreach':False,'durable_handoff':'HANDOFF.txt','detailed_results':'RESULTS.txt'}
(BASE/'COMPLETION.json').write_text(json.dumps(completion,indent=2)+'\n')
files={}
for f in sorted(BASE.iterdir()):
    if f.is_file() and f.name!='MANIFEST.json':
        b=f.read_bytes()
        files[f.name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
(BASE/'MANIFEST.json').write_text(json.dumps({'created_utc':now,'files':files},indent=2)+'\n')
total=sum(f.stat().st_size for f in BASE.iterdir() if f.is_file())
assert total<2_000_000, total
print(json.dumps({'completed':True,'output_bytes':total,'manifest_files':len(files),
                  'preserved_old_files':len(manifest['files']),'normal_gate':gate['exit_code'],
                  'nothing_running':True}))
