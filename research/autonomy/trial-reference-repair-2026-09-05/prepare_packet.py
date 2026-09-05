"""Extract full selected registry modules without referring to prior adjudications."""
import gzip, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'research/autonomy/trial-discoverability-2026-09-05/sources'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
sel=json.loads((OUT/'selection.json').read_text(encoding='utf-8'))
receipt=OUT/'freeze-receipt.json'
if not receipt.exists():
    dump(receipt,dict(frozen_at_utc=datetime.now(timezone.utc).isoformat(),criteria_read_before_freeze=False,sha256={p.name:sha(p) for p in [OUT/'label-protocol.json',OUT/'selection.json',OUT/'freeze.py',OUT/'round-contract.json']}))
ids={n for s in sel['strata'] for n in s['selected_ids']}|{a['nct_id'] for a in sel['challenge_anchors']}
found={}
for p in sorted(SOURCE.rglob('*.json.gz')):
    data=json.loads(gzip.decompress(p.read_bytes()))
    for i,r in enumerate(data.get('studies',[])):
        n=r['protocolSection']['identificationModule']['nctId']
        if n in ids:
            item=dict(source=str(p.relative_to(ROOT)).replace('\\','/'),source_sha256=sha(p),pointer=f'/studies/{i}',record=r)
            if n not in found: found[n]=item
            else:
                assert found[n]['record']==r, f'Conflicting snapshots for {n}'
assert ids==found.keys(), sorted(ids-found.keys())
dump(OUT/'review-packet.json',found)
parts=[]
for n,x in sorted(found.items()):
    ps=x['record']['protocolSection']
    parts.append('\n==== '+n+' ====\n'+x['source']+'#'+x['pointer'])
    for m in ['identificationModule','statusModule','conditionsModule','designModule','descriptionModule','armsInterventionsModule','eligibilityModule']:
        parts.append(m+'\n'+json.dumps(ps.get(m,{}),ensure_ascii=False,indent=2))
(OUT/'review-packet.txt').write_text('\n'.join(parts)+'\n',encoding='utf-8')
print(json.dumps(dict(records=len(found),characters=sum(map(len,parts)),ids=sorted(found))))
