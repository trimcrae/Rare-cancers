#!/usr/bin/env python3
"""Verify retained source binding and claim boundaries; zero network/response analysis."""
import json,hashlib,shutil
from pathlib import Path
B=Path(__file__).resolve().parent
checks=[]
def check(name,ok):
 checks.append({'name':name,'pass':bool(ok)})
 if not ok:raise AssertionError(name)
plan=json.loads((B/'PLAN-FROZEN.json').read_text())
check('prospective source-only scope', 'no new drug quantities' in plan['scope'])
check('three distinct native contexts retained',len(plan['models'])==3)
check('exposed prior data explicit','not blinded' in plan['prior_exposure'])
claims=json.loads((B/'PUBLISHED-QUALITATIVE-CLAIMS.json').read_text())
p=Path(claims['primary']['cache_path']);raw=p.read_bytes()
check('primary original sha',hashlib.sha256(raw).hexdigest()==claims['primary']['sha256'])
check('primary original bytes',len(raw)==claims['primary']['bytes'])
check('only selected discussion and caption',len(claims['selected'])==2)
a,z=[q['numeric_masked_source_text'] for q in claims['selected']]
check('adverse monotherapy author statement', 'not in the validation as monotherapy in both models' in a)
check('discussion exact veneto-doxo wording','As venetoclax and doxorubicin' in a)
check('caption exact veneto-carfilzomib wording','venetoclax plus [numeric masked]' in z and 'carfilzomib' in z)
check('caption second pair doxo-carfilzomib','doxorubicin plus [numeric masked]' in z)
check('mask protects numerical response token exposure','[numeric masked]' in a and '[numeric masked]' in z)
check('no new network',claims['new_network_calls']==0)
check('no new raw copies',claims['new_original_bytes']==0)
check('initial qualitative exposure documented',bool(claims['exposure_limit']))
for rec in json.loads((B/'PRIOR-EVALUATION-BINDINGS.json').read_text()):
 f=Path(rec['path']);r=f.read_bytes();check('prior sha '+f.name,hashlib.sha256(r).hexdigest()==rec['sha256']);check('prior bytes '+f.name,len(r)==rec['bytes'])
coverage=json.loads((B/'COVERAGE.json').read_text())
check('all three core models covered',len(coverage['core'])==3)
check('broader contexts retained',len(coverage['broader'])==5)
check('all core pending statuses explicit',all(q.get('pending') for q in coverage['core']))
check('absence from selected24 not inactivity','not inactivity' in coverage['core'][2]['negative'])
check('no new quantities in coverage',coverage['new_gene_or_drug_quantities']==0)
check('free storage >=10GiB',shutil.disk_usage('/workspace').free>=10737418240)
for name in ['MEASUREMENT-OWNER-BINDING.json']:
 f=B/name
 if f.exists():
  o=json.loads(f.read_text())
  for rec in o['artifacts']:
   q=Path(rec['path']);r=q.read_bytes();check('owner sha '+q.name,hashlib.sha256(r).hexdigest()==rec['sha256']);check('owner bytes '+q.name,len(r)==rec['bytes'])
decision=json.loads((B/'DECISION.json').read_text())
check('no quantitative stage justified',decision['decision'].startswith('NO-GO'))
check('zero drug quantities',decision['new_drug_response_quantities']==0)
check('zero new gene values',decision['new_gene_values']==0)
check('exact measured pairs resolved','carfilzomib+venetoclax and carfilzomib+doxorubicin' in decision['pair_resolution'])
check('no universal protein veto','Universal same-material protein prerequisite' in decision['not_a_reason'])
check('concrete prospective reopening',len(decision['reopening'])==3)
report={'status':'PASS','checks':checks,'number_checks':len(checks),'network_calls':0,'new_response_quantity_inspections':0,'image_inspections':0,'scope':'Source hashes, qualitative author claim/condition boundaries, retained prior evidence and resources only; no numerical drug-response validation.'}
(B/'VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','number_checks':len(checks),'network':0,'new_response_values':0}))
