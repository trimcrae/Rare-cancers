#!/usr/bin/env python3
"""Source integrity/field-scope and published rule qualification only."""
import json,hashlib,re,shutil
from pathlib import Path
from lxml import etree
P=Path(__file__).resolve().parent
load=lambda n:json.loads((P/n).read_text())
checks=[]
for f in P.glob('*.json'):
 if f.name.startswith('VALIDATION'):continue
 json.loads(f.read_text());checks.append('JSON:'+f.name)
for r in load('PORTABILITY.json')['cache_only_inputs']:
 b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];checks.append('bytes:'+Path(r['path']).name)
r=load('RETAINED-NATIVE2014-FDG-CLAIM-TEXT.json');b=Path(r['source_path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
checks.append('retained2014exactsource')
x=etree.parse(str(P/'raw-cache/dual_time_soft_tissue2023.xml'))
# Clinical diagnosis strings only, no frequency/SUV/RI data cells.
labels=[]
for t in x.xpath('//table-wrap')[:2]:
 for tr in t.xpath('.//tbody/tr'):
  cells=tr.xpath('./td')
  if not cells:continue
  selected=cells[:2] if cells[0].get('rowspan') else cells[:1]
  for c in selected:
   s=' '.join(c.itertext()).strip()
   if s and re.search('[A-Za-z]',s):labels.append(s)
assert 'Chondrosarcoma (ST metastasis)' in labels and 'Myxofibrosarcoma' in labels and 'Myxoma' in labels
assert not any('extraskeletal' in s.lower() or 'EMC' in s for s in labels)
checks.append('allprinteddiagnosislabels—genericchondrosarcomanotrelabelled')
# Exact published qualifications, string membership only; no numerical fields projected.
disc=' '.join(x.xpath('//sec[title="4. Discussion"]//p//text()'))
for q in ['cannot help differentiate low-grade sarcomas from benign lesions','all lesions should still be biopsied','some tumors with pure myxoid content','need to be confirmed in a larger']:
 assert q in disc;checks.append('authorqualification:'+q)
a=load('ALL-SOURCE-CONDITIONS-AND-COVERAGE.json');assert len(a['all_exact_native_FDG_query_records'])==11 and a['native_query_complete_return']
d=load('DECISION.json');assert not d['numeric_stage_or_new_classifier'] and not d['publication_worthy_finding'] and not d['campaign_exhausted']
assert load('PORTABILITY.json')['new_raw_bytes']<=8*1024*1024 and shutil.disk_usage(P).free>=10*1024**3
print(json.dumps({'status':'PASS','checks':checks,'scope':'Exact source bytes, bounded metadata, clinical-label schema and original author qualifications only. No numericalendpoint/cutoff extraction, image or predictiveanalysis.'},indent=2))
