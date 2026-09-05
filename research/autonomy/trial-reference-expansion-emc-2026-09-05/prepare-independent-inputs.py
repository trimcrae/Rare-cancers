"""Prepare answer-free source inputs for a fresh EMC adjudication reader.

Usage: python prepare-independent-inputs.py OUTPUT_DIRECTORY
This copies original registry records and provenance, not first-reader judgments.
It verifies selected record bytes against original compressed source pages.
Packet separation prevents accidental disclosure, not access-control enforcement.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

folder = Path(__file__).resolve().parent
root = folder.parents[2]
out = Path(sys.argv[1]).resolve()
sha = lambda b: hashlib.sha256(b).hexdigest()
canonical = lambda x: json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
order = read(folder/'work-order.json')
packet = read(folder/'source-packet.json')
protocol = read(folder/'label-protocol.json')
freeze = read(folder/'frame-freeze-receipt.json')
assert sha((folder/'work-order.json').read_bytes()) == freeze['files']['work-order.json']
assert sha((folder/'label-protocol.json').read_bytes()) == freeze['files']['label-protocol.json']
assert sha((folder/'source-packet.json').read_bytes()) == read(folder/'source-extraction-receipt.json')['packet_sha256']
assert len(order)==50 and len({x['nct_id'] for x in order})==50
records=[]
cache={}
for item in order:
    source=packet[item['nct_id']]['copies'][0]
    name=source['source']
    if name not in cache:
        path=(root/name).resolve();assert path.is_relative_to(root)
        raw=path.read_bytes();decoded=gzip.decompress(raw)
        cache[name]=(sha(raw),sha(decoded),json.loads(decoded))
    stored_hash,decoded_hash,doc=cache[name]
    assert stored_hash==source['source_sha256'] and decoded_hash==source['decoded_sha256']
    actual=doc
    for part in source['pointer'].split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        actual=actual[int(part)] if isinstance(actual,list) else actual[part]
    assert actual==source['record'] and sha(canonical(actual))==source['record_sha256']
    assert actual['protocolSection']['identificationModule']['nctId']==item['nct_id']
    records.append({'position':item['position'],'pair_id':item['pair_id'],'nct_id':item['nct_id'],
                    'original_record':actual,
                    'provenance':{k:source[k] for k in ['source','source_sha256','decoded_sha256','pointer','record_sha256']}})
products={'source-only-packet.json':{'scope':'All 50 new EMC pairs; original saved registry records and provenance only. No first-reader label, rationale, selected quote or adjudication supplied.','records':records},
          'label-protocol.json':protocol,
          'work-order.json':order}
out.mkdir(parents=True,exist_ok=True)
manifest={'scope':'Reader preparation; not independent judgments, scientific validation or technical blinding.','source_inputs':{n:sha((folder/n).read_bytes()) for n in ['work-order.json','source-packet.json','label-protocol.json']},'record_count':len(records),'original_pages_checked':len(cache),'files':[]}
for name,value in products.items():
    b=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    p=out/name
    if p.exists():assert p.read_bytes()==b, 'Existing packet changed'
    else:p.write_bytes(b)
    manifest['files'].append({'file':name,'bytes':len(b),'sha256':sha(b)})
mb=(json.dumps(manifest,indent=2)+'\n').encode();mp=out/'input-manifest.json'
if mp.exists():assert mp.read_bytes()==mb
else:mp.write_bytes(mb)
print(json.dumps({'output':str(out),'records':len(records),'source_pages':len(cache),'manifest_sha256':sha(mb)}))
