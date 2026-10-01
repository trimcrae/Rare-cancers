import hashlib,itertools,json,math,subprocess
from collections import Counter
from pathlib import Path
D=Path('research/autonomy/data-opportunities-2026-09-30');O=Path('campaign-output/printed-ipd-followthrough');O.mkdir(parents=True,exist_ok=True)
R=dict(schema='printed-ipd-figure-precision-and-eightcase/1',sources=[],errors=[],limits=['Printed records and hypothetical figure-compatible records are separate','Precision intervals are assumptions, not reported actual rounding or statistical confidence intervals','Surgery censors are not independent censoring established by this audit','No curve uniquely identifies event/censor histories','Trabectedin treated5 includes2EMC/3MCS; BSC3 is MCS only, not an EMC comparator','No efficacy comparisons or pooling across papers'])
def unwrap(x,predicate):
 if isinstance(x,str):
  try:return unwrap(json.loads(x),predicate)
  except (ValueError,TypeError):return None
 if isinstance(x,dict):
  if predicate(x):return x
  for v in x.values():
   z=unwrap(v,predicate)
   if z is not None:return z
 if isinstance(x,list):
  for v in x:
   z=unwrap(v,predicate)
   if z is not None:return z
 return None
def source(p,predicate):
 b=p.read_bytes() if p.exists() else subprocess.check_output(['git','show','HEAD:'+p.as_posix()])
 if p.as_posix()=='research/modalities/km-figure-readings.json':assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='65edc0013dc2691091cbde9435b548dac5f54c0e'
 R['sources'].append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));q=unwrap(json.loads(b),predicate);assert q is not None;return q
def km(v):
 assert v and all(math.isfinite(x['time']) and x['time']>=0 for x in v)
 risk=len(v);s=1.;steps=[];med=None
 for t in sorted({x['time'] for x in v}):
  d=sum(x['time']==t and x['event'] for x in v);c=sum(x['time']==t and not x['event'] for x in v);before=s
  if d:s*=1-d/risk
  if med is None and s<=.5:med=t
  steps.append(dict(time=t,atRisk=risk,events=d,censors=c,survivalBefore=before,survival=s));risk-=d+c
 return dict(n=len(v),events=sum(x['event'] for x in v),censors=sum(not x['event'] for x in v),median=med,steps=steps,lastObserved=max(x['time'] for x in v))
def survival(q,t):
 s=1.
 for z in q['steps']:
  if z['time']>t:break
  s=z['survival']
 return s
def rmst(q,tau):
 assert 0<=tau<=q['lastObserved'];a=0.;last=0.;s=1.
 for z in q['steps']:
  t=min(tau,z['time']);a+=(t-last)*s;last=t
  if z['time']>=tau:return a
  s=z['survival']
 return a+(tau-last)*s
