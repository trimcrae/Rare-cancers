"""Author-requested overlap-exclusion sensitivity. Fixed plan; exact decimal comparisons."""
from pathlib import Path
from decimal import Decimal
from statistics import median
import csv,json,hashlib
W=Path(__file__).resolve().parent
all_values=json.loads((W/'selected-values.json').read_text(),parse_float=Decimal)['CSPG4']
rows=list(csv.DictReader((W/'selected-panel-values.csv').open()))
EMC='Extraskeletal myxoid chondrosarcoma'
original=[r['sample_id'] for r in rows if r['original_diagnosis']==EMC]
added=['104-92','168-97','536-00']
assert len(original)==9 and not set(original)&set(added)
assert '5081-14' not in original+added
for r in rows:assert Decimal(r['CSPG4_TPM'])==all_values[r['sample_id']]
primary=[r for r in rows if r['broad_reference']=='True']
broader=[r for r in rows if r['source_class'] in {'Malignant','Intermediate'} and r['original_diagnosis'] not in {EMC,'Melanoma','Spindle cell tumor NOS'}]
assert len(primary)==393 and len(broader)==489
x=[all_values[s] for s in original+added]
def q(p):
 z=sorted(x);i=Decimal(len(z)-1)*p;lo=int(i);hi=min(lo+1,len(z)-1)
 return str(z[lo]+(z[hi]-z[lo])*(i-lo))
def score(y):
 wins=sum(a>b for a in x for b in y);ties=sum(a==b for a in x for b in y);n=len(x)*len(y)
 return {'emc_n':len(x),'reference_n':len(y),'pairs':n,'wins':wins,'ties':ties,'losses':n-wins-ties,'twice_credit':2*wins+ties,'twice_pairs':2*n,'A':float(Decimal(2*wins+ties)/Decimal(2*n))}
out={'plan_sha256':hashlib.sha256((W/'EXCLUSION-SENSITIVITY-PLAN.json').read_bytes()).hexdigest(),'added_primary_TPM':{s:str(all_values[s]) for s in added},'retained_nine_TPM':{s:str(all_values[s]) for s in original},'all12_median_TPM':str(median(x)),'all12_q1_TPM':q(Decimal('.25')),'all12_q3_TPM':q(Decimal('.75')),'all12_range_TPM':[str(min(x)),str(max(x))],'primary_reference':score([Decimal(r['CSPG4_TPM']) for r in primary]),'broader_reference':score([Decimal(r['CSPG4_TPM']) for r in broader]),'scope':'All12source-primaryEMCagainstunchangedreferences.Descriptiveexclusion sensitivity;original9caseanalysisunchanged.','input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [W/'selected-values.json',W/'selected-panel-values.csv']}}
(W/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
