"""Independent subject-record coverage and exact suffix-cache verification."""
from fractions import Fraction as F
from itertools import combinations_with_replacement,product
from pathlib import Path
import importlib.util
import json
import math
import sys
import time
import suffix
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'ipd-bounds-development-2026-09-06'
sys.path.insert(0,str(OLD))
spec=importlib.util.spec_from_file_location('subject_verifier',OLD/'verify.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def inside(q,interval):return F(interval[0])<=q and (interval[1]=='infinity' or q<=F(interval[1]))


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


def compatible_suffixes(rel,name,key):
    # Enumerate all remaining subject-category multisets, independently of solver
    # transitions/pruning. At most three remaining subjects in these tiny checks.
    t,y,e,s=key;k=len(rel['grid']);r=rel[name];digits=rel['probability_digits'];out=set()
    if t>k:return {()} if y==e==0 else set()
    categories=list(product(range(t,k+1),[0,1]))
    for rows in combinations_with_replacement(categories,y):
        if sum(event for time,event in rows)!=e:continue
        current=s;path=[];valid=True
        for time in range(t,k+1):
            risk=sum(x>=time for x,event in rows);d=sum(x==time and event for x,event in rows)
            c=sum(x==time and not event for x,event in rows)
            if str(time) in r['risk_counts'] and risk!=r['risk_counts'][str(time)]:valid=False;break
            if risk:current*=1-F(d,risk)
            scaled=current*10**digits;rounded=(2*scaled.numerator+scaled.denominator)//(2*scaled.denominator)
            if rounded!=F(r['survival_rounded'][time-1])*10**digits:valid=False;break
            path.append((d,c))
        if valid:out.add(tuple(path))
    return out


def check_cache(rel,result,memo,counts):
    for name,arm in result['arms'].items():
        assert arm['cache_unknown_entries']==0
        assert arm['cache_entries']==arm['proved_true']+arm['proved_false']
        for entry in arm['cache']:
            vals=entry['key'];key=tuple(map(int,vals[:3]))+(F(vals[3]),)
            lookup=(json.dumps(rel[name],sort_keys=True),key)
            if lookup not in memo:memo[lookup]=compatible_suffixes(rel,name,key)
            expected=memo[lookup]
            if entry['status']=='FALSE':assert not expected,(name,key,expected);counts['false_cache_checks']+=1
            else:
                assert entry['status']=='TRUE'
                assert tuple(map(tuple,entry['continuation'])) in expected,(name,key,entry,expected)
                counts['true_cache_checks']+=1
    if result['reason'] and result['reason'].startswith('forced_suffix_'):
        context=result['stop_context'];assert isinstance(context,dict)
        detail=context['detail'];arm=result['arms'][detail['arm']]
        # The frame interrupted at entry/after successor has not proved itself false.
        assert not any(e['key']==detail['key'] and e['status']=='FALSE' for e in arm['cache'])
        assert arm['unknown_returns']>0
        counts['forced_suffix_unknown_checks']+=1


def main():
    start=time.perf_counter();rows=list(combinations_with_replacement(list(product(range(1,4),[0,1])),3))
    groups={}
    for records in rows:
        key=json.dumps(old.summarize(records,3,0,[1]),sort_keys=True)
        groups.setdefault(key,[]).append(records)
    counts={'runs':0,'history_coverage_checks':0,'false_cache_checks':0,'true_cache_checks':0,
            'forced_suffix_unknown_checks':0,'active_parent_stops':0,'initial_region_stops':0,
            'joint_children_and_parent_stops':0,'pruned_transitions':0,'no_witness_checks':0}
    memo={};stop_reasons={};force_samples=[]
    settings=[{},*({'max_work':x} for x in [0,1,2,7,40]),
              {'force':{'suffix_entry':3}},{'force':{'suffix_after_successor':2}},
              {'force':{'suffix_entry':3},'initial_witness':False},
              {'force':{'suffix_after_successor':2},'initial_witness':False},
              {'force':{'joint_after_successor':1}},
              {'max_transitions':0,'initial_witness':False}, {'max_states':0},
              {'max_cache_entries':0},{'max_memory_bytes':0},{'seconds':0}]
    for key,aa in groups.items():
        rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],'probability_digits':0,'a':json.loads(key),'b':json.loads(key)}
        expected=[(a,b,old.subject_score(a,b)) for a in aa for b in aa]
        for opts in settings:
            result=suffix.solve(rel,debug=True,**opts)
            check_witnesses(rel,result);check_cache(rel,result,memo,counts)
            assert result['work_units']==sum(result['work_counts'].values())
            assert result['work_units']<=result['limits']['max_work_units']
            reason=result['reason'];stop_reasons[str(reason)]=stop_reasons.get(str(reason),0)+1
            if reason:
                if result['active_parent_retained']:counts['active_parent_stops']+=1
                else:counts['initial_region_stops']+=1
            if result['active_parent_retained'] and result['retained_children']:counts['joint_children_and_parent_stops']+=1
            if not result['nonempty_proven']:
                assert not result['decision'].startswith('stable_');counts['no_witness_checks']+=1
            counts['pruned_transitions']+=sum(a['pruned_transitions'] for a in result['arms'].values())
            regions={}
            for region in result['regions']:
                vals=region['key'];rkey=tuple(map(int,vals[:5]))+tuple(map(F,vals[5:]))
                regions.setdefault(rkey,[]).append(tuple(map(F,region['box'])))
            for a,b,q in expected:
                assert inside(q,result['q_outer'])
                assert any(any(lo<=u<=hi and vlo<=v<=vhi for lo,hi,vlo,vhi in regions.get(rkey,[]))
                           for rkey,u,v in prefix_states(a,b,3)),('lost history',opts,a,b,result)
                counts['history_coverage_checks']+=1
            if not opts:assert result['complete_traversal']
            if result['reason'] in ['forced_suffix_entry','forced_suffix_after_successor'] and len(force_samples)<8:
                force_samples.append({'options':opts,'reason':reason,'stop_context':result['stop_context'],
                                      'retained_regions':len(result['regions']),'arms':{n:{k:v for k,v in a.items() if k!='cache'} for n,a in result['arms'].items()}})
            counts['runs']+=1
    assert counts['forced_suffix_unknown_checks'] and counts['joint_children_and_parent_stops']
    assert counts['false_cache_checks'] and counts['pruned_transitions']
    # Exhaustive interrupted recursion on the same tiny release groups: every
    # after-successor hook, including false children and partially explored lists.
    partial_false=0
    for key in groups:
        rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],'probability_digits':0,'a':json.loads(key),'b':json.loads(key)}
        full=suffix.solve(rel,debug=True)
        for stop_at in range(1,full['hook_counts']['suffix_after_successor']+1):
            stopped=suffix.solve(rel,debug=True,force={'suffix_after_successor':stop_at})
            check_cache(rel,stopped,memo,counts)
            assert stopped['reason']=='forced_suffix_after_successor'
            if stopped['stop_context']['detail']['child_false']:partial_false+=1
            # Every actual pair still covered through prefix-region membership.
            regions={}
            for region in stopped['regions']:
                vals=region['key'];rkey=tuple(map(int,vals[:5]))+tuple(map(F,vals[5:]))
                regions.setdefault(rkey,[]).append(tuple(map(F,region['box'])))
            for a in groups[key]:
                for b in groups[key]:
                    assert any(any(lo<=u<=hi and vlo<=v<=vhi for lo,hi,vlo,vhi in regions.get(rkey,[]))
                               for rkey,u,v in prefix_states(a,b,3))
                    counts['history_coverage_checks']+=1
            counts['runs']+=1
    assert partial_false>0
    zero=old.summarize([(1,0),(2,0),(3,0)],3,0,[1])
    zrel={'schema':'discrete-km-release-v1','synthetic':True,'grid':[1,2,3],'probability_digits':0,'a':zero,'b':zero}
    nw=suffix.solve(zrel,max_transitions=0,initial_witness=False)
    assert nw['q_outer']==['0','0'] and nw['decision']=='unresolved_no_witness'
    yes=suffix.solve(zrel,max_transitions=0)
    assert yes['decision']=='stable_nonreject' and not yes['complete_traversal'];check_witnesses(zrel,yes)
    bad=json.loads(json.dumps(zrel));bad['a']['risk_counts']['1']=2
    empty=suffix.solve(bad);assert empty['complete_traversal'] and empty['decision']=='infeasible_release'
    # Explicit tri-state API: stop=>None, false=>False, terminal true=>().
    suffix.tracemalloc.start()
    b=suffix.Budget(time.perf_counter(),30,0,1000,2**30,None);arm=suffix.Arm(zrel,'a',b)
    unknown,reason=arm.query((1,3,0,F(1)));assert unknown is None and reason=='work_limit' and not arm.cache
    b.max_work=1000
    false,reason=arm.query((1,2,0,F(1)));assert false is False and reason is None
    true,reason=arm.query((4,0,0,F(1)));assert true==() and true is not False and reason is None
    suffix.tracemalloc.stop()
    # Compare only to saved oracle outputs after all inference runs finish.
    observed=json.loads((ROOT/'results.json').read_text())
    original={x['case_id']:x['result'] for x in json.loads((OLD/'development-results.json').read_text())['cases']}
    releases={x['case_id']:x['release'] for name in ['development-releases.json','stress-releases.json'] for x in json.loads((OLD/name).read_text())['cases']}
    comparisons=[]
    for item in observed['cases']:
        r=item['result'];check_witnesses(releases[item['case_id']],r)
        assert r['work_units']==sum(r['work_counts'].values())
        if item['case_id'] in original:
            o=original[item['case_id']];assert all(inside(F(q),r['q_outer']) for q in o['q_outer'])
            comparisons.append({'case_id':item['case_id'],'oracle_q_outer':o['q_outer'],'suffix_q_outer':r['q_outer'],'contained':True})
    assert len(comparisons)==18 and len(observed['cases'])==22
    out={'passed':True,'scope':'Worker independently implemented subject enumeration; coordinator verification separate.',
         'existing_tiny_subject_multisets':len(rows),'release_groups':len(groups),**counts,
         'distinct_independent_suffix_enumerations':len(memo),'after_false_successor_interruptions':partial_false,
         'stop_reasons':stop_reasons,'forced_stop_samples':force_samples,'oracle_comparisons':comparisons,
         'zero_variance_nonemptiness_infeasible_checked':True,'explicit_unknown_false_true_semantics_checked':True,
         'all_emitted_witnesses_independently_compatible':True,'elapsed_seconds':time.perf_counter()-start}
    (ROOT/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['forced_stop_samples','oracle_comparisons']}))


if __name__=='__main__':main()
