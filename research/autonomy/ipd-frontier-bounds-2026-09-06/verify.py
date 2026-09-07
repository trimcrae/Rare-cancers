"""Independent subject-history coverage tests using prior tiny oracle fixtures."""
from fractions import Fraction as F
from itertools import combinations_with_replacement,product
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import time
import sys
import frontier

ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'ipd-bounds-development-2026-09-06'
sys.path.insert(0,str(OLD))
spec=importlib.util.spec_from_file_location('old_independent_verifier',OLD/'verify.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def inside(q,interval):
    return F(interval[0])<=q and (interval[1]=='infinity' or q<=F(interval[1]))


def prefix_states(a,b,k):
    sa=sb=F(1);u=v=F(0)
    for t in range(1,k+2):
        ya=sum(x>=t for x,e in a);yb=sum(x>=t for x,e in b)
        ea=sum(x>=t and e for x,e in a);eb=sum(x>=t and e for x,e in b)
        yield (t,ya,yb,ea,eb,sa,sb),u,v
        if t>k:break
        da=sum(x==t and e for x,e in a);db=sum(x==t and e for x,e in b)
        n=ya+yb;d=da+db
        if n:
            u+=da-F(ya*d,n)
            if n>1:v+=F(ya,n)*F(yb,n)*F(d*(n-d),n-1)
        if ya:sa*=1-F(da,ya)
        if yb:sb*=1-F(db,yb)


def check_witnesses(rel,result):
    for label,w in result['witnesses'].items():
        records={}
        for arm in ['a','b']:
            rows=[]
            for t,(d,c) in enumerate(w[arm],1):rows.extend([(t,1)]*d+[(t,0)]*c)
            assert old.summarize(rows,len(rel['grid']),rel['probability_digits'],list(map(int,rel[arm]['risk_counts'])))==rel[arm]
            records[arm]=rows
        q=old.subject_score(records['a'],records['b']);assert str(q)==w['q']
        p=math.erfc(math.sqrt(float(q)/2))
        if label=='stable_reject':assert p<.05
        if label=='stable_nonreject':assert p>=.05
    assert result['nonempty_proven']==bool(result['witnesses'])
    if result['decision'].startswith('stable_'):assert result['nonempty_proven']


def main():
    start=time.perf_counter()
    # Same 56 multisets used by the committed oracle checker. Coarse release design
    # is chosen beforehand to exercise merging; these are validation cases, not new
    # scientific simulation or a search for a favorable certificate.
    rows=list(combinations_with_replacement(list(product(range(1,4),[0,1])),3))
    groups={}
    for records in rows:
        key=json.dumps(old.summarize(records,3,0,[1]),sort_keys=True)
        groups.setdefault(key,[]).append(records)
    checks=0;coverage_checks=0;active_stops=0;merges=0;no_witness_tests=0
    for key,aa in groups.items():
        rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],'probability_digits':0,'a':json.loads(key),'b':json.loads(key)}
        expected=[(a,b,old.subject_score(a,b)) for a in aa for b in aa]
        for limit in [0,1,2,7,100000]:
            result=frontier.solve(rel,seconds=30,max_transitions=limit,max_states=10000,witness_seconds=0,debug=True)
            check_witnesses(rel,result);merges+=result['merged_histories'];active_stops+=result['active_parent_retained']
            if not result['nonempty_proven']:
                assert not result['decision'].startswith('stable_');no_witness_tests+=1
            regions={}
            for region in result['regions']:
                vals=region['key'];rkey=tuple(map(int,vals[:5]))+tuple(map(F,vals[5:]))
                regions.setdefault(rkey,[]).append(tuple(map(F,region['box'])))
            for a,b,q in expected:
                assert inside(q,result['q_outer'])
                covered=False
                for rkey,u,v in prefix_states(a,b,3):
                    if any(lo<=u<=hi and vlo<=v<=vhi for lo,hi,vlo,vhi in regions.get(rkey,[])):covered=True;break
                assert covered,('lost history',limit,a,b,result)
                coverage_checks+=1
            if limit==100000:assert result['complete_traversal']
            checks+=1
    # Direct outward-box properties, including impossible coordinate combinations.
    boxes=[(F(-2),F(3),F(0),F(4)),(F(2),F(3),F(1),F(4)),
           (F(0),F(0),F(0),F(4)),(F(-2),F(3),F(0),F(0)),(F(2),F(3),F(0),F(0))]
    for box in boxes:
        lo,hi=frontier.q_box(*box)
        for unum in range(-8,13):
            u=F(unum,4)
            for vnum in range(17):
                v=F(vnum,4)
                if not(box[0]<=u<=box[1] and box[2]<=v<=box[3]):continue
                if v==0 and u!=0:continue # Not a possible ordinary-logrank pair.
                q=F(0) if v==0 else u*u/v
                assert lo<=q and (hi is None or q<=hi)
    assert frontier.q_box(F(2),F(3),F(0),F(0))==(F(0),None)
    # Impossible release never becomes a vacuous certificate; explicit time/state
    # stops retain coverage, and a zero-event partial bound without a witness cannot certify.
    zero=old.summarize([(1,0),(2,0),(3,0)],3,0,[1])
    zrel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],'probability_digits':0,'a':zero,'b':zero}
    no_witness=frontier.solve(zrel,max_transitions=0,witness_seconds=0)
    assert no_witness['q_outer']==['0','0'] and no_witness['decision']=='unresolved_no_witness'
    with_witness=frontier.solve(zrel,max_transitions=0)
    assert not with_witness['complete_traversal'] and with_witness['decision']=='stable_nonreject'
    for kwargs in [{'seconds':0},{'max_states':0}]:
        stopped=frontier.solve(zrel,**kwargs);assert not stopped['complete_traversal'] and stopped['active_parent_retained']
    bad=json.loads(json.dumps(zrel));bad['a']['risk_counts']['1']=2
    infeasible=frontier.solve(bad);assert infeasible['complete_traversal'] and infeasible['decision']=='infeasible_release'
    # Existing oracle interval containment; neither hidden truth nor oracle scores
    # were supplied to frontier.run_existing, which reads released summaries only.
    observed=json.loads((ROOT/'results.json').read_text())
    oracle={x['case_id']:x['result'] for x in json.loads((OLD/'development-results.json').read_text())['cases']}
    releases={x['case_id']:x['release'] for name in ['development-releases.json','stress-releases.json'] for x in json.loads((OLD/name).read_text())['cases']}
    comparisons=[]
    for item in observed['cases']:
        r=item['result'];check_witnesses(releases[item['case_id']],r)
        if item['case_id'] in oracle:
            o=oracle[item['case_id']];assert all(inside(F(q),r['q_outer']) for q in o['q_outer'])
            comparisons.append({'case_id':item['case_id'],'oracle_q_outer':o['q_outer'],'frontier_q_outer':r['q_outer'],'contained':True})
    assert len(comparisons)==18 and len(observed['cases'])==22
    output={'passed':True,'scope':'Worker independent subject-history coverage/arithmetic; coordinator review separate.',
            'existing_tiny_multisets':len(rows),'tiny_release_groups':len(groups),'forced_and_complete_runs':checks,
            'individual_history_coverage_checks':coverage_checks,'active_parent_stop_checks':active_stops,
            'merge_operations_exercised':merges,'no_witness_no_certificate_checks':no_witness_tests,
            'zero_variance_and_impossible_box_checked':True,'time_and_state_limit_checked':True,
            'partial_zero_event_certificate_requires_witness_checked':True,'infeasible_checked':True,
            'oracle_comparisons':comparisons,'all_returned_witnesses_independently_verified':True,
            'elapsed_seconds':time.perf_counter()-start}
    (ROOT/'verification.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='oracle_comparisons'}))


if __name__=='__main__':main()
