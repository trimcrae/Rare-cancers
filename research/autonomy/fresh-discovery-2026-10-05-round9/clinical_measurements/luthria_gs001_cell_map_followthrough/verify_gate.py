import pathlib,json,hashlib,re,shutil
B=pathlib.Path(__file__).resolve().parent
checks=[]
def c(n,o):checks.append({'check':n,'pass':bool(o)})
def j(n):return json.loads((B/n).read_text())
p=j('PLAN-FROZEN.json');a=j('ACCESS.json');safe=j('SAFE-SOURCE-METADATA-OBSERVATIONS.json')
c('two prospective source branches',len(p['branches'])==2);c('exacttwo requests',len(a)==2);c('source-only no matrix calls',all('raw.githubusercontent.com/IzarLab/sarcoma-sn/' in x['url'] for x in a))
for x in a:
 b=pathlib.Path(x['cache_path']).read_bytes();c('raw hash '+x['repository_path'],len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']);c('frozenblob '+x['repository_path'],hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['git_blob_sha1']);c('HTTP200 '+x['repository_path'],x['status']==200 and not x.get('error'))
for x in j('REUSED-SOURCE-BINDINGS.json')['sources']:
 q=pathlib.Path(x['path']);c('reusedbinding '+q.name,q.stat().st_size==x['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256'])
block=re.compile(r'numbat|cnv|cna|copy.?num|chromos|FAP|HLA|glycan|gene|protein|expression|malignant|tumou?r|cluster|cell.?type|cell.?class|annotation|clone|assign',re.I)
for x in safe:
 c('outputs never inspected '+x['source'],x['notebook_outputs_inspected'] is False);c('permitted final lines '+x['source'],all(not block.search(y['text']) for y in x['safe_source_lines']));c('restrictednames omitted '+x['source'],all(not block.search(y) for y in x['metadata_field_names_schema_only']))
r=j('REUSED-SOURCE-BINDINGS.json')['all21_source_library_rows'];c('all21 original conditions retained',len(r)==21);c('21 unique library IDs',len({x['accession'] for x in r})==21)
x=j('CONDITION-AND-OBJECT-LINKAGE.json');c('GS001GS002 andfrozen conditionsretained',[z['condition'] for z in x['conditions']]==['GS001','GS002','Eight frozen native specimens']);c('eightfrozen aliases',len(x['conditions'][2]['code_aliases'])==8)
loc='data/sarcoma_all/data_sarcoma_all_merged_obj.rds';texts=['\n'.join(v['text'] for v in s['safe_source_lines']) for s in safe];c('same literal localproducer/consumerpath',all(loc in t for t in texts));c('new safe files no GS001identity',all('gs001' not in t.lower() for t in texts))
f=j('PORTABILITY-AND-READ-SCOPE.json');c('newraw10690',f['new_original_bytes']==10690);c('under8MiB',f['new_original_bytes']<=8388608);c('freefloor',shutil.disk_usage(B).free>=10737418240);c('no outcomes',f['new_gene_or_cell_outcome_values']==0 and f['notebook_outputs_read']==0)
c('promotionfalse',j('DECISION.json')['promotion'] is False);c('noexhaustion',j('DECISION.json')['no_exhaustion'] is True)
(B/'VERIFICATION.json').write_text(json.dumps({'all_pass':all(x['pass'] for x in checks),'checks':checks,'network_in_verifier':0,'note':'Whitelisted source metadata only; no value tests or inference from path naming.'},indent=2)+'\n')
assert all(x['pass'] for x in checks)
print(str(len(checks))+' checks PASS; verifier no network')
