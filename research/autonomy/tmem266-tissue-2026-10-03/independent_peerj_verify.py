"""Clinical worker's independent reader/arithmetic check; no producer imports."""
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,'.cache/python-deps')
from pathlib import Path
import openpyxl,numpy as np,json,hashlib
from scipy.stats import rankdata
p=Path('research/autonomy/tmem266-tissue-2026-10-03');f=p/'peerj-source-s009.xlsx'
w=openpyxl.load_workbook(f,read_only=True,data_only=True)
assert hashlib.sha256(f.read_bytes()).hexdigest()=='20165fd3ff09ec2d5a24b3c20b78515f42a3309119f248ed055c7484deb45e75'
s=w['EMC_Gene-expression_Log2CPM'];rr=list(s.values);hd=rr[0];data=rr[1:]
sym=[str(r[0]).strip() for r in data];i=sym.index('TMEM266');a=np.asarray([r[1:] for r in data],float)
o=json.loads((p/'peerj-tmem266-results.json').read_text());errors=[]
assert len(set(sym))==len(sym)
for g,z in o['genes'].items():
 j=sym.index(g);q=np.quantile(a,.25,axis=0);r=rankdata(a,method='average',axis=0)[j]/a.shape[0]
 for k,ID in enumerate(hd[1:]):
  t=z['specimens'][ID]
  for label,x,y in [('value',a[j,k],t['published_log2CPM']),('rank',r[k],t['within_sample_midrank_fraction']),('q25',q[k],o['sample_lower_quartiles'][ID])]:
   if abs(x-y)>1e-10:errors.append([g,ID,label,float(x),y])
  if bool(a[j,k]<=q[k])!=t['at_or_below_bottom_quartile']:errors.append([g,ID,'bottom_quartile'])
 if abs(np.median(a[j])-z['median_published_log2CPM'])>1e-10:errors.append([g,'median'])
 if [a[j].min(),a[j].max()]!=z['range_published_log2CPM']:errors.append([g,'range'])
assert not errors,errors
assert i+2==2996 and a.shape==(9500,12)
assert all(g not in sym for g in o['missing_or_ambiguous_controls'])
formulas=sum(isinstance(c,str) and c.startswith('=') for r in openpyxl.load_workbook(f,read_only=True,data_only=False).active.values for c in r)
assert formulas==0
receipt={'independent_reader':'openpyxl vs producer standard-library XML','independent_rank':'scipy.rankdata vs producer manual ranks','dimensions':list(a.shape),'target_excel_row':i+2,'genes_checked':list(o['genes']),'errors':errors,'formulas':formulas,'TMEM266_values':a[i].tolist(),'below_quartile':[ID for k,ID in enumerate(hd[1:]) if a[i,k]<=np.quantile(a[:,k],.25)],'scope':'Arithmetic/mapping only, not localization or molecular identity validation.'}
(p/'independent-peerj-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
