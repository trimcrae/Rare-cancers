"""Dated September21 amendment; specimen bootstrap, no new hypothesis tests."""
from pathlib import Path
import csv,hashlib,json
from datetime import datetime,timezone
import numpy as np
W=Path(__file__).resolve().parent
I=W/'inputs'/'selected-panel-values.csv'
rows=list(csv.DictReader(I.open(encoding='utf8')))
EMC='Extraskeletal myxoid chondrosarcoma'
excluded={EMC,'Melanoma','Spindle cell tumor NOS'}
x=np.array([float(r['CSPG4_TPM']) for r in rows if r['original_diagnosis']==EMC])
assert len(x)==9
out={}
for name,selected,expected,types in [
 ('primary',[r for r in rows if r['broad_reference']=='True'],393,28),
 ('inclusive',[r for r in rows if r['source_class'] in {'Malignant','Intermediate'} and r['original_diagnosis'] not in excluded],489,37)]:
 y=np.array([float(r['CSPG4_TPM']) for r in selected]);labels=np.array([r['original_diagnosis'] for r in selected])
 assert len(y)==expected and len(set(labels))==types
 pair=(x[:,None]>y).astype(float)+.5*(x[:,None]==y)
 rng=np.random.default_rng(20260921);replicates=[]
 # Two independent specimen resamples represented by their multinomial multiplicities.
 for i in range(50):
  wx=rng.multinomial(len(x),np.full(len(x),1/len(x)),size=1000)
  wy=rng.multinomial(len(y),np.full(len(y),1/len(y)),size=1000)
  replicates.extend(np.einsum('bi,ij,bj->b',wx,pair,wy,optimize=True)/(len(x)*len(y)))
 limits=np.quantile(replicates,[.025,.975],method='linear')
 out[name]={'n_emc':len(x),'n_reference':len(y),'reference_labels':types,'reference_median_TPM':float(np.median(y)),'A':float(pair.mean()),'equal_type_A':float(np.mean([pair[:,labels==l].mean() for l in sorted(set(labels))])),'bootstrap_95_percentile':[float(v) for v in limits],'bootstrap_replicates':50000,'seed':20260921,'numpy_version':np.__version__,'label_counts':{l:int(sum(labels==l)) for l in sorted(set(labels))}}
(W/'AMENDED-RESULTS.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'amendment_sha256':hashlib.sha256((W/'ANALYSIS-AMENDMENT.json').read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(I.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'results':out},indent=2)+'\n')
print(json.dumps({k:{a:b for a,b in v.items() if a!='label_counts'} for k,v in out.items()}))
