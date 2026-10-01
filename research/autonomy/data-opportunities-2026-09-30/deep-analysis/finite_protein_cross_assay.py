import os,json,re,time,hashlib,urllib.request
from pathlib import Path
import numpy as np,pandas as pd,h5py
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression
ROOT=Path(os.environ.get('PROTEOMICS_OUTPUT_DIR','campaign-output/proteomics'));ROOT.mkdir(parents=True,exist_ok=True);CACHE=ROOT/'inputs';CACHE.mkdir(exist_ok=True);HERE=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('PROTEOMICS_MATCHED_SOURCE',str(HERE/'results'/'protein-RNA-matched-measurements.json')))
PANEL=['CD276','SSTR2','PRAME','FAP','CD248','CSPG4','MSLN','L1CAM','GPC3','ALPP','CDH17','CHRNA6'];CORE3=['CD276','CSPG4','L1CAM'];ACCS=dict(zip(PANEL,['Q5ZPR3','P30874','P78395','Q12884','Q9HCU0','Q6UVK1','Q13421','P32004','P51654','P05187','Q12864','Q15825']))
rng=np.random.default_rng(20261001);receipts=[]
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,np.integer):return int(x)
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
 if isinstance(x,np.bool_):return bool(x)
 return x
def save(name,value):(ROOT/name).write_text(json.dumps(clean(value),indent=2,allow_nan=False)+'\n')
def req(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-finite-cross-assay-audit/1'}),timeout=120)
def fetch(f):
 p=CACHE/f['name']
 if not p.exists():
  temp=p.with_suffix(p.suffix+'.part');n=0
  with req(f['download_url']) as h,temp.open('wb') as w:
   while True:
    b=h.read(4*1024**2)
    if not b:break
    n+=len(b)
    if n>512*1024**2:raise ValueError('Frozen source512MiB cap exceeded')
    w.write(b)
  temp.replace(p)
 md=hashlib.md5();sh=hashlib.sha256()
 with p.open('rb') as h:
  for b in iter(lambda:h.read(4*1024**2),b''):md.update(b);sh.update(b)
 if md.hexdigest()!=(f.get('computed_md5') or f.get('supplied_md5')):raise ValueError('Source MD5 mismatch')
 if p.stat().st_size!=f['size']:raise ValueError('Source size mismatch')
 receipts.append({'id':f['id'],'name':f['name'],'bytes':p.stat().st_size,'md5':md.hexdigest(),'sha256':sh.hexdigest(),'url':f['download_url']});print('CROSS_ASSAY_RETRIEVED '+f['name'],flush=True);return p
def frame(records,index):
 x=pd.DataFrame(records).set_index(index);x.index=x.index.astype(str);return x
def correlation(df,a,b):
 z=df.dropna(subset=[a,b])
 if len(z)<3 or z[a].std()<1e-12 or z[b].std()<1e-12:return {'n':len(z),'rho':None}
 ans={'n':len(z),'rho':float(spearmanr(z[a],z[b]).statistic),'scope':'descriptive family-level rank association'}
 if len(z)>=5:
  boots=[];groups=[v.index.to_numpy() for _,v in z.reset_index(drop=True).groupby('Cancer_type')];za=z[a].to_numpy();zb=z[b].to_numpy()
  for _ in range(1000):
   ix=np.concatenate([rng.choice(g,size=len(g),replace=True) for g in groups])
   if np.std(za[ix])>1e-12 and np.std(zb[ix])>1e-12:boots.append(spearmanr(za[ix],zb[ix]).statistic)
  ans['familyHistologyBootstrapCI95']=np.quantile(boots,[.025,.975]) if boots else None;ans['successfulBootstrapReplicates']=len(boots)
 return ans
d=json.loads(SOURCE.read_text());meta=frame(d['metadata'],'model_id');rna=frame(d['rna'],'index');protein=frame(d['protein'],'index')
meta.loc[meta.Cancer_type.eq('Mesothelioma'),'primarySarcomaTest']=False;meta.loc[meta.BROAD_ID.eq('ACH-000561'),'isTraining']=False
lung=meta.Cell_line.isin(['EMC-BAC-1','EMC-BAC-2'])&meta.Cancer_type.eq('Non-Small Cell Lung Carcinoma');meta.loc[lung,['disputedEMCLabel','isSarcoma','primarySarcomaTest']]=False;meta.loc[lung,'isTraining']=True
primary=meta.primarySarcomaTest.astype(bool);training=meta.isTraining.astype(bool)
with req('https://api.figshare.com/v2/articles/19345397') as h:mb=h.read()
manifest=json.loads(mb);save('cross-assay-source-manifest.json',manifest);receipts.append({'name':'article19345397manifest','sha256':hashlib.sha256(mb).hexdigest(),'bytes':len(mb),'version':manifest.get('version')});files={f['id']:f for f in manifest['files']};lp=fetch(files[34411172]);hp=fetch(files[34411016])
if receipts[-1]['sha256']!='839818e7333caec11b2717e63aafc0a0fee2186349573819fc9e06b1f377ef52':raise ValueError('Pinned HDF5 SHA256 mismatch')
raw=pd.read_csv(lp,sep='\t',index_col=0);print('CROSS_ASSAY_8498_SCHEMA '+json.dumps({'shape':list(raw.shape),'indexFirst':raw.index[:5].astype(str).tolist(),'columnsFirst':raw.columns[:5].astype(str).tolist()}),flush=True)
if sum(str(x).startswith('SIDM') for x in raw.index)<sum(str(x).startswith('SIDM') for x in raw.columns):raw=raw.T
raw.index=[str(x).split(';')[0] for x in raw.index];raw=raw.apply(pd.to_numeric,errors='coerce').groupby(level=0).mean();mapping={g:[c for c in raw.columns if a in re.split(r'[;|]',str(c))] for g,a in ACCS.items()};less=pd.DataFrame({g:raw[cols].mean(axis=1) if cols else pd.Series(np.nan,index=raw.index) for g,cols in mapping.items()}).reindex(meta.index);decode=lambda x:x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x)
with h5py.File(hp,'r') as h:
 features=[decode(x) for x in h['features']['proteomics_broad'][...]];samples=[decode(x) for x in h['samples']['Other'][...]];values=h['data']['proteomics_broad']['Other'][...];print('CROSS_ASSAY_BROAD_SCHEMA '+json.dumps({'shape':list(values.shape),'featuresFirst':features[:12],'samplesFirst':samples[:5]}),flush=True)
 if values.shape!=(len(samples),len(features)):raise ValueError('Unexpected Broad HDF5 shape')
 symbols=[re.sub(r'\s+\(\d+\)$','',x) for x in features];broad=pd.DataFrame(values,index=samples,columns=symbols).T.groupby(level=0).mean().T.reindex(meta.index)
