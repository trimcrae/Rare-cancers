"""Offline assembly and validation of saved single-reader judgments and exact sources.

Run with Python -X utf8 from repository root. --check compares regenerated outputs.
No rankings or automated clinical labels are calculated.
"""
import gzip, hashlib, json, sys
from collections import Counter
from pathlib import Path
from author_labels import J
from freeze import selection

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(obj,pointer):
    for part in pointer.split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        obj=obj[int(part)] if isinstance(obj,list) else obj[part]
    return obj
def serialize(x): return json.dumps(x,indent=2,ensure_ascii=False)+'\n'
def emit(name,x):
    target=OUT/name
    if '--check' in sys.argv:
        assert target.read_text(encoding='utf-8')==serialize(x),name+' not reproducible'
    else: target.write_text(serialize(x),encoding='utf-8')

# These cohort judgments disaggregate rather than overwrite the frozen label taxonomy.
C={
 'NCT05918640': {
  'EMC':[('Phase 1 escalation/exploratory','fusion_class_compatible','EWSR1/TAF15 EMC variants can satisfy FET class; slot unknown.'),('Phase 2','explicit_exclusion','Ewing sarcoma required.')],
  'DSRCT':[('Phase 1','fusion_class_compatible_conditional_hold','FET defining fusion matches, but enrollment hold release unknown.'),('Phase 2','explicit_exclusion','Ewing sarcoma required.')],
  'SS':[('Phase 1','insufficient_evidence','SS18::SSX does not supply required FET fusion; extra alteration unestablished.'),('Phase 2','explicit_exclusion','Ewing sarcoma required.')]},
 'NCT04901702':{'DSRCT':[('Phase I A/B and A1/B1','broad_tumor_compatible','Non-CNS solid tumors; non-Ewing expansion.'),('Phase I A2','extra_biomarker_uncertain','HR/DSB alteration required.'),('Phase II','explicit_exclusion','Ewing histology required.')]},
 'NCT06571734':{d:[('Cohort 1 leiomyosarcoma','explicit_exclusion','Restricted histology.'),('Cohort 2 bone sarcoma','explicit_exclusion','Soft tissue diagnosis is not bone-sarcoma histology, including when metastasized to bone.'),('Cohort 3 TAS','explicit_diagnosis_compatible' if d=='SS' else 'fusion_class_compatible','TAS pathology acceptance and >2 prior lines required.')] for d in ['EMC','DSRCT','SS']},
 'NCT05071209':{
  'EMC':[('Part A / B1 EWS','fusion_class_compatible','EWSR1-containing variant only; age/phase restrictions.'),('Part A / B3 DDR','extra_biomarker_uncertain','Separate inactivating DDR alteration required.'),('B2 ARMS','explicit_exclusion','PAX3-FOXO1 alveolar rhabdomyosarcoma required.')],
  'DSRCT':[('Part A / B1 EWS','defining_fusion_compatible','EWS-WT1 explicitly named.'),('Part A / B3 DDR','extra_biomarker_uncertain','Separate inactivating DDR alteration required.'),('B2 ARMS','explicit_exclusion','PAX3-FOXO1 alveolar rhabdomyosarcoma required.')],
  'SS':[('Part A / B1 EWS','insufficient_evidence','SS18::SSX not EWS; any additional EWS fusion unestablished.'),('Part A / B3 DDR','extra_biomarker_uncertain','Broad non-CNS scope conditional on qualifying DDR alteration.'),('B2 ARMS','explicit_exclusion','PAX3-FOXO1 ARMS required.')]},
 'NCT06761651':{'SS':[('Part 1','broad_tumor_compatible','No mandatory tumor biomarker in dose escalation.'),('Part 2','insufficient_evidence','Selected carcinoma cohorts or other best-responding tumor types; SS expansion not established.')]},
 'NCT07030959':{'DSRCT':[('Parts A/B/C','extra_biomarker_uncertain','KRAS variant and part-specific criteria omitted; broad umbrella scope only.')]},
 'NCT05687136':{d:[('Dose escalation','extra_biomarker_uncertain','Listed alteration evidence and PI approval required.'),('Dose expansion','extra_biomarker_uncertain','Same alteration gate plus measurable disease/paired biopsy.')] for d in ['EMC','DSRCT','SS']},
 'NCT06094101':{d:[('Screening stage 1','explicit_diagnosis_compatible' if d=='SS' else 'explicit_exclusion','Closed rhabdomyosarcoma/Ewing/SS list.'),('Screening stage 2','manufacturing_and_remission_uncertain' if d=='SS' else 'explicit_exclusion','Successful vaccine manufacture and CR/stable PRplus, after stage 1.')] for d in ['EMC','DSRCT','SS']},
 'NCT05135975':{d:[('Stratum A','explicit_diagnosis_compatible_provisional' if d=='DSRCT' else 'broad_tumor_compatible_provisional','BR2 or later; full additional exclusions unavailable.'),('Strata B/C/D','explicit_exclusion','Metastatic Ewing/osteosarcoma/fusion-positive rhabdomyosarcoma respectively.')] for d in ['EMC','DSRCT','SS']}
}

