"""Independent source integrity, count structure and experimental-unit verification.

No expression estimates are produced. Run from any working directory.
"""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import io
import itertools
import json
import re
import xml.etree.ElementTree as ET

P = Path(__file__).resolve().parent

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest = json.loads((P / 'manifest.json').read_text())
    for group, base in [('files', P), ('dependencies', P.parent)]:
        for item in manifest[group]:
            p = base / item['file']
            assert p.stat().st_size == item['bytes']
            assert digest(p) == item['sha256'], p
    soft = gzip.decompress((P / 'GSE119630_family.soft.gz').read_bytes()).decode()
    records = {}
    for block in re.split(r'^\^SAMPLE = ', soft, flags=re.M)[1:]:
        lines = block.splitlines()
        fields = collections.defaultdict(list)
        for line in lines[1:]:
            if line.startswith('!') and ' = ' in line:
                key, value = line.split(' = ', 1)
                fields[key].append(value)
        if fields['!Sample_organism_ch1'] == ['Homo sapiens']:
            records[lines[0]] = fields
    mapped = json.loads((P / 'sample-column-mapping.json').read_text())
    assert len(records) == len(mapped) == len({x['gsm'] for x in mapped}) == 119
    expected_hierarchy = set(itertools.product(range(1, 6), ['Normal', 'Cancer'], range(1, 3), range(1, 4)))
    observed_hierarchy = set()
    results = {}
    all_annotations = []
    for filename in ['GSE119630_ColonCancerReplicatesMaster.csv.gz', 'GSE119630_HumanGeneCountsMaster.csv.gz']:
        with gzip.open(P / filename, 'rt', newline='') as handle:
            rows = csv.reader(handle)
            header = next(rows)
            assert header[:3] == ['Probe_ID', 'Probe_Sequence', 'Accession']
            assert len(header) == len(set(header))
            annotations = {}
            cells = 0
            for row in rows:
                assert len(row) == len(header)
                assert row[0] not in annotations
                annotations[row[0]] = tuple(row[1:3])
                assert all(re.fullmatch('[0-9]+', value) and int(value) >= 0 for value in row[3:])
                cells += len(row) - 3
        assert len(annotations) == 21111
        for number, column in enumerate(header[3:], 4):
            matched = [x for x in mapped if x['matrix'] == filename and x['column'] == column]
            assert len(matched) == 1 and matched[0]['column_1based'] == number
            rec = records[matched[0]['gsm']]
            assert column in rec['!Sample_description']
            if 'ColonCancerReplicates' in filename:
                m = re.fullmatch(r'Patient(\d+)_(Normal|Cancer)_bioRep(\d+)_techRep(\d+)', column)
                assert m
                patient, state, biological, technical = m.groups()
                observed_hierarchy.add((int(patient), state, int(biological), int(technical)))
                title = rec['!Sample_title'][0]
                assert f'Patient {patient},' in title
                assert f'biological replicate {biological}, technical replicate {technical}' in title
                assert ('normal colon tissue' if state == 'Normal' else 'cancerous colon tissue') in title
        all_annotations.append(annotations)
        results[filename] = {'probes': len(annotations), 'libraries': len(header)-3, 'integer_counts_checked': cells}
    assert observed_hierarchy == expected_hierarchy
    assert all_annotations[0] == all_annotations[1]
    assert list(all_annotations[0]) != list(all_annotations[1])
    # Check every stored primary-method paragraph locator against the original XML.
    locators = json.loads((P / 'primary-method-locators.json').read_text())
    trees = {}
    for loc in locators:
        src = P.parent / loc['source']
        assert digest(src) == loc['sha256']
        if str(src) not in trees:
            trees[str(src)] = ET.parse(src)
        sections = [s for s in trees[str(src)].findall('.//sec')
                    if s.get('id') == loc['section_id'] and s.findtext('title') == loc['section_title']]
        assert len(sections) == 1
        paragraph = sections[0].findall('p')[loc['direct_p_index_1based']-1]
        assert ''.join(paragraph.itertext()) == loc['text']
    output = {'status': 'passed', 'worker_manifest_sha256': digest(P/'manifest.json'),
              'frozen_files_checked': len(manifest['files']), 'dependencies_checked': len(manifest['dependencies']),
              'matrices': results, 'human_samples_mapped_once':119, 'colon_patients':5,
              'normal_lysates':10, 'normal_libraries':30, 'primary_paragraph_locators_checked':len(locators),
              'scope':'Source structure and provenance only; no expression contrasts or publication readiness claim.'}
    (P/'coordinator-verification.json').write_bytes((json.dumps(output,indent=2)+'\n').encode())
    print(json.dumps(output,indent=2))

if __name__ == '__main__':
    main()
