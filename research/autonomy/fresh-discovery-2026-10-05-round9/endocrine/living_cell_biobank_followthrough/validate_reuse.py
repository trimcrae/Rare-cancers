#!/usr/bin/env python3
"""Exact primary/citation and complete donor-unit reconciliation; no endpoint analysis."""
from pathlib import Path
import json,hashlib,datetime,shutil
from lxml import etree
P=Path(__file__).resolve().parent
checks=[]
def check(k,v):checks.append({'check':k,'pass':bool(v)})
def bound(a):
 f=Path(a['path']);b=f.read_bytes();return len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256']
for f in P.glob('*.json'):json.loads(f.read_text())
r=json.loads((P/'EXACT-SOURCE-RECONCILIATION.json').read_text())
check('all_exact_reused_input_bindings',all(bound(a) for a in r['verified_reuse_bindings']))
check('same_known_PMID_DOI',r['previous_retained_EPMC']['id']=='42333717' and r['previous_retained_EPMC']['doi']=='10.1002/ctm2.70722')
check('same_Crossref_DOI',r['previous_retained_Crossref']['DOI']=='10.1002/ctm2.70722')
root=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new')
x=etree.parse(str(root/'raw-cache/integration2026.xml'))
check('GenPharm_is_distinct_actual_source',x.xpath('//article-meta/article-id[@pub-id-type="doi"]/text()')==['10.1038/s41698-026-01555-2'] and x.xpath('//article-meta/article-id[@pub-id-type="pmid"]/text()')==['42310153'])
old=json.loads((root/'LIVING-ROSTER.json').read_text());new=json.loads((P/'ALL-DONOR-CONDITION-REUSE.json').read_text())
base=[{k:v for k,v in a.items() if k!='conditions'} for a in new['donors']]
check('all19_donor_roster_fields_unchanged',base==old['donor_rows'] and len(base)==19)
check('all29_source_modelconditions',sum(len(x['cultures']) for x in base)==29 and sum(len(x['conditions']) for x in new['donors'])==29)
check('unique29_culture_labels',len({a for d in base for a in d['cultures']})==29)
check('exactaccountability',new['accountability']==old['accountability'])
check('commercial_control_not_newpatient',new['commercial_control']==old['commercial_control'])
check('threebroad_source_donors_pending',[(x['donor'],x['cultures']) for x in base if x['diagnosis_literal']=='Undifferentiated sarcoma, pleomorphic']==[('TBB-S-045',['SAR030']),('TBB-S-087',['SAR109']),('TBB-S-099',['SAR121'])])
check('samepatient_region_stage_counts_preserved',[(d['donor'],len(d['cultures'])) for d in base if len(d['cultures'])>1]==[('TBB-S-044',8),('TBB-S-155',2),('TBB-S-052',3)])
check('percondition_source_stage_therapy_labels_present',all(set(a)=={'model','source_stage','source_prior_treatment_literal'} for d in new['donors'] for a in d['conditions']))
check('source_stage_categories_only',{a['source_stage'] for d in new['donors'] for a in d['conditions']}=={'Primary tumour','Metastasis','Local recurrence'})
check('no_new_requests_or_copies',r['new_source_requests']==0 and r['new_original_or_derivative_copies']==0)
check('no_gene_response_stage',json.loads((P/'COVERAGE-AND-DECISION.json').read_text())['response_gene_value_stage'] is False)
check('free_floor',shutil.disk_usage(P).free>=10737418240)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Exact old publication and full previously verified donor/model unit accounting; no new original-body review, phenotype or response validation.','checks':checks,'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','errors':[x['check'] for x in checks if not x['pass']]}
(P/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'errors':result['errors']}));raise SystemExit(bool(result['errors']))
