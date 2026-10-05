from pathlib import Path
from decimal import Decimal
import json,hashlib
p=Path(__file__).resolve().parent
plan=json.loads((p/'PLAN-FROZEN.json').read_text())
for s in plan['inputs']:
 assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
iw=json.loads(Path(plan['inputs'][1]['path']).read_text())
bg=json.loads(Path(plan['inputs'][0]['path']).read_text())
by_cas={r['cas']:r for r in iw['tables'][0]['records']}
screen=[]
for s in plan['fixed_NCC_screen_conditions']:
 r=by_cas[s['cas']]; assert r['drug']==s['drug'] and r['source_row']==s['source_row']
 screen.append({k:r[k] for k in ['drug','cas','viability_percent','sd_percentage_points','sheet','source_row']})
reference=next(r for r in screen if r['cas']=='1197953-54-0')
for r in screen:
 r['descriptive_mean_minus_brigatinib_percentage_points']=str(Decimal(str(r['viability_percent']))-Decimal(str(reference['viability_percent'])))
by_ic50={r['cas']:r for r in iw['tables'][1]['records']}
ref=Decimal(str(by_ic50['1197953-54-0']['ic50_nM']))
ic50=[]
for cas in json.loads((p/'AMENDMENT-01-CAS-CROSSWALK.json').read_text())['fixed_IC50_CAS']:
 r=by_ic50[cas]
 d={k:r[k] for k in ['drug','cas','ic50_nM','sheet','source_row']}
 d['descriptive_reported_IC50_over_brigatinib']=str(Decimal(str(r['ic50_nM']))/ref)
 d['exact_screen_CAS_crosswalk']=next(s['drug'] for s in screen if s['cas']==cas)
 ic50.append(d)
ordinal=[]
for name in plan['fixed_USZ20_conditions']:
 r=next(x for x in bg['rows'] if x['literal_figure_drug']==name)
 ordinal.append({k:r[k] for k in ['source_model','source_figure','literal_figure_drug','source_CAS','ordinal_source_category','chemical_identity_verified']})
missing=[]
for name in plan['missing_fixed_family']:
 assert not any(name in r['drug'].lower() for r in iw['tables'][0]['records'])
 missing.append({'fixed_name':name,'status':'No named NCC221 source condition; not a measured nonresponse.'})
result={'plan_sha256':hashlib.sha256((p/'PLAN-FROZEN.json').read_bytes()).hexdigest(),'screen_denominator':221,'IC50_denominator':24,'USZ20_denominator':40,'NCC_screen_selected':screen,'NCC_IC50_selected':ic50,'USZ20_ordinal_separate':ordinal,'missing_fixed_names':missing,'unit_limits':'Reported source summaries only; shared exposure/control compatibility remains unverified. Ratios/differences are arithmetic descriptions, not potency ranking, inferential statistics or target/class evidence. Enantiomers/salts not collapsed.','new_network':0,'no_gene_values':True}
(p/'EMPIRICAL-RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
