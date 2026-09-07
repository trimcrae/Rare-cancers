"""Independent source/count and exact-design check; no worker-code imports."""
from fractions import Fraction
from math import comb
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent


def pmf(n, k, p):
    return comb(n, k) * p ** k * (1 - p) ** (n - k)


def run():
    manifest = json.loads((HERE / 'manifest.json').read_bytes())
    for item in manifest['files']:
        raw = (HERE / item['path']).read_bytes()
        assert len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256']
    original = HERE.parent / 'response-recoverability-2026-09-05/sources/NCT00601003.json'
    assert original.read_bytes() == (HERE / 'NCT00601003.saved.json').read_bytes()
    record = json.loads(original.read_bytes())['study']
    outcome = record['resultsSection']['outcomeMeasuresModule']['outcomeMeasures'][1]
    assert outcome['type'] == 'PRIMARY'
    assert len(outcome['groups']) == 1
    assert len(outcome['classes']) == 1
    counts = {entry['title']: int(entry['measurements'][0]['value'])
              for entry in outcome['classes'][0]['categories']}
    assert counts == {'Complete Response': 7, 'Partial Response': 11,
                      'Stable Disease': 35, 'Progressive Disease': 23}
    assert sum(counts.values()) == int(outcome['denoms'][0]['counts'][0]['value']) == 76
    assert not outcome.get('populationDescription') and not outcome.get('analyses')
    assert 'MIBG' in outcome['description'] and 'Bone Marrow' in outcome['description']

    reported = json.loads((HERE / 'decision-check.json').read_bytes())['protocol_arithmetic']
    design_results = {}
    for name, n1, stop, n, reject_above, p0, p1 in [
        ('I', 19, 6, 39, 16, Fraction(3, 10), Fraction(1, 2)),
        ('II', 18, 4, 33, 10, Fraction(1, 5), Fraction(2, 5)),
    ]:
        rates = []
        for p in (p0, p1):
            # Convolve each complete stage distribution, enforcing the interim path.
            probability = sum(pmf(n1, i, p) * pmf(n - n1, j, p)
                              for i in range(n1 + 1) for j in range(n - n1 + 1)
                              if i > stop and i + j > reject_above)
            rates.append(float(probability))
        assert abs(rates[0] - reported[name]['null_rejection_probability']) < 1e-14
        assert abs(rates[1] - reported[name]['alternative_rejection_probability']) < 1e-14
        design_results[name] = {'null_rejection_probability': rates[0], 'power': rates[1]}
    tails = {k: sum(pmf(21, j, Fraction(1, 20)) for j in range(k, 22)) for k in range(22)}
    cutoff = min(k for k, tail in tails.items() if tail <= Fraction(1, 20))
    assert cutoff == 4 and tails[3] > Fraction(1, 20)
    assert cutoff == reported['III']['computed_not_quoted_rejection_cutoff']
    return {'status': 'passed', 'worker_manifest_files': len(manifest['files']),
            'saved_record_byte_identity': True, 'pooled_outcome_denominator': 76,
            'pooled_CR_PR': 18, 'source_defines_separate_evaluable_strata': True,
            'root_original_page_inspection': [17, 18, 19], 'design_arithmetic': design_results,
            'stratum_III_derived_cutoff': cutoff,
            'scope': 'Source rules and design arithmetic only; no actual efficacy decision identifiable or computed.'}


if __name__ == '__main__':
    result = run()
    (HERE / 'coordinator-check-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
