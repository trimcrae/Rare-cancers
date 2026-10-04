#!/usr/bin/env python3
"""Bind compact extraction/coverage to retained source bytes; no source reacquisition."""
import hashlib
import json
import math
import pathlib
import shutil
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
LEAD = pathlib.Path('/workspace/Rare-cancers')

def write(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def h(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def wilson(k, n):
    z = 1.959963984540054
    den = 1 + z*z/n
    center = (k/n + z*z/(2*n))/den
    half = z*math.sqrt((k/n)*(1-k/n)/n+z*z/(4*n*n))/den
    return [center-half, center+half]

table = [
 ('EMC',31,[9,2,5,12]),
 ('Skeletal chondrosarcoma',20,[0,0,0,0]),
 ('Chordoma',10,[1,0,0,0]),
 ('Myxofibrosarcoma',20,[0,0,0,0]),
 ('Myxoid liposarcoma',20,[0,0,0,0]),
 ('Intramuscular myxoma',15,[0,0,0,0]),
 ('Low-grade fibromyxoid sarcoma',10,[0,0,0,0]),
 ('Soft-tissue myoepithelioma',20,[1,0,0,0]),
 ('Ossifying fibromyxoid tumor',10,[3,0,0,0]),
 ('Angiomatoid fibrous histiocytoma, myxoid',5,[0,0,0,0]),
 ('Dedifferentiated liposarcoma, myxoid',10,[0,0,0,0]),
 ('Ewing sarcoma',10,[3,0,0,0]),
 ('CIC-rearranged sarcoma',5,[0,0,0,0]),
 ('Poorly differentiated synovial sarcoma',5,[0,0,0,0]),
 ('BCOR-CCNB3 sarcoma',5,[0,0,1,0]),
 ('Miscellaneous tumors',22,[1,1,0,0]),
]
assert sum(x[1] for x in table[1:]) == 187
assert sum(sum(x[2]) for x in table[1:]) == 11
assert sum(table[0][2]) == 28

observations = {
 'schema':'emc-r6-diagnostic-extraction/1','author':'Codex AI assistant /root/diagnostic',
 'meaning':'Source-reported measurements and prior art; no new clinical validation or pooled independent cohort.',
 'Yoshida2018':{
   'pmid':'29327709','doi':'10.1038/modpathol.2017.189',
   'source_sha256':h(ROOT/'sources/insm1_2018_primary.pdf'),
   'location':'PDF pp744–752; Table1 p747; Methods pp745–747; Discussion pp748–750',
   'identity':'All 31 EMCs had NR4A3 break-apart FISH confirmation; 24 were EWSR1 rearranged and 7 EWSR1 unrearranged.',
   'assay':'INSM1 nuclear IHC, clone A-8, 1:100; moderate/strong in >=5% of cells counts positive.',
   'table_columns':['entity','n','counts_5to25_26to50_51to75_76to100'],
   'complete_table1_rows':table,
   'all31_negative_conditions':{
      'negative_total':3,'EWSR1_rearranged_negative':2,'EWSR1_unrearranged_negative':1,
      'cellular_variant_negative':1,
      'conditions':[{'case_id':None,'condition':'One negative resection previously acid-decalcified.'},
                    {'case_id':None,'condition':'A different negative case: repeat on preoperative biopsy focally positive.'}],
      'crosswalk':'Individual IDs and a molecular/morphology/handling crosswalk are unavailable in the main PDF; none was invented.'},
   'other_conditions':'Three needle biopsy specimens positive; not counted as independent new donors or biopsy superiority.',
   'synaptophysin':{'any_signal_positive':13,'tested':31,'at_least5percent_positive_reported_percent':26},
   'authors_associations':'No significant association of INSM1 extent with cytomorphology, fusion group, synaptophysin or disease-specific survival.'
 },
 'Dulken2024':{'pmid':'38447752','doi':'10.1016/j.modpat.2024.100464',
   'source':'Verified primary abstract/crosswalk audit reused; new EPMC record agrees.',
   'reported_emc_strong_diffuse':25,'examined_emc':25,'mimics':685,'mimics_threshold_positive':0,'mimics_subthreshold':69,
   'threshold':'>5 puncta or 1 chromogen aggregate in >25% of cells',
   'case_crosswalk':'Unavailable; paired INSM1/discovery-validation overlap unknown.'},
 'Lenz2023':{'pmid':'36563884','examined_emc':17,'stained_emc':16,'positive':13,'negative':3,
   'criterion':'>=5% cells, any intensity','extent_bins_1plus_to4plus':[7,2,2,2],
   'intensity_weak_moderate_strong':[5,2,6],'molecular_success':12,
   'moderate_strong_in_more_than25percent_original_reported_percent':31,'individual_mapping':'Unavailable in retrieved primary abstract.'},
 'Giner2023':{'pmid':'36376703','n':31,'insm1_positive_original_percent':38.7,'synaptophysin_original_percent':22.6,
   'EWSR1_NR4A3_reported':19,'TAF15_NR4A3_reported':7,'threshold_and_patient_mapping':'Unavailable in retrieved abstract.'},
 'Huang2023':{'pmid':'36948401','molecular_confirmed_emc':58,'panTRK_tested':48,
   'insm1_moderate_strong_original_percent':54.6,'insm1_denominator':'Not resolved from abstract; not silently assigned 48 or 58.'},
 'Wang2022_singlecase':{'pmid':'35488288','pmcid':'PMC9052449','source_sha256':h(ROOT/'sources/PMC9052449.xml'),
   'identity':'One 69-year-old man; EWSR1::NR4A3 fusion by NGS; FISH EWSR1 and NR4A3 rearrangements.',
   'positive':['CD117','vimentin','CD56','NSE'],'focal_positive':['desmin'],
   'negative':['myogenin','S100','SYN','INSM1','CD34','STAT6','INI1','Brachyury','ERG','TLE1','AE1/AE3','WT1','CD99','SMA'],
   'CHRNA6':'Not reported','overlap':'Preprint PPR391699 describes the same case; overlap with later series is unknown.'},
 'Jiang2026_singlecase':{'pmid':'42088406','pmcid':'PMC13136674','source_sha256':h(ROOT/'sources/PMC13136674.xml'),
   'identity':'One 73-year-old man, left knee; TAF15::NR4A3 by targeted RNA sequencing.',
   'conditions':'Needle biopsy and surgical specimen were largely consistent; one donor.',
   'INSM1':'No measurement in inspected main XML','CHRNA6':'No measurement in inspected main XML','synaptophysin':'Negative.',
   'panel':'Myoepithelial-marker phenotype/diagnostic revision already original published finding.'},
 'uncertainty_descriptive_only':{
   'Yoshida_positive_28of31_wilson95':wilson(28,31),
   'Dulken_positive_25of25_wilson95':wilson(25,25),
   'meaning':'Binomial specimen-level illustrative precision only; neither new sensitivity estimate nor adjustment for donor/cohort selection. No pooling.'}
}
write('OBSERVATIONS.json', observations)

coverage = {
 'date':'2026-10-04','cutoff':'Sources acquired 2026-10-04; queries preserved in retrieve.py; no claim of universal exhaustion.',
 'population':'Molecularly authenticated EMC; CHRNA6 RNA-ISH/INSM1 or related measured diagnostic panels; relevant mesenchymal mimics.',
 'disposition':'Shelve the standalone paper; no novel claim advances; incomplete relevant case-level coverage remains visible.',
 'verified_evaluation_reused':[
   {'source':'CHRNA6 source evidence/crosswalk packets, 2026-10-02','paths':['research/autonomy/usage-sprint-2026-10-01/chrna6-source-evidence/handoff.md','research/autonomy/usage-sprint-2026-10-01/chrna6-specimen-crosswalk/handoff.md'],
    'meaning':'Discovery/validation donor overlap is unknown; do not repeat unchanged acquisitions or expression kernels.'},
   {'source':'R1–R5 baseline decision index and ROUND2-SOURCE-AUDIT.txt','meaning':'Known neural markers, pan-TRK positive observations, morphology associations and bulk screens are prior art; TMEM266 remains shelved.'}],
 'evaluated':[
   {'source':'Yoshida 2018, PMID 29327709','coverage':'All 31 EMC published marginals and all 187 mimic observations; negative-case handling and repeat-biopsy conditions; individual row map is not released in the main PDF.','independence':'31 source cases; the previously confirmed molecular cohort may overlap earlier Yoshida studies; these are not new donors.'},
   {'source':'Dulken 2024, PMID 38447752','coverage':'All reported 25 EMC/685 mimic aggregate findings from the verified abstract; a patient-linked panel was not obtained.','independence':'Discovery/validation/other RNA cohort overlap is unknown.'},
   {'source':'Lenz 2023, PMID 36563884','coverage':'All reported 16 stains/17 cases/12 molecular successes in the primary abstract; case crosswalk is missing.'},
   {'source':'Giner 2023, PMID 36376703','coverage':'All reported 31-case aggregate panel percentages; individual thresholds/maps are unknown.'},
   {'source':'Huang 2023, PMID 36948401','coverage':'58 molecular cases and reported INSM1 percentage; its denominator is unknown from the abstract.'},
   {'source':'Wang 2022, PMC9052449','coverage':'All reported IHC conditions and molecular authentication for the single case; duplicate preprint excluded.'},
   {'source':'Jiang 2026, PMC13136674','coverage':'One authentic donor, biopsy/surgical conditions, synaptophysin negative; no INSM1/CHRNA6 assay.'},
   {'source':'Zhang 2022, PMC9750778','coverage':'All 20 published soft-tissue categories and methods; EMC identity remains unresolved for 6 generic chondrosarcomas.'}
 ],
 'demonstrably_unsuitable_measurement':[
   {'source':'Pediatric case, PMC12285907','reason':'INSM1 positive, but NR4A3 was expressly not assessed; molecular authentication is absent for this claim.'},
   {'source':'Buttock case, PMC12376927','reason':'CHRNA6 is a citation only, not a case assay; genetic testing was not performed.'},
   {'source':'Buttock case, PMC10756670','reason':'INSM1 is a literature citation, not a case-linked result; identity is not authenticated.'},
   {'source':'PMC12504171','reason':'Review/citation trail, not a new measured cohort.'}
 ],
 'pending_accessible_analysis':[
   {'source':'Huang 2023, PMID 36948401','locator':'http://www.modernpathology.org/article/S0893395223000662/pdf','gap':'OpenAlex indexes bronze open access; case-level tables/supplement were not retrieved or analyzed.'},
   {'source':'Zhang 2022, PMC9750778','gap':'Supplementary Table S1, dataset identities and case subtypes are needed to resolve 6 generic chondrosarcomas; none is counted as EMC or confirmed non-EMC.'},
   {'source':'Primary sources identified through citations','pmids':['41755350','39828007','36754860','35932215','41315062'],
    'gap':'Individual diagnostic panel measurements, identity and overlap are not fully evaluated; no inference follows from a citation.'},
   {'source':'Broader mimic studies','pmids':['42720542','37169096','33610950','33210141','33629710'],
    'gap':'Comparator condition tables are not fully evaluated; no pooling or substitution for EMC evidence.'},
   {'source':'Initial broad INSM1 mesenchymal search','gap':'The response exceeded the 4 MiB cap; a title/abstract-scoped query with 87 hits completed, but the full broad query is not fully covered.'}
 ],
 'unavailable_evidence':[
   {'source':'Dulken 2024 case crosswalk','reason':'Verified 2026-10-02 audit reused; authoritative individual discovery/validation pairing was not obtained. This is not proof that it is unpublished.'},
   {'source':'Lenz 2023/Giner 2023 individual tables','reason':'Europe PMC/OpenAlex closed locators were observed; only the primary abstracts were evaluated. No claim of global absence.'}
 ],
 'stop':'Prior art defeats assay-limitation novelty; missing individual panel measurements prevent a useful new contrast. Pending suitable sources would block promotion.',
 'reopening':'Distinct public authenticated case-linked paired-marker, handling and mimic data with donor crosswalks enabling an unanswered consequential comparison.'
}
write('COVERAGE.json',coverage)
manifest = []
for p in sorted((ROOT/'sources').glob('*')):
    if p.is_file():
        manifest.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':h(p),'disposition':'cache_only'})
manifest.append({'path':'SEARCH-INDEX.json','bytes':(ROOT/'SEARCH-INDEX.json').stat().st_size,'sha256':h(ROOT/'SEARCH-INDEX.json'),'disposition':'cache_only_derived_duplicate'})
raw_bytes = sum(x['bytes'] for x in manifest)
assert raw_bytes <= 64*1024*1024
assert shutil.disk_usage(ROOT).free >= 10*1024*1024*1024
write('SOURCE-MANIFEST.json', {'files':manifest,'retained_raw_and_duplicate_bytes':raw_bytes,
  'portability':'Original sources are cache-only; URLs, SHA256 and acquisition scripts are committed; selected measurements are in OBSERVATIONS.json. Windows recovery archives are unavailable and were not reloaded.'})
write('DECISION.json',{'date':datetime.now(timezone.utc).isoformat(),'decision':'Shelve the standalone paper',
 'validity':'Source-reported prior limitations are supported; no new paired conditional finding.',
 'value':'Already published in primary studies; aggregate heterogeneity does not resolve assay, spectrum, handling or overlap differences.',
 'reopening':coverage['reopening'],'pending_evidence_blocks_promotion':True,'no_universal_exhaustion_claim':True,
 'running_processes':[],'raw_budget_bytes':raw_bytes,'storage_free_bytes':shutil.disk_usage(ROOT).free,
 'independent_review':'Requested from the radiotherapy worker after their RT freeze; the lead owns final integration.'})
print('Extraction arithmetic/source hashes verified;raw+duplicatebytes',raw_bytes)
