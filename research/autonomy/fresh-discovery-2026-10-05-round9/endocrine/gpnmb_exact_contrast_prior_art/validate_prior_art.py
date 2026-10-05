#!/usr/bin/env python3
"""Replay exact source hash/field membership; never reads numeric outcomes."""
from pathlib import Path
import json,hashlib,zipfile,io,re,shutil
from lxml import etree
P=Path(__file__).resolve().parent
load=lambda n:json.loads((P/n).read_text())
checks=[]
for p in P.glob('*.json'):
 if p.name.startswith('VALIDATION'):continue
 json.loads(p.read_text());checks.append('JSON:'+p.name)
for r in load('ORIGINAL-PRIMARY-CACHE-RECEIPTS.json')+load('REUSED-METHOD-IDENTITY-RECEIPTS.json'):
 b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];checks.append('exact source bytes:'+Path(r['path']).name)
ali=re.compile(r'\b(?:GPNMB|osteoactivin|HGFIN|DC-HIL)\b',re.I)
for r in load('ORIGINAL-PRIMARY-CACHE-RECEIPTS.json'):
 x=etree.parse(r['path'])
 # Whitelisted captions, labels and header text only; no table data cells.
 fields=x.xpath('//fig/label|//fig/caption|//table-wrap/label|//table-wrap/caption|//table-wrap//thead|//supplementary-material/label|//supplementary-material/caption')
 assert not any(ali.search(' '.join(f.itertext())) for f in fields)
 checks.append('caption/header alias membership:'+r['ids']['pmid'])
r=load('BRENCA-NATIVE-S1-SCHEMA.json');b=Path(r['archive_path']).read_bytes();assert len(b)==r['archive_bytes'] and hashlib.sha256(b).hexdigest()==r['archive_sha256']
with zipfile.ZipFile(io.BytesIO(b)) as z:b=z.read(r['member'])
assert len(b)==r['member_bytes'] and hashlib.sha256(b).hexdigest()==r['member_sha256']
with zipfile.ZipFile(io.BytesIO(b)) as z:
 ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 x=etree.fromstring(z.read('xl/sharedStrings.xml'))
 strings=[''.join(s.xpath('.//s:t/text()',namespaces=ns)) for s in x]
 assert not any(ali.search(s) for s in strings)
 checks.append('nativeS1 string-only alias membership; numeric cells closed')
c=load('ALL-NATIVE-SOURCE-UNITS-AND-SCOPE.json')
assert len(c['Hofvander']['all_native_conditions'])==13
assert c['Brenca']['all_native_case_labels']==list(range(1,13)) and c['Brenca']['paired_preservation_conditions']==5
assert 'unresolved' in c['EmMa']['status']
d=load('DECISION.json');assert not d['new_gene_matrix_or_statistics'] and not d['fully_blinded'] and not d['publication_worthy_finding'] and not d['campaign_exhausted']
assert shutil.disk_usage(P).free>=10*1024**3
print(json.dumps({'status':'PASS','checks':checks,'scope':'Exact inherited source bytes, gene-label/header fields, all native source units and honest limits. No numerical outcomes, plots, app gene views or scientific replication.'},indent=2))
