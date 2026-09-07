"""Recompute query partitions from subject-record scores, before reading true answer."""
from fractions import Fraction as F
import json
import math
import time
from pathlib import Path
import bounds
from verify import subject_score,summarize

ROOT=Path(__file__).resolve().parent


def decision(lo,hi):
    if lo>F('3.84145882069413'):return 'stable_reject'
    if hi<=F('3.84145882069412'):return 'stable_nonreject'
    return 'unresolved'


def main():
    start=time.perf_counter();case='n80-hazard-b-0.18-sparse'
    fixture=next(x for x in json.loads((ROOT/'development-releases.json').read_text())['cases'] if x['case_id']==case)
    rel=fixture['release']
    result=next(x['result'] for x in json.loads((ROOT/'development-results.json').read_text())['cases'] if x['case_id']==case)
    candidates={}
    for arm in ['a','b']:
        paths,meta=bounds.enumerate_arm(rel,arm);assert meta['complete']
        rows=[]
        for path in paths:
            records=tuple((t,e) for t,(d,c) in enumerate(path,1) for e in [0,1] for _ in range(d if e else c))
            assert summarize(records,6,2,list(map(int,rel[arm]['risk_counts'])))==rel[arm]
            rows.append(records)
        candidates[arm]=rows
    scores=[(a,b,subject_score(a,b)) for a in candidates['a'] for b in candidates['b']]
    opts=[]
    for arm in ['a','b']:
        for t in rel['grid']:
            if str(t) in rel[arm]['risk_counts']:continue
            groups={}
            for a,b,q in scores:
                records=a if arm=='a' else b
                risk=sum(x>=t for x,e in records)
                groups.setdefault(risk,[]).append(q)
            if len(groups)<2:continue
            outcomes=[{'risk':risk,'pairs':len(qs),'q_outer':[str(min(qs)),str(max(qs))],
                       'decision':decision(min(qs),max(qs))} for risk,qs in sorted(groups.items())]
            opts.append({'arm':arm,'time':t,'outcomes':outcomes,
                         'worst_unresolved_pairs':max(o['pairs'] if o['decision']=='unresolved' else 0 for o in outcomes),
                         'worst_pairs':max(o['pairs'] for o in outcomes)})
    assert opts==result['query_options']
    chosen=min(opts,key=lambda o:(o['worst_unresolved_pairs'],o['worst_pairs'],o['arm'],o['time']))
    assert chosen==result['selected_query']
    # Only after selection verification inspect original answer and rerun narrowed release.
    original=next(x for x in json.loads((ROOT/'development-truth.json').read_text())['cases'] if x['case_id']==fixture['parent_case_id'])
    answer=sum(t>=chosen['time'] for t,e in original[chosen['arm']])
    narrowed=json.loads(json.dumps(rel));narrowed[chosen['arm']]['risk_counts'][str(chosen['time'])]=answer
    after=bounds.solve(narrowed,queries=False)
    outcome=next(o for o in chosen['outcomes'] if o['risk']==answer)
    assert after['complete'] and after['q_outer']==outcome['q_outer'] and after['decision']==outcome['decision']
    assert after['enumerated_pairs']==outcome['pairs']
    out={'passed':True,'synthetic':True,'case_id':case,'subject_pair_scores':len(scores),
         'query_options_independently_recomputed':len(opts),'selected_query':chosen,
         'original_answer_read_after_selection':answer,'conditioned_pairs':after['enumerated_pairs'],
         'conditioned_decision':after['decision'],'conditioned_p_extrema_approx':after['p_extrema_approx'],
         'scope':'Independent subject-score and query-group implementation; production enumeration supplies paths already exhaustively tested on tiny models. One development example, no query-policy superiority estimate.',
         'elapsed_seconds':time.perf_counter()-start}
    (ROOT/'query-verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='selected_query'}))


if __name__=='__main__':main()
