"""Source/index verification only: no abstract, phosphosite or kinase values parsed."""
from pathlib import Path
import json,hashlib,datetime,shutil
HERE=Path(__file__).resolve().parent
RET=Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions')
OWNER=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/phosphoproteomic_manifest_gate')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok,detail=None):
 checks.append({'check':name,'pass':bool(ok),'detail':detail})
 if not ok:raise AssertionError(name)
check('owner prospective plan exact',sha(OWNER/'PLAN.json')=='8e2a40a9baf22655a56113ea6d0c646377db6758473db2796552bf5327a1f755')
check('original RET plan exact',sha(RET/'RET-PLAN-FROZEN.json')=='a38aeadacce369d6258c77425f72c02cea39f2cc35b600155d7e849674862f65')
check('original RET freeze exact',sha(RET/'RET-GATE-FREEZE.json')=='ac322b2bcffaa0b2a243ddb87755eb0af8b50e7e4d7be8ce0aa6e2da795f93c6')
f=json.loads((RET/'RET-GATE-FREEZE.json').read_text())
for a in f['files']+f['cache_only_inputs']:
 p=RET/a['path'];check('old RET binding '+a['path'],sha(p)==a['sha256'] and ('bytes' not in a or p.stat().st_size==a['bytes']))
prior=Path('/workspace/emc-r6-challenge/research/autonomy/fresh-discovery-2026-10-05-round9/imprinting/sources/ret_emc_prior.json')
check('prior RET activation source exact',sha(prior)=='d62aa04f1ab5e6fa0e5191ae310a92fd8525bf80e56464dc590ad10b274040a5')
x=HERE/'source-cache/Crossref-exact-DOI.json';check('new Crossref source exact',sha(x)=='04c0f334aa504f5c0409fb649107b55becbf6e65814419f69b207ed6cc3b5db8' and x.stat().st_size==44222)
m=json.loads(x.read_text())['message']
check('DOI title and preprint match',m['DOI']=='10.64898/2026.07.08.737171' and m['title']==['Prospective pan-cancer phosphoproteomics at clinical scale extends therapeutic options in precision oncology'] and m['type']=='posted-content')
check('registered date and publisher',m['published']['date-parts']==[[2026,7,9]] and m['publisher']=='openRxiv')
a=m.get('author',[]);check('canonical author source identity',a[0]['family']=='Schneider' and a[-1]['family']=='Kuster' and a[-1]['given']=='Bernhard')
check('no declared Crossref relations in this response',m.get('relation')=={},'Not global absence of clinical data')
check('returned link is similarity-checking not deposit',len(m['link'])==1 and m['link'][0]['intended-application']=='similarity-checking')
check('105reference schema scope',len(m['reference'])==105 and sum('DOI' in r for r in m['reference'])==103 and sum('unstructured' in r for r in m['reference'])==3,'No105study review claim')
check('one actual method citation',any(r.get('DOI')=='10.1101/2025.11.18.689017' and 'Chemical proteomics' in r.get('unstructured','') for r in m['reference']),'Not a clinical manifest or EMC measurement')
for relative,expected in [('diffusion_mri_omission_review/FREEZE.json','eea728f90f2d711ab59cf620e2748c1283da1522ce90e855ee6daaf49a8a1bea'),('telomere_phenotype_review/FREEZE.json','12e095a257654cac2569ea23b3bf3794544eab9b669844fc4fb6771d84e67352'),('microvascular_review/FREEZE.json','c53fac73ede21fff60a4fc13c56b89e17fcd9c5cf24d52e8985aa148c6e60c68')]:
 p=HERE.parent/relative;check('immutable earlier freeze '+relative,sha(p)==expected)
 old=json.loads(p.read_text());records=old.get('files',old.get('bindings',[]))
 for r in records:
  name=r.get('file',r.get('path'));target=p.parent/name
  check('immutable earlier export '+relative+':'+name,sha(target)==r['sha256'])
schema=OWNER/'raw-cache/public-column-schema.source'
check('public metadata schema exact',sha(schema)=='c1ce0c6a335c974e2ab45ca9f7020f236d30fbf928989d810b3cbc5590c19a42')
cols=json.loads(schema.read_text())
check('19 dictionary column definitions not empty',isinstance(cols,list) and len(cols)==19 and all(isinstance(c,dict) for c in cols))
check('patient condition field labels supplied',{'case_submitter_id','primary_diagnosis','tumor_grade','treatment_type','treatment_outcome','site_of_resection_or_biopsy'} <= {c.get('dataField') for c in cols},'Headers only, not patient values or release provenance')
cohort=OWNER/'raw-cache/public-cohort-names.source'
check('cohort identifier source exact',sha(cohort)=='17b883dd4a125c32f8c97d0c200283b233b3463085bc6553dba1755503c21f7a')
check('four returned CPTAC identifiers',json.loads(cohort.read_text())==['LUAD_CPTAC','BRCA_CPTAC','UCEC_CPTAC','CPTAC_PAN_Cancer'],'Not exhaustive portal inventory or disease transfer')
check('final owner manifest exact',sha(OWNER/'MANIFEST.json')=='36a96dea16f024e9b6a7cdfd36ccc4ea63745e7c80ae68a0fc54a7bcaf5f85ed')
owner_manifest=json.loads((OWNER/'MANIFEST.json').read_text())
for row in owner_manifest['files']:
 p=OWNER/row['file'];check('owner final export '+row['file'],sha(p)==row['sha256'] and p.stat().st_size==row['bytes'])
owner_port=json.loads((OWNER/'PORTABILITY.json').read_text())
for row in owner_port['raw_sources']:
 p=OWNER/row['path'];check('owner retained raw '+row['path'],sha(p)==row['sha256'] and p.stat().st_size==row['bytes'])
correction=json.loads((OWNER/'SCHEMA-READ-CORRECTION.json').read_text())
check('one correction batch retained before freeze',correction['raw_schema_sha256']=='c1ce0c6a335c974e2ab45ca9f7020f236d30fbf928989d810b3cbc5590c19a42' and '19dictentries' in correction['actual_schema'])
check('10GiBfreefloor',shutil.disk_usage(HERE).free>=10737418240)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS source/index and immutable-prior verification','checks':checks,'checks_count':len(checks),'phosphosite_or_kinase_outcomes_parsed':0,'new_target_selection':False,'source_assay_indices_only':True,'full_repository_gates':'Pending integrating lead, not claimed by sparse source reviewer.'}
(HERE/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'failed':0}))
