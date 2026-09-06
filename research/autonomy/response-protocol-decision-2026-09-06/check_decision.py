"""Offline source integrity, saved-record extraction and protocol-rule arithmetic.

No simulated patients and no application of stratum rules to pooled trial outcomes.
Run: python -B -X utf8 check_decision.py
"""
from pathlib import Path
from fractions import Fraction
from math import comb
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pmf(n, k, p):
    return comb(n, k) * p**k * (1-p)**(n-k)

def tail(n, k, p):
    return sum((pmf(n, j, p) for j in range(k, n+1)), Fraction())

def stage_rule(n1, r1, n, r, x1, total=None):
    if not 0 <= x1 <= n1:
        raise ValueError('invalid interim count')
    if total is not None and not x1 <= total <= x1 + n - n1:
        raise ValueError('invalid continuation count')
    if x1 <= r1:
        return 'stop_futility'
    if total is None:
        return 'continue'
    return 'reject_null' if total > r else 'do_not_reject_null'

def rejection_probability(n1, r1, n, r, p):
    return sum((pmf(n1, x, p) * tail(n-n1, max(0, r+1-x), p)
                for x in range(r1+1, n1+1)), Fraction())

def main():
    freeze = json.loads((HERE/'rules-freeze.json').read_text())
    retrieval = json.loads((HERE/'retrieval.json').read_text())
    saved = json.loads((HERE/'saved-record-read.json').read_text())
    assert sha(HERE/freeze['path']) == freeze['sha256']
    assert sha(HERE/'Prot_SAP_000.pdf') == retrieval['sha256']
    assert sha(HERE/'NCT00601003.saved.json') == saved['sha256']
    assert freeze['frozen_utc'] < saved['opened_utc']
    d = json.loads((HERE/'NCT00601003.saved.json').read_text())['study']
    measures = d['resultsSection']['outcomeMeasuresModule']['outcomeMeasures']
    matches = [(i, m) for i, m in enumerate(measures)
               if m['title'] == 'Best Radiological Response in Participants Using the RECIST Criteria']
    assert len(matches) == 1
    i, m = matches[0]
    categories = {c['title']: int(c['measurements'][0]['value'])
                  for cl in m['classes'] for c in cl['categories']}
    n = int(m['denoms'][0]['counts'][0]['value'])
    assert sum(categories.values()) == n
    flow = d['resultsSection']['participantFlowModule']
    milestones = {v['type']: int(v['achievements'][0]['numSubjects'])
                  for v in flow['periods'][0]['milestones']}
    assert milestones['STARTED'] == milestones['COMPLETED'] + milestones['NOT COMPLETED']
    out = {'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source_integrity': 'passed',
           'rules_frozen_before_saved_record_open': True,
           'outcome_pointer': f'/study/resultsSection/outcomeMeasuresModule/outcomeMeasures/{i}',
           'outcome': m,
           'pooled_categories': categories, 'reported_outcome_denominator': n,
           'pooled_CR_plus_PR': categories['Complete Response'] + categories['Partial Response'],
           'flow_milestones': milestones,
           'population_description_present': 'populationDescription' in m,
           'analyses_present': 'analyses' in m,
           'observed_outcome_groups': m['groups'],
           'stage_results_present': False,
           'decision_identifiable': False,
           'reason': 'Only one pooled response group; required stratum-specific evaluable totals, CR/PR counts and interim accrual-order outcomes are not supplied.',
           'no_real_patient_decision_computed': True,
           'protocol_arithmetic': {}}
    for name, args, p0, p1 in [('I', (19, 6, 39, 16), Fraction(3,10), Fraction(1,2)),
                                ('II', (18, 4, 33, 10), Fraction(1,5), Fraction(2,5))]:
        n1,r1,nt,r=args
        assert stage_rule(*args, r1) == 'stop_futility'
        assert stage_rule(*args, r1+1) == 'continue'
        assert stage_rule(*args, r1+1, r) == 'do_not_reject_null'
        assert stage_rule(*args, r1+1, r+1) == 'reject_null'
        assert stage_rule(*args, r1, r+1) == 'stop_futility'
        cells=0
        for x1 in range(n1+1):
            for x2 in range(nt-n1+1):
                expected = 'stop_futility' if x1 <= r1 else ('reject_null' if x1+x2 > r else 'do_not_reject_null')
                assert stage_rule(*args,x1,x1+x2) == expected
                cells+=1
        out['protocol_arithmetic'][name] = {
            'design': args, 'boundary_and_path_checks': 'passed', 'count_pairs_checked': cells,
            'null_rejection_probability': float(rejection_probability(*args,p0)),
            'alternative_rejection_probability': float(rejection_probability(*args,p1)),
            'null_stage1_futility_probability': float(1-tail(n1,r1+1,p0)),
            'scope': 'Exact design arithmetic only, not an observed trial result'}
    nt=21; p0=Fraction(1,20); alpha=Fraction(1,20)
    cutoff=next(k for k in range(nt+1) if tail(nt,k,p0)<=alpha)
    assert cutoff == 4 and tail(nt,cutoff-1,p0)>alpha
    out['protocol_arithmetic']['III'] = {
        'computed_not_quoted_rejection_cutoff': cutoff,
        'null_tail_at_3': float(tail(nt,3,p0)),
        'null_tail_at_4': float(tail(nt,4,p0)),
        'scope': 'Derived from page 18 n=21 and page 19 directional exact test; no observed stratum count available'}
    (HERE/'decision-check.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in out.items() if k!='outcome'},indent=2))

if __name__ == '__main__':
    main()
