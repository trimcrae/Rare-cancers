"""Independent exhaustive multiset filter and subject-level arithmetic.

Imports production functions only as systems under test. Does not use production
curve generator, rounding function, path score, or classifier for expected results.
"""
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_HALF_UP
from itertools import combinations_with_replacement,product
import hashlib
import json
import math
import time
from pathlib import Path
import bounds

ROOT=Path(__file__).resolve().parent


def summarize(rows,k,digits,risk_times):
    surv=F(1);curve=[]
    for t in range(1,k+1):
        risk=len([r for r in rows if r[0]>=t]);events=len([r for r in rows if r==(t,1)])
        if risk:surv*=1-F(events,risk)
        # Independent Decimal rounding; 100 digits far exceeds tiny-case rational
        # denominators here. Halfway rational cases use exact integer comparison.
        z=surv*10**digits;integer=z.numerator//z.denominator
        if z-integer>=F(1,2):integer+=1
        with localcontext() as ctx:
            ctx.prec=100
            curve.append(format(Decimal(integer)/Decimal(10**digits),f'.{digits}f'))
    return {'n':len(rows),'total_events':sum(e for t,e in rows),'survival_rounded':curve,
            'risk_counts':{str(t):len([1 for x,e in rows if x>=t]) for t in risk_times}}


def subject_score(a,b):
    # Sum per-event-time observed-minus-expected using subject records directly.
    u=F(0);variance=F(0)
    for t in sorted(set(x for x,e in a+b if e)):
        risk_a=[r for r in a if r[0]>=t];risk_b=[r for r in b if r[0]>=t]
        d_a=len([r for r in a if r==(t,1)]);d_b=len([r for r in b if r==(t,1)])
        na=len(risk_a);nb=len(risk_b);n=na+nb;d=d_a+d_b
        u+=d_a-F(na,n)*d
        if n>1:variance+=F(d*(n-d),n-1)*F(na,n)*F(nb,n)
    if variance==0:
        assert u==0;return F(0)
    return u**2/variance


def path(rows,k):
    return tuple((rows.count((t,1)),rows.count((t,0))) for t in range(1,k+1))


