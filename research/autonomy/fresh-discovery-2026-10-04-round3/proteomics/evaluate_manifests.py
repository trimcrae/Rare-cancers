"""Read retained source annotations. Never use protein expression to relabel disease."""
from pathlib import Path
import csv, io, json, hashlib, collections, re, xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
def sha(name): return hashlib.sha256((P/name).read_bytes()).hexdigest()
def save(name,value): (P/name).write_text(json.dumps(value,indent=2),encoding='utf8')
def counts(rows,key): return dict(collections.Counter(r.get(key,'') for r in rows))
def named_emc(text):
    return bool(re.search(r'extraskeletal\s+myxoid\s+chondrosarcoma|\bEMCS?\b|NR4A[23].*(?:EWSR1|TAF15|TCF12|FUS)|(?:EWSR1|TAF15|TCF12|FUS).*NR4A[23]',text,re.I))
rows=[r for r in csv.DictReader(io.StringIO((P/'panatlas-sample_info.txt').read_text(encoding='utf-8-sig')),delimiter='\t') if r['Sample']]
rows=[{k:v for k,v in r.items() if k} for r in rows]
labels=list(csv.DictReader(io.StringIO((P/'panatlas-sample_labels.txt').read_text(encoding='utf-8-sig')),delimiter='\t'))
sar=[r for r in rows if r['Group']=='Sarcoma']
generic=[r for r in sar if r['Subtype'].lower() in ['malignant fibrous histiocytoma','pleomorphic sarcoma','spindle cell sarcoma','high grade spindle cell sarcoma']]
# Preserve exact source labels rather than rely on this convenience classification.
save('panatlas-all53-sarcoma-rows.json',sar)
out={'source_sha256':sha('panatlas-sample_info.txt'),'label_source_sha256':sha('panatlas-sample_labels.txt'),'total_records':len(rows),'unique_sample_ids':len({r['Sample'] for r in rows}),'sample_type_counts':counts(rows,'Sample Type'),'selection_counts':counts(rows,'Primary Selection'),'selected_by_sample_type':counts([r for r in rows if r['Primary Selection']=='TRUE'],'Sample Type'),'label_file_rows':len(labels),'sarcoma_records':len(sar),'sarcoma_subtype_counts':counts(sar,'Subtype'),'sarcoma_sample_types':counts(sar,'Sample Type'),'sarcoma_selected':counts(sar,'Primary Selection'),'all_record_named_emc_or_diagnostic_fusion_hits':[r for r in rows if named_emc(' '.join(str(v) for v in r.values()))],'generic_sarcoma_rows':generic,'interpretation':'No explicitly authenticated EMC in supplied annotations. Generic sarcoma records unresolved; absent fusion columns and no recovered pathology crosswalk prevent exclusion as hidden EMC. No protein values evaluated.'}
hits=out['all_record_named_emc_or_diagnostic_fusion_hits']
out['keyword_hit_disposition']={'count':len(hits),'subtype_counts':counts(hits,'Subtype'),'all_EMC_Cohort_and_colorectal':all('EMC Cohort' in r['Miscellaneous'] and r['Subtype']=='Colorectal carcinoma' for r in hits),'conclusion':'124 literalEMC keyword hits occur in colorectal carcinoma cohort annotations. They are not an EMC disease diagnosis or diagnosticfusion; all original rows preserved.'}
out['additional_alias_hits']=[r for r in rows if re.search(r'myxoid|chondrosarcoma|extraskeletal|extra.skeletal|\bEMCS\b|\bTEC\b|\bCHN\b|NR4A[23]',' '.join(str(v) for v in r.values()),re.I)]
assert len(hits)==124 and out['keyword_hit_disposition']['all_EMC_Cohort_and_colorectal']
save('panatlas-eligibility-evaluation.json',out)

