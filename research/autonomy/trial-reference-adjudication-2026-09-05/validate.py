"""Read-only reproducibility and source-integrity validator. Run Python -B from repository root."""
import json,gzip,hashlib,collections,sys
from pathlib import Path
from independent_judgments import OUT,ROOT,REPAIR,load,sha,resolve,J
from adjudicate import build

def validate():
 checks=[];cache={};pointer_count=0;excerpt_count=0
 def check(ok,name):
  if not ok:raise AssertionError(name)
  checks.append(name)
 def source(e):
  nonlocal pointer_count
  p=e['source'];b=(ROOT/p).read_bytes();assert sha(b)==e['source_sha256'],p
  if p not in cache:cache[p]=json.loads(gzip.decompress(b))
  pointer_count+=1;return resolve(cache[p],e['pointer'])
 receipt=load(OUT/'independent-freeze-receipt.json')
 for n,h in receipt['sha256'].items():check(sha((OUT/n).read_bytes())==h,'immutable independent freeze: '+n)
 for n,h in receipt['input_sha256'].items():check(sha((REPAIR/n).read_bytes())==h,'frozen allowed input: '+n)
 prior=load(REPAIR/'reference.json');ind=load(OUT/'independent-labels.json');final=load(OUT/'adjudicated-reference.json');dis=load(OUT/'discrepancy/adjudication.json');ev=load(OUT/'source-evidence.json')['evidence'];selection=load(REPAIR/'selection.json');pkt=load(REPAIR/'review-packet.json')
 check(prior['selection_sha256']==sha((REPAIR/'selection.json').read_bytes()),'same selection as first reader')
 expected={};metadata_n=0
 for s in selection['strata']:
  order=sorted(s['frame_ids'],key=lambda n:sha((selection['seed']+'|'+s['diagnosis']+'|'+s['stratum']+'|'+n).encode()))
  check(order[:min(4,len(order))]==s['selected_ids'],'offline deterministic selection: '+s['diagnosis']+'/'+s['stratum'])
  check(len(set(s['frame_ids']))==s['frame_n'],'unique frozen stratum frame: '+s['diagnosis']+'/'+s['stratum'])
  for n in s['selected_ids']:
   metadata_n+=1;expected.setdefault(s['diagnosis']+':'+n,[]).append({'set':'metadata_sample','stratum':s['stratum'],'frame_n':s['frame_n'],'sample_n':len(s['selected_ids']),'inclusion_fraction':str(len(s['selected_ids']))+'/'+str(s['frame_n'])})
 for a in selection['challenge_anchors']:
  for d in a['diagnoses']:expected.setdefault(d+':'+a['nct_id'],[]).append({'set':'challenge_anchor','stratum':'purposive'})
 check(len(expected)==49 and metadata_n==33,'49 unique selected pairs and 33 metadata memberships')
 check(sum(len(v)==2 for v in expected.values())==2 and sum(any(x['set']=='challenge_anchor' for x in v) for v in expected.values())==18,'18 challenge memberships, two overlaps')
 check(sum(s['frame_n'] for s in selection['strata'] if s['stratum'] in ['ordinary','molecular_only'])==149,'149 ordinary/molecular frame pairs are separate expansion target')
 check(len(final['pairs'])==49 and {p['pair_id'] for p in final['pairs']}==set(expected),'every adjudicated pair appears exactly once')
 check(len({p['nct_id'] for p in final['pairs']})==37,'37 distinct trials')
 check(len(ind['pairs'])==49 and len({p['pair_id'] for p in ind['pairs']})==49,'49 unique independent judgments')
 check(len(ev)==len({e['evidence_id'] for e in ev}),'unique evidence identifiers')
 eidx={e['evidence_id']:e for e in ev}
 for e in ev:
  value=source(e)
  if 'excerpt' in e:
   check(value[e['start_codepoint']:e['end_codepoint']]==e['excerpt'],'exact independent excerpt '+e['evidence_id']);check(sha(e['excerpt'].encode())==e['excerpt_utf8_sha256'],'excerpt hash '+e['evidence_id']);excerpt_count+=1
  else:
   check(value==e['value'],'raw pointer value '+e['evidence_id']);check(sha(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==e['value_canonical_sha256'],'raw value canonical hash '+e['evidence_id'])
 def walk_prior(x):
  nonlocal excerpt_count
  if isinstance(x,dict):
   if all(k in x for k in ['source','pointer','source_sha256']):
    value=source(x)
    if 'excerpt' in x:assert value[x['char_start']:x['char_end']]==x['excerpt'];excerpt_count+=1
   for v in x.values():walk_prior(v)
  elif isinstance(x,list):
   for v in x:walk_prior(v)
 walk_prior(prior);check(True,'all first-reader source pointers, byte hashes and excerpt offsets resolve')
 for p in prior['pairs']:
  for e in p['reviewed_modules']:
   check(source(e)==pkt[p['nct_id']]['record']['protocolSection'][e['pointer'].split('/')[-1]],'first and independent readers judged same module version: '+p['pair_id']+'/'+e['pointer'].split('/')[-1])
  for c in p.get('cohorts',[]):
   if 'evidence_pointer' in c:
    matches=[e for e in p['reviewed_modules'] if c['evidence_pointer'].startswith(e['pointer'])]
    check(bool(matches),'first-reader cohort pointer source identifiable: '+p['pair_id'])
    q=dict(matches[0]);q['pointer']=c['evidence_pointer'];source(q)
 fidx={p['pair_id']:p for p in final['pairs']}
 for p in final['pairs']:
  a=p['adjudicated'];n=p['nct_id'];d=p['diagnosis'];first=p['first_reader'];independent=p['independent_reader']
  check(p['sets']==expected[p['pair_id']]==first['sets']==a['sets'],'original exact memberships and fractions: '+p['pair_id'])
  check(independent['label']==J[n]['labels'][d],'reproduce authored independent label: '+p['pair_id'])
  check(first['overall_status']==a['current_availability']['overall_status_snapshot'] and first['snapshot_current']==independent['current_availability']['current_as_defined_in_frozen_sample']==a['current_availability']['snapshot_current'],'snapshot status preserved: '+p['pair_id'])
  check(not a['clinical_eligibility_established'] and not a['external_protocol_reviewed'],'no invented patient/protocol determination: '+p['pair_id'])
  check(a['protocol_uncertainty'] and a['recruitment_uncertainty'] and a['benchmark_disposition'],'explicit uncertainty fields: '+p['pair_id'])
  check(all(e in eidx for e in a['evidence_ids']),'pair evidence IDs resolve: '+p['pair_id'])
  check(a['clinical_trial_purpose']['registry_primary_purpose']==first['registry_primary_purpose'] and a['clinical_trial_purpose']['phases']==first['phase'],'purpose and phase retained: '+p['pair_id'])
  check(p['adjudication']['adjudicated_label']==a['label'],'decision label agrees with reference: '+p['pair_id'])
  if a['label']=='insufficient_evidence':check('do_not' in a['benchmark_disposition'],'unknown not negative: '+p['pair_id'])
  if a['extra_biomarker_requirement']['state']=='required_unestablished':check(a['molecular_compatibility']['status']=='unestablished' and 'uncomplicated' in a['benchmark_disposition'],'unestablished marker never unconditional positive: '+p['pair_id'])
 for d in ['EMC','DSRCT','SS']:
  a=fidx[d+':NCT05135975']['adjudicated'];check(a['known_missing_additional_exclusions'] and 'missing_protocol' in a['benchmark_disposition'],'missing CaboMain protocol held unresolved: '+d)
 hold=fidx['DSRCT:NCT05918640']['adjudicated']['current_availability']['conditional_safety_hold'];check(hold['state']=='release_unknown' and hold['known_current_hold_in_effect'] is None,'DSRCT safety hold remains conditional')
 check(fidx['SS:NCT05687136']['adjudicated']['molecular_compatibility']['status']=='unestablished','SS18 mutation/fusion unresolved')
 check(fidx['EMC:NCT07202884']['adjudicated']['clinical_trial_purpose']['task_domain']=='nononcology','nononcology false hit kept separate')
 _,_,rebuilt,decisions=build();check(rebuilt==final['pairs'] and decisions==dis['decisions'],'deterministic adjudicated content reproduces exactly')
 check(sum(x['label_discrepancy'] for x in decisions)==2 and len(decisions)==49,'all 49 comparisons; two label differences resolved')
 check(receipt['frozen_utc']<final['created_utc'],'independent freeze precedes adjudicated reference')
 readlog=load(OUT/'reading-log.json');check(len(readlog['trials'])==37 and not readlog['unreviewed_ids'],'37 complete saved-record readings recorded')
 return {'status':'passed','checks_count':len(checks),'checks':checks,'source_pointer_resolutions':pointer_count,'exact_excerpt_checks':excerpt_count,'distinct_raw_files_verified':len(cache),'independent_evidence_objects':len(ev),'counts':final['counts'],'label_counts_unique_pairs':dict(collections.Counter(p['adjudicated']['label'] for p in final['pairs'])),'unreviewed_pairs':[],'unresolved_source_questions_preserved':True,'preflight_run':False,'scope':'Offline data/source/selection/provenance validation; no clinical validation, performance benchmarking or integration preflight.'}
if __name__=='__main__':
 result=validate();print(json.dumps(result,ensure_ascii=False,indent=2))
