"""Offline exact source/identity validation; no requests or expression cells."""
from pathlib import Path
import json,hashlib,collections,xml.etree.ElementTree as ET,datetime,shutil
P=Path(__file__).resolve().parent
checks=[]
def ck(name,c):
 checks.append({'check':name,'pass':bool(c)})
 if not c:raise AssertionError(name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((P/n).read_text())
port=load('PORTABILITY.json')
for r in port['new_originals']:ck('original '+r['path'],sha(P/r['path'])==r['sha256'] and (P/r['path']).stat().st_size==r['bytes'])
for r in port['shared_originals_read_only']:ck('shared source '+r['absolute_path'],sha(Path(r['absolute_path']))==r['sha256'])
for r in load('PRIOR-STATUS-REUSE.json')['bindings']:ck('prior freeze/source '+r['absolute_read_only_path'],sha(Path(r['absolute_read_only_path']))==r['sha256'])
root=ET.fromstring((P/'raw-cache/GSE299349-BioSample-all68.xml').read_bytes())
by={b.attrib['accession']:b for b in root.findall('.//BioSample')}
bio=load('ALL68-BIOSAMPLE-IDENTITY-CONDITION-FIELDS.json')
roles=load('ALL68-EVALUATED-ROLE-DISPOSITIONS.json')
links=load('ALL68-DECLARED-BIOSAMPLE-METADATA-LINKS.json')
geo=load('RETAINED-GEO-WHITELIST-REPLAY.json')
geo_by=collections.defaultdict(dict)
for r in geo['source_rows']:
 if r['field']=='!Sample_source_name_ch1':geo_by[r['GSM']]['source_name']=r['value']
 elif r['value'].startswith('tissue:'):geo_by[r['GSM']]['tissue']=r['value'].split(':',1)[1].strip()
 elif r['value'].startswith('cell type:'):geo_by[r['GSM']]['cell_type']=r['value'].split(':',1)[1].strip()
ck('all68 literal accession coverage',len(by)==len(bio['records'])==len(roles['records'])==len(links['actual_links'])==68)
role_by={r['GSM']:r for r in roles['records']}
ck('unique GSM records',len(role_by)==68)
for r in bio['records']:
 b=by[r['BioSample']]
 raw_attrs={a.attrib.get('harmonized_name') or a.attrib.get('attribute_name'):a.text or '' for a in b.findall('./Attributes/Attribute')}
 out_attrs={a['harmonized_name'] or a['attribute_name']:a['value'] for a in r['identity_condition_attributes']}
 for k,v in out_attrs.items():ck(r['GSM']+' literal BioSample '+k,raw_attrs[k]==v)
 for k in ['source_name','tissue','cell_type']:
  ck(r['GSM']+' GEO/BioSample '+k,geo_by[r['GSM']].get(k)==out_attrs.get(k))
 ck(r['GSM']+' missing collectiondate',out_attrs.get('collection_date')=='missing')
 actual_links=[{'type':l.attrib.get('type'),'target':l.attrib.get('target'),'label':l.attrib.get('label'),'value':l.text or ''} for l in b.findall('./Links/Link')]
 ck(r['GSM']+' outward links exact',actual_links==r['outward_metadata_links'])
 ck(r['GSM']+' declared corresponding GEO link',any(x['value']=='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+r['GSM'] for x in actual_links))
 ck(r['GSM']+' project only other outwardlink',len(actual_links)==2 and any(x['target']=='bioproject' and x['value']=='1273954' for x in actual_links))
 rr=role_by[r['GSM']]
 ck(r['GSM']+' role fields literal',rr['BioSample_identity_fields']=={k:out_attrs[k] for k in ['source_name','tissue','cell_type','collection_date'] if k in out_attrs})
 ck(r['GSM']+' processed link public declaration only',rr['processed_source_links'] and rr['source_molecule']=='polyA RNA')
 ck(r['GSM']+' no invented new quantity action',rr['additional_EMC_numerical_action'].startswith('None;'))
ck('exact62 explicit tissue labels',collections.Counter(r['BioSample_identity_fields']['tissue'] for r in roles['records'] if 'cell_type' not in r['BioSample_identity_fields'])=={'myxofibrosarcoma':14,'synovial sarcoma':12,'undifferentiated pleomorphic sarcoma':13,'malignant peripheral nerve sheath tumor':11,'leiomyosarcoma':12})
ck('one source-labelled EMC already evaluated',len([r for r in roles['records'] if r['source_label_status']=='EMC already evaluated'])==1 and [r['GSM'] for r in roles['records'] if r['source_label_status']=='EMC already evaluated']==['GSM9037837'])
ck('source alias correction literal',role_by['GSM9037835']['source_alias_only']=='USZ-20_REA1' and role_by['GSM9037835']['BioSample_identity_fields']['cell_type']=='BCOR-rearranged sarcoma')
for n in ['ALL68-EVALUATED-ROLE-DISPOSITIONS.json','DECISION.json']:ck(n+' no values',load(n).get('new_GPNMB_values',load(n).get('new_quantities'))==0)
bar=load('ADDITIVE-CURRENT-READINESS-BARRIERS.json');w=bar['cache_only_witness'];ck('cache-only source witness bytes/hash',sha(P/w['path'])==w['sha256'] and (P/w['path']).stat().st_size==w['bytes'])
wit=load(w['path'])
for r in wit['source_bindings']:ck('witness reused source '+r['absolute_path'],sha(Path(r['absolute_path']))==r['sha256'])
ck('raw23 accessible not convenience exclusion',len(wit['Brenca']['current_deposit_records'])==23 and sum(len(r['actual_public_FASTQ_urls_only']) for r in wit['Brenca']['current_deposit_records'])==46)
ck('existing45/threecultures status evaluated','already evaluated' in wit['completed_not_pending'])
ck('free>=10GiB',shutil.disk_usage('/workspace').free>=10*1024**3)
ck('new source original budget',sum(r['bytes'] for r in port['new_originals'])<64*1024**2)
ck('all metadata calls<=4',load('COVERAGE.json')['requests']['actual_new_calls']==2)
ck('no new numerical stage',load('DECISION.json')['new_statistics']==0 and not roles['eligible_new_EMC_quantitative_stage'])
out={'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'Offline original-byte and source-label replay only. No network, sequence body, expression cells or numerical biological computation.','checks':checks,'passed':sum(c['pass'] for c in checks),'failed':0,'free_bytes':shutil.disk_usage('/workspace').free}
(P/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'failed':0,'validation_sha256':sha(P/'VALIDATION.json')}))
