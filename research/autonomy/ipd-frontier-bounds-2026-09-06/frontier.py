"""Rational joint-state outer bounds for the existing discrete-time release model."""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import argparse
import importlib.util
import json
import math
import time
import tracemalloc

ORACLE_PATH=Path(__file__).resolve().parent.parent/'ipd-bounds-development-2026-09-06'/'bounds.py'
spec=importlib.util.spec_from_file_location('ipd_discrete_oracle',ORACLE_PATH)
oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)


class Stop(Exception):pass


def q_box(lo,hi,vlo,vhi):
    """Outer Q for actual ordinary-logrank pairs enclosed by this rectangle."""
    assert lo<=hi and 0<=vlo<=vhi
    if vhi==0:
        # Actual V=0 entails U=0. A rectangle excluding it must not certify.
        return (F(0),F(0)) if lo<=0<=hi else (F(0),None)
    if lo==hi==0:return F(0),F(0)
    distance=F(0) if lo<=0<=hi else min(abs(lo),abs(hi))
    lower=distance*distance/vhi
    upper=max(lo*lo,hi*hi)/vlo if vlo else None
    return lower,upper


def classify(lo,hi):
    if lo>oracle.Q_HI:return 'stable_reject'
    if hi is not None and hi<=oracle.Q_LO:return 'stable_nonreject'
    return 'unresolved'


def increments(ya,yb,da,db):
    y=ya+yb;d=da+db
    if not y:return F(0),F(0)
    return F(da)-F(d*ya,y),F(ya*yb*d*(y-d),y*y*(y-1)) if y>1 else F(0)


class Arm:
    def __init__(self,release,name):
        r=release[name];self.n=r['n'];self.events=r['total_events'];self.k=len(release['grid'])
        self.digits=release['probability_digits'];self.want=[int(F(x)*10**self.digits) for x in r['survival_rounded']]
        self.risks={int(t):y for t,y in r['risk_counts'].items()}

    def transitions(self,t,y,e,s):
        """Lazy necessary-only-pruned transitions; no cache of complete paths."""
        if not 0<=e<=y:return
        if t in self.risks and self.risks[t]!=y:return
        future=max((v for j,v in self.risks.items() if j>t),default=0)
        for d in range(min(y,e)+1):
            snext=s*F(y-d,y) if y else s
            if oracle.rounded_integer(snext,self.digits)!=self.want[t-1]:continue
            if t==self.k:
                if d==e:yield 0,0,snext,d,y-d
                continue
            maximum=y-d-max(e-d,future)
            if maximum<0:continue
            if t+1 in self.risks:
                c=y-d-self.risks[t+1]
                cs=[c] if 0<=c<=maximum else []
            else:cs=range(maximum+1)
            for c in cs:yield y-d-c,e-d,snext,d,c

    def witness(self,seconds=2,max_nodes=50000):
        start=time.perf_counter();nodes=0;dead=set();reason=None
        def dfs(t,y,e,s):
            nonlocal nodes
            key=t,y,e,s
            if key in dead:return None
            nodes+=1
            if nodes>max_nodes:raise Stop('witness_node_limit')
            if nodes%64==0 and time.perf_counter()-start>seconds:raise Stop('witness_time_limit')
            if t>self.k:return () if y==e==0 else None
            for yn,en,sn,d,c in self.transitions(t,y,e,s):
                suffix=dfs(t+1,yn,en,sn)
                if suffix is not None:return ((d,c),)+suffix
            dead.add(key);return None
        path=None
        try:
            if seconds<=0:raise Stop('witness_time_limit')
            path=dfs(1,self.n,self.events,F(1))
        except Stop as exc:reason=str(exc)
        return path,{'found':path is not None,'complete':reason is None,'reason':reason,'nodes':nodes,'seconds':time.perf_counter()-start}


def merge(target,key,box,prefix):
    if key in target:
        old,rep=target[key]
        target[key]=((min(old[0],box[0]),max(old[1],box[1]),min(old[2],box[2]),max(old[3],box[3])),rep)
        return True
    target[key]=(box,prefix);return False


