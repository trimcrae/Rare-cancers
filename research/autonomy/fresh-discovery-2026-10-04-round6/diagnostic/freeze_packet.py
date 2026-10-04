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
   'identity':'All31 EMCs NR4A3 break-apart FISH confirmed;24 EWSR1 rearranged,7 EWSR1 unrearranged.',
   'assay':'INSM1 nuclear IHC,cloneA-8,1:100;moderate/strong in>=5% cells counts positive.',
   'table_columns':['entity','n','counts_5to25_26to50_51to75_76to100'],
   'complete_table1_rows':table,
   'all31_negative_conditions':{
      'negative_total':3,'EWSR1_rearranged_negative':2,'EWSR1_unrearranged_negative':1,
      'cellular_variant_negative':1,
      'conditions':[{'case_id':None,'condition':'One negative resection previously acid-decalcified.'},
                    {'case_id':None,'condition':'A different negative case: repeat on preoperative biopsy focally positive.'}],
      'crosswalk':'IndividualIDs and linking molecular/morphology/handling crosswalk unavailable in mainPDF; not invented.'},
   'other_conditions':'Three needle biopsy specimens positive; not counted as independent new donors or biopsy superiority.',
   'synaptophysin':{'any_signal_positive':13,'tested':31,'at_least5percent_positive_reported_percent':26},
   'authors_associations':'No significant association of INSM1 extent with cytomorphology,fusiongroup,synaptophysin or disease-specific survival.'
 },
 'Dulken2024':{'pmid':'38447752','doi':'10.1016/j.modpat.2024.100464',
   'source':'Verified primary abstract/crosswalk audit reused; new EPMC record agrees.',
   'reported_emc_strong_diffuse':25,'examined_emc':25,'mimics':685,'mimics_threshold_positive':0,'mimics_subthreshold':69,
   'threshold':'>5 puncta or1 chromogen aggregate in>25% cells',
   'case_crosswalk':'Unavailable; pairedINSM1/discovery-validation overlap unknown.'},
 'Lenz2023':{'pmid':'36563884','examined_emc':17,'stained_emc':16,'positive':13,'negative':3,
   'criterion':'>=5% cells,any intensity','extent_bins_1plus_to4plus':[7,2,2,2],
   'intensity_weak_moderate_strong':[5,2,6],'molecular_success':12,
   'moderate_strong_in_more_than25percent_original_reported_percent':31,'individual_mapping':'Unavailable in retrieved primaryabstract.'},
 'Giner2023':{'pmid':'36376703','n':31,'insm1_positive_original_percent':38.7,'synaptophysin_original_percent':22.6,
   'EWSR1_NR4A3_reported':19,'TAF15_NR4A3_reported':7,'threshold_and_patient_mapping':'Unavailable in retrieved abstract.'},
 'Huang2023':{'pmid':'36948401','molecular_confirmed_emc':58,'panTRK_tested':48,
   'insm1_moderate_strong_original_percent':54.6,'insm1_denominator':'Not resolved from abstract; not silently assigned48 or58.'},
 'Wang2022_singlecase':{'pmid':'35488288','pmcid':'PMC9052449','source_sha256':h(ROOT/'sources/PMC9052449.xml'),
   'identity':'One69-year-oldman;EWSR1::NR4A3 fusion byNGS;FISH EWSR1 andNR4A3 rearrangements.',
   'positive':['CD117','vimentin','CD56','NSE'],'focal_positive':['desmin'],
   'negative':['myogenin','S100','SYN','INSM1','CD34','STAT6','INI1','Brachyury','ERG','TLE1','AE1/AE3','WT1','CD99','SMA'],
   'CHRNA6':'Not reported','overlap':'PreprintPPR391699 is samecase;later-series donor overlap unknown.'},
 'Jiang2026_singlecase':{'pmid':'42088406','pmcid':'PMC13136674','source_sha256':h(ROOT/'sources/PMC13136674.xml'),
   'identity':'One73-year-oldman,leftknee;TAF15::NR4A3 bytargetedRNAseq.',
   'conditions':'Needlebiopsy andsurgical specimen largelyconsistent;one donor.',
   'INSM1':'No measurement in inspected mainXML','CHRNA6':'No measurement in inspected mainXML','synaptophysin':'Negative.',
   'panel':'Myoepithelial-marker phenotype/diagnostic revision already originalpublished finding.'},
 'uncertainty_descriptive_only':{
   'Yoshida_positive_28of31_wilson95':wilson(28,31),
   'Dulken_positive_25of25_wilson95':wilson(25,25),
   'meaning':'Binomial specimen-level illustrative precision only; neither new sensitivity estimate nor adjustment for donor/cohort selection. No pooling.'}
}
write('OBSERVATIONS.json', observations)

