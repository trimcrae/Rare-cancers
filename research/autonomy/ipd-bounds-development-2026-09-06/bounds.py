"""Exact synthetic discrete-KM compatibility; see protocol.md for model limits.

No statistical certificate is returned after incomplete traversal. Floating p values
are approximations for display. Rational Q and a rigorously enclosed threshold
determine decisions. Standard library only.
"""
from fractions import Fraction as F
from math import erfc, sqrt, isqrt
import argparse
import json
import time
from pathlib import Path

Q_LO = F('3.84145882069412')
Q_HI = F('3.84145882069413')


def alternating_atan(x, terms=100):
    s = sum(((-1)**k*x**(2*k+1)/F(2*k+1) for k in range(terms)), F(0))
    nxt = (-1)**terms*x**(2*terms+1)/F(2*terms+1)
    return min(s,s+nxt), max(s,s+nxt)


def sqrt_enclosure(x, digits=60):
    scale = 10**digits
    floor = isqrt(x.numerator*scale*scale//x.denominator)
    return F(floor,scale), F(floor+1,scale)


def threshold_proof():
    """Machin pi identity + alternating erf series certify the threshold bracket."""
    alo,ahi = alternating_atan(F(1,5)); blo,bhi = alternating_atan(F(1,239))
    pi_lo,pi_hi = 16*alo-4*bhi,16*ahi-4*blo
    bounds = []
    for q in [Q_LO,Q_HI]:
        y = q/2
        # Term magnitude ratio is y*(2k+1)/((k+1)*(2k+3)) < 1.
        # y < 2 implies this for every k>=0: denominator-2*(2k+1)
        # = 2k^2+k+1 > 0. Thus the alternating remainder theorem applies.
        assert 0 < y < 2
        total = F(0); power = F(1); fact = 1; terms=80
        for k in range(terms):
            if k: power *= y; fact *= k
            total += (-1)**k*power/(fact*(2*k+1))
        nxt = (-1)**terms*(power*y)/(fact*terms*(2*terms+1))
        slo,shi = min(total,total+nxt), max(total,total+nxt)
        flo = sqrt_enclosure(y/pi_hi)[0]
        fhi = sqrt_enclosure(y/pi_lo)[1]
        plo,phi = 1-2*fhi*shi,1-2*flo*slo
        bounds.append((plo,phi))
    assert bounds[0][0] > F(1,20)
    assert bounds[1][1] < F(1,20)
    return {'verified':True,'q_lower':str(Q_LO),'q_upper':str(Q_HI),
            'p_at_lower_minus_alpha_positive':str(bounds[0][0]-F(1,20)),
            'alpha_minus_p_at_upper_positive':str(F(1,20)-bounds[1][1]),
            'method':'Rational alternating arctan (100 terms), Machin identity; alternating erf (80 terms); integer-square-root enclosure at 60 decimal places.'}


def rounded_integer(value, digits):
    scaled = value*10**digits
    return (2*scaled.numerator+scaled.denominator)//(2*scaled.denominator)


def rounded_string(value,digits):
    z=rounded_integer(value,digits)
    if not digits: return str(z)
    return f'{z//10**digits}.{z%10**digits:0{digits}d}'


def validate_release(release):
    if release.get('schema') != 'discrete-km-release-v1': raise ValueError('schema')
    if release.get('synthetic') is not True: raise ValueError('development accepts explicitly synthetic releases only')
    grid=release['grid']; digits=release['probability_digits']
    if not isinstance(grid,list) or not grid or grid!=list(range(1,len(grid)+1)): raise ValueError('grid')
    if type(digits) is not int or not 0<=digits<=6: raise ValueError('digits')
    for arm in ['a','b']:
        r=release[arm]; n=r['n']; e=r['total_events']
        if type(n) is not int or n<1 or type(e) is not int or not 0<=e<=n: raise ValueError('n/events')
        if len(r['survival_rounded'])!=len(grid): raise ValueError('curve length')
        for s in r['survival_rounded']:
            if not isinstance(s,str) or not 0<=F(s)<=1 or (F(s)*10**digits).denominator!=1: raise ValueError('rounded value')
        for t,y in r['risk_counts'].items():
            if str(int(t))!=t or int(t) not in grid or type(y) is not int or not 0<=y<=n: raise ValueError('risk count')


class BudgetStop(Exception):
    pass


def enumerate_arm(release, arm, max_nodes=1000000, max_paths=20000, seconds=15):
    """DFS over all aggregate integer count paths; necessary-only pruning."""
    r=release[arm]; kmax=len(release['grid']); digits=release['probability_digits']
    want=[int(F(x)*10**digits) for x in r['survival_rounded']]
    risks={int(t):y for t,y in r['risk_counts'].items()}
    paths=[]; nodes=0; start=time.perf_counter(); reason=None

    def visit(t,y,s,events,path):
        nonlocal nodes
        nodes+=1
        if nodes>max_nodes: raise BudgetStop('node_limit')
        if nodes%256==0 and time.perf_counter()-start>seconds: raise BudgetStop('time_limit')
        if t in risks and risks[t]!=y: return
        if events>r['total_events'] or events+y<r['total_events']: return
        if any(v>y for j,v in risks.items() if j>t): return
        for d in range(min(y,r['total_events']-events)+1):
            snext=s*F(y-d,y) if y else s
            if rounded_integer(snext,digits)!=want[t-1]: continue
            cvalues=[y-d] if t==kmax else range(y-d+1)
            for c in cvalues:
                left=y-d-c
                if events+d+left<r['total_events']: continue
                if t==kmax:
                    if events+d!=r['total_events']: continue
                    paths.append(tuple(path+[(d,c)]))
                    if len(paths)>=max_paths: raise BudgetStop('path_limit')
                else:
                    if any(v>left for j,v in risks.items() if j>t): continue
                    visit(t+1,left,snext,events+d,path+[(d,c)])
    try:
        if seconds<=0: raise BudgetStop('time_limit')
        visit(1,r['n'],F(1),0,[])
    except BudgetStop as exc: reason=str(exc)
    return paths,{'complete':reason is None,'reason':reason,'nodes':nodes,
                  'accepted_paths':len(paths),'elapsed_seconds':time.perf_counter()-start}


def path_risks(path):
    y=sum(d+c for d,c in path); out=[]
    for d,c in path:
        out.append(y);y-=d+c
    return out


def score(a,b):
    ya=sum(d+c for d,c in a);yb=sum(d+c for d,c in b)
    u=v=F(0)
    for (da,ca),(db,cb) in zip(a,b):
        y=ya+yb; d=da+db
        if y:
            u+=F(da)-F(d*ya,y)
            if y>1: v+=F(ya*yb*d*(y-d),y*y*(y-1))
        ya-=da+ca;yb-=db+cb
    if not v:
        if u: raise ArithmeticError('zero variance with nonzero score')
        return F(0)
    return u*u/v


def decision(qmin,qmax):
    if qmin>Q_HI: return 'stable_reject'
    if qmax<=Q_LO: return 'stable_nonreject'
    return 'unresolved'


def p_approx(q):
    return erfc(sqrt(float(q)/2))


def path_rows(path):
    return [[i,1] for i,(d,c) in enumerate(path,1) for _ in range(d)]+[[i,0] for i,(d,c) in enumerate(path,1) for _ in range(c)]


def solve(release,max_nodes=1000000,max_paths=20000,max_pairs=100000,seconds=15,queries=True):
    validate_release(release)
    start=time.perf_counter()
    a,ma=enumerate_arm(release,'a',max_nodes,max_paths,seconds)
    b,mb=enumerate_arm(release,'b',max_nodes,max_paths,seconds)
    base={'schema':'discrete-km-bounds-v1','synthetic':True,'arm_enumerations':{'a':ma,'b':mb},
          'limits':{'max_nodes_per_arm':max_nodes,'max_paths_per_arm':max_paths,'max_pairs':max_pairs,'seconds_per_phase':seconds},
          'enumerated_pairs':0,'complete':False,'decision':'unresolved',
          'q_outer':['0','infinity'],'p_outer':[0,1]}
    # Even if the other arm seems empty, an unfinished enumeration is never certified.
    if not (ma['complete'] and mb['complete']):
        base['reason']='incomplete_arm_enumeration';base['elapsed_seconds']=time.perf_counter()-start;return base
    if not a or not b:
        base.update(complete=True,decision='infeasible_release',reason='empty_compatible_set',q_outer=None,p_outer=None)
        base['elapsed_seconds']=time.perf_counter()-start;return base
    pair_start=time.perf_counter(); scores=[];qmin=qmax=None;wmin=wmax=None
    stopped=None
    for ia,pa in enumerate(a):
        if stopped:break
        for ib,pb in enumerate(b):
            if len(scores)>=max_pairs:stopped='pair_limit';break
            if len(scores)%256==0 and time.perf_counter()-pair_start>seconds:stopped='pair_time_limit';break
            q=score(pa,pb);scores.append((ia,ib,q))
            if qmin is None or q<qmin:qmin=q;wmin=(pa,pb)
            if qmax is None or q>qmax:qmax=q;wmax=(pa,pb)
    base['enumerated_pairs']=len(scores)
    if stopped:
        base['reason']=stopped
        base['observed_q_extrema_not_bounds']=None if qmin is None else [str(qmin),str(qmax)]
    else:
        base.update(complete=True,decision=decision(qmin,qmax),reason=None,q_outer=[str(qmin),str(qmax)],
                    p_outer=None,p_extrema_approx=[p_approx(qmax),p_approx(qmin)],
                    witnesses={'q_min':{'a':wmin[0],'b':wmin[1]},'q_max':{'a':wmax[0],'b':wmax[1]}})
        if queries:
            opts=[]
            ar=[path_risks(p) for p in a];br=[path_risks(p) for p in b]
            for arm,risks in [('a',ar),('b',br)]:
                for t in release['grid']:
                    if str(t) in release[arm]['risk_counts']:continue
                    groups={}
                    for ia,ib,q in scores:
                        y=risks[ia if arm=='a' else ib][t-1]
                        if y not in groups:groups[y]=[0,q,q]
                        g=groups[y];g[0]+=1;g[1]=min(g[1],q);g[2]=max(g[2],q)
                    if len(groups)<2:continue
                    outcomes=[{'risk':y,'pairs':g[0],'q_outer':[str(g[1]),str(g[2])],
                               'decision':decision(g[1],g[2])} for y,g in sorted(groups.items())]
                    opts.append({'arm':arm,'time':t,'outcomes':outcomes,
                                 'worst_unresolved_pairs':max(o['pairs'] if o['decision']=='unresolved' else 0 for o in outcomes),
                                 'worst_pairs':max(o['pairs'] for o in outcomes)})
            base['query_options']=opts
            base['selected_query']=min(opts,key=lambda x:(x['worst_unresolved_pairs'],x['worst_pairs'],x['arm'],x['time'])) if opts else None
    base['elapsed_seconds']=time.perf_counter()-start
    return base


def release_arm(rows,k,digits,risk_times):
    s=F(1); curve=[]
    for t in range(1,k+1):
        y=sum(x>=t for x,e in rows);d=sum(x==t and e==1 for x,e in rows)
        if y:s*=F(y-d,y)
        curve.append(rounded_string(s,digits))
    return {'n':len(rows),'total_events':sum(e for t,e in rows), 'survival_rounded':curve,
            'risk_counts':{str(t):sum(x>=t for x,e in rows) for t in risk_times}}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('release',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=15);parser.add_argument('--max-pairs',type=int,default=100000)
    args=parser.parse_args();proof=threshold_proof()
    data=json.loads(args.release.read_text());out=solve(data,seconds=args.seconds,max_pairs=args.max_pairs)
    out['threshold_proof']=proof
    args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out.get(k) for k in ['complete','decision','reason','enumerated_pairs','elapsed_seconds']}))
