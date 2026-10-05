import pathlib,json,hashlib,datetime,os
p=pathlib.Path(__file__).parent;owner=pathlib.Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round9/clinical_measurements/gpnmb_culture_context_quantification');x=json.load(open(p/'INDEPENDENT-RAW-FEATURE-EXTRACTION.json'));r=json.load(open(owner/'RESULTS.json'));freeze=json.load(open(owner/'SCIENCE-FREEZE.json'));checks=[]
def ck(name,a,b):checks.append({'check':name,'pass':a==b,'independent':a,'owner_or_expected':b})
for f in freeze['files']:
 b=(owner/f['name']).read_bytes();ck('frozen_sha:'+f['name'],hashlib.sha256(b).hexdigest(),f['sha256']);ck('frozen_bytes:'+f['name'],len(b),f['bytes'])
for s in r['sources']:
 actual=next(i['sha256'] for i in x['source_bindings'] if i['path']==s['path']);ck('original_sha:'+s['path'],actual,s['sha256'])
ck('owner_plan_sha',hashlib.sha256((owner/'PLAN-FROZEN.json').read_bytes()).hexdigest(),r['plan_sha256'])
conds=r['conditions'];ah=x['ARCHS4']['symbol_hits'];ck('ARCHS4_unique_GPNMB',len(ah),1)
for c in conds[:2]:
 ck('ARCHS4value:'+c['GSM'],ah[0]['lexemes'][c['GSM']],c['reported_value']);ck('ARCHS4physical_line:'+c['GSM'],ah[0]['line'],c['source_row_number']);ck('ARCHS4column:'+c['GSM'],x['ARCHS4']['header'].index(c['GSM']),c['source_column'])
u=x['USZ22'];c=conds[2];ck('USZ22unique_GPNMB',len(u['GPNMB_hits']),1);h=u['GPNMB_hits'][0]
for name,a,b in [('value',h['lexeme'],c['reported_gene_count']),('physical_line',h['line'],c['source_row_number']),('column',h['column_index_zero_based'],c['source_column']),('allrows',u['source_data_rows'],c['full_reported_feature_rows']),('invalid',len(u['invalid']),c['invalid_or_negative_reported_counts']),('sum',u['reported_count_sum_decimal'],c['denominator_reported_count_sum']),('share',u['per_million_reported_count_share_decimal'],c['per_million_reported_count_share'])]:ck('USZ22:'+name,a,b)
ck('USZ22sameGSMnotreplicate',c['GSM'],conds[1]['GSM']);ck('USZ22exactunique_column',u['header'].count('USZ-22_EMC2'),1)
v=x['USZ23'];c=conds[3];ck('USZ23four_unique',v['all_four_unique_finite_nonnegative'],True)
for a,b in zip(v['fixed_features_in_prespecified_order'],c['features']):
 for name,aa,bb in [('identifier',a['Name'],b['Name']),('physical_line',a['line'],b['source_row_number']),('TPMlexeme',a['TPM_lexeme'],b['reported_TPM']),('NumReadslexeme',a['NumReads_lexeme'],b['reported_NumReads'])]:ck('USZ23:'+a['Name']+':'+name,aa,bb)
ck('USZ23partial_TPM',v['partial_TPM_subtotal_decimal'],c['partial_four_feature_TPM_subtotal']);ck('USZ23partial_NumReads',v['partial_NumReads_subtotal_decimal'],c['partial_four_feature_NumReads_subtotal'])
ck('USZ23zero_lexemes_preserved',[(a['TPM_lexeme'],a['NumReads_lexeme']) for a in v['fixed_features_in_prespecified_order'][2:]],[('0.000000','0.000'),('0.000000','0.000')])
now=datetime.datetime.now(datetime.timezone.utc).isoformat();free=os.statvfs(p).f_bavail*os.statvfs(p).f_frsize
out={'scientific_closed_utc':now,'hard_stop':'2026-10-05T21:44:02+00:00','before_deadline':now<'2026-10-05T21:44:02','n_checks':len(checks),'failed':[c for c in checks if not c['pass']],'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':checks,'free_bytes':free,'original_counting_semantics':'Owner source_row_number is physical line includingheader. Independent also preserves data_row=line−1 explicitly; no roworder repair or differentselectedfeatures.','scope':'Exact fixed threeoriginal-source feature extraction and arithmetic validation only; no new discovery/statistics/crossassay pooling/completegenecapture/protein/localization/dependency claim.','exposure':'Owner fixed row/feature summary exposed beforeprotocol; full result quantities read only after independent source extraction. Failedleadingblankheader assumption and sourcefeature diagnosis exposure explicit AM01. Not globally blind.'};(p/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
