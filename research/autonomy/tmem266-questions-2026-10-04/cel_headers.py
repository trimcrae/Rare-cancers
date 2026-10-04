"""Bounded metadata-only CEL retrieval; source IDs and technical batch evidence."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
OLD=BASE.parent/'tmem266-prepublication-2026-10-03'
spec=importlib.util.spec_from_file_location('pilot',OLD/'raw_array_pilot.py')
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)

def decode(node):
    if isinstance(node,list):return [decode(x) for x in node]
    if not isinstance(node,dict):return node
    out={k:decode(v) for k,v in node.items()}
    if 'hex' in node:
        b=bytes.fromhex(node['hex']);typ=node.get('type','')
        if 'text/plain' in typ:
            out['decoded']=b.decode('utf-16-be',errors='replace').rstrip('\x00')
        elif 'ascii' in typ:
            out['decoded']=b.decode('ascii',errors='replace').rstrip('\x00')
    return out

def main():
    old=json.loads((OLD/'raw-array-results.json').read_text())
    rows=[]
    for sample in old['arrays']:
        c=pilot.Calvin(sample['url']);raw=c.read(0,65536)
        b=pilot.B(raw)
        assert (b.num('B'),b.num('B'))==(59,1)
        groups=b.num('i');pointer=b.num('I');g=b.generic()
        rows.append({'accession':sample['acc'],'title':sample['title'],
                     'url':sample['url'],'header_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                     'header':decode(g)})
    out={'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'scope':'Metadata only; no new target intensities, no biological collection-date inference',
         'total_network_bytes':sum(r['header_bytes'] for r in rows),'arrays':rows}
    (BASE/'cel-headers.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'arrays':len(rows),'bytes':out['total_network_bytes'],'saved':'cel-headers.json'}))

if __name__=='__main__':main()
