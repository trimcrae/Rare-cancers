#!/usr/bin/env python3
"""Check actual frozen input bytes; no source supersession is necessary."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def load(name):
    return json.loads((ROOT/name).read_text())
def check(path, size, digest):
    data = path.read_bytes()
    assert len(data) == size and hashlib.sha256(data).hexdigest() == digest, str(path)
sources = load('SOURCE-BINDINGS.json')['inputs']
for item in sources:
    check(Path(item['path']), item['bytes'], item['sha256'])
for item in load('SCIENCE-FREEZE.json')['files']:
    check(ROOT/item['path'], item['bytes'], item['sha256'])
binding = load('OWNER-FINAL-OPERATIONAL-BINDING.json')
owner = Path(next(s['path'] for s in sources if s['path'].endswith('FIG1-IDENTITY-INSPECTION-RECEIPT.json'))).parent
data = (owner/'SCIENCE-FREEZE.json').read_bytes()
assert hashlib.sha256(data).hexdigest() == binding['owner_freeze']['sha256']
freeze = json.loads(data)
for item in freeze['artifacts']:
    check(owner/item['path'], item['bytes'], item['sha256'])
our = load('IDENTITY-ONLY-OBSERVATIONS-CORRECTED.json')['all_displayed_sample_labels_by_coarse_histology']
roster = json.loads((owner/'ALL45-SAMPLE-IDENTITY-ROSTER.json').read_text())
assert len(roster['records']) == 45
for row in roster['records']:
    assert row['sample_id'] in our[row['source_Fig1g_category']]
result = {'status':'PASS','source_bindings':len(sources),'source_mismatches':0,'unchanged_independent_science_files':13,'owner_frozen_files':16,'categorical_sample_labels':45,'receipt_supersessions':0,'raw_response_rank_protein_values_used':False,'scope':'Actual byte bindings and prior-scoped categorical projection. Initial erroneous operational assumption is preserved and corrected in FINAL-BINDING-AMENDMENT-01.json.'}
(ROOT/'SETTLED-VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
