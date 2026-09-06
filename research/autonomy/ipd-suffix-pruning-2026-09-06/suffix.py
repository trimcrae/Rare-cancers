"""Exact release-only suffix pruning; original frontier/oracle imported read-only."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import importlib.util
import json
import math
import time
import tracemalloc

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'ipd-frontier-bounds-2026-09-06'/'frontier.py'
spec=importlib.util.spec_from_file_location('original_frontier',BASE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
oracle=base.oracle
q_box=base.q_box
classify=base.classify
increments=base.increments
merge=base.merge


class Stop(Exception):pass


class Budget:
    def __init__(self,start,seconds,max_work,max_cache_entries,max_memory_bytes,force):
        self.start=start;self.seconds=seconds;self.max_work=max_work
        self.max_cache_entries=max_cache_entries;self.max_memory_bytes=max_memory_bytes
        self.work=0;self.counts={};self.cache_entries=0;self.force=force or {};self.hooks={}
        self.stop_context=None

    def check(self,context):
        self.stop_context=context
        if time.perf_counter()-self.start>=self.seconds:raise Stop('time_limit')
        if tracemalloc.get_traced_memory()[1]>=self.max_memory_bytes:raise Stop('memory_limit')

    def tick(self,kind):
        self.check(kind)
        if self.work>=self.max_work:raise Stop('work_limit')
        self.work+=1;self.counts[kind]=self.counts.get(kind,0)+1

    def hook(self,kind,detail):
        self.hooks[kind]=self.hooks.get(kind,0)+1
        if self.force.get(kind)==self.hooks[kind]:
            self.stop_context={'hook':kind,'detail':detail}
            raise Stop('forced_'+kind)

    def cache_insert(self):
        self.check('cache_insert')
        if self.cache_entries>=self.max_cache_entries:raise Stop('cache_limit')
        self.cache_entries+=1


class Arm(base.Arm):
    def __init__(self,release,name,budget):
        super().__init__(release,name)
        self.budget=budget;self.cache={};self.name=name
        self.stats={'calls':0,'hits_true':0,'hits_false':0,'proved_true':0,'proved_false':0,
                    'unknown_returns':0,'pruned_transitions':0,'successors_exhausted':0,'max_depth':0}

    def transitions(self,t,y,e,s):
        # Same admissible transition set as the original Arm, with charged loops.
        if not 0<=e<=y:return
        if t in self.risks and self.risks[t]!=y:return
        future=max((v for j,v in self.risks.items() if j>t),default=0)
        for d in range(min(y,e)+1):
            self.budget.tick('event_candidates')
            snext=s*F(y-d,y) if y else s
            if oracle.rounded_integer(snext,self.digits)!=self.want[t-1]:continue
            if t==self.k:
                if d==e:
                    self.budget.tick('censor_successors')
                    yield 0,0,snext,d,y-d
                continue
            maximum=y-d-max(e-d,future)
            if maximum<0:continue
            if t+1 in self.risks:
                c=y-d-self.risks[t+1]
                cs=[c] if 0<=c<=maximum else []
            else:cs=range(maximum+1)
            for c in cs:
                self.budget.tick('censor_successors')
                yield y-d-c,e-d,snext,d,c

    def feasible(self,key,depth=1):
        """Return False or a real continuation tuple. Stop propagates UNKNOWN."""
        self.stats['calls']+=1;self.stats['max_depth']=max(depth,self.stats['max_depth'])
        try:
            self.budget.tick('suffix_calls')
            self.budget.hook('suffix_entry',{'arm':self.name,'key':list(map(str,key)),'depth':depth})
            if key in self.cache:
                path=self.cache[key]
                self.stats['hits_false' if path is False else 'hits_true']+=1
                return path
            t,y,e,s=key
            if t>self.k:path=() if y==e==0 else False
            else:
                path=False
                for yn,en,sn,d,c in self.transitions(t,y,e,s):
                    suffix=self.feasible((t+1,yn,en,sn),depth+1)
                    self.stats['successors_exhausted']+=1
                    self.budget.hook('suffix_after_successor',{'arm':self.name,'key':list(map(str,key)),
                                                              'depth':depth,'child_false':suffix is False})
                    if suffix is not False:
                        path=((d,c),)+suffix
                        break
            self.budget.cache_insert()
            self.cache[key]=path
            self.stats['proved_false' if path is False else 'proved_true']+=1
            return path
        except Stop:
            # Nothing stores this interrupted key as FALSE. Completed descendants survive.
            self.stats['unknown_returns']+=1
            raise

    def query(self,key):
        try:return self.feasible(key),None
        except Stop as exc:return None,str(exc) # None is explicitly UNKNOWN, distinct from False and ().

    def report(self,debug=False):
        result={**self.stats,'cache_entries':len(self.cache),'cache_unknown_entries':0}
        if debug:result['cache']=[{'key':list(map(str,key)),'status':'FALSE' if path is False else 'TRUE',
                                  'continuation':None if path is False else path} for key,path in self.cache.items()]
        return result


def solve(release,seconds=12,max_work=200000,max_transitions=100000,max_states=20000,
          max_cache_entries=100000,max_memory_bytes=64*1024*1024,initial_witness=True,debug=False,force=None):
    oracle.validate_release(release)
    start=time.perf_counter();tracemalloc.start();tracemalloc.reset_peak()
    budget=Budget(start,seconds,max_work,max_cache_entries,max_memory_bytes,force)
    arms=[Arm(release,n,budget) for n in ['a','b']];k=len(release['grid'])
    observed={}
    def save_witness(pa,pb):
        q=oracle.score(pa,pb);decision=classify(q,q)
        if decision not in observed:observed[decision]={'q':str(q),'a':pa,'b':pb}
    initial=(1,arms[0].n,arms[1].n,arms[0].events,arms[1].events,F(1),F(1))
    current={initial:((F(0),F(0),F(0),F(0)),())};following={};terminal=[]
    active=None;reason=None;transitions=0;expanded=0;merged=0;peak_states=1;layers=0
    initial_results=[];paths=[]
    search_start=time.perf_counter()
    try:
        if initial_witness:
            for arm in arms:
                path,stop=arm.query((1,arm.n,arm.events,F(1)))
                initial_results.append('UNKNOWN' if path is None else 'FALSE' if path is False else 'TRUE')
                if stop:raise Stop(stop)
                if path is False:
                    current={};break
                paths.append(path)
            if len(paths)==2:save_witness(*paths)
        while current:
            active=current.popitem();key,(box,prefix)=active
            t,ya,yb,ea,eb,sa,sb=key
            budget.check('joint_parent')
            if t>k:
                terminal.append((key,(box,prefix)))
                save_witness(tuple(x[0] for x in prefix),tuple(x[1] for x in prefix));active=None
            else:
                # Active parent remains until all locally admissible children are exhausted.
                for yna,ena,sna,da,ca in arms[0].transitions(t,ya,ea,sa):
                    fa,stop=arms[0].query((t+1,yna,ena,sna))
                    if stop:raise Stop(stop)
                    if fa is False:arms[0].stats['pruned_transitions']+=1;continue
                    for ynb,enb,snb,db,cb in arms[1].transitions(t,yb,eb,sb):
                        fb,stop=arms[1].query((t+1,ynb,enb,snb))
                        if stop:raise Stop(stop)
                        if fb is False:arms[1].stats['pruned_transitions']+=1;continue
                        if transitions>=max_transitions:raise Stop('transition_limit')
                        if len(current)+len(following)+len(terminal)>=max_states:raise Stop('state_limit')
                        budget.tick('joint_pairs')
                        du,dv=increments(ya,yb,da,db)
                        newbox=(box[0]+du,box[1]+du,box[2]+dv,box[3]+dv)
                        newkey=(t+1,yna,ynb,ena,enb,sna,snb)
                        merged+=merge(following,newkey,newbox,prefix+(((da,ca),(db,cb)),))
                        transitions+=1
                        budget.hook('joint_after_successor',{'transitions':transitions,'time':t})
                        peak_states=max(peak_states,len(current)+len(following)+len(terminal)+1)
                expanded+=1;active=None
            peak_states=max(peak_states,len(current)+len(following)+len(terminal)+(active is not None))
            if not current:current,following=following,{};layers+=1
    except Stop as exc:reason=str(exc)
    search_seconds=time.perf_counter()-search_start
    regions=terminal+list(current.items())+list(following.items())+([active] if active is not None else [])
    intervals=[];records=[]
    for key,(box,prefix) in regions:
        t,ya,yb,ea,eb,sa,sb=key
        outer=(box[0]-eb,box[1]+ea,box[2],box[3]+F(ea+eb,4))
        lo,hi=q_box(*outer);intervals.append((lo,hi))
        if debug:records.append({'key':list(map(str,key)),'box':list(map(str,box)),
                                 'suffix_box':list(map(str,outer)),'q_outer':[str(lo),'infinity' if hi is None else str(hi)]})
    if intervals:
        lower=min(lo for lo,hi in intervals)
        upper=None if any(hi is None for lo,hi in intervals) else max(hi for lo,hi in intervals)
        outer_decision=classify(lower,upper);status=outer_decision if observed else 'unresolved_no_witness'
        qout=[str(lower),'infinity' if upper is None else str(upper)]
        width='infinity' if upper is None else str(upper-lower)
        pdisplay=[0 if upper is None else math.erfc(math.sqrt(float(upper)/2)),math.erfc(math.sqrt(float(lower)/2))]
    else:
        assert reason is None and not observed
        outer_decision=status='infeasible_release';qout=pdisplay=width=None
    arm_reports={n:a.report(debug) for n,a in zip(['a','b'],arms)}
    current_bytes,peak_bytes=tracemalloc.get_traced_memory();tracemalloc.stop()
    out={'schema':'discrete-suffix-frontier-v1','synthetic':True,'complete_traversal':reason is None,
         'reason':reason,'decision':status,'outer_interval_decision':outer_decision,
         'q_outer':qout,'q_width':width,'p_outer_approx':pdisplay,'nonempty_proven':bool(observed),
         'opposing_witnesses_found':'stable_reject' in observed and 'stable_nonreject' in observed,
         'witnesses':observed,'initial_feasibility':initial_results,'arms':arm_reports,
         'transitions':transitions,'expanded_states':expanded,'merged_histories':merged,
         'peak_live_states':peak_states,'covered_regions':len(regions),'terminal_regions':len(terminal),
         'active_parent_retained':active is not None,'retained_children':len(following),'completed_layers':layers,
         'work_units':budget.work,'work_counts':budget.counts,'stop_context':budget.stop_context if reason else None,
         'hook_counts':budget.hooks,'search_seconds':search_seconds,'elapsed_seconds':time.perf_counter()-start,
         'tracemalloc_current_bytes':current_bytes,'tracemalloc_peak_bytes':peak_bytes,
         'limits':{'seconds_total_search':seconds,'max_work_units':max_work,'max_transitions':max_transitions,
                   'max_joint_states':max_states,'max_cache_entries':max_cache_entries,
                   'max_traced_bytes':max_memory_bytes,'initial_witness':initial_witness,'forced_stops':force}}
    if debug:out['regions']=records
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('release',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();oracle.threshold_proof();r=solve(json.loads(a.release.read_text()))
    a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['decision','complete_traversal','reason','q_outer','elapsed_seconds','tracemalloc_peak_bytes']}))
