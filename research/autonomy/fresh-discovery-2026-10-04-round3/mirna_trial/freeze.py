import pathlib,json,hashlib,datetime,shutil,subprocess
R=pathlib.Path(__file__).resolve().parent
other=pathlib.Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round3/mirna_trial_review')
binding={n:{'path':str(other/n),'sha256':hashlib.sha256((other/n).read_bytes()).hexdigest()} for n in ['MANIFEST.json','RESULTS.txt','HANDOFF.txt','source-crosscheck.json']}
assert binding['MANIFEST.json']['sha256']=='0f4c52fae76633305dc30d6fcc5ec6cdee264b783a888ece32918cf83f186c97'
(R/'independent-review-binding.json').write_text(json.dumps(binding,indent=2))
# Improve prose spacing without changing source files, identifiers or URLs.
replacements={'June2026':'June 2026','March2026':'March 2026','September28,2026':'September 28, 2026','September1':'September 1','October2025':'October 2025','October1,2025':'October 1, 2025','October14':'October 14','June3':'June 3','June18':'June 18','Phase1a':'Phase 1a','phase0':'phase 0','phase1a':'phase 1a','trialEMC':'trial EMC','prior2013/2014':'prior 2013/2014','all16':'all 16','all33pages':'all 33 pages','subject102-001':'subject 102-001','Subject101-001':'Subject 101-001','patient103-003':'patient 103-003','Figure4':'Figure 4','Figure3':'Figure 3','figure3':'figure 3','slide13':'slide 13','slide17':'slide 17','slide18':'slide 18','slide15':'slide 15','slide16':'slide 16','repeatedSD':'repeated SD','2 not-evaluable':'2 not-evaluable','source2013':'source 2013','624-model':'624-model','both accessible supplements':'both accessible supplements'}
for n in ['RESULTS.txt','COVERAGE.txt']:
 p=R/n;s=p.read_text(encoding='utf-8')
 for a,b in replacements.items():s=s.replace(a,b)
 p.write_text(s,encoding='utf-8')
head=subprocess.check_output(['git','-C','C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional','rev-parse','HEAD'],text=True).strip()
assert head=='373a430957178c1ce76cab89b3ae21b337cb3fc0'
files=[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(R.iterdir()) if p.is_file() and p.name!='MANIFEST.json']
assert sum(p['bytes'] for p in files)<10*1024*1024
free=shutil.disk_usage(R).free;assert free>=10*1024**3
m={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_head':head,'free_bytes_at_freeze':free,'files':files,'source_bytes_excluding_manifest':sum(p['bytes'] for p in files),'owned_processes_running':False,'committed':False,'pushed':False}
(R/'MANIFEST.json').write_text(json.dumps(m,indent=2))
print(json.dumps({'files':len(files)+1,'total_bytes':sum(p.stat().st_size for p in R.iterdir() if p.is_file()),'manifest_sha256':hashlib.sha256((R/'MANIFEST.json').read_bytes()).hexdigest(),'free_bytes':free,'head':head},indent=2))
