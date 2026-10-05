import pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parent
checks={}
for s in json.loads((P/'REUSED-SOURCE-HASHES.json').read_text())['sources']:
 checks['source_'+s['key']]=hashlib.sha256(pathlib.Path(s['path']).read_bytes()).hexdigest()==s['sha256']
a=json.loads((P/'ALL-CANONICAL-COMPOUND-NAMES.json').read_text())['data']
checks['complete285_names']=sum(map(len,a.values()))==285
checks['projected_field_mask']=all(set(r)<=({'source_model','source_figure','source_panel','panel_row','literal_figure_drug','source_CAS','chemical_identity_verified'} if k=='bangerter40' else {'source_row','sheet','drug','cas'}) for k,rr in a.items() for r in rr)
checks['zero_numeric_stage']=json.loads((P/'DECISION.json').read_text())['numerical_stage'] is False
rr=json.loads((P/'PRIOR-BROADER-IDENTITY-REUSE.json').read_text())
checks['all19_prior_donor_labels']=len(rr['all_donor_labels'])==19
checks['all29_prior_cultures']=sum(len(r['cultures']) for r in rr['all_donor_labels'])==29
checks['three_broad_pending']=sum('unresolved' in r['EMC_eligibility'] for r in rr['all_donor_labels'])==3
checks['prior_roster_hash']=hashlib.sha256(pathlib.Path(rr['source']).read_bytes()).hexdigest()==rr['source_sha256']
checks['method_only_passed']=json.loads((P/'VERIFICATION.json').read_text())['pass']
assert all(checks.values()),checks
print(json.dumps({'pass':True,'checks':len(checks),'raw_bytes':0,'outcome_fields':0,'checks_detail':checks}))
