"""Offline path-only replay of eight unchanged historical scientific files."""
from pathlib import Path,PurePosixPath,PureWindowsPath
import argparse,copy,csv,datetime,gzip,hashlib,importlib.metadata,json,os,platform,shutil,stat,subprocess,sys,time,traceback,zipfile
HERE=Path(__file__).resolve().parent
CSV_FILES=['all12-gene-effects.csv','all-hofvander-contrasts.csv','all-primary-deletions.csv','all-year-cells.csv','all-shared-histology-replication.csv']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def no_links(p):
    for q in [p]+list(p.parents):
        if q.is_symlink() or (hasattr(q,'is_junction') and q.is_junction()):raise ValueError('link/junction path refused: '+str(q))
def destination(root,rel):
    rel=str(rel).replace('\\','/');s=PurePosixPath(rel)
    if s.is_absolute() or '..' in s.parts or PureWindowsPath(rel).drive:raise ValueError('unsafe relative path: '+rel)
    p=root.joinpath(*s.parts);no_links(p);p.resolve().relative_to(root.resolve());return p
def check_digest(p,expected):
    no_links(p);assert p.is_file() and sha(p)==expected,str(p)
def extract_selected(archive,root,files,archive_members):
    with zipfile.ZipFile(archive) as z:
        names=[]
        for info in z.infolist():
            destination(root,info.filename)
            if stat.S_ISLNK(info.external_attr>>16):raise ValueError('archive link refused')
            names.append(info.filename)
        assert len(names)==len(set(names)),'duplicate archive members'
        for name,digest in files.items():
            assert archive_members[name]==digest
            data=z.read(name);assert hashlib.sha256(data).hexdigest()==digest
            target=destination(root,name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
def command(args,cwd,run,tag,receipt):
    start=utc();tick=time.perf_counter();env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONNOUSERSITE']='1'
    (run/'temporary').mkdir(exist_ok=True)
    for key in ['TEMP','TMP','TMPDIR']:env[key]=str(run/'temporary')
    with (run/(tag+'.stdout.log')).open('w',encoding='utf-8') as out,(run/(tag+'.stderr.log')).open('w',encoding='utf-8') as err:
        result=subprocess.run(args,cwd=cwd,env=env,stdout=out,stderr=err)
    record={'command':args,'cwd':str(cwd),'started_utc':start,'finished_utc':utc(),'elapsed_seconds':time.perf_counter()-tick,'exit_code':result.returncode,'environment_overrides':{'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'},'stdout_sha256':sha(run/(tag+'.stdout.log')),'stderr_sha256':sha(run/(tag+'.stderr.log'))};receipt['commands'].append(record);dump(run/'receipt.json',receipt)
    if result.returncode:raise RuntimeError(tag+' exit '+str(result.returncode))
def compare(a,b,path,state):
    if type(a)!=type(b):state['mismatches'].append({'path':path,'expected_type':type(a).__name__,'actual_type':type(b).__name__});return
    if isinstance(a,dict):
        if set(a)!=set(b):state['mismatches'].append({'path':path,'expected_keys':sorted(a),'actual_keys':sorted(b)})
        for k in a.keys()&b.keys():compare(a[k],b[k],path+'/'+k,state)
    elif isinstance(a,list):
        if len(a)!=len(b):state['mismatches'].append({'path':path,'expected_length':len(a),'actual_length':len(b)})
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i),state)
    else:
        state['scalar_comparisons']+=1
        if a!=b:state['mismatches'].append({'path':path,'expected':a,'actual':b})
