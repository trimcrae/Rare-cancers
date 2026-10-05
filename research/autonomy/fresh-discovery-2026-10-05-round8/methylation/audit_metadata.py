from pathlib import Path
import json,subprocess,hashlib,re,collections,datetime
P=Path(__file__).resolve().parent
W=P.parents[3]
old='research/autonomy/fresh-discovery-2026-10-04-round3/genomics/reassessment/methylation-tables.json'
b=subprocess.check_output(['git','show','80c40ed9fb1af0086bdfc9754c97b176490996e0:'+old],cwd=W);d=json.loads(b)
rows=d['41467_2020_20603_MOESM4_ESM.xlsx']['Tabelle1'];headers=rows[0]
refs=[dict(zip(headers[:11],r[:11])) for r in rows[1:] if r and str(r[0]).startswith('REFERENCE_SAMPLE')]
soft=(P/'sources/GSE140686_metadata.txt').read_text()
ms={}
for block in soft.split('^SAMPLE = ')[1:]:
 lines=block.splitlines();gsm=lines[0].strip();fields={}
 for line in lines[1:]:
  if line.startswith('!Sample_') and ' = ' in line:
   k,v=line.split(' = ',1);fields.setdefault(k[8:],[]).append(v)
 ids=[x for x in fields.get('description',[]) if x.startswith(('REFERENCE_SAMPLE','VALIDATION_SAMPLE'))]
 for x in ids:assert x not in ms;ms[x]={'GSM':gsm,**fields}
assert len(ms)==1505
emc=[r for r in refs if r['Diagnosis']=='Extraskeletal myxoid chondrosarcoma']
controls=[r for r in refs if r['Manifestation']=='Primary' and r['DNA']=='FFPE' and re.search('(?i)(synovial sarcoma|myxoid liposarcoma|low.grade fibromyxoid sarcoma|sclerosing epithelioid)',r['Diagnosis'])]
for r in emc+controls:
 r['GEO']={k:ms[r['ID']].get(k,[]) for k in ['GSM','description','characteristics_ch1','platform_id','data_processing']};r['array_slide']=r['IDAT'].split('_')[0]
 r['individual_age_released']=any('age:' in x.lower() for x in r['GEO'].get('characteristics_ch1',[]))
 assert r['GEO']['description'].count(r['ID'])==1
 r['platform']=r['GEO']['platform_id'][0]
checks=[]
for e in emc:
 sameplat=[c for c in controls if c['platform']==e['platform']]
 same=[c for c in sameplat if c['Supplier']==e['Supplier'] and c['Batch']==e['Batch']]
 chip=[c for c in sameplat if c['array_slide']==e['array_slide']]
 checks.append({'EMC_ID':e['ID'],'GSM':e['GEO']['GSM'],'IDAT':e['IDAT'],'platform':e['platform'],'same_platform_controls':len(sameplat),'same_supplier_and_batch_controls':[c['ID'] for c in same],'same_slide_controls':[c['ID'] for c in chip],'individual_age_released':e['individual_age_released']})
val=d['41467_2020_20603_MOESM6_ESM.xlsx']['Tabelle1']
vr=[r for r in val[1:] if len(r)>5 and 'extraskeletal myxoid' in str(r[5]).lower()]
assert len(emc)==10 and len(vr)==1
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prior_derived_binding':{'Git': '80c40ed9fb1af0086bdfc9754c97b176490996e0','path':old,'sha256':hashlib.sha256(b).hexdigest()},'GEO_metadata_binding':{'path':'sources/GSE140686_metadata.txt','sha256':hashlib.sha256((P/'sources/GSE140686_metadata.txt').read_bytes()).hexdigest(),'cache_only':True},'reference_metadata_records':len(refs),'all_GEO_records_inspected':len(ms),'EMC_reference_cases':emc,'fixed_primary_FFPE_control_cases':controls,'matching_feasibility':checks,'EMC_summary':{'suppliers':dict(collections.Counter(r['Supplier'] for r in emc)),'platforms':dict(collections.Counter(r['platform'] for r in emc)),'slide_counts':dict(collections.Counter(r['array_slide'] for r in emc)),'individual_age_metadata_present':sum(r['individual_age_released'] for r in emc)},'fixed_control_summary':{'cases':len(controls),'diagnoses':dict(collections.Counter(r['Diagnosis'] for r in controls)),'platforms':dict(collections.Counter(r['platform'] for r in controls)),'individual_age_metadata_present':sum(r['individual_age_released'] for r in controls)},'validation_initial_EMC_label':{'row':vr[0],'GSM':ms[vr[0][0]]['GSM'],'disposition':'Reclassified SEF with EWSR1:CREB3L4; demonstrably unsuitable EMC observation, not extra authenticated EMC'},'interpretation':'Source authentication/matching feasibility only, no methylation outcomes inspected. Chronological age, current proliferation and fusion partner per case absent. Same supplier/date does not identify donors or fully remove chip/platform/mixture confounding.'}
(P/'EMC-CONTROL-METADATA-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print('authenticated metadata',len(emc),'controls',len(controls),'reference',len(refs),'GEO',len(ms));print(out['EMC_summary']);print(out['fixed_control_summary']);print(checks)