try:
 actual=source(D/'deep-analysis/results/printed-clinical-IPD-actual.json',lambda x:'printedPatientRows' in x and 'primarySource' in x);v=[dict(patientID=str(x['patientId']),time=float(x['time']),event=bool(x['event']),printedPFS=x['printedPFS']) for x in actual['printedPatientRows']];assert len(v)==11 and sum(x['event'] for x in v)==8
 q=km(v);R['printedAnthracycline']=dict(primarySource=actual['primarySource'],patientRecords=v,KM=q,S6=survival(q,6),RMST6=rmst(q,6),RMST8=rmst(q,8),RMST10=rmst(q,10));assert abs(rmst(q,6)-5)<1e-10;lo=[]
 for i in range(11):
  z=km(v[:i]+v[i+1:]);lo.append(dict(omittedPatient=v[i]['patientID'],median=z['median'],RMST6=rmst(z,6)))
 R['leaveOneOut']=lo;scenarios=[];eps=1e-8
 for mask in range(1<<11):
  for mode in (0,1):
   z=[]
   for i,x in enumerate(v):
    sign=1 if (mask>>i)&1 else -1;time=x['time']+sign*(.5-2*eps);offset=eps if x['event']==bool(mode) else -eps;z.append(dict(time=time+offset,event=x['event']))
   a=km(z);scenarios.append(dict(median=a['median'],S6=survival(a,6),RMST6=rmst(a,6),RMST8=rmst(a,8)))
 R['hypotheticalNearestMonthSensitivity']=dict(scenarios=len(scenarios),intervalRule='Printed t interpreted hypothetically as [t-.5,t+.5); inward epsilon protects adjacent-bin order; event/censor tie order both examined',ranges={k:[min(x[k] for x in scenarios),max(x[k] for x in scenarios)] for k in ('median','S6','RMST6','RMST8')});assert len(scenarios)==4096
 readings=source(Path('research/modalities/km-figure-readings.json'),lambda x:'recipes' in x and 'readings' in x);rec=next(x for x in readings['recipes'] if x['id']=='stacchiotti2013_pfs_anthracycline');reading=next(x for x in readings['readings'] if x['id']==rec['id']);points=reading['digitized'];risk=rec['risk_table_printed'];assert len(points)==15 and risk==[[2,10],[4,7],[6,5],[8,1],[10,0]]
 R['printedTableRiskChecks']=[dict(tick=t,printedPostCount=n,printedTableStrictlyAfterTick=sum(x['time']>t for x in v)) for t,n in risk];assert all(x['printedPostCount']==x['printedTableStrictlyAfterTick'] for x in R['printedTableRiskChecks'])
 candidate=[dict(time=t,event=True) for t in (2.0,2.985878,3.986761,4.987643,4.987643,7.984996,7.984996,9.986761)]+[dict(time=t,event=False) for t in (3.99,7.,7.)];a=km(candidate);checks=[dict(tick=t,printedPostCount=n,candidateStrictlyAfterTick=sum(x['time']>t for x in candidate)) for t,n in risk];assert all(x['printedPostCount']==x['candidateStrictlyAfterTick'] for x in checks)
 deviations=[dict(time=t,figure=s,candidate=survival(a,t),absoluteDifference=abs(s-survival(a,t))) for t,s in points];R['constructedFigureCompatibleCounterexample']=dict(candidate=candidate,KM=a,S6=survival(a,6),RMST6=rmst(a,6),riskChecks=checks,stepChecks=deviations,maxAbsoluteSurvivalDeviation=max(x['absoluteDifference'] for x in deviations),scope='Constructed counterexample only; not observed patient IPD. First event2.0 differs from pixel2.000883 by.000883 within recorded calibration uncertainty. Arbitrary compatible censor times are not identified.');assert a['events']==8 and a['censors']==3 and R['constructedFigureCompatibleCounterexample']['maxAbsoluteSurvivalDeviation']<.005
 primary=source(D/'deep-analysis/results/clinical-and-ASO-primary-supplements.json',lambda x:x.get('id')=='TRABECTEDIN' and 'tables' in x);tab=next(x for x in primary['tables'] if x['id']=='Tab2');assert 'Censored observation' in tab['text'];rr=[]
 for row in tab['rows']:
  if not row or not str(row[0]).isdigit():continue
  assert len(row)>=8;k=int(row[0]);pfs=str(row[3]);os=str(row[6]);rr.append(dict(subjectID=k,histology=row[1],group='trabectedin' if k<=5 else 'BSC',PFSprinted=pfs,PFStime=float(pfs.replace('*','').strip()),PFSevent='*' not in pfs,OSprinted=os,OStime=float(os.replace('*','').strip()),OSevent='*' not in os,response=row[4],discontinuation=row[7]))
 assert len(rr)==8 and sorted(x['subjectID'] for x in rr)==list(range(1,9));bench=dict(source=primary['primarySource'],literalTable=tab,rows=rr,estimates=[],scope='All8 literal source cases; histology groups retained; star defines endpoint censoring, not discontinuation reason.')
 for group,ep,tau,expected in [('trabectedin','PFS',12,12.5),('BSC','PFS',1,1),('trabectedin','OS',24,26.4),('BSC','OS',24,6.4)]:
  vv=[dict(time=x[ep+'time'],event=x[ep+'event']) for x in rr if x['group']==group];z=km(vv);assert abs(z['median']-expected)<1e-9;bench['estimates'].append(dict(group=group,endpoint=ep,KM=z,RMSTtau=tau,RMST=rmst(z,tau),publishedMedian=expected,medianConcordant=True))
 bench['PFSDiscontinuationSemanticDiscrepancies']=[x for x in rr if not x['PFSevent'] and x['discontinuation']=='progression'];R['printedEightCaseConcordance']=bench
except Exception as e:R['errors'].append(dict(type=type(e).__name__,message=str(e)))
(O/'printed-ipd-figure-precision-eightcase.json').write_text(json.dumps(R,indent=2)+'\n');print('PRINTED_IPD_PRECISION_BEGIN');print(json.dumps(R,separators=(',',':')));print('PRINTED_IPD_PRECISION_END')
if R['errors']:raise SystemExit(1)
