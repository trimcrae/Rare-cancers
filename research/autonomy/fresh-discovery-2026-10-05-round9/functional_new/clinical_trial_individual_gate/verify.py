"""Replay clinical identity/schema masks locally; no network or outcome cells."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
p=Path(__file__).resolve().parent
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
plan=json.loads((p/'PLAN.json').read_text()); source=Path(plan['reused_source']['path']); assert h(source)==plan['reused_source']['sha256']
r=E.parse(source).getroot();labels=[]
for tr in r.findall('.//table-wrap[@id="tbl2"]/table/tbody/tr'):
 cells=tr.findall('./td')
 for i in [0,2]:
  if len(cells)>i:
   v=''.join(cells[i].itertext()).strip()
   if v: labels.append(v)
x=json.loads((p/'ALL-ELIGIBLE-IDENTITY-COVERAGE.json').read_text());assert len(labels)==len(x['all_histology_labels'])==34
assert labels==[v['source_histology_label'] for v in x['all_histology_labels']]
assert next(v for v in x['all_histology_labels'] if v['source_histology_label']=='Extraskeletal myxoid chondrosarcoma')['source_baseline_case_count']=='3'
selected=[]
for tr in r.findall('.//table-wrap[@id="tbl4"]/table/tbody/tr'):
 cells=tr.findall('./td')
 if cells: selected.append(''.join(cells[0].itertext()).strip())
assert len(selected)==11 and 'Extraskeletal myxoid chondrosarcoma' not in selected
assert json.loads((p/'SUPPLEMENT-ACCESS.json').read_text())['status']=='unavailable or cap-limited; no retry'
assert not list((p/'raw-cache').glob('*.pdf'))
for v in json.loads((p/'VERIFIED-REUSE.json').read_text())['sources']:assert h(Path(v['path']))==v['sha256']
po=json.loads((p/'PORTABILITY.json').read_text());assert po['new_owner_retained_bytes']<=po['owner_cap_bytes'] and po['free_bytes']>=po['free_floor_bytes']
for v in po['new_owner_raw']: assert h(p/v['file'])==v['sha256']
if (p/'MANIFEST.json').exists():
 for v in json.loads((p/'MANIFEST.json').read_text())['files']:assert h(p/v['file'])==v['sha256']
print(json.dumps({'status':'PASS','baseline_histology_labels':34,'author_EMC_baseline_count':3,'selected_histology_rows':11,'outcome_cells_or_network_accessed':False}))
