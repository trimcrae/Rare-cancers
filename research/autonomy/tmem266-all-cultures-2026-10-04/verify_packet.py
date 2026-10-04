"""Offline preservation, source-result arithmetic and artifact verification."""
import datetime,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old={}
for folder,mname in [('discovery-2026-10-03','MANIFEST-CURRENT.json'),('tmem266-tissue-2026-10-03','MANIFEST.json'),('tmem266-prepublication-2026-10-03','MANIFEST.json'),('tmem266-questions-2026-10-04','MANIFEST.json')]:
    base=P.parent/folder;m=json.loads((base/mname).read_text(encoding='utf-8'))
    for name,record in m['files'].items():
        f=base/name
        assert f.stat().st_size==record['bytes'] and sha(f)==record['sha256'],str(f)
    old[folder]={'verified_files':len(m['files']),'manifest_sha256':sha(base/mname)}
r=json.loads((P/'usz22-prefix-replay.json').read_text(encoding='utf-8'))
assert r['total_complete_records']==607616
assert len(r['events'])==4 and all(len(x['anchor'])==40 for x in r['events'])
assert all(x['matched_records']==x['qualifying_Q20_records']==x['fragments']==0 for x in r['summary'])
for mate,n,digest in [(1,308649,'bb8f6c870aec138b31ffc1d920b12a3aa96212102992a8eb414bd62f0335a1cc'),(2,298967,'b97e2a3effc17e266f92cd48d12d8304f688b0ac6a4a3748161599c4c2c6336c')]:
    v=r['mates'][mate-1]
    assert v['mate']==mate and v['complete_records']==n and v['prefix_sha256']==digest
a=json.loads((P/'archs4-results.json').read_text(encoding='utf-8'))
assert a['gene_rows']==67186 and a['missing_GSMs_not_zeros']==['GSM9037837']
t=[x for x in a['selected_rows'] if x['gene']=='TMEM266'];assert len(t)==1
assert t[0]['counts']=={'GSM2113301':30,'GSM6883080':5}
for sample,v in t[0]['counts'].items():assert abs(t[0]['CPM_of_reported_counts'][sample]-1e6*v/a['column_sums'][sample])<1e-12
assert sha(P/'archs4-subset.zip')==a['source']['archive_sha256']
syntax=[];parsed=[];utf8=[];links=[]
for f in P.iterdir():
    if f.suffix in ['.md','.txt','.py','.json']:
        s=f.read_text(encoding='utf-8');utf8.append(f.name)
        if f.suffix=='.py':compile(s,str(f),'exec');syntax.append(f.name)
        if f.suffix=='.json':json.loads(s);parsed.append(f.name)
for name in ['DRAFT.md','SUPPLEMENT.md','COVERAGE.md']:
    for target in re.findall(r'\]\(([^)]+)\)',(P/name).read_text(encoding='utf-8')):
        if target.startswith(('http://','https://')):continue
        assert (P/target.split('#')[0]).exists(),target
        links.append(target)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed',
     'previous_packets':old,'prior_files_preserved':sum(x['verified_files'] for x in old.values()),
     'USZ22_worker_root_prefix_concordance':True,'ARCHS4_target_and_CPM_checks':True,
     'python_syntax':syntax,'JSON_parsed':parsed,'UTF8_text':utf8,'local_links_checked':len(links),
     'scope':'Scientific extraction receipts, source hashes and preservation; not a full publication gate'}
(P/'verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':out['status'],'prior_files_preserved':out['prior_files_preserved'],'local_links_checked':len(links)}))
