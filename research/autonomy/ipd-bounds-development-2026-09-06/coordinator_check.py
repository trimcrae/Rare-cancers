"""Coordinator checks unequal arms, exact extrema, and query partitions independently."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from fractions import Fraction as F
from pathlib import Path


def summary(rows, k, digits, risks):
    s = F(1)
    curve = []
    for t in range(1, k + 1):
        at = sum(x >= t for x, e in rows)
        events = sum(x == t and e for x, e in rows)
        if at:
            s *= F(at - events, at)
        scaled = s * 10 ** digits
        q, rem = divmod(scaled.numerator, scaled.denominator)
        q += 2 * rem >= scaled.denominator
        curve.append(str(q) if digits == 0 else f'{q // 10**digits}.{q % 10**digits:0{digits}d}')
    return dict(n=len(rows), total_events=sum(e for t, e in rows), survival_rounded=curve,
                risk_counts={str(t): sum(x >= t for x, e in rows) for t in risks})


def statistic(a, b):
    observed = expected = variance = F(0)
    for t in sorted({x for x, e in a + b if e}):
        na, nb = (sum(x >= t for x, e in rows) for rows in (a, b))
        ea, eb = (sum(x == t and e for x, e in rows) for rows in (a, b))
        total, events = na + nb, ea + eb
        observed += ea
        expected += F(na * events, total)
        if total > 1:
            variance += F(events * na * nb * (total - events), total**2 * (total - 1))
    if not variance:
        assert observed == expected
        return F(0)
    return (observed - expected)**2 / variance


def rows_from_path(path):
    return [(t, e) for t, (d, c) in enumerate(path, 1) for e, count in ((1, d), (0, c)) for _ in range(count)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    spec = importlib.util.spec_from_file_location('tested_bounds', args.source / 'bounds.py')
    tested = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tested)
    # Different dimensions from the author's n=3,K=3 checks: unbalanced arms n=2,4,K=2.
    categories = list(itertools.product((1, 2), (0, 1)))
    record_sets = [list(itertools.combinations_with_replacement(categories, n)) for n in (2, 4)]
    group_checks = pair_checks = 0
    for digits, risks in itertools.product((0, 1, 2), ((1,), (1, 2))):
        groups = []
        for records in record_sets:
            group = {}
            for rows in records:
                key = json.dumps(summary(rows, 2, digits, risks), sort_keys=True)
                group.setdefault(key, []).append(list(rows))
            groups.append(group)
        for ak, aset in groups[0].items():
            for bk, bset in groups[1].items():
                release = dict(schema='discrete-km-release-v1', synthetic=True, grid=[1, 2],
                               probability_digits=digits, a=json.loads(ak), b=json.loads(bk))
                expected = [statistic(a, b) for a in aset for b in bset]
                result = tested.solve(release, queries=False)
                assert result['complete']
                assert list(map(F, result['q_outer'])) == [min(expected), max(expected)]
                group_checks += 1
                pair_checks += len(expected)
    # Independently rebuild moderate true summaries and check each endpoint witness.
    releases = json.loads((args.source / 'development-releases.json').read_text())['cases']
    truth = {c['case_id']: c for c in json.loads((args.source / 'development-truth.json').read_text())['cases']}
    results = {c['case_id']: c['result'] for c in json.loads((args.source / 'development-results.json').read_text())['cases']}
    checked, query_checks = [], []
    for item in releases:
        rel, result = item['release'], results[item['case_id']]
        original = truth[item['parent_case_id']]
        a, b = [list(map(tuple, original[arm])) for arm in ('a', 'b')]
        for arm, rows in (('a', a), ('b', b)):
            assert summary(rows, len(rel['grid']), rel['probability_digits'], map(int, rel[arm]['risk_counts'])) == rel[arm]
        q = statistic(a, b)
        lo, hi = map(F, result['q_outer'])
        assert lo <= q <= hi
        p = math.erfc(math.sqrt(float(q) / 2))
        assert result['decision'] != 'stable_reject' or p < .05
        assert result['decision'] != 'stable_nonreject' or p >= .05
        for label, expected in (('q_min', lo), ('q_max', hi)):
            witness = result['witnesses'][label]
            wa, wb = [rows_from_path(witness[arm]) for arm in ('a', 'b')]
            assert statistic(wa, wb) == expected
            for arm, rows in (('a', wa), ('b', wb)):
                assert summary(rows, len(rel['grid']), rel['probability_digits'], map(int, rel[arm]['risk_counts'])) == rel[arm]
        checked.append(dict(case_id=item['case_id'], q=str(q), p_approx=p, original_contained=True))
        if result['decision'] != 'unresolved':
            continue
        arm_paths = []
        for arm in ('a', 'b'):
            paths, meta = tested.enumerate_arm(rel, arm)
            assert meta['complete']
            arm_paths.append([rows_from_path(path) for path in paths])
        scores = [(a, b, statistic(a, b)) for a in arm_paths[0] for b in arm_paths[1]]
        assert [min(q for a, b, q in scores), max(q for a, b, q in scores)] == [lo, hi]
        options = []
        def classify(low, high):
            if low > F('3.84145882069413'):
                return 'stable_reject'
            if high <= F('3.84145882069412'):
                return 'stable_nonreject'
            return 'unresolved'
        for arm_index, arm in enumerate(('a', 'b')):
            for t in rel['grid']:
                if str(t) in rel[arm]['risk_counts']:
                    continue
                partition = {}
                for a, b, q in scores:
                    count = sum(x >= t for x, e in (a, b)[arm_index])
                    partition.setdefault(count, []).append(q)
                if len(partition) < 2:
                    continue
                outcomes = [dict(risk=count, pairs=len(qs), q_outer=[str(min(qs)), str(max(qs))],
                                 decision=classify(min(qs), max(qs))) for count, qs in sorted(partition.items())]
                options.append(dict(arm=arm, time=t, outcomes=outcomes,
                                    worst_unresolved_pairs=max(o['pairs'] if o['decision']=='unresolved' else 0 for o in outcomes),
                                    worst_pairs=max(o['pairs'] for o in outcomes)))
        assert options == result['query_options']
        selected = min(options, key=lambda o: (o['worst_unresolved_pairs'], o['worst_pairs'], o['arm'], o['time']))
        assert selected == result['selected_query']
        query_checks.append(dict(case_id=item['case_id'], pairs=len(scores), options=len(options), selected=selected))
    # An independent high-precision numerical cross-check supplements (not replaces) the rational proof.
    sys.path.insert(0, 'C:/Projects/EMC-Research/.cache/python-deps')
    sys.path.insert(0, str(Path.cwd() / '.cache' / 'ipd-verifier-deps'))
    import mpmath as mp
    mp.mp.dps = 65
    threshold = [mp.erfc(mp.sqrt(mp.mpf(q) / 2)) for q in ('3.84145882069412', '3.84145882069413')]
    assert threshold[0] > mp.mpf('.05') > threshold[1]
    out = dict(passed=True, source_sha256={name: hashlib.sha256((args.source/name).read_bytes()).hexdigest()
               for name in ('bounds.py', 'protocol.md', 'development-releases.json', 'development-results.json', 'development-truth.json')},
               unequal_arm_release_pairs=group_checks, unequal_arm_subject_pairs=pair_checks,
               development_checks=checked, query_partition_checks=query_checks,
               independent_threshold_p=[str(v) for v in threshold],
               mpmath_version=mp.__version__,
               initial_attempt='Scientific checks completed; supplementary mpmath import failed. Installed mpmath1.3.0 in isolated coordinator cache and reran.',
               proof_review='Coordinator inspected Machin pi enclosure, decreasing alternating erf terms, positive interval products and exact sqrt floor; numerical check is supplementary.',
               elapsed_seconds=time.monotonic()-started,
               scope='Coordinator independent expected values; author solver imported only as system under test. Grouped-time development only, not held-out or publication verification.')
    args.output.write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: out[k] for k in ('passed', 'unequal_arm_release_pairs', 'unequal_arm_subject_pairs', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
