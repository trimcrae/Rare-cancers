"""Official public subset retrieval; disputed identity remains explicit."""
import urllib.request,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
API='https://depmap.org/portal/breadbox/'
receipts=[]
def fetch(path,body=None):
    u=API+path
    req=urllib.request.Request(u,data=None if body is None else json.dumps(body).encode(),headers={'User-Agent':'EMC-public-data-review/1.0','Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(15000001)
    assert len(b)<=15000000
    receipts.append({'url':u,'read_only_query_body':body,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    return json.loads(b)
catalog=fetch('datasets/?feature_type=gene&sample_type=depmap_model')
uid='20528fee-bd1d-4f3f-b7a2-f991fc875858'
d=next(x for x in catalog if x['id']==uid)
assert d['units']=='log2(TPM+1)' and d['name']=='Expression (Short-read) Public 26Q1'
genes=['TMEM266','NR4A3','CHRNA6','ACTB','GAPDH']
x=fetch('datasets/matrix/'+uid,{'features':genes,'feature_identifier':'label'})
m=fetch('datasets/tabular/depmap_model_metadata',{'columns':['CellLineName','OncotreePrimaryDisease','OncotreeSubtype','CellLineDisplayName']})
k='ACH-001519';assert m['CellLineName'][k]=='H-EMC-SS'
vals={g:x[g][k] for g in genes}
out={'scope':'Disputed EMC-labelled culture; no authenticated EMC biological inference',
     'dataset':d,'model_id':k,'model_metadata':{a:b.get(k) for a,b in m.items()},
     'log2_TPM_plus_1':vals,'TMEM266_inverse_TPM':2**vals['TMEM266']-1,
     'inverse_units_note':'Algebraic inversion of source log2(TPM+1), not an independently quantified TPM estimate',
     'receipts':receipts}
(BASE/'disputed-model-expression.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'dataset':d['name'],'values':vals,'TMEM266_inverse_TPM':out['TMEM266_inverse_TPM']},indent=2))
