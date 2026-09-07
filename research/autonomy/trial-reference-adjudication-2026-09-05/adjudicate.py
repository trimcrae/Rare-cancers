"""Evidence adjudication after immutable independent freeze; offline and unfitted."""
import json,copy,hashlib,datetime
from pathlib import Path
from independent_judgments import OUT,ROOT,REPAIR,load,sha,now,dump,J

def build():
 freeze=load(OUT/'independent-freeze-receipt.json')
 for n,h in freeze['sha256'].items():assert sha((OUT/n).read_bytes())==h
 first=load(REPAIR/'reference.json');ind=load(OUT/'independent-labels.json');selection=load(REPAIR/'selection.json')
 fidx={(p['diagnosis'],p['nct_id']):p for p in first['pairs']}
 details={
 ('DSRCT','NCT05918640'):('Retain independent disease-scope label; first-reader hold evidence accepted in a separate conditional-availability field.','Both readers identify the same phase-1 FET-compatible DSRCT scope and unknown safety-lead-in release. The first reader used explicit_exclusion for a conditional enrollment hold. The source says until at least 3 non-DSRCT patients have been enrolled without dose limiting toxicity; it does not state whether this threshold has or has not been cleared. The final disease-scope label is explicit_diagnosis_compatible with conditional_hold_release_unknown. Neither an unconditional exclusion nor an open-slot assertion is supported.'),
 ('SS','NCT05918640'):('Retain independent broad histology label, with molecular gate explicitly unestablished and excluded from uncomplicated-positive scoring.','The same phase-1 criterion requires a recurrent/relapsed solid tumor plus a documented EWSR1/FUS/TAF15 fusion. It does not name a synovial-sarcoma exclusion, but SS18::SSX does not meet the FET requirement. Broad_tumor_compatible describes histologic scope only; additional FET fusion presence and protocol acceptance remain unestablished. This harmonizes the histology-versus-biomarker distinction used for the DDR, KRAS and B7-H3 conditional baskets; it is not evidence that SS qualifies. The first-reader insufficient_evidence concern is preserved in molecular_compatibility and benchmark disposition.')}
 biomarker_trials={'NCT05918640','NCT05071209','NCT07695311','NCT06456359','NCT07297979','NCT06094101','NCT06571734','NCT07698899','NCT07030959','NCT07686367','NCT05687136'}
 conditional_extra={('SS','NCT05918640'),('SS','NCT05071209'),('EMC','NCT05687136'),('DSRCT','NCT05687136'),('SS','NCT05687136'),('DSRCT','NCT07030959'),('SS','NCT07698899'),('SS','NCT07686367')}
 addenda={
 'NCT04901702':'Eligibility age >12 months and <30 differs from inclusive-looking structured bounds; text controls this uncertainty.',
 'NCT06094101':'Description says age <40 while structured maximumAge is 40; retain this source conflict.',
 'NCT06526897':'Structured phase NA differs from phase III description. This is surveillance, not a drug treatment trial.',
 'NCT07359053':'HBV carrier allowance and active-HBV thresholds need clinical/protocol reconciliation; no hepatitis status inferred.',
 'NCT07383116':'A squamous-NSCLC testing note is inconsistent with nonsquamous indication. Both alternatives still fail to establish EMC scope.',
 'NCT07695311':'Description mentions anti-CTLA-4 although listed combination arm specifies pembrolizumab; regimen details require protocol clarification. This does not change EMC exclusion.',
 'NCT07698899':'Full eligibility age <22 differs from structured maximumAge 22.',
 'NCT06625190':'Cure/expected-survival numbers in eligibility are sponsor-defined inclusion conditions, not prognosis estimates validated by this adjudication.'}
 pairs=[];decisions=[]
 for independent in ind['pairs']:
  key=(independent['diagnosis'],independent['nct_id']);old=fidx[key];n=key[1];d=key[0];a=copy.deepcopy(independent)
  assert {(x['set'].replace('metadata_sample','metadata').replace('challenge_anchor','challenge'),x['stratum'] if x['set']=='metadata_sample' else 'anchor') for x in old['sets']}=={(x['set'],x['stratum']) for x in a['memberships']}
  a['pair_id']=old['pair_id'];a['independent_pair_id']=independent['pair_id'];a['sets']=copy.deepcopy(old['sets'])
  a['current_availability']['snapshot_current']=old['snapshot_current'];a['current_availability']['status_verified_date']=old['status_verified_date']
  assert old['overall_status']==a['current_availability']['overall_status_snapshot']
  a['clinical_trial_purpose']['oncology_task_domain']=old['oncology_task_domain']
  a['exclusions_and_other_constraints']=old['exclusions_and_other_constraints']
  a['external_protocol_reviewed']=False;a['clinical_eligibility_established']=False
  a['known_missing_additional_exclusions']=n=='NCT05135975'
  a['source_internal_uncertainty_addendum']=addenda.get(n,'No additional adjudication note; complete saved modules retained.')
  a['extra_biomarker_requirement']['state']='required_unestablished' if key in conditional_extra else ('required_variant_or_protocol_confirmation' if n in biomarker_trials else 'no_additional_tumor_gate_stated_or_not_applicable_to_excluded_histology')
  a['molecular_compatibility']={'status':'unestablished' if key in conditional_extra else ('defining_fusion_match' if a['label']=='defining_fusion_compatible' else 'variant_or_class_conditional' if a['label']=='fusion_class_compatible' else 'not_established_by_label'),'detail':a['extra_biomarker_requirement']['detail']}
  a['current_availability']['conditional_safety_hold']={'state':'release_unknown','condition':'At least 3 non-DSRCT patients enrolled without dose limiting toxicity','known_current_hold_in_effect':None,'evidence_id':n+':quote:1'} if key==('DSRCT','NCT05918640') else None
  # These are interpretation flags, never fitted binary labels or retrieval scores.
  if a['clinical_trial_purpose']['task_domain']=='nononcology':use='outside_oncology_endpoint; do_not_treat_as_patient_eligibility_negative'
  elif key in conditional_extra:use='biomarker_unestablished; exclude_from_uncomplicated_positive_or_negative_scoring'
  elif key==('DSRCT','NCT05918640'):use='conditional_safety_hold_release_unknown; no_unconditional_availability_label'
  elif a['label']=='insufficient_evidence':use='unresolved; do_not_score_as_negative'
  elif n=='NCT05135975':use='registry_histology_scope_only; missing_protocol_exclusions; no_definitive_eligibility_label'
  elif a['label']=='explicit_exclusion':use='source_supported_disease_scope_restriction_only; not_global_patient_ineligibility'
  else:use='registry_disease_scope_only; retain_variant_cohort_purpose_and_snapshot_conditions'
  a['benchmark_disposition']=use
  changed=old['label']!=a['label'];decision,why=details.get(key,('Concordant scope label retained after independent source comparison.','Both readers support the same disease-scope label. The complete saved eligibility, descriptions and all arm/cohort modules support the independent rationale. Final fields retain both readers, source-specific uncertainty, original sample membership and snapshot status.'))
  if not changed:why+=' '+a['eligibility_scope']['rationale']
  decision_record={'pair_id':old['pair_id'],'label_discrepancy':changed,'first_reader_label':old['label'],'independent_label':independent['label'],'adjudicated_label':a['label'],'decision':decision,'source_grounded_resolution':why,'evidence_ids':a['evidence_ids'],'uncertainty_disposition':use,'adjudication_scope':'All 49 pairs reviewed; label concordance does not waive cohort, biomarker, purpose or status review.'}
  decisions.append(decision_record)
  pairs.append({'pair_id':old['pair_id'],'diagnosis':d,'nct_id':n,'sets':copy.deepcopy(old['sets']),'first_reader':copy.deepcopy(old),'independent_reader':copy.deepcopy(independent),'adjudicated':a,'adjudication':decision_record})
 return first,ind,pairs,decisions
