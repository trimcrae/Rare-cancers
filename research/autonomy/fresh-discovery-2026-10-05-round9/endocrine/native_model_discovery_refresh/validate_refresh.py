#!/usr/bin/env python3
"""Source/metadata/native-unit integrity only; no response or gene-value analysis."""
import pathlib,json,hashlib,datetime,shutil
P=pathlib.Path(__file__).resolve().parent
checks=[]
def check(k,v):checks.append({'check':k,'pass':bool(v)})
def bound(x):
 f=pathlib.Path(x['path']);b=f.read_bytes();return len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
for f in P.glob('*.json'):json.loads(f.read_text())
for a in json.loads((P/'REUSED-SOURCE-DECISIONS.json').read_text())['sources']:check('reused_'+pathlib.Path(a['path']).name,bound(a))
port=json.loads((P/'PORTABILITY.json').read_text())
check('cache_sources_all_exact',all(bound(x) for x in port['cache_only']))
check('newraw_under8MiB',port['new_retained_cache_bytes']<=8388608)
check('free_above10GiB',shutil.disk_usage(P).free>=10737418240)
q=json.loads((P/'METADATA-SOURCE-RECEIPTS.json').read_text())
check('exactNCC2query_unconfirmed_0',q[0]['hitCount']==0 and q[0]['returned']==0)
check('exactdisease_metadata_enumerated_only',q[2]['hitCount']==q[2]['returned']==21 and q[3]['hitCount']==q[3]['returned']==22)
resources=json.loads((P/'AUTHOR-MODEL-RESOURCE-RECEIPTS.json').read_text())
c=[x for x in resources if x['name']=='known_full_control'][0]
check('knownNCC1positive_metadata_control',c['hitCount']==c['returned']==1)
m=json.loads((P/'MODEL-RESOURCE-IDENTITY-GATE.json').read_text())
check('all3catalogue_records_retained',len(m['all_returned_entries'])==3)
names=[x['source_names'][0]['value'] for x in m['all_returned_entries']]
check('sameknownUSZ/disputedcatalogue',names==['USZ20-EMC1','USZ22-EMC2','H-EMC-SS'])
check('disputedcatalogue_doesnotauthenticate',m['all_returned_entries'][2]['native_authentication_disposition'].startswith('disputed'))
check('Kondo_original_supp_reuse_three',m['Kondo2026_primary_supplements_verified_reuse']['S1']['EMC_total']==3)
a=json.loads((P/'JINNO-SAFE-IDENTITY-AND-METHOD-GATE.json').read_text())
check('genuineJinno_exact_source',a['citation']['PMID']=='42456169' and a['citation']['DOI'].lower()=='10.1158/1535-7163.mct-26-0096')
check('fullcase/assaymapping_explicitlyunresolved',all(x is None for x in a['roster_method_fields'].values()))
check('taxonomymentions_notfullroster',a['safe_abstract_taxonomy_mentions']==['leiomyosarcoma','rhabdomyosarcoma'] and a['explicit_abstract_model_codes']==[])
access=json.loads((P/'JINNO-PUBLISHED-ACCESS-RECEIPTS.json').read_text())
check('actualpublisher403bound',access[0]['status']==403 and bound(access[0]))
check('noOAmetadata_link',json.loads((P/'raw-cache/jinno_openalex').read_text())['best_oa_location'] is None)
check('noPMCidentifier',json.loads((P/'JINNO-PRIMARY-LINK-METADATA.json').read_text())['pmcid'] is None)
check('noresponse_numericalstage',json.loads((P/'EXPOSURE-AND-QUERY-QA.json').read_text())['outcome_stage'] is False)
check('NCC2_notinvented',json.loads((P/'DECISION.json').read_text())['nativeNCC2existence'].startswith('UNKNOWN'))
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Exactmetadata/source/hash/assay-unit/status validation, not fulloriginal-source scientific reproduction or responseanalysis.','checks':checks,'errors':[x['check'] for x in checks if not x['pass']],'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL'}
(P/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'errors':result['errors']}));raise SystemExit(bool(result['errors']))
