import json
from concurrent.futures import ThreadPoolExecutor
from fetch_sources import fetch,D
p=json.loads((D/'cbio-profile-catalog.json').read_text())
svstudies={x['studyId'] for x in p if x['molecularAlterationType']=='STRUCTURAL_VARIANT'}
mp=[x['molecularProfileId'] for x in p if x['molecularAlterationType']=='MUTATION_EXTENDED' and x['studyId'] not in svstudies]
jobs=[(i,mp[i:i+20]) for i in range(0,len(mp),20)]
def run(t):
 i,ids=t
 r=fetch('https://www.cbioportal.org/api/mutations/fetch?projection=DETAILED',f'cbio-nr4a3-mutation-batch-{i:03d}.json',{'molecularProfileIds':ids,'entrezGeneIds':[8013]})
 return {k:v for k,v in r.items() if k!='body'}
with ThreadPoolExecutor(max_workers=3) as ex:
 for r in ex.map(run,jobs): print(json.dumps(r),flush=True)
events=[]
for i,_ in jobs:
 f=D/f'cbio-nr4a3-mutation-batch-{i:03d}.json'
 if f.exists():
  j=json.loads(f.read_text())
  if isinstance(j,list):events.extend(j)
(D/'cbio-nr4a3-mutation-all-events.json').write_text(json.dumps(events,indent=2))
print('profiles',len(mp),'records',len(events),'types',sorted(set(t['mutationType'] for t in events)))
print('fusionlike',[(t['studyId'],t['sampleId'],t.get('proteinChange'),t['mutationType']) for t in events if any(s in str(t).upper() for s in ['FUSION','REARRANGE','TRANSLOC'])])