def compare_outputs(frozen,run,compat):
    state={'policy':'strict decoded types/values, full arrays/order; named top-level provenance only excepted','scalar_comparisons':0,'mismatches':[],'files':[],'provenance_checks':[]}
    for directory in ['results','replication-results']:
        expected_files={p.name for p in (frozen/directory).glob('*.json')};actual_files={p.name for p in (run/directory).glob('*.json')};assert actual_files==expected_files,(expected_files,actual_files)
        for name in sorted(expected_files):
            ep=frozen/directory/name;ap=run/directory/name;a=json.loads(ep.read_text());b=json.loads(ap.read_text());path=directory+'/'+name
            if name=='execution.json':
                assert b['status']=='complete' and 'error' not in b and a['stage']==b['stage']
                state['provenance_checks'].append({'path':path,'status_and_stage_match':True,'timestamps':'retained, not equality targets'});continue
            if name=='result.json':
                assert b.pop('authorization')==compat;a.pop('authorization')
                if directory=='replication-results':
                    assert b.pop('original_result_sha256')==sha(run/'results/result.json');a.pop('original_result_sha256')
                state['provenance_checks'].append({'path':path,'authorization_matches_compatibility':True,'original_result_digest_verified':directory=='replication-results'})
            compare(a,b,path,state);state['files'].append({'path':path,'expected_sha256':sha(ep),'replay_sha256':sha(ap)})
    for name in CSV_FILES:
        with (frozen/name).open(newline='',encoding='utf-8') as f:a=list(csv.DictReader(f))
        with (run/'reports'/name).open(newline='',encoding='utf-8') as f:b=list(csv.DictReader(f))
        compare(a,b,'reports/'+name,state);state['files'].append({'path':'reports/'+name,'expected_sha256':sha(frozen/name),'replay_sha256':sha(run/'reports'/name),'comparison':'exact parsed strings/column keys and row order (stronger than numeric semantic equality)'})
    dump(run/'comparison.json',state);assert not state['mismatches'],'scientific replay mismatch'
    return state
