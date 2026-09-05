"""Freeze deliverable inventory and actual elapsed time; no repository mutation outside round."""
import datetime, subprocess
import retrieve as r
end=datetime.datetime.now(datetime.timezone.utc);start=datetime.datetime.fromisoformat(r.read(r.ROOT/'selection.json')['scientific_start_utc'].replace('Z','+00:00'))
assert (end-start).total_seconds()<1800,'Round deadline exceeded'
repo=r.ROOT.parents[2]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
assert head=='13059f5cee4ceb032455d5877d6245006614be75'
assert not subprocess.check_output(['git','diff','--name-only'],cwd=repo,text=True).strip(),'Tracked changes unexpectedly present'
files=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=repo,text=True).splitlines()
assert all(x.startswith('research/autonomy/trial-discoverability-2026-09-05/') for x in files)
r.save(r.ROOT/'run-record.json',{
 'worktree':str(repo),'base_head':head,'coordinator_task':'01a071e4-d344-7053-b429-7bdfc963c8c2','worker_task':'01a07264-029e-71d3-be08-c044d1d1f03b',
 'bounded_objective':'Determine whether fusion-defined sarcoma trial discoverability warrants a distinct paper','decision':'no-go for paper development now; explicit scientific reopening conditions in pilot.md',
 'scientific_start_utc':start.isoformat(),'output_frozen_utc':end.isoformat(),'scientific_elapsed_seconds':round((end-start).total_seconds(),3),'maximum_seconds':1800,
 'reasoning_effort':'medium requested in dispatch; actual runtime effort metadata not independently exposed to this worker','model':'GPT-6 system identity; exact model execution metadata retained by coordinator dispatch, not re-inferred here','token_usage':'Unavailable in worker run instrumentation; no total usage pacing imposed',
 'resource':'paper:PUB-CARE-DELIVERY; reservation confirmed by coordinator before writes','paid_api_or_gpu_used':False,'nested_agents_tasks_or_runners':False,
 'processes_running':False,'process_status_basis':'All retrieval, archive, analysis, compression and validation command sessions returned exit0; preflight process could not launch because bash unavailable. No persistent service or scheduler created.',
 'validation':'24 complete queries,112 pages; raw/storage hashes,pagination,unique counts,set arithmetic,74 source pointers,Python syntax/JSON parse passed. Required memo frontmatter parsed. Normal preflight not run: missing bash.',
 'unresolved':['Single-worker provisional labels require coordinator independent verification','Reference corpus is query-bounded; no independent global eligibility denominator','Public cohort-stage availability and SS18 mutation-versus-fusion interpretation unresolved','No molecular-versus-solid-tumor hierarchy ranking/effort benchmark','EMC primary fullTextXML unavailable404; primary abstract archived instead'],
 'scope_check':'No tracked changes; all untracked outputs confined to authorized round directory; contract preserved','commit_or_publication':False,
 'next_action':'Coordinator independently check decision-bearing sources and disposition; integrate evidence if appropriate; do not develop a paper from omission counts alone.'})
inventory=[]
for p in sorted(r.ROOT.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name=='artifact-manifest.json':continue
 b=p.read_bytes();inventory.append({'file':p.relative_to(r.ROOT).as_posix(),'sha256':r.sha(b),'bytes':len(b)})
r.save(r.ROOT/'artifact-manifest.json',{'created_at_utc':r.now(),'files':inventory,'total_bytes':sum(x['bytes'] for x in inventory),'note':'Hashes are stored-file hashes; registry query manifests also retain original uncompressed response hashes. Inventory excludes itself and transient Python bytecode.'})
print('elapsed_seconds',round((end-start).total_seconds(),3))
for name in ['pilot.md','selection.json','evidence.json','artifact-manifest.json','run-record.json','validation.json']:
 print(name,r.sha((r.ROOT/name).read_bytes()))
print('files',len(inventory),'bytes',sum(x['bytes'] for x in inventory))
