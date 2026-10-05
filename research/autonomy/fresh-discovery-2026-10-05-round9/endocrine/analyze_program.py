"""Frozen endocrine-set contrast; retains every source EMC, original array mapping, and negatives."""
import pathlib,json,gzip,csv,zipfile,io,hashlib,datetime,collections
import numpy as np
from scipy.stats import rankdata
import openpyxl
B=pathlib.Path(__file__).parent
ROOT=pathlib.Path('/workspace/Rare-cancers/research/autonomy')
EMC='Extraskeletal myxoid chondrosarcoma';CONTROL=['Low-grade fibromyxoid sarcoma','Myxofibrosarcoma'];CTX=['ESR1','ESR2','PGR','GREB1'];SEED=20261005
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,d): (B/n).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def auc(x,y):
 if not len(x) or not len(y):return None
 z=np.asarray(x)[:,None]-np.asarray(y)[None,:];return float(np.mean((z>0)+.5*(z==0)))
def score(vals,ids,genes):return dict(zip(ids,np.mean([rankdata([vals[g][i] for i in ids],method='average')/(len(ids)+1) for g in genes],axis=0).tolist()))
def ev(scores,emc,controls):
 a={h:auc([scores[i] for i in emc],[scores[i] for i in ids]) for h,ids in controls.items()}
 return {'n_emc':len(emc),'n_controls':{h:len(ids) for h,ids in controls.items()},'AUC_by_histology':a,'equal_histology_AUC':float(np.mean(list(a.values()))) if a and all(x is not None for x in a.values()) else None}
def bootstrap(scores,e,ctrl):
 rng=np.random.default_rng(SEED);v=[]
 for k in range(2000):
  ee=rng.choice(e,len(e),replace=True).tolist();cc={h:rng.choice(c,len(c),replace=True).tolist() for h,c in ctrl.items()};v.append(ev(scores,ee,cc)['equal_histology_AUC'])
 return {'replicates':2000,'seed':SEED,'one_sided_95_lower':float(np.quantile(v,.05)),'one_sided_95_upper':float(np.quantile(v,.95)),'scope':'conditional specimen bootstrap; no unproved independent donor or cross-cohort linkage'}
def gene_direction(vals,genes,e,ctrl):
 out={}
 for g in genes:
  med=float(np.median([vals[g][i] for i in e]));out[g]={'EMC_median':med,'controls':{h:{'median':float(np.median([vals[g][i] for i in c])),'AUC':auc([vals[g][i] for i in e],[vals[g][i] for i in c])} for h,c in ctrl.items()}}
 good=[g for g in genes if all(out[g]['EMC_median']>d['median'] for d in out[g]['controls'].values())]
 return {'genes_with_higher_EMC_median_in_both_controls':good,'fraction':len(good)/len(genes),'all_gene_results':out}
def hof_inputs(genes):
 src=ROOT/'atlas-hofvander-source-2026-09-06';mp=ROOT/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json';manifest=json.loads(mp.read_text());rows=manifest['samples']
 p=src/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx';w=openpyxl.load_workbook(p,read_only=True,data_only=True);rs=list(w.active.values);heads=rs[1];by={r[0]:dict(zip(heads,r)) for r in rs[2:] if r[0]}
 for r in rows:
  s=by[r['source_label']];r.update(sex=s['Sex'],age=s['Age at diagnosis'],site=s['Sitec'],source_class=s['Class'])
 vals={};p=src/'tpm_matrix.tsv.gz'
 with gzip.open(p,'rt') as f:
  rr=csv.reader(f,delimiter='\t');ids=next(rr)[1:]
  for v in rr:
   if v[0] in genes:
    assert v[0] not in vals;vs=list(map(float,v[1:]));assert len(vs)==len(ids) and all(x>=0 and np.isfinite(x) for x in vs);vals[v[0]]=dict(zip(ids,vs))
 return rows,vals,{'matrix':{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)},'metadata':{'path':str(mp),'sha256':sha(mp)},'primary_s1':{'path':str(src/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx'),'sha256':sha(src/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx')}}
