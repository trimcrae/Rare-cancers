"""Compare independent original-OOXML EMC extraction to functional worker output."""
import hashlib,json,math
from pathlib import Path
D=Path(__file__).resolve().parent
F=D.parent/'functional'
if not F.exists():
 F=Path(r'C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04/functional')
ip=D/'mendeley-independent-values.json';wp=F/'mendeley-analysis.json'
a=json.loads(ip.read_text());b=json.loads(wp.read_text())
errors=[];counts={'drug_curves':0,'drug_points':0,'drug_replicate_cells':0,'reported_auc_rows':0,'fiber_conditions':0,'fiber_values':0,'pATR_source_values':0,'signature_counts':0}
delta=[]
def same(x,y,label):
 if x!=y:errors.append(label)
def close(x,y,label):
 delta.append(abs(x-y))
 if not math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-10):errors.append(label)
curves={r['drug']:r for r in b['curves'] if r['model']=='USZ-23_EMC3'}
same(len(curves),8,'eight worker EMC curves')
for r in a['drug_curves']:
 w=curves[r['drug']];counts['drug_curves']+=1
 same(len(w['points']),len(r['points']),r['drug']+' point count')
 for x,y in zip(r['points'],w['points']):
  label=r['drug']+' row '+str(x['source_row'])
  same(x['source_row'],y['row'],label+' row');same(x['concentration_uM'],y['dose_uM'],label+' dose')
  same(x['replicates'],y['values'],label+' raw values');close(x['mean'],y['mean'],label+' mean');close(x['sd_technical'],y['sd'],label+' SD')
  counts['drug_points']+=1;counts['drug_replicate_cells']+=len(x['replicates'])
auc={r['drug_label']:r for r in b['source_auc'] if r['model']=='USZ-23_EMC3'}
same(len(auc),8,'eight worker EMC source AUC rows')
for x in a['reported_auc']:
 y=auc[x['drug']]
 for k,v in [('mean','mean'),('sd','source_SD'),('reported_N','source_N')]:same(x[k],y[v],x['drug']+' '+k)
 counts['reported_auc_rows']+=1
for x in a['other_emc_measurements']:
 if x['sheet']=='5B':
  ys=[r for r in b['pATR_positive_nuclei'] if r['model']=='USZ-23_EMC3'];same(len(ys),1,'one pATR EMC row');y=ys[0]
  counts['pATR_source_values']+=x['n_numeric_cells']
 else:
  ys=[r for r in b['fiber_lengths'] if r['sheet']==x['sheet'] and r['column']==x['column'] and r['condition']==x['label']]
  same(len(ys),1,x['sheet']+' '+x['column']+' fiber condition');y=ys[0]
  counts['fiber_conditions']+=1;counts['fiber_values']+=x['n_numeric_cells']
 vals=list(x['numeric_cells'].values());same(vals,y['values'],x['sheet']+' '+x['column']+' raw values')
 for k in ['mean','median','sd']:close(x[k],y[k],x['sheet']+' '+x['column']+' '+k)
ys=[r for r in b['signature_counts'] if r['model']=='USZ-23_EMC3'];same(len(ys),1,'one EMC signature row')
same(a['signature_transcript_counts'],ys[0]['counts'],'signature transcript counts');counts['signature_counts']=len(a['signature_transcript_counts'])
inputs={}
for name,path in [('original_source',F/'mendeley-supporting-values.xlsx'),('independent_values',ip),('worker_analysis',wp),('independent_extractor',D/'challenge_mendeley.py'),('worker_extractor',F/'analyze_mendeley.py')]:
 raw=path.read_bytes();inputs[name]={'name':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
report={'date':'2026-10-04','status':'PASS' if not errors else 'FAIL','inputs':inputs,'checked':counts,'maximum_summary_absolute_difference':max(delta),'errors':errors,'limits':['Checks every explicitly labelled EMC numerical condition in the deposit, not unlabelled model sheets 4I and 5E.','This checks deposited arithmetic and identity; it does not establish final-2026 version concordance, assay units/duration or biological replicate hierarchy.','Fibers and technical columns are not independent donors; source AUC N13 remains uninterpreted.','Drug-specific positive responses disallow a general ATR/DDR resistance claim; reported original-source observations are not newly discovered EMC biology.']}
(D/'mendeley-crosscheck-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='inputs'},indent=2))
assert not errors,errors