coverage = {
 'date':'2026-10-04','cutoff':'Sources acquired2026-10-04;queries preserved inretrieve.py;not universalexhaustion.',
 'population':'Molecularlyauthenticated EMC;CHRNA6 RNA-ISH/INSM1 or related measured diagnosticpanels;relevant mesenchymalmimics.',
 'disposition':'Shelve standalonepaper;no advancing novelclaim;incomplete relevant case-levelcoverage remains visible.',
 'verified_evaluation_reused':[
   {'source':'CHRNA6 sourceevidence/crosswalk packets2026-10-02','paths':['research/autonomy/usage-sprint-2026-10-01/chrna6-source-evidence/handoff.md','research/autonomy/usage-sprint-2026-10-01/chrna6-specimen-crosswalk/handoff.md'],
    'meaning':'Discovery/validation donoroverlapunknown;do not repeat unchangedacquisitions or expressionkernels.'},
   {'source':'R1–R5 baseline decisionindex and ROUND2-SOURCE-AUDIT.txt','meaning':'Known neuralmarkers/panTRK positiveobservations,morphology associations andbulk screens are priorart;TMEM266shelved.'}],
 'evaluated':[
   {'source':'Yoshida2018PMID29327709','coverage':'All31EMC published marginals/all187mimiccategories;negativecase handling/repeatbiopsy conditions;individualrow mapnotreleased inmainPDF.','independence':'31sourcecases;previouslyconfirmed molecularcohort mayoverlap earlier Yoshida studies;notnewdonors.'},
   {'source':'Dulken2024PMID38447752','coverage':'Allreported25EMC/685mimicaggregatefindings fromverifiedabstract;patientlinkedpanelnotobtained.','independence':'Discovery/validation/otherRNAcohortoverlap unknown.'},
   {'source':'Lenz2023PMID36563884','coverage':'Allreported16stains/17cases/12molecularsuccesses inprimaryabstract;casecrosswalk missing.'},
   {'source':'Giner2023PMID36376703','coverage':'Allreported31caseaggregatepanelpercentages;individualthresholds/mapsunknown.'},
   {'source':'Huang2023PMID36948401','coverage':'58molecularcases,reportedINSM1percent;itsdenominatorunknownfromabstract.'},
   {'source':'Wang2022PMC9052449','coverage':'AllreportedIHCconditions andmolecularauthentication forsinglecase;preprintduplicateexcluded.'},
   {'source':'Jiang2026PMC13136674','coverage':'Oneauthenticdonor,biopsy/surgicalconditions,synaptophysinnegative;noINSM1/CHRNA6assay.'},
   {'source':'Zhang2022PMC9750778','coverage':'All20publishedsofttissuecategories andmethods;6genericchondrosarcomas remainEMCidentityunresolved.'}
 ],
 'demonstrably_unsuitable_measurement':[
   {'source':'PediatricPMC12285907','reason':'INSM1positive,butNR4A3expresslynotassessed;notmolecularlyauthenticatedforthisclaim.'},
   {'source':'ButtockPMC12376927','reason':'CHRNA6citationonly,notcaseassay;genetictestingnotperformed.'},
   {'source':'ButtockPMC10756670','reason':'INSM1literaturecitation,notcase-linkedINSM1result;identitynotauthenticated.'},
   {'source':'PMC12504171','reason':'Review/citationtrail,notnewmeasuredcohort.'}
 ],
 'pending_accessible_analysis':[
   {'source':'Huang2023PMID36948401','locator':'http://www.modernpathology.org/article/S0893395223000662/pdf','gap':'OpenAlexindexedbronzeOA;case-leveltables/supplementnotretrieved/analyzed.'},
   {'source':'Zhang2022PMC9750778','gap':'SupplementaryTableS1/dataset/casesubtypesneededtoresolve6genericchondrosarcomas;notcountedEMCornonEMC.'},
   {'source':'Citationidentifiedprimarysources','pmids':['41755350','39828007','36754860','35932215','41315062'],
    'gap':'Individualdiagnosticpanelmeasurements/identity/overlapnotfullyevaluated;noinferencefromcitation.'},
   {'source':'Broadermimicstudies','pmids':['42720542','37169096','33610950','33210141','33629710'],
    'gap':'Comparatorconditiontablesnotfullyevaluated;notpooled;noEMCsubstitution.'},
   {'source':'BroadinitialINSM1mesenchymalsearch','gap':'Responseexceeded4MiBcap;title/abstractscopedquery87hitscompleted;fullbroadquerynotfullycovered.'}
 ],
 'unavailable_evidence':[
   {'source':'Dulken2024casecrosswalk','reason':'Verified2026-10-02auditreused;authoritativeindividualdiscovery/validationpairingnotobtained,notproofunpublished.'},
   {'source':'Lenz2023/Giner2023individualtables','reason':'EPMC/OpenAlexclosedlocatorsobserved;primaryabstractonlyevaluated.NoGlobalabsenceclaim.'}
 ],
 'stop':'Priorartdefeatsassaylimitationnovelty;individualpanelgap preventsusefulnewcontrast. Pending suitable sources wouldblockpromotion.',
 'reopening':'Distinctpublicauthenticatedcase-linkedpairedmarker/handling/mimicdatawithdonorcrosswalk enablingunansweredconsequentialcomparison.'
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
  'portability':'Originalsources/cacheonly;URLs/SHA256/acquisitionscriptscommitted;selectedmeasurementsinOBSERVATIONS.json. Windowsrecoveryarchivesnotavailable/reloaded.'})
write('DECISION.json',{'date':datetime.now(timezone.utc).isoformat(),'decision':'Shelve the standalone paper',
 'validity':'Source-reported priorlimitations supported;no newpairedconditionalfinding.',
 'value':'Alreadyprimarypublished;aggregateheterogeneity doesnotresolveassay/spectrum/handlingoroverlap.',
 'reopening':coverage['reopening'],'pending_evidence_blocks_promotion':True,'no_universal_exhaustion_claim':True,
 'running_processes':[],'raw_budget_bytes':raw_bytes,'storage_free_bytes':shutil.disk_usage(ROOT).free,
 'independent_review':'Requestedfromcampaignchallengeworker;leadownsfinalintegration.'})
print('Extraction arithmetic/source hashes verified;raw+duplicatebytes',raw_bytes)
