"""Safely reproduce the immutable experiment in a new, explicitly named directory."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import zipfile

PACKAGE = Path(__file__).resolve().parent
EXPERIMENT = 'trial-frozen-baseline-2026-09-06'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def read(path): return json.loads(path.read_text(encoding='utf-8'))

def safe_name(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '\\' in name or ':' in name or str(p)!=name:
        raise ValueError('Unsafe ZIP path: '+name)
    reserved={'CON','PRN','AUX','NUL'}|{'COM'+str(i) for i in range(1,10)}|{'LPT'+str(i) for i in range(1,10)}
    if any(x in ('','.','..') or x.endswith((' ','.')) or x.split('.')[0].upper() in reserved for x in p.parts):
        raise ValueError('Unsafe ZIP component: '+name)
    return p

def verify_hashes(root, hashes):
    for name, expected in hashes.items():
        rel=safe_name(name)
        if digest(root.joinpath(*rel.parts))!=expected: raise ValueError('Hash mismatch: '+name)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,help='A new directory that must not already exist')
    args=parser.parse_args()
    output=Path(args.output).expanduser().absolute()
    if output.exists() or output.is_symlink(): raise ValueError('Output must not already exist')
    if not output.parent.is_dir(): raise ValueError('Output parent must already exist')
    output=output.parent.resolve()/output.name
    manifest=read(PACKAGE/'archive-manifest.json')
    archive=PACKAGE/'frozen-experiment.zip'
    if digest(archive)!=manifest['archive_sha256']: raise ValueError('Archive digest mismatch')
    entries=manifest['entries']
    # Validate the entire central directory and manifest before creating output.
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist(); names=[x.filename for x in infos]
        if len(names)!=len(set(n.casefold() for n in names)): raise ValueError('Duplicate ZIP paths')
        if set(names)!=set(entries): raise ValueError('Archive/manifest entry mismatch')
        for info in infos:
            safe_name(info.filename)
            if info.is_dir() or stat.S_ISLNK(info.external_attr>>16): raise ValueError('Non-file ZIP entry')
            if info.file_size!=entries[info.filename]['size']: raise ValueError('ZIP entry size mismatch')
        output.mkdir(exist_ok=False)
        for info in infos:
            target=output.joinpath(*safe_name(info.filename).parts)
            if not target.resolve().is_relative_to(output): raise ValueError('Extraction outside output')
            target.parent.mkdir(parents=True,exist_ok=True)
            h=hashlib.sha256(); size=0
            with z.open(info) as src, target.open('xb') as dst:
                for block in iter(lambda:src.read(1024*1024),b''):
                    h.update(block); size+=len(block); dst.write(block)
            if size!=entries[info.filename]['size'] or h.hexdigest()!=entries[info.filename]['sha256']:
                raise ValueError('Extracted entry mismatch: '+info.filename)
    experiment=output/EXPERIMENT
    verify_hashes(output,read(experiment/'freeze.json')['hashes'])
    verify_hashes(experiment,read(experiment/'output-manifest.json'))
    original_results=read(experiment/'first-run-hashes.json')
    verify_hashes(experiment,original_results)
    commands=[['baseline.py','verify'],['baseline.py','check'],['baseline.py','run'],['verify_results.py']]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (output/'reproduction.log').open('w',encoding='utf-8') as log:
        for command in commands:
            invocation=[sys.executable,'-B','-X','utf8',str(experiment/command[0]),*command[1:]]
            log.write(json.dumps({'command':invocation})+'\n'); log.flush()
            run=subprocess.run(invocation,cwd=output,stdout=log,stderr=subprocess.STDOUT,check=False)
            log.write(json.dumps({'exit_code':run.returncode})+'\n'); log.flush()
            if run.returncode: raise RuntimeError('Reproduction command failed; inspect reproduction.log')
    verify_hashes(experiment,original_results)
    verify_hashes(output,read(experiment/'freeze.json')['hashes'])
    verification=read(experiment/'verification.json')
    if not verification['pilot_failed_screen_rejected'] or verification['reference_value_read_calls']!=0:
        raise ValueError('Pilot access guard did not pass')
    if digest(archive)!=manifest['archive_sha256']: raise ValueError('Archive changed during reproduction')
    receipt={'started_utc':started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python':sys.executable,'output_directory':str(output),'archive_sha256':manifest['archive_sha256'],
        'archive_preserved':True,'entries_verified':len(entries),'frozen_input_hashes_verified':True,
        'original_artifact_hashes_verified_before_execution':True,'five_result_hashes':original_results,
        'all_five_results_identical':True,'pilot_failed_screen_rejected':True,'reference_value_read_calls':0,
        'log_sha256':digest(output/'reproduction.log'),'status':'passed'}
    (output/'reproduction-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
