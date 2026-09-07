"""Independent real-time step-interval and labelled weak-order checks."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import time
from fractions import Fraction as F
from pathlib import Path


def uv(a,b):
    u=v=F(0)
    for t in sorted({x for x,e in a+b if e}):
        ya,yb=[sum(x>=t for x,e in rows) for rows in (a,b)]
        da,db=[sum(x==t and e for x,e in rows) for rows in (a,b)]
        y,d=ya+yb,da+db
        u+=da-F(d*ya,y)
        if y>1:v+=F(d*(y-d),y-1)*F(ya,y)*F(yb,y)
    assert v or not u
    return u,v


def feasible(arm,rows,horizon):
    if len(rows)!=arm['n'] or any(not 0<t<=horizon for t,e in rows):return False
    if arm['total_events'] is not None and sum(e for t,e in rows)!=arm['total_events']:return False
    if any(sum(x>=F(t) for x,e in rows)!=count for t,count in arm['risk_counts'].items()):return False
    # The actual right-continuous curve is constant on [left,right), plus the final point.
    cuts=sorted({F(0),horizon}|{t for t,e in rows})
    s=F(1);segments=[]
    for i,t in enumerate(cuts):
        y=sum(x>=t for x,e in rows);d=sum(x==t and e for x,e in rows)
        if y:s*=F(y-d,y)
        segments.append((t,cuts[i+1] if i+1<len(cuts) else t,i==len(cuts)-1,s))
    previous=F(0)
    for o in arm['observations']:
        tl,th,sl,sh=[F(o[k]) for k in ('time_lo','time_hi','survival_lo','survival_hi')]
        candidates=[]
        for left,right,right_closed,s in segments:
            if not sl<=s<=sh:continue
            lower=max(left,tl,previous);upper=min(right,th)
            if lower<=upper and (lower<right or right_closed):candidates.append(lower)
        if not candidates:return False
        previous=min(candidates)
    return True


def ordered_partitions(n):
    seen=set()
    for perm in itertools.permutations(range(n)):
        for mask in range(1<<(n-1)):
            blocks=[];current=[perm[0]]
            for j in range(n-1):
                if mask & (1<<j):blocks.append(tuple(sorted(current)));current=[]
                current.append(perm[j+1])
            blocks.append(tuple(sorted(current)));seen.add(tuple(blocks))
    return seen


def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    started=time.monotonic();source=args.source/'oracle.py';digest=hashlib.sha256(source.read_bytes()).hexdigest()
    spec=importlib.util.spec_from_file_location('interval_oracle_under_test',source);oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    witness_checks=0;original_checks=0
    outputs={}
    for path in sorted((args.source/'results').glob('*.json')):
        name=path.stem;r=json.loads((args.source/'releases'/(name+'.json')).read_text());out=json.loads(path.read_text());outputs[name]=out
        assert out['complete']
        for score in out['scores']:
            rows=[[],[]]
            for group in score['groups']:
                t=F(group['time']);ae,ac,be,bc=group['counts']
                rows[0].extend([(t,1)]*ae+[(t,0)]*ac);rows[1].extend([(t,1)]*be+[(t,0)]*bc)
            for arm,records in zip(('a','b'),rows):assert feasible(r[arm],records,F(r['horizon']))
            u,v=uv(*rows);assert (u,v)==(F(score['u']),F(score['variance']));assert F(score['q'])==(u*u/v if v else 0)
            witness_checks+=1
    for item in json.loads((args.source/'originals-development.json').read_text()):
        r=json.loads((args.source/'releases'/(item['case']+'.json')).read_text());rows=[[(F(t),e) for t,e in item[a]] for a in ('a','b')]
        for arm,records in zip(('a','b'),rows):assert feasible(r[arm],records,F(r['horizon']))
        assert uv(*rows) in {(F(s['u']),F(s['variance'])) for s in outputs[item['case']]['scores']}
        original_checks+=1
    # Exhaust every labelled weak order/status assignment, not canonical slots, for four exits.
    partitions=ordered_partitions(4);assert len(partitions)==75
    expected=set();assignments=0
    for blocks in partitions:
        times={label:F(j+1,len(blocks)+1) for j,block in enumerate(blocks) for label in block}
        for events in itertools.product((0,1),repeat=4):
            rows=[[(times[i],events[i]) for i in range(2)],[(times[i],events[i]) for i in range(2,4)]]
            expected.add(uv(*rows));assignments+=1
    arm=dict(n=2,total_events=None,risk_counts={'0':2,'1':0},observations=[])
    release=dict(schema='interval-km-release-v1',horizon='1',a=arm,b=arm)
    result=oracle.solve(release)
    assert result['complete']
    assert {(F(s['u']),F(s['variance'])) for s in result['scores']}==expected
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,'Source changed during verification'
    out=dict(passed=True,source_sha256=digest,right_continuous_witness_checks=witness_checks,
             original_real_time_checks=original_checks,independent_labelled_weak_orders=len(partitions),
             event_status_order_assignments=assignments,complete_uv_values=len(expected),
             elapsed_seconds=time.monotonic()-started,
             scope='Coordinator checks use actual half-open step intervals for box feasibility and labelled ordered partitions for an independent exhaustive set; no held-out or benchmark-performance claim.')
    args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(out))


if __name__=='__main__':main()