allrows=list(csv.DictReader(io.StringIO((P/'cptac-all-metadata.csv').read_text(encoding='utf-8-sig'))))
cpt=[r for r in allrows if r['Tumor']=='SAR']
cases={}
for r in cpt: cases.setdefault(r['Case_ID'],[]).append(r)
caseout=[{'case_id':k,'slide_rows':len(v),'specimen_ids':sorted({r['Specimen_ID'] for r in v}),'histologies':sorted({r['Tumor_Histological_Type'] for r in v}),'proteomics_status':sorted({r['Proteomics_Available'] for r in v}),'pdc_links':sorted({r['PDC_Link'] for r in v})} for k,v in cases.items()]
save('cptac-sar-case-evaluation.json',caseout)
cptout={'source_sha256':sha('cptac-all-metadata.csv'),'slide_rows':len(cpt),'unique_cases':len(cases),'histology_slide_counts':counts(cpt,'Tumor_Histological_Type'),'proteomics_status_counts':counts(cpt,'Proteomics_Available'),'nonempty_PDC_links':[r['PDC_Link'] for r in cpt if r['PDC_Link']],'cases_with_conflicting_histology':[r for r in caseout if len(r['histologies'])>1],'named_emc_or_fusion_hits':[r for r in cpt if named_emc(' '.join(str(v) for v in r.values()))],'extraskeletal_other_histology_rows':[r for r in cpt if 'extraskeletal' in r['Tumor_Histological_Type'].lower()],'interpretation':'All retained slide records evaluated and collapsed to case IDs. No EMC-labelled case and no downloadable PDC protein link. Generic histology is unresolved, not evidence that hidden EMC is impossible. Portal summary300slides differs from CSV305; use the actual305records, no silent exclusion.'}
save('cptac-eligibility-evaluation.json',cptout)

root=E.parse(P/'procan-sharedStrings.xml').getroot()
strings=[''.join(el.itertext()) for el in root]
hist=[s for s in strings if re.search('sarcoma|chondro|myxoid|mesench|NR4A',s,re.I)]
save('procan-label-vocabulary-evaluation.json',{'source_sha256':sha('procan-sharedStrings.xml'),'source_workbook':'PXD056810/cohort_1_processed_matrix.xlsx','shared_string_count':len(strings),'shared_string_declared_count':root.attrib,'relevant_vocabulary':hist,'explicit_EMC_or_fusion_labels':[s for s in strings if named_emc(s)],'limitation':'Complete shared-string dictionary evaluated, not every1260sample-row metadata mapping. Inline strings or unspecific labels cannot be excluded by this alone. Public processed workbook row crosswalk remains accessible/pending; no biological inference or manuscript advancement.'})

if (P/'procan-all1260-sample-metadata.json').exists():
    meta=json.loads((P/'procan-all1260-sample-metadata.json').read_text())
    sarcoma=[r for r in meta if 'sarcoma' in (r['cancer_type']+' '+r['cancer_subtype']).lower()]
    assert len(meta)==1260 and len({r['sample_id'] for r in meta})==1260
    pro={'annotation_sha256':sha('procan-all1260-sample-metadata.json'),'extraction_receipt_sha256':sha('procan-all1260-extraction-receipt.json'),'records':len(meta),'unique_sample_ids':len({r['sample_id'] for r in meta}),'cancer_type_counts':counts(meta,'cancer_type'),'tissue_type_counts':counts(meta,'tissue_type'),'cancer_subtype_counts':counts(meta,'cancer_subtype'),'sarcoma_rows':sarcoma,'sarcoma_subtype_counts':counts(sarcoma,'cancer_subtype'),'sarcoma_tissue_counts':counts(sarcoma,'tissue_type'),'named_emc_or_diagnostic_fusion_hits':[r for r in meta if named_emc(' '.join(str(v) for v in r.values()))],'missing_annotations':[r for r in meta if any(not r[k] for k in ['sample_id','cancer_type','tissue_type','cancer_subtype'])],'interpretation':'All1260publicCohort1 sample annotation rows evaluated including inline/shared strings. No explicitEMC ordiagnosticfusion annotation. This supersedes the prior individual-row pendingstatus; it doesnotresolve privateISKScohort11 or prevent hidden/misdiagnosedtumors. No proteinvalues analyzed.'}
    save('procan-all1260-eligibility-evaluation.json',pro)
    save('procan-label-vocabulary-evaluation.json',{'source_sha256':sha('procan-sharedStrings.xml'),'shared_string_count':len(strings),'relevant_vocabulary':hist,'explicit_EMC_or_fusion_labels':[s for s in strings if named_emc(s)],'limitation':'Vocabulary alone was insufficient; all1260individualannotation rows subsequently evaluated in procan-all1260-eligibility-evaluation.json. This file is no longer a pending-only determination.'})

print(json.dumps({'PanAtlas':{k:out[k] for k in ['total_records','unique_sample_ids','sarcoma_records','sarcoma_subtype_counts','selected_by_sample_type']},'CPTAC':{k:cptout[k] for k in ['slide_rows','unique_cases','cases_with_conflicting_histology','proteomics_status_counts']},'ProCan_relevant_vocabulary':hist},indent=2))
