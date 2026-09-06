"""Cross-library check of all returned reconstructed witness statistics."""
from pathlib import Path
from fractions import Fraction as F
import json,math
from scipy.stats import CensoredData,logrank
import scipy
P=Path(__file__).resolve().parent;rows=[]
for file in sorted((P/'results').glob('*.json')):
 for s in json.loads(file.read_text())['scores']:
  arms={a:{1:[],0:[]} for a in 'ab'}
  for g in s['groups']:
   for a,start in [('a',0),('b',2)]:
    for idx,event in [(start,1),(start+1,0)]:arms[a][event].extend([float(F(g['time']))]*g['counts'][idx])
  cd=[CensoredData(uncensored=arms[a][1],right=arms[a][0]) for a in 'ab'];r=logrank(*cd)
  # All predefined nonempty fixtures have positive logrank variance.
  err=abs(float(r.pvalue)-s['p_display']);assert err<1e-12
  rows.append(dict(case=file.stem,u=s['u'],variance=s['variance'],oracle_p=s['p_display'],scipy_p=float(r.pvalue),absolute_discrepancy=err))
out=dict(scipy_version=scipy.__version__,witnesses=len(rows),max_absolute_p_discrepancy=max(x['absolute_discrepancy'] for x in rows),rows=rows)
(P/'scipy-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
