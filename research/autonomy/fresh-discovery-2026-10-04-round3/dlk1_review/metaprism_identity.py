from pathlib import Path
import urllib.request,json,hashlib,re,shutil
from datetime import datetime,timezone
base=Path(__file__).parent
assert shutil.disk_usage(base).free>10*1024**3+2*1024**2
out={'utc':datetime.now(timezone.utc).isoformat(),'scope':'Clinical sample/patient metadata only. No molecular or expression values requested.','sources':[]}
by_id={}
for attr in ['HISTOLOGY','CANCER_TYPE','CANCER_TYPE_DETAILED','RNASEQ_SAMPLE_ID','SAMPLE_TYPE']:
 typ='SAMPLE'
 url='https://cbioportal.gustaveroussy.fr/api/studies/metaprism_2023/clinical-data?clinicalDataType=SAMPLE&attributeId='+attr+'&pageSize=100000'
 response=urllib.request.urlopen(url,timeout=20);b=response.read();x=json.loads(b)
 assert all(r['clinicalAttributeId']==attr for r in x)
 out['sources'].append({'url':url,'status':response.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'n_clinical_records':len(x),'attributes':sorted(set(r['clinicalAttributeId'] for r in x))})
 for r in x:
  entity=r.get('sampleId',r.get('entityId'))
  key=typ+':'+entity
  if key not in by_id:by_id[key]={'id':entity,'patientId':r.get('patientId'),'type':typ}
  by_id[key][r['clinicalAttributeId']]=r['value']
rows=list(by_id.values())
out['n_entities_by_type']={t:sum(r['type']==t for r in rows) for t in ['SAMPLE','PATIENT']}
out['all_identity_rows']=rows
out['sarcoma_and_alias_rows']=[r for r in rows if re.search(r'sarcoma|chondr|extraskeletal|myxoid|\bEMC\b|NR4A[23]',str(r),re.I)]
out['literal_EMC_alias_rows']=[r for r in rows if re.search(r'extraskeletal|extra-skeletal|myxoid.*chondr|chondr.*myxoid|\bEMC\b|NR4A[23]',str(r),re.I)]
(base/'metaprism-identity.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(out['n_entities_by_type'])
print('attributes',[(s['n_clinical_records'],s['attributes']) for s in out['sources']])
print('EMC_alias',out['literal_EMC_alias_rows'])
print('sarcoma_rows',len(out['sarcoma_and_alias_rows']))
print(out['sarcoma_and_alias_rows'][:5])
