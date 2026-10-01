import json,hashlib,urllib.request,re,time,os
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr
ROOT=Path(os.environ.get('AUTHENTIC_SCREEN_OUTPUT_DIR','campaign-output/authentic-screen'));ROOT.mkdir(parents=True,exist_ok=True)
BASE='https://raw.githubusercontent.com/trimcrae/Rare-cancers/af7211708205b5189d8c537c1ce2a23aa4bea076/research/literature/emc-census-2026-09-12/iwata-2025-screen-extraction.json'
FAMILIES={'afatinib':['439081-18-2','850140-73-7'],'bendamustine':['16506-27-7','3543-75-7'],'cabozantinib':['849217-68-1','1140909-48-3'],'ceritinib':['1032900-25-6','1380575-43-8'],'crizotinib non-S':['877399-52-5','1415560-69-8'],'cyclophosphamide':['50-18-0','6055-19-2'],'dasatinib':['302962-49-8','854001-07-3'],'doxorubicin':['23214-92-8','25316-40-9'],'ixazomib':['1201902-80-8','1239908-20-3'],'regorafenib':['755037-03-7','835621-07-3','1019206-88-2'],'ribociclib':['1211441-98-3','1211443-80-9','1374639-75-4'],'rucaparib':['283173-50-2','459868-92-9','1859053-21-6'],'sorafenib':['284461-73-0','475207-59-1'],'sunitinib':['557795-19-4','341031-54-7'],'tamoxifen':['10540-29-1','54965-24-1']}
def get(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Rare-cancers-source-replay/1'}),timeout=90) as r:return r.read()
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
 if isinstance(x,np.integer):return int(x)
 return x
def save(n,x):(ROOT/n).write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')
b=get(BASE);archive=json.loads(b);receipt=[{'url':BASE,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}];parsed=[]
for table in archive['tables']:
 src=table['source'];data=get(src['url']);h=hashlib.sha256(data).hexdigest()
 if h!=src['sha256'] or len(data)!=src['bytes']:raise RuntimeError('Primary supplement differs from archived pin: '+src['file'])
 p=ROOT/src['file'];p.write_bytes(data);sheets=pd.read_excel(p,sheet_name=None,header=None);receipt.append({'url':src['url'],'file':src['file'],'bytes':len(data),'sha256':h});headers={};rows=[];metric='viability_percent' if 's5' in src['file'] else 'ic50_nM'
 for sn,df in sheets.items():
  headers[sn]=df.head(8).where(pd.notna(df),None).values.tolist();save(src['file']+'.headers.json',headers);print('AUTHENTIC_PRIMARY_HEADER '+json.dumps(clean({'file':src['file'],'sheet':sn,'rows':headers[sn]}),allow_nan=False),flush=True)
  for i,row in df.iterrows():
   vals=list(row);hits=[j for j,v in enumerate(vals) if re.fullmatch(r'\d{2,7}-\d{2}-\d',str(v).strip())]
   if not hits:continue
   if len(hits)!=1:raise RuntimeError('Multiple CAS values per row')
   j=hits[0];name=str(vals[j+1]).strip();value=pd.to_numeric(pd.Series([vals[j+2]]),errors='coerce').iloc[0]
   if pd.isna(value):raise RuntimeError('Non-numeric endpoint at row '+str(i+1))
   rr={'cas':str(vals[j]).strip(),'drug':name,metric:float(value),'sheet':sn,'source_row':int(i+1)}
   if metric=='viability_percent':
    sd=pd.to_numeric(pd.Series([vals[j+3]]),errors='coerce').iloc[0]
    if pd.isna(sd):raise RuntimeError('Missing SD at row '+str(i+1))
    rr['sd_percentage_points']=float(sd)
   rows.append(rr)
 old=table['records']
 if len(rows)!=len(old):raise RuntimeError('Supplement row count mismatch')
 oldby={(r['sheet'],r['source_row'],r['cas']):r for r in old}
 for r in rows:
  q=oldby[(r['sheet'],r['source_row'],r['cas'])]
  if abs(r[metric]-q[metric])>1e-8:raise RuntimeError('Numeric extraction mismatch')
  if metric=='viability_percent' and abs(r['sd_percentage_points']-q['sd_percentage_points'])>1e-8:raise RuntimeError('SD extraction mismatch')
 parsed.append(rows);save(src['file']+'.headers.json',headers);save(src['file']+'.records.json',rows)
screen=pd.DataFrame(parsed[0]);ic=pd.DataFrame(parsed[1])
if not screen.cas.is_unique or not ic.cas.is_unique:raise RuntimeError('CAS nonunique; do not silently collapse')
paired=ic.merge(screen,on='cas',how='left',suffixes=('_dose','_screen'),validate='one_to_one')
if paired.viability_percent.isna().any():raise RuntimeError('Selected IC50 CAS absent from screen')
screen['screenRank']=screen.viability_percent.rank(method='average',ascending=True);ic['ic50Rank']=ic.ic50_nM.rank(method='average',ascending=True);paired=paired.merge(screen[['cas','screenRank']],on='cas').merge(ic[['cas','ic50Rank']],on='cas');rho=spearmanr(paired.viability_percent,paired.ic50_nM);paired['withinSelectedScreenRank']=paired.viability_percent.rank(method='average',ascending=True);paired['rankDifferenceIC50MinusScreen']=paired.ic50Rank-paired.withinSelectedScreenRank;forms=[]
for name,cases in FAMILIES.items():
 df=screen[screen.cas.isin(cases)]
 if len(df)<2:continue
 forms.append({'predefinedChemicalFamily':name,'sourceRows':df.to_dict('records'),'screenRangePercentagePoints':float(df.viability_percent.max()-df.viability_percent.min()),'interpretation':'Distinct source CAS rows; replication and comparable formulation concentrations require verification; not salt-specific biology evidence'})
res={'schema':'authentic-emc-screen-replay/1','executedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'model':'NCC-EMC1-C1','independentPatientModels':1,'sourceReceipts':receipt,'primaryExtractionReplay':'All221 screening values/SDs and all24 IC50s match primary workbooks','screenRows':len(screen),'selectedIC50Rows':len(ic),'screenNegative':int((screen.viability_percent<0).sum()),'screenAbove100':int((screen.viability_percent>100).sum()),'screenRange':[float(screen.viability_percent.min()),float(screen.viability_percent.max())],'selectedScreenIC50Spearman':{'rho':float(rho.statistic),'nominalP':float(rho.pvalue),'n':len(paired),'scope':'Selection-conditioned descriptive association; one model, not24 independent biological units'},'endpointRankTable':paired.to_dict('records'),'predefinedFormulationFamilies':forms,'limitations':['Primary concentration/exposure/normalization and IC50 methods must be verified before interpreting endpoint discordance','The24 IC50 compounds are selected, not random among221','Workbook headers retained to verify units; no magnitude-based inference','No pooling with Bangerter or clinical efficacy/selectivity inference','No independent EMC cohort; technical replicates do not create patient units']}
save('execution-summary.json',res);save('source-receipts.json',receipt);print('AUTHENTIC_SCREEN_RESULT_BEGIN');print(json.dumps(clean(res),allow_nan=False));print('AUTHENTIC_SCREEN_RESULT_END')
