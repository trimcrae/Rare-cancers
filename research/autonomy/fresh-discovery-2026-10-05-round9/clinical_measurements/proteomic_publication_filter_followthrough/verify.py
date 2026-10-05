import pathlib,json,hashlib,datetime,shutil
P=pathlib.Path(__file__).resolve().parent
checks=[]
def check(name,ok):
 checks.append({'name':name,'pass':bool(ok)})
plan=json.loads((P/'PLAN-FROZEN.json').read_text());stop=json.loads((P/'SOURCE-STOP.json').read_text())
check('scientific stop before deadline',datetime.datetime.fromisoformat(stop['scientific_close_utc'])<datetime.datetime.fromisoformat(stop['deadline_utc']))
check('durable stop before archival recorded',stop['durable_stop_marker_written_before_archive'])
raw=0
for i in range(1,4):
 a=json.loads((P/f'ACCESS-{i:02}.json').read_text());f=pathlib.Path(a['cache_path']);b=f.read_bytes();raw+=len(b)
 check(f'raw{i} exact hash',hashlib.sha256(b).hexdigest()==a['sha256'])
 check(f'raw{i} exact length and cap',len(b)==a['bytes'] and len(b)<=a['cap'])
 check(f'request{i} anonymous and no redirects',a['anonymous'] and not a['automatic_redirects'])
 check(f'request{i} complete before stop',datetime.datetime.fromisoformat(a['completed_utc'])<datetime.datetime.fromisoformat(stop['scientific_close_utc']))
 check(f'route{i} prospectively frozen',datetime.datetime.fromisoformat(json.loads((P/f'ROUTE-{i:02}-FROZEN.json').read_text())['frozen_at_utc'])<datetime.datetime.fromisoformat(a['utc']))
check('exactly three requests',stop['new_requests']==3 and len(list(P.glob('ACCESS-*.json')))==3)
check('raw cap',raw==82349 and raw<=plan['caps']['raw'])
check('free storage',shutil.disk_usage(P).free>=plan['caps']['free'])
for src in json.loads((P/'SOURCE-BINDINGS.json').read_text())['sources']:
 f=pathlib.Path(src['path']);check('unchanged '+src['role'],f.exists() and hashlib.sha256(f.read_bytes()).hexdigest()==src['sha256'])
# Reproduce only the already frozen publication-cell audit, with no other row fields.
audit=json.loads((P/'PUBLICATION-CELL-COVERAGE-AUDIT.json').read_text())
x=json.loads((P/'raw-cache/stage-03.source').read_text());idx=x['result_set']['datasets_title_list'].index('publications');rows=x['datasets'];cells=[r[idx] for r in rows if isinstance(r,list) and len(r)>idx]
match=sum('10.1002/prca.201900054' in str(c).lower() or '31419061' in str(c) for c in cells)
check('publication column schema',idx==audit['publication_column_index']==7)
check('all 100 publication cells audited',len(rows)==len(cells)==audit['returned_records']==audit['eligible_publication_cells']==100)
check('literal target match replay',match==audit['exact_target_citation_matches']==0)
check('projection scope preserved',json.loads((P/'ACTUAL-PUBLICATION-PROBE-PROJECTION.json').read_text())['matching_publication_records']==[])
check('no numerical authorization used',not json.loads((P/'DECISION.json').read_text())['numerical_authorization_used'])
check('derived cap',sum(f.stat().st_size for f in P.iterdir() if f.is_file())<=plan['caps']['derived'])
r={'scope':'Offline archival verification; no network or new scientific interpretation. Prior generic-search marker FAIL remains historical.','checks':checks,'passed':sum(c['pass'] for c in checks),'total':len(checks),'raw_bytes':raw,'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL'}
(P/'VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['passed'],r['total'])
if r['status']!='PASS': raise SystemExit(1)
