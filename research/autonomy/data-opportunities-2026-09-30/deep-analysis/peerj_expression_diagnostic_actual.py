import json,io,zipfile,hashlib,datetime,re,collections
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import rankdata,spearmanr,pearsonr
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
import pediatric_and_ewing_processed_exports_actual as exp
import atlas_panel_extension as atlas
OUT=sm.OUT;NAME='peerj-14-21497-s009.xlsx';PIN='20165fd3ff09ec2d5a24b3c20b78515f42a3309119f248ed055c7484deb45e75';SIZE=1423709;IDS=['Si01','Si02','Si05','Si09','Si10','Si14','Si15','Si16','Si17','Si19','Si20','Si22'];GENES=['PXN','TYMS','H1FX'];PAIRS=[('PXN','TYMS'),('PXN','H1FX'),('TYMS','H1FX')];FLOOR=.010026459
AMENDMENT={'dated_utc':'2026-10-01','selection':'Full9500gene×12specimenexport/frozen3genes/all3pairs','variants':['publishedlog2CPM','specimenmidrank9500','maskrepeated.010026459±5e-10','maskat/belowbottomquartile'],'repeated_value':'Exportdiagnostic notestablisheddetectionfloor','identity':'SpecimenIDs no linkedoutcomes/rawdepth','limits':'No prognosisfit/DE/signature/markermechanism; originalauthorselectedgenes'}
def get():
 paths=sorted({p for root in [OUT,Path('restored-artifacts'),Path('restored-artifacts-extra')] for p in root.rglob(NAME)})
 if paths:
  for p in paths:assert p.stat().st_size==SIZE and hashlib.sha256(p.read_bytes()).hexdigest()==PIN
  return paths[0],{'saved':str(paths[0]),'bytes':SIZE,'sha256':PIN,'source':'restoredfrozenmember'}
 p,r=sm.getfull('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13374579/supplementaryFiles','PeerJ-complete-supplements.zip',32*1024**2)
 with zipfile.ZipFile(p) as z:
  hits=[v for v in z.namelist() if Path(v).name==NAME];assert len(hits)==1;b=z.read(hits[0]);assert len(b)==SIZE and hashlib.sha256(b).hexdigest()==PIN;target=OUT/NAME;target.write_bytes(b)
 return target,{'saved':str(target),'bytes':SIZE,'sha256':PIN,'source_zip_member':hits[0],'container_receipt':r,'container_identity_rule':'RegeneratedZIPreceipt retained; exactmember frozen'}
def association(a,b):
 valid=np.isfinite(a)&np.isfinite(b);x=a[valid];y=b[valid];n=len(x);r={'n_source_specimens':n,'included_specimens':np.asarray(IDS)[valid].tolist(),'excluded_specimens':np.asarray(IDS)[~valid].tolist()}
 if n<4 or np.unique(x).size<2 or np.unique(y).size<2:return {**r,'status':'constant_or_insufficient'}
 rho,p=spearmanr(x,y);pear,pp=pearsonr(x,y);loo=[]
 for k in range(n):
  xx=np.delete(x,k);yy=np.delete(y,k);v=float(spearmanr(xx,yy).statistic) if np.unique(xx).size>1 and np.unique(yy).size>1 else None;loo.append({'excluded_specimen':r['included_specimens'][k],'Spearman_rho':v})
 return {**r,'status':'measured','Spearman_rho':float(rho),'Spearman_unadjusted_p':float(p),'Pearson_r':float(pear),'Pearson_unadjusted_p':float(pp),'leave_one_specimen_out':loo,'leave_one_out_finite_range':[min(v['Spearman_rho'] for v in loo if v['Spearman_rho'] is not None),max(v['Spearman_rho'] for v in loo if v['Spearman_rho'] is not None)]}