packet=read(OUT/'review-packet.json')
assert read(OUT/'reader-judgments.json')==J, 'Reader JSON must be regenerated from authored judgments'
sel=read(OUT/'selection.json'); regen=selection()
assert {k:v for k,v in sel.items() if k!='frozen_at_utc'}==regen
receipt=read(OUT/'freeze-receipt.json')
for name,h in receipt['sha256'].items(): assert sha(OUT/name)==h, 'Frozen input changed: '+name
expected={}
for s in sel['strata']:
    for n in s['selected_ids']: expected.setdefault((s['diagnosis'],n),[]).append(dict(set='metadata_sample',stratum=s['stratum'],frame_n=s['frame_n'],sample_n=len(s['selected_ids']),inclusion_fraction=f"{len(s['selected_ids'])}/{s['frame_n']}"))
for a in sel['challenge_anchors']:
    for d in a['diagnoses']: expected.setdefault((d,a['nct_id']),[]).append(dict(set='challenge_anchor',stratum='purposive'))
assert len({(j['diagnosis'],j['nct_id']) for j in J})==len(J), 'Duplicate reader judgment'
assert set(expected)=={(j['diagnosis'],j['nct_id']) for j in J}, 'Missing/extra judgment'
source_cache={}; source_records={}; source_manifests={}; excerpts=0
def evidence(x,subpointer,excerpt=None):
    source=x['source']; p=ROOT/source
    if source not in source_cache:
        assert sha(p)==x['source_sha256'],source
        uncompressed=gzip.decompress(p.read_bytes())
        source_cache[source]=json.loads(uncompressed)
        manifest=read(p.parent/'manifest.json')
        page=next(a for a in manifest['pages'] if Path(a['file']).name==p.name)
        assert page['stored_sha256']==sha(p)
        assert page['sha256']==hashlib.sha256(uncompressed).hexdigest()
        source_records[source]=dict(stored_sha256=sha(p),decoded_sha256=page['sha256'],retrieved_at_utc=page['retrieved_at_utc'],url=page['url'])
        source_manifests[str((p.parent/'manifest.json').relative_to(ROOT)).replace('\\','/')]=sha(p.parent/'manifest.json')
    ptr=x['pointer']+'/protocolSection/'+subpointer
    value=resolve(source_cache[source],ptr)
    e=dict(source=source,pointer=ptr,source_sha256=x['source_sha256'])
    if excerpt is not None:
        assert isinstance(value,str) and excerpt in value,(ptr,excerpt)
        start=value.index(excerpt)
        e.update(excerpt=excerpt,char_start=start,char_end=start+len(excerpt))
    return e

