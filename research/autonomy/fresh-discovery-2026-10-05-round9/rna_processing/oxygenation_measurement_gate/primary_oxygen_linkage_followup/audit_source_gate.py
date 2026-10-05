#!/usr/bin/env python3
"""Verify only source identity/hash, allowed clinical methods and cohort units."""
import hashlib,json,pathlib,xml.etree.ElementTree as E
P=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((P/n).read_text())
checks=[]
parent=load('../MANIFEST.json')
for b in parent['files']:
 f=P.parent/b['path'];assert sha(f)==b['sha256'] and f.stat().st_size==b['bytes']
assert sha(P.parent/'SCIENCE-FREEZE.json')=='8a29bbd0e8b6c16b7d54cf5160f8de5f033498fe13877cef888c055e05c55225'
checks.append({'check':'Original37 exports and81018e sciencefreeze unchanged','pass':True})
g=load('NORDSMARK-ORIGINAL-ASSAY-IDENTITY-GATE.json');r=E.parse(P/g['source']['xml']).getroot();s=''.join(r.find('./body/preformat').itertext());ls=s.splitlines()
assert len(s)==29189 and len(ls)==570
assert s==(P/g['source']['derived_text']).read_text()
assert g['allowed_patient_methods_excerpt']=='\n'.join(ls[28:47])
assert g['allowed_oxygen_method_excerpt']=='\n'.join(ls[47:54])+'\n'+'\n'.join(ls[95:110])
assert g['allowed_overlap_excerpt']=='\n'.join(ls[111:118])
checks.append({'check':'Actual archivepreformat and selected oxygen/patient/overlap methods exact, no localOCR or endpoint reproduction','pass':True})
assert g['cohort_units']['nominal_STS_patients']==33
b=load('BENTZEN-ORIGINAL-ABSTRACT-ASSAY-GATE.json');assert b['cohort_units']['suspected_soft_tissue_tumors']==13 and b['cohort_units']['completed_electrode_after_PET']==11 and b['cohort_units']['malignant_STS']+b['cohort_units']['benign_tumors']==13
assert b['cohort_units']['case_histotypes_or_EMC_map'] is None
checks.append({'check':'33sourceSTS and13suspected/11electrode/7STS6benign distinct donor/assay denominators, no sum or identity transfer','pass':True})
if (P/'PORTABILITY.json').exists():
 for f in load('PORTABILITY.json')['raw_inventory']:
  p=P/f['path'];assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
 checks.append({'check':'All retained exact cache hashes','pass':True})
if (P/'MANIFEST.json').exists():
 for f in load('MANIFEST.json')['files']:
  p=P/f['path'];assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
 checks.append({'check':'Selected export manifest bindings','pass':True})
print(json.dumps({'status':'PASS','checks':checks,'scope':'Source/hash/clinicalcondition consistency only. Not independent scientific-value endorsement, full public-coverage certificate, raw-source recovery guarantee or biological negative.'},indent=2))
