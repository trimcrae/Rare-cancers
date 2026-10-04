"""Verify frozen lane integration and decisive scientific quantities, read-only."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,ast
P=Path(__file__).resolve().parent
checks=[]
def check(name,value):
    checks.append({'check':name,'pass':bool(value)})
    assert value,name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for receipt in sorted(P.glob('INTEGRATION-*.json')):
    j=json.loads(receipt.read_text())
    for lane,entry in j['lanes'].items():
        for rel,record in entry['file_hashes'].items():
            p=P/lane/rel;check('integrated hash '+lane+'/'+rel,p.is_file() and sha(p)==record['sha256'])
for p in sorted(P.rglob('*.py')):
    ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p));check('Python syntax '+p.relative_to(P).as_posix(),True)
g=json.loads((P/'genomics/final-scoped-analysis.json').read_text())
check('all75FoundationEMCprofiles',g['foundation_cases']==75)
check('all49Foundationsecondaryeventrows',g['secondary_event_count']==49)
check('all34event-bearingprofiles',g['secondary_event_cases']==34)
check('all6JapaneseEMCsmallvariantrows',len(g['japan_cas70214']['all_six_emc_small_variant_rows'])==6)
check('OrigiMed all2sourceEMClabels plus identityconflict retained',len(g['origimed']['source_cases'])==3 and g['origimed']['all_emc_labeled_ids']==['P-4093','P-5337'])
m=json.loads((P/'clinical/matrix-independent-challenge.json').read_text())
check('independentmatrix396comparisons',m['RNA_contrasts_checked']==396)
check('independentmatrix594checks',len(m['checks'])==594 and all(x['pass'] for x in m['checks']))
v=json.loads((P/'matrix/validation-results.json').read_text())
check('noallocatedmatrixgenevalidates',len(v['nominated_results'])==5 and not any(x['passes_allocation']for x in v['nominated_results'].values()))
for rel in ['matrix/tissue-results.json','matrix/validation-results.json','h1fx/expression-results.json']:
    j=json.loads((P/rel).read_text())
    for path,expected in j['input_hashes'].items():check('sourcehash '+rel+' '+Path(path).name,sha(Path(path))==expected)
h=json.loads((P/'h1fx/GSE6481-identity.json').read_text())
check('all105GSE6481records andzeroEMC',len(h['all105_samples'])==105 and h['EMC_explicit_matches']==[] and h['histology_counts']['Myxoid liposarcoma']==19)
hi=json.loads((P/'clinical/h1fx-independent-identity.json').read_text())
check('independentGSE6481eligibility',hi['eligible_EMC']==0)
hc=json.loads((P/'regulatory/h1fx-independent-challenge.json').read_text())
check('independentH1FXvaluesrawRNA',hc['raw_H1FX_RNA_value_check'].startswith('PASS'))
check('independentH1FXvaluesrawarray',hc['raw_H1FX_array_value_check'].startswith('PASS'))
for path,expected in m['reviewed_files'].items():check('matrixreviewbound '+Path(path).name,sha(Path(path))==expected)
c=json.loads((P/'regulatory/clinical-independent-challenge.json').read_text())
check('independentlateconditionalrisk',abs(c['independent_late_risk']-(1-(11/12)*(6/7)))<1e-10)
out={'utc':datetime.now(timezone.utc).isoformat(),'status':'PASS','checks':checks,'scope':'File integration/source binding, syntax, decisive counts and independent numerical-review receipts. Not new experiments, full publication validation, or complete public-evidence closure.'}
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'checks':len(checks),'scope':out['scope']}))
