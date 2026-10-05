from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
p=Path(__file__).resolve().parent
meta=json.loads((p/'PORTABILITY.json').read_text())
b=Path(meta['original_path']).read_bytes()
assert len(b)==meta['original_bytes']
assert hashlib.sha256(b).hexdigest()==meta['original_sha256']
r=ET.fromstring(b)
s=next(x for x in r.iter('sec') if x.get('id')=='s2-3-1')
text=[''.join(x.itertext()).strip() for x in s.findall('p')]
assert text==json.loads((p/'SAFE-CLINICAL-NMR-LINEAGE.json').read_text())['exact_clinical_NMR_cohort_only']
assert not s.findall('.//xref')
for d in json.loads((p/'DATA-AVAILABILITY-LINKS.json').read_text())['sections']:
 a=next(x for x in r.iter('sec') if x.get('id')==d['section_id'])
 assert ''.join(a.find('p').itertext()).strip()==d['data_availability_statement']
print('PASS: source bytes/hash, exact cohort paragraph, zero cohort citations, two exact availability statements. No network or numerical assays.')
