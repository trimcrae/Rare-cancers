import json,hashlib,datetime
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import rankdata
import pediatric_processed_numeric_actual as original
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT;ROOTS=[Path('restored-artifacts'),Path('restored-artifacts-extra'),OUT]
def one(name):
 pp=sorted({p for root in ROOTS for p in root.rglob(name)});assert pp;assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in pp})==1;return pp[0]
def main():
 p=one('pediatric-public-numeric-actual.json');d=json.loads(p.read_text());d=d.get('result',d);assert d['schema']=='emc-pediatric-public-numeric/1';tp=one('pediatric-identifier-cluster-QC-composition.tsv');frame=pd.read_csv(tp,sep='\t');assert len(frame)==62 and frame.identifier_cluster.nunique()==62;out=[]
 for i,left in enumerate(original.QC):
  endpoints=['malignant']
  for cell in original.CELLS:endpoints.extend([cell,cell+' within nonmalignant percent'])
  for j,right in enumerate(endpoints):
   old=next(t for t in d['all33_fixed_quality_composition_tests'] if t['QC_metric']==left and t['composition_endpoint']==right);g=frame.dropna(subset=[left,right]);n=len(g);xraw=g[left].to_numpy(float);yraw=g[right].to_numpy(float);e=g.entity.to_numpy();x=rankdata(xraw)/n;y=rankdata(yraw)/n;point=original.corr(x,y,e);assert abs(point-old['entity_adjusted_rank_rho'])<1e-12;groups=[np.flatnonzero(e==k) for k in np.unique(e)];rng=np.random.default_rng(original.SEED+12000+i*100+j)
   for unused in range(10000):
    for z in groups:rng.permutation(z)
   fixed=[];reranked=[]
   for unused in range(2000):
    idx=np.concatenate([rng.choice(z,len(z),replace=True) for z in groups]);v=original.corr(x[idx],y[idx],e[idx]);w=original.corr(rankdata(xraw[idx])/n,rankdata(yraw[idx])/n,e[idx])
    if np.isfinite(v):fixed.append(v)
    if np.isfinite(w):reranked.append(w)
   old_ci=np.quantile(fixed,[.025,.975]);assert np.max(np.abs(old_ci-np.asarray(old['stratified_identifier_cluster_bootstrap95'])))<1e-12,'Cannot reproduceoriginalCI';record=dict(old);record['original_fixed_rank_resample95']=old_ci.tolist();record['reranked_identifier_cluster_bootstrap95']=np.quantile(reranked,[.025,.975]).tolist();record['bootstrap_finite_draws']=len(reranked);record['bootstrap_discarded_constant_draws']=2000-len(reranked);record['stratified_identifier_cluster_bootstrap95']=record['reranked_identifier_cluster_bootstrap95'];out.append(record)
 assert len(out)==33;result={'schema':'emc-pediatric-reranked-bootstrap/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':{'dated_utc':'2026-10-01','reason':'Recompute ranks in everystratifiedresampledidentifier draw; reproduce/retainoriginalfixedrankCI','unchanged':'All33points/withinentitypermutationp/BH33; no newendpoints','identity':'62identifierprefixgroups notverifiedpatients'},'sources':[{'saved':str(v),'bytes':v.stat().st_size,'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for v in [p,tp]],'all33_fixed_quality_composition_tests':out};dest=OUT/'pediatric-reranked-bootstrap-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_RERANKED_BOOTSTRAP_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_RERANKED_BOOTSTRAP_END')
if __name__=='__main__':main()
