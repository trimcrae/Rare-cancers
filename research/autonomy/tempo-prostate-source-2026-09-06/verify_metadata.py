"""Validate preserved public metadata without retrieving or analyzing expression."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

P = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks = []
for receipt, filename in [('prostate-retrieval.json','prostate-article.xml'),
                          ('E-MTAB-12593-retrieval.json','E-MTAB-12593.json')]:
    d = json.loads((P/receipt).read_text())
    assert d['status'] == 200 and sha(P/filename) == d['sha256']
    assert (P/filename).stat().st_size == d['bytes']
    checks.append({'file':filename,**d})
for d in json.loads((P/'E-MTAB-12593-files-retrieval.json').read_text())['requests']:
    assert d['status'] == 200 and sha(P/d['file']) == d['sha256']
    assert (P/d['file']).stat().st_size == d['bytes']
    checks.append(d)
with (P/'E-MTAB-12593.sdrf.txt').open(encoding='utf-8-sig',newline='') as h:
    rows = list(csv.DictReader(h,delimiter='\t'))
assert len(rows) == 45
donors = collections.defaultdict(list)
for row in rows:
    assert row['Characteristics[organism]'] == 'Homo sapiens'
    assert row['Characteristics[disease]'] == 'prostate cancer'
    assert row['Characteristics[organism part]'] == 'prostate gland'
    donors[row['Characteristics[individual]']].append(row['Characteristics[sampling site]'])
assert len(donors) == 15
assert all(sorted(v)==['microenvironment','neoplasm','normal tissue'] for v in donors.values())
assert len({r['Source Name'] for r in rows}) == len({r['Comment[ENA_RUN]'] for r in rows}) == 45
files = []
def inventory(x):
    if isinstance(x,dict):
        if x.get('type') == 'file' and 'path' in x: files.append(x['path'])
        for v in x.values(): inventory(v)
    elif isinstance(x,list):
        for v in x: inventory(v)
inventory(json.loads((P/'E-MTAB-12593.json').read_text()))
assert sorted(files) == ['E-MTAB-12593.idf.txt','E-MTAB-12593.sdrf.txt']
tree = ET.parse(P/'prostate-article.xml')
methods=[]
for sid in ['sec2dot5-jcm-12-02605','sec2dot6-jcm-12-02605']:
    sec=tree.find(f'.//sec[@id="{sid}"]')
    assert sec is not None
    methods.append({'section_id':sid,'text':' '.join(''.join(p.itertext()) for p in sec.findall('p'))})
assert 'standard attenuators' in methods[0]['text'] and '22,537 probes' in methods[1]['text']
out={'status':'passed','source_checks':checks,'donors':15,'biological_regions':45,
     'regions_by_donor':dict(donors),'public_study_file_inventory':files,
     'methods':methods,'controls_in_primary_methods':'Internal processing RNA and no-sample controls run on each plate',
     'deposited_control_rows_identified':0,'processed_count_file_in_study_inventory':False,
     'scope':'Cancer-patient normal regions, not healthy donors. No raw reads or counts retrieved. No cross-study calibration claim.'}
(P/'coordinator-verification.json').write_bytes((json.dumps(out,indent=2)+'\n').encode())
(P/'sample-map.json').write_bytes((json.dumps(rows,indent=2)+'\n').encode())
print(json.dumps({'status':'passed','donors':len(donors),'regions':len(rows),'public_files':files}))
