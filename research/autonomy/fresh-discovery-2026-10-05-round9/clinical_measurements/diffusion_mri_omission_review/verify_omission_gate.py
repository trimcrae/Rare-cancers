#!/usr/bin/env python3
"""Verify diagnosis-count/schema/reuse assertions without parsing ADC values."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
b=Path(__file__).resolve().parent
o=Path('/workspace/emc-r6-radiotherapy/research/autonomy/fresh-discovery-2026-10-05-round9/endocrine/diffusion_mri_gate')
r=ET.parse(o/'raw-cache/PMC6427044.xml').getroot()
rows=[]
for tr in r.findall('.//table-wrap[@id="Tab2"]//tr'):
 vals=[' '.join(e.itertext()) for e in tr if e.tag in ['td','th']]
 rows.extend(v for v in vals if v.startswith('ESMC'))
assert len(rows)==2 and any('2' in v for v in rows) and any('1' in v for v in rows)
assert 'PMC5510859' in ' '.join(r.find('.//ref[@id="CR26"]').itertext())
r=ET.parse(b/'source-cache/PMC10231763.xml').getroot()
ref=' '.join(r.find('.//ref[@id="pone.0286417.ref022"]').itertext());assert '94826' in ref
r=ET.parse(b/'source-cache/PMC10342739.xml').getroot()
for tid,want in [('jcm-12-04369-t002',['1']),('jcm-12-04369-t003',['0','2'])]:
 matches=[]
 for tr in r.findall('.//table-wrap[@id="'+tid+'"]//tr'):
  vals=[' '.join(e.itertext()) for e in tr if e.tag in ['td','th']]
  if vals and vals[0]=='Extraskeletal myxoid chondrosarcoma':matches.append(vals[1:])
 assert matches==[want],(tid,matches)
for a in json.loads((b/'PORTABILITY.json').read_text())['local_cache']:
 p=b/a['path'];assert p.stat().st_size==a['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
for a in json.loads((b/'PORTABILITY.json').read_text())['borrowed_zero_copy']:
 p=Path(a['path']);assert p.stat().st_size==a['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
print(json.dumps({'status':'PASS','checks':'2019EMC2+1/reuse2017;2023nativeall125reuse2021;postoponeEMCdonor0tumour2changes;allsourcehashes','no_ADC_values_parsed':True}))
