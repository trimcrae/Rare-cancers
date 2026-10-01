import os,json,re,time,hashlib,urllib.request
from pathlib import Path
import numpy as np,pandas as pd,h5py
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression
ROOT=Path(os.environ.get('PROTEOMICS_OUTPUT_DIR','campaign-output/proteomics'));ROOT.mkdir(parents=True,exist_ok=True);CACHE=ROOT/'inputs';CACHE.mkdir(exist_ok=True);HERE=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('PROTEOMICS_MATCHED_SOURCE',str(HERE/'results'/'protein-RNA-final-matched-measurements.json')))
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
  restored=list(Path('restored-artifacts').rglob(f['name']))
  if restored:p=restored[0]
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
def protein_overlap_diagnostics(meta,rna,protein,less,broad,correlation):
 rows=[]
 for gene in ['CD276','CSPG4','L1CAM']:
  if gene not in broad or gene not in rna:continue
  z=pd.DataFrame({'rna':rna[gene],'protein6692':protein[gene],'protein8498':less[gene],'broad':broad[gene]}).join(meta[['relatedGroup','Cancer_type','primarySarcomaTest']]);z=z[z.primarySarcomaTest].groupby(['relatedGroup','Cancer_type'],as_index=False).mean(numeric_only=True)
  common=z.dropna(subset=['rna','protein6692','protein8498','broad']);original=z.dropna(subset=['rna','protein8498','protein6692']);added=z[z.protein6692.isna()].dropna(subset=['rna','protein8498']);paired8498=z.dropna(subset=['rna','protein8498','broad'])
  rows.append({'gene':gene,'ProCan6692to8498SameModels':correlation(z,'protein6692','protein8498'),'ProCan8498toBroadPairwise':correlation(z,'protein8498','broad'),'RNAto8498OriginalQuantifiedSubset':correlation(original,'rna','protein8498'),'RNAto8498AdditionalQuantifiedSubset':correlation(added,'rna','protein8498'),'RNAto8498BroadMatchedSubset':correlation(paired8498,'rna','protein8498'),'RNAtoBroad8498MatchedSubset':correlation(paired8498,'rna','broad'),'allAssaysCommonN':len(common),'allAssaysCommonSourceFamilies':common[['relatedGroup','Cancer_type']].to_dict('records'),'commonSubsetCorrelations':{a+'__'+b:correlation(common,a,b) for a,b in [('rna','protein6692'),('rna','protein8498'),('rna','broad'),('protein6692','broad'),('protein8498','broad')]}})
 return {'schema':'fixed-three-gene-assay-overlap-diagnostic/1','rows':rows,'scope':'Descriptive same-model sensitivity, not frozen predictor error or new clinical validation','limitations':['Quantification-selected subsets; missing is not biological negative','8498 changes identification support; no attribution to one processing step','Broad Other inputs retain author preprocessing; ranks only','Conditional histology-stratified family bootstrap; not simultaneous, training or cross-lab uncertainty']}
published=json.loads(SOURCE.read_text());d=published.get('result',published)
if d.get('schema')!='frozen-sarcoma-matched-measurements/1':raise ValueError('Final source schema mismatch')
if 'execution' in published and published['execution'].get('run_id')!=36896523203:raise ValueError('Require final growth/taxonomy source')
meta=frame(d['metadata'],'model_id');rna=frame(d['rna'],'index');protein=frame(d['protein'],'index');primary=meta.primarySarcomaTest.astype(bool);training=meta.isTraining.astype(bool)
if (len(meta),int(primary.sum()),int(training.sum()))!=(786,61,717):raise ValueError('Final cohort counts mismatch')
with req('https://api.figshare.com/v2/articles/19345397') as h:mb=h.read()
manifest=json.loads(mb);save('cross-assay-source-manifest.json',manifest);receipts.append({'name':'article19345397manifest','sha256':hashlib.sha256(mb).hexdigest(),'bytes':len(mb),'version':manifest.get('version')});files={f['id']:f for f in manifest['files']};lp=fetch(files[34411172]);hp=fetch(files[34411016])
if receipts[-2]['sha256']!='5e7adf7e8217e5a02389c299dce1266e74c7a3b786b8c177e56d12402fe783ac':raise ValueError('Pinned8498 SHA256 mismatch')
if receipts[-1]['sha256']!='839818e7333caec11b2717e63aafc0a0fee2186349573819fc9e06b1f377ef52':raise ValueError('Pinned HDF5 SHA256 mismatch')
raw=pd.read_csv(lp,sep='\t',index_col=0);print('CROSS_ASSAY_8498_SCHEMA '+json.dumps({'shape':list(raw.shape),'indexFirst':raw.index[:5].astype(str).tolist(),'columnsFirst':raw.columns[:5].astype(str).tolist()}),flush=True)
if sum(str(x).startswith('SIDM') for x in raw.index)<sum(str(x).startswith('SIDM') for x in raw.columns):raw=raw.T
raw.index=[str(x).split(';')[0] for x in raw.index];raw=raw.apply(pd.to_numeric,errors='coerce').groupby(level=0).mean();mapping={g:[c for c in raw.columns if a in re.split(r'[;|]',str(c))] for g,a in ACCS.items()};less=pd.DataFrame({g:raw[cols].mean(axis=1) if cols else pd.Series(np.nan,index=raw.index) for g,cols in mapping.items()}).reindex(meta.index);decode=lambda x:x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x)
with h5py.File(hp,'r') as h:
 features=[decode(x) for x in h['features']['proteomics_broad'][...]];samples=[decode(x) for x in h['samples']['Other'][...]];values=h['data']['proteomics_broad']['Other'][...];print('CROSS_ASSAY_BROAD_SCHEMA '+json.dumps({'shape':list(values.shape),'featuresFirst':features[:12],'samplesFirst':samples[:5]}),flush=True)
 if values.shape!=(len(samples),len(features)):raise ValueError('Unexpected Broad HDF5 shape')
 symbols=[re.sub(r'\s+\(\d+\)$','',x) for x in features];broad=pd.DataFrame(values,index=samples,columns=symbols).T.groupby(level=0).mean().T.reindex(meta.index)
diagnostic=protein_overlap_diagnostics(meta,rna,protein,less,broad,correlation)
diagnostic.update({'executedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'primarySarcomaModels':int(primary.sum()),'matchedSourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'receipts':receipts})
save('three-gene-assay-overlap-diagnostic.json',diagnostic)
print('PROTEIN_OVERLAP_DIAGNOSTIC_BEGIN');print(json.dumps(clean(diagnostic),allow_nan=False));print('PROTEIN_OVERLAP_DIAGNOSTIC_END')