def main():
 OUT.mkdir(parents=True,exist_ok=True);p,r=get();book=src.xlsx_tables(p.read_bytes());s=next(t for t in book['tables'] if t['sheet']=='EMC_Gene-expression_Log2CPM');rows=s['rows'];assert rows[0]==['symbol']+IDS and len(rows)==9501 and all(len(v)==13 for v in rows[1:]);symbols=[str(v[0]).strip() for v in rows[1:]];vals=np.array([[float(x) for x in row[1:]] for row in rows[1:]],float);assert vals.shape==(9500,12) and np.isfinite(vals).all();lookup=collections.defaultdict(list)
 for i,symbol in enumerate(symbols):lookup[symbol].append(i)
 ranks=rankdata(vals,axis=0,method='average')/9500;repeated=np.abs(vals-FLOOR)<=5e-10;quartiles=np.quantile(vals,.25,axis=0);low=vals<=quartiles;mapping={};selected={}
 for gene in GENES:
  candidates=[gene]+(['H1-10'] if gene=='H1FX' else []);hits=[(name,i) for name in candidates for i in lookup.get(name,[])];mapping[gene]={'exact_or_explicit_alias_candidates':candidates,'matching_rows':hits,'used_unique':len(hits)==1}
  if len(hits)==1:selected[gene]=hits[0][1]
 variants={'original_log2CPM':vals,'specimen_midrank':ranks,'repeated_value_censored':np.where(repeated,np.nan,vals),'bottom_quartile_censored':np.where(low,np.nan,vals)};tests=[]
 for variant,v in variants.items():
  for left,right in PAIRS:
   if left not in selected or right not in selected:tests.append({'variant':variant,'left':left,'right':right,'status':'missing_or_ambiguous_gene','absence_claim':False});continue
   tests.append({'variant':variant,'left':left,'right':right,**association(v[selected[left]],v[selected[right]])})
 order=sorted([(i,t['Spearman_unadjusted_p']) for i,t in enumerate(tests) if 'Spearman_unadjusted_p' in t],key=lambda z:z[1]);q=1.
 for k in range(len(order)-1,-1,-1):i,pv=order[k];q=min(q,pv*12/(k+1));tests[i]['BH_q_fixed12_descriptive']=q
 targets=[]
 for gene in sorted(exp.TARGETS):
  hits=lookup.get(gene,[]);targets.append({'gene':gene,'matching_rows_0based':hits,'published_log2CPM':dict(zip(IDS,vals[hits[0]].tolist())) if len(hits)==1 else None,'specimen_midrank':dict(zip(IDS,ranks[hits[0]].tolist())) if len(hits)==1 else None,'missing_symbol_is_biological_absence':False})
 panels=[]
 for name,members in atlas.GROUPS.items():
  present=[g for g in members if len(lookup.get(g,[]))==1];missing=[g for g in members if len(lookup.get(g,[]))!=1];panels.append({'historical_panel':name,'frozen_membership':members,'unique_present':present,'missing_or_ambiguous':missing,'specimen_mean_member_midrank':dict(zip(IDS,ranks[[lookup[g][0] for g in members]].mean(axis=0).tolist())) if not missing else None,'interpretation':'Existingmembership notfit/activity/betweendiagnosis'})
 table=pd.DataFrame(vals,index=symbols,columns=IDS);target_names=[g for g in sorted(exp.TARGETS) if len(lookup.get(g,[]))==1];table.loc[target_names].to_csv(OUT/'PeerJ-frozen-target-published-expression.tsv',sep='\t');result={'schema':'emc-PeerJ-fixed-expression-diagnostic/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'source_receipt':r,'matrix_shape':list(vals.shape),'duplicate_symbols':{k:len(v) for k,v in lookup.items() if len(v)>1},'numeric_or_date_style_symbol_rows':[{'row_1based':i+2,'literal_symbol':s} for i,s in enumerate(symbols) if re.fullmatch(r'\d+(?:\.\d+)?',s) or re.search(r'\d{4}-\d\d-\d\d',s)],'source_symbol_cell_styles':{k:v for k,v in s['cell_style_indices'].items() if re.fullmatch(r'A\d+',k)},'cell_style_frequencies':dict(collections.Counter(s['cell_style_indices'].values())),'specimen_export_diagnostics':[{'specimen':sid,'log2CPM_quantiles':np.quantile(vals[:,j],[0,.25,.5,.75,1]).tolist(),'repeated_value_rows':int(repeated[:,j].sum()),'bottom_quartile_censored_rows':int(low[:,j].sum())} for j,sid in enumerate(IDS)],'gene_mapping':mapping,'all12_fixed_pair_sensitivities':tests,'all_frozen_target_expression':targets,'historical_panel_descriptive_context':panels,'no_linked_individual_outcomes':True};dest=OUT/'PeerJ-fixed-expression-diagnostic-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEERJ_FIXED_DIAGNOSTIC_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEERJ_FIXED_DIAGNOSTIC_END')
if __name__=='__main__':main()
