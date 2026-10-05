#!/usr/bin/env python3
"""Read-only byte/source-availability R8 checkpoint audit; no numerical science rerun."""
import argparse,ast,collections,copy,datetime,hashlib,json,pathlib,re,shutil,struct,subprocess,zipfile,xml.etree.ElementTree as E
P=pathlib.Path(__file__).resolve().parent;R=pathlib.Path('/workspace/Rare-cancers');B=pathlib.Path('research/autonomy/fresh-discovery-2026-10-05-round8')
ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(P/'REVIEW-PRELIMINARY.json'));ap.add_argument('--phase',choices=['preliminary','final'],default='preliminary');args=ap.parse_args()
def run(*cmd,cwd=R):return subprocess.check_output(cmd,cwd=cwd)
def digest(b):return hashlib.sha256(b).hexdigest()
hash_memo={}
def filehash(p):
 p=p.resolve();st=p.stat();key=(str(p),st.st_size,st.st_mtime_ns)
 if key in hash_memo:return hash_memo[key]
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 hash_memo[key]=h.hexdigest();return hash_memo[key]
assign=json.load(open(R/B/'ROUND-CONTRACT.json'))['assignments'];source_checks=[];sourcepins=[];roottracked=set(run('git','ls-files',str(B)).decode().splitlines());json_fail=[];freezechecks=[];dependency_checks={};all_root_files=sorted(set(roottracked)|{str(x.relative_to(R)) for x in (R/B).rglob('*') if x.is_file() and '.cache' not in x.parts and 'sources' not in x.parts})
exportfile=R/B/'PORTABLE-EXPORT.json';export=json.load(open(exportfile)) if exportfile.is_file() else None;exportpins={x['branch']:x for x in export['source_branches']} if export else {}
name_locations=collections.defaultdict(list);compact_locations=set()
for work in [R]+[pathlib.Path(a['worktree']) for a in assign]:
 for name in run('git','ls-files',cwd=work).decode().splitlines():compact_locations.add(str((work/name).resolve()))
 roots=[work/B,work/'research/autonomy/fresh-discovery-2026-10-04-round6/single_cell']
 for root in roots:
  if root.exists():
   for f in root.rglob('*'):
    if f.is_file():name_locations[f.name].append(f.resolve())
for name in all_root_files:
 if name.endswith('.json'):
  try:json.load(open(R/name))
  except Exception as e:json_fail.append({'path':name,'error':str(e)})
