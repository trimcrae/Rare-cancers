"""Build an answer-free comparator packet from the immutable frozen sources.

Usage: python prepare-independent-inputs.py OUTPUT_DIRECTORY
Checks every original source copy before emitting one identical full record per
pair. Procedural separation is not a technical access barrier.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

folder = Path(__file__).resolve().parent
root = folder.parents[2]
emc = folder.parent / 'trial-reference-expansion-emc-2026-09-05'
out = Path(sys.argv[1]).resolve()
sha = lambda b: hashlib.sha256(b).hexdigest()
canonical = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
order = read(folder / 'work-order.json')
protocol = read(folder / 'protocol.json')
freeze = read(folder / 'freeze-receipt.json')
packet_path = emc / 'source-packet.json'
assert sha(packet_path.read_bytes()) == protocol['source_packet_sha256']
for name in ['protocol.json', 'work-order.json']:
    assert sha((folder / name).read_bytes()) == freeze['sha256'][name]
assert len(order) == 74 and len({x['pair_id'] for x in order}) == 74
assert [x['position'] for x in order] == list(range(1, 75))
assert sum(x['diagnosis'] == 'DSRCT' for x in order) == 29
assert sum(x['diagnosis'] == 'SS' for x in order) == 45
packet = read(packet_path)
cache, records = {}, []
copies_checked = 0
for item in order:
    copies = packet[item['nct_id']]['copies']
    assert copies and len({x['record_sha256'] for x in copies}) == 1
    provenance = []
    for source in copies:
        name = source['source']
        if name not in cache:
            path = (root / name).resolve()
            assert path.is_relative_to(root)
            raw = path.read_bytes()
            decoded = gzip.decompress(raw)
            cache[name] = (sha(raw), sha(decoded), json.loads(decoded))
        stored_hash, decoded_hash, doc = cache[name]
        assert stored_hash == source['source_sha256'] and decoded_hash == source['decoded_sha256']
        actual = doc
        for part in source['pointer'].split('/')[1:]:
            part = part.replace('~1', '/').replace('~0', '~')
            actual = actual[int(part)] if isinstance(actual, list) else actual[part]
        assert actual == source['record'] and sha(canonical(actual)) == source['record_sha256']
        assert actual['protocolSection']['identificationModule']['nctId'] == item['nct_id']
        provenance.append({k: source[k] for k in ['source', 'source_sha256', 'decoded_sha256', 'pointer', 'record_sha256']})
        copies_checked += 1
    records.append({**item, 'original_record': copies[0]['record'], 'provenance': provenance})

# Only the frozen generic scientific rules are supplied, without the original
# execution history, first-reader outcomes or coordinator-selected evidence.
reader_protocol = {
    'scope': 'Independent source-only reading of 29 DSRCT and 45 synovial sarcoma pairs.',
    'diagnosis_names': {'DSRCT': 'desmoplastic small round cell tumor', 'SS': 'synovial sarcoma'},
    'labels': protocol['labels'],
    'rules': protocol['rules'][:5],
    'separation': 'Freeze independent source-linked judgments before consulting any prior labels. This is procedural separation, not technical blinding.',
}
products = {
    'source-only-packet.json': {'scope': 'Complete archived records and provenance; no first-reader judgments, selected quotes or rationale.', 'records': records},
    'label-protocol.json': reader_protocol,
    'work-order.json': order,
}
out.mkdir(parents=True, exist_ok=True)
manifest = {
    'scope': 'Source-only preparation and byte verification; not independent semantic validation.',
    'source_inputs': {
        'work-order.json': sha((folder / 'work-order.json').read_bytes()),
        'protocol.json': sha((folder / 'protocol.json').read_bytes()),
        'source-packet.json': sha(packet_path.read_bytes()),
    },
    'record_count': len(records), 'copies_checked': copies_checked,
    'original_pages_checked': len(cache), 'files': [],
}
for name, value in products.items():
    raw = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()
    path = out / name
    if path.exists():
        assert path.read_bytes() == raw, 'Existing packet changed'
    else:
        path.write_bytes(raw)
    manifest['files'].append({'file': name, 'bytes': len(raw), 'sha256': sha(raw)})
raw = (json.dumps(manifest, indent=2) + '\n').encode()
path = out / 'input-manifest.json'
if path.exists():
    assert path.read_bytes() == raw
else:
    path.write_bytes(raw)
print(json.dumps({'output': str(out), 'records': len(records), 'copies': copies_checked, 'pages': len(cache), 'manifest_sha256': sha(raw)}))