def main(bundle,frozen,run):
    no_links(bundle);no_links(frozen);no_links(run);bundle=bundle.resolve();frozen=frozen.resolve();run=run.resolve();assert not run.exists(),'run directory must be new';run.mkdir(parents=True)
    receipt={'record_kind':'mechanical_path_only_local_replay','started_utc':utc(),'status':'running','initiator':'worker /root/resume_existing_evidence on coordinator standing replay authorization','standing_authorization':json.loads((HERE/'standing-authorization.json').read_text()),'commands':[],'host_scope':'one fresh directory on this Windows host; no second host/OS claim'};dump(run/'receipt.json',receipt)
    try:
        lock=json.loads((HERE/'input-lock.json').read_text());codefreeze=json.loads((HERE/'code-freeze.json').read_text())
        for name,h in codefreeze.items():check_digest(HERE/name,h)
        for name,record in lock['bundle_inputs'].items():check_digest(bundle/name,record['sha256'])
        for name,h in lock['frozen_inputs'].items():check_digest(frozen/name,h)
        receipt['input_lock_sha256']=sha(HERE/'input-lock.json');receipt['code_freeze_sha256']=sha(HERE/'code-freeze.json');receipt['bundle_inputs']=lock['bundle_inputs']
        versions={'python':platform.python_version(),**{n:importlib.metadata.version(n) for n in ['numpy','openpyxl','et-xmlfile']}}
        assert versions=={'python':'3.12.14','numpy':'2.3.5','openpyxl':'3.1.5','et-xmlfile':'2.0.0'},versions
        receipt['environment']={'versions':versions,'executable':sys.executable,'implementation':platform.python_implementation(),'platform':platform.platform(),'machine':platform.machine()}
        authorization=json.loads((frozen/'coordinator-authorization.json').read_text());receipt['historical_authorization_sha256']=sha(frozen/'coordinator-authorization.json')
        code=run/'code';code.mkdir();historical=run/'frozen';historical.mkdir()
        for name,h in authorization['sha256'].items():check_digest(frozen/name,h);shutil.copyfile(frozen/name,code/name);shutil.copyfile(frozen/name,historical/name)
        shutil.copyfile(frozen/'coordinator-authorization.json',historical/'coordinator-authorization.json')
        hm=json.loads((code/'metadata-manifest.json').read_text());am=json.loads((code/'replication-manifest.json').read_text());hs=run/'sources/hofvander';ars=run/'sources/array';hs.mkdir(parents=True);ars.mkdir(parents=True)
        hp=bundle/'research/autonomy/atlas-hofvander-source-2026-09-06';hpv=json.loads((hp/'preservation-manifest.json').read_text());ap=bundle/'research/autonomy/atlas-original-array-source-2026-09-06';apv=json.loads((ap/'preservation-manifest.json').read_text())
        check_digest(hp/'tpm_matrix.tsv.gz',hpv['matrix']['compressed_sha256']);check_digest(hp/'source-provenance.zip',hpv['source_provenance_archive']['sha256']);check_digest(ap/'original-source-recovery.zip',apv['source_archive']['sha256'])
        dst=destination(hs,'source_data/tpm_matrix.tsv');dst.parent.mkdir(parents=True)
        with gzip.open(hp/'tpm_matrix.tsv.gz','rb') as src,dst.open('wb') as target:shutil.copyfileobj(src,target)
        extract_selected(hp/'source-provenance.zip',hs,{n:r['sha256'] for n,r in hm['source_files'].items() if n!='source_data/tpm_matrix.tsv'},hpv['source_provenance_archive']['members'])
        extract_selected(ap/'original-source-recovery.zip',ars,{n:r['sha256'] for n,r in am['source_files'].items() if n!='GSE24369.soft.gz'},apv['source_archive']['members'])
        oldarray=apv['excluded_duplicate_preserved_at']['GSE24369.soft.gz'];check_digest(bundle/oldarray['path'],oldarray['sha256']);shutil.copyfile(bundle/oldarray['path'],ars/'GSE24369.soft.gz')
        receipt['source_members']={}
        for manifest,folder in [(hm,hs),(am,ars)]:
            for name,r in manifest['source_files'].items():check_digest(folder/name,r['sha256']);receipt['source_members'][str(folder.relative_to(run)/name)]={'sha256':sha(folder/name),'bytes':(folder/name).stat().st_size}
        relocated=[]
        for name,folder in [('metadata-manifest.json',hs),('replication-manifest.json',ars)]:
            original=json.loads((code/name).read_text());derived=copy.deepcopy(original);derived['source_location']=str(folder)
            x=copy.deepcopy(original);y=copy.deepcopy(derived);x.pop('source_location');y.pop('source_location');assert x==y
            before=sha(code/name);dump(code/name,derived);relocated.append({'file':name,'json_pointer':'/source_location','before':original['source_location'],'after':derived['source_location'],'original_sha256':before,'derived_sha256':sha(code/name),'all_other_decoded_content_identical':True})
        compat=copy.deepcopy(authorization)
        for r in relocated:compat['sha256'][r['file']]=r['derived_sha256']
        compat.update({'record_kind':'local_replay_compatibility','original_authorization_sha256':sha(frozen/'coordinator-authorization.json'),'original_authorization_path':str(historical/'coordinator-authorization.json'),'relocations':relocated,'local_replay_initiator':receipt['initiator'],'local_replay_started_utc':receipt['started_utc'],'notice':'Historical coordinator fields satisfy the unchanged entry-point schema. They are not newly issued coordinator approval, a new preregistration, a new hypothesis, clinical authority or publication permission. Mechanical local replay is separately authorized by standing-authorization.json.'})
        dump(code/'replay-compatibility.json',compat);receipt['relocations']=relocated;receipt['compatibility_sha256']=sha(code/'replay-compatibility.json');dump(run/'receipt.json',receipt)
        prefix=[sys.executable,'-B','-X','utf8']
        command(prefix+[str(code/'analyze.py')],code,run,'fixtures-hofvander',receipt);command(prefix+[str(code/'replication.py')],code,run,'fixtures-replication',receipt)
        command(prefix+[str(code/'analyze.py'),'--authorization',str(code/'replay-compatibility.json'),'--output',str(run/'results')],code,run,'hofvander',receipt)
        command(prefix+[str(code/'replication.py'),'--authorization',str(code/'replay-compatibility.json'),'--original-results',str(run/'results'),'--output',str(run/'replication-results')],code,run,'replication',receipt)
        normal=bundle/'research/autonomy/atlas-normal-context-2026-09-06/fixed-panel-normal-context-roster.json'
        command(prefix+[str(HERE/'report.py'),'--run-dir',str(run),'--normal-context',str(normal)],code,run,'reporting',receipt)
        result=compare_outputs(frozen,run,compat);receipt['comparison']={'files':len(result['files']),'scalar_comparisons':result['scalar_comparisons'],'mismatches':len(result['mismatches']),'comparison_sha256':sha(run/'comparison.json')};receipt['status']='complete'
        # Original science, original expected files, and wrapper bytes still match.
        for name,h in lock['frozen_inputs'].items():check_digest(frozen/name,h)
        for name,h in codefreeze.items():check_digest(HERE/name,h)
    except Exception:
        receipt['status']='failed';receipt['error']=traceback.format_exc();raise
    finally:
        receipt['finished_utc']=utc();dump(run/'receipt.json',receipt)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--frozen-packet',type=Path,default=HERE.parent);p.add_argument('--run-dir',type=Path,required=True);a=p.parse_args();main(a.bundle,a.frozen_packet,a.run_dir)
