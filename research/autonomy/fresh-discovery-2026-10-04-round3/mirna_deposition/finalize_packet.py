"""Verify retrieval bytes and freeze metadata-only evidence; no Git mutations."""
from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
D=Path(__file__).resolve().parent;W=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
verified=[]
for name in ['entrez-search-receipts.json','metadata-receipts.json','candidate-receipts.json','final-candidate-receipts.json','linked-project-receipts.json']:
    for r in json.loads((D/name).read_text()):
        if r.get('sha256'):
            p=D/r.get('file',f"entrez-search-{r.get('number',0):02d}.json")
            assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
            verified.append(p.name)
e=json.loads((D/'trace-evaluation.json').read_text());l=json.loads((D/'linked-project-evaluation.json').read_text())
assert not e['quantitative_miRNA_payloads_opened'] and e['MSTS16_authenticated_public_deposit']is None
assert [e['complete_candidate_identity'][a]['n']for a in ['E-MTAB-7265','GSE87054','SRP223204']]==[102,27,8]
assert l['PRJNA692081']['n']==23 and l['PRJEB110929']['organism_counts']=={'Potamogeton crispus':1,'Homo sapiens':9}
reuse=[Path('C:/Projects/EMC-Research/research/autonomy')/p for p in ['tmem266-prepublication-2026-10-03/SOURCE-GATES.txt','tmem266-tissue-2026-10-03/SOURCE-AUDIT.txt','tmem266-tissue-2026-10-03/PLAN.txt']]
M=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round3/small_rna')
reuse += [M/p for p in ['GSE69470-samples.txt','nci-cell-identities.json','metadata-evaluation.json']]
scope=str(D.relative_to(W)).replace('\\','/')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()
status=subprocess.check_output(['git','status','--porcelain=v1','--',scope],cwd=W,text=True)
free=shutil.disk_usage(D).free;assert free>=10*1024**3
(D/'freeze-status.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':head,'git_status_exact':status,'scope':scope,'commit_push_merge_PR_performed':False,'owned_running_processes':[],'free_bytes':free,'retrieval_payloads_hash_verified':len(verified),'reused_sources':{str(p):{'sha256':sha(p),'bytes':p.stat().st_size}for p in reuse},'decision':'No authenticated numerical target-cohort deposit; proposed empirical analysis shelved pending source; no biological negative or global exhaustion claim.'},indent=2)+'\n')
manifest=D/'file-manifest.json';assert not manifest.exists()
files=[{'path':str(p.relative_to(D)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(D.rglob('*'))if p.is_file()]
manifest.write_text(json.dumps({'date':'2026-10-04','files':files,'count_excluding_manifest':len(files),'bytes_excluding_manifest':sum(r['bytes']for r in files)},indent=2)+'\n')
total=sum(p.stat().st_size for p in D.rglob('*')if p.is_file());assert total<=5*1024**2
print(json.dumps({'files_including_manifest':len(files)+1,'bytes_including_manifest':total,'manifest_sha256':sha(manifest),'HEAD':head,'git_status':status,'free_bytes':free,'verified_source_payloads':len(verified),'owned_processes':[]}))
