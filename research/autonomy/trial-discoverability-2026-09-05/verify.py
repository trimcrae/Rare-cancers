"""Verify real archived evidence and derived set arithmetic, not scientific eligibility."""
import ast, collections, datetime, json, pathlib, subprocess
import retrieve as r
checks=[]
q=r.load_queries();checks.append({'check':'all_registry_payload_original_hashes_and_unique_counts','result':'pass','queries':len(q),'pages':sum(len(m['pages']) for m,_ in q.values())})
for m,_ in q.values():
 assert m['complete'] and not m['pages'][-1]['next_page_token']
 for i,p in enumerate(m['pages']):
  if i:assert p['request_page_token']==m['pages'][i-1]['next_page_token']
  if p.get('stored_sha256'):assert r.sha((r.ROOT/p['file']).read_bytes())==p['stored_sha256']
checks.append({'check':'pagination_chain_exhaustion_and_compressed_storage_hashes','result':'pass'})
freeze=r.read(r.ROOT/'freeze-provenance.json')
for x in freeze['files']:assert r.sha((r.ROOT/x['file']).read_bytes())==x['sha256']
selection=r.read(r.ROOT/'selection.json');first=min(m['started_at_utc'] for m,_ in q.values());assert datetime.datetime.fromisoformat(selection['frozen_at_utc'].replace('Z','+00:00'))<datetime.datetime.fromisoformat(first)
assert all(m['selection_sha256']==r.sha((r.ROOT/'selection.json').read_bytes()) for m,_ in q.values())
checks.append({'check':'frozen_selection_precedes_registry_outcomes_and_amendments_unchanged','result':'pass','first_query':first})
union={n:s for _,ss in q.values() for n,s in ss.items()};parent=set(q['parent_sarcoma'][1])|set(q['parent_eligibility_sarcoma'][1]);c=r.read(r.ROOT/'corrected-comparison.json');sens=r.read(r.ROOT/'sensitivity-results.json')
assert len(union)==c['corpus_union_count'] and len(parent)==c['parent_union_count']
for d in selection['diagnoses']:
 k=d['id'];o=set(q[k+'_ordinary'][1])|set(q[k+'_eligibility_ordinary'][1]);strong=o|set(q[k+'_unquoted_ordinary'][1])|set(q[k+'_unquoted_eligibility'][1]);mol=set(q[k+'_molecular'][1])|set(q[k+'_eligibility_molecular'][1]);assert len(o)==c['comparisons'][k]['ordinary_union_count'];assert sorted(mol-strong)==sens['diagnoses'][k]['molecular_only_ids'];assert len(strong)==sens['diagnoses'][k]['ordinary_strong_count']
checks.append({'check':'ordinary_molecular_parent_set_arithmetic','result':'pass','corpus_unique':len(union),'parent_unique':len(parent)})
e=r.read(r.ROOT/'evidence.json');packet={x['nct_id']:x for x in r.read(r.ROOT/'review-packet.json')};cache={}
for row in e['records']:
 n=row['nct_id'];assert n in packet
 for p in row['source_pointers']:
  if p['file'] not in cache:cache[p['file']]=r.read(r.ROOT/p['file'])
  obj=cache[p['file']]
  for part in p['json_pointer'].strip('/').split('/'):obj=obj[int(part)] if isinstance(obj,list) else obj[part]
  assert obj==packet[n]['eligibility']
checks.append({'check':'all_provisional_record_pointers_resolve_to_unchanged_full_criteria','result':'pass','records':len(e['records'])})
# Evidence for decision-bearing examples: each must really be missed/recovered as stated.
assert 'NCT05918640' in sens['diagnoses']['EMC']['molecular_only_ids'] and 'NCT05918640' in parent
assert 'NCT05071209' in sens['diagnoses']['DSRCT']['molecular_only_ids'] and 'NCT05071209' in parent
assert union['NCT05071209']['protocolSection']['statusModule']['overallStatus']=='ACTIVE_NOT_RECRUITING'
assert 'NCT05135975' in sens['diagnoses']['DSRCT']['removed_by_unquoted_ids']
assert 'SS18' in packet['NCT05687136']['eligibility'] and 'principal investigator' in packet['NCT05687136']['eligibility']
assert 'FET-non ETS' in packet['NCT07092306']['eligibility'] and 'EWSR1-WT1' in packet['NCT07092306']['eligibility']
checks.append({'check':'decision_example_retrieval_membership_and_source_anchors','result':'pass'})
for p in r.ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
for p in r.ROOT.rglob('*.json'):json.loads(p.read_text(encoding='utf8'))
checks.append({'check':'all_round_python_syntax_and_json_parse','result':'pass'})
for entry in r.read(r.SOURCES/'literature/source-manifest.json'):
 if 'file' in entry:assert r.sha((r.ROOT/entry['file']).read_bytes())==entry['sha256']
checks.append({'check':'archived_literature_hashes','result':'pass','known_failure':'EMC fullTextXML404; primary abstract successfully archived'})
try:
 proc=subprocess.run(['bash','scripts/preflight.sh'],cwd=r.ROOT.parents[2],capture_output=True,text=True,timeout=120)
 (r.ROOT/'preflight.log').write_text(proc.stdout+'\n'+proc.stderr,encoding='utf8')
 preflight={'result':'pass' if proc.returncode==0 else 'fail','exit_code':proc.returncode,'log':'preflight.log'}
except (OSError,subprocess.TimeoutExpired) as exc:
 (r.ROOT/'preflight.log').write_text('Normal preflight could not run: '+repr(exc)+'\n',encoding='utf8')
 preflight={'result':'not_run','reason':repr(exc),'log':'preflight.log'}
r.save(r.ROOT/'validation.json',{'verified_at_utc':r.now(),'checks':checks,'normal_preflight':preflight,'scope':'Round data/provenance validation. No independent scientific review, full publication gate, patient eligibility validation, or clinical result claimed.'})
print(json.dumps({'checks':checks,'normal_preflight':preflight},indent=2))