coverage=[];broad_rows=[];unfiltered=[]
for gene in PANEL:
 available=gene in broad;coverage.append({'gene':gene,'lessFilteredFeatureColumns':mapping[gene],'primaryModels':int(primary.sum()),'filtered6692ProteinN':int(protein.loc[primary,gene].notna().sum()),'lessFiltered8498ProteinN':int(less.loc[primary,gene].notna().sum()),'BroadMeasuredFeaturePresent':available,'BroadQuantifiedSarcomaN':int(broad.loc[primary,gene].notna().sum()) if available else 0,'matchedRNALessFilteredN':int((rna.reindex(columns=[gene])[gene].notna()&less[gene].notna()&primary).sum())})
 if gene in rna:
  z=pd.DataFrame({'rna':rna[gene],'less':less[gene]}).join(meta[['Cancer_type','relatedGroup','isTraining','primarySarcomaTest']]).dropna(subset=['rna','less']);z=z.groupby(['relatedGroup','Cancer_type','isTraining','primarySarcomaTest'],as_index=False).mean(numeric_only=True);tr=z[z.isTraining];te=z[z.primarySarcomaTest];result={'gene':gene,'trainN':len(tr),'testN':len(te),'status':'insufficient descriptive support','source':'8498lessfiltered exploratory sensitivity'}
  if len(tr)>=10 and len(te)>=3:
   model=LinearRegression().fit(tr[['rna']],tr.less);pred=model.predict(te[['rna']]);mae=np.abs(te.less-pred).mean();baseline=np.abs(te.less-tr.less.median()).mean();result.update({'status':'evaluated descriptive single-RNA transfer','relativeImprovementOverTrainingMedian':1-mae/baseline if baseline else None,'observedRNAProteinRank':correlation(te,'rna','less')})
  unfiltered.append(result)
 if gene in CORE3 and available and gene in rna:
  z=pd.DataFrame({'rna':rna[gene],'protein6692':protein[gene],'broad':broad[gene]}).join(meta[['relatedGroup','Cancer_type','primarySarcomaTest']]);z=z[z.primarySarcomaTest];z=z.groupby(['relatedGroup','Cancer_type'],as_index=False).mean(numeric_only=True);broad_rows.append({'gene':gene,'RNAtoBroadProtein':correlation(z,'rna','broad'),'ProCan6692toBroadProtein':correlation(z,'protein6692','broad'),'perLineageRNAtoBroadProtein':{c:correlation(v,'rna','broad') for c,v in z.groupby('Cancer_type')}})
result={'schema':'finite-protein-coverage-cross-assay-sensitivity/1','executedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'matchedSourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'receipts':receipts,'primarySarcomaModels':int(primary.sum()),'coverage':coverage,'lessFilteredSingleRNATransfers':unfiltered,'independentMeasurementRankChecks':broad_rows,'limitations':['8498 includes weaker identifications; fixed primary6692 estimand is not replaced by favorable sensitivity','Broad author-processed whole-cell measured inputs in Othergroup only; rank-only checks; no unit restoration claim','Same cell systems across assays are not independent patients or verified EMC','All12 fixed panel/control coverage failures reported; only three core-supported genes receive rank validation','Bootstrap intervals conditional on observed histology support and not simultaneous','Detection selection and whole-cell-to-surface gap remain']}
save('finite-cross-assay-execution-summary.json',result);print('CROSS_ASSAY_RESULT_BEGIN');print(json.dumps(clean(result),allow_nan=False));print('CROSS_ASSAY_RESULT_END')
