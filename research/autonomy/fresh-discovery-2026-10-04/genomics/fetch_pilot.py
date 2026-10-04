import json,urllib.request,hashlib,pathlib,datetime
OUT=pathlib.Path(__file__).resolve().parent
API='https://www.cbioportal.org/api'
STUDY='msk_impact_50k_2026'
receipts=[]
def get(path,body=None,save=None):
    url=API+path
    payload=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(url,data=payload,headers={'Accept':'application/json','Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=90) as f: raw=f.read()
    rows=json.loads(raw)
    receipts.append({'url':url,'method':'GET' if body is None else 'POST','body':body,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'saved':save})
    if save: (OUT/save).write_bytes(raw)
    (OUT/'retrieval_receipts.json').write_text(json.dumps(receipts,indent=2))
    return rows
if __name__=='__main__':
    attrs=get('/studies/'+STUDY+'/clinical-attributes',save='clinical_attributes.json')
    prof=get('/studies/'+STUDY+'/molecular-profiles',save='profiles.json')
    study=get('/studies/'+STUDY,save='study.json')
    labels=get('/studies/'+STUDY+'/clinical-data?attributeId=CANCER_TYPE_DETAILED&clinicalDataType=SAMPLE&projection=SUMMARY&pageSize=100000')
    emc=[r for r in labels if 'extraskeletal myxoid' in r['value'].lower() or r['value'].upper() in ('EMCHS','EMC')]
    (OUT/'emc_label_records.json').write_text(json.dumps(emc,indent=2))
    print('Labels:',len(labels),'EMC samples:',len(emc),'patient IDs:',len({r['patientId'] for r in emc}))
    print(json.dumps(emc,indent=2))
