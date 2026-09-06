"""Independent subject-history coverage checks for interrupted frontier bounds."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import time
from fractions import Fraction as F
from pathlib import Path


def arm_summary(rows, k, digits, risk_times):
    s = F(1)
    rounded = []
    for t in range(1, k+1):
        y = sum(x >= t for x, e in rows)
        d = sum(x == t and e for x, e in rows)
        if y:
            s *= F(y-d, y)
        z = s * 10**digits
        integer, rest = divmod(z.numerator, z.denominator)
        integer += 2*rest >= z.denominator
        rounded.append(str(integer) if not digits else f'{integer//10**digits}.{integer%10**digits:0{digits}d}')
    return dict(n=len(rows), total_events=sum(e for x, e in rows), survival_rounded=rounded,
                risk_counts={str(t): sum(x >= t for x, e in rows) for t in risk_times})


def history(a, b, k):
    ua = va = F(0)
    sa = sb = F(1)
    states = []
    for t in range(1, k+2):
        ya, yb = [sum(x >= t for x, e in rows) for rows in (a, b)]
        ea, eb = [sum(x >= t and e for x, e in rows) for rows in (a, b)]
        states.append(((F(t), F(ya), F(yb), F(ea), F(eb), sa, sb), ua, va))
        da, db = [sum(x == t and e for x, e in rows) for rows in (a, b)]
        if ya:
            sa *= F(ya-da, ya)
        if yb:
            sb *= F(yb-db, yb)
        y, d = ya+yb, da+db
        if y:
            ua += da - F(d*ya, y)
        if y > 1:
            va += F(d*(y-d), y-1)*F(ya,y)*F(yb,y)
    assert va or ua == 0
    return states, ua*ua/va if va else F(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    started = time.monotonic()
    source = args.source/'frontier.py'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location('frontier_under_test', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    categories = list(itertools.product((1, 2, 3), (0, 1)))
    records = [list(itertools.combinations_with_replacement(categories, n)) for n in (2, 1)]
    settings = [dict(max_transitions=v) for v in (0, 1, 5, 30, 100000)] + [dict(max_states=1), dict(seconds=0), dict(max_transitions=0, witness_seconds=0)]
    checks = coverage_checks = complete = partial = no_witness = active = 0
    for digits, risks in ((0, (1,)), (1, (1, 2))):
        groups = []
        for rows_list in records:
            group = {}
            for rows in rows_list:
                key = json.dumps(arm_summary(rows, 3, digits, risks), sort_keys=True)
                group.setdefault(key, []).append(list(rows))
            groups.append(group)
        for ak, aa in groups[0].items():
            for bk, bb in groups[1].items():
                rel = dict(schema='discrete-km-release-v1', synthetic=True, grid=[1,2,3],
                           probability_digits=digits, a=json.loads(ak), b=json.loads(bk))
                histories = [history(a,b,3) for a in aa for b in bb]
                for limits in settings:
                    result = module.solve(rel, debug=True, **limits)
                    checks += 1
                    if result['complete_traversal']:
                        complete += 1
                    else:
                        partial += 1
                    active += result['active_parent_retained']
                    no_witness += not result['nonempty_proven']
                    assert result['q_outer'] is not None
                    lo, hi = result['q_outer']
                    lower = F(lo)
                    upper = None if hi == 'infinity' else F(hi)
                    regions = [(tuple(map(F,r['key'])), list(map(F,r['box']))) for r in result['regions']]
                    for hist, q in histories:
                        assert lower <= q and (upper is None or q <= upper)
                        covered = any(key == region_key and box[0] <= u <= box[1] and box[2] <= v <= box[3]
                                      for key,u,v in hist for region_key,box in regions)
                        assert covered, (rel, limits, hist, result)
                        coverage_checks += 1
                    if result['decision'].startswith('stable'):
                        assert result['nonempty_proven']
                    if not result['nonempty_proven']:
                        assert result['decision'] == 'unresolved_no_witness'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest, 'Source changed during verification; rerun against settled source'
    out = dict(passed=True, source_sha256=digest, release_budget_checks=checks,
               actual_subject_history_coverage_checks=coverage_checks, complete_runs=complete,
               partial_runs=partial, active_parent_retention_runs=active, nonemptiness_unproved_runs=no_witness,
               limits=settings, elapsed_seconds=time.monotonic()-started,
               scope='Coordinator independently enumerated unequal-arm subject histories and checked each remains inside an actual retained structural-state U/V rectangle, including forced interruption; no held-out utility claim.')
    args.output.write_text(json.dumps(out,indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(out))


if __name__ == '__main__':
    main()
