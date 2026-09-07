"""Independent subject enumeration for suffix pruning and interrupted coverage."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import time
from fractions import Fraction as F
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def continuations(arm, key, k, digits):
    """Enumerate labelled-subject multisets, independent of solver transitions."""
    t, y, e = map(int, key[:3])
    s = F(key[3])
    choices = list(itertools.product(range(t, k+1), (0, 1)))
    valid = set()
    if t > k:
        return {()} if y == e == 0 else set()
    for rows in itertools.combinations_with_replacement(choices, y):
        if sum(event for _, event in rows) != e:
            continue
        survival = s
        path = []
        good = True
        for j in range(t, k+1):
            risk = sum(exit_time >= j for exit_time, _ in rows)
            d = sum(exit_time == j and event for exit_time, event in rows)
            c = sum(exit_time == j and not event for exit_time, event in rows)
            if str(j) in arm['risk_counts'] and risk != arm['risk_counts'][str(j)]:
                good = False
                break
            if risk:
                survival *= F(risk-d, risk)
            z = survival * 10**digits
            integer, rest = divmod(z.numerator, z.denominator)
            integer += 2*rest >= z.denominator
            if F(integer, 10**digits) != F(arm['survival_rounded'][j-1]):
                good = False
                break
            path.append((d, c))
        if good:
            valid.add(tuple(path))
    return valid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    solver = load('suffix_checked', args.source)
    helpers = load('subject_checks', Path(__file__).resolve().parent.parent / 'ipd-frontier-bounds-2026-09-06/coordinator_check.py')
    settings = ([dict(max_work=n) for n in (0, 1, 5, 20, 80, 200000)]
                + [dict(max_cache_entries=n) for n in (0, 1, 5)]
                + [dict(max_transitions=0), dict(max_states=1), dict(seconds=0), dict(max_memory_bytes=1)]
                + [dict(force={hook: n}) for hook in ('suffix_entry', 'suffix_after_successor', 'joint_after_successor') for n in (1, 3, 10)]
                + [dict(initial_witness=False)])
    categories = list(itertools.product((1, 2, 3), (0, 1)))
    records = [list(itertools.combinations_with_replacement(categories, n)) for n in (2, 1)]
    counts = dict(release_budget_checks=0, history_coverage_checks=0, false_cache_checks=0,
                  true_cache_checks=0, complete=0, partial=0, no_witness=0, active_parent=0)
    independently_enumerated = {}
    for digits, risks in ((0, (1,)), (1, (1, 2))):
        groups = []
        for rows_list in records:
            group = {}
            for rows in rows_list:
                key = json.dumps(helpers.arm_summary(rows, 3, digits, risks), sort_keys=True)
                group.setdefault(key, []).append(rows)
            groups.append(group)
        for ak, aa in groups[0].items():
            for bk, bb in groups[1].items():
                release = dict(schema='discrete-km-release-v1', synthetic=True, grid=[1,2,3],
                               probability_digits=digits, a=json.loads(ak), b=json.loads(bk))
                histories = [helpers.history(a, b, 3) for a in aa for b in bb]
                for limits in settings:
                    out = solver.solve(release, debug=True, **limits)
                    counts['release_budget_checks'] += 1
                    counts['complete' if out['complete_traversal'] else 'partial'] += 1
                    counts['no_witness'] += not out['nonempty_proven']
                    counts['active_parent'] += out['active_parent_retained']
                    assert out['q_outer'] is not None
                    lo, hi = out['q_outer']
                    regions = [(tuple(map(F, r['key'])), tuple(map(F, r['box']))) for r in out['regions']]
                    for states, q in histories:
                        assert F(lo) <= q and (hi == 'infinity' or q <= F(hi))
                        assert any(key == rkey and box[0] <= u <= box[1] and box[2] <= v <= box[3]
                                   for key,u,v in states for rkey,box in regions), (release, limits)
                        counts['history_coverage_checks'] += 1
                    if not out['nonempty_proven']:
                        assert out['decision'] == 'unresolved_no_witness'
                    for name in ('a', 'b'):
                        for entry in out['arms'][name]['cache']:
                            cachekey = (json.dumps(release[name], sort_keys=True), digits, tuple(entry['key']))
                            if cachekey not in independently_enumerated:
                                independently_enumerated[cachekey] = continuations(release[name], entry['key'], 3, digits)
                            valid = independently_enumerated[cachekey]
                            if entry['status'] == 'FALSE':
                                assert not valid, (release[name], entry)
                                counts['false_cache_checks'] += 1
                            else:
                                assert tuple(map(tuple, entry['continuation'])) in valid
                                counts['true_cache_checks'] += 1
    assert hashlib.sha256(args.source.read_bytes()).hexdigest() == digest
    result = dict(passed=True, source_sha256=digest, **counts,
                  independent_suffix_enumerations=len(independently_enumerated), settings=settings,
                  elapsed_seconds=time.monotonic()-start,
                  scope='Unequal tiny arms; independent subject-history enumeration, every retained frontier, exhaustive false-cache and real true-continuation checks under work/cache/memory/time/state/transition and recursive forced stops. No practical utility or publication certification.')
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
