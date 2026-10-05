#!/usr/bin/env python3
"""Exact primary identity/unit checks; no case PET/pO2 or genetic endpoints."""
import argparse, hashlib, html, json, re
from pathlib import Path
from xml.etree import ElementTree as ET

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    root = Path(args.source_root)
    hashes = {'nordsmark2001-primary-xml.xml': '1c09b970fb4df27699a4cbde52b076089c5bd3bf32aecf243256cbc801e15e15',
              'bentzen2003-metadata.json': '98979f06835594d43e7040c9515d83c1f1a8350453be48c2b6074b6a65acff37'}
    inputs = []
    for name, expected in hashes.items():
        f = root/name
        assert hashlib.sha256(f.read_bytes()).hexdigest() == expected
        inputs.append({'path': str(f), 'bytes': f.stat().st_size, 'sha256': expected})
    article = ET.parse(root/'nordsmark2001-primary-xml.xml').getroot()
    body = article.find('body')
    preformat = body.find('preformat')
    assert preformat is not None
    text = ''.join(preformat.itertext())
    normalized = ' '.join(text.split())
    assert len(text) == 29189
    # Select protocol/cohort counts, not measured pressure or survival values.
    for phrase in ['The study involved 33 patients', 'Two patients had recurrent STS',
                   'minimum of 3 electrode tracks', 'involving 21 STS', 'involving 25 STS']:
        assert phrase in normalized, phrase
    assert re.search(r'median of 5 electrode tracks \(range 3.?7\)', normalized)
    aliases = ['extraskeletal', 'extra-skeletal', 'myxoid', 'chondrosarcoma', 'chordoid']
    alias_counts = {a: len(re.findall(re.escape(a), text, re.I)) for a in aliases}
    assert not any(alias_counts.values())
    metadata = json.loads((root/'bentzen2003-metadata.json').read_text())
    row = metadata['resultList']['result'][0]
    assert row['id'] == '12865184'
    abstract = ' '.join(html.unescape(re.sub('<[^>]+>', ' ', row['abstractText'])).split())
    assert 'Thirteen patients' in abstract and 'eleven of these patients' in abstract
    assert 'seven tumours were shown to be STS and six tumours were benign' in abstract
    assert 'following the scanning' in abstract
    assert 'Neither did it reflect the extent of hypoxia as determined with the oxygen electrode measurements.' in abstract
    data = {'scope': 'Before-values source structure, cohort/protocol counts and qualitative published calibration only.',
        'inputs': inputs, 'nordsmark': {'archive_preformat_characters': len(text),
            'body_child_tags': [x.tag for x in body], 'patients': 33,
            'source_recurrent_conditions': 2, 'minimum_tracks': 3, 'median_tracks': 5,
            'track_range': [3,7], 'earlier_overlapping_cohorts': [21,25],
            'isotope_not_patient_count': '31PMRS is phosphorus-31 spectroscopy, not 31 donors.',
            'literal_alias_counts': alias_counts,
            'interpretation': 'Provided archive preformat is real readable source text; absent structured sections/tables is not absent body. No explicit EMC label, not proven zero EMC.'},
        'bentzen': {'suspected_tumors': 13, 'completed_electrode_after_PET': 11,
            'all_13_histology_counts': {'STS': 7, 'benign': 6},
            'composition_of_11_paired_subset': 'Not authenticated from abstract; cannot assign all7STS to paired subset.',
            'published_qualitative_conclusion': 'In this setting FMISO did not reflect electrode-defined hypoxia; not a new EMC-specific finding or universal FMISO failure.'},
        'case_pO2_PET_or_genetic_endpoints_accessed': False, 'errors': []}
    Path(args.output).write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps({'inputs':len(inputs), 'cohort_and_track_protocol_checks':'PASS', 'errors':0, 'case_endpoint_cells_read':False}))

if __name__ == '__main__': main()
