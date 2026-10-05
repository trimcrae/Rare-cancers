"""Offline assembly of allowed identity/role dispositions. No network or outcomes."""
import pathlib,json,hashlib,datetime,collections
P=pathlib.Path(__file__).resolve().parent
R=P.parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(n):return json.loads((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bio=load('ALL68-BIOSAMPLE-IDENTITY-CONDITION-FIELDS.json')
geo=load('RETAINED-GEO-WHITELIST-REPLAY.json')
oldpath=R/'gpnmb_source_access_status/GSE299349-ALL68-EVALUATED-SOURCE-FIELDS.json'
old=json.loads(oldpath.read_text())
oldby={r['GSM']:r for r in old['samples']}
group=collections.defaultdict(dict)
for r in geo['source_rows']:
 if r['field']=='!Sample_source_name_ch1':group[r['GSM']]['source_name']=r['value']
 elif r['value'].startswith('tissue:'):group[r['GSM']]['tissue']=r['value'].split(':',1)[1].strip()
 elif r['value'].startswith('cell type:'):group[r['GSM']]['cell_type']=r['value'].split(':',1)[1].strip()
assert len(oldby)==len(group)==len(bio['records'])==68
rows=[]
for r in bio['records']:
 gsm=r['GSM'];o=oldby[gsm];g=group[gsm]
 ba={a['harmonized_name'] or a['attribute_name']:a['value'] for a in r['identity_condition_attributes']}
 assert ba['source_name']==g['source_name'] and ba['tissue']==g['tissue']
 assert ba.get('cell_type')==g.get('cell_type')
 hascell='cell_type' in ba
 diagnosis=ba.get('cell_type') or ba['tissue']
 assert diagnosis!='cells'
 emc='myxoid chondrosarcoma' in diagnosis.casefold()
 role=('Existing independently authenticated USZ23 EMC culture; current three-culture measurement gate has already evaluated its permitted GPNMB input. No new donor or quantity.' if emc else 'Submitted explicit non-EMC histotype label; outside the native-EMC input universe at this source-label scope. No histology inferred from its alias.')
 rows.append({'GSM':gsm,'BioSample':r['BioSample'],'declared_BioSample_url':r['declared_url'],'source_alias_only':o.get('source_alias_only'),'GEO_identity_fields':g,'BioSample_identity_fields':{k:ba[k] for k in ['source_name','tissue','cell_type','collection_date'] if k in ba},'identity_evidence_unit':'One GEO/BioSample library record, not an independently authenticated donor','source_label_status':'EMC already evaluated' if emc else 'Source-labelled non-EMC','EMC_access_consequence':role,'processed_source_links':o['actual_processed_source_links'],'source_molecule':o['molecule_ch1'],'role_limit':'Individual donor, patient/model lineage, technical-repeat, preservation, treatment and comparator alignment are not established by these identity fields. Source collection date is missing.','additional_EMC_numerical_action':'None; no additional EMC label or authenticated EMC condition emerged.'})
counts=collections.Counter(r['BioSample_identity_fields'].get('cell_type') or r['BioSample_identity_fields']['tissue'] for r in rows)
core=[r for r in rows if 'cell_type' in r['BioSample_identity_fields']]
remaining=[r for r in rows if 'cell_type' not in r['BioSample_identity_fields']]
assert len(core)==6 and len(remaining)==62
assert collections.Counter(r['BioSample_identity_fields']['tissue'] for r in remaining)=={'myxofibrosarcoma':14,'synovial sarcoma':12,'undifferentiated pleomorphic sarcoma':13,'malignant peripheral nerve sheath tumor':11,'leiomyosarcoma':12}
assert len([r for r in rows if r['source_label_status']=='EMC already evaluated'])==1
out={'created_utc':now,'question':'Does the GSE299349 membership contain another author-labelled EMC record needing ordinary RNA evaluation?','answer':'No additional source-labelled EMC record was found among these exact 68 records. The one directly labelled USZ23 EMC culture was already evaluated. This is a submitted-metadata eligibility conclusion, not universal histopathological exclusion or evidence about EMC expression.','units':{'membership_records':68,'six_prior_direct_cell_type_records':6,'previously_called_generic_records':62,'explicit_EMC_records':1,'additional_explicit_EMC_records':0,'proved_independent_donors':'Not established'},'previous62_tissue_label_counts':dict(collections.Counter(r['BioSample_identity_fields']['tissue'] for r in remaining)),'all68_histotype_labels':dict(counts),'source_agreement':'All68 retained GEO source_name/tissue and all6 cell_type strings match corresponding current BioSample fields literally. The old retained fields, not a novel disease-identification source, already supported these labels.','records':rows,'new_GPNMB_values':0,'new_effect_statistics':0,'eligible_new_EMC_quantitative_stage':False}
(P/'ALL68-EVALUATED-ROLE-DISPOSITIONS.json').write_text(json.dumps(out,indent=2)+'\n')
amendment={'created_utc':now,'original_plan_preserved_sha256':sha(P/'PLAN-FROZEN.json'),'original_source_packet_preserved_sha256':sha(R/'gpnmb_source_access_status/SCIENCE-FREEZE.json'),'correction':'The earlier narrative classification of62 records as generic/unresolved EMC identity overlooked explicit source_name/tissue histotype strings already present in retained GEO. They lack cell_type but carry explicit MFS14/SS12/UPS13/MPNST11/LMS12 labels. BioSample confirms these exact labels; it is not a newly discovered native cohort or additional EMC bridge.','what_remains_unresolved':'Individual donor/model/technical-repeat/perturbation/preservation roles and independent pathological re-review for these submitted labels. These limits do not turn explicit non-EMC submitted diagnoses into unknown EMC identities.','alias_correction':'Current retained GSM9037835 source alias is USZ-20_REA1. Earlier root/task CIC1 shorthand is not source-bearing for this record. The literal BCOR-rearranged sarcoma identity label governs eligibility; no underlying rearrangement mechanism was inspected.','before_and_after_counts':{'old_narrative':'six direct cell_type records plus62 incorrectly described generic identities','corrected_source_scope':'six direct cell_type records plus62 explicit non-EMC source_name/tissue labels; one already evaluated EMC record total'},'no_changed_originals':True,'no_new_quantities':True,'no_new_COMPARATOR_analysis':True,'consequence':'No additional native-EMC numerical action from this exact68 metadata universe. Preserve unknown donor and assay compatibility; do not pool other histotypes or substitute aliases for labels.','evidence':[{'path':'RETAINED-GEO-WHITELIST-REPLAY.json','sha256':sha(P/'RETAINED-GEO-WHITELIST-REPLAY.json')},{'path':'ALL68-BIOSAMPLE-IDENTITY-CONDITION-FIELDS.json','sha256':sha(P/'ALL68-BIOSAMPLE-IDENTITY-CONDITION-FIELDS.json')} ]}
(P/'AMENDMENT-01-RETAINED-IDENTITY-CLASSIFICATION.json').write_text(json.dumps(amendment,indent=2)+'\n')
print(json.dumps({'68_role_records':len(rows),'new_EMC_records':0,'all68_exact_GEO_BioSample_agreement':True,'previous62_histotypes':out['previous62_tissue_label_counts'],'amendment_sha256':sha(P/'AMENDMENT-01-RETAINED-IDENTITY-CLASSIFICATION.json')}))
