#!/usr/bin/env python3
"""Verify source/identity/method/status bindings without emitting outcome fields."""
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
def load(name):
    return json.loads((ROOT/name).read_text())
def check(item):
    data = Path(item['path']).read_bytes()
    assert len(data) == item['bytes']
    assert hashlib.sha256(data).hexdigest() == item['sha256']
    return data
plan = load('PLAN.json')
corpus = []
for item in plan['corpus_bindings']:
    data = json.loads(check(item))
    # Project identity only, never abstracts/outcomes.
    corpus.extend((x['source'],x['id']) for x in data['resultList']['result'])
assert len(corpus) == len(set(corpus)) == 185
for item in plan['verified_reuse_bindings']:
    check(item)
receipts = load('SELECTED-SOURCE-RECEIPTS.json') + load('BIOC-SOURCE-RECEIPTS.json')
for item in receipts:
    check(item)
for item in load('BIOC-SOURCE-RECEIPTS.json'):
    tree = ET.fromstring(check(item))
    methods = []
    for passage in tree.iter('passage'):
        inf = {x.attrib['key']:x.text for x in passage.findall('infon')}
        # Exclude the entire embedded-table passage, not only its text/numerals.
        if 'xml' in inf or inf.get('section_type') != 'METHODS':
            continue
        methods.append(passage.findtext('text') or '')
    text = ' '.join(methods)
    if 'PMC9481662' in item['path']:
        assert 'extraskeletal myxoid chondrosarcoma (15 total, 3 TMA)' in text
        assert 'three cases each of extraskeletal myxoid chondrosarcoma' in text
        assert '5 cases had two specimens, representing primary tumor and recurrence' in text
    else:
        assert '16 extraskeletal myxoid chondrosarcomas' in text
        assert '1 representative section per case' in text
reconciled = load('CORPUS-RECONCILIATION.json')
assert [(x['source'],x['id']) for x in reconciled['records']] == corpus
assert reconciled['statuses'] == {'pending accessible analysis':173,'verified evaluation reused':10,'evaluated':2}
for item in reconciled['reused_method_decision_bindings']:
    check(item)
assert load('EXPOSURE-AND-NUMERICAL-STAGE-STATUS.json')['outcome_cells_exposed'] is True
assert load('DECISION.json')['numerical_stage_launched'] is False
result = {'status':'PASS','corpus_records':185,'unique_records':185,'source_originals':4,'prior_method_decisions':10,'new_method_sources':2,'remaining_primary_bodies_pending':173,'new_raw_retained_bytes':sum(x['bytes'] for x in receipts),'outcome_exposure_preserved':True,'numerical_analysis':False,'scope':'Source byte integrity, corpus identity, safe methods-count projection and explicit status/exposure truth. No table/result values read or computed by this audit; not full raw-source scientific reproduction.'}
(ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
