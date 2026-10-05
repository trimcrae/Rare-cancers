"""Static documentation verification only. Do not execute source or call patient APIs."""
from pathlib import Path
import json,hashlib,ast,shutil,datetime
HERE=Path(__file__).resolve().parent
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,v):
 checks.append({'check':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
app=HERE/'source-cache/app.py';proto=HERE/'source-cache/data_api.py'
check('app primarysource sha',sha(app)=='1329fa7fa220e14068e3565c55f53ec928eae0c878021c833bf46b3bd8784c64')
check('app gitblob matches publictree',hashlib.sha1(b'blob '+str(app.stat().st_size).encode()+b'\x00'+app.read_bytes()).hexdigest()=='ae4497e5b9feb98a693e9d1463aa1f44ec29800b')
check('protocol primarysource sha',sha(proto)=='e83a516ce2a6c1cc8a0203b461a11c244cc650424ab5ce1fc1377a54999fc782')
check('protocol gitblob matches publictree',hashlib.sha1(b'blob '+str(proto.stat().st_size).encode()+b'\x00'+proto.read_bytes()).hexdigest()=='11a0e0c5b841fb91fe62391adc3c64dfb15345ce')
s=app.read_text();tree=ast.parse(s);functions={x.name:x for x in tree.body if isinstance(x,ast.FunctionDef)}
target=['patients','patientsmetadata','patients_meta_fields','unique_field_intereset','get_patientslist_by_fieldname','cohort_names']
for name in target:
 n=functions[name];decs=n.decorator_list
 route=[d for d in decs if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='route']
 check('source app.route '+name,len(route)==1)
 check('default GET no explicit methods '+name,not any(k.arg=='methods' for k in route[0].keywords))
 check('no handler auth decorator '+name,all(isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr in ['route','cached'] for d in decs))
n=functions['unique_field_intereset'];txt=ast.get_source_segment(s,n)
check('one requested field only','get_patient_metadata_df(cohort_index)[fieldname]' in txt)
check('unique filtered string JSONresponse',all(x in txt for x in ['.dropna()','.unique()','.tolist()','str(x)','jsonify(sorted(unique_list))']))
check('no global before_request decorator in module',not any(isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='before_request' for x in tree.body if isinstance(x,ast.FunctionDef) for d in x.decorator_list))
check('cohort names configuration-interface delegation','cohorts_db.config.get_cohort_names()' in ast.get_source_segment(s,functions['cohort_names']))
pt=ast.parse(proto.read_text());cls=next(x for x in pt.body if isinstance(x,ast.ClassDef) and x.name=='CohortDataAPI')
check('imported wrapper only Protocol',any(isinstance(x,ast.Name) and x.id=='Protocol' for x in cls.bases))
check('replicate vs donor contract remains explicit','replicates are included' in proto.read_text() and 'replicates are not included' in proto.read_text())
parent=HERE.parent;check('original scientificfreeze hash unchanged',sha(parent/'FREEZE.json')=='490da03d703fff7519096c2c0ef6ccc5175f74f784276985c2d3fe2a4c9dc1a1')
old=json.loads((parent/'FREEZE.json').read_text())
for x in old['bindings']:check('original frozenexport '+x['file'],sha(parent/x['file'])==x['sha256'])
port=json.loads((HERE/'PORTABILITY.json').read_text())
for x in port['zero_copy_shared_originals']:check('sharedsource '+Path(x['path']).name,sha(Path(x['path']))==x['sha256'])
check('8MiB sourcecap',port['new_raw_bytes']==30878 and port['new_raw_bytes']<=8388608)
check('free10GiB',shutil.disk_usage(HERE).free>=10737418240)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS bounded documentation verification','checks':checks,'checks_count':len(checks),'clinical_API_calls':0,'code_execution':False,'biochemical_or_treatment_outcome_values_inspected':0,'no_auth_guarantee':'Source decorators only; deployed access not tested','index_mapping':'Unresolved; no guessed or instantiated index request','full_repo_gates':'Pending integrating lead, not workerpassed'}
(HERE/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'failed':0}))
