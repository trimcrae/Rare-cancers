#!/usr/bin/env python3
"""Read-only independent audit of the frozen R8 metabolism packet."""
from pathlib import Path
from collections import Counter
import json,hashlib,datetime,xml.etree.ElementTree as ET
P=Path(__file__).parent
Q=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round8/metabolism')
R=Path('/workspace/Rare-cancers/research/autonomy/fresh-discovery-2026-10-04/functional')
def load(p):return json.loads(p.read_text())
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
manifest=load(Q/'MANIFEST.json');mismatches=[]
for row in manifest['files']:
    actual=bind(Q/row['path'])
    if any(actual[k]!=row[k] for k in ['bytes','sha256']):mismatches.append(row['path'])
assert not mismatches
usz=load(R/'reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json')
ncc=load(R/'reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json')
expected=[{'cohort':'Bangerter40','label':r['literal_figure_drug']} for r in usz['rows']]
for t in ncc['tables']:expected.extend({'cohort':'Iwata_'+t['source']['file'],'label':r['drug']} for r in t['records'])
roster=load(Q/'COMPLETE-SCREEN-ROSTER.json');assert roster['rows']==expected
assert len(usz['rows'])==40 and [len(t['records']) for t in ncc['tables']]==[221,24]
measured=load(Q/'REUSED-MEASUREMENTS.json');checks=[]
for row in measured['NCC_conditions']:
    matched=[r for t in ncc['tables'] if t['source']['file']==row['source'] for r in t['records'] if r['source_row']==row['source_row'] and r['sheet']==row['sheet']]
    assert len(matched)==1
    for k in ['drug','cas','viability_percent','sd_percentage_points']:assert row[k]==matched[0][k],k
    checks.append({'drug':row['drug'],'source_row':row['source_row'],'all_exported_source_fields_exact':True})
for row in measured['USZ_condition']:
    matched=[r for r in usz['rows'] if r['literal_figure_drug']==row['drug']]
    assert len(matched)==1 and row['category']==matched[0]['ordinal_source_category']
    assert row['literal_legend_range']==usz['literal_legend_ranges'][row['category']]
assert len(checks)==7 and len(measured['USZ_condition'])==1
primaries=load(Q/'PRIMARY-ELIGIBILITY-EXCERPTS.json');primary_checks=[]
for row in primaries:
    source=Path(row['source_binding']['path']);assert bind(source)==row['source_binding']
    root=ET.fromstring(source.read_bytes());text=' '.join(' '.join(root.itertext()).split())
    excerpts=list(row['selected_eligibility_rows'])
    if row.get('complete_four_model_source_passage'):excerpts.append(row['complete_four_model_source_passage'])
    for excerpt in excerpts:assert ' '.join(excerpt.split()) in text,row['id']
    primary_checks.append({'id':row['id'],'source_hash_verified':True,'exact_primary_excerpts_checked':len(excerpts)})
context=load(Q/'RNA-SOURCE-CONTEXT.json');assert len(context['all13_Hofvander_EMC'])==13 and len(context['all6_GSE24369_EMC'])==6
for binding in context['source_bindings']:assert bind(Path(binding['path']))==binding
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'single_cell/microenvironment worker; independent read-only source/decision review',
        'input_bindings':[bind(Q/n) for n in ['MANIFEST.json','PLAN.json','RESULTS.txt','DECISION.json','COVERAGE.json','COMPLETE-SCREEN-ROSTER.json','REUSED-MEASUREMENTS.json','PRIMARY-ELIGIBILITY-EXCERPTS.json','RNA-SOURCE-CONTEXT.json']],
        'validation':{'manifest_files':len(manifest['files']),'hash_mismatches':mismatches,'complete_roster_counts':dict(Counter(r['cohort'] for r in expected)),
                      'focused_NCC_exact_source_checks':checks,'USZ_sorafenib_ordinal_exact':True,'primary_checks':primary_checks,'all13_plus6_RNA_identity_records_retained':True},
        'scientific_review':{'decision_endorsed':'Shelve standalone lipid-redox/ferroptosis paper; no useful new measured EMC mechanism established; public search not exhausted',
                             'strongest_alternative':'Sorafenib freebase/tosylate and USZ ordinal results are unmatched formulation/dose/exposure viability; kinase effects/general cytotoxicity remain. No lipid or rescue endpoint can be inferred.',
                             'positive_and_negative_conditions':'All40/221/24 literal conditions retained; seven NCC descriptive label-selected observations plus unfavorable USZ none retained. Literal canonical-alias absence is not complete target or chemical coverage.',
                             'assay_and_donor':'Two screened patient-derived models, not245NCC donors; technicalreplicates/selectiveIC50 endpoints cannotcreate independentvalidation. Six-day USZ dose context known, NCC screening dose/exposure remains unacquired.',
                             'other_sources':'Other-cancer GPX4/rescue evidence and UPS mouse toxicity are prior-art/alternative controls. CAM fluorescence, PPARG transcription, disputed cell models and bulk RNA do not authenticate native EMC lipid-redox dependence.',
                             'pending_vs_excluded':'CTRP full model/condition crosswalk, generic organoid/model/CIVO mapping and ascorbate/MRI histology/access remain unresolved; acquired main-source exclusions do not close all underlying broader screens.',
                             'limitations':'Focused extracts are source-exact; this review did not newly retrieve every linked underlying experiment or cure source access/identity gaps. No complete biological negative, dependency, efficacy, prognosis, safety or target ranking endorsed.'},
        'ownership':'Only owned microenvironment peer review written. Metabolism originals unchanged; no duplicate retrieval, restricted-topic source reading or shared-state mutation.'}
(P/'METABOLISM-INDEPENDENT-REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['validation'],indent=2))
