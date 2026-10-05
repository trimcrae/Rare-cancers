"""Validate source-only metadata without reading gene summary values or abstracts."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
port=json.loads((P/'PORTABILITY.json').read_text())
for x in port['new_originals']:
 p=Path(x['path']);checks.append({'check':p.name+' source binding','pass':p.stat().st_size==x['bytes'] and sha(p)==x['sha256']})
r=json.loads((P/'EVALUATED-CLINICAL-TARGET-RATIONALE.json').read_text())['records']
checks.append({'check':'original seven-family source cards','pass':[x['gene'] for x in r]==['ERBB2','TACSTD2','NECTIN4','FOLR1','CD276','GPNMB','LRRC15']})
for x in r:
 if 'source_sha256' in x:
  p=Path(x.get('source_cache',x.get('source'))); checks.append({'check':x['gene']+' exact source','pass':sha(p)==x['source_sha256']})
  if 'drug_bindings' in x:checks.append({'check':x['gene']+' real FDA binding','pass':len(x['drug_bindings'])>0})
prior=json.loads((P/'PRIOR-DESIGN-AND-EXPOSURE-REUSE.json').read_text())
checks.append({'check':'prior immutable TSV hash','pass':sha(Path(prior['exact_source']))==prior['sha256']})
checks.append({'check':'two allocation-only old records','pass':prior['two_prior_flags_only']==[{'gene':'GPNMB','allocated':'False'},{'gene':'LRRC15','allocated':'False'}] or sorted(prior['two_prior_flags_only'],key=lambda x:x['gene'])==[{'gene':'GPNMB','allocated':'False'},{'gene':'LRRC15','allocated':'False'}]})
checks.append({'check':'new retained originals cap','pass':port['new_raw_total_bytes']<=port['cap_bytes']})
checks.append({'check':'source decision HOLD','pass':json.loads((P/'SOURCE-STATUS-AND-DECISION.json').read_text())['decision'].startswith('HOLD')})
result={'scope':'Source-only whitelist/citation/hash checks; no gene numerical rows, abstract endpoints or native outcome values','checks':checks,'all_pass':all(c['pass'] for c in checks)}
(P/'SOURCE-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'all_pass':result['all_pass']}))
assert result['all_pass']
