from pathlib import Path
from decimal import Decimal
from collections import Counter
import json, hashlib

ROOT = Path('C:/Projects/EMC-Research')
source = ROOT/'research/modalities/emc-expression-panels.json'
parent = json.loads(source.read_text(encoding='utf-8'), parse_float=Decimal)
genes = ['CD276','SSTR2','PRAME','FAP','CD248','CSPG4','MSLN','L1CAM','GPC3','ALPP','CDH17']
def avg(values):
    return sum(values, Decimal(0))/Decimal(len(values))
def sign(x):
    return (x>0)-(x<0)
results = {}
for gene in genes:
    results[gene] = {}
    for matrix, row in parent['gene_reads'][gene].items():
        if not row['readable']:
            results[gene][matrix] = {'readable':False}
            continue
        samples = row['per_sample']
        e = [s for s in samples if s['class']=='EMC' and s.get('z_vs_array') is not None]
        c = [s for s in samples if s['class']!='EMC' and s.get('z_vs_array') is not None]
        assert len({s['gsm'] for s in samples}) == len(samples)
        baseline = avg([s['z_vs_array'] for s in e])-avg([s['z_vs_array'] for s in c])
        e_deleted = {s['gsm']:avg([t['z_vs_array'] for t in e if t['gsm']!=s['gsm']])-avg([t['z_vs_array'] for t in c]) for s in e if len(e)>1}
        classes = Counter(s['class'] for s in c)
        c_deleted = {label:avg([s['z_vs_array'] for s in e])-avg([s['z_vs_array'] for s in c if s['class']!=label]) for label,n in classes.items() if n<len(c)}
        results[gene][matrix] = {'readable':True,'n_EMC':len(e),'n_comparator':len(c),'comparator_classes':dict(classes),'baseline':str(baseline),'parent_delta':str(row['welch_EMC_vs_comparator']['delta_a_minus_b']),'EMC_deletions':{k:str(v) for k,v in e_deleted.items()},'histology_deletions':{k:str(v) for k,v in c_deleted.items()},'EMC_flips':[k for k,v in e_deleted.items() if sign(v)!=sign(baseline)],'histology_flips':[k for k,v in c_deleted.items() if sign(v)!=sign(baseline)]}
output = ROOT/'.cache/research-cycle/independent_expected.json'
output.write_text(json.dumps({'parent_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'results':results},indent=2)+'\n',encoding='utf-8',newline='\n')
print('Independent Decimal arithmetic completed for',len(genes),'addresses')
for gene, matrices in results.items():
    print(gene,[(matrix, 'unreadable' if not r['readable'] else {'delta':round(float(r['baseline']),6),'EMC_flips':r['EMC_flips'],'histology_flips':r['histology_flips']}) for matrix,r in matrices.items()])
