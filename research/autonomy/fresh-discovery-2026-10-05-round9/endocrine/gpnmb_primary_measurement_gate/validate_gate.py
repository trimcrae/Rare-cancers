#!/usr/bin/env python3
"""Source-integrity and safe method scope only; never reads gene outcomes."""
import hashlib,json,shutil
from pathlib import Path
from lxml import etree
P=Path(__file__).resolve().parent
def load(n): return json.loads((P/n).read_text())
checks=[]
for f in sorted(P.glob('*.json')):
 if f.name.startswith('VALIDATION'): continue
 json.loads(f.read_text());checks.append('JSON:'+f.name)
for r in load('PORTABILITY.json')['cache_only_inputs']+load('REUSED-SOURCE-RECEIPTS.json'):
 b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];checks.append('bytes:'+Path(r['path']).name)
x=etree.parse(str(P/'raw-cache/adc_sts2025.xml'))
sections=x.xpath('//sec[title="ADC targets and predictive biomarkers"]')
assert len(sections)==1
safe=' '.join(sections[0].xpath('.//text()'))
assert all(a.lower() not in safe.lower() for a in ['GPNMB','osteoactivin','glycoprotein nonmetastatic'])
checks.append('GPNMB literal not authenticated in declared target Methods section; not whole-assay absence')
d=load('EVALUATED-SOURCE-CONDITIONS.json');a=d['source_branches'][0]
assert sum(a['selected_histotype_counts'].values())==1664
assert a['input_specimens']==2344 and a['input_datasets']==26 and not d['native_GPNMB_measurement_authenticated']
assert load('ADC2025-S1-PRIMARY-RECEIPT.json')['method']=='HEAD'
assert '403' in load('ADC2025-S1-PRIMARY-RECEIPT.json')['error']
assert load('PORTABILITY.json')['new_raw_bytes']<=8*1024*1024
assert shutil.disk_usage(P).free>=10*1024**3
assert not load('DECISION.json')['new_matrix_statistics_authorized_or_run']
assert not load('DECISION.json')['publication_worthy_survivor']
assert not load('DECISION.json')['campaign_exhausted']
print(json.dumps({'status':'PASS','checks':checks,'scope':'Metadata, bytes, fixed source counts and whitelisted Methods literals only; no GPNMB biological values or statistical analysis'},indent=2))
