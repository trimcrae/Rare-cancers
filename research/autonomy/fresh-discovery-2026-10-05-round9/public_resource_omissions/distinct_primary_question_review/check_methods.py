"""Check primary method/schema eligibility only; do not read assay outcomes."""
from pathlib import Path
import json,hashlib,re,sys,datetime
from lxml import etree
P=Path(__file__).resolve().parent
plan=json.loads((P/'PLAN-FROZEN.json').read_text())
for b in plan['input_bindings']:
 f=Path(b['path']);assert f.stat().st_size==b['bytes'];assert hashlib.sha256(f.read_bytes()).hexdigest()==b['sha256']
r=etree.parse(plan['input_bindings'][1]['path'])
sec=next(sec for sec in r.findall('.//sec') if '2.4. Pathological Analysis'==' '.join(sec.xpath('./title//text()')))
method=' '.join(sec.itertext())
assert 'some specimens' in method and 'Cytoplasmic brown precipitate' in method
assert '24 hours' in method and '10%' in method
headers=[];ids=[]
for table in r.findall('.//table-wrap'):
 headers.append({'id':table.get('id'),'headers':[' '.join(tr.itertext()) for tr in table.findall('.//thead//tr')]})
 for tr in table.findall('.//tbody/tr'):
  c=tr.findall('./td')
  if c:ids.append(' '.join(c[0].itertext()))
assert len(headers)==1 and ids==list(map(str,range(1,14)))
# Presence check only. No text fields, assay values or imaging outcomes projected.
full=' '.join(r.getroot().itertext())
patterns={'Ki67':r'Ki[\s-]*67','MIB1':r'MIB[\s-]*1','mitotic':r'mitotic','mitoses':r'mitoses'}
occurrences={n:len(re.findall(p,full,re.I)) for n,p in patterns.items()}
assert all(v==0 for v in occurrences.values())
assert not any(re.search(p,' '.join(h['headers']),re.I) for p in patterns.values() for h in headers)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':plan['input_bindings'][1]['sha256'],'method_scope':'Only2.4 pathological method, sole table header and caseID column; normalized literal presence tests, no biological absence inference','method_quote':method,'table_schema':headers,'all_case_ids_only':ids,'normalized_target_term_occurrences':occurrences,'source_prerequisite':'No named direct proliferation assay, counted tumour-cell/ROI denominator, mitotic-count/area method or paired numerical field established in recovered source. Generic IHC is not Ki67 fraction.','outcome_values_inspected':0,'passed':True}
if '--write' in sys.argv:(P/'METHOD-SCHEMA-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'caseIDs':13,'tables':1,'outcomes_inspected':0}))
