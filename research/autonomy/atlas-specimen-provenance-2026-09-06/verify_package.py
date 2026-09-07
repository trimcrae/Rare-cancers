"""Read-only package and inherited-input verification, including required Markdown metadata."""
import datetime, hashlib, json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
manifest=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
for rec in manifest['files']:
    p=ROOT/rec['file']
    assert len(p.read_bytes())==rec['bytes'],rec['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'],rec['file']
    if p.suffix=='.json': json.loads(p.read_text(encoding='utf-8-sig'))
    if p.suffix=='.md':
        t=p.read_text(encoding='utf-8'); fm=t.split('---',2)[1]
        for k in ['id','title','kind','status','purpose','scope','audience','date','last_verified']:
            assert '\n'+k+':' in '\n'+fm,k
        assert all(line.rstrip()==line for line in t.splitlines()),p
proc=subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'check_sources.py')],capture_output=True,text=True,encoding='utf-8')
assert proc.returncode==0,proc.stderr
checks=json.loads(proc.stdout)
assert checks==json.loads((ROOT/'source-checks.json').read_text(encoding='utf-8-sig'))
print(json.dumps({'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package_files_verified':len(manifest['files']),'source_checks_passed':checks['passed'],'check_sources_exit_code':proc.returncode,'scope':'Read-only package hashes, JSON, Markdown metadata, inherited sources and claim-link/definition checks; not an independent scientific review','process_state':'complete; no background processes started'},indent=2))