def main():
    start=time.perf_counter();all_rows=list(combinations_with_replacement(list(product(range(1,4),[0,1])),3))
    total_groups=0;total_release_pairs=0;total_subject_pairs=0;has_ties=False;has_both_censored=False
    for digits in [0,1]:
        for risk_times in [[1],[1,2]]:
            groups={}
            for rows in all_rows:
                key=json.dumps(summarize(rows,3,digits,risk_times),sort_keys=True)
                groups.setdefault(key,[]).append(rows)
            total_groups+=len(groups)
            for key,compatible in groups.items():
                rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],
                     'probability_digits':digits,'a':json.loads(key),'b':json.loads(key)}
                accepted,meta=bounds.enumerate_arm(rel,'a')
                assert meta['complete']
                assert set(accepted)=={path(rows,3) for rows in compatible}
            # Every possible pair of n=3,K=3 datasets for this release design.
            for ka,aa in groups.items():
                for kb,bb in groups.items():
                    rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],
                         'probability_digits':digits,'a':json.loads(ka),'b':json.loads(kb)}
                    qs=[]
                    for a in aa:
                        for b in bb:
                            qs.append(subject_score(a,b));total_subject_pairs+=1
                            has_ties|=any(sum(x==t and e for x,e in a+b)>1 for t in [1,2,3])
                            has_both_censored|=any(e==0 for x,e in a) and any(e==0 for x,e in b)
                    result=bounds.solve(rel,queries=False)
                    assert result['complete']
                    assert list(map(F,result['q_outer']))==[min(qs),max(qs)]
                    total_release_pairs+=1
    # Explicit endpoint, no-event, infeasible, and exhausted-budget behavior.
    assert bounds.rounded_integer(F(1,8),2)==13
    assert bounds.rounded_integer(F(124999,1000000),2)==12
    z=[(1,0),(2,0),(3,0)]
    arm=summarize(z,3,2,[1])
    rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],'probability_digits':2,'a':arm,'b':arm}
    zero=bounds.solve(rel);assert zero['complete'] and zero['q_outer']==['0','0'] and zero['decision']=='stable_nonreject'
    failures=[]
    for kwargs in [{'max_nodes':0},{'max_paths':1},{'seconds':0},{'max_pairs':1}]:
        result=bounds.solve(rel,**kwargs)
        assert result['decision']=='unresolved' and not result['complete'] and result['q_outer']==['0','infinity'] and result['p_outer']==[0,1]
        failures.append({'settings':kwargs,'reason':result['reason']})
    bad=json.loads(json.dumps(rel));bad['a']['risk_counts']['1']=2
    infeasible=bounds.solve(bad)
    assert infeasible['complete'] and infeasible['decision']=='infeasible_release'
    # Independently evaluate actual moderate development hidden rows after solving.
    fixtures=json.loads((ROOT/'development-releases.json').read_text())
    truth={x['case_id']:x for x in json.loads((ROOT/'development-truth.json').read_text())['cases']}
    results={x['case_id']:x['result'] for x in json.loads((ROOT/'development-results.json').read_text())['cases']}
    checked=[];scipy_comparisons=[]
    try:
        import sys
        sys.path.insert(0,'C:/Projects/EMC-Research/.cache/python-deps')
        import scipy
        from scipy.stats import CensoredData,logrank
    except ImportError:scipy=None
    for fixture in fixtures['cases']:
        true=truth[fixture['parent_case_id']];rel=fixture['release'];r=results[fixture['case_id']]
        a=list(map(tuple,true['a']));b=list(map(tuple,true['b']));q=subject_score(a,b)
        assert str(q)==true['true_q']
        for arm,rows in [('a',a),('b',b)]:
            assert summarize(rows,6,2,list(map(int,rel[arm]['risk_counts'])))==rel[arm]
        contained=None
        if r['complete']:
            lo,hi=map(F,r['q_outer']);contained=lo<=q<=hi;assert contained
            actual_p=math.erfc(math.sqrt(float(q)/2))
            if r['decision']=='stable_reject':assert actual_p<.05
            if r['decision']=='stable_nonreject':assert actual_p>=.05
            # Every reported endpoint witness must reproduce the release and score.
            for field,expected in [('q_min',lo),('q_max',hi)]:
                wa=[];wb=[]
                for arm,out in [('a',wa),('b',wb)]:
                    for t,(d,c) in enumerate(r['witnesses'][field][arm],1):out.extend([(t,1)]*d+[(t,0)]*c)
                    assert summarize(out,6,2,list(map(int,rel[arm]['risk_counts'])))==rel[arm]
                assert subject_score(wa,wb)==expected
        if scipy:
            data=[CensoredData(uncensored=[t for t,e in rows if e],right=[t for t,e in rows if not e]) for rows in [a,b]]
            p=float(logrank(*data).pvalue);expected=math.erfc(math.sqrt(float(q)/2))
            assert math.isclose(p,expected,abs_tol=2e-14)
            scipy_comparisons.append(abs(p-expected))
        checked.append({'case_id':fixture['case_id'],'true_q':str(q),'true_p_approx':math.erfc(math.sqrt(float(q)/2)),
                        'complete':r['complete'],'decision':r['decision'],'original_contained':contained})
    proof=bounds.threshold_proof()
    result={'passed':True,'synthetic':True,'scope':'Worker independent multiset filter and subject-level arithmetic; production enumerator is system under test. No independent external review claimed.',
            'tiny_subject_multisets':len(all_rows),'release_designs':4,'unique_arm_release_groups':total_groups,
            'tiny_release_pair_checks':total_release_pairs,'tiny_subject_pair_checks':total_subject_pairs,
            'tied_events_exercised':has_ties,'both_arm_censoring_exercised':has_both_censored,
            'budget_failures':failures,'infeasible_release_checked':True,'zero_variance_checked':True,
            'threshold_proof_verified':proof['verified'],'development_checks':checked,
            'scipy_version':None if scipy is None else scipy.__version__,
            'scipy_comparisons':len(scipy_comparisons),'max_scipy_p_discrepancy':max(scipy_comparisons,default=None),
            'elapsed_seconds':time.perf_counter()-start}
    (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
