"""Zero-copy replay of root-authorized diagnosis-only indexed metadata; no requests."""
from pathlib import Path
import json,hashlib,datetime,re,shutil
HERE=Path(__file__).resolve().parent
OWNER=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/phosphoproteomic_manifest_gate/diagnosis_eligibility_stage')
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,v):
 checks.append({'check':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
plan=json.loads((OWNER/'PLAN.json').read_text());check('owner prospectiveplan exact',sha(OWNER/'PLAN.json')=='aa8fca141c7919e5d5a7eb789450041740e4a3fc56571867c824a801591227b3')
access=json.loads((OWNER/'ACCESS.json').read_text());check('exact4requestsrootauthorized',len(access['responses'])==4 and [r['index'] for r in access['responses']]==[0,1,2,3])
check('receipt noauth cookies tokens redirect follow',access['noauth_cookies_tokens_redirect_follow'] is True)
expected=[('cdf9914efd3710c64515cef6f2740cef9f62769f7bd6f31c36b6ad7e5f45996d',34,2),('8772f48b12957840eb1fe6b1ca9d28d27ce233d73e9e39ec3f662b96ea7ff77f',278,9),('ba14f16376bdbcda5ce2f1c1c176cbe3ba63b6a7e5b8da9712ec4f5866c6fd6c',47,2),('c4dbea79b7fe588ccf563cdb7ceeb2defeff0c0bd376b4e2775dc964aa6b8685',316,10)]
all_labels=[];sets=[]
for i,r in enumerate(access['responses']):
 f=OWNER/r['file'];h,b,n=expected[i];raw=f.read_bytes();labels=json.loads(raw)
 check('payloadexact '+str(i),sha(f)==h==r['sha256'] and len(raw)==b==r['bytes'])
 check('exactdocumented fieldURL '+str(i),r['url']=='https://topas-portal.kusterlab.org/master_topas-portal_backend/'+str(i)+'/metadata/fields/primary_diagnosis')
 check('HTTP200JSON '+str(i),r['http']==200 and r['content_type']=='application/json')
 check('unique stringlist shape '+str(i),isinstance(labels,list) and len(labels)==n and all(isinstance(x,str) for x in labels) and len(set(labels))==n and labels==sorted(labels))
 check('noatcap '+str(i),not r['at_cap'] and b<1048576)
 check('calls afterbeforevaluesfreeze '+str(i),datetime.datetime.fromisoformat(r['utc'])>datetime.datetime.fromisoformat(plan['utc']))
 sets.append(set(labels));all_labels.extend((i,k,s) for k,s in enumerate(labels))
check('23unique labelentries notpatients',len(all_labels)==23)
check('fourempty unknownmarkers',sum(s=='' for _,_,s in all_labels)==4)
check('twoNotReported markers',sum(s=='Not Reported' for _,_,s in all_labels)==2)
known=[s for _,_,s in all_labels if s not in ['', 'Not Reported']]
check('17literal carcinoma labelentries',len(known)==17 and all('carcinoma' in s.lower() for s in known))
check('noexplicitEMCorfixedsarcoma labels atliteral scope',not any(re.search(r'\bEMC\b|extraskeletal|extra-skeletal|chondrosarcoma|sarcoma|myxoid|chordoid|NR4A3',s,re.I) for _,_,s in all_labels))
check('indexed3categoryset uniononly',sets[3]==sets[0]|sets[1]|sets[2])
eval_labels=json.loads((HERE/'ALL-EVALUATED-DIAGNOSIS-LABELS.json').read_text())['labels'];check('all23extract observations exact',[(x['response_index'],x['label_position'],x['primary_diagnosis']) for x in eval_labels]==all_labels)
port=json.loads((HERE/'PORTABILITY.json').read_text());check('675Bresponses reviewerzero newraw',sum(x['bytes'] for x in port['shared_response_inputs'])==675 and port['reviewer_new_raw_bytes']==0)
parent=HERE.parent;check('backend oldfreeze untouched',sha(parent/'FREEZE.json')=='5585b3fe3be18bf3d9e25d6e113902a2a74f6ff03e3d4a786a2e86d55725ea1d')
for x in json.loads((parent/'FREEZE.json').read_text())['bindings']:check('backend oldexport '+x['file'],sha(parent/x['file'])==x['sha256'])
science=parent.parent;check('science oldfreeze unchanged',sha(science/'FREEZE.json')=='490da03d703fff7519096c2c0ef6ccc5175f74f784276985c2d3fe2a4c9dc1a1')
for x in json.loads((science/'FREEZE.json').read_text())['bindings']:check('science oldexport '+x['file'],sha(science/x['file'])==x['sha256'])
owner_manifest=OWNER/'MANIFEST.json'
check('owner final manifest exact',sha(owner_manifest)=='21c1b583c89f8eebad86b81f62847a3ac7e5c358870274f55992151e070bac28')
m=json.loads(owner_manifest.read_text());check('owner six frozen exports',len(m['files'])==6)
for x in m['files']:check('owner final export '+x['file'],sha(OWNER/x['file'])==x['sha256'] and (OWNER/x['file']).stat().st_size==x['bytes'])
for x in m['source_bindings']:check('owner original source binding '+Path(x['path']).name,sha(Path(x['path']))==x['sha256'])
p=json.loads((OWNER/'PORTABILITY.json').read_text());check('owner all four exact raw bindings',len(p['raw_files'])==4 and p['raw_bytes']==675)
for x in p['raw_files']:check('owner final raw binding '+x['file'],sha(OWNER/x['file'])==x['sha256'] and (OWNER/x['file']).stat().st_size==x['bytes'])
e=json.loads((OWNER/'EVALUATED-LABEL-ELIGIBILITY.json').read_text())
check('owner all label routes exactly match responses', {(r['source_label'],i) for r in e['rows'] for i in r['indexed_routes']}=={(label,i) for i,_,label in all_labels})
check('owner all label denominators match',e['route_label_counts']==[2,9,2,10] and e['label_occurrences']==23 and e['missing_marker_label_occurrences']==6 and e['carcinoma_label_occurrences']==17 and e['global_unique_labels']==10 and e['global_named_carcinoma_labels']==8)
check('owner no eligible literal diagnosis',e['explicit_EMC_MLPS_SS_LGFMS_or_generic_sarcoma_myxoid_chondrosarcoma_labels_observed'] is False)
d=json.loads((OWNER/'DECISION-COVERAGE.json').read_text());check('owner numerical stage no-go and campaign continues',d['decision']=='SOURCE NO-GO for numerical biological stage; campaign continues.')
check('owner labels and missing conditions coverage',len(d['coverage'])==6 and 'SQL' in d['coverage'][4]['detail'] and '1998' in d['coverage'][4]['scope'] and 'dropna' in d['coverage'][3]['detail'])
check('owner label equality not donor proof',any('donor overlap or replication' in z for z in d['strongest_limits']))
check('no retrieval script claimed',not any('retriev' in x['file'].lower() for x in m['files']))
check('free10GiB',shutil.disk_usage(HERE).free>=10737418240)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS scoped indexed diagnosis eligibility source replay','checks':checks,'checks_count':len(checks),'reviewer_requests':0,'biochemical_or_treatment_outcomes_inspected':0,'denominators':'Only unique labels; no patient/donor/missingness fractions','limits':'Anonymousaccess reportedforfourdatedfieldonlycalls; namedcohort/SQLorder/runtimebackend/1998links stillunknown. No broaderabsence inference.','repo_gates':'Pending integrating lead, not sparseworkerpassed'}
(HERE/'VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(checks),'failed':0}))
