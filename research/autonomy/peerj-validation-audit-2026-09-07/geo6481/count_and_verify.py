"""Audit all SOFT sample labels without evaluating expression table values."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import re
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source' / 'GSE6481_family.soft.gz'

def one(fields, key):
    vals = fields[key]
    assert len(vals) == 1, (key, vals)
    return vals[0]

def main():
    started = time.perf_counter()
    meta = json.loads((HERE / 'metadata.json').read_text(encoding='utf-8'))
    rows = []
    for sample in meta['samples']:
        fields = sample['fields']
        histology = [v for v in fields['Sample_characteristics_ch1'] if v.startswith('Histology:')]
        assert len(histology) == 1, (sample['accession'], histology)
        raw = histology[0].split(':', 1)[1]
        description = one(fields, 'Sample_description')
        description_id, gender, description_diagnosis = description.split(', ', 2)
        assert raw == description_diagnosis, sample['accession']
        rows.append({
            'sample_accession': sample['accession'],
            'sample_record_source_line': sample['source_line'],
            'source_sample_id': description_id,
            'title': one(fields, 'Sample_title'),
            'histology_raw': histology[0],
            'diagnosis': raw,
            'description_raw': description,
            'source_name_raw': one(fields, 'Sample_source_name_ch1'),
            'platform': one(fields, 'Sample_platform_id'),
            'sampling_site_raw': [v for v in fields['Sample_characteristics_ch1'] if v.startswith('Sampling site:')],
            'provider': one(fields, 'Sample_biomaterial_provider_ch1'),
        })
    counts = dict(sorted(Counter(r['diagnosis'] for r in rows).items()))
    source_ids = [r['source_sample_id'] for r in rows]
    assert len(source_ids) == len(set(source_ids))
    design = one(meta['series'][0]['fields'], 'Series_overall_design')
    design_roster = design.split('consisting of ', 1)[1].split(' were analyzed', 1)[0]
    aggregate = {}
    for part in re.split(r', | and ', design_roster):
        match = re.fullmatch(r'(.+) \(n=(\d+)\)', part)
        assert match, part
        assert match[1] not in aggregate
        aggregate[match[1]] = int(match[2])
    assert {k.lower(): v for k, v in counts.items()} == aggregate

    # Separate streaming check of a different diagnostic field, directly from the
    # original compressed source, without loading metadata.json's parsed records.
    direct = {}
    listed = []
    current = None
    in_table = False
    with gzip.open(SOURCE, 'rt', encoding='utf-8') as stream:
        for line_number, line in enumerate(stream, 1):
            line = line.rstrip('\r\n')
            if line.endswith('_table_begin'):
                in_table = True
                continue
            if line.endswith('_table_end'):
                in_table = False
                continue
            if in_table:
                continue
            if line.startswith('^'):
                current = None
                if line.startswith('^SAMPLE = '):
                    current = line.removeprefix('^SAMPLE = ')
                    assert current not in direct
                    direct[current] = {'record_line': line_number}
            if line.startswith('!Series_sample_id = '):
                listed.append(line.removeprefix('!Series_sample_id = '))
            if current is not None and line.startswith('!Sample_source_name_ch1 = '):
                assert 'source_name' not in direct[current]
                value = line.removeprefix('!Sample_source_name_ch1 = ')
                assert value.startswith('Soft tissue tumors - ')
                direct[current].update(source_name=value, diagnosis=value.removeprefix('Soft tissue tumors - '), source_name_line=line_number)
    assert not in_table
    assert len(listed) == len(set(listed)) == len(direct) == len(rows) == 105
    assert set(listed) == set(direct) == {r['sample_accession'] for r in rows}
    for row in rows:
        other = direct[row['sample_accession']]
        assert row['diagnosis'] == other['diagnosis']
        assert row['sample_record_source_line'] == other['record_line']
        row['source_name_source_line'] = other['source_name_line']
    direct_counts = dict(sorted(Counter(r['diagnosis'] for r in direct.values()).items()))
    assert direct_counts == counts
    result = {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'full_sample_count': len(rows), 'unique_source_sample_ids': len(set(source_ids)),
        'diagnosis_counts_from_histology': counts,
        'diagnosis_counts_from_independent_source_name_scan': direct_counts,
        'aggregate_design_diagnosis_counts': aggregate,
        'three_source_fields_agree_per_sample': True,
        'series_roster_and_two_sample_parsers_agree': True,
        'per_sample_counts_equal_series_design': True,
        'missing_histology_labels': 0,
        'samples_annotated_chondrosarcoma': sum('chondrosarcoma' in r['diagnosis'].lower() for r in rows),
        'samples_annotated_extraskeletal_myxoid_chondrosarcoma': sum('extraskeletal myxoid chondrosarcoma' in r['diagnosis'].lower() for r in rows),
        'platform_counts': dict(Counter(r['platform'] for r in rows)),
        'sampling_site_counts': dict(Counter(v for r in rows for v in r['sampling_site_raw'])),
        'source_design': design,
        'elapsed_seconds': time.perf_counter() - started,
        'expression_values_parsed_or_computed': False,
        'limits': ['Counts describe deposited source diagnoses; they do not re-diagnose specimens.',
                   'The actual dataset or sample selection used by PeerJ.21497 is not identified by this audit.'],
    }
    (HERE / 'complete-sample-roster.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    (HERE / 'complete-count-audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
