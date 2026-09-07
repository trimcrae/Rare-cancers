import pathlib,json,hashlib,subprocess,sys,datetime
ROOT=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
for f in manifest['files']:
    p=ROOT/f['path']; assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256'],f['path']
for f in manifest['dependencies']:
    p=ROOT.parents[2]/f['path']; assert sha(p)==f['sha256'],f['path']
names=['workbook-inventory.json','feature-cell-inventory.json','article-source-locators.json']
before={n:sha(ROOT/n) for n in names}
r=subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'inspect_workbook.py')],capture_output=True,text=True,encoding='utf-8')
assert r.returncode==0,r.stderr
assert before=={n:sha(ROOT/n) for n in names}
for f in json.loads((ROOT/'retrieval.json').read_text(encoding='utf-8-sig')):
    assert sha(ROOT/f['file'])==f['sha256']
f=json.loads((ROOT/'supplement-retrieval.json').read_text());assert sha(ROOT/f['file'])==f['sha256']
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'passed','manifest_files':len(manifest['files']),'dependency_hashes':len(manifest['dependencies']),'regenerated_outputs_equal':names,'all_source_retrieval_hashes_match':True,'full_preflight':'not run by bounded source worker','processes_running':False}
(ROOT/'verification-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
