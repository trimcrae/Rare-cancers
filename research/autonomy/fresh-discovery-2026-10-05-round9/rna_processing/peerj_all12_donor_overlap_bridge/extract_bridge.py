"""Source-only exact Si/BioSample/ENA bridge; no matrices or outcome cells."""
from pathlib import Path
import json,hashlib,datetime,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
READINESS=P.parent/'gpnmb_all_condition_readiness'
SOURCE=Path('/workspace/Rare-cancers/research/autonomy/fresh-discovery-2026-10-05-round8/microenvironment/TEMPO-SOURCE-GATE.json')
allowed={'Sex','Age','Tissue','Cellularity','FISH_1','Metastasis','Collection date','Biomaterial Provider','Geographic location','Isolate'}
xml=P/'raw/all12-biosample.xml';assert hashlib.sha256(xml.read_bytes()).hexdigest()=='5d615f7178ddca1cfeb2316279b77b20613f0987096bc0ac4dccf1d36d34ac88';root=E.parse(xml).getroot();fresh={}
for b in root.findall('.//BioSample'):
 ids=[{'db':a.get('db'),'label':a.get('db_label'),'value':a.text} for a in b.findall('Ids/Id')]
 name=next(x['value'] for x in ids if x['label']=='Sample name')
 attrs={a.get('attribute_name'):a.text for a in b.findall('Attributes/Attribute') if a.get('attribute_name') in allowed}
 fresh[name]={'biosample':b.get('accession'),'sample_name':name,'sra_sample':next(x['value'] for x in ids if x['db']=='SRA'),'source_attributes':attrs}
prior=json.loads(SOURCE.read_text())['all12_library_ids'];ena={r['sample_alias']:r for r in prior}
header=json.loads((READINESS/'TEMPO-FILTERED-SCHEMA-ONLY.json').read_text())['sheets'][0]['header'][1:]
assert set(fresh)==set(ena)==set(header) and len(fresh)==12
hof=json.loads((READINESS/'HOFVANDER-SCHEMA.json').read_text())['EMC_conditions']
a=json.loads((READINESS/'ARRAY-CONDITION-ROSTERS.json').read_text())['all58_source_records']
seq=json.loads((READINESS/'GSE28866-ASSAY-AND-PEAK-ANNOTATION.json').read_text())
core={'Hofvander13':[{'sample_id':r['sample_id'],'source_label':r['source_label'],'known_overlap':r['known_overlap'],'patient_group':r['patient_group'],'specimen_exception':r['specimen_exception']} for r in hof], 'GSE24369_six':[{'gsm':r['gsm'],'title':r['title'],'platform':r['platform']} for r in a if r['gse']=='GSE24369' and r['title'].startswith('Extraskeletal myxoid chondrosarcoma')], 'GSE4303_ten':[{'gsm':r['gsm'],'title':r['title'],'platform':r['platform'],'reference':r['source_ch1']} for r in a if r['gse']=='GSE4303' and r['source_ch1']==['CRH-mRNA']], 'GSE28866_four':[{'gsm':r['accession'],'title':r['title'],'processed_column':'EMC_'+r['title'].removesuffix('_EMC'),'assay':'3SEQ','preservation':'FFPE'} for r in seq['EMC_source_records']]}
assert [len(v) for v in core.values()]==[13,6,10,4]
rows=[]
for si in header:
 x=fresh[si];old=ena[si];assert x['biosample']==old['sample_accession']
 rows.append({'processed_column':si,**x,'experiment':old['experiment_accession'],'run':old['run_accession'],'column_to_source_label_status':'Resolved exact Si Sample name + prior same-study accession map, not numeric suffix/order inference','patient_id':None,'patient_id_status':'No explicit distinct public patient identifier in released BioSample; author article reports final12 patients at cohort level','specimen_block_id':None,'specimen_block_status':'FFPE source material known, block/core ID and possible multiple available blocks not individually linked','sampled_lesion_primary_recurrent_metastatic':None,'sampled_lesion_status':'Metastasis attribute records unspecified clinical history; cannot classify sampled lesion or time','pre_post_treatment':None,'treatment_status':'Collected by study but no per-Si treatment field in inspected released attributes/source tables','numeric_tumor_purity':None,'purity_status':'Cellularity source category is morphology, not numeric malignant fraction','diagnosis_status':'Author-reviewed EMC cohort linked by PRJNA1357027/Si source map; generic BioSample title does not independently assert EMC. EWSR1FISH label not NR4A3 partner authentication.','technical_run_status':'One exact run/experiment/BioSample perSi in verified R8 release; this doesnot authenticate donor uniqueness/block replication','core_cohort_overlap':{k:{'status':'unresolved','direct_shared_patient_or_specimen_crosswalk':None,'reason':'No explicit source case/donor bridge. Provider/site/date/sex/age or absent shared aliases cannot establish overlap/non-overlap; no demographic or suffix inference used.'} for k in core}})
result={'date':'2026-10-05','source_original_sha256':hashlib.sha256(xml.read_bytes()).hexdigest(),'source_aliases_all12_exact':True,'source_author_reported_final_patients':12,'source_individually_identified_patient_ids':0,'rows':rows,'newly_resolved':'Exact Si/SAMN/SRS/SRX/SRR source alias map plus age/sex/site/preservation/provider/geography/collectionyear/morphology/FISH eligibility and unqualified metastasis-history labels. No new gene outcomes.','remaining':'All12 individual donor/block/lesion/treatment and every12x4 core overlap relation unresolved. Source dates/provider semantics need reconciliation.','no_independence_claim':True,'no_promotion':True}
(P/'ALL12-DONOR-SPECIMEN-CONDITION-BRIDGE.json').write_text(json.dumps(result,indent=2)+'\n');(P/'CORE-COHORT-IDENTITY-REFERENCE.json').write_text(json.dumps({'date':'2026-10-05','core_conditions':core,'scope':'Previously validated identities reused; no outcome/source cohort reanalysis. 33 core condition records are not33independent patients. Matching absence is not non-overlap.'},indent=2)+'\n')
print('All12 explicit Si-to-source labels verified; 48 cross-cohort donor/specimen relations unresolved.')
