"""Carry a previously documented library-name conflict into tissue claims."""
import hashlib
import json
from pathlib import Path
import statistics
import urllib.request
import xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent
prior=BASE.parent/'tmem266-tissue-2026-10-03'
d=json.loads((prior/'fish-sensitivity-results.json').read_text())
link=[x for x in d['run_linkage'] if x['sample_alias']=='Si22']
assert len(link)==1
u='https://www.ebi.ac.uk/ena/browser/api/xml/'+link[0]['experiment_accession']
with urllib.request.urlopen(u,timeout=30) as r:b=r.read(100001)
assert len(b)<=100000
xml=ET.fromstring(b)
library=xml.findtext('.//LIBRARY_NAME')
assert library=='Si21',library
kept=[x for x in d['rows'] if x['id']!='Si22']
assert len(kept)==11
def summarize(rows):
    vals=[x['TMEM266_Log2CPM'] for x in rows]
    return {'n':len(vals),'ids':[x['id'] for x in rows],
            'median':statistics.median(vals),'minimum':min(vals),'maximum':max(vals)}
out={'scope':'Exploratory identity-qualified subset; no relabeling or detection inference',
     'conflict':{'alias':'Si22','library_name':library,'run_linkage':link[0]},
     'receipt':{'url':u,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},
     'all12':summarize(d['rows']),'exclude_Si22':summarize(kept),
     'EWSR1_positive_exclude_Si22':summarize([x for x in kept if x['FISH_1']=='EWSR1+']),
     'EWSR1_negative_exclude_Si22':summarize([x for x in kept if x['FISH_1']=='EWSR1-']),
     'rows':[{k:x[k] for k in ['id','FISH_1','TMEM266_Log2CPM']} for x in d['rows']]}
(BASE/'identity-sensitivity-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['rows','receipt','conflict']}))