def solve(release,seconds=8,max_transitions=100000,max_states=20000,witness_seconds=2,witness_nodes=50000,debug=False):
    oracle.validate_release(release)
    start=time.perf_counter();tracemalloc.start();tracemalloc.reset_peak()
    arms=[Arm(release,n) for n in ['a','b']];k=len(release['grid'])
    paths=[];wmeta=[]
    for arm in arms:
        path,meta=arm.witness(witness_seconds,witness_nodes);paths.append(path);wmeta.append(meta)
    observed={}
    def save_witness(pa,pb):
        q=oracle.score(pa,pb);decision=classify(q,q)
        if decision not in observed:observed[decision]={'q':str(q),'a':pa,'b':pb}
    if all(p is not None for p in paths):save_witness(*paths)
    initial=(1,arms[0].n,arms[1].n,arms[0].events,arms[1].events,F(1),F(1))
    current={initial:((F(0),F(0),F(0),F(0)),())};following={};terminal=[]
    active=None;reason=None;transitions=0;expanded=0;merged=0;peak_states=1;layers=0
    joint_start=time.perf_counter()
    try:
        while current:
            active=current.popitem();key,(box,prefix)=active
            t,ya,yb,ea,eb,sa,sb=key
            if t>k:
                terminal.append((key,(box,prefix)))
                pa=tuple(x[0] for x in prefix);pb=tuple(x[1] for x in prefix)
                save_witness(pa,pb);active=None
            else:
                # Parent stays in active until every generated or ungenerated sibling
                # is exhausted. Any exception below leaves its entire region covered.
                for yna,ena,sna,da,ca in arms[0].transitions(t,ya,ea,sa):
                    for ynb,enb,snb,db,cb in arms[1].transitions(t,yb,eb,sb):
                        if transitions>=max_transitions:raise Stop('transition_limit')
                        if transitions%128==0 and time.perf_counter()-joint_start>seconds:raise Stop('time_limit')
                        if len(current)+len(following)+len(terminal)>=max_states:raise Stop('state_limit')
                        du,dv=increments(ya,yb,da,db)
                        newbox=(box[0]+du,box[1]+du,box[2]+dv,box[3]+dv)
                        newkey=(t+1,yna,ynb,ena,enb,sna,snb)
                        merged+=merge(following,newkey,newbox,prefix+(((da,ca),(db,cb)),))
                        transitions+=1
                        peak_states=max(peak_states,len(current)+len(following)+len(terminal)+1)
                expanded+=1;active=None
            peak_states=max(peak_states,len(current)+len(following)+len(terminal)+(active is not None))
            if not current:
                current,following=following,{}
                layers+=1
    except Stop as exc:reason=str(exc)
    # Complete states, unexpanded states, partial children AND active parent cover
    # all compatible histories. Parent/child overlap is safe and intentional.
    regions=terminal+list(current.items())+list(following.items())+([active] if active is not None else [])
    intervals=[];records=[]
    for key,(box,prefix) in regions:
        t,ya,yb,ea,eb,sa,sb=key
        outer=(box[0]-eb,box[1]+ea,box[2],box[3]+F(ea+eb,4))
        lo,hi=q_box(*outer);intervals.append((lo,hi))
        if debug:records.append({'key':[str(v) for v in key],'box':list(map(str,box)),
                                 'suffix_box':list(map(str,outer)),'q_outer':[str(lo),'infinity' if hi is None else str(hi)]})
    if intervals:
        lower=min(lo for lo,hi in intervals)
        upper=None if any(hi is None for lo,hi in intervals) else max(hi for lo,hi in intervals)
        outer_decision=classify(lower,upper)
        status=outer_decision if observed else 'unresolved_no_witness'
        qout=[str(lower),'infinity' if upper is None else str(upper)]
        pdisplay=[0 if upper is None else math.erfc(math.sqrt(float(upper)/2)),math.erfc(math.sqrt(float(lower)/2))]
    else:
        assert reason is None and not observed
        lower=upper=None;outer_decision=status='infeasible_release';qout=pdisplay=None
    current_bytes,peak_bytes=tracemalloc.get_traced_memory();tracemalloc.stop()
    out={'schema':'discrete-frontier-bounds-v1','synthetic':True,'complete_traversal':reason is None,
         'reason':reason,'decision':status,'outer_interval_decision':outer_decision,
         'q_outer':qout,'p_outer_approx':pdisplay,'nonempty_proven':bool(observed),
         'opposing_witnesses_found':'stable_reject' in observed and 'stable_nonreject' in observed,
         'witnesses':observed,'witness_searches':wmeta,'transitions':transitions,'expanded_states':expanded,
         'merged_histories':merged,'peak_live_states':peak_states,'covered_regions':len(regions),
         'terminal_regions':len(terminal),'active_parent_retained':active is not None,
         'retained_children':len(following),'completed_layers':layers,
         'joint_seconds':time.perf_counter()-joint_start,'elapsed_seconds':time.perf_counter()-start,
         'tracemalloc_current_bytes':current_bytes,'tracemalloc_peak_bytes':peak_bytes,
         'limits':{'seconds_joint':seconds,'max_transitions':max_transitions,'max_states':max_states,
                   'witness_seconds_per_arm':witness_seconds,'witness_nodes_per_arm':witness_nodes}}
    if debug:out['regions']=records
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('release',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();oracle.threshold_proof();r=solve(json.loads(a.release.read_text()))
    a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['decision','complete_traversal','reason','q_outer','elapsed_seconds','tracemalloc_peak_bytes']}))
