import os,json,hashlib,urllib.request,zipfile,io,re,time,datetime
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(os.environ.get('PROTEOMICS_OUTPUT_DIR','campaign-output/proteomics'));ROOT.mkdir(parents=True,exist_ok=True);HERE=Path(__file__).resolve().parent;SOURCE=Path(os.environ.get('PROTEOMICS_MATCHED_SOURCE',str(HERE/'results'/'protein-RNA-matched-measurements.json')))
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
 if isinstance(x,np.integer):return int(x)
 if isinstance(x,np.bool_):return bool(x)
 if isinstance(x,(datetime.date,datetime.datetime,pd.Timestamp)):return x.isoformat()
 return x
def save(name,x):(ROOT/name).write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')
def fetch(url,cap=150*1024**2):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-prior-growth-audit/1'}),timeout=120) as h:b=h.read(cap+1)
 if len(b)>cap:raise ValueError('Frozen source size cap exceeded')
 return b,{'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def prior_art(meta):
 commit='43893810ae38a4ae4f230cfb3f87da9caaa4b822';sources=[];splits={}
 for split in ['train','test']:
  path='machine_learning/intermediate_files/E0022_P06_Protein_Matrix_ProNorM_no_control_'+split+'.txt';url='https://raw.githubusercontent.com/EmanuelGoncalves/cancer_proteomics/'+commit+'/'+path;b,receipt=fetch(url);sources.append(receipt);columns=list(pd.read_csv(io.BytesIO(b),sep='\t',nrows=0).columns);print('PRIOR_SPLIT_HEADER '+json.dumps({'split':split,'receipt':receipt,'columnsFirst':columns[:15]}),flush=True)
  if 'Cell_line' not in columns:raise ValueError('Original split lacks documented Cell_line identifier')
  names=pd.read_csv(io.BytesIO(b),sep='\t',usecols=['Cell_line']).Cell_line.dropna().astype(str);splits[split]=set(names)
 names=meta.Cell_line.fillna('').astype(str);audit=meta[['Cell_line','Cancer_type','relatedGroup','primarySarcomaTest','disputedEMCLabel']].copy()
 for split in splits:audit['original_'+split]=names.isin(splits[split])
 family_split=audit.groupby('relatedGroup')[['original_train','original_test']].any();both=family_split[family_split.original_train&family_split.original_test].index.tolist()
 result={'schema':'author-prior-split-audit/1','sourceCommit':commit,'sources':sources,'originalSplitN':{k:len(v) for k,v in splits.items()},'mappedMeasuredOtherModels':len(meta),'sarcomaInOriginalTraining':audit[audit.primarySarcomaTest&audit.original_train].Cancer_type.value_counts().to_dict(),'sarcomaInOriginalTest':audit[audit.primarySarcomaTest&audit.original_test].Cancer_type.value_counts().to_dict(),'relatedFamiliesAcrossOriginalSplit':both,'scope':'Current measured protein+RNA Othergroup overlap, not all949. Original author correlation and random-fivefold benchmarks already exist. Contribution is class-heldout transfer, calibration, coverage and target-only outcomes; no generic-first claim.','mapping':audit.reset_index().replace({np.nan:None}).to_dict('records')}
 save('author-prior-split-audit.json',result);print('PRIOR_ART_RESULT_BEGIN');print(json.dumps(clean(result),allow_nan=False));print('PRIOR_ART_RESULT_END');return result
def growth_source():
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9387775/supplementaryFiles';b,receipt=fetch(url);save('growth-zip-source-receipt.json',receipt);(ROOT/'primary-procan-supplements.zip').write_bytes(b);z=zipfile.ZipFile(io.BytesIO(b));inventory=[{'name':i.filename,'bytes':i.file_size} for i in z.infolist()];save('primary-procan-supplement-inventory.json',inventory);print('GROWTH_PRIMARY_ZIP '+json.dumps({'source':receipt,'inventory':inventory}),flush=True);candidates=[];headers=[]
 for info in z.infolist():
  if not info.filename.lower().endswith(('.xlsx','.xls')):continue
  if info.file_size>50*1024**2:raise ValueError('Primary workbook exceeds frozen50MiB cap')
  xb=z.read(info);xsrc={'name':info.filename,'bytes':len(xb),'sha256':hashlib.sha256(xb).hexdigest()};xf=pd.ExcelFile(io.BytesIO(xb));print('GROWTH_WORKBOOK_SOURCE '+json.dumps({'source':xsrc,'sheets':xf.sheet_names}),flush=True)
  for sheet in xf.sheet_names:
   preview=xf.parse(sheet_name=sheet,header=None,nrows=30)
   for rowno in range(len(preview)):
    row=preview.iloc[rowno].fillna('').astype(str).str.strip();idcols=[j for j,v in enumerate(row) if re.sub(r'[^a-z0-9]','',v.lower()) in {'modelid','sidm','sangermodelid'}];gcols=[j for j,v in enumerate(row) if 'growth' in v.lower()]
    if not gcols:continue
    head={'source':xsrc,'sheet':sheet,'headerRow':rowno+1,'header':row.tolist(),'firstRows':preview.head(12).replace({np.nan:None}).values.tolist(),'idColumns':idcols,'growthColumns':gcols};headers.append(head);save('primary-growth-header-candidates.json',headers);print('GROWTH_PRIMARY_HEADER '+json.dumps(clean(head),allow_nan=False),flush=True)
    if len(idcols)!=1:continue
    frame=xf.parse(sheet_name=sheet,header=None);body=frame.iloc[rowno+1:];mid=body.iloc[:,idcols[0]].fillna('').astype(str).str.strip();valid=mid.str.startswith('SIDM')
    for col in gcols:
     values=pd.to_numeric(body.iloc[:,col],errors='coerce');good=valid&values.notna();records=[{'model_id':j,'growthValue':float(v)} for j,v in zip(mid[good],values[good])];candidates.append({'source':xsrc,'sheet':sheet,'headerRow':rowno+1,'growthHeader':row.iloc[col],'measuredModelRows':len(records),'duplicateModelIDs':pd.Series([r['model_id'] for r in records],dtype=str).duplicated().sum(),'records':records,'unitsVerified':False,'interpretation':'Published numeric candidate. Confirm exact header/primary footnote is DMSO day4/day1 growth ratio before replacing RNA-proliferation proxy; never infer units from numerical scale.'})
 result={'schema':'primary-measured-growth-reconciliation/1','source':receipt,'inventory':inventory,'headerCandidates':headers,'numericCandidates':candidates,'executedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};save('primary-measured-growth-reconciliation.json',result);print('GROWTH_PRIMARY_RESULT_BEGIN');print(json.dumps(clean(result),allow_nan=False));print('GROWTH_PRIMARY_RESULT_END');return result
if __name__=='__main__':
 if SOURCE.exists():
  data=json.loads(SOURCE.read_text());meta=pd.DataFrame(data['metadata']).set_index('model_id');meta.loc[meta.Cancer_type.eq('Mesothelioma'),'primarySarcomaTest']=False;lung=meta.Cell_line.isin(['EMC-BAC-1','EMC-BAC-2'])&meta.Cancer_type.eq('Non-Small Cell Lung Carcinoma');meta.loc[lung,['disputedEMCLabel','primarySarcomaTest']]=False;prior_art(meta)
 else:raise ValueError('Required durable measured metadata absent')
 growth_source()
