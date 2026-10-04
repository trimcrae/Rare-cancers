"""Exploratory landmark calculation from all Oliveira2000 Table2 patients.

No reconstructed patients or event times. Hand-transcribed numeric times are
retained alongside source rows for independent review. Deaths all follow metastasis in the eligible
cohort; hence its metastasis CIF and 1-KM coincide. Independent censoring and
selection are still substantive assumptions. No cross-cohort pooling.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,hashlib
BASE=Path(__file__).resolve().parent
# id, baseline metastatic, first distant metastasis(years), final followup(years), final status
DATA=[
 [1,False,10/12,23/12,'DOD'],[2,False,9,22,'DOD'],[3,True,None,13,'alive'],
 [4,False,None,21,'NED'],[5,False,None,0.5,'NED'],[6,True,None,1,'alive_mets'],
 [7,False,None,20.3,'NED'],[8,False,None,23.5,'NED'],[9,False,4/12,8/12,'DOD'],
 [10,False,3.3,6,'DOD'],[11,False,5.5,6.8,'DOD'],[12,False,None,14.6,'NED'],
 [13,False,1.2,6.5,'alive_mets'],[14,False,None,8.2,'NED'],[15,True,None,7,'alive_mets'],
 [16,False,4,6.8,'alive_mets'],[17,False,None,5.5,'NED'],[18,False,None,6,'NED'],
 [19,False,None,6.2,'NED'],[20,False,0.5,3.3,'alive_mets'],[21,False,None,17,'NED'],
 [22,False,None,13,'NED'],[23,False,None,2,'NED']]
source=json.loads((BASE/'oliveira2000-table2-tables.json').read_text())['tables'][0]
assert len(source)==24 and len(DATA)==23
rows=[]
for id,bline,dm,fu,status in DATA:
 raw=source[id];assert int(raw[0])==id
 assert dm is None or dm<=fu
 rows.append({'id':id,'baseline_metastatic':bline,'dm_years':dm,'followup_years':fu,'final_status':status,'original_source_row':raw})
assert [r['id'] for r in rows if r['baseline_metastatic']]==[3,6,15]
eligible=[r for r in rows if not r['baseline_metastatic']]
assert all(r['dm_years'] is not None for r in eligible if r['final_status']=='DOD')
def estimate(start,end,censor_first=False):
 cohort=[r for r in eligible if r['followup_years']>=start and (r['dm_years'] is None or r['dm_years']>start)]
 events=sorted(set(r['dm_years'] for r in cohort if r['dm_years'] is not None and start<r['dm_years']<=end))
 s=1.;g=0.;risksets=[]
 for t in events:
  at=[r for r in cohort if r['followup_years']>=t and (r['dm_years'] is None or r['dm_years']>=t)]
  if censor_first:at=[r for r in at if not(r['dm_years'] is None and r['followup_years']==t)]
  d=sum(r['dm_years']==t for r in at);n=len(at)
  s*=1-d/n;g+=d/(n*(n-d))
  risksets.append({'year':t,'at_risk':n,'events':d,'ids':[r['id'] for r in at]})
 z=1.959963984540054;se=math.sqrt(g)/abs(math.log(s));v=math.log(-math.log(s))
 slo=math.exp(-math.exp(v+z*se));shi=math.exp(-math.exp(v-z*se))
 return {'start_year':start,'end_year':end,'landmark_n':len(cohort),'landmark_ids':[r['id'] for r in cohort], 'end_observed_eventfree_n':sum(r['followup_years']>=end and(r['dm_years'] is None or r['dm_years']>end) for r in cohort),'events':sum(x['events'] for x in risksets),'risk':1-s,'risk_loglog_greenwood_95ci':[1-shi,1-slo],'risksets':risksets,'event_before_censor_at_ties':not censor_first}
out={'utc':datetime.now(timezone.utc).isoformat(),'population':'Oliveira2000 Table2: all23 rows; exclude3 presenting with metastases, retain20 initially nonmetastatic','source_url':'https://www.nature.com/articles/3880161/tables/2','source_sha256':hashlib.sha256((BASE/'oliveira2000-table2.xml').read_bytes()).hexdigest(),'rows':rows,'early':estimate(0,5),'late':estimate(5,10),'late_tie_sensitivity':estimate(5,10,True),'printed_aggregate_reexpressions':[{'source':'Drilon2008 Table2','time_origin':'wide local excision irrespective of prior procedures','n':73,'s5':0.71,'s10':0.58,'conditional_net_risk':1-0.58/0.71,'uncertainty':'not recoverable from printed two percentages alone; not cumulative incidence'},{'source':'Ogura2012 primary abstract','time_origin':'not authenticated from abstract','n_initially_localized':20,'s5':0.89,'s10':0.61,'conditional_net_risk':1-0.61/0.89,'uncertainty':'not recoverable from printed two percentages alone; full methods pending'}],'decision':'bounded pilot only; no pooled inference or surveillance advice; scientific value and complete coverage unresolved'}
(BASE/'conditional-pilot-results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ['rows']},indent=2))
