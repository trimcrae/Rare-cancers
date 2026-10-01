import argparse,json,csv,re,hashlib,datetime,collections
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
import pediatric_and_ewing_processed_exports_actual as exp
import atlas_panel_extension as atlas
OUT=sm.OUT;SEED=20261001
PINS={'a45759fd4aaaf001e2897ff2':'68a0778e88c24cc5aac825b6eacd06d3309060902dbe442bfdaddb63eb8f0d20','878d9cc368e36466cbbbb537':'9bb442c1a8b8e751e4ef125d527c24fcfc8a8caa734a7208ed351285d2eddb18','383819d0ac9d17d45f6df4d3':'fb5dcacf81361815f4cdf715104354be5d9cc605d1641b8ac055a127b58203e6','612a1c3ddfcb119bdceef161':'c1f160747729128e5e445cb79b9f369ba2f289c68e5d9bc4bcf99edbe91addde','22cef30afd9e9b61fdb72a80':'d76b95af6b73cf3e3cb2804710d2cc6f9584c4dd2c65673a96ff4f0e0a793797'}
CELLS=['CD4+ T','CD8+ T','Macrophages','Fibroblasts','Endothelial cells'];QC=['Median Genes per Cell','Median UMI Counts per Cell','Fraction Reads in Cells']
AMENDMENT={'dated_utc':'2026-10-01','format_fix':'Actual Table2/fullTable3 contain CSV records in one XLSX cell; decode authoritative CSV fields before matching. Wholecell no-match was not gene absence.','genes':'Exact frozen exp.TARGETS/atlas.GROUPS. AuthorDGE scores/logfoldchanges/p-values inherited, not independent patient DE or EMC validation.','composition':'Five fixed celltypes percentallnuclei/percentnonmalignant, plusmalignantpct; zero denominator withheld.','QC':'3metrics x11endpoints; equal specimen means within62identifier-prefix clusters; broadentity-adjusted rank residual correlation,10000within-entityclusterpermutations,BH33,2000stratifiedclusterbootstrap. Association not causal depth correction.','identity':'Remove final numeric specimen suffix;62prefixgroups matches paper62patients but no independent clinical identity mapping.','limits':'No clinical outcomes/rawcounts; EGA EGAS50000000393 controlled; predictedLR not functional receptor evidence.'}
def frame(t,embedded=False):
 r=t['rows'];r=[next(csv.reader([str(x[0])])) for x in r] if embedded else r;h=r[0];assert len(h)==len(set(h)) and all(len(x)==len(h) for x in r[1:]);return pd.DataFrame(r[1:],columns=h)
def corr(x,y,e):
 x=np.asarray(x,float).copy();y=np.asarray(y,float).copy()
 for k in np.unique(e):z=e==k;x[z]-=x[z].mean();y[z]-=y[z].mean()
 d=np.linalg.norm(x)*np.linalg.norm(y);return float(x@y/d) if d>0 else np.nan
def test(f,left,right,seed):
 g=f.dropna(subset=[left,right]);n=len(g);e=g.entity.to_numpy();x=rankdata(g[left])/n;y=rankdata(g[right])/n;v=corr(x,y,e);r={'QC_metric':left,'composition_endpoint':right,'n_identifier_clusters':n,'entity_counts':g.entity.value_counts().to_dict(),'within_entity_descriptive':[]}
 for k,z in g.groupby('entity'):r['within_entity_descriptive'].append({'entity':k,'n':len(z),'rho':float(spearmanr(z[left],z[right]).statistic) if len(z)>=3 and z[left].nunique()>1 and z[right].nunique()>1 else None})
 if not np.isfinite(v):return {**r,'status':'Constant/insufficient endpoint'}
 rng=np.random.default_rng(seed);groups=[np.flatnonzero(e==k) for k in np.unique(e)];null=[]
 for unused in range(10000):
  p=np.arange(n)
  for z in groups:p[z]=rng.permutation(z)
  null.append(corr(x[p],y,e))
 boot=[]
 for unused in range(2000):
  p=np.concatenate([rng.choice(z,len(z),replace=True) for z in groups]);b=corr(x[p],y[p],e[p])
  if np.isfinite(b):boot.append(b)
 return {**r,'status':'measured','entity_adjusted_rank_rho':v,'identifier_cluster_permutation_p':float((1+np.sum(np.abs(null)>=abs(v)))/10001),'stratified_identifier_cluster_bootstrap95':np.quantile(boot,[.025,.975]).tolist() if boot else None}
