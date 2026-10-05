from pathlib import Path
import json,hashlib
from decimal import Decimal
p=Path(__file__).resolve().parent
plan=json.loads((p/'PLAN-FROZEN.json').read_text());a=json.loads((p/'AMENDMENT-01-CAS-CROSSWALK.json').read_text());r=json.loads((p/'EMPIRICAL-RESULTS.json').read_text())
checks=0
for s in plan['inputs']:
 assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256'];checks+=1
assert hashlib.sha256((p/'PLAN-FROZEN.json').read_bytes()).hexdigest()==a['original_plan_sha256']==r['plan_sha256'];checks+=1
x=json.loads(Path(plan['inputs'][1]['path']).read_text());y=json.loads(Path(plan['inputs'][0]['path']).read_text())
assert [len(t['records']) for t in x['tables']]==[221,24] and len(y['rows'])==40;checks+=1
for z in r['NCC_screen_selected']:
 src=next(q for q in x['tables'][0]['records'] if q['source_row']==z['source_row'])
 for k in ['drug','cas','viability_percent','sd_percentage_points','sheet','source_row']:assert z[k]==src[k];checks+=1
ref=next(z for z in r['NCC_screen_selected'] if z['cas']=='1197953-54-0')
for z in r['NCC_screen_selected']:
 assert Decimal(z['descriptive_mean_minus_brigatinib_percentage_points'])==Decimal(str(z['viability_percent']))-Decimal(str(ref['viability_percent']));checks+=1
ref50=next(z for z in r['NCC_IC50_selected'] if z['cas']=='1197953-54-0')
assert [z['cas'] for z in r['NCC_IC50_selected']]==a['fixed_IC50_CAS'];checks+=1
for z in r['NCC_IC50_selected']:
 src=next(q for q in x['tables'][1]['records'] if q['source_row']==z['source_row'])
 for k in ['drug','cas','ic50_nM','sheet','source_row']:assert z[k]==src[k];checks+=1
 assert Decimal(z['descriptive_reported_IC50_over_brigatinib'])==Decimal(str(z['ic50_nM']))/Decimal(str(ref50['ic50_nM']));checks+=1
 assert z['exact_screen_CAS_crosswalk']==next(q['drug'] for q in r['NCC_screen_selected'] if q['cas']==z['cas']);checks+=1
for z in r['USZ20_ordinal_separate']:
 src=next(q for q in y['rows'] if q['literal_figure_drug']==z['literal_figure_drug'])
 for k,v in z.items():assert v==src[k];checks+=1
for z in r['missing_fixed_names']:
 assert not any(z['fixed_name'] in q['drug'].lower() for q in x['tables'][0]['records']);checks+=1
assert next(z for z in r['NCC_screen_selected'] if z['cas']=='877399-52-5')['viability_percent']<0;checks+=1
print(json.dumps({'result':'PASS','checks':checks,'scope':'Exact frozen source hash, literal fields, units/crosswalk and fixed arithmetic; no new dataset, statistics or source requests.','independence':'Independent verification path over canonical source exports, not a new independent source or raw-workbook authentication.'}))
