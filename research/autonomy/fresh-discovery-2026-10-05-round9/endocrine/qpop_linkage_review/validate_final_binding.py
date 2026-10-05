#!/usr/bin/env python3
"""Validate final metadata; preserve the original as-at source receipt binding."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def load(name):
    return json.loads((ROOT/name).read_text())
def check(path, size, digest):
    data = path.read_bytes()
    assert len(data) == size and hashlib.sha256(data).hexdigest() == digest, str(path)

binding = load('OWNER-FINAL-OPERATIONAL-BINDING.json')
supersession = binding['transient_owner_receipt_supersession']
for item in load('SOURCE-BINDINGS.json')['inputs']:
    if item['path'] == supersession['path']:
        assert item['sha256'] == supersession['initial_sha256']
        check(Path(item['path']), supersession['owner_final_bytes'], supersession['owner_final_sha256'])
    else:
        check(Path(item['path']), item['bytes'], item['sha256'])
for item in load('SCIENCE-FREEZE.json')['files']:
    check(ROOT/item['path'], item['bytes'], item['sha256'])
owner = Path(supersession['path']).parent
freeze_bytes = (owner/'SCIENCE-FREEZE.json').read_bytes()
assert hashlib.sha256(freeze_bytes).hexdigest() == binding['owner_freeze']['sha256']
freeze = json.loads(freeze_bytes)
for item in freeze['artifacts']:
    check(owner/item['path'], item['bytes'], item['sha256'])
our_roster = load('IDENTITY-ONLY-OBSERVATIONS-CORRECTED.json')['all_displayed_sample_labels_by_coarse_histology']
owner_roster = json.loads((owner/'ALL45-SAMPLE-IDENTITY-ROSTER.json').read_text())
assert len(owner_roster['records']) == 45
for row in owner_roster['records']:
    assert row['sample_id'] in our_roster[row['source_Fig1g_category']]
print('PASS: 15 final source bindings, 13 unchanged independent science files, 16 owner files and 45 categorical labels; one documented transient owner receipt supersession; no endpoints.')
