#!/usr/bin/env python3
import io,json,hashlib,urllib.request,zipfile,datetime
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path('campaign-output/proteomics');ROOT.mkdir(parents=True,exist_ok=True)
ZIP_SHA='67010b969bd95de6d70129d71a6a5b229aff1715b106f05e54a04b9d049b8438'
XLS_SHA='9327f665d259ef4d148d3a64e7c76cdeb51dce8dee06768efd6b7d044130e203'
URL='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9387775/supplementaryFiles'
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple,np.ndarray)):return [clean(v) for v in x]
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
 if isinstance(x,(np.integer,np.bool_)):return x.item()
 if isinstance(x,(datetime.date,datetime.datetime,pd.Timestamp)):return x.isoformat()
 return x
def save(name,x):(ROOT/name).write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')
paths=[ROOT/'primary-procan-supplements.zip'];restored=Path('restored-artifacts')
if restored.exists():paths+=list(restored.rglob('primary-procan-supplements.zip'))
p=next((v for v in paths if v.exists()),None)
if p is None:
 with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'Rare-cancers-targeted-growth-audit/1'}),timeout=120) as r:b=r.read(160*1024**2+1)
 if len(b)>160*1024**2:raise ValueError('Frozen supplement160MiB cap exceeded')
 p=ROOT/'primary-procan-supplements.zip';p.write_bytes(b)
else:b=p.read_bytes()
if hashlib.sha256(b).hexdigest()!=ZIP_SHA:raise ValueError('Pinned supplement-container mismatch')
receipt={'url':URL,'bytes':len(b),'sha256':ZIP_SHA,'localPath':str(p),'restoredArtifact':11172625155}
with zipfile.ZipFile(io.BytesIO(b)) as z:xb=z.read('mmc2.xlsx')
if len(xb)!=960365 or hashlib.sha256(xb).hexdigest()!=XLS_SHA:raise ValueError('Pinned growth workbook mismatch')
xf=pd.ExcelFile(io.BytesIO(xb));legend=xf.parse('Legend',header=None);preview=xf.parse('Cell line level sample info',header=None,nrows=12)
header={'containerReceipt':receipt,'workbook':'mmc2.xlsx','workbookSHA256':XLS_SHA,'sheet':'Cell line level sample info','headerRow':2,'preview':preview.replace({np.nan:None}).values.tolist(),'legend':legend.replace({np.nan:None}).values.tolist()}
save('primary-growth-exact-header.json',header);print('GROWTH_EXACT_PRIMARY_HEADER '+json.dumps(clean(header),allow_nan=False),flush=True)
frame=xf.parse('Cell line level sample info',header=1)
if not {'model_id','growth'}.issubset(frame):raise ValueError('Actual primary growth header mismatch')
mid=frame.model_id.fillna('').astype(str);values=pd.to_numeric(frame.growth,errors='coerce');good=mid.str.startswith('SIDM')&values.notna()
records=[{'model_id':j,'growthValue':float(v)} for j,v in zip(mid[good],values[good])]
result={'schema':'primary-measured-growth-reconciliation/2','source':receipt,'workbookSHA256':XLS_SHA,'sheet':'Cell line level sample info','growthHeader':'growth','measuredModelRows':len(records),'duplicateModelIDs':int(pd.Series([r['model_id'] for r in records],dtype=str).duplicated().sum()),'records':records,'unitsVerified':False,'unitVerificationRequired':'Use exact primary methods definition; do not infer whether ratio, log-ratio or rate from numerical magnitudes.'}
save('primary-measured-growth-reconciliation.json',result);print('GROWTH_PRIMARY_RESULT_BEGIN');print(json.dumps(clean(result),allow_nan=False));print('GROWTH_PRIMARY_RESULT_END',flush=True)
