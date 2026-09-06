"""Independent archive-to-packet checks; does not import worker code or read labels."""
from pathlib import Path
import gzip
import hashlib
import itertools
import json
import zipfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'trial-frozen-baseline-package-2026-09-06'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def run():
    receipt = json.loads((HERE / 'integrity-receipt.json').read_bytes())
    for name, expected in receipt['files'].items():
        raw = (HERE / name).read_bytes()
        assert len(raw) == expected['bytes'] and digest(raw) == expected['sha256'], name
    manifest = json.loads((HERE / 'coordinator/packet-manifest.json').read_bytes())
    reader = json.loads((HERE / 'reader/manifest.json').read_bytes())
    archive = PACKAGE / 'frozen-experiment.zip'
    assert digest(archive.read_bytes()) == manifest['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        ranks = json.loads(z.read('trial-frozen-baseline-2026-09-06/rankings-EMC.json'))
        audit = json.loads(z.read('trial-frozen-baseline-2026-09-06/version-audit.json'))
        order = {key: sorted(ranks, key=lambda row: (-row['methods'][key]['score'], row['nct_id']))
                 for key in ('H', 'A')}
        sets = {key: {row['nct_id'] for row in rows[:100]} for key, rows in order.items()}
        h, a = sets['H'], sets['A']
        assert (len(h & a), len(a - h), len(h - a)) == (83, 17, 17)
        for key, rows in order.items():
            assert rows[99]['methods'][key]['score'] != rows[100]['methods'][key]['score']
            assert all(row['methods'][key]['rank'] == index + 1 for index, row in enumerate(rows))
        mappings = manifest['membership_and_provenance']
        assert len(mappings) == 34 and {row['nct_id'] for row in mappings} == h ^ a
        reader_by_case = {row['case_id']: row for row in reader['records']}
        assert len(reader_by_case) == 34
        pages = {}
        for item in mappings:
            nct = item['nct_id']
            assert item['group'] == ('entrant' if nct in a - h else 'displaced')
            origin = item['selected_source']
            name = origin['archive_member']
            if name not in pages:
                stored = z.read(name)
                raw = gzip.decompress(stored)
                pages[name] = (stored, raw, json.loads(raw))
            stored, raw, page = pages[name]
            assert digest(stored) == origin['page_stored_sha256']
            assert digest(raw) == origin['page_raw_sha256']
            entry = reader_by_case[item['case_id']]
            record = (HERE / 'reader' / entry['file']).read_bytes()
            assert record == raw[origin['byte_start']:origin['byte_end']]
            selected = page['studies'][int(origin['json_pointer'].split('/')[-1])]
            assert json.loads(record) == selected
            assert selected['protocolSection']['identificationModule']['nctId'] == nct
            canonical = json.dumps(selected, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
            assert digest(canonical) == audit[nct]['selected_record_sha256'] == entry['canonical_sha256']
            assert digest(record) == entry['raw_sha256'] == item['selected_raw_sha256']
            assert item['version_audit'] == audit[nct]
            assert len(audit[nct]['distinct_record_sha256']) == 1
            assert not any(key in entry for key in ('group', 'rank', 'score', 'H', 'A'))

    # Independent exhaustive calculation of the partial-identification formula.
    assignments = 0
    for intervals in itertools.product(((0, 0), (0, 1), (1, 1)), repeat=5):
        common, e1, e2, d1, d2 = intervals
        actual = []
        for c, x1, x2, y1, y2 in itertools.product(*(range(lo, hi + 1) for lo, hi in intervals)):
            actual.append((c + x1 + x2) - (c + y1 + y2))
            assignments += 1
        bound = (e1[0] + e2[0] - d1[1] - d2[1], e1[1] + e2[1] - d1[0] - d2[0])
        assert bound == (min(actual), max(actual))
    return {'status': 'passed', 'frozen_files_checked': len(receipt['files']),
            'rank_records': len(ranks), 'common': 83, 'entrants': 17, 'displaced': 17,
            'complete_record_source_slices_checked': 34, 'distinct_source_pages_checked': len(pages),
            'selected_versions_reconciled': 34, 'synthetic_interval_patterns': 3 ** 5,
            'synthetic_assignments_checked': assignments,
            'scope': 'Source identity, frozen membership, version audit and cancellation bounds; no relevance labels or scientific utility established.'}


if __name__ == '__main__':
    result = run()
    (HERE / 'coordinator-check-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
