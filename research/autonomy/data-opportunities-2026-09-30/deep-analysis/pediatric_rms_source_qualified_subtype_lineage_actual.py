import json,gzip,io,csv,re,hashlib,itertools,datetime,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import rankdata
from pediatric_rms_same_assay_programme_actual import scores as score,corr as cor
import spatial_marker_followthrough_actual as sm
from atlas_panel_extension import GROUPS
from pediatric_and_ewing_processed_exports_actual import TARGETS
OUT=sm.OUT;ROOTS=[OUT,Path('restored-artifacts'),Path('restored-artifacts-extra'),Path('restored-artifacts-third')]
SENS=['human_UMI_ge500','all_source_barcodes','all_reference_UMI_ge500'];ENDS=['fraction_detected','fraction_summed_human_UMI']
def rc(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def find(name,pin=None):
 ps=sorted({p for root in ROOTS for p in root.rglob(name)});good=[p for p in ps if pin is None or rc(p)['sha256']==pin];assert good,'Restore exact '+name;return good[0]
def bh(rs,n,key):
 o=sorted([(i,r['permutation_p']) for i,r in enumerate(rs) if r.get('permutation_p') is not None],key=lambda z:z[1]);q=1.
 for j in range(len(o)-1,-1,-1):i,p=o[j];q=min(q,p*n/(j+1));rs[i][key]=q
def fit(a,y,roots,kind,seed):
 n=len(y);x=score(a);rng=np.random.default_rng(seed);r={'n_literal_roots':n,'root_ids':roots,'RNA_midrank':x.tolist(),'source_values':y.tolist()}
 if len(set(x))==1 or len(set(y))==1:r['undefined_reason']='Constant score/phenotype;noabsenceclaim';return r
 if kind=='S1_subtype':
  b=y.astype(bool);nb=int(b.sum());point=float(x[b].mean()-x[~b].mean());comb=list(itertools.combinations(range(n),nb));mask=np.zeros((len(comb),n),bool)
  for i,ix in enumerate(comb):mask[i,list(ix)]=True
  null=(mask@x)/nb-((~mask)@x)/(n-nb);ib=np.flatnonzero(b);ig=np.flatnonzero(~b);ix=np.column_stack([rng.choice(ib,(2000,len(ib)),replace=True),rng.choice(ig,(2000,len(ig)),replace=True)]);bs=score(a[ix]);boots=bs[:,:nb].mean(axis=1)-bs[:,nb:].mean(axis=1);pv=float(np.mean(np.abs(null)>=abs(point)-1e-14));r['effect_units']='ARMS minus ERMS mean midrank';r['exact_label_assignments']=len(null)
 else:
  yr=rankdata(y,method='average');point=float(cor(x,yr));perms=np.array([rng.permutation(yr) for unused in range(10000)]);null=cor(np.broadcast_to(x,perms.shape),perms);pv=float((1+np.sum(np.abs(null)>=abs(point)-1e-14))/10001);ix=rng.integers(0,n,(2000,n));boots=cor(score(a[ix]),rankdata(y[ix],axis=1,method='average'));r['effect_units']='Spearman RNA-score/lineage-state fraction';r['permutations']=10000
 finite=boots[np.isfinite(boots)];r.update(effect=point,permutation_p=pv,bootstrap_attempts=2000,bootstrap_finite=len(finite),bootstrap_discarded=2000-len(finite),reranked_bootstrap95=np.quantile(finite,[.025,.975]).tolist() if len(finite)>=1800 else None,leave_one_root_out=[])
 for j,root in enumerate(roots):
  keep=np.arange(n)!=j;s=score(a[keep]);yy=y[keep]
  v=float(s[yy.astype(bool)].mean()-s[~yy.astype(bool)].mean()) if kind=='S1_subtype' else float(cor(s,rankdata(yy,method='average')))
  r['leave_one_root_out'].append({'omitted_root':root,'effect':v if np.isfinite(v) else None})
 return r
def main():
 OUT.mkdir(parents=True,exist_ok=True);path=find('RMS-restored-publisher-assets-actual.json');d=json.loads(path.read_text());assets=d['all15_declared_XLSX'];assert len(assets)==15 and all(x['status']=='complete_all_sheet_source_reparse' for x in assets)
 sheets=[s for a in assets for s in a['sheets']];assert len(sheets)==93;archive=find(Path(d['complete_table_archive']['saved']).name,d['complete_table_archive']['sha256']);z=zipfile.ZipFile(archive)
 def table(s):
  b=z.read(Path(s['all_source_values']['saved']).name);assert len(b)==s['all_source_values']['bytes'] and hashlib.sha256(b).hexdigest()==s['all_source_values']['sha256'];return list(csv.reader(io.StringIO(gzip.decompress(b).decode()),delimiter='\t'))
 S1=table(assets[0]['sheets'][0]);assert S1[2][1:5]==['Patient SJ ID#','Age','Gender','Subtype (fusion status)'];labels={};s1=[]
 for row in S1[3:]:
  if len(row)<5 or not row[1].startswith('SJRHB'):continue
  assert row[1] not in labels and (row[4]=='ERMS' or row[4].startswith('ARMS'));labels[row[1]]=row;s1.append(row)
 assert len(s1)==18
 rootlabels={}
 for row in s1:rootlabels.setdefault(row[1].split('_')[0],[]).append(row)
 assert all(len({row[4] for row in rr})==1 for rr in rootlabels.values())
 cp=find('RMS-all42-measured-targets-compact.json','7f8bc0b9cd39e96eb5376b6085f263db016d5304a59222dedd12461f9875272c');cd=json.loads(cp.read_text());assert len(cd['libraries'])==42;libs={r['identity_audit']['literal_title']:r for r in cd['libraries'] if r['identity_audit']['source_class']=='baseline_PDX'};phen=[];audit=[]
 for s in assets[4]['sheets']:
  assert s['sheet'] not in [r['source_sheet'] for r in audit];rows=table(s);assert [v.strip() for v in rows[3][:5]]==['barcode','mesoderm','myoblast','myocyte','total'];clones=[]
  for row in rows[4:]:
   if not re.fullmatch(r'[ACGT]{18}',row[0]):continue
   v=np.array([float(x) for x in row[1:5]]);assert np.isfinite(v).all() and (v>=0).all() and np.all(v==v.astype(int)) and abs(v[:3].sum()-v[3])<1e-8
   if v[3]>0:clones.append(v)
  a=np.array(clones);assert len(a)>0;values={'cells':(a[:,:3].sum(axis=0)/a[:,3].sum()).tolist(),'clones':(a[:,:3]/a[:,3,None]).mean(axis=0).tolist()};lib=libs.get(s['sheet']);audit.append({'source_sheet':s['sheet'],'source':s['all_source_values'],'positive_lineage_clones':len(a),'clone_assigned_cells':float(a[:,3].sum()),'values':values,'GSM':lib['GSM'] if lib else None,'join':'Exactsheet/GEOtitle;no alias normalization'})
  if lib:phen.append({'root':lib['identity_audit']['literal_model_root'],'GSM':lib['GSM'],**values})
 assert len(audit)==15 and len(phen)==14 and len({r['root'] for r in phen})==10
 human=[];unmatched=[];rows=[]
 for lib in cd['libraries']:
  ident=lib['identity_audit'];title=ident['literal_title'];sc=ident['source_class'];assay=ident['assay']
  if sc=='human_tumor' and assay=='snRNA':
   if ident['literal_model_root'] in rootlabels:
    rr=rootlabels[ident['literal_model_root']];human.append({'GSM':lib['GSM'],'root':ident['literal_model_root'],'ARMS':rr[0][4].startswith('ARMS'),'S1_root_source_IDs':[r[1] for r in rr],'exact_specimen_ID_match':title in labels,'join':'Exact literal root subtype only; no specimen alias normalization'})
   else:unmatched.append({'GSM':lib['GSM'],'literal_title':title,'reason':'No exact S1 root'})
  for v in lib['measured_counts']['all_frozen_target_summaries']:rows.append({'GSM':lib['GSM'],'root':ident['literal_model_root'],'source_class':sc,'assay':assay,**v})
 assert len(human)==16 and len({r['root'] for r in human})==13;f=pd.DataFrame(rows);panels={'CSPG4_RNA':['CSPG4'],**{n:[g for g in gs if g!='CSPG4'] for n,gs in GROUPS.items()}};genes=sorted(set(sum(panels.values(),[])));tests=[];rootvalues=[];pframe=pd.DataFrame(phen);hframe=pd.DataFrame(human)
 for si,sens in enumerate(SENS):
  for ei,end in enumerate(ENDS):
   for kind in ['S1_subtype','S5_cells','S5_clones']:
    chosen=human if kind=='S1_subtype' else phen;gsm=[r['GSM'] for r in chosen];sf=f[(f.barcode_sensitivity==sens)&f.GSM.isin(gsm)];mat=sf.groupby(['root','gene'])[end].mean().unstack('gene').reindex(columns=genes);roots=mat.index.tolist();assert np.isfinite(mat.to_numpy()).all()
    if kind=='S1_subtype':
     cat=hframe.groupby('root').ARMS;assert cat.nunique().max()==1;y=cat.first().reindex(roots).to_numpy(bool);assert len(roots)==13 and y.sum()==5;endpoints=[('ARMS_vs_ERMS',y)]
    else:
     field=kind[3:];v=np.stack([np.array(pframe[pframe.root==root][field].tolist()).mean(axis=0) for root in roots]);assert len(roots)==10;endpoints=[(state,v[:,i]) for i,state in enumerate(['mesoderm','myoblast','myocyte'])]
    rootvalues.append({'barcode_sensitivity':sens,'RNA_endpoint':end,'kind':kind,'roots':roots,'gene_columns':genes,'RNA_values':mat.to_numpy().tolist()})
    for state,y in endpoints:
     for name,gs in panels.items():
      r=fit(mat[gs].to_numpy(),np.asarray(y),roots,kind,2026100200+len(tests));r.update(kind=kind,state=state,panel=name,members=gs,RNA_endpoint=end,barcode_sensitivity=sens);tests.append(r)
  for kind,n in [('S1_subtype',28),('S5_cells',84),('S5_clones',84)]:
   fam=[r for r in tests if r['barcode_sensitivity']==sens and r['kind']==kind];assert len(fam)==n;bh(fam,n,'BH_q_fixed_source_family')
 assert len(tests)==588;bh(tests,588,'BH_q_all588')
 S3=table(assets[2]['sheets'][0]);assert S3[2][:2]==['gene','adjusted p value'];pool={row[0]:row for row in S3[3:] if row[0]};assert len(pool)==sum(bool(row[0]) for row in S3[3:]),'Retain duplicate source gene identities explicitly before interpreting';qual=[{'planned_literal_string':g,'mapped_exact_source_symbol':g in pool,'source_columns':S3[2],'literal_source_row':pool.get(g),'missing_is_biological_absence':False} for g in sorted(TARGETS)];assert len(qual)==88
 out={'schema':'emc-RMS-source-qualified-subtype-lineage/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'extension_record':{'dated_before_fits':'2026-10-01','scope':'CSPG4 +13 historical programmes; all2RNAendpoints×3barcodes×subtype/3statecellweighted/3stateequalclone;588 fixedtests','score':'Exact half-integer per-gene across-root rank sums;CSPG4 removedfromowncore programme','test':'Exactsubtype labelperm;10000lineage rootperms;2000rerankedbootstrap/LOO;fixed28/84families+BH588','aggregation':'Equallibrary RNA/composition means perroot'},'input_receipts':[rc(path),rc(archive),rc(cp)],'all93_sheet_sources':[{'sheet':s['sheet'],'source':s['all_source_values']} for s in sheets],'all18_S1_source_rows':s1,'human_joins':human,'human_unmatched':unmatched,'all15_S5_exact_join_audit':audit,'all88_S3_pooled_source_state_qualification':qual,'all_root_RNA_values':rootvalues,'all588_fixed_tests':tests,'limits':['Only source subtype root annotation joined; specimen-specific age/site/diagnostic fields not assigned across differing specimen IDs','Roots notverifiedclinicalpatients','18nt lineagebarcodes;no10x cellstates inferred','Partiallineagecell capture;3fractions compositional','Subtype/composition/QC confounding;no protein/glycan/function/treatmentclaim','S3 authorpooled summaries/pvalues;no newpatientinference','Myogenesis/EGFR findings priorart;exploratory reuse']}
 dest=OUT/'RMS-source-qualified-subtype-lineage-actual.json';dest.write_text(json.dumps(sm.clean(out),allow_nan=False));print('EMC_RMS_SOURCE_QUALIFIED_SUBTYPE_LINEAGE_BEGIN');print(json.dumps(sm.clean(out),allow_nan=False));print('EMC_RMS_SOURCE_QUALIFIED_SUBTYPE_LINEAGE_END')
if __name__=='__main__':main()
