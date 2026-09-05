"""Verify first-reader provenance/coverage without claiming independent adjudication.

Arguments: worker repository root, output receipt. Uses original compressed registry
pages and prior integrated adjudicated reference. Standard library only.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

root = Path(sys.argv[1]).resolve()
folder = root / 'research/autonomy/trial-reference-expansion-emc-2026-09-05'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
canonical = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

def resolve(x, pointer):
    for k in pointer.split('/')[1:]:
        k = k.replace('~1', '/').replace('~0', '~')
        x = x[int(k)] if isinstance(x, list) else x[k]
    return x

freeze = read(folder / 'frame-freeze-receipt.json')
for name, expected in freeze['files'].items():
    assert sha((folder / name).read_bytes()) == expected, name
frame = read(folder / 'full-frame.json')
labels = read(folder / 'first-reader-labels.json')
pending = read(folder / 'unfinished-pairs.json')
overlap = read(folder / 'overlap-reference.json')
outside = read(folder / 'outside-frame-reference.json')
prior = read(root / 'research/autonomy/trial-reference-adjudication-2026-09-05/adjudicated-reference.json')['pairs']
fid = {p['pair_id'] for p in frame}
assert len(fid) == len(frame) == 149
assert len({p['nct_id'] for p in frame}) == 124
assert {d: sum(p['diagnosis'] == d for p in frame) for d in ['EMC', 'DSRCT', 'SS']} == {'EMC':58, 'DSRCT':39, 'SS':52}
assert overlap == [p for p in prior if p['pair_id'] in fid]
assert outside == [p for p in prior if p['pair_id'] not in fid]
assert len(overlap) == 25 and len(outside) == 24 and len(labels) == 50 and len(pending) == 74
oid = {p['pair_id'] for p in overlap}; lid = {p['pair_id'] for p in labels}; pid = {p['pair_id'] for p in pending}
assert not (oid & lid or oid & pid or lid & pid) and oid | lid | pid == fid
assert {p['diagnosis'] for p in labels} == {'EMC'}
assert {d: sum(p['diagnosis'] == d for p in pending) for d in ['EMC', 'DSRCT', 'SS']} == {'EMC':0,'DSRCT':29,'SS':45}
order = sorted([p['nct_id'] for p in labels], key=lambda n:(sha(('20260905|EMC-expansion|'+n).encode()),n))
assert order == [p['nct_id'] for p in labels]
pages = {}
def page(e):
    p = (root / e['source']).resolve(); assert p.is_relative_to(root)
    if e['source'] not in pages:
        b = p.read_bytes(); raw = gzip.decompress(b)
        pages[e['source']] = (sha(b), sha(raw), json.loads(raw))
    sh, dh, obj = pages[e['source']]
    assert sh == e['source_sha256'] and dh == e['decoded_sha256']
    return obj

quotes = modules = copies = 0
for row in labels:
    assert row['state'] == 'first_reader_pending_independent_verification'
    assert not row['clinical_eligibility_established'] and not row['clinical_benefit_established']
    for e in row['evidence']:
        s = resolve(page(e), e['pointer'])
        assert s[e['char_start']:e['char_end']] == e['excerpt']
        quotes += 1
    for e in row['reviewed_modules']:
        obj = page(e)
        parent, key = e['pointer'].rsplit('/', 1)
        module = resolve(obj, parent).get(key)
        assert (key in resolve(obj,parent)) == e['module_present']
        assert sha(canonical(module)) == e['module_sha256']
        modules += 1
packet = read(folder / 'source-packet.json')
assert set(packet) == {p['nct_id'] for p in frame}
for n, value in packet.items():
    assert value['copies']
    for copy in value['copies']:
        raw_record = resolve(page(copy), copy['pointer'])
        assert raw_record == copy['record'] == value['copies'][0]['record']
        assert sha(canonical(raw_record)) == copy['record_sha256']
        copies += 1
receipt = {'utc':datetime.now(timezone.utc).isoformat(), 'status':'passed', 'root':str(root),
           'frame_pairs':149,'distinct_trials':124,'preserved_adjudicated_overlaps':25,
           'preserved_outside_frame_pairs':24,'new_first_reader_pairs':50,'unfinished_pairs':74,
           'original_source_pages':len(pages),'record_copies_verified':copies,
           'source_excerpts_verified':quotes,'complete_modules_verified':modules,
           'scope':'Provenance and coverage verification only. New clinical-scope labels still require a separate independent reader and adjudication before evaluation.',
           'input_sha256':{n:sha((folder/n).read_bytes()) for n in ['frame-freeze-receipt.json','first-reader-labels.json','source-packet.json','unfinished-pairs.json']}}
Path(sys.argv[2]).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
