import pathlib,json,hashlib,xml.etree.ElementTree as E
P=pathlib.Path(__file__).resolve().parent
D=json.loads((P/'ALL23-BIOSAMPLE-SRA-SAFE-METADATA.json').read_text());checks={}
for r in D['sources']:checks['hash_'+r['key']]=hashlib.sha256(pathlib.Path(r['path']).read_bytes()).hexdigest()==r['sha256']
checks['source15assertions']=json.loads((P/'SOURCE-VERIFICATION.json').read_text())['pass']
nd=json.loads((P/'NATIVE-CONTROL-PREPARATION-REUSE.json').read_text());checks['all12native']=len(nd['native12'])==12;checks['7EWS5TAF']=[sum(r['partner']==p for r in nd['native12']) for p in ['EWSR1','TAF15']]==[7,5];checks['fivepreps4EWS1TAF']=(nd['matched_additional_frozen5']['n'],nd['matched_additional_frozen5']['EWSR1'],nd['matched_additional_frozen5']['TAF15'])==(5,4,1)
prim=E.parse(next(s['path'] for s in D['sources'] if s['key']=='primary')).getroot();tab=next(t for t in prim.findall('.//table-wrap') if ' '.join(t.findtext('label','').split())=='Table 1');original=[[' '.join(''.join(x.itertext()).split()) for x in r] for r in tab.findall('.//tbody/tr')]
checks['primary12caseRowsExact']=[[str(x['published_case']),x['partner'],x['sex'],str(x['age']),x['site']] for x in nd['native12']]==original
checks['noNativeFromGenericLabel']=all(r['native_case_partner_preparation_link'].startswith('unknown') for r in D['rows'])
checks['noRNAfieldsSelected']=not any(set(r)&{'metadata_read_pairs','metadata_total_bases','FASTQ_source_metadata','expression','TPM','values'} for r in D['rows'])
O=pathlib.Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/brenca_native_metadata_bridge');m=json.loads((O/'SCIENCE-FREEZE.json').read_text())
for r in m['files']:checks['owner_'+r['name']]=hashlib.sha256((O/r['name']).read_bytes()).hexdigest()==r['sha256'] and (O/r['name']).stat().st_size==r['bytes']
owner=json.loads((O/'ALL23-RETAINED-METADATA-REPLAY.json').read_text());om={r['BioSample']:r for r in owner['records']}
checks['owner23identitySafeExact']=all(all(r[k]==om[r['BioSample']][k] for k in ['SRA_sample','experiment','library_name','design','prior_identity']) and r['BioSample_attributes']==om[r['BioSample']]['attributes'] and r['runs']==[om[r['BioSample']]['run']] for r in D['rows'])
checks['ownerNoRNAnewSource']=json.loads((O/'DECISION.json').read_text())['new_network_requests']==0 and json.loads((O/'DECISION.json').read_text())['new_RNA_outcomes']==0
assert all(checks.values()),checks
print(json.dumps({'pass':True,'checks':len(checks),'details':checks,'new_requests':0,'new_raw':0,'new_RNA_values':0}))
