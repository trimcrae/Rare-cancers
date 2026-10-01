import json,hashlib,datetime,itertools
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
import spatial_marker_followthrough_actual as sm
import peerj_expression_diagnostic_actual as p
import scientific_source_access_followthrough as src
OUT=sm.OUT
def rc(path):return {'saved':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def bh(tests,key,n):
 order=sorted([(i,r['exact_label_permutation_p']) for i,r in enumerate(tests) if r.get('exact_label_permutation_p') is not None],key=lambda z:z[1]);q=1.
 for j in range(len(order)-1,-1,-1):i,v=order[j];q=min(q,v*n/(j+1));tests[i][key]=q
def stat(x,b):
 r=rankdata(x,method='average');return float(r[b].mean()-r[~b].mean())
def fit(x,b,labels,seed):
 good=np.isfinite(x);x=x[good];b=b[good];labels=np.array(labels)[good];n=len(x);nb=int(b.sum());ng=n-nb;r={'included_specimens':labels.tolist(),'n':n,'literal_B':nb,'literal_G':ng}
 if min(nb,ng)<3:r['status']='withheld_insufficient_label_groups';return r
 point=stat(x,b);null=[]
 for chosen in itertools.combinations(range(n),nb):
  bb=np.zeros(n,bool);bb[list(chosen)]=True;null.append(stat(x,bb))
 null=np.array(null);rng=np.random.default_rng(seed);ib=np.flatnonzero(b);ig=np.flatnonzero(~b);boot=[]
 for unused in range(2000):
  ix=np.r_[rng.choice(ib,len(ib),replace=True),rng.choice(ig,len(ig),replace=True)];boot.append(stat(x[ix],b[ix]))
 r.update(status='measured',B_minus_G_mean_midrank=point,B_minus_G_median_value=float(np.median(x[b])-np.median(x[~b])),B_vs_G_pairwise_probability=float(np.mean([(u>v)+.5*(u==v) for u in x[b] for v in x[~b]])),exact_label_assignments=len(null),exact_label_permutation_p=float(np.mean(np.abs(null)>=abs(point)-1e-14)),reranked_stratified_bootstrap_attempts=2000,reranked_bootstrap95=np.quantile(boot,[.025,.975]).tolist(),leave_one_source_specimen_out=[])
 for j,label in enumerate(labels):
  keep=np.arange(n)!=j;r['leave_one_source_specimen_out'].append({'excluded_specimen':str(label),'B_minus_G_mean_midrank':stat(x[keep],b[keep])})
 return r
def main():
 OUT.mkdir(parents=True,exist_ok=True);roots=[OUT,Path('restored-artifacts'),Path('restored-artifacts-extra'),Path('restored-artifacts-third')];paths=sorted({f for root in roots for f in root.rglob('exact-RMS-publisher-and-PeerJ-project-metadata-actual.json')});assert paths;d=json.loads(paths[0].read_text());meta=d['PeerJ_project_metadata'];clinical={}
 for r in meta['BioSample_records']:
  names=[v['value'] for v in r['identifiers'] if v['attributes'].get('db_label')=='Sample name'];assert len(names)==1;si=names[0];assert si in p.IDS and si not in clinical
  a={v['attributes']['attribute_name']:v['value'] for v in r['attributes']};assert a['Prognosis'] in ['G','B'];clinical[si]={'BioSample':r['accession'],'literal_sample_name':si,'literal_attributes':a,'Time_equals2020_minusCollectionYear':float(a['Time'])==2020-float(a['Collection date'])}
 assert set(clinical)==set(p.IDS);assert sum(clinical[si]['literal_attributes']['Prognosis']=='B' for si in p.IDS)==6
 path,source=p.get();book=src.xlsx_tables(path.read_bytes());sheet=next(t for t in book['tables'] if t['sheet']=='EMC_Gene-expression_Log2CPM');rows=sheet['rows'];assert rows[0]==['symbol']+p.IDS;V=np.array([[float(v) for v in row[1:]] for row in rows[1:]]);assert V.shape==(9500,12) and np.isfinite(V).all();symbols=[str(r[0]) for r in rows[1:]];ranked=rankdata(V,axis=0,method='average')/9500;repeated=np.abs(V-p.FLOOR)<=5e-10;bottom=V<=np.quantile(V,.25,axis=0);variants=[('published_log2CPM',V),('specimen_midrank9500',ranked),('mask_repeated_export_value',np.where(repeated,np.nan,V)),('mask_bottom_quartile',np.where(bottom,np.nan,V))];b=np.array([clinical[si]['literal_attributes']['Prognosis']=='B' for si in p.IDS]);tests=[]
 for scope in ['all12_literal_BioSample_joins','exclude_Si22_library_name_conflict']:
  keep=np.array([scope=='all12_literal_BioSample_joins' or si!='Si22' for si in p.IDS])
  for vi,(variant,A) in enumerate(variants):
   for gi,gene in enumerate(p.GENES):
    assert symbols.count(gene)==1;test=fit(A[symbols.index(gene),keep],b[keep],np.array(p.IDS)[keep],2026100180+len(tests));test.update(scope=scope,variant=variant,gene=gene);tests.append(test)
  family=[r for r in tests if r['scope']==scope];assert len(family)==12;bh(family,'BH_q_fixed12',12)
 bh(tests,'BH_q_all24',24)
 out={'schema':'emc-PeerJ-literal-clinical-label-diagnostic/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_receipts':[rc(paths[0]),source],'clinical_rows':clinical,'ENA_alias_conflicts':[r for r in meta['all_ENA_records'] if len(r['literal_Si_ids'])!=1],'primary_definition_receipt':{'PMCID':'PMC13374579','primary_XML_sha256':'2d9a6ee4ed417860867eb954e0b0a4fa3fa3042787f5af3c0a1fea9bb5fbe768','published_groups':'Good: no disease/indolent or surviving>8years; poor: rapidly progressive/died of disease within8years','mapping_limit':'Literal metadata G/B codelegend not inspected; results retain B/G without event/time translation'},'extension_record':{'dated_before_fits':'2026-10-01','selection':'Frozen3 source-selected genes×4 export variants; all12 exactsample joins plus11 excluding Si22 conflict sensitivity','units':'Unique literalBioSample sample names matched publishedSi columns; no library_name alias correction','testing':'Exact fixedgroup label permutations,2000 stratified rerankedbootstrap,LOO,BH12eachscope/BH24all'},'all24_fixed_diagnostics':tests,'limits':['Selectedsame12 published specimens: internalpostselection, no independent predictionvalidation','Time0–23 exactly2020−collectionyear is undefined for survival/censoring; noCox/logrank fit','LiteralPrognosis binary comparisons do not establish causal or therapeutic relevance']}
 dest=OUT/'PeerJ-literal-clinical-label-diagnostic-actual.json';dest.write_text(json.dumps(sm.clean(out),allow_nan=False));print('EMC_PEERJ_LITERAL_CLINICAL_LABEL_BEGIN');print(json.dumps(sm.clean(out),allow_nan=False));print('EMC_PEERJ_LITERAL_CLINICAL_LABEL_END')
if __name__=='__main__':main()