def array_inputs(genes):
 pp=ROOT/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz';zp=ROOT/'atlas-original-array-source-2026-09-06/original-source-recovery.zip';z=zipfile.ZipFile(zp);ann=z.read('GPL6244-original-annotation.tsv');pm={}
 for r in csv.DictReader(io.StringIO(ann.decode()),delimiter='\t'):
  sy={a.split(' // ')[1].strip() for a in r['gene_assignment'].split(' /// ') if len(a.split(' // '))>=2};sy.discard('---')
  if len(sy)==1:
   g=next(iter(sy))
   if g in genes:pm[r['ID']]=g
 rows=[];vprobe={};id=None;mode=False;all_measured={}
 with gzip.open(pp,'rt') as f:
  for l in f:
   l=l.rstrip('\r\n')
   if l.startswith('^SAMPLE = '):id=l.split(' = ')[1];rows.append({'sample_id':id,'sex':'unreported','sequencing_year':'same_original_RMA_series','eligible':True,'primary_lesion':None,'known_overlap':'unresolved donor links','source_class':'Malignant'})
   elif l.startswith('!Sample_title = '):rows[-1]['title']=l.split(' = ',1)[1]
   elif l.startswith('!Sample_characteristics_ch1 = tissue: '):
    rows[-1]['diagnosis']=l.split(': ',1)[1]
    rows[-1]['source_class']='Malignant' if rows[-1]['diagnosis'] in [EMC]+CONTROL else 'intermediate/SFT-unstratified/poolednormal; not assumed malignant'
   elif l=='!sample_table_begin':mode=True;all_measured[id]=set()
   elif l=='!sample_table_end':mode=False
   elif mode and id and not l.startswith('ID_REF'):
    p,x=l.split('\t')[:2];all_measured[id].add(p)
    if p in pm:vprobe.setdefault(p,{})[id]=float(x)
 common=set.intersection(*all_measured.values());assert len(rows)==42;vals={};maps={}
 for g in genes:
  probes=sorted(p for p,h in pm.items() if h==g and p in common)
  if probes:
   vals[g]={r['sample_id']:float(np.median([vprobe[p][r['sample_id']] for p in probes])) for r in rows};maps[g]=probes
 return rows,vals,{'soft':{'path':str(pp),'bytes':pp.stat().st_size,'sha256':sha(pp)},'original_annotation_zip':{'path':str(zp),'sha256':sha(zp)},'annotation_member_sha256':hashlib.sha256(ann).hexdigest(),'all_common_measured_probes':len(common),'selected_probe_mapping':maps}
