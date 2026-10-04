"""Reproduce source-row authentication and descriptive arithmetic, not a disease test."""
from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,datetime,collections
B=Path(__file__).resolve().parent
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'published observation evaluation; no inferential pooling or new biomarker claim','tables':{},'source_hashes':{}}
for name in ['localized2020','eastley2018','structural2020','dr62012','heinhuis2020']:
 f=B/(name+'.xml');out['source_hashes'][f.name]=hashlib.sha256(f.read_bytes()).hexdigest();r=E.parse(f).getroot();tabs=[]
 for t in r.findall('.//table-wrap'):
  rows=[]
  for row in t.findall('.//tr'):
   vals=[' '.join(x.itertext()).strip() for x in row if x.tag in ['th','td']]
   s=' '.join(vals).lower()
   if any(q in s for q in ['exmc','extraskeletal','extra-skeletal','soft tissue chondrosarcoma','vwde','meaf6']):rows.append(vals)
  if rows:tabs.append({'id':t.get('id'),'rows':rows})
 out['tables'][name]=tabs
# Values directly read from localized2020 supplementaryTableS1 and mainTable1/3;
# preserve provenance/units and avoid treating five aliquots as five donors.
out['localized_case3_descriptive']={'cfDNA_ng_ml_intraoperative':15,'cfDNA_ng_ml_first_postoperative':7.8,'absolute_change_ng_ml':7.8-15,'relative_change_percent':100*(7.8/15-1),'ddPCR_donors':1,'ddPCR_timepoints':{'intraoperative':1,'postoperative':4},'reported_detected_timepoints':0,'followup_months':30.1,'recurrence':'No','tumor_volume_cm3':588,'target':'VWDE Cys1302Arg','tumor_VAF_percent':42,'interpretation':'Total cfDNA change is not ctDNA clearance; nondetection in one NED donor cannot estimate recurrence sensitivity or shedding.'}
out['known_linkage_failures']={'eastley2018_donor8':'No matched tumor in donor8, so no verified plasma target-positive opportunity.','M2':'Author-labelled EMC; MEAF6-PHF1 molecular conflict; no published NR4A3 co-fusion; preserve identity uncertainty. Thesis duplicates same donor.','Czachor_patient9':'Baseline0.92 with unspecified unit; no subsequent EMC blood observation.','DR6':'3 EMC in pooled17undifferentiated; no sample-ID linkage to serial41pairs/2thirdsamples.','Heinhuis':'2generic extraskeletal chondrosarcoma samples, training/evaluation only; no fusion/subtype crosswalk; plateletexpression not plasma tumorDNA.','AxiSTS':'One molecularly reclassifiedEMC; no patient ID linking to ACTG1/CRP/albumin results;8LMS discovery is notEMC.'}
# All GEO specimen identities were evaluated; broad metadata cannot exclude EMC.
out['Asano_metadata']={'GPL18941':json.loads((B/'asano-eligibility.json').read_text())[0], 'GPL21263':json.loads((B/'asano-compact-eligibility.json').read_text())}
assert out['Asano_metadata']['GPL18941']['n']==42
assert out['Asano_metadata']['GPL21263']['n']==1370
out['Asano_interpretation']='1412metadatarecords examined, no subtype labels; not evidence of zeroEMC. Expression not downloaded/analyzed because identities are unresolved.'
# Reuse the authenticated previous Subramanian evaluation with byte hashes.
old=B.parent/'immune'
out['verified_prior_reuse']={}
for name in ['subramanian-table-eligibility.json','gse213065.txt','COVERAGE.md','RESULTS.md']:
 f=old/name
 if f.exists():out['verified_prior_reuse'][str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
out['decision']='SHELVE standalone contribution; no new useful EMC shedding/monitoring finding demonstrated. Pending eligibility/linkage remains visible.'
(B/'evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({'source_row_sets':{k:len(v) for k,v in out['tables'].items()},'descriptive_cfDNA_change_percent':out['localized_case3_descriptive']['relative_change_percent'],'Asano_metadata_records':1412,'decision':out['decision']},indent=2))