for item in assign:
 W=pathlib.Path(item['worktree']);lane=item['lane'];pin=exportpins.get(item['branch']);commit=pin['source_local_commit'] if pin else run('git','rev-parse','HEAD',cwd=W).decode().strip();prefix=B/lane
 # Additional source-gate packet belongs to this same explicit writer lease.
 prefixes=[prefix]+([B/'cell_compartment_source_gate'] if lane=='adaptation' else [])+([B/'adc_targets'] if lane=='neurosecretory' else [])
 if pin:prefixes=[B/name for name in pin['lanes']]
 paths=run('git','ls-tree','-r','--name-only',commit,'--',*[str(x) for x in prefixes],cwd=W).decode().splitlines();sourcepins.append({'lane':lane,'worktree':str(W),'commit':commit,'source_files':len(paths)})
 whole_worker_tree=set(run('git','ls-tree','-r','--name-only',commit,cwd=W).decode().splitlines())
 for name in paths:
  original=run('git','show',commit+':'+name,cwd=W);target=R/name;exists=target.exists();source_checks.append({'path':name,'source_commit':commit,'source_sha256':digest(original),'bytes':len(original),'root_present':exists,'root_matches_original':exists and filehash(target)==digest(original),'root_git_tracked':name in roottracked})
  if not name.endswith('.json'):continue
  try:j=json.loads(original)
  except Exception:continue
  parent=W/pathlib.Path(name).parent
  # Hash-bound compact freeze/manifests. Preserve historical output and later additive amendments.
  if 'FREEZE' in pathlib.Path(name).name or pathlib.Path(name).name=='MANIFEST.json':
   for field in ['files','file_hashes','bindings','committed_evidence']:
    data=j.get(field,[]) if isinstance(j,dict) else []
    records=[]
    if isinstance(data,dict):
     for key,val in data.items():
      records.append({'path':key,'sha256':val if isinstance(val,str) else val.get('sha256'),'bytes':None if isinstance(val,str) else val.get('bytes')})
    elif isinstance(data,list):records=[x for x in data if isinstance(x,dict) and 'path' in x and 'sha256' in x]
    for x in records:
     if not isinstance(x.get('sha256'),str) or len(x['sha256'])!=64:continue
     target=parent/x['path'];root_target=R/pathlib.Path(name).parent/x['path'];present=target.exists();freezechecks.append({'freeze':name,'binding':x['path'],'sha256':x['sha256'],'original_worker_file_matches':present and filehash(target)==x['sha256'],'root_file_matches':root_target.exists() and filehash(root_target)==x['sha256'],'root_present':root_target.exists()})
  def descend(x):
   if isinstance(x,dict):
    if isinstance(x.get('sha256'),str) and re.fullmatch('[0-9a-f]{64}',x['sha256']):
     path=next((x[k] for k in ['path','cache_path','local_path','raw_path','source_path'] if isinstance(x.get(k),str)),None)
     if path:
      rel=pathlib.Path(path);candidates=[rel] if rel.is_absolute() else [parent/rel,W/rel,R/rel,W/'research/autonomy'/rel,R/'research/autonomy'/rel]
      candidates += name_locations[rel.name]
      # Peer receipts deliberately use paths relative to their reviewed packet or reused_base.
      # Resolve existing byte-matched peer inputs instead of fabricating unavailable copies.
      matching=[f for f in candidates if f.is_file() and filehash(f)==x['sha256']]
      actual=(matching[0] if matching else next((f for f in candidates if f.is_file()),candidates[0])).resolve();key=(str(actual),x['sha256'])
      try:worker_rel=str(actual.relative_to(W))
      except ValueError:worker_rel=None
      shared=(str(actual).startswith('/workspace/Rare-cancers/') and not str(actual).startswith(str(R/B)))
      is_compact=str(actual) in compact_locations
      if not is_compact or shared:
       exists=actual.is_file();root_guess=R/rel if not rel.is_absolute() else actual
       rec=dependency_checks.setdefault(key,{'path':str(actual),'declared_path':path,'sha256':x['sha256'],'declared_bytes':x.get('bytes',x.get('retained_bytes')),'available_local':exists,'actual_sha256':filehash(actual) if exists else None,'source_receipts':[],'storage_class':'existing shared legacy read-only input' if shared else 'cache-only or original unavailable; not a compact worker Git export','root_original_copied':root_guess.is_file() and not shared and root_guess!=actual})
       rec['source_receipts'].append(name)
    for v in x.values():descend(v)
   elif isinstance(x,list):
    for v in x:descend(v)
  descend(j)
# Initial seven and explicit later amendments: exact hashes and read_by-only semantic delta.
regpath='research/manuscripts/emc-systems-map.json';registry=json.load(open(R/regpath));registry_base=json.load(open(R/B/'ROUND-CONTRACT.json'))['base_commit'];prior_bytes=run('git','show',registry_base+':'+regpath);prior=json.loads(prior_bytes);registration=json.load(open(R/B/'MODEL-CONSUMER-REGISTRATION.json'));diffs=[];assert digest(prior_bytes)==registration['registry_before_sha256'];registry_chain_sha=registration['registry_after_sha256'];registry_amendments=[];added_consumers=[{'consumer':x,'sha256':registration['source_file_hashes'][x['file']]} for x in registration['added_consumers']]
for f in sorted((R/B).glob('MODEL-CONSUMER-AMENDMENT-*.json')):
 record=json.load(open(f));assert record['registry_before_sha256']==registry_chain_sha;registry_chain_sha=record['registry_after_sha256'];registry_amendments.append({'path':str(f.relative_to(R)),'sha256':filehash(f),'before_sha256':record['registry_before_sha256'],'after_sha256':registry_chain_sha});added=record['added'];added_consumers.extend(added if isinstance(added,list) else [{'consumer':added,'sha256':record['consumer_sha256']}])
formatfile=R/B/'INTEGRATION-REPAIR-RECEIPT.json';formatcheck=None
if formatfile.is_file():
 formatting=json.load(open(formatfile));assert formatting['map_before_sha256']==registry_chain_sha;assert formatting['map_after_sha256']==filehash(R/regpath);assert formatting['semantic_equal'] is True
 expected=copy.deepcopy(prior);expected['objects'][18]['read_by'].extend(x['consumer'] for x in added_consumers);assert expected==registry
 formatcheck={'path':str(formatfile.relative_to(R)),'sha256':filehash(formatfile),'before_sha256':registry_chain_sha,'after_sha256':filehash(R/regpath),'semantic_equality_independently_verified':'Entire parsed registry equals base registry with only the exact ten appended reader classifications; all identity/measurement fields unchanged.'}
