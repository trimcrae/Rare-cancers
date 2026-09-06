"""Generate only the deterministic fixtures frozen in fixtures-plan.md."""
import copy,json
from pathlib import Path
P=Path(__file__).resolve().parent
box=lambda lo,hi,sl,sh:dict(time_lo=lo,time_hi=hi,survival_lo=sl,survival_hi=sh)
a=dict(n=2,total_events=1,risk_counts={'0':2,'3':0},observations=[box('1','2','49/100','51/100')])
wide=dict(schema='interval-km-release-v1',synthetic=True,horizon='3',a=copy.deepcopy(a),b=copy.deepcopy(a))
cases={'wide':wide}; exact=copy.deepcopy(wide)
for arm in 'ab':exact[arm]['risk_counts']['3/2']=2;exact[arm]['observations']=[box('3/2','3/2','1/2','1/2')]
cases['exact_boundary']=exact
ordered=copy.deepcopy(wide)
for arm in 'ab':ordered[arm]['observations']=[box('2','2','1/2','1/2'),box('1','1','1','1')]
cases['ordered_impossible']=ordered
unknown=copy.deepcopy(wide)
for arm in 'ab':unknown[arm]['total_events']=None
cases['unknown_events']=unknown
three=copy.deepcopy(wide)
for arm in 'ab':three[arm]=dict(n=3,total_events=1,risk_counts={'0':3,'1':3,'2':1,'3':0},observations=[box('1','1','2/3','2/3')])
cases['n3_boundary']=three
originals=[{'case':'wide','label':'original','a':[['5/4',1],['11/4',0]],'b':[['7/4',1],['5/2',0]]},
 {'case':'wide','label':'censor_before_other_event','a':[['5/4',1],['3/2',0]],'b':[['7/4',1],['5/2',0]]},
 {'case':'wide','label':'event_tie','a':[['3/2',1],['11/4',0]],'b':[['3/2',1],['5/2',0]]},
 {'case':'wide','label':'event_censor_tie','a':[['5/4',1],['7/4',0]],'b':[['7/4',1],['5/2',0]]},
 {'case':'exact_boundary','label':'at_boundary','a':[['3/2',1],['3/2',0]],'b':[['3/2',1],['5/2',0]]},
 {'case':'unknown_events','label':'original','a':[['5/4',1],['11/4',0]],'b':[['7/4',1],['5/2',0]]},
 {'case':'n3_boundary','label':'original','a':[['1',1],['3/2',0],['5/2',0]],'b':[['1',1],['3/2',0],['5/2',0]]}]
(P/'releases').mkdir(exist_ok=True)
for name,r in cases.items():(P/'releases'/f'{name}.json').write_text(json.dumps(r,indent=2)+'\n')
(P/'originals-development.json').write_text(json.dumps(originals,indent=2)+'\n')
print('Generated five predeclared release fixtures and seven original-record checks.')
