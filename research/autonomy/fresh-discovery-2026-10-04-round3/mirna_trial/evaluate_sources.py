import pathlib,json,hashlib,re,io,warnings,datetime
from html.parser import HTMLParser
import openpyxl
R=pathlib.Path(__file__).resolve().parent
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
  if t=='img':self.parts.extend(v for k,v in a if k=='alt')
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
extracted={}
for n in ['june-deck-mirror.decoded.html','esmo-poster-mirror.decoded.html','sept-release-mirror.decoded.html','sept-sponsor-original.html','june3-mirror.html','yoo2018.html']:
 p=Text();p.feed((R/n).read_text(encoding='utf-8',errors='replace'));s=re.sub(r'\s+',' ',' '.join(p.parts));extracted[n]=s
(R/'source-texts.json').write_text(json.dumps(extracted,indent=2),encoding='utf-8')
registry=json.loads((R/'trial-NCT06260774.json').read_text());p=registry['protocolSection']
roster=[
 ['100-003','endometrium',0.8],['103-001','solitary fibrous tumor (hemangiopericytoma)',0.8],['100-002','rectal adenocarcinoma',0.8],['100-004','sigmoid colon',1.6],
 ['102-001','extraskeletal myxoid chondrosarcoma','1.6 to 3.2'],['100-005','olfactory neuroblastoma',1.6],['103-002','adenoid cystic carcinoma',3.2],['101-001','myxoid sarcoma',3.2],['102-002','breast adenocarcinoma',3.2],
 ['100-007','leiomyosarcoma of retroperitoneum',4.8],['103-003','papillary thyroid carcinoma',4.8],['103-004','renal cell carcinoma',4.8],['100-008','adenoid cystic carcinoma','3.2 BF'],['102-003','p16+ poorly differentiated anal squamous carcinoma','3.2 BF'],['100-009','mucinous sigmoid adenocarcinoma','3.2 BF'],['103-007','pancreatic adenocarcinoma','3.2 BF']]
assert len(roster)==16 and len(set(x[0] for x in roster))==16
assert all(x[0] in extracted['june-deck-mirror.decoded.html'] for x in roster)
with warnings.catch_warnings():
 warnings.simplefilter('ignore');w=openpyxl.load_workbook(io.BytesIO((R/'yoo2018-s001.bin').read_bytes()),read_only=True,data_only=True)
sheet=w.worksheets[0];rows=list(sheet.values);assert rows[0]==('FEATURE','FREQ','WEIGHT','EFFECT')
features=[x[0] for x in rows[1:]]
out={
 'evaluated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source_hashes':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['trial-NCT06260774.json','june-deck-mirror.decoded.html','esmo-poster-mirror-tm2528668d1_ex99-2img001.jpg','march2026-selected.pdf','march-slide18.jpg','june-deck-mirror-tm2618153d1_ex99-1img013.jpg','june-deck-mirror-tm2618153d1_ex99-1img017.jpg','sept-release-mirror-tm2626237d1_ex99-1img01.jpg','sept-sponsor-original.html','yoo2018-s001.bin']},
 'registry':{k:p[k] for k in ['identificationModule','statusModule','designModule','outcomesModule']},
 'registry_has_results':registry.get('hasResults'),
 'registered_locations':[{'facility':x.get('facility'),'city':x.get('city'),'state':x.get('state')} for x in p.get('contactsLocationsModule',{}).get('locations',[])],
 'june_all16_roster_manual_transcription_verified_against_image':{'columns':['subject_id','sponsor_diagnosis','dose_mg_per_kg'],'rows':roster,'remaining_study_starred':['102-001','103-003','100-008']},
 'source_trial_identifiers':{n:sorted(set(re.findall(r'NCT\d+',s))) for n,s in extracted.items()},
 'image_inspection':{
  'esmo2025':{'figure4_102001_label':'rectal cancer','figure4_101001_label':'myxoid liposarcoma','data_cutoff':'2025-10-01','phase':'1a','trial_id_visible_in_original':'NCT06260774','103003':'thyroid cancer; thyroglobulin graph','102001_in_figure3_waterfall':False,'interpretation':'Conflicting diagnosis, no silent correction and no retrospective EMC outcome assignment from this figure.'},
  'march2026_slide18':{'102001_label':'myxoid chondrosarcoma','102001_response_labels':'Repeated SD, no numeric per-patient lesion values; dose legend1.6mg/kg IVQ28D','101001_label':'myxoid liposarcoma','101001_response_labels':'SD','102001_in_waterfall':False,'cutoff':'Not explicit on selected slide; cannot equate file month with data cutoff.'},
  'june2026_slide13_17':{'102001_label':'Extraskeletal myxoid chondrosarcoma','dose':'1.6mg/kg escalated to3.2mg/kg; no escalation date shown','response_labels':'Repeated SD for102-001 in plotted series; do not digitize exact duration','series_dose_color':'1.6mg/kg throughout drawn bar; cannot split pre/post-escalation response','table_source_date':'2026-03-14','table_denominator_issue':'Table calls N14 evaluable yet includes2NE; counts CR0 PR0 SD9 PD3 NE2. No correction/pooling.'},
  'sept2026_release':{'release':'2026-09-28','reported_cutoff':'2026-09-01','102001_response_labels':'Repeated SD in safety-population swimmer; no histology on figure itself','101001_response_labels':'SD then PD in swimmer','102001_individual_GMI_or_lesion_values':None,'individual_EMC_blood_or_tissue_mir10b_target_engagement':None,'public_aggregate_claims_not_assigned_to_EMC':['RNA-seq immune effects','6/15GMI>1.3','10/14SD'],'report_discordance':'Header6monthDCR36.7% versus body35.7%; preserve, no EMC calculation.'}
 },
 'yoo2018_s1_actual_evaluation':{'sheet':sheet.title,'rows_including_header':len(rows),'columns':list(rows[0]),'feature_rows':len(features),'model_roster_exposed':False,'interpretation':'This is an elastic-net feature list, not the624-model response roster. Its lack of an EMC name cannot prove exclusion. Full per-model linkage remains unavailable in inspected supporting file.'},
 'decision':'SHELVE standalone EMC miR-10b trial discovery. These are source-reported exposures/categorical observations and material provenance gaps, not a new causal or clinically useful inference.'
}
(R/'evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'roster':len(roster),'trial_identifiers':out['source_trial_identifiers'],'registered_locations':out['registered_locations'],'screen':out['yoo2018_s1_actual_evaluation'],'retained_bytes':sum(f.stat().st_size for f in R.iterdir() if f.is_file())},indent=2))