SUPPORT={
 'NCT05918640':['Phase 2: Histologically confirmed diagnosis of recurrent or relapsed Ewing sarcoma','Patients with Desmoplastic small round cell tumor (DSRCT) will be excluded from enrollment until at least 3 non-DSRCT patients have been enrolled without dose limiting toxicity.'],
 'NCT04901702':['Patients with refractory or recurrent Ewing sarcoma','deleterious alteration in germline or somatic genes involved in HR repair and DSBs signaling'],
 'NCT05687136':['SWI/SNF member mutation (ARID1A, PBRM1, SMARCA4, ARID2, ARID1b, SMARCB1, SMARCA2, SS18)','All mutations/alterations must be approved by the overall principal investigator (PI).'],
 'NCT05135975':['SEE PROTOCOL FOR ADDITIONAL EXCLUSION CRITERIA','Any other soft tissue sarcoma, BR2 or later'],
 'NCT06571734':['Patients must have undergone greater than 2 lines of antineoplastic treatment','Tumors invading the GI tract from external viscera'],
 'NCT06094101':['Design and production of the patient-individual vaccine cocktail was successful','Whole exome sequencing and RNA sequencing data of the gene fusion'],
 'NCT07030959':['Details are defined for each part'],
 'NCT07698899':['Patients must have recurrent or refractory disease with CNS parenchymal and/or leptomeningeal disease'],
 'NCT06761651':['Phase 2: A new cohort of subjects with advanced or metastatic solid tumors'],
 'NCT06456359':['High SSTR2/3/5 mRNA expression'],
 'NCT07695311':['Participants must have demonstrated HLA'],
 'NCT06526897':['or other grade 2 or grade 3 sarcomas not further classified'],
 'NCT05071209':['B3, DDR Non-statistical Cohort','detection of a variant on circulating tumor DNA/RNA is not sufficient to qualify']
}
DOMAIN={'NCT07037433':'non_oncology_cardiovascular','NCT07202884':'non_oncology_urinary_incontinence','NCT03967834':'oncology_characterization','NCT06235125':'oncology_surgical_imaging','NCT06526897':'oncology_surveillance','NCT07271914':'oncology_surgical_staging','NCT07575724':'oncology_surgical_management'}
rows=[]
for j in sorted(J,key=lambda j:(j['diagnosis'],j['nct_id'])):
    n=j['nct_id']; d=j['diagnosis']; x=packet[n]; ps=x['record']['protocolSection']
    e=evidence(x,'eligibilityModule/eligibilityCriteria',j['decisive_excerpt']); excerpts+=1
    assert resolve(source_cache[x['source']],x['pointer'])==x['record'], 'Review packet differs from saved raw record: '+n
    eall=[e]
    for excerpt in SUPPORT.get(n,[]):
        eall.append(evidence(x,'eligibilityModule/eligibilityCriteria',excerpt)); excerpts+=1
    for z in j['extra_evidence']:
        eall.append(evidence(x,z['module']+'/'+z['field'],z['excerpt'])); excerpts+=1
    reviewed=[]
    for m in ['eligibilityModule','descriptionModule','conditionsModule','armsInterventionsModule','designModule','statusModule']:
        if m in ps: reviewed.append(evidence(x,m))
    criteria=ps['eligibilityModule']['eligibilityCriteria']
    # The registry snapshot is the reference scope, not a reverified clinical protocol.
    incomplete=n=='NCT05135975'
    conditional=j['exclusion_mode']=='conditional_enrollment_hold'
    cohorts=[dict(cohort=a,judgment=b,rationale=c,evidence_pointer=e['pointer']) for a,b,c in C.get(n,{}).get(d,[(j['cohort'],j['label'],j['rationale'])])]
    # Per-cohort pointer always includes full eligibility; narrative disambiguation remains above.
    row={k:v for k,v in j.items() if k not in ['extra_evidence','decisive_excerpt']}
    row.update(pair_id=d+':'+n,sets=expected[(d,n)],title=ps['identificationModule']['briefTitle'],registry_url='https://clinicaltrials.gov/study/'+n,
        oncology_task_domain=DOMAIN.get(n,'oncology_treatment'),registry_primary_purpose=ps['designModule'].get('designInfo',{}).get('primaryPurpose'),
        phase=ps['designModule'].get('phases',[]),phase_evidence=evidence(x,'designModule/phases') if 'phases' in ps['designModule'] else None,
        overall_status=ps['statusModule']['overallStatus'],status_verified_date=ps['statusModule'].get('statusVerifiedDate'),status_evidence=evidence(x,'statusModule/overallStatus'),
        snapshot_current=ps['statusModule']['overallStatus'] in ['RECRUITING','NOT_YET_RECRUITING','ENROLLING_BY_INVITATION'],
        recruitment_uncertainty='Saved overall status only; site/cohort slots and release of safety gates not independently verified. Status verification month retained; no live recruitment assertion.',
        cohorts=cohorts,evidence=eall,reviewed_modules=reviewed,full_saved_eligibility_characters=len(criteria),
        complete_saved_criteria_read=True,external_protocol_reviewed=False,known_missing_additional_exclusions=incomplete,
        binary_benchmark_use='unresolved_do_not_score_as_negative' if row['label']=='insufficient_evidence' or conditional or incomplete else 'scope_specific_endpoint_required',
        clinical_eligibility_established=False)
    if n=='NCT05687136':
        row['protocol_uncertainty']+=' Wording uses a list ending in "and"; exact disjunctive/conjunctive interpretation of biomarker list should be confirmed, not assumed from a gene match.'
    rows.append(row)