if __name__=='__main__':
 first,ind,pairs,decisions=build();stamp=now();(OUT/'discrepancy').mkdir(exist_ok=True)
 dump('discrepancy/adjudication.json',{'created_utc':stamp,'first_reader_reference_sha256':sha((REPAIR/'reference.json').read_bytes()),'independent_freeze_sha256':sha((OUT/'independent-freeze-receipt.json').read_bytes()),'label_discrepancy_count':sum(x['label_discrepancy'] for x in decisions),'decisions':decisions,'unresolved_adjudication_disagreements':[],'unresolved_source_questions':'All source uncertainties remain explicit; resolution means evidence-based disposition, not obtaining missing protocol information.'})
 dump('adjudicated-reference.json',{'schema':'emc-independent-adjudicated-reference/1','state':'independent_model_adjudication_complete_pending_coordinator_verification','created_utc':stamp,'independence':'Fresh model source reading; first-reader labels inaccessible to this session until independent hash/timestamp freeze. Diagnosis and anchors disclosed; no human clinical review or inter-rater reliability claim.','input_reference_sha256':sha((REPAIR/'reference.json').read_bytes()),'independent_freeze_receipt':'independent-freeze-receipt.json','evidence_file':'source-evidence.json','counts':{'unique_pairs':49,'trials':37,'metadata_sample':33,'challenge_anchor':18,'overlap_pairs':2},'source_files_first_reader':first['source_files'],'pairs':pairs,'endpoints_supported':['Auditable multicategory disease/cohort scope annotation on these 49 frozen pairs.','Separate descriptive analysis of 33 metadata-sampled pairs and 18 purposive challenge memberships with overlaps identified.','Evaluation of explicit mention, fusion-class matching, closed-list restrictions, conditional biomarkers and source uncertainty handling.','Snapshot-status and oncology-purpose-aware subset descriptions, without live availability claims.'],'endpoints_not_supported':['Patient eligibility, treatment recommendation, safety, efficacy, therapeutic window, prognosis or expected clinical benefit.','Current site/cohort slots or release of conditional safety holds.','Unqualified binary compatibility scoring collapsing extra biomarkers, missing protocols or ambiguous cohorts.','Global recall, all-trial precision, population prevalence, performance outside the judged sample, or pooled prevalence from challenge anchors.','A 149-pair current ordinary/molecular benchmark: that expansion is a distinct next task, and unreviewed pairs remain unjudged.','Human expert reference standard or inter-rater reliability.'],'next_distinct_task':'Source adjudication expansion to the 149 current ordinary/molecular pairs, preserving already-reviewed overlap; no absent case is an all-negative label. No rankings or fitted models produced.'})
 print('Adjudicated',len(pairs),'pairs;',sum(x['label_discrepancy'] for x in decisions),'label differences resolved with explicit uncertainty retained.')
