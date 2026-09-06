"""Exact tiny continuous-time order oracle. Standard library; input releases only."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse, json, math, time

class LimitReached(Exception): pass

def validate(r):
    if r.get('schema')!='interval-km-release-v1': raise ValueError('Unsupported schema')
    T=F(r['horizon'])
    if T<=0: raise ValueError('Positive horizon required')
    bounds={F(0),T}
    for arm in 'ab':
        a=r[arm];n=a['n'];e=a['total_events']
        seen_risk_times=set()
        if type(n) is not int or n<1: raise ValueError('Positive integer n required')
        if e is not None and (type(e) is not int or not 0<=e<=n): raise ValueError('Invalid event total')
        for t,v in a['risk_counts'].items():
            t=F(t)
            if t in seen_risk_times: raise ValueError('Duplicate rational risk time')
            seen_risk_times.add(t)
            if not 0<=t<=T or type(v) is not int or not 0<=v<=n: raise ValueError('Invalid risk count')
            bounds.add(t)
        for o in a['observations']:
            lo,hi,sl,sh=map(F,[o['time_lo'],o['time_hi'],o['survival_lo'],o['survival_hi']])
            if not 0<=lo<=hi<=T or not 0<=sl<=sh<=1: raise ValueError('Invalid observation box')
            bounds.update([lo,hi])
    return sorted(bounds)

def observation_witness(r,groups,bounds):
    cuts=sorted(set(bounds)|{t for t,c in groups})
    candidates=sorted(set(cuts)|{(a+b)/2 for a,b in zip(cuts,cuts[1:])})
    chosen={}
    for arm,idx in [('a',0),('b',2)]:
        y=r[arm]['n'];s=F(1);series=[]
        for t,c in groups:
            d,censor=c[idx:idx+2]
            if d: s*=F(y-d,y)
            y-=d+censor
            series.append((t,s))
        values=[];i=0;s=F(1)
        for t in candidates:
            while i<len(series) and series[i][0]<=t:
                s=series[i][1];i+=1
            values.append(s)
        last=F(0);arm_chosen=[]
        for o in r[arm]['observations']:
            lo,hi,sl,sh=map(F,[o['time_lo'],o['time_hi'],o['survival_lo'],o['survival_hi']])
            match=next((t for t,s in zip(candidates,values) if max(last,lo)<=t<=hi and sl<=s<=sh),None)
            if match is None:return None
            arm_chosen.append(str(match));last=match
        chosen[arm]=arm_chosen
    return chosen

def score_increment(rem,g):
    ya=rem[0]+rem[1];yb=rem[2]+rem[3];d=g[0]+g[2];y=ya+yb
    if not d:return F(0),F(0)
    u=F(g[0])-F(d*ya,y)
    v=F(ya*yb*d*(y-d),y*y*(y-1)) if y>1 else F(0)
    return u,v

def solve(r,node_limit=1000000):
    if type(node_limit) is not int or node_limit<1: raise ValueError('Positive integer node limit required')
    started=time.perf_counter();bounds=validate(r);N=r['a']['n']+r['b']['n'];T=bounds[-1]
    stages=[]
    for left,right in zip(bounds,bounds[1:]):stages.extend([('open',left,right),('point',right,right)])
    risks={arm:{F(t):v for t,v in r[arm]['risk_counts'].items()} for arm in 'ab'}
    scores={};nodes=0;feasible_classes=0;terminal_classes=0;complete=True
    def group_options(rem):
        return product(*(range(v+1) for v in rem))
    def walk(stage,j,rem,groups,u,v):
        nonlocal nodes,feasible_classes,terminal_classes
        if nodes>=node_limit:raise LimitReached
        nodes+=1
        if stage==len(stages):
            if any(rem):return
            terminal_classes+=1
            obs=observation_witness(r,groups,bounds)
            if obs is None:return
            feasible_classes+=1
            if not v:assert not u
            q=u*u/v if v else F(0)
            key=(u,v)
            if key not in scores:
                scores[key]={'u':str(u),'variance':str(v),'q':str(q),'p_display':math.erfc(math.sqrt(float(q)/2)),
                             'groups':[{'time':str(t),'counts':list(g)} for t,g in groups],'observation_times':obs}
            return
        kind,left,right=stages[stage]
        if kind=='point':
            if any(left in risks[a] and risks[a][left]!=rem[i]+rem[i+1] for a,i in [('a',0),('b',2)]):return
            options=[rem] if left==T else group_options(rem)
            for g in options:
                next_rem=tuple(x-z for x,z in zip(rem,g));du,dv=score_increment(rem,g)
                walk(stage+1,0,next_rem,groups+([(left,g)] if any(g) else []),u+du,v+dv)
        else:
            # Stop this open cell, including empty cell, then enumerate each nonempty next weak group.
            walk(stage+1,0,rem,groups,u,v)
            if j>=N:return
            t=left+(right-left)*F(j+1,N+1)
            for g in group_options(rem):
                if not any(g):continue
                next_rem=tuple(x-z for x,z in zip(rem,g));du,dv=score_increment(rem,g)
                walk(stage,j+1,next_rem,groups+[(t,g)],u+du,v+dv)
    possible=[]
    for a in 'ab':
        e=r[a].get('total_events');possible.append([e] if e is not None else range(r[a]['n']+1))
    try:
        if all(risks[a].get(F(0),r[a]['n'])==r[a]['n'] for a in 'ab'):
            for ea,eb in product(*possible):walk(0,0,(ea,r['a']['n']-ea,eb,r['b']['n']-eb),[],F(0),F(0))
    except LimitReached:complete=False
    values=sorted(scores.values(),key=lambda x:(F(x['q']),F(x['u']),F(x['variance'])))
    out={'schema':'interval-order-result-v1','complete':complete,'nonempty_proven':bool(scores),'nodes':nodes,'node_limit':node_limit,
         'terminal_classes':terminal_classes,'feasible_classes':feasible_classes,'distinct_uv':len(values),
         'bounds': [str(t) for t in bounds], 'scores':values,'elapsed_seconds':time.perf_counter()-started}
    if complete and values:
        out.update(status='exhaustive_nonempty',q_bounds_exact=[values[0]['q'],values[-1]['q']],p_bounds_display=[values[-1]['p_display'],values[0]['p_display']])
    elif complete:out.update(status='exhaustive_empty',q_bounds_exact=None,p_bounds_display=None)
    else:out.update(status='incomplete',q_bounds_exact=['0','infinity'],p_bounds_display=[0.0,1.0])
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('release',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--node-limit',type=int,default=1000000);a=ap.parse_args()
    if a.node_limit<1:ap.error('positive node limit required')
    result=solve(json.loads(a.release.read_text(encoding='utf-8-sig')),a.node_limit)
    a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='scores'},indent=2))
