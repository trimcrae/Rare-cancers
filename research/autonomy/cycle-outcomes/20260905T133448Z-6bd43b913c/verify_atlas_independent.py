import json,hashlib,re,gzip,csv
from collections import Counter
from pathlib import Path
w=Path('C:/Projects/EMC-Research/.cache/research-runs/20260905T133448Z-6bd43b913c/worktree')
report=json.loads((w/'research/modalities/atlas-independent-normal-feasibility.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
for v in report['sources'].values():
 b=(w/v['file']).read_bytes();assert sha(b)==v['file_sha256']
 x=json.loads(b) if v['file'].endswith('.json') else b.decode()
 if v['pointer']:
  for token in v['pointer'][1:].split('/'):
   token=token.replace('~1','/').replace('~0','~');x=x[int(token)] if isinstance(x,list) else x[token]
 assert sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())==v['value_sha256']
print('Verified all',len(report['sources']),'source pointer/file/value hashes independently.')
b=Path('.cache/GSE28866_normalized_peaks.txt.gz').read_bytes();rows=csv.reader(gzip.decompress(b).decode().splitlines(),delimiter='\t');h=next(rows)
emc=[x for x in h if x.startswith('EMC_')];normal=[x for x in h if '_normal_' in x]
adult=[x for x in normal if '_Adult_' in x];fetal=[x for x in normal if '_Fetal_' in x]
counts=report['cohorts']['GSE28866']['counts']['value'];assert len(emc)==counts['EMC_libraries']==4;assert len(normal)==counts['normal_libraries']==27;assert len(adult)==17 and len(fetal)==10
assert {x['column'] for x in report['cohorts']['GSE28866']['roster_EMC_and_normal']}==set(emc+normal)
assert sum(1 for _ in rows)==36048
assert Counter(x.rsplit('_',1)[1] for x in adult)==Counter({'breast':5,'colon':3,'kidney':3,'lung':5,'uterus':1})
print('Independent primary matrix confirms 4 EMC,17 adult,10 fetal columns; five adult organ types;36048 rows.')
a=json.loads((w/'research/modalities/emc-expression-panels-inputs.json').read_text())['targets']
for k,v in a.items():
 out=report['cohorts'][v['gse']];assert {x['gsm'] for x in v['samples']}=={x['gsm'] for x in out['roster']};assert len(v['samples'])==out['cached_records']['value'];assert out['unique_patients']['value'] is None
f=json.loads((w/'research/modalities/emc-fourth-cohort-quant-inputs.json').read_text())['run_table']['rows'];assert len(f)==12
assert [(x['run_accession'],x['library_name'],x['sample_alias']) for x in f if x['library_name']!=x['sample_alias']]==[('SRR35940654','Si21','Si22')]
print('Array rosters, unresolved patient counts and fourth-cohort alias discrepancy verified.')
s=json.loads((w/'research/modalities/surface-address-sensitivity.json').read_text())['platforms'];p=list(s.values());common=set(p[0]['addresses'])&set(p[1]['addresses']);both=[x for x in sorted(common) if all(q['addresses'][x]['readable'] and q['addresses'][x]['status']=='stable_positive' for q in p)]
assert len(common)==11 and not both
print('Existing finite deletion-sensitivity result: 0 of11 named addresses stable_positive on both cached array platforms. This is comparator-dependent and does not refute biological targetability.')
print('PASS independent verification; no expression-effect estimates or clinical claims.')
