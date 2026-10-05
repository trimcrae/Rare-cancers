#!/usr/bin/env python3
import pathlib,json,csv,gzip,io,zipfile,datetime,statistics,hashlib
ROOT=pathlib.Path(__file__).resolve().parent
OWNER=pathlib.Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/gpnmb_exploratory_analysis_results')
CONTRACT=OWNER.parent/'gpnmb_exploratory_analysis_contract'
load=lambda p:json.loads(p.read_text());cells=load(ROOT/'INDEPENDENT-FIXED-CELLS.json');unit=load(CONTRACT/'FROZEN-SPECIMEN-UNITS.json');roster=load(OWNER/'ACTUAL-ANALYTICAL-ROSTER.json')
checks=[]
def ck(n,a,b):checks.append({'check':n,'pass':a==b,'expected':a,'actual':b} if a!=b else {'check':n,'pass':True})
hmeta={r['sample_id']:r for r in unit['Hofvander']};ameta={r['gsm']:r for r in unit['ARRAY_SOURCE_RECORDS']}
for r in roster['conditions']:
 ds=r['dataset'];sid=r['condition_id']
 if ds=='Hofvander':ck('original frozen Hof specimen metadata '+sid,hmeta[sid],r['source_metadata'])
 elif ds in ('GSE24369','GSE4303'):
  ck('original array donor/condition/capture/reference metadata '+sid,ameta[sid],r['source_metadata'])
  if ds=='GSE4303':ck('reference not pooled '+sid,';'.join(ameta[sid]['source_ch1']),r['reference'])
 rec=next(x for x in cells['published_TempO' if ds=='TempO_published' else ds] if x.get('sample_id',x.get('gsm',x.get('condition')))==sid)
 f={'GPNMB_Log2CPM':rec['value']} if ds=='TempO_published' else {'GPNMB':rec['value']} if ds=='Hofvander' else dict(rec['features'])
 if ds in ('GSE4303','GSE28866'):f['median_fixed_three' if ds=='GSE4303' else 'median_fixed_two']=rec['value']
 ck('features '+ds+'/'+sid,set(f),set(r['features']))
 ck('finite features '+ds+'/'+sid,{k for k,v in f.items() if v is not None},set(r['evaluated_finite_features']))
 ck('missing features '+ds+'/'+sid,{k for k,v in f.items() if v is None},set(r['missing_or_unavailable_features']))
# Original eight missing probe lexical source cells, not absent row/zero.
z=zipfile.ZipFile('/workspace/Rare-cancers/research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip');raw_null=[]
with gzip.open(io.BytesIO(z.read('GSE4303-GPL3290-source-matrix.gz')),'rt') as f:
 head=None
 for line in f:
  if line.startswith(('ID_REF','"ID_REF"')):head=next(csv.reader([line],delimiter='\t'))[1:]
  pr=line.partition('\t')[0].strip('"')
  if pr not in ('5535','10100','19562'):continue
  vals=next(csv.reader([line],delimiter='\t'))[1:]
  for sid,v in zip(head,vals):
   if next(r for r in cells['GSE4303'] if r['gsm']==sid)['features'][pr] is None:raw_null.append({'probe':pr,'condition_id':sid,'original_source_lexeme':v})
ck('eight actual source nulls',8,len(raw_null));ck('null source lexeme',{'null'},set(r['original_source_lexeme'] for r in raw_null))
# Each original fixed feature remains available even where composite unavailable.
ck('six composites unavailable',6,sum(r['value'] is None for r in cells['GSE4303']))
ck('all ten EMC old ratios accounted',10,len([r for r in cells['GSE4303'] if r['source_ch1']==['CRH-mRNA']]))
ck('3SEQ all four original conditions',unit['3SEQ_source_conditions'],[r['condition'] for r in cells['GSE28866'] if r['condition'].startswith('EMC_')])
ck('published TempO all12',12,len(cells['published_TempO']))
ck('all169 source conditions',169,sum(len(v) for v in cells.values()))
# Fixed agreement plus correct observed-separation/boundary interpretation.
sep=[]
def boundary(name,own):
 ex=own['EMC_ids'];cy=own['comparator_ids']
 if name.startswith('Hof'):
  vals={r['sample_id']:r['value'] for r in cells['Hofvander']}
 elif name.startswith('RMA'):vals={r['gsm']:r['value'] for r in cells['GSE24369']}
 else:
  feat=name.split('/')[1];vals={r['condition']:r['value'] if feat=='median_fixed_two' else r['features'][feat] for r in cells['GSE28866']}
 x=[vals[s] for s in ex];y=[vals[s] for s in cy];s=max(x)<min(y) or min(x)>max(y)
 ck('observed separation flag '+name,s,own['complete_observed_rank_separation'])
 for label,vs in [('EMC',x),('comparator',y)]:
  for k,v in [('min',min(vs)),('max',max(vs)),('source_n',len(vs)),('finite_n',len(vs)),('missing_n',0)]:ck(name+'/'+label+'/'+k,v,own[label][k])
 rr=own['A_lower_conditional_empirical_resampling_95_range']
 if s:sep.append({'contrast':name,'A_lower':own['A_lower'],'conditional_range':rr,'interpretation':'Observed empirical rank support only; no zero population uncertainty/universal separation/selection-adjusted inference'})
h=load(OWNER/'HOFVANDER-RESULTS.json')
for s,cc in h.items():
 for c,rs in cc.items():boundary('Hof/'+s+'/'+c,rs)
boundary('RMA/8131844',load(OWNER/'GSE24369-RESULTS.json')['primary_LGFMS'])
for f,cc in load(OWNER/'GSE28866-RESULTS.json')['comparisons'].items():
 for c,rs in cc.items():boundary('3SEQ/'+f+'/'+c,rs)
# Original output/source hashes and pre-output freezes stay exact.
for fr in ['PLAN-FREEZE.json','PREOUTPUT-CODE-FREEZE.json']:
 for name,b in load(ROOT/fr)['files'].items():ck('pre-output frozen bytes '+name,b['sha256'],hashlib.sha256((ROOT/name).read_bytes()).hexdigest())
for b in load(OWNER/'SCIENCE-FREEZE.json')['files']:ck('owner frozen bytes '+b['path'],b['sha256'],hashlib.sha256((OWNER/b['path']).read_bytes()).hexdigest())
# Restricted field7 not accessed in independent/owner script; explicit indexed selection versus dictionary key.
owner_code=(OWNER/'run_pilot.py').read_text();ck('owner never references source DE column',False,'differentially_expressed_cancer_type' in owner_code)
report={'validated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'passed':sum(r['pass'] for r in checks),'failed':sum(not r['pass'] for r in checks),'source_null_fields':raw_null,'complete_observed_separation_contexts':sep,'scope':'Identity/condition/probe completeness and interpretation replay; no new sources, targets or inferential question. Exact arithmetic agreement is separate from scientific value.'}
(ROOT/'IDENTITY-MISSING-AND-INTERPRETATION-CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'failed':report['failed'],'observed_boundary_contexts':len(sep),'failures':[r for r in checks if not r['pass']]},indent=2))
