"""Replay the bounded official ARCHS4 subset request in two explicit stages.

python retrieve_archs4.py request
python retrieve_archs4.py download

The second stage checks status once. Do not treat missing GSMs as zeros.
The API is live; the original retained ZIP is the immutable analysis input.
"""
import hashlib, json, sys, urllib.request
from pathlib import Path
P=Path(__file__).parent
BASE='https://maayanlab.cloud/sigpy'
def get(url, payload=None, cap=15000000):
    req=urllib.request.Request(url, data=None if payload is None else json.dumps(payload).encode(),
                               headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=45) as r: b=r.read(cap+1)
    assert len(b)<=cap
    return b
if sys.argv[1]=='request':
    payload={'gsm_ids':['GSM2113301','GSM6883080','GSM9037837'],'species':'human'}
    b=get(BASE+'/data/samples',payload)
    out={'url':BASE+'/data/samples','payload':payload,'bytes':len(b),
         'sha256':hashlib.sha256(b).hexdigest(),'response':json.loads(b)}
    (P/'archs4-request-replay.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out))
elif sys.argv[1]=='download':
    task=json.loads((P/'archs4-request-replay.json').read_text())['response']['task_id']
    state=json.loads(get(BASE+'/data/samples/status/'+task))
    print(state)
    if state.get('status')=='SUCCESS':
        b=get(BASE+'/data/samples/download/'+task)
        (P/'archs4-subset-replay.zip').write_bytes(b)
        print({'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
else:
    raise SystemExit('Use request or download')