else:assert filehash(R/regpath)==registry_chain_sha
def delta(a,b,path=''):
 if type(a)!=type(b):diffs.append({'path':path,'kind':'type'});return
 if isinstance(a,dict):
  for k in set(a)|set(b):
   if k not in a or k not in b:diffs.append({'path':path+'/'+k,'kind':'key'})
   elif a[k]!=b[k]:delta(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):diffs.append({'path':path,'kind':'list_length','before':len(a),'after':len(b),'new_tail':b[len(a):]});return
  for i,(x,y) in enumerate(zip(a,b)):
   if x!=y:delta(x,y,path+'/'+str(i))
 else:diffs.append({'path':path,'kind':'value'})
delta(prior,registry);model_checks=[]
for entry in added_consumers:
 x=entry['consumer']
 f=R/x['file'];text=f.read_text();model_checks.append({'consumer':x,'sha256':filehash(f),'matches_registration':filehash(f)==entry['sha256'],'verified_source_context_lines':[{'line':i+1,'line_sha256':digest(line.encode()),'semantic_use':'Source-discovery query' if 'metabolism/' in x['file'] else 'Explicit model exclusion or identity-pending limitation'} for i,line in enumerate(text.splitlines()) if any(alias.casefold() in line.casefold() for alias in registry['objects'][18]['aliases'])]})
# File/storage screen: suffix/magic, NPZ header only, no array values or scientific outcomes.
file_inventory=[];suspicious=[];npz_headers=[]
for name in all_root_files:
 f=R/name;b=f.read_bytes();rec={'path':name,'bytes':len(b),'sha256':digest(b),'git_tracked':name in roottracked};file_inventory.append(rec)
 if any(part in ['sources','source-cache','.cache','raw'] for part in pathlib.Path(name).parts) or re.search(r'\.(pdf|xml|fastq|fq|h5|h5ad|rds|tar|gz|zip)$',name,re.I) or b.startswith(b'%PDF-') or b.startswith(b'<?xml') or b.startswith(b'@SRR'):suspicious.append(rec)
 if f.suffix=='.npz':
  heads=[]
  with zipfile.ZipFile(f) as z:
   for member in z.namelist():
    with z.open(member) as q:
     header=q.read(8);assert header[:6]==b'\x93NUMPY';ver=tuple(header[6:]);count=2 if ver==(1,0) else 4;n=struct.unpack('<H' if count==2 else '<I',q.read(count))[0];meta=ast.literal_eval(q.read(n).decode())
    heads.append({'member':member,'header':meta})
  npz_headers.append({'path':name,'bytes':len(b),'headers':heads,'interpretation':'Header/storage check only, deliberately derived TempO probe-count vector governed by AMENDMENT-03; not raw FASTQ or a downloaded full source matrix.'})
# Independently verify every declared export, without calling the lead verifier.
export_checks=[]
if export:
 seen=set()
 for x in export['files']:
  rel=pathlib.Path(x['path']);f=(R/rel).resolve();safe=not rel.is_absolute() and f.is_relative_to(R) and str(rel) not in seen;seen.add(str(rel));exists=f.is_file() if safe else False
  export_checks.append({'path':x['path'],'safe_unique_relative_path':safe,'present':exists,'declared_bytes':x['bytes'],'actual_bytes':f.stat().st_size if exists else None,'declared_sha256':x['sha256'],'actual_sha256':filehash(f) if exists else None,'matches':exists and f.stat().st_size==x['bytes'] and filehash(f)==x['sha256'],'original_worker_record':bool(x.get('source_local_commit'))})
 assert len(export_checks)==export['total_files'];assert sum(x['declared_bytes'] for x in export_checks)==export['total_bytes'];assert sum(x['original_worker_record'] for x in export_checks)==export['worker_files'];assert {x['path'] for x in export_checks if x['original_worker_record']}=={x['path'] for x in source_checks}
