#!/usr/bin/env python3
"""Match independently extracted/calculated outputs to immutable owner results."""
import csv,json,pathlib,math,datetime,collections,hashlib
ROOT=pathlib.Path(__file__).resolve().parent
OWNER=pathlib.Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/gpnmb_exploratory_analysis_results')
load=lambda p:json.loads(p.read_text())
ours=load(ROOT/'INDEPENDENT-FIXED-CELLS.json'); est=load(ROOT/'INDEPENDENT-ESTIMANDS.json')
checks=[]; failures=[]; max_numeric_error=0

def check(name,a,b):
 global max_numeric_error
 if isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isinstance(a,bool) and not isinstance(b,bool):
  diff=abs(a-b); max_numeric_error=max(max_numeric_error,diff); ok=diff<=max(1e-12,1e-12*abs(a))
 elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b) and all(isinstance(x,(int,float)) for x in a+b):
  diff=max([abs(x-y) for x,y in zip(a,b)]+[0]);max_numeric_error=max(max_numeric_error,diff);ok=all(abs(x-y)<=max(1e-12,1e-12*abs(x)) for x,y in zip(a,b))
 else:ok=a==b
 checks.append({'check':name,'pass':ok})
 if not ok:failures.append({'check':name,'independent':a,'owner':b})

expected={}
for source,records in ours.items():
 for r in records:
  sid=r.get('sample_id',r.get('gsm',r.get('condition')))
  if source=='Hofvander':expected[(source,'GPNMB',sid)]=r['value']
  elif source=='published_TempO':expected[('TempO_published','GPNMB_Log2CPM',sid)]=r['value']
  else:
   for feature,v in r['features'].items():expected[(source,feature,sid)]=v
   if source in ('GSE4303','GSE28866'):expected[(source,'median_fixed_three' if source=='GSE4303' else 'median_fixed_two',sid)]=r['value']
owner_rows=list(csv.DictReader((OWNER/'MEASUREMENTS.tsv').open(),delimiter='\t'))
actual={}
units={'Hofvander':'TPM','GSE24369':'RMA log2','GSE4303':'log2 tumor/reference','GSE28866':'normalized square-root peak density','TempO_published':'published Log2CPM'}
for r in owner_rows:
 key=(r['dataset'],r['feature'],r['condition_id']);check('gene_'+str(key),'GPNMB',r['gene'])
 check('units_'+str(key),units[r['dataset']],r['unit']);check('unique_'+str(key),False,key in actual)
 actual[key]=float(r['value']) if r['value'] else None
 check('finite/missing_'+str(key),'source_missing' if actual[key] is None else '',r['missing_reason'])
check('all fixed feature/condition keys',sorted(expected),sorted(actual))
for key,v in expected.items():check('cell_'+str(key),v,actual.get(key))
check('169 source conditions',169,len({(a,c) for a,b,c in actual}))
check('297 feature rows',297,len(actual))
check('source+derived missing14',14,sum(v is None for v in actual.values()))

def comp(name,ind,own,rna=False,year=False):
 e=ind['native_scale']
 for a,b in [('EMC_ids','EMC_ids'),('control_ids','comparator_ids')]:check(name+'/'+a,ind[a],own[b])
 for a,b in [('n_EMC','n_EMC'),('n_control','n_comparator'),('A_lower','A_lower'),('median_shift','EMC_minus_comparator_median_shift'),('A_lower_conditional_range','A_lower_conditional_empirical_resampling_95_range'),('median_shift_conditional_range','median_shift_conditional_empirical_resampling_95_range')]:check(name+'/'+a,e[a],own[b])
 check(name+'/EMC_median',e['median_EMC'],own['EMC']['median']);check(name+'/control_median',e['median_control'],own['comparator']['median'])
 check(name+'/range interpretation',True,own['resampling_range_is_not_population_or_selection_adjusted_CI'])
 x=ind['leave_one_EMC_out'];y=own['leave_one_EMC_specimen_out'];check(name+'/LOOcount',len(x),len(y))
 for i,(aa,bb) in enumerate(zip(x,y)):
  for k in ('removed_id','A_lower','median_shift'):check(name+'/LOO'+str(i)+'/'+k,aa[k],bb[k])
 if rna:
  log=ind['log2_1_plus_TPM'];check(name+'/log median shift',log['median_shift'],own['EMC_minus_comparator_median_log2_1plusTPM_shift']);check(name+'/log range',log['median_shift_conditional_range'],own['log2_1plusTPM_shift_conditional_empirical_resampling_95_range'])
 if year:
  yy=ind['year_point_only'];oo=own['year_point_estimates_only'];check(name+'/year no interval',True,oo['no_year_interval']);check(name+'/year not full adjustment',True,oo['not_all_specimen_batch_adjustment'])
  check(name+'/year pair weighted',yy['pair_weighted_A_lower'],oo['A_lower_pair_weighted']);check(name+'/year pairs',yy['pairs'],oo['finite_pairs'])
  for a,b in zip(yy['strata'],oo['strata']):
   for ka,kb in [('year','year'),('EMC_ids','EMC_ids'),('control_ids','comparator_ids'),('pairs','pairs'),('A_lower','A_lower')]:check(name+'/year'+a['year']+'/'+ka,a[ka],b[kb])

