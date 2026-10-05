import pathlib,json,hashlib,datetime,decimal,shutil
P=pathlib.Path(__file__).resolve().parent
plan=json.loads((P/'PLAN-FROZEN.json').read_text());r=json.loads((P/'RESULTS.json').read_text());D=decimal.Decimal
checks=[]
def check(name,ok):checks.append({'name':name,'pass':bool(ok)})
check('plan before quantities',datetime.datetime.fromisoformat(plan['frozen_at_utc'])<datetime.datetime.fromisoformat(r['measured_at_utc']))
check('quantity completion before deadline',datetime.datetime.fromisoformat(r['completed_utc'])<datetime.datetime.fromisoformat(plan['deadline_utc']))
check('exact prospective plan hash',hashlib.sha256((P/'PLAN-FROZEN.json').read_bytes()).hexdigest()==r['plan_sha256'])
check('no new requests',r['network_requests']==0)
for s in r['sources']:check('unchanged original '+pathlib.Path(s['path']).name,hashlib.sha256(pathlib.Path(s['path']).read_bytes()).hexdigest()==s['sha256'])
for s in json.loads((P/'SOURCE-AND-PRIOR-FREEZE-BINDINGS.json').read_text())['prior_sources_unchanged']:check('unchanged prior '+pathlib.Path(s['path']).parent.name,hashlib.sha256(pathlib.Path(s['path']).read_bytes()).hexdigest()==s['sha256'])
check('allthree culture identifiers',set(c['GSM'] for c in r['conditions'])=={'GSM2113301','GSM6883080','GSM9037837'})
check('four separate assay records',len(r['conditions'])==4)
a,b,u,t=r['conditions']
check('fixed estimated-count captures',a['identifier']==b['identifier']=='GPNMB' and a['source_row_number']==b['source_row_number']==7248 and a['source_column']==1 and b['source_column']==2)
check('no ARCHS4 normalization',a['normalized_quantity'] is None and b['normalized_quantity'] is None)
check('USZ22 fixed capture',u['identifier']=='GPNMB' and u['source_row_number']==9957 and u['source_column']==10)
check('complete denominator validity',u['full_reported_feature_rows']==54507 and u['invalid_or_negative_reported_counts']==0 and D(u['denominator_reported_count_sum'])>0)
check('conditional share arithmetic',D(u['per_million_reported_count_share'])==D(1000000)*D(u['reported_gene_count'])/D(u['denominator_reported_count_sum']))
check('same USZ22 source not replication',u['GSM']==b['GSM'] and 'not independent' in u['library_reuse'])
check('fixed four USZ23 identifiers',set(x['Name'] for x in t['features'])=={'NM_001005340.2','NM_002510.3','XM_005249578.3','XM_017011678.2'})
check('partial TPM arithmetic',D(t['partial_four_feature_TPM_subtotal'])==sum((D(x['reported_TPM']) for x in t['features']),D(0)))
check('partial count arithmetic',D(t['partial_four_feature_NumReads_subtotal'])==sum((D(x['reported_NumReads']) for x in t['features']),D(0)))
check('zero observations preserved',all(D(x['reported_TPM'])==0 and D(x['reported_NumReads'])==0 for x in t['features'] if x['Name'].startswith('XM_')))
check('not whole-gene capture',t['capture'].startswith('PARTIAL') and not t['normalized_across_contexts'])
d=json.loads((P/'DECISION.json').read_text());check('no standalone or publication claim',not d['standalone_finding'] and not d['publication_worthy'])
check('all pending native contexts retained',len(json.loads((P/'COVERAGE.json').read_text())['remaining'])==4)
check('free storage minimum',shutil.disk_usage(P).free>=10*1024**3)
check('compact cap',sum(f.stat().st_size for f in P.iterdir() if f.is_file())<4*1024**2)
out={'scope':'Offline hash/arithmetic/unit/coverage verification; no network, new source quantities or unrelated targets. Independent raw-feature replay is separate.','checks':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks),'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL'}
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['passed'],out['total'])
if out['status']!='PASS':raise SystemExit(1)
