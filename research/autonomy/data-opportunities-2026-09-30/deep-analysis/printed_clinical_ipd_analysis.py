#!/usr/bin/env python3
"""Printed EMC clinical IPD reuse; no cross-study efficacy comparison."""
import hashlib,json,re,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
EXPECTED="390e456b36664c767f2b06d5bc6c5ffc2afcf5f2d1074727dd5c06fc248bf8c7"
def km(rows,tau):
 g=defaultdict(lambda:[0,0])
 for p in rows:g[float(p['time'])][0 if p['event'] else 1]+=1
 risk=len(rows);s=1.;last=0.;area=0.;median=None;steps=[];landmark=1.
 for t,(e,c) in sorted(g.items()):
  if last<tau:area+=s*(min(t,tau)-last)
  s*=1-e/risk
  if median is None and s<=.5:median=t
  if t<=tau:landmark=s
  steps.append(dict(timeMonths=t,atRisk=risk,events=e,censors=c,survival=s))
  risk-=e+c;last=t
 if last<tau:area+=s*(tau-last)
 supported=last>=tau or s==0
 return dict(n=len(rows),events=sum(p['event'] for p in rows),censors=sum(not p['event'] for p in rows),tauMonths=tau,rmstMonths=area if supported else None,medianMonths=median,landmarkSurvival=landmark,atRiskBeforeLandmark=sum(p['time']>=tau for p in rows),horizonSupported=supported,kaplanMeier=steps)
p=Path(sys.argv[1]);b=p.read_bytes();j=json.loads(b);j=j.get('result',j)
sources=j.get('sources',j.get('clinical',{}).get('sources',[]))
s=next(x for x in sources if x['id']=='ANTHRACYCLINE')
assert s['primarySource']['sha256']==EXPECTED,'unexpected primary source revision'
t=next(x for x in s['tables'] if x['id']=='T2')
assert t['rows'][0][0]=='Patient ID' and t['rows'][0][-1]=='PFS'
assert 'censored at the time of surgical resection' in t['text']
rows=[]
for r in t['rows'][1:]:
 assert len(r)==10 and re.fullmatch(r'\d+\*?',r[9]),r
 rows.append(dict(patientId=r[0],sex=r[1],ageYears=int(r[2]),diagnosis=r[3],NR4A3Rearrangement=r[4],primarySite=r[5],initialStage=r[6],relapseSites=r[7],RECIST=r[8],printedPFS=r[9],time=float(r[9].rstrip('*')),event=not r[9].endswith('*'),censorReason='surgery' if r[9].endswith('*') else None))
assert len(rows)==11 and len({r['patientId'] for r in rows})==11
assert Counter(r['NR4A3Rearrangement'] for r in rows)=={'yes':11}
assert {r['patientId'] for r in rows if not r['event']}=={'1','7','10'}
R=dict(schema='emc-printed-clinical-ipd-analysis/1',startedUtc=datetime.now(timezone.utc).isoformat(),inputArtifact=dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()),primarySource=s['primarySource'],sourceTable='T2',printedPatientRows=rows,scope='11 centrally reviewed NR4A3-rearranged EMC patients receiving anthracycline regimens; retrospective series, surgery censoring, no untreated or randomized comparator.',limitations=['Printed times integer months; rounding precision unspecified.','Surgery censoring may be informative and does not estimate a complete strategy effect.','Post hoc RMST/leave-one-out descriptive. Ranges are not confidence intervals.','Primary text approximately50% progression-free at six months; printed rounded rows yield63.6%. Preserve both.','Aggregate9/11EWS rearrangement cannot assign named fusion partner to other cases.'])
R['estimates']=[km(rows,h) for h in (3,6,8,10)]
R['responseDenominators']=dict(allTreated=11,evaluable=10,counts=dict(Counter(r['RECIST'] for r in rows)),partialResponsePerEvaluable=4/10,partialResponsePerAllTreated=4/11)
R['leaveOneOut']=[dict(tauMonths=h,analyses=[dict(omittedPatientId=r['patientId'],estimate=km([x for x in rows if x['patientId']!=r['patientId']],h)) for r in rows]) for h in (6,8,10)]
legacy=Path(sys.argv[2]) if len(sys.argv)>2 else Path('research/modalities/km-figure-readings.json')
if legacy.exists():
 lb=legacy.read_bytes();old=json.loads(lb)['readings'][0]['reconstructions'];diag={}
 for key in ('risk_table_anchored','risk_table_printed'):
  q=old[key];er=km(q['ipd'],6)
  diag[key]=dict(admissibleUnderHistoricalChecks=q['admissible'],estimate=er,eventCountDifferenceFromPrinted=er['events']-8,censorCountDifferenceFromPrinted=er['censors']-3,medianDifferenceFromPrinted=er['medianMonths']-8,rmst6DifferenceFromPrinted=er['rmstMonths']-5)
 R['legacyReconstructionDiagnostic']=dict(path=str(legacy),sha256=hashlib.sha256(lb).hexdigest(),variants=diag,interpretation='Median match does not verify patient event/censor counts. Printed IPD preferred; reconstructed rows diagnostics only.')
R['finishedUtc']=datetime.now(timezone.utc).isoformat()
out=Path('campaign-output/deep-analysis/outputs/printed-clinical-ipd-analysis.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(R,indent=2)+'\n')
print('EMC_PRINTED_CLINICAL_IPD_RESULT_BEGIN');print(json.dumps(R,separators=(',',':')));print('EMC_PRINTED_CLINICAL_IPD_RESULT_END')