# Exact current lead-reader hashes; absent/future files remain pending, never a final approval.
readers=[f for f in (R/B).iterdir() if f.is_file()]+[R/regpath,R/'research/manuscripts/emc-systems-map.md',R/'research/autonomy/fresh-discovery-2026-10-04-handoff/CLOUD-HANDOFF.md',R/'research/autonomy/fresh-discovery-2026-10-04-handoff/CONTINUE-IN-CLOUD.txt'];reader_hashes={str(f.relative_to(R)):{'bytes':f.stat().st_size,'sha256':filehash(f)} for f in sorted(readers)}
ci=json.load(open(R/B/'INHERITED-CI-STATUS.json'));normal_files=[str(f.relative_to(R)) for f in (R/B).glob('*PREFLIGHT*')]
ci_original=R/ci['original_log']['path'];ci_log_check={'path':ci['original_log']['path'],'declared_bytes':ci['original_log']['bytes'],'declared_sha256':ci['original_log']['sha256'],'available_local':ci_original.is_file(),'bytes_match':ci_original.is_file() and ci_original.stat().st_size==ci['original_log']['bytes'],'sha256_match':ci_original.is_file() and filehash(ci_original)==ci['original_log']['sha256'],'storage':'Existing ignored local CI log; not a scientific raw input or new Git export'}
stream_records=[];count_derivatives=[]
micro=next(a for a in assign if a['lane']=='microenvironment');mroot=pathlib.Path(micro['worktree'])/B/'microenvironment';streamfile=mroot/'COMPLETE-TEMPO-SOURCE-RECEIPTS.json'
if streamfile.is_file():
 for x in json.load(open(streamfile)):
  stream_records.append({k:x.get(k) for k in ['sample','run','url','complete','expected_bytes','compressed_bytes','expected_md5','compressed_md5','compressed_sha256','FASTQ_retained_bytes']})
  f=mroot/x['count_output'];count_derivatives.append({'sample':x['sample'],'path':str(f),'declared_sha256':x['count_sha256'],'available_local':f.is_file(),'actual_sha256':filehash(f) if f.is_file() else None,'matches':f.is_file() and filehash(f)==x['count_sha256'],'root_git_tracked':str(B/'microenvironment'/x['count_output']) in roottracked,'storage':'Derived probe-count vector in local cache; no array values read or count analysis rerun'})
surface=next(a for a in assign if a['lane']=='surface_targets');surfacehash=json.load(open(pathlib.Path(surface['worktree'])/B/'surface_targets/SOURCE-HASHES.json'))
not_retained={'TempO_stream_receipt_sha256':filehash(streamfile) if streamfile.is_file() else None,'TempO_receipts':stream_records,'TempO_declared_streamed_compressed_bytes':sum(x.get('compressed_bytes',0) or 0 for x in stream_records),'TempO_declared_FASTQ_retained_bytes':sum(x.get('FASTQ_retained_bytes',0) or 0 for x in stream_records),'TempO_derived_vectors':count_derivatives,'surface_streamed_archive_members':surfacehash['streamed_members'],'methylation_matrix_status':json.load(open(R/B/'methylation/MANIFEST.json'))['matrix_files'],'audit_limit':'Receipt/storage/hash checks only. No full FASTQ/source member re-download or numerical matrix/scientific reconstruction; source-stream hashes remain the workers recorded measurements.'}
citationcheck=None
anchorfile=R/B/'PRIMARY-CITATION-ANCHOR.json'
if anchorfile.is_file():
 anchor=json.load(open(anchorfile));f=pathlib.Path(anchor['source_path']);assert f.is_file() and f.stat().st_size==anchor['source_bytes'] and filehash(f)==anchor['source_sha256']
 source=E.fromstring(f.read_bytes());fields={x.attrib['key']:x.text for x in source.findall('.//infon') if x.attrib.get('key') in anchor['source_fields']}
 assert fields==anchor['source_fields']
 citationcheck={'path':str(anchorfile.relative_to(R)),'sha256':filehash(anchorfile),'source_path':str(f),'source_sha256':filehash(f),'all_three_identifier_fields_equal_primary_XML':True,'scope':'Primary metadata-only citation anchor independently verified; no patient treatment result inferred or new retrieval.'}
gatechecks=[]
for f in sorted((R/B).glob('VALIDATION*.json')):
 record=json.load(open(f));log=R/B/('PREFLIGHT-INITIAL.log' if 'INITIAL' in f.name else 'PREFLIGHT.log')
 if 'log_sha256' in record:
  gatechecks.append({'receipt':str(f.relative_to(R)),'receipt_sha256':filehash(f),'log':str(log.relative_to(R)),'actual_log_bytes':log.stat().st_size if log.is_file() else None,'actual_log_sha256':filehash(log) if log.is_file() else None,'log_matches_receipt':log.is_file() and log.stat().st_size==record['log_bytes'] and filehash(log)==record['log_sha256'],'command':record.get('command'),'mode':record.get('normal_mode_flags'),'exit_code':record.get('exit_code'),'scope':record.get('scope')})
