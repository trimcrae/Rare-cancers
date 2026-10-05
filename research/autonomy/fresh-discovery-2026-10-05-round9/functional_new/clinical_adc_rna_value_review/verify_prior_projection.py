#!/usr/bin/env python3
"""Replay only fixed-name/prior-claim projections; never emit biological values."""
from pathlib import Path
import csv, hashlib, json
root=Path('/workspace/Rare-cancers')
base=Path(__file__).resolve().parent
receipt=json.loads((base/'PRIOR-CLAIM-AND-EXPOSURE-REUSE.json').read_text())
for b in receipt['bindings']:
 p=Path(b['path'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==b['sha256'], p
panel=json.loads((root/'research/autonomy/fresh-discovery-2026-10-05-round8/adc_targets/PLAN-FROZEN.json').read_text())['fixed_panel']
assert set(['ERBB2','TACSTD2','NECTIN4','FOLR1']).issubset(panel)
protocol=(root/'research/autonomy/atlas-hofvander-validation-2026-09-06/protocol.md').read_text()
assert 'CD276' in protocol
source=root/'research/autonomy/discovery-2026-10-03/round2-surface-discovery.tsv'
selected=[]
with source.open() as stream:
 for row in csv.DictReader(stream,delimiter='\t'):
  if row['gene'] in ['GPNMB','LRRC15']:
   selected.append({'gene':row['gene'],'allocated':row['allocated']})
assert len(selected)==2
assert {x['gene'] for x in selected}=={'GPNMB','LRRC15'}
assert all(x['allocated']=='False' for x in selected)
print(json.dumps({'bound_claim_sources':len(receipt['bindings']),'seven_family_prior_names_verified':True,'name_boolean_only':selected,'new_outcome_computations':0,'new_source_requests':0},indent=2))
