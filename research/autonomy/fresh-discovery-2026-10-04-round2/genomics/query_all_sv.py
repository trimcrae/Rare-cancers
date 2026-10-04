import json,datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fetch_sources import fetch
D=Path(__file__).resolve().parent
profiles=json.loads((D/'cbio-profile-catalog.json').read_text())
sv=[p['molecularProfileId'] for p in profiles if p['molecularAlterationType']=='STRUCTURAL_VARIANT']
jobs=[(i,sv[i:i+20]) for i in range(0,len(sv),20)]
def work(t):
 i,ids=t
 return fetch('https://www.cbioportal.org/api/structural-variant/fetch',f'cbio-nr4a3-sv-batch-{i:03d}.json',{'molecularProfileIds':ids,'entrezGeneIds':[8013]})
with ThreadPoolExecutor(max_workers=3) as ex:
 for r in ex.map(work,jobs):print(json.dumps(r),flush=True)
events=[]
for i,ids in jobs:
 p=D/f'cbio-nr4a3-sv-batch-{i:03d}.json'
 if p.exists():
  data=json.loads(p.read_text())
  if isinstance(data,list):events.extend(data)
(D/'cbio-nr4a3-sv-all-events.json').write_text(json.dumps(events,indent=2))
print('events',len(events))
print('keys',list(events[0]) if events else [])
print('studies',sorted(set(t.get('studyId','?') for t in events)))