deps=list(dependency_checks.values());out={'schema':'emc-r8-independent-lead-portability-review/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':args.phase,'root_commit':run('git','rev-parse','HEAD').decode().strip(),'scope':'Byte/source availability, storage/declarations/reader-state only; no biological measurement, scientific reanalysis or publication certification','source_pins':sourcepins,'portable_export_manifest':{'path':str(exportfile.relative_to(R)),'sha256':filehash(exportfile),'total_files':export['total_files'],'total_bytes':export['total_bytes'],'worker_files':export['worker_files'],'mismatch_count':sum(not x['matches'] for x in export_checks),'checks':export_checks,'scope':'Independent every-export byte/size/path check plus original-worker Git comparisons; no raw-source reproduction or branch remote reachability inferred'} if export else None,'worker_export_checks':source_checks,'worker_export_counts':{'files':len(source_checks),'present':sum(x['root_present'] for x in source_checks),'mismatches_present':sum(x['root_present'] and not x['root_matches_original'] for x in source_checks),'pending_missing':sum(not x['root_present'] for x in source_checks)},'freeze_checks':freezechecks,'freeze_counts':{'bindings':len(freezechecks),'original_worker_mismatches':sum(not x['original_worker_file_matches'] for x in freezechecks),'root_present_mismatches':sum(x['root_present'] and not x['root_file_matches'] for x in freezechecks),'pending_root_missing':sum(not x['root_present'] for x in freezechecks)},'JSON_parse_failures':json_fail,'cache_dependency_checks':deps,'cache_dependency_counts':{'distinct_declared_path_hash_pairs':len(deps),'available_local':sum(x['available_local'] for x in deps),'original_unavailable_local':sum(not x['available_local'] for x in deps),'available_hash_mismatches':sum(x['available_local'] and x['actual_sha256']!=x['sha256'] for x in deps)},'model_consumer_registry':{'registration_sha256':filehash(R/B/'MODEL-CONSUMER-REGISTRATION.json'),'registry_sha256':filehash(R/regpath),'semantic_changes':diffs,'initial_seven_preserved':len(registration['added_consumers'])==7,'registry_amendment_chain':registry_amendments,'formatting_normalization':formatcheck,'all_added_consumers':model_checks,'interpretation':'Exact source-context/manual review supports search queries and explicit disputed-line exclusions only. No model authentication or measured phenotype accepted.'},'tracked_and_pending_R8_file_inventory':file_inventory,'suspicious_raw_original_files':suspicious,'derived_npz_headers':npz_headers,'reader_hashes':reader_hashes,'method_correction_scope':'Initial methylation method/report/decision freeze preserved; additive AMENDMENT-01 records stemTOC32cancer types includingSARC versus15narrowerendpoint, AMENDMENT-02 separately reassesses favorable age-free cumulative-score value. Review does not rerun arrays.','historical_CI_scope':{'receipt_sha256':filehash(R/B/'INHERITED-CI-STATUS.json'),'base_commit':ci['commit'],'run_id':ci['run_id'],'conclusion':ci['conclusion'],'gates_job':ci['gates_job'],'pytest_job':ci['pytest_job'],'failed_test_ids':[x.split(' - ',1)[0] for x in ci['failures']],'meaning':'Four hosted baseline failures preserved; no full-suite/publication success inferred. Normal preflight receipt scope must be read separately.'},'normal_gate_reader_files':normal_files,'normal_gate_receipt_checks':gatechecks,'primary_citation_repair_check':citationcheck,'CI_original_log_check':ci_log_check,'streamed_and_unstaged_source_declarations':not_retained,'free_disk_bytes':shutil.disk_usage(R).free,'scientific_findings_inferred':False,'root_or_registry_edits':False,'live_owned_processes':0}
pathlib.Path(args.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'phase':args.phase,'source_counts':out['worker_export_counts'],'freeze_counts':out['freeze_counts'],'cache_counts':out['cache_dependency_counts'],'JSON_failures':len(json_fail),'raw_suspicious':len(suspicious),'derived_npz_headers':len(npz_headers),'model_consumers':len(model_checks),'reader_hashes':len(reader_hashes),'review_sha256':filehash(pathlib.Path(args.output))},indent=2))
