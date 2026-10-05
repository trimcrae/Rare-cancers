"""Public source implementation/index verification; no source execution or APIcalls."""
from pathlib import Path
import json,hashlib,ast,datetime,shutil
HERE=Path(__file__).resolve().parent
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,v):
 checks.append({'check':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
def method(file,cls,name):
 s=(HERE/'source-cache'/file).read_text();t=ast.parse(s);c=next(x for x in t.body if isinstance(x,ast.ClassDef) and x.name==cls);f=next(x for x in c.body if isinstance(x,ast.FunctionDef) and x.name==name);return ast.get_source_segment(s,f)
for plan in ['PLAN.json','PROVIDER-DOCUMENT-PLAN.json']:
 rows=json.loads((HERE/plan).read_text())['genuine_files' if plan=='PLAN.json' else 'files']
 for r in rows:
  n=Path(r.get('repo_path')).name
  if '/databases/' in r['repo_path']:n='provider-'+n
  p=HERE/'source-cache'/n;b=p.read_bytes()
  check('genuine authorblob '+n,hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()==r['git_blob_sha'])
  check('expected sourcebytes '+n,len(b)==r.get('expected_bytes',r.get('bytes')))
for recfile in ['ACCESS.json','PROVIDER-DOCUMENT-ACCESS.json']:
 for r in json.loads((HERE/recfile).read_text()):check('source receipt '+Path(r['path']).name,sha(Path(r['path']))==r['sha256'] and r['status']==200)
cf=lambda n:method('config.py','CohortConfig',n)
check('names preserve reportdirectory keyorder','list(self.config["report_directory"].keys())' in cf('get_cohort_names'))
check('name index cached list indexOf','self.cohort_names.index(cohort_name)' in cf('get_cohort_index'))
check('directoryindex enumerates same mapping','enumerate(self.config["report_directory"].items())' in cf('get_cohort_index_from_report_directory'))
check('SQL metadata path positional separatemapping','list(self.config["patient_annotation_path"].values())[int(cohort_index)]' in cf('get_patients_metadata_path'))
for fn,cls in [('provider-in_memory.py','InMemoryProvider'),('provider-sql.py','SQLProvider')]:
 s=method(fn,cls,'load_tables');check('provider name-index load '+cls,'config.get_cohort_names()' in s and 'config.get_cohort_index(cohort_name)' in s and 'self.load_single_cohort(cohort_name, cohort_index, config)' in s)
s=method('provider-in_memory.py','InMemoryProvider','load_single_cohort');check('memory checksstored name index consistency','data_layer_cohort_name != cohort_name' in s)
s=method('provider-in_memory.py','InMemoryProvider','get_dataframe');check('memorymetadata integer index retrieval','self.dict_all_data[data_layer][int(cohort_index)]["data_frame"]' in s)
s=method('provider-sql.py','SQLProvider','load_cohort_to_db_patient_meta_data');check('SQL import sets name derived index','config.get_cohort_index(cohort_name)' in s and 'cohort_id={cohort_index}' in s)
s=method('sql.py','SQLCohortDataAPI','get_patient_metadata_df');check('SQLmetadata selectsame numericcohortID','WHERE cohort_id={cohort_index}' in s)
s=method('provider-sql.py','SQLProvider','_db_patient_meta_data_importer');check('SQLimport path getter links positional metadata','config.get_patients_metadata_path(cohort_index)' in s)
prior=HERE.parent/'dated_route_documentation_review';check('old datedfreeze unchanged',sha(prior/'FREEZE.json')=='98ee5308e8aa232d394f38a88d1d2ef74814c1aedc2d25ed86d5014d1316af70')
for x in json.loads((prior/'FREEZE.json').read_text())['bindings']:check('old datedexport '+x['file'],sha(prior/x['file'])==x['sha256'])
parent=HERE.parent;check('old original sciencefreeze unchanged',sha(parent/'FREEZE.json')=='490da03d703fff7519096c2c0ef6ccc5175f74f784276985c2d3fe2a4c9dc1a1')
for x in json.loads((parent/'FREEZE.json').read_text())['bindings']:check('old scienceexport '+x['file'],sha(parent/x['file'])==x['sha256'])
port=json.loads((HERE/'PORTABILITY.json').read_text())
for x in port['shared_readonly_originals']:check('shared original '+Path(x['path']).name,sha(Path(x['path']))==x['sha256'])
check('newraw 53068B cap',port['new_raw_bytes']==53068 and port['new_raw_bytes']<8388608)
req=json.loads((HERE/'EXACT-METADATA-REQUEST-PROPOSAL.json').read_text());check('exactfourlisted indexrequests',[x['documented_zero_based_index'] for x in req['requests']]==[0,1,2,3] and req['field_mask']==['primary_diagnosis only'] and req['no_calls_executed'])
check('freefloor10GiB',shutil.disk_usage(HERE).free>=10737418240)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS bounded intendedindex/schema verification','checks':checks,'checks_count':len(checks),'clinical_API_calls':0,'source_execution':False,'biochemical_or_treatment_outcomes_inspected':0,'runtime_auth_or_configuration':'Notverified; independent source-documentation rule only','repo_gates':'Integrating lead pending, not sparseworkerpassed'}
(HERE/'VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(checks),'failed':0}))