def run():
 freeze=json.loads((B/'ANALYSIS-FREEZE.json').read_text());sets=json.loads((B/'FIXED-GENE-SETS.json').read_text());assert sha(B/'FIXED-GENE-SETS.json')==freeze['gene_set_file_sha256']
 gs=set(CTX)|set(sets['early']['genes'])|set(sets['late']['genes']);cohorts={};inputs={};values={};sample_records={};scores_out={};data={}
 for name,fun in [('Hofvander',hof_inputs),('GSE24369',array_inputs)]:
  rows,vals,receipts=fun(gs);data[name]=(rows,vals);inputs[name]=receipts
 for name,(rows,vals) in data.items():
  all_e=[r['sample_id'] for r in rows if r.get('diagnosis')==EMC];e=[r['sample_id'] for r in rows if r.get('diagnosis')==EMC and r['eligible']] if name=='Hofvander' else all_e
  ctr={h:[r['sample_id'] for r in rows if r.get('diagnosis')==h and r['eligible']] for h in CONTROL}
  assert len(all_e)==(13 if name=='Hofvander' else 6) and len(e)==(9 if name=='Hofvander' else 6)
  population=all_e+sum(ctr.values(),[]);broad={h:[r['sample_id'] for r in rows if r.get('diagnosis')==h and r['eligible'] and r['source_class']=='Malignant'] for h in sorted({r.get('diagnosis','') for r in rows if r['source_class']=='Malignant' and r.get('diagnosis')!=EMC})};broad={h:v for h,v in broad.items() if v};broadpop=list(dict.fromkeys(all_e+sum(broad.values(),[])))
  result={'all_EMC':all_e,'primary_EMC':e,'all_source_EMC_metadata':[r for r in rows if r['sample_id'] in all_e],'sex_counts_all_EMC':dict(collections.Counter(r['sex'] for r in rows if r['sample_id'] in all_e)),'comparators':ctr,'sets':{},'units':'TPM and log2(TPM+1) for scoring' if name=='Hofvander' else 'original RMA log2 array intensity'}
  sample_records[name]=[r for r in rows if r['sample_id'] in broadpop or r['sample_id'] in population];values[name]={g:{i:vals[g][i] for i in broadpop} for g in sorted(vals)};scores_out[name]={}
  # Preserve native measurement units in export; monotone transform does not change ranks.
  logvals={g:{i:float(np.log2(x+1)) for i,x in v.items()} for g,v in vals.items()} if name=='Hofvander' else vals
  for sn,s in sets.items():
   genes=[g for g in s['genes'] if g in vals];common=[g for g in genes if all(g in vv for rr,vv in data.values())];sc=score(logvals,population,genes);bc=score(logvals,broadpop,genes);noex=[g for g in genes if g not in CTX];sce=score(logvals,population,noex);scc=score(logvals,population,common)
   point=ev(sc,e,ctr);ci=bootstrap(sc,e,ctr);coherence=gene_direction(logvals,genes,e,ctr);metadata={r['sample_id']:r for r in rows};matched={}
   for fields in [('sex',),('sequencing_year',),('sex','sequencing_year')]:
    key='+'.join(fields);match={}
    for h,c in ctr.items():
     pairs=[]
     for i in e:
      target=[j for j in c if all(metadata[i][f]==metadata[j][f] and metadata[i][f] not in ('NA','unreported',None) for f in fields)]
      if target:pairs.append(auc([sc[i]],[sc[j] for j in target]))
     match[h]={'supported_EMC':len(pairs),'AUC':float(np.mean(pairs)) if pairs else None}
    matched[key]=match
   r={'covered_genes':genes,'missing_exact_symbols':[g for g in s['genes'] if g not in vals],'coverage_fraction':len(genes)/200,'primary':point,'bootstrap':ci,'coherence':coherence,'all_EMC_sensitivity':ev(sc,all_e,ctr),'exclude_LR_only':ev(sc,[i for i in all_e if metadata[i].get('specimen_exception')!='LR'],ctr),'exclude_known_MDB_overlap_only':ev(sc,[i for i in all_e if not metadata[i].get('known_overlap','').startswith('MDB')],ctr),'leave_one_EMC_out':{i:ev(sc,[j for j in e if j!=i],ctr) for i in e},'remove_published_exemplars':ev(sce,e,ctr),'common_mapped_genes':{'n':len(common),'result':ev(scc,e,ctr)},'matched_metadata_sensitivities':matched,'broad_malignant_context':ev(bc,e,broad)}
   r['primary_effect_gate']=len(genes)>=160 and point['equal_histology_AUC']>=.70 and all(x>.5 for x in point['AUC_by_histology'].values()) and ci['one_sided_95_lower']>.5
   r['coherence_gate']=coherence['fraction']>=.65
   r['late_check_gate']=len(genes)>=160 and point['equal_histology_AUC']>=.65 and all(x>.5 for x in point['AUC_by_histology'].values())
   result['sets'][sn]=r;scores_out[name][sn]={'primary_population':sc,'broad_population':bc,'units':'average within-assay gene percentile'}
  result['context_receptors_separate']={g: {'all_EMC_measurements':{i:vals[g][i] for i in all_e},'primary':gene_direction(logvals,[g],e,ctr)} if g in vals else {'status':'missing_exact_symbol'} for g in CTX};cohorts[name]=result
 res={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze_sha256':sha(B/'ANALYSIS-FREEZE.json'),'cohorts':cohorts,'set_overlap':len(set(sets['early']['genes'])&set(sets['late']['genes'])),'replicated_numerical_gate':all(d['sets']['early']['primary_effect_gate'] and d['sets']['early']['coherence_gate'] and d['sets']['late']['late_check_gate'] for d in cohorts.values()),'limits':'Bulk gene-set scores do not measure ER/PR protein, pathway activity, hormone response, dependency or clinical benefit; late overlap is not independent replication; source donor overlap unresolved; sex unavailable in original array.'}
 dump('PROGRAM-RESULTS.json',res);dump('SOURCE-INPUT-RECEIPTS.json',inputs);dump('SELECTED-SET-MEASUREMENTS.json',values);dump('SAMPLE-CONDITION-RECORDS.json',sample_records);dump('PROGRAM-SCORES.json',scores_out)
 print(json.dumps({n:{s:{'n':len(v['covered_genes']),'AUC':v['primary']['equal_histology_AUC'],'by_histology':v['primary']['AUC_by_histology'],'coherence':v['coherence']['fraction'],'bootstrap_lower':v['bootstrap']['one_sided_95_lower']} for s,v in d['sets'].items()} for n,d in cohorts.items()},indent=2))
if __name__=='__main__':run()
