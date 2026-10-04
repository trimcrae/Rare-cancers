"""Freeze source-level scientific dispositions and exact observation counts.

This is eligibility analysis, not an analysis of malignant-cell programs.
Retained original responses are cache-only; derived relevant observations and
source receipts are durable. Uses existing openpyxl and pdftotext only.
"""
import collections, datetime, hashlib, io, json, pathlib, re, xml.etree.ElementTree as ET, zipfile
from sample_metadata import FIELDS
ROOT=pathlib.Path(__file__).resolve().parent
def write(name,obj): (ROOT/name).write_text(json.dumps(obj,indent=2)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def docx(name):
 z=zipfile.ZipFile(io.BytesIO((ROOT/'sources'/name).read_bytes()))
 o=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 return [[''.join(c.itertext()) for c in r.findall('w:tc',ns)] for r in o.findall('.//w:tr',ns)]

if __name__=='__main__':
 first=json.loads((ROOT/'GSM-ELIGIBILITY-OBSERVATIONS.json').read_text())
 more=json.loads((ROOT/'ADDITIONAL-GSM-ELIGIBILITY-OBSERVATIONS.json').read_text())
 retry=json.loads((ROOT/'FOCUSED-FOLLOWUP-RECEIPTS.json').read_text())[0]
 text=(ROOT/retry['path']).read_text(); row={'accession':'GSM9511154','source_sha256':retry['sha256'],'source_status':retry['status']}
 for f in FIELDS:row[f]=re.findall(r'^!Sample_'+f+r' = (.*)',text,re.M)
 write('GSM9511154-RETRY-OBSERVATION.json',row)
 # The earlier transient failure remains immutable in its original observation.
 libraries={**first['libraries'],**more['libraries'],'GSM9511154':row}
 by_series={**first['by_series'],**more['by_series']}
 assay=[]
 for s in by_series['GSE318841']:
  t=(ROOT/'sources'/(s+'.json')).read_text()
  files=re.findall(r'^!Sample_supplementary_file[^ ]* = (.*)',t,re.M)
  assay.append({'accession':s,'source_sha256':libraries[s]['source_sha256'],'files':files,'reported_units':libraries[s]['data_processing'][-1],'RSEM_gene_vector':len(files)==1 and 'RSEM.genes.counts.gz' in files[0]})
 assert all(r['RSEM_gene_vector'] for r in assay) and len(assay)==277
 write('PEDIATRIC-SIBLING-ASSAY-OBSERVATIONS.json',assay)
 for s in ['GSM9511127','GSM9511129']:
  assert libraries[s]['title'] and libraries[s]['characteristics_ch1']
 write('ANNOTATION-CONFLICTS.json',{'interpretation':'Do not silently repair title/disease discordance or derive donor/subtype concordance from prefixes. Neither conflicting label authenticates EMC.','rows':[libraries[s] for s in ['GSM9511127','GSM9511129']]})
 primary_types=['ALL','ATC','BCC','BLCA','BRCA','CESC','ccRCC','CRC','cSCC','DSRCT','GCTB','GBM','HNSCC','HCC','ICC','LUAD','LUSC','MPNST','MB','MCC','MESO','MPAL','NB','OS','OV','PAAD','PNET','PTC','PRAD','RMS','SACC','SKCM','STAD','SyS','TGCT','WT']
 assert len(primary_types)==36
 write('SCTUMOR-ROSTER-OBSERVATIONS.json',{'primary_type_abbreviations':primary_types,'source_pdf_sha256':sha(ROOT/'sources/sctumor_media1.pdf'),'extract_sha256':sha(ROOT/'SCTUMOR-TABLE1-EXTRACT.txt'),'all_types_inspected':True,'EMC_or_unspecified_sarcoma_type':False,'new_GEO_sample':'GSM9515643: Retroperitoneal leiomyosarcoma','version_uncertainty':'GEO says135441 cells/494 samples; retrieved version2 preprint says135424 cells/499 samples. Do not merge totals or infer499 independent donors.','source_repositories':'The evaluated full primary roster uses named diseases and source/sample ranges. It does not close every cell-line observation in PRJCA021248/GSE157220.'})
 col=json.loads((ROOT/'sources/cellxgene_collections.json').read_text())
 relevant=[x for x in col if re.search(r'sarcoma|chondrosarcoma|extraskeletal|NR4A3',json.dumps(x),re.I)]
 write('CELLXGENE-ELIGIBILITY-OBSERVATIONS.json',{'collections_screened':len(col),'screen_regex':'sarcoma|chondrosarcoma|extraskeletal|NR4A3','limitations':'Metadata search does not authenticate or exclude all generic tumor donors. It is not a cell-level biological evaluation.','matching_collections':[{'collection_id':x['collection_id'],'name':x['name'],'description':x['description'],'doi':x['doi'],'datasets':[{'dataset_id':d['dataset_id'],'assay':d['assay'],'disease':d['disease'],'suspension_type':d['suspension_type']} for d in x['datasets']]} for x in relevant]})
 write('BO112-PUBLISHED-ROSTER-OBSERVATIONS.json',{'table2_sha256':sha(ROOT/'sources/bo112_table2.json'),'table2_rows':docx('bo112_table2.json'),'table10_sha256':sha(ROOT/'sources/bo112_table10.json'),'table10_patient_ids':['001','002','003','004','007','009','010','011','012','013','014','015','016','017'],'table10_histology_crosswalk':False,'interpretation':'The14-patient aggregate histology table and individual-outcome table do not identify Patient012 or RT-only comparator histologies. UPS/spindle category is retained as source classified and cannot authenticate NR4A3 status.'})
 pending=['GSM9376750','GSM9376751','GSM9376752','GSM9376753','GSM9376754','GSM9376755']
 write('BO112-COVERAGE-BY-CONDITION.json',{'rows':[{'accession':s,**libraries[s],'status':('pending accessible analysis' if s in pending else 'demonstrably unsuitable measurement'),'reason':('Processed single-cell measurements exist; individual EMC eligibility is unresolved, not an EMC biological negative.' if s in pending else 'Source labels or explicit overlapping patient code identify MFS/LPS/UPS, not EMC.'),'mapping_basis':('GSE279852 shared BO112004:MFS;010/011:UPS; source-version/cohort crosswalk still required before pooling' if s.startswith('GSM937') else 'Direct sample-level tissue field')} for a in ['GSE313859','GSE313858','GSE279852'] for s in by_series[a]],'unresolved_libraries':pending,'unresolved_donors':['Patient012','Radiation-only001','Radiation-only002','Radiation-only003'],'overlap':'004/010/011 are reused across313859 and279852; spatial313858T1-T4 belongs to004. RT001CD45neg/pos are two technical sorts of one donor.','not_independent_validation':True})
 coverage=[
  {'source':'GSE213065/GSE212527/GSE212526;Subramanian2024','status':'verified evaluation reused','finding':'Prior R3 checked87/7/4metadata records and22supplement sheets; no authenticated EMC. Gene NR4A3 in a table is not identity.','location':'research/autonomy/fresh-discovery-2026-10-04-round3/immune/RESULTS.md;COVERAGE.md'},
  {'source':'Ngo2025 DOI10.1002/cac2.70077','status':'verified evaluation reused','finding':'All single-cell/spatial specimens are epithelioid sarcoma; EMC appears only in external bulk panel.','location':'research/autonomy/fresh-discovery-2026-10-04-round2/regulatory/RESULTS.txt;protein-spatial-eligibility.json'},
  {'source':'scTumor2026 DOI10.64898/2026.02.14.705396v2;GSE319327','status':'demonstrably unsuitable measurement','finding':'Full36primarytype roster inspected; no EMC or generic sarcoma type. One new deposited sample is LMS. Cell-line table provenance remains a separate incomplete check.','location':'SCTUMOR-ROSTER-OBSERVATIONS.json;SCTUMOR-TABLE1-EXTRACT.txt'},
  {'source':'GSE319124','status':'demonstrably unsuitable measurement','finding':'All59libraries examined, with one successful transient retry. Labels RMS23/EWS9/OST6/NBL21; two title/disease conflicts retained. No authenticated EMC library. The study headline352sc/sn experiments is not closed by this subseries.','location':'GSM-ELIGIBILITY-OBSERVATIONS.json;GSM9511154-RETRY-OBSERVATION.json;ANNOTATION-CONFLICTS.json'},
  {'source':'GSE318841','status':'demonstrably unsuitable measurement','finding':'All277libraries examined. Six reported cell types: RMS150/NBL53/EWS31/OST17/WT14/RBL12. Every released measurement is a library-level RSEM gene vector; no cell-specific observation in this sibling.','location':'ADDITIONAL-GSM-ELIGIBILITY-OBSERVATIONS.json;PEDIATRIC-SIBLING-ASSAY-OBSERVATIONS.json'},
  {'source':'GSE330883','status':'demonstrably unsuitable measurement','finding':'Series explicitly methylation profiling by genome tiling array,220libraries. Not a single-cell/spatial transcriptomic measurement; no expression values inspected.','location':'sources/GSE330883.json;SCTUMOR-PEDIATRIC-FOLLOWUP-RECEIPTS.json'},
  {'source':'GSE200529','status':'demonstrably unsuitable measurement','finding':'All26libraries inspected: OS/ES/DSRCT; both MDA-SA98 entries explicitly OS. Warm/cold/nuclei and replicate conditions retained; no authenticated EMC. Later linkedPMIDs do not change the current roster.','location':'GSM-ELIGIBILITY-OBSERVATIONS.json'},
  {'source':'GSE184118;2024primaryand2026reanalyses','status':'demonstrably unsuitable measurement','finding':'All11libraries inspected: conventional central/peripheral CS,dedifferentiatedCS,enchondroma,chondroblasticOS,fetal femur. Reanalyses reuse this cohort, not newEMC donors.','location':'GSM-ELIGIBILITY-OBSERVATIONS.json;CANDIDATE-RECEIPTS.json'},
  {'source':'GSE243381;archival2024 DOI10.1158/1078-0432.CCR-23-2976','status':'demonstrably unsuitable measurement','finding':'All21current libraries inspected across RNA,TCR,lpWGS. Primary describes5UPS/3INS specimens;6source patientIDs include pairedX/Y. NoEMC. Libraries/paired specimens are not independent donors.','location':'GSM-ELIGIBILITY-OBSERVATIONS.json;CANDIDATE-RECEIPTS.json'},
  {'source':'GSE336655','status':'demonstrably unsuitable measurement','finding':'All3libraries are immune cells from JJ012-derived CS xenografts, not malignant authenticEMC.','location':'GSM-ELIGIBILITY-OBSERVATIONS.json'},
  {'source':'2025PTC DOI10.1016/j.xcrm.2025.101990;PRJCA024849','status':'demonstrably unsuitable measurement','finding':'Primary limits scRNA experiments toSS andRMS; broader cultured histologies do not imply EMC scRNA data.','location':'PRIMARY-ELIGIBILITY-EXTRACTS.json'},
  {'source':'2025TLS DOI10.1038/s41419-025-08376-4','status':'demonstrably unsuitable measurement','finding':'Its STS measurements are bulknCounter/IHC; single-cell externalOMIX009480 is HNSCC and spatialGSE289272 is NPC. GSE213065 reuse adds noEMC cells.','location':'PRIMARY-ELIGIBILITY-EXTRACTS.json'},
  {'source':'GSE279852/GSE313858/GSE313859;BO1122026','status':'pending accessible analysis','finding':'All26libraryconditions examined.20source-mappedconditions are MFS/LPS/UPS;6libraries/4donors remain unresolved eligibility despite accessible processed measurements. Three donor codes overlap sources; spatial4timepoints one donor.','location':'BO112-COVERAGE-BY-CONDITION.json;BO112-PUBLISHED-ROSTER-OBSERVATIONS.json'},
  {'source':'Remaining pediatric352sc/snexperiment crosswalk;scTumor cell-line sourcesPRJCA021248/GSE157220;new pediatric89samplepreprint DOI10.21203/rs.3.rs-10374394/v1','status':'pending accessible analysis','finding':'Complete sc/sn source/donor crosswalk or model authentication not completed within pilot. Do not infer their exclusion from the inspected named subseries or other tumors.','location':'SEARCH-RECEIPTS.json;FOLLOWUP-SEARCH-RECEIPTS.json;PEDIATRIC-FAMILY-RECEIPTS.json'},
 ]
 write('COVERAGE.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'claim':'Reproducible malignant differentiation/proliferative heterogeneity in authenticated EMC cells/spots','sources':coverage,'search_limits':'Dated bounded search, not universal exhaustion. Initial broad full-text query pages stopped at1000, with unreturned hits preserved as incomplete; tighter title/abstract searches complete within returned counts. Repository metadata/ontology coverage does not exclude generic or misclassified tumors.','eligible_authenticated_EMC_biological_observations':0,'actual_library_metadata_evaluated':len(libraries),'promotion_blocked':True,'biological_negative_established':False})
 extracts={}
 for filename,pattern in [('tumor_clusters_2025_PMC11970405.json',r'Next, we conducted single.cell RNA'),('tls_singlecell_2025_PMC12748978.json',r'For single.cell data analyses|For GeoMx data analyses|All data generated'),('archival_singlecell_2024_PMC11443197.json',r'75,716|two sarcoma subtypes')]:
  root=ET.fromstring((ROOT/'sources'/filename).read_bytes());extracts[filename]={'sha256':sha(ROOT/'sources'/filename),'paragraphs':[' '.join(e.itertext()) for e in root.iter('p') if re.search(pattern,' '.join(e.itertext()),re.I)]}
 write('PRIMARY-ELIGIBILITY-EXTRACTS.json',extracts)
 write('DECISION.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision':'shelve the standalone paper','validity':'No authenticated EMC cell-level measurements were recovered in evaluated sources. No malignant-cell state result, positive or negative, was computed.','value':'Eligibility exclusions, annotation conflicts and cohort reuse are useful durable source knowledge, not newEMC biology. No publication-worthy finding survives this lane.','coverage_incomplete':True,'specific_pending':['BO112012and3RTcomparatordonors:6libraries','pediatric352experimentcompletecrosswalk','scTumorcell-linepanels','89samplepediatricsarcomapreprint'], 'reopening':'An authenticated donor-linked processed cohort with malignant identity and >=2independentEMCdonors, appropriate stress/cycle/stromal controls and a useful question beyond prior fusion/axon-guidance biology. Resolve identity before biological analysis; complete relevant coverage before advancement.','TMEM266':'remains shelved','owned_processes_running':False,'publication_action':'none','integration':'Lead responsibility; local packet is not verified remote integration.'})
 print('metadata_libraries',len(libraries),'BO112pending',len(pending),'EMC_measured',0)
