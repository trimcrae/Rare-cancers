"""Independently verify R logrank outputs and released-summary compatibility.
No hidden original records read. Continuous reconstructions are never rounded.
"""
import json, pathlib, math
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP
from scipy.stats import CensoredData, logrank
P=pathlib.Path(__file__).resolve().parent
rows=[]
for f in sorted((P/'development').glob('*-result.json')):
 x=json.loads(f.read_text());r=json.loads(f.with_name(f.name.replace('-result','-release')).read_text())
 for method,m in x['methods'].items():
  out={'case':f.stem.removesuffix('-result'),'method':method,'status':m['status']}
  if m['status']=='failure':out['error']=m['error'];rows.append(out);continue
  arms={a:[(v['time'],v['event']) for v in m['ipd'] if v['arm']==a] for a in 'ab'}
  inp=[CensoredData(uncensored=[t for t,e in arms[a] if e],right=[t for t,e in arms[a] if not e]) for a in 'ab']
  check=logrank(*inp);out.update(r_p=m['logrank_p'],scipy_p=float(check.pvalue),absolute_p_discrepancy=abs(m['logrank_p']-float(check.pvalue)))
  assert out['absolute_p_discrepancy']<1e-10
  details={}
  for a,rec in arms.items():
   d=r[a];s=Fraction(1);sf={}
   for t in sorted(set(t for t,e in rec)):
    y=sum(tt>=t for tt,e in rec);ev=sum(tt==t and e for tt,e in rec);s*=Fraction(y-ev,y);sf[t]=s
   vals=[]
   for t in r['grid']:
    z=sf[max([v for v in sf if v<=t])] if any(v<=t for v in sf) else Fraction(1)
    rounded=(Decimal(z.numerator)/Decimal(z.denominator)).quantize(Decimal(1).scaleb(-r['probability_digits']),rounding=ROUND_HALF_UP);vals.append(str(rounded))
   actual_risks={t:sum(tt>=float(t) for tt,e in rec) for t in d['risk_counts']}
   details[a]={'sample_size_match':len(rec)==d['n'],'event_total_match':sum(e for t,e in rec)==d['total_events'],'discrete_support_match':all(t in r['grid'] for t,e in rec),'risk_counts_match':actual_risks==d['risk_counts'],'rounded_curve_match':vals==d['survival_rounded'],'actual_risks':actual_risks,'actual_rounded_curve':vals,'n':len(rec),'events':sum(e for t,e in rec)}
  out['compatibility']=details;out['same_discrete_release_compatible']=all(all(v[k] for k in ['sample_size_match','event_total_match','discrete_support_match','risk_counts_match','rounded_curve_match']) for v in details.values());rows.append(out)
summary={m:{'success':sum(v['status']=='success' for v in rows if v['method']==m),'failure':sum(v['status']=='failure' for v in rows if v['method']==m),'same_discrete_release_compatible':sum(v.get('same_discrete_release_compatible',False) for v in rows if v['method']==m)} for m in ['IPDfromKM','CIFresolve']}
(P/'validation.json').write_text(json.dumps({'scope':'Released development inputs and reconstructed outputs only; no original hidden IPD opened','max_p_discrepancy':max(v.get('absolute_p_discrepancy',0) for v in rows),'summary':summary,'cases':rows},indent=2)+'\n');print(summary)