reference=dict(schema='emc-diagnosis-cohort-reference/1',state='single_reader_labels_frozen_pending_independent_verification',
    label_protocol_sha256=sha(OUT/'label-protocol.json'),selection_sha256=sha(OUT/'selection.json'),reader_judgments_sha256=sha(OUT/'reader-judgments.json'),
    reference_scope='Saved CT.gov registry text, 33 metadata-sampled current pairs plus 18 purposive anchor pairs; two pairs overlap. No patient eligibility, global recall, or unjudged negatives.',
    blinding='Independent of prior worker label files; disclosed anchor and molecular-scope prompt knowledge. Single model-assisted reader; no inter-rater claim.',
    source_files=source_records,source_manifest_hashes=source_manifests,pairs=rows)
emit('reference.json',reference)
counts=[]
for s in sel['strata']:
    rr=[r for r in rows if r['diagnosis']==s['diagnosis'] and any(z['set']=='metadata_sample' and z['stratum']==s['stratum'] for z in r['sets'])]
    counts.append(dict(diagnosis=s['diagnosis'],stratum=s['stratum'],frame_n=s['frame_n'],sample_n=len(rr),label_counts=dict(sorted(Counter(r['label'] for r in rr).items()))))
validation=dict(selection_reproduced=True,frozen_hashes_verified=len(receipt['sha256']),unique_trials=len(packet),unique_pairs=len(rows),metadata_pairs=sum(len(s['selected_ids']) for s in sel['strata']),challenge_pairs=sum(len(a['diagnoses']) for a in sel['challenge_anchors']),
    overlapping_pairs=[r['pair_id'] for r in rows if len(r['sets'])>1],
    exact_excerpts_verified=excerpts,source_gzip_and_decoded_hashes_verified=len(source_records),all_selected_pairs_accounted_for=True,
    strata=counts,challenge_label_counts=dict(sorted(Counter(r['label'] for r in rows if any(z['set']=='challenge_anchor' for z in r['sets'])).items())),
    unresolved_pairs=[r['pair_id'] for r in rows if r['binary_benchmark_use']=='unresolved_do_not_score_as_negative'],
    independent_scientific_verification='not performed by this single reader; coordinator required',rankings_run=False,normal_preflight='coordinator after integration, not run by worker')
emit('validation.json',validation)
print(serialize(validation))
