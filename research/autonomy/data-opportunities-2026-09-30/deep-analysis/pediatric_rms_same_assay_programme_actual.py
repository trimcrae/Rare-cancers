import json,hashlib,datetime
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import rankdata
import spatial_marker_followthrough_actual as sm
from atlas_panel_extension import GROUPS
OUT=sm.OUT
PIN='7f8bc0b9cd39e96eb5376b6085f263db016d5304a59222dedd12461f9875272c'
SENS=['human_UMI_ge500','all_source_barcodes','all_reference_UMI_ge500']
ENDS=['fraction_detected','fraction_summed_human_UMI']
def scores(a):
 r=rankdata(a,axis=-2,method='average')
 return rankdata(r.sum(axis=-1),axis=-1,method='average')
def corr(a,b):
 a=a-a.mean(axis=-1,keepdims=True);b=b-b.mean(axis=-1,keepdims=True)
 den=np.sqrt((a*a).sum(axis=-1)*(b*b).sum(axis=-1))
 return np.divide((a*b).sum(axis=-1),den,out=np.full(den.shape,np.nan),where=den>0)
def bh(recs,n,key):
 order=sorted([(i,r['permutation_p']) for i,r in enumerate(recs) if r.get('permutation_p') is not None],key=lambda z:z[1]);q=1.
 for k in range(len(order)-1,-1,-1):
  i,p=order[k];q=min(q,p*n/(k+1));recs[i][key]=q
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 paths=sorted({p for root in [OUT,Path('restored-artifacts'),Path('restored-artifacts-extra'),Path('restored-artifacts-third')] for p in root.rglob('RMS-all42-measured-targets-compact.json')})
 good=[p for p in paths if hashlib.sha256(p.read_bytes()).hexdigest()==PIN];assert good,'Restore completed36921291739 compact output'
 path=good[0];d=json.loads(path.read_text());assert d['schema']=='emc-RMS-all42-measured-targets/1' and len(d['libraries'])==42
 rows=[];ids=[]
 for lib in d['libraries']:
  identity=lib['identity_audit']
  if identity['source_class']!='human_tumor' or identity['assay']!='snRNA':continue
  ids.append({'GSM':lib['GSM'],**identity})
  for v in lib['measured_counts']['all_frozen_target_summaries']:rows.append({**v,'root':identity['literal_model_root'],'GSM':lib['GSM']})
 assert len(ids)==18 and len({r['literal_model_root'] for r in ids})==14
 f=pd.DataFrame(rows);assert len(f)==18*88*3
 assert len(GROUPS)==13
 genes=sorted(set(['CSPG4']+sum(GROUPS.values(),[])));tests=[];values=[]
 for si,sens in enumerate(SENS):
  sf=f[f.barcode_sensitivity==sens];assert sf.groupby('gene').feature_mapped.all().reindex(genes).all()
  for ei,end in enumerate(ENDS):
   mat=sf.groupby(['root','gene'])[end].mean().unstack('gene').reindex(columns=genes)
   assert mat.shape==(14,len(genes)) and np.isfinite(mat.to_numpy()).all()
   roots=mat.index.tolist();x=mat['CSPG4'].to_numpy();n=len(x);xr=rankdata(x,method='average')
   values.append({'barcode_sensitivity':sens,'endpoint':end,'roots':roots,'gene_columns':genes,'equal_library_mean_values':mat.to_numpy().tolist()})
   for gi,(name,members) in enumerate(GROUPS.items()):
    used=[g for g in members if g!='CSPG4'];a=mat[used].to_numpy();sr=scores(a);rho=float(corr(xr,sr))
    rng=np.random.default_rng(2026100130+si*10000+ei*100+gi)
    rec={'panel':name,'endpoint':end,'barcode_sensitivity':sens,'frozen_membership':members,'scored_membership':used,'CSPG4_part_whole_removed':'CSPG4' in members,'n_literal_roots':n,'root_ids':roots,'CSPG4_values':x.tolist(),'module_score_midrank':sr.tolist(),'spearman_rho':rho if np.isfinite(rho) else None}
    if np.isfinite(rho):
     perms=np.array([rng.permutation(xr) for _ in range(10000)]);null=corr(perms,np.broadcast_to(sr,perms.shape));assert np.isfinite(null).all()
     ix=rng.integers(0,n,(2000,n));boots=corr(rankdata(x[ix],axis=1,method='average'),scores(a[ix]));finite=boots[np.isfinite(boots)]
     loo=[]
     for j in range(n):
      keep=np.arange(n)!=j;v=float(corr(rankdata(x[keep],method='average'),scores(a[keep])));loo.append({'omitted_root':roots[j],'rho':v if np.isfinite(v) else None})
     rec.update(permutation_p=float((1+np.sum(np.abs(null)>=abs(rho)-1e-14))/10001),permutation_draws=10000,reranked_bootstrap_attempts=2000,finite_bootstrap_draws=int(len(finite)),constant_bootstrap_draws_discarded=int(2000-len(finite)),reranked_bootstrap95=np.quantile(finite,[.025,.975]).tolist() if len(finite) else None,leave_one_root_out=loo)
    else:rec['undefined_reason']='Constant target or fixed module score; no biological absence claim'
    tests.append(rec)
  fam=[r for r in tests if r['barcode_sensitivity']==sens];assert len(fam)==26;bh(fam,26,'BH_q_fixed26')
 assert len(tests)==78;bh(tests,78,'BH_q_all78')
 out={'schema':'emc-RMS-same-assay-frozen-programme/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'extension_record':{'dated_before_new_fits':'2026-10-01','scope':'Exploratory fixed13-panel extension;2 RNA endpoints×3 barcode sensitivities','membership_source':'atlas_panel_extension.py blob e617ffc29afe3febb5291ace524adafd343b31c0','source_selection':'All18 human-snRNA libraries equally averaged within14 literal roots','score':'Sum per-gene across-root midranks then rank score for Spearman, equivalent equal positive mean without floating tie break; reranked after root resampling/deletion','part_whole':'CSPG4 removed from its core-protein panel; other fixed genes unchanged','testing':'10000 two-sided target-root permutations; BH26 each sensitivity and BH78 complete family;2000 reranked bootstrap attempts','technical_covariates':'None; no filtered-barcode QC mean assumed'},'source_receipt':{'saved':str(path),'bytes':path.stat().st_size,'sha256':PIN},'human_snRNA_library_identity':ids,'all_root_gene_endpoint_values':values,'all78_tests':tests,'limits':['Literal roots are not verified independent clinical patients','Same assay does not remove composition/genotype/batch effects','RNA associations do not measure malignant cells, protein, glycan, sulfation, activity or treatment','Equal positive module coefficients are historical annotations, not validated pathway activities','Exploratory; no external validation']}
 dest=OUT/'RMS-same-assay-frozen-programme-actual.json';dest.write_text(json.dumps(sm.clean(out),allow_nan=False))
 print('EMC_RMS_SAME_ASSAY_PROGRAMME_BEGIN');print(json.dumps(sm.clean(out),allow_nan=False));print('EMC_RMS_SAME_ASSAY_PROGRAMME_END')
if __name__=='__main__':main()
