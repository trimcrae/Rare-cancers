"""Exploratory challenge to B-lineage specificity; see immutable amendments first."""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET,itertools,statistics,math,urllib.request
import numpy as np
from scipy.stats import spearmanr
BASE=Path(__file__).resolve().parent
SRC=Path('C:/Projects/EMC-Research/research/autonomy/tmem266-tissue-2026-10-03/peerj-source-s009.xlsx')
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
B=['MS4A1','CD79A','CD79B','CD37'];T=['CD3D','CD3E','CD3G'];M=['LST1','AIF1','FCER1G']
GENES=B+T+M+['PTPRC','PXN','H1FX','TYMS']
def read():
 with zipfile.ZipFile(SRC) as z:
  ss=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
  rows=[]
  for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('s:sheetData/s:row',NS):
   v=[]
   for c in row.findall('s:c',NS):
    x=c.find('s:v',NS);v.append(ss[int(x.text)] if c.attrib.get('t')=='s' else float(x.text) if x is not None else None)
   rows.append(v)
  assert len(rows)==9501 and all(len(r)==13 for r in rows)
  assert len(set(r[0] for r in rows[1:]))==9500
  return rows[0][1:],{r[0]:r[1:] for r in rows[1:]}
def A(a,b):return sum((x>y)+.5*(x==y) for x in a for y in b)/(len(a)*len(b))
def contrast(v,low):
 low=set(low);a=[v[i] for i in low];b=[v[i] for i in range(len(v)) if i not in low];obs=A(a,b)
 null=[A([v[i] for i in k],[v[i] for i in range(len(v)) if i not in k]) for k in itertools.combinations(range(len(v)),len(low))]
 p=sum(abs(x-.5)>=abs(obs-.5)-1e-12 for x in null)/len(null)
 loo=[]
 for omit in range(len(v)):
  aa=[v[i] for i in low if i!=omit];bb=[v[i] for i in range(len(v)) if i not in low and i!=omit]
  loo.append(A(aa,bb))
 return {'A_low_gt_high':obs,'mean_difference_low_minus_high':float(np.mean(a)-np.mean(b)),'exact_two_sided_permutation_p':p,'label_permutations':len(null),'leave_one_out_A':loo}
def main():
 ids,rows=read(); vals={g:rows[g] for g in GENES if g in rows}; missing=[g for g in GENES if g not in rows]
 out={'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'sample_ids':ids,'genes':vals,'missing':missing,'scope':'Exploratory RNA marker contrasts. Unverified reconstruction of published risk groups; no outcome validation or cell proportions.'}
 if len([g for g in B if g in rows])>=3 and all(g in rows for g in ['PTPRC','PXN','H1FX','TYMS']):
  scores={n:np.mean([rows[g] for g in panel if g in rows],axis=0) for n,panel in [('B',B),('T',T),('myeloid',M)]}
  scores['PTPRC']=np.array(rows['PTPRC']);scores['B_minus_PTPRC']=scores['B']-scores['PTPRC']
  riskgenes=['PXN','H1FX','TYMS'];X=np.array([rows[g] for g in riskgenes]);w=np.array([1.16,1.58,1.0]);Z=(X-X.mean(axis=1)[:,None])/X.std(axis=1,ddof=1)[:,None]
  riskz=w@Z;riskraw=w@X;iz=sorted(range(12),key=lambda i:riskz[i])[:6];ir=sorted(range(12),key=lambda i:riskraw[i])[:6]
  out.update({'scores':{k:list(map(float,v)) for k,v in scores.items()},'risk_z':list(map(float,riskz)),'risk_raw':list(map(float,riskraw)),'low_risk_z':[ids[i] for i in iz],'low_risk_raw':[ids[i] for i in ir],'same_risk_allocation':set(iz)==set(ir),'contrasts_z':{k:contrast(v,iz) for k,v in scores.items()},'contrasts_raw':{k:contrast(v,ir) for k,v in scores.items()},'B_correlations':{k:{'rho':float(spearmanr(scores['B'],v).statistic),'p_asymptotic_descriptive':float(spearmanr(scores['B'],v).pvalue)} for k,v in scores.items() if k not in ['B','B_minus_PTPRC']}})
 else:out['decision']='Stop: frozen panel or published-score assay coverage insufficient. No substitute panel selected.'
 (BASE/'bcell-pilot-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ['genes','scores','risk_z','risk_raw']},indent=2))
if __name__=='__main__':main()
