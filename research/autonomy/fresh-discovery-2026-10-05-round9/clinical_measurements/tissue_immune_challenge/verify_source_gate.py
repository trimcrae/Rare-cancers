#!/usr/bin/env python3
"""Verify scoped text-source bindings/roster arithmetic, not graphics or immune outcomes."""
from pathlib import Path
import hashlib,json,re,sys
b=Path(__file__).resolve().parent
main=(b/'source-cache/dancsok2019-text.txt').read_text()
supp=(b/'source-cache/dancsok2019-supplement-text.txt').read_text()
table=main[main.index('Table 1 Sarcoma samples'):main.index('DFSP dermato',main.index('Table 1 Sarcoma samples'))]
r=json.loads((b/'DANCSOK2019-ROSTER.json').read_text())
for row in r['table1_rows']:
 label=row['source_label']
 assert re.search(re.escape(label)+r'\s+'+str(row['n'])+r'\b',table),row
assert sum(row['n'] for row in r['table1_rows'])==1070
assert len(r['table1_rows'])==22
assert re.search(r'Total\s+1072\b',table)
assert not re.search(r'extraskeletal|extra-skeletal|myxoid chondrosarcoma',main+'\n'+supp,re.I)
assert 'CD3' not in supp[supp.index('Supplementary Table 1. Details of primary antibodies used for immunohistochemistry',supp.index('Supplementary Table 1. Details of primary antibodies used for immunohistochemistry')+1):supp.index('Abbreviations: mAb')]
for item in json.loads((b/'PORTABILITY.json').read_text())['cache_sources']:
 p=b/item['path'];assert p.exists()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],str(p)
 assert p.stat().st_size==item['bytes'],str(p)
print(json.dumps({'status':'PASS','main_table1_rows':22,'row_sum':1070,'source_printed_total':1072,'no_explicit_EMC_label_in_text':'verified; generic labels and images unresolved','source_bindings':'all checked','scope':'No image/count reconstruction, no restricted fields, no clinical efficacy inference'}))