def main():
 p=argparse.ArgumentParser();p.add_argument('--input-root',action='append');a=p.parse_args();roots=[Path(v) for v in (a.input_root or ['restored-artifacts',str(OUT)])];paths={};books={}
 for key,pin in PINS.items():
  pp=sorted({p for root in roots for p in root.rglob('pediatric-'+key+'.xlsx')});assert pp
  for path in pp:assert hashlib.sha256(path.read_bytes()).hexdigest()==pin
  paths[key]=pp[0];books[key]=src.xlsx_tables(pp[0].read_bytes())['tables']
 qc=frame(books['878d9cc368e36466cbbbb537'][0],True);dge=frame(next(t for t in books['383819d0ac9d17d45f6df4d3'] if t['sheet']=='cancer_rank_genes_groups_full'),True);tme=frame(books['612a1c3ddfcb119bdceef161'][0]);assert dge.columns.tolist()==['group','gene','scores','logfoldchanges','pvals','pvals_adj'];assert qc['sample'].is_unique and tme['sample'].is_unique
 for f,skip in [(qc,['sample','folder']),(tme,['sample']),(dge,['group','gene'])]:
  for col in f.columns:
   if col not in skip:f[col]=pd.to_numeric(f[col],errors='raise')
 vals=tme.drop(columns='sample').to_numpy(float);sums=vals.sum(axis=1);assert np.isfinite(vals).all() and (vals>=0).all() and (vals<=100).all() and np.max(np.abs(sums-100))<=.1 and len(tme)==89;g=tme.merge(qc,on='sample',how='left',validate='one_to_one',indicator=True);assert (g['_merge']=='both').all();g=g.drop(columns='_merge');keys=[re.fullmatch(r'(CIPPST_(EWS|OST|STS)_\d+)_\d+',s) for s in g['sample']];assert all(keys);g['identifier_cluster']=[m.group(1) for m in keys];g['entity']=[m.group(2) for m in keys];assert g.identifier_cluster.nunique()==62;den=100-g.malignant;endpoints=['malignant']
 for cell in CELLS:name=cell+' within nonmalignant percent';g[name]=np.where(den>0,g[cell]/den*100,np.nan);endpoints.extend([cell,name])
 agg=g.groupby(['identifier_cluster','entity'])[QC+endpoints].mean().reset_index();agg.to_csv(OUT/'pediatric-identifier-cluster-QC-composition.tsv',sep='\t',index=False);summary=[]
 for entity,z in g.groupby('entity'):summary.append({'entity':entity,'specimens':len(z),'identifier_clusters':int(z.identifier_cluster.nunique()),'malignant_percent_quantiles':np.quantile(z.malignant,[0,.25,.5,.75,1]).tolist(),'nonmalignant_zero_denominator_specimens':z.loc[z.malignant==100,'sample'].tolist(),'fixed_cell_percent_quantiles':{c:np.quantile(z[c],[0,.25,.5,.75,1]).tolist() for c in CELLS}})
 tests=[test(agg,m,v,SEED+12000+i*100+j) for i,m in enumerate(QC) for j,v in enumerate(endpoints)];order=sorted([(i,r['identifier_cluster_permutation_p']) for i,r in enumerate(tests) if 'identifier_cluster_permutation_p' in r],key=lambda x:x[1]);q=1.
 for k in range(len(order)-1,-1,-1):i,v=order[k];q=min(q,v*33/(k+1));tests[i]['BH_q_fixed33']=q
 target=dge[dge.gene.isin(exp.TARGETS)].copy();target.to_csv(OUT/'pediatric-frozen-target-author-DEG.tsv',sep='\t',index=False);audit=[];panels=[]
 for entity,z in dge.groupby('group'):
  z=z.copy();z['midrank']=rankdata(z.scores)/len(z);lookup=collections.defaultdict(list)
  for i,gene in enumerate(z.gene):lookup[gene].append(i)
  audit.append({'author_entity':entity,'gene_rows':len(z),'unique_genes':int(z.gene.nunique()),'duplicate_gene_rows':int(z.gene.duplicated().sum()),'zero_author_pvals':int((z.pvals==0).sum()),'frozen_targets_present':sorted(set(z.gene)&exp.TARGETS),'frozen_targets_missing':sorted(exp.TARGETS-set(z.gene))})
  for name,members in atlas.GROUPS.items():
   ok=[v for v in members if len(lookup[v])==1];missing=[v for v in members if len(lookup[v])!=1];r={'author_entity':entity,'historical_panel':name,'frozen_membership':members,'present_unique':ok,'missing_or_ambiguous':missing,'coverage':len(ok)/len(members),'scoring':'Mean within-author-entity rankedDGEscore, differsfromwithin-specimenRNA rank; context only'}
   if not missing:v=z.iloc[[lookup[x][0] for x in members]];r.update(mean_author_score_midrank=float(v.midrank.mean()),member_author_logfoldchanges=dict(zip(v.gene,v.logfoldchanges.astype(float))),all_members_numeric_finite=bool(np.isfinite(v[['scores','logfoldchanges']].to_numpy(float)).all()))
   panels.append(r)
 unique=frame(next(t for t in books['22cef30afd9e9b61fdb72a80'] if t['sheet']=='Unique_sarcoma_interactions_fil'));shared=frame(next(t for t in books['22cef30afd9e9b61fdb72a80'] if t['sheet']=='Sarcoma_shared_interactions'),True);interactions=[]
 for row in unique.to_dict(orient='records'):
  left,right=row['Unique_interaction'].split('->');hit=sorted(set([left]+right.split('_'))&exp.TARGETS)
  if hit:interactions.append({'author_entity':row['Entity'],'published_interaction':row['Unique_interaction'],'frozen_symbols_matched':hit,'evidence':'PublishedinferredLRassignment,notprotein/functionmeasurement'})
 result={'schema':'emc-pediatric-public-numeric/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'source_receipts':[{'path':str(v),'bytes':v.stat().st_size,'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for v in paths.values()],'decoded_full_DGE_shape':list(dge.shape),'author_entity_gene_audit':audit,'frozen_target_author_rows':target.to_dict(orient='records'),'historical_panel_author_context':panels,'QC_libraries':len(qc),'TME_specimens':len(tme),'identifier_clusters':int(agg.identifier_cluster.nunique()),'QC_without_TME':qc.loc[~qc['sample'].isin(tme['sample'])].to_dict(orient='records'),'TME_percentage_row_sum_range':[float(sums.min()),float(sums.max())],'sample_composition_summary':summary,'all33_fixed_quality_composition_tests':tests,'unique_LR_counts_by_author_entity':unique.Entity.value_counts().to_dict(),'frozen_LR_context_matches':interactions,'published_shared_LR':shared.to_dict(orient='records'),'derived_tables':[str(OUT/'pediatric-identifier-cluster-QC-composition.tsv'),str(OUT/'pediatric-frozen-target-author-DEG.tsv')],'limits':'No EMC entity; no patient outcome/rawcount fit. Allpublicderivednumericcontext analyzed; separateRMSGSE174376 alternate remainsfinitelead.'};dest=OUT/'pediatric-public-numeric-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_PUBLIC_NUMERIC_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_PUBLIC_NUMERIC_END')
if __name__=='__main__':main()
