"""Audit every saved certificate and witness without rerunning the scientific batch."""
import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location('independent_subjects', ROOT/'ipd-frontier-bounds-2026-09-06/coordinator_check.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
releases = {}
for filename in ('development-releases.json', 'stress-releases.json'):
    releases.update({r['case_id']: r['release'] for r in read(ROOT/'ipd-bounds-development-2026-09-06'/filename)['cases']})
oracle = {r['case_id']: r['result'] for r in read(ROOT/'ipd-bounds-development-2026-09-06/development-results.json')['cases']}
prior = {r['case_id']: r['result'] for r in read(ROOT/'ipd-frontier-bounds-2026-09-06/results.json')['cases']}
saved = read(HERE/'results.json')
assert saved['solver_sha256'] == hashlib.sha256((HERE/'suffix.py').read_bytes()).hexdigest()
assert saved['protocol_sha256'] == hashlib.sha256((HERE/'protocol.md').read_bytes()).hexdigest()
assert len(saved['cases']) == len(releases) == 22
seen = set()
counts = dict(cases=0, witnesses=0, oracle_containment=0, development_certificates=0,
              stress_certificates=0, prior_completed_intervals_unchanged=0)
for case in saved['cases']:
    identity, result = case['case_id'], case['result']
    assert identity not in seen
    seen.add(identity)
    release = releases[identity]
    lo, hi = result['q_outer']
    lower, upper = F(lo), None if hi == 'infinity' else F(hi)
    assert result['work_units'] == sum(result['work_counts'].values())
    assert result['work_units'] <= result['limits']['max_work_units']
    if result['reason'] == 'work_limit':
        assert result['work_units'] == result['limits']['max_work_units']
    if result['decision'].startswith('stable'):
        assert result['nonempty_proven'] and result['witnesses']
        if result['decision'] == 'stable_reject':
            assert lower > F('3.84145882069413')
        else:
            assert upper is not None and upper < F('3.84145882069412')
        counts['development_certificates' if identity in oracle else 'stress_certificates'] += 1
    for label, witness in result['witnesses'].items():
        arms = []
        for name in ('a', 'b'):
            rows = []
            assert len(witness[name]) == len(release['grid'])
            for t, (d, c) in enumerate(witness[name], 1):
                assert isinstance(d, int) and isinstance(c, int) and min(d, c) >= 0
                rows.extend([(t, 1)]*d + [(t, 0)]*c)
            assert helpers.arm_summary(rows, len(release['grid']), release['probability_digits'],
                                       tuple(map(int, release[name]['risk_counts']))) == release[name]
            arms.append(rows)
        _, q = helpers.history(*arms, len(release['grid']))
        assert q == F(witness['q']) and lower <= q and (upper is None or q <= upper)
        if label == 'stable_reject':
            assert q > F('3.84145882069413')
        elif label == 'stable_nonreject':
            assert q < F('3.84145882069412')
        counts['witnesses'] += 1
    if identity in oracle:
        old_lo, old_hi = map(F, oracle[identity]['q_outer'])
        assert lower <= old_lo and (upper is None or old_hi <= upper)
        counts['oracle_containment'] += 1
    if prior[identity]['complete_traversal']:
        assert result['complete_traversal'] and result['q_outer'] == prior[identity]['q_outer']
        counts['prior_completed_intervals_unchanged'] += 1
    counts['cases'] += 1
assert seen == set(releases)
out = dict(passed=True, **counts, scope='Exact saved witness summaries and tied scores; rational certification thresholds; all 18 saved exact oracle intervals; input/protocol/source digests and charged work. No rerun or speed/general utility claim.')
(HERE/'coordinator-saved-check.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(out))
