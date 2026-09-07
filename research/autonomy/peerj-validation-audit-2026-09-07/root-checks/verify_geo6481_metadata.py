"""Independent check of the complete official SOFT roster; no expression analysis."""
import argparse, collections, gzip, hashlib, json
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--source',type=Path,required=True)
p.add_argument('--worker',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
digest=hashlib.sha256(a.source.read_bytes()).hexdigest()
assert digest=='eec1f676f7b05f3115d2b04c926e6085a429350ec6b84a1d637ff27ae8375887'
samples=[]; declared=[]; sample=None
with gzip.open(a.source,'rt',encoding='utf-8') as f:
    for line in f:
        if line.startswith('!Series_sample_id = '): declared.append(line.strip().split(' = ',1)[1])
        if line.startswith('^SAMPLE = '):
            sample={'id':line.strip().split(' = ',1)[1],'histology':[],'platform':[]};samples.append(sample)
        elif sample is not None and line.startswith('!Sample_characteristics_ch1 = Histology:'):
            sample['histology'].append(line.strip().split('Histology:',1)[1])
        elif sample is not None and line.startswith('!Sample_platform_id = '):
            sample['platform'].append(line.strip().split(' = ',1)[1])
assert len(samples)==len(declared)==len(set(declared))==105
assert {r['id'] for r in samples}==set(declared)
assert all(len(r['histology'])==1 and r['platform']==['GPL96'] for r in samples)
counts=dict(collections.Counter(r['histology'][0] for r in samples))
assert sum(counts.values())==105
assert not any('chondrosarcoma' in h.lower() for h in counts)
worker=json.loads(a.worker.read_text(encoding='utf-8'))
assert worker['source_sha256']==digest and worker['source_records']['SAMPLE']==105
report={'source_sha256':digest,'complete_unique_samples':105,'series_roster_agrees':True,'platform':'GPL96','histology_counts':counts,'emc_histology_labels':0,'figure_B_printed_total':147,'figure_B_printed_group_counts':[19,59],'figure_B_group_sum':78,'article_B_comparator_count':128,'scope':'Source metadata and printed figure counts only; no proof of the actual data selection underlying Figure S6B. Accession or group-label reporting error remains possible.','errors':[]}
a.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(report,indent=2))