hof=load(OWNER/'HOFVANDER-RESULTS.json')
sets={'all13':'all_conditions','primary12':'primary_lesions','known_overlap9':'primary_non_known_overlap'}
controls={'LGFMS':'Low-grade fibromyxoid sarcoma','MLPS_all14':'Myxoid liposarcoma','MLPS_uncertain_omitted13':'Myxoid liposarcoma_uncertain2492omitted','SS_context':'Synovial sarcoma'}
for sk,ok in sets.items():
 for sc,oc in controls.items():
  key=sk+'__'+sc; comp('Hof/'+key,est['Hofvander'][key],hof[ok][oc],True,sc!='SS_context')
comp('GSE24369/primaryLGFMS',est['GSE24369']['8131844__EMC_vs_LGFMS'],load(OWNER/'GSE24369-RESULTS.json')['primary_LGFMS'])
seq=load(OWNER/'GSE28866-RESULTS.json')
for feature,ownerf in [('10146','10146'),('10147','10147'),('both_peak_median','median_fixed_two')]:
 for sc,oc in [('MLPS','secondary_MLPS'),('SS','context_SS')]:comp('3SEQ/'+feature+'/'+sc,est['GSE28866'][feature+'__'+sc],seq['comparisons'][ownerf][oc])
# Per-context summaries independent of incompatible reference/group comparisons.
tempo=load(OWNER/'TEMPO-PROCESSED-CONTEXT.json');vals=[r['value'] for r in ours['published_TempO']];import numpy as np
for k,v in {'source_n':12,'finite_n':12,'missing_n':0,'min':min(vals),'median':float(np.median(vals)),'max':max(vals)}.items():check('TempO/distribution/'+k,v,tempo['distribution'][k])
check('TempO12 values',{r['condition']:r['value'] for r in ours['published_TempO']},tempo['values'])
old=load(OWNER/'GSE4303-RESULTS.json')
for feature in ('5535','10100','19562'):check('old array/'+feature,{r['gsm']:r['features'][feature] for r in ours['GSE4303']},old['per_probe'][feature])
check('old array fixed3 composites',{r['gsm']:r['value'] for r in ours['GSE4303']},old['all_three_finite_median'])
check('old array CRH-mRNA native10',10,len(old['reference_groups']['CRH-mRNA']))
check('old array reference groups',{'CRH-mRNA','CRH','UHR'},set(old['reference_groups']))
missing=load(OWNER/'MISSING-REASON-CLARIFICATION.json')
report={'closed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner_freeze_sha256':hashlib.sha256((OWNER/'SCIENCE-FREEZE.json').read_bytes()).hexdigest(),'independently_verified_cells':297,'source_conditions':169,'comparisons':19,'Hof_transformed_shift_comparisons':12,'year_sensitivities':9,'checks':checks,'passed':sum(r['pass'] for r in checks),'failed':len(failures),'failures':failures,'maximum_numeric_error':max_numeric_error,'tolerance':'max(1e-12,1e-12*abs(independent value)); IDs, counts, missing, source hashes exact','value_scope':'Agreement only. Post-pilot scientific contribution assessed independently by challenge. No pooled units, certified donor/population interval, protein/therapy/intrinsic or campaign-exhaustion claim.'}
(ROOT/'ARITHMETIC-AND-CELL-COMPARISON.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['closed_at','passed','failed','maximum_numeric_error','failures']},indent=2))
