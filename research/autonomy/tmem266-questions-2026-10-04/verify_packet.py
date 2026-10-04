"""Offline preservation, independent-replay concordance and artifact checks."""
import datetime,hashlib,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old={}
for folder,mname in [('discovery-2026-10-03','MANIFEST-CURRENT.json'),('tmem266-tissue-2026-10-03','MANIFEST.json'),('tmem266-prepublication-2026-10-03','MANIFEST.json')]:
    p=BASE.parent/folder;m=json.loads((p/mname).read_text())
    for n,r in m['files'].items():
        f=p/n;assert f.stat().st_size==r['bytes'] and sha(f)==r['sha256'],str(f)
    old[folder]={'verified_files':len(m['files']),'manifest_sha256':sha(p/mname)}
w=json.loads((BASE/'usz-prefix-worker.json').read_text());r=json.loads((BASE/'usz-prefix-replay.json').read_text())
assert r['total_complete_records']==w['total_complete_records']==565700
for a,b in zip(w['mates'],r['mates']):
    for k in ['mate','content_range','prefix_sha256','decompressed_bytes','complete_records','incomplete_tail_lines','incomplete_tail_bytes']:assert a[k]==b[k],k
hits=[h for mate in r['mates'] for h in mate['matches']]
assert len(hits)==2 and len({h['fragment_id'] for h in hits})==1
selected=json.loads((BASE/'usz-selected-reads.json').read_text())
for a,b in zip(selected['reads'],hits):
    assert a['sequence']==b['read_sequence'] and a['quality_ascii']*a['quality_repeat']==b['read_quality']
    assert a['header']==b['read_id'] and a['minimum_anchor_Phred']==b['minimum_anchor_Phred']==40
sv=json.loads((BASE/'splice-read-verification.json').read_text())
assert sv['status']=='passed' and sv['selected_reads_sha256']==sha(BASE/'usz-selected-reads.json')
quant=json.loads((BASE/'usz-worker-quant.json').read_text())
assert abs(sum(x['TPM'] for x in quant['selected_rows'])-quant['sum_TPM'])<1e-12
ep=json.loads((BASE/'exact-probe-counts.json').read_text())
positive=[x for x in ep['measurements'] if x['persisted_positive']]
assert len(positive)==6 and len([x for x in positive if not x['identity_conflict']])==5
assert all(x['count_lower_bound'] is None for x in ep['measurements'] if not x['persisted_positive'])
br=json.loads((BASE/'blast-probe_RNA.json').read_text())
assert br['sha256']=='413ba9ec67106a591804f5075957a76b349406dea36627c0ac1d5d871c8723a4'
assert len(br['rows'])==31 and sum(x['hit_limit_reached'] for x in br['rows'])==26
ids={'NM_152335','XM_005254160','XM_017021915','XM_047432151','XM_054377283','XM_054377284','XM_054377285'}
off=[(x['query'],h[1]) for x in br['rows'] for h in x['near_or_terminal_flank_candidates'] if h[1].split('.')[0] not in ids]
assert sorted(off)==[('195969','NR_120360.1'),('828175','NR_120360.1')]
ob=json.loads((BASE/'blast-observed_RNA.json').read_text())
assert ob['sha256']=='91c9b47cb5ca10bc7d54a33dafb9265f8b256c40614b5fc856f2a308950c669c'
assert len(ob['rows'])==3 and all(x['hit_limit_reached'] for x in ob['rows'])
syntax=[]
for p in BASE.glob('*.py'):
    compile(p.read_text(encoding='utf-8-sig'),str(p),'exec');syntax.append(p.name)
parsed=[]
for p in BASE.glob('*.json'):json.loads(p.read_text());parsed.append(p.name)
links=[]
for name in ['DRAFT.md','SUPPLEMENT.md']:
    for target in re.findall(r'\]\(([^)]+)\)',(BASE/name).read_text()):
        if re.match(r'https?://',target):continue
        assert (BASE/target.split('#')[0]).exists(),target
        links.append(target)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed',
     'earlier_packets_unchanged':old,'prefix_worker_root_concordant':True,
     'selected_read_reference_check':sv['status'],'detector_positive_libraries':6,
     'identity_qualified_detector_positive_libraries':5,'RNA_BLAST_known_non_TMEM_candidates':off,
     'python_syntax_checked':syntax,'JSON_parsed':parsed,'local_links_checked':len(links),
     'limits':'Integrity and selected arithmetic/replay checks; not a clinical, full-transcript or publication validation.'}
(BASE/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['python_syntax_checked','JSON_parsed']},indent=2))
