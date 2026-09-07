"""Run bounded offline checks and seal the delivered reference pack (no commit)."""
import hashlib,json,os,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
BASE='8b3c210215c1433a637a6514537753112725896b'
def now(): return datetime.now(timezone.utc)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head==BASE,head
status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
assert all(line[3:].startswith('research/autonomy/trial-reference-repair-2026-09-05/') for line in status.splitlines()), status
checks=[]; log=[]; env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
if '--resume-after-approval' in sys.argv:
    checks=[json.loads(line) for line in (OUT/'checks.log').read_text(encoding='utf-8').splitlines() if line.startswith('{"script":')]
    assert len(checks)==3 and all(x['exit_code']==0 for x in checks), 'Completed checks not reusable'
for name,args in ([] if checks else [('freeze.py',[]),('verify_frame.py',['--check']),('build_reference.py',['--check'])]):
    cmd=[sys.executable,'-B','-X','utf8',str(OUT/name),*args]
    started=time.perf_counter(); r=subprocess.run(cmd,cwd=ROOT,env=env,text=True,encoding='utf-8',capture_output=True)
    elapsed=time.perf_counter()-started
    checks.append(dict(script=name,args=args,exit_code=r.returncode,seconds=round(elapsed,3)))
    log.append(json.dumps(checks[-1])+'\n'+r.stdout+'\n'+r.stderr)
    (OUT/'checks.log').write_text('\n'.join(log),encoding='utf-8')
    assert r.returncode==0,name
v=load(OUT/'validation.json')
seal_names=['round-contract.json','label-protocol.json','selection.json','freeze-receipt.json','reader-judgments.json','reference.json','review-packet.json','author_labels.py','build_reference.py']
sealed={n:sha(OUT/n) for n in seal_names}
if (OUT/'label-freeze.json').exists():
    assert load(OUT/'label-freeze.json')['sha256']==sealed, 'Previously frozen labels changed'
else:
    dump(OUT/'label-freeze.json',dict(frozen_at_utc=now().isoformat(),scope='Single-reader labels and source pack; independent scientific verification pending',rankings_run_before_freeze=False,sha256=sealed))
files={str(p.relative_to(OUT)).replace('\\','/'):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(OUT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['output-manifest.json','run-record.json']}
dump(OUT/'output-manifest.json',dict(schema='emc-output-manifest/1',excludes=['output-manifest.json (self)','run-record.json (contains manifest hash)','__pycache__ (generated interpreter cache, not a research output)'],files=files))
end=now(); start=datetime.fromisoformat('2026-09-05T17:39:18+00:00'); scientific_seconds=(end-start).total_seconds()
approval=load(OUT/'approval-wait.json') if (OUT/'approval-wait.json').exists() else None
blocked_proxy_seconds=(datetime.fromisoformat(approval['blocked_tool_interval_proxy_end_utc'].replace('Z','+00:00'))-datetime.fromisoformat(approval['blocked_tool_interval_proxy_start_utc'].replace('Z','+00:00'))).total_seconds() if approval else 0
scientific_estimate=scientific_seconds-blocked_proxy_seconds
record=dict(schema='emc-bounded-research-run/1',task_id='01a072a6-0a2e-78b3-83db-0e1f8404bc15',coordinator_task_id='01a071e4-d344-7053-b429-7bdfc963c8c2',resource='paper:PUB-CARE-DELIVERY',
    outcome='bounded_reference_pack_complete_pending_coordinator_scientific_verification',worktree=str(ROOT),base_revision=BASE,head_revision=head,commit_created=False,
    model='Exact model identifier not exposed to worker; coordinator execution metadata is authoritative',reasoning_effort_assigned='medium',reasoning_effort_independently_instrumented=False,
    timing=dict(initialization_goal_created_at_utc='2026-09-05T17:38:12Z',instructions_read_complete_observed_utc='2026-09-05T17:38:25Z',reservation_confirmation_observed_utc=start.isoformat(),scientific_start_utc=start.isoformat(),scientific_end_utc=end.isoformat(),elapsed_wall_seconds=round(scientific_seconds,3),scientific_seconds=None if approval else round(scientific_seconds,3),scientific_seconds_estimate_excluding_blocked_tool_proxy=round(scientific_estimate,3),blocked_tool_proxy_seconds=round(blocked_proxy_seconds,3),offline_checks_measured_seconds=round(sum(c['seconds'] for c in checks),3),reserved_scientific_seconds=1800,estimated_within_reservation=scientific_estimate<=1800,approval_wait_record='approval-wait.json' if approval else None,timing_uncertainty='Exact approval request/grant times and shell startup uninstrumented; blocked-tool proxy is an estimate. No precise actual scientific-time claim. Wall-time overrun was caused by pending execution approval; completed checks reused for bookkeeping repair.' if approval else None,initialization_and_wait_seconds_from_goal_creation=66,initialization_note='Instruction reading began before first clock observation; exact first read time unavailable. Goal createdAt anchors initialization. Scientific clock starts at first clock observation immediately after coordinator confirmation; message-arrival-to-clock latency not instrumented.'),
    outputs=dict(directory=str(OUT),required_outputs={n:sha(OUT/n) for n in ['label-protocol.json','selection.json','reference.json','repair.md']},output_manifest='output-manifest.json',output_manifest_sha256=sha(OUT/'output-manifest.json'),files_in_manifest=len(files),label_freeze='label-freeze.json'),
    results=dict(metadata_pairs=v['metadata_pairs'],challenge_pairs=v['challenge_pairs'],unique_pairs=v['unique_pairs'],unique_trials=v['unique_trials'],exact_excerpts=v['exact_excerpts_verified'],frame_records=6182,raw_registry_pages_verified=112,query_manifests_verified=24,all_selected_pairs_labeled=True,ranking_evaluation_performed=False,patient_eligibility_claimed=False,unjudged_as_negative=False),
    checks=checks,checks_log='checks.log',normal_preflight='Not run; coordinator owns normal preflight after integration',
    independence=dict(prior_evidence_json_read=False,prior_curate_py_read=False,prior_pilot_verdicts_read=False,known_anchors_disclosed=True,reader_count=1,independent_scientific_verification_performed=False),
    unresolved_issues=['Coordinator independent scientific verification remains required before reference-standard use.','NCT05135975 refers additional exclusions to an external protocol not reviewed in allowed saved-source scope; three labels remain provisional.','NCT05918640 DSRCT safety hold release unknown; retain conditional class compatibility and do not score as a permanent negative.','SS18 mutation/fusion semantics and other extra biomarker/cohort requirements unresolved; broad labels are conditional scope only.','No live site/cohort recruitment confirmation; one historical challenge is active-not-recruiting.','Four cases per stratum are insufficient for strong full-parent ranking/workload inference; next concrete repair is 149-pair ordinary/molecular enumeration, with 124 still unjudged, and prospectively frozen parent sampling if needed.'],
    next_action='Coordinator verifies the bounded labels, preserves unresolved gates, integrates with normal preflight, then sends frozen endpoint/labels to a fresh ranking or sampling-expansion worker.',
    usage=dict(task_tokens='unavailable',subscription_capacity='not queried',paid_api_used=False,gpu_used=False),nested_workers_or_runners=False,publication_or_outreach=False,processes_running=False)
dump(OUT/'run-record.json',record)
print(json.dumps(dict(outcome=record['outcome'],scientific_seconds=record['timing']['scientific_seconds'],checks=checks,unique_pairs=v['unique_pairs'],output_manifest_sha256=record['outputs']['output_manifest_sha256'],processes_running=False),indent=2))
