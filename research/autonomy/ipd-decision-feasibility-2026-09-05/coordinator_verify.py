import itertools, json, hashlib, math, sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, 'C:/Projects/EMC-Research/.cache/python-deps')
from scipy.stats import CensoredData, logrank

root = Path(__file__).resolve().parent
data = json.loads((root/'pilot-results.json').read_text())
s = data['selected']; a = s['published_a']; b = s['published_b']
events_a = [x[0] for x in a['km']]; events_b = [x[0] for x in b['km']]
assert a['total_events'] == len(events_a) and b['total_events'] == len(events_b) == b['n']
constraints = dict(zip(a['risk_times'], a['risks']))
prev = Fraction(1)
for t, survival in a['km']:
    now = Fraction(survival); y = 1/(1-now/prev)
    assert y.denominator == 1
    if t in constraints: assert constraints[t] == y
    constraints[t] = int(y); prev = now
cuts = sorted(set(a['risk_times'] + events_a + events_b))
grid = [(x+y)/2 for x,y in zip(cuts,cuts[1:])]
nc = a['n']-a['total_events']; accepted=[]; visited=0
for c in itertools.combinations_with_replacement(grid,nc):
    visited += 1
    if all(sum(x>=t for x in events_a)+sum(x>=t for x in c)==y for t,y in constraints.items()):
        accepted.append(c)
def score(c):
    return float(logrank(CensoredData(uncensored=events_a,right=c),CensoredData(uncensored=events_b)).pvalue)
ps=[score(c) for c in accepted]
assert len(accepted)==s['classes']==10
assert math.isclose(min(ps),s['p_min'],abs_tol=1e-14)
assert math.isclose(max(ps),s['p_max'],abs_tol=1e-14)
def curve(rows):
    out=[]; survival=Fraction(1)
    for t in sorted(set(x for x,e in rows if e)):
        y=sum(x>=t for x,e in rows);d=sum(x==t and e for x,e in rows)
        survival *= Fraction(y-d,y);out.append([t,str(survival)])
    return out
for key in ['true_a','minimum_p_witness_a','maximum_p_witness_a','midpoint_a']:
    rows=s[key];assert curve(rows)==a['km']
    assert [sum(x>=t for x,e in rows) for t in a['risk_times']]==a['risks']
    assert len(rows)==a['n'] and sum(e for x,e in rows)==a['total_events']
    observed=logrank(CensoredData(uncensored=[x for x,e in rows if e],right=[x for x,e in rows if not e]),CensoredData(uncensored=events_b)).pvalue
    assert min(ps)-1e-14<=observed<=max(ps)+1e-14
alpha=data['alpha'];options=[]
for t in events_b:
    groups={}
    for c,p in zip(accepted,ps):
        y=sum(x>=t for x in events_a)+sum(x>=t for x in c)
        groups.setdefault(y,[]).append(p)
    worst=max(len(v) if min(v)<alpha<=max(v) else 0 for v in groups.values())
    width=max(max(v)-min(v) for v in groups.values())
    options.append((worst,width,t,groups))
best=min(options,key=lambda x:x[:3]);assert best[2]==s['selected_query']['time']
assert best[0]==0 and len(best[3])==2
out={'passed':True,'input_sha256':hashlib.sha256((root/'pilot-results.json').read_bytes()).hexdigest(),
     'independent_global_multisets':visited,'compatible_classes':len(accepted),'p_range':[min(ps),max(ps)],
     'query_time':best[2],'query_outcomes':{str(y):{'classes':len(v),'p_min':min(v),'p_max':max(v)} for y,v in best[3].items()},
     'scope':'Coordinator implementation without worker imports; derives constraints from released exact summaries, uses SciPy scores, verifies witnesses and minimax selection. Restricted exact-summary one-censored-arm case only. No clinical/general benchmark claim.'}
Path(__file__).with_name('independent-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
