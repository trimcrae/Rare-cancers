import json,urllib.request,hashlib
from fetch_pilot import OUT,get,STUDY,receipts
receipts.extend(json.loads((OUT/'retrieval_receipts.json').read_text()))
old='sarcoma_mskcc_2022'; labels=json.loads((OUT/'historical_msk2022_emc_labels.json').read_text());ids=sorted({r['sampleId'] for r in labels})
profiles=get('/studies/'+old+'/molecular-profiles',save='historical_msk2022_profiles.json')
get('/studies/'+STUDY+'/clinical-data/fetch?clinicalDataType=SAMPLE',{'ids':['P-0022485-T01-IM6']},'historical_unique_current_lookup.json')
get('/studies/'+old+'/clinical-data/fetch?clinicalDataType=SAMPLE',{'ids':ids},'historical_msk2022_emc_clinical.json')
for pr in profiles:
 typ=pr['molecularAlterationType'];mp=pr['molecularProfileId']
 if typ=='MUTATION_EXTENDED':get('/molecular-profiles/'+mp+'/mutations/fetch?projection=DETAILED',{'sampleIds':ids},'historical_msk2022_emc_mutations.json')
 if typ=='COPY_NUMBER_ALTERATION' and pr['datatype']=='DISCRETE':get('/molecular-profiles/'+mp+'/molecular-data/fetch?projection=DETAILED',{'sampleIds':ids},'historical_msk2022_emc_cna.json')
 if typ=='STRUCTURAL_VARIANT':get('/structural-variant/fetch',{'sampleMolecularIdentifiers':[{'sampleId':s,'molecularProfileId':mp} for s in ids]},'historical_msk2022_emc_sv.json')
url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13198192/fullTextXML'
try:
 raw=urllib.request.urlopen(url,timeout=60).read();(OUT/'bandlamudi2026.xml').write_bytes(raw)
 (OUT/'primary_source_receipt.json').write_text(json.dumps({'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},indent=2))
 print('primary xml',len(raw))
except Exception as e:print(type(e).__name__,str(e))
print('profiles',[(p['molecularProfileId'],p['molecularAlterationType']) for p in profiles])
