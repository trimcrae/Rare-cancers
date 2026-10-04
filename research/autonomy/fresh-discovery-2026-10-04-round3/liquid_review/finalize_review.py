from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
ROOT=Path(__file__).resolve().parent
WORKTREE=ROOT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
free=shutil.disk_usage(ROOT).free
assert free>=10*1024**3
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WORKTREE,text=True).strip()
receipt={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_head':head,
 'status':'Frozen source-bound independent review; scoped shelving recommendation; owner Asano/AxiSTS/TEP follow-up pending',
 'free_bytes':free,'commits_created':0,'pushed':False,'owned_running_processes':[],
 'actual_persisted_scripts_run':['review_primary.py','finalize_review.py'],
 'complete_source_image_sha256':{p.name:sha(p) for p in ROOT.glob('*-medium.png')},
 'reviewer_claim':'Original DR6 Figures3D/4 contain no EMC individual/serial identifiers; no pixel-derived measurements',
 'pending_owner_outputs':'Asano/AxiSTS/TEP source analysis and final Results/Coverage not certified by this checkpoint'}
(ROOT/'REVIEW-RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
files=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(ROOT.iterdir()) if p.is_file() and p.name!='MANIFEST.json']
size=sum(f['bytes'] for f in files)
assert size<1024**2
(ROOT/'MANIFEST.json').write_text(json.dumps({'files':files,'listed_bytes':size,'listed_count':len(files),'manifest_excludes_itself':True},indent=2),encoding='utf8')
print(json.dumps({'files':len(files)+1,'bytes':size+(ROOT/'MANIFEST.json').stat().st_size,'manifest_sha256':sha(ROOT/'MANIFEST.json'),'head':head,'free_bytes':free}))
