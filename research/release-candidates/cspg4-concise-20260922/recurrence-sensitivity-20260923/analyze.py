"""Author-approved all13 EMC exclusion sensitivity; fixed references, exact decimal pairs."""
from pathlib import Path
from decimal import Decimal
from statistics import median
import csv,json,hashlib
W=Path(__file__).resolve().parent
all_values=json.loads((W/'selected-values.json').read_text(),parse_float=Decimal)['CSPG4']
rows=list(csv.DictReader((W/'selected-panel-values.csv').open()))
EMC='Extraskeletal myxoid chondrosarcoma'
original=[r['sample_id'] for r in rows if r['original_diagnosis']==EMC]
primary_added=['104-92','168-97','536-00'];recurrence='5081-14'
assert len(original)==9 and len(set(original+primary_added+[recurrence]))==13
for r in rows:assert Decimal(r['CSPG4_TPM'])==all_values[r['sample_id']]
refs={'primary393':[r for r in rows if r['broad_reference']=='True'],'broader489':[r for r in rows if r['source_class'] in {'Malignant','Intermediate'} and r['original_diagnosis'] not in {EMC,'Melanoma','Spindle cell tumor NOS'}]}
assert len(refs['primary393'])==393 and len(refs['broader489'])==489
ids=original+primary_added+[recurrence];x=[all_values[s] for s in ids]
def q(p):
 z=sorted(x);i=Decimal(len(z)-1)*p;lo=int(i);hi=min(lo+1,len(z)-1)
 return str(z[lo]+(z[hi]-z[lo])*(i-lo))
def score(y):
 wins=sum(a>b for a in x for b in y);ties=sum(a==b for a in x for b in y);pairs=len(x)*len(y)
 return {'emc_n':len(x),'reference_n':len(y),'pairs':pairs,'wins':wins,'ties':ties,'losses':pairs-wins-ties,'twice_credit':2*wins+ties,'twice_pairs':2*pairs,'A':float(Decimal(2*wins+ties)/Decimal(2*pairs))}
out={'plan_sha256':hashlib.sha256((W/'ANALYSIS-PLAN.json').read_bytes()).hexdigest(),'recurrence_id':recurrence,'recurrence_CSPG4_TPM':str(all_values[recurrence]),'all13_specimen_TPM':{s:str(all_values[s]) for s in ids},'median_TPM':str(median(x)),'q1_TPM':q(Decimal('.25')),'q3_TPM':q(Decimal('.75')),'range_TPM':[str(min(x)),str(max(x))],'comparisons':{k:score([Decimal(r['CSPG4_TPM']) for r in v]) for k,v in refs.items()},'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [W/'selected-values.json',W/'selected-panel-values.csv']},'scope':'All13sourceEMCincludingone localrecurrence,comparedwithunchangedprimary-lesionreferences. Descriptiveexclusion sensitivity,notanestimateofrecurrencebiology.'}
(W/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
