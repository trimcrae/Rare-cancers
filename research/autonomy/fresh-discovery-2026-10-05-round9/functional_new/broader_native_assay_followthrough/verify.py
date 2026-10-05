"""Local method/identity audit only; no network, expression or biochemical values."""
from pathlib import Path
from collections import Counter
import hashlib,json
p=Path(__file__).resolve().parent
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
plan=json.loads((p/'PLAN.json').read_text()); c=Path(plan['source_catalogue']['path']); assert h(c)==plan['source_catalogue']['sha256']
d=json.loads(c.read_text())['result']; assert len(d['uids'])==53
x=next(d[u] for u in d['uids'] if d[u]['accession']=='GSE135323')
m=json.loads((p/'GSE135323-ASSAY-CONDITION-MAP.json').read_text()); rows=m['all_condition_rows']; assert len(rows)==132
assert {z['gsm'] for z in rows}=={z['accession'] for z in x['samples']}
assert Counter(z['source_name'] for z in rows)==Counter({"Ewing's Sarcoma Cells 2D":57,"TE-Tumor, 3D Osteoblasts and Ewing's Sarcoma":60,'TE-Bone, 3D Osteoblasts':15})
assert len({z['gsm'] for z in rows})==132 and all(z['organism']=='Homo sapiens' for z in rows)
for f in ['SOURCE-ACCESS.json','GSM-METADATA-ACCESS.json']:
 a=json.loads((p/f).read_text()); entries=a.get('requests',[a])
 for r in entries:
  if 'file' in r: assert h(p/r['file'])==r['sha256'] and (p/r['file']).stat().st_size==r['bytes']
raw=(p/'raw-cache/GSE135323-allGSM-brief.txt').read_text(); assert '!sample_table_begin' not in raw.lower()
assert json.loads((p/'PRIMARY-METHOD-ACCESS.json').read_text())['status']=='unavailable; no retry'
for r in json.loads((p/'VERIFIED-REUSE.json').read_text())['bindings']: assert h(Path(r['path']))==r['sha256']
a=json.loads((p/'GSE140819-IDENTITY-CONDITION-COVERAGE.json').read_text()); source=Path(a['source_cache']['path']); assert h(source)==a['source_cache']['sha256']
assert len(a['all40_preparation_rows'])==40 and len({r['gsm'] for r in a['all40_preparation_rows']})==40
assert sum(r['status']=='pending native histology/identity' for r in a['all40_preparation_rows'])==19
assert a['source_label_preparation_counts']=={'lung cancer':5,'neuroblastoma':10,'MBC':10,'glioma':2,'CLL':2,'ovarian':5,'melanoma':2,'sarcoma':4}
port=json.loads((p/'PORTABILITY.json').read_text()); assert port['new_owner_raw_bytes_including_derivative_copies']==sum(r['bytes'] for r in port['new_owner_raw_files'])<=port['stage_cap_bytes']
for r in port['new_owner_raw_files']: assert h(p/r['file'])==r['sha256']
if (p/'MANIFEST.json').exists():
 for r in json.loads((p/'MANIFEST.json').read_text())['files']: assert h(p/r['file'])==r['sha256']
print(json.dumps({'status':'PASS','catalogue_records':53,'GSE135323_sample_records':132,'sample_units_not_donors':True,'raw_data_tables_accessed':False,'no_network':True}))
