"""Offline, all-labelled-specimen HLA coverage audit; no population inference."""
import argparse
import hashlib
import json
from pathlib import Path


def run(source):
    names = ['emc_label_records.json', 'emc_and_nr4a3_sample_clinical.json',
             'emc_and_nr4a3_patient_clinical.json']
    if not (source / names[2]).exists():
        names[2] = 'patient_clinical.json'
    inputs = {n: json.loads((source / n).read_text(encoding='utf-8')) for n in names}
    labels = inputs[names[0]]
    clinical = {}
    for row in inputs[names[1]]:
        clinical.setdefault(row['sampleId'], {})[row['clinicalAttributeId']] = row['value']
    patient = {}
    for row in inputs[names[2]]:
        patient.setdefault(row['patientId'], {})[row['clinicalAttributeId']] = row['value']
    rows = []
    fields = ['HLA_' + locus + str(allele) + '_LOH' for locus in 'ABC' for allele in (1, 2)]
    for label in sorted(labels, key=lambda x: x['sampleId']):
        sid, pid = label['sampleId'], label['patientId']
        c, p = clinical[sid], patient.get(pid, {})
        calls = {f: c.get(f) for f in fields}
        rows.append({'sample': sid, 'patient': pid, 'sample_type': c.get('SAMPLE_TYPE'),
                     'facets_qc': c.get('FACETS_QC'), 'facets_purity': c.get('FACETS_PURITY'),
                     'pathology_purity': c.get('TUMOR_PURITY'),
                     'genotypes': {f: p.get(f) for f in ['HLA-' + l + str(a) for l in 'ABC' for a in (1, 2)]},
                     'calls': calls, 'any_reported_call': any(v is not None for v in calls.values()),
                     'all_six_literal_unchanged': all(v == 'Unchanged' for v in calls.values())})
    called = [r for r in rows if r['any_reported_call']]
    return {'source_hashes': {n: hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names},
            'samples': len(rows), 'patients': len({r['patient'] for r in rows}),
            'samples_with_any_call': len(called), 'patients_with_any_call': len({r['patient'] for r in called}),
            'samples_all_six_unchanged': sum(r['all_six_literal_unchanged'] for r in rows),
            'unreported_samples': sum(not r['any_reported_call'] for r in rows),
            'calls_outside_literal_unchanged': sorted({v for r in rows for v in r['calls'].values() if v is not None and v != 'Unchanged'}),
            'rows': rows,
            'decision': 'Shelve: same source and four calls as September30 campaign; not new biology.',
            'limits': ['Unreported is not intact.', 'Six alleles are not six patients.',
                       'Literal Unchanged is not measured antigen presentation or immune competence.',
                       'Selected clinical series with sparse availability cannot estimate disease prevalence.']}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path(__file__).resolve().parent.parent / 'genomics')
    ap.add_argument('--out', type=Path, default=Path(__file__).with_name('hla-results.json'))
    args = ap.parse_args()
    result = run(args.source)
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','source_hashes')}))
