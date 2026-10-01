import argparse,ast,hashlib,json,pathlib,statistics
from collections import Counter
p=argparse.ArgumentParser();p.add_argument('--clinical',required=True);p.add_argument('--numeric',required=True);p.add_argument('--out',default='campaign-output/immunosarc-numeric-outcomes');a=p.parse_args();receipts=[]
def read(path,schema):
 b=pathlib.Path(path).read_bytes();q=json.loads(b);receipts.append({'path':path,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 for _ in range(10):
  if q.get('schema')==schema:return q
  if isinstance(q.get('result'),dict):q=q['result']
  elif isinstance(q.get('structuredContent'),dict):q=q['structuredContent']
  elif isinstance(q.get('content'),str):q=json.loads(q['content'])
  elif isinstance(q.get('content'),list):q=json.loads(next(x['text'] for x in q['content'] if x.get('type')=='text'))
  else:raise ValueError('Unknown durablewrapper')
 raise ValueError('Wrapperlimit')
c=read(a.clinical,'immunosarc-assay-outcome-composition/1');n=read(a.numeric,'immunosarc-numeric-IHC-published-supplement/1');assert not c['errors'] and not n['errors'];f=pathlib.Path(__file__).parent/'immunosarc_assay_outcome_composition.py';tree=ast.parse(f.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('km','rmst','composition')];ns={'Counter':Counter};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(f),'exec'),ns);patients={x['Subject']:x for x in c['patientLiteralAndCanonicalRows']};assert len(patients)==77;allids=set(patients);rows=n['numericCells'];R={'schema':'immunosarc-measured-IHC-outcome-composition/1','sources':receipts,'eventCoding':c['eventCoding'],'availability':[],'pairedChangeSummaries':[],'limits':['MeasurednumericIHC reconciled across publishedtables; conflicts not averaged.','Future-defined availability; descriptivecomposition, not causal/treatment/biomarkervalidation.','NoEMC in study.'],'errors':[]}
for field in ('CD8','PD1'):
 by={t:{x['subject'] for x in rows if x['field']==field and x['timepoint']==t and x['status']=='one-distinct-numeric-value'} for t in ('Baseline','On-Treatment')};by['paired']=by['Baseline']&by['On-Treatment']
 for kind,ids in by.items():R['availability'].append({'field':field,'kind':kind,'available':ns['composition'](ids,patients),'unavailable':ns['composition'](allids-ids,patients)})
 v=[x['changePercentagePoints'] for x in n['pairedChanges'] if x['field']==field];R['pairedChangeSummaries'].append({'field':field,'n':len(v),'medianPercentagePointChange':statistics.median(v),'min':min(v),'max':max(v),'increases':sum(x>0 for x in v),'decreases':sum(x<0 for x in v),'ties':sum(x==0 for x in v)})
d=pathlib.Path(a.out);d.mkdir(parents=True,exist_ok=True);(d/'immunosarc-numeric-outcome-composition.json').write_text(json.dumps(R,indent=2));print(json.dumps(R))
