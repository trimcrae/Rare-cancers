"""Independent labelled-slot and direct-record checker; no oracle module import."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json, math, subprocess, sys, time
P=Path(__file__).resolve().parent

def arm_ok(a,records,T):
    if len(records)!=a['n'] or any(not 0<t<=T for t,e in records):return False
    if a['total_events'] is not None and sum(e for t,e in records)!=a['total_events']:return False
    if any(sum(t>=F(r) for t,e in records)!=n for r,n in a['risk_counts'].items()):return False
    cuts=sorted({F(0),T}|{t for t,e in records}|{F(v) for o in a['observations'] for v in [o['time_lo'],o['time_hi']]})
    candidate=sorted(set(cuts)|{(x+y)/2 for x,y in zip(cuts,cuts[1:])})
    def survival(at):
        s=F(1)
        for et in sorted({t for t,e in records if e and t<=at}):
            nr=sum(t>=et for t,e in records);ne=sum(t==et and e for t,e in records);s*=F(nr-ne,nr)
        return s
    allowed=[]
    for o in a['observations']:
        lo,hi,sl,sh=[F(o[k]) for k in ['time_lo','time_hi','survival_lo','survival_hi']]
        allowed.append([t for t in candidate if lo<=t<=hi and sl<=survival(t)<=sh])
    return any(all(a<=b for a,b in zip(ts,ts[1:])) for ts in product(*allowed))

def direct_score(a,b):
    u=F(0);v=F(0)
    for et in sorted({t for t,e in a+b if e}):
        ya=sum(t>=et for t,e in a);yb=sum(t>=et for t,e in b)
        da=sum(t==et and e for t,e in a);db=sum(t==et and e for t,e in b)
        y=ya+yb;d=da+db
        u+=F(da)-F(ya*d,y)
        if y>1:v+=F(ya*yb*d*(y-d),y*y*(y-1))
    return u,v

def rows_from_groups(groups):
    return {a:[(F(g['time']),event) for g in groups for idx,event in [(start,1),(start+1,0)] for i in range(g['counts'][idx])] for a,start in [('a',0),('b',2)]}

def main():
    start=time.perf_counter();verification={};releases={f.stem:json.loads(f.read_text()) for f in (P/'releases').glob('*.json')}
    result={f.stem:json.loads(f.read_text()) for f in (P/'results').glob('*.json')}
    for name in ['wide','exact_boundary']:
        r=releases[name];T=F(r['horizon']);N=r['a']['n']+r['b']['n'];bounds={F(0),T}
        for a in 'ab':
            bounds|={F(t) for t in r[a]['risk_counts']}
            bounds|={F(o[k]) for o in r[a]['observations'] for k in ['time_lo','time_hi']}
        bounds=sorted(bounds);slots=sorted(set(bounds[1:])|{left+(right-left)*F(j,N+1) for left,right in zip(bounds,bounds[1:]) for j in range(1,N+1)})
        arm_records={}
        for a in 'ab':
            assert r[a]['n']==2 and r[a]['total_events']==1
            arm_records[a]=[[(te,1),(tc,0)] for te,tc in product(slots,repeat=2) if arm_ok(r[a],[(te,1),(tc,0)],T)]
        scores={direct_score(a,b) for a,b in product(arm_records['a'],arm_records['b'])}
        actual={(F(x['u']),F(x['variance'])) for x in result[name]['scores']}
        assert result[name]['complete'] and scores==actual,(name,scores-actual,actual-scores)
        verification[name]={'slots':list(map(str,slots)),'unfiltered_labelled_assignments':len(slots)**4,'feasible_labelled_assignments':len(arm_records['a'])*len(arm_records['b']),'distinct_uv':len(scores),'full_uv_set_equal':True}
    original_checks=[]
    for original in json.loads((P/'originals-development.json').read_text()):
        name=original['case'];r=releases[name];records={a:[(F(t),e) for t,e in original[a]] for a in 'ab'}
        assert all(arm_ok(r[a],records[a],F(r['horizon'])) for a in 'ab')
        u,v=direct_score(records['a'],records['b']);score_set={(F(x['u']),F(x['variance'])) for x in result[name]['scores']};assert (u,v) in score_set
        q=u*u/v if v else F(0);original_checks.append({'case':name,'label':original['label'],'u':str(u),'variance':str(v),'q':str(q),'p_display':math.erfc(math.sqrt(float(q)/2)),'contained':True})
    witness_count=0
    for name,res in result.items():
        assert res['complete']
        for score in res['scores']:
            records=rows_from_groups(score['groups']);r=releases[name]
            assert all(arm_ok(r[a],records[a],F(r['horizon'])) for a in 'ab')
            assert direct_score(records['a'],records['b'])==(F(score['u']),F(score['variance']))
            # Check the oracle's actual chosen observation timestamps, not only independent existence.
            for a in 'ab':
                times=[F(x) for x in score['observation_times'][a]]
                assert all(x<=y for x,y in zip(times,times[1:]))
                for t,box in zip(times,r[a]['observations']):
                    one=dict(r[a]);one['observations']=[dict(box,time_lo=str(t),time_hi=str(t))]
                    assert arm_ok(one,records[a],F(r['horizon']))
            witness_count+=1
    assert result['ordered_impossible']['status']=='exhaustive_empty'
    r=releases['ordered_impossible']
    for a in 'ab':
        for box in r[a]['observations']:
            one=dict(r[a]);one['observations']=[box];assert arm_ok(one,[(F('3/2'),1),(F('5/2'),0)],F(3))
    forced=[]
    for lim in [1,100]:
        out=P/f'forced-{lim}.json';cmd=[sys.executable,'-B',str(P/'oracle.py'),str(P/'releases/wide.json'),str(out),'--node-limit',str(lim)]
        proc=subprocess.run(cmd,capture_output=True);(P/f'forced-{lim}.log').write_bytes(proc.stdout+proc.stderr);assert proc.returncode==0
        x=json.loads(out.read_text());assert not x['complete'] and x['p_bounds_display']==[0.,1.] and x['nodes']==lim
        forced.append({'node_limit':lim,'universal_bounds':True,'nonempty_proven':x['nonempty_proven']})
    import copy
    invalid=copy.deepcopy(releases['wide']);invalid['a']['observations'][0]['time_lo']='2';invalid['a']['observations'][0]['time_hi']='1';(P/'invalid-box.json').write_text(json.dumps(invalid,indent=2)+'\n')
    proc=subprocess.run([sys.executable,'-B',str(P/'oracle.py'),str(P/'invalid-box.json'),str(P/'invalid-result.json')],capture_output=True);(P/'invalid-box.log').write_bytes(proc.stdout+proc.stderr);assert proc.returncode!=0 and b'Invalid observation box' in proc.stderr
    report={'independent_no_oracle_import':True,'labelled_enumerations':verification,'original_checks':original_checks,'all_returned_witnesses_checked':witness_count,'ordered_individually_feasible_but_jointly_impossible':True,'forced_limits':forced,'malformed_box_rejected':True,'elapsed_seconds':time.perf_counter()-start}
    (P/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
