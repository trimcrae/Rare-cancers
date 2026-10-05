"""Read-only source/identity/method replay. No physiological outcomes parsed."""
from pathlib import Path
import json, hashlib, xml.etree.ElementTree as ET, re, shutil, datetime
HERE=Path(__file__).resolve().parent
OWNER=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/microvascular_measurement_gate')
CHECKS=[]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,condition,detail=None):
 CHECKS.append({'check':name,'pass':bool(condition),'detail':detail})
 if not condition: raise AssertionError(name)
def text(e): return ' '.join(''.join(e.itertext()).split())
def section(root,title):
 return [text(p) for s in root.findall('.//sec') if s.findtext('title','')==title for p in s.findall('p')]
def rows(root,tid):
 t=root.find('.//table-wrap[@id="'+tid+'"]'); return [{'cells':[text(td) for td in r.findall('td')]} for r in t.findall('.//tr') if r.findall('td')]
m= json.loads((OWNER/'MANIFEST.json').read_text())
check('owner original manifest exact',sha(OWNER/'MANIFEST.json')=='271fb11f507538d3a172f097a555973375bcd09c53c21884602b81e7308caef9')
for a in m['exports']:check('owner original export '+a['file'],sha(OWNER/a['file'])==a['sha256'] and (OWNER/a['file']).stat().st_size==a['bytes'])
am=json.loads((OWNER/'ADDITIVE-FREEZE-01.json').read_text())
check('owner PDF followup exact freeze',sha(OWNER/'ADDITIVE-FREEZE-01.json')=='d732fc3206f0e39ebbf24a48eebb1997b7ec861622c7966a23df12b03fa79842')
for a in am['bindings']:check('owner additive '+a['file'],sha(OWNER/a['file'])==a['sha256'] and (OWNER/a['file']).stat().st_size==a['bytes'])
port=json.loads((OWNER/'PORTABILITY.json').read_text())
for a in port['local_raw']+port['shared_raw']:
 p=Path(a['path']) if Path(a['path']).is_absolute() else OWNER/a['path'];check('borrowed raw '+p.name,sha(p)==a['sha256'] and p.stat().st_size==a['bytes'])
r92=ET.parse(OWNER/'raw-cache/PMC11107050.xml').getroot()
r165=ET.parse(Path('/workspace/emc-r6-radiotherapy/research/autonomy/fresh-discovery-2026-10-05-round9/endocrine/diffusion_mri_gate/raw-cache/PMC11717864.xml')).getroot()
rosters=json.loads((OWNER/'COMPLETE-HISTOLOGY-ROSTERS.json').read_text())
check('complete92 source histology replay',rows(r92,'Tab1')==rosters[1]['full_histology_rows'])
check('complete165 source histology replay',rows(r165,'T2')==rosters[0]['full_histology_rows'])
t92=text(r92.find('.//table-wrap[@id="Tab1"]'))
t165=text(r165.find('.//table-wrap[@id="T2"]'))
check('two EMC explicit165 pathology labels','Extraskeletal myxoid chondrosarcoma (n = 2)' in t165)
check('no explicit92 EMC label and generic14 retained','Extraskeletal myxoid chondrosarcoma' not in t92 and 'Fibrosarcoma (n = 14)' in t92)
check('92 group census31+61',sum([1,1,1,2,1,17,2,5,1])==31 and sum([6,2,14,9,2,1,4,5,1,1,12,4])==61)
check('165 group census54+111 excludes parent-subtype doublecount',sum([18,7,4,7,5,3,2,2,1,1,1,1,1,1])==54 and sum([32,22,15,15,10,4,2,2,2,1,1,1,1,1,1,1])==111)
p92=' '.join(section(r92,'Patients'));p165=' '.join(section(r165,'Study Patients'))
check('92 explicit no chemoRT before surgery','no chemotherapy or radiotherapy before surgery' in p92)
check('165 singleinitial source unit and prior same-site surgery','initial single STT' in p165 and 'prior surgery at the same site' in p165)
check('165 no explicit chemoRT eligibility exclusion',not re.search('chemotherap|radiotherap',p165,re.I),'Unresolved; no absence of prior therapy inferred')
a92=' '.join(section(r92,'MRI acquisition'));a165=' '.join(section(r165,'MRI Protocols'))
check('92 bolus dose timing','0.1mmol/kg' in a92 and '2mL/s' in a92 and '8 s' in a92)
check('165 bolus dose timing','0.1 mmol/kg' in a165 and '1.3 mL/s' in a165)
m92=' '.join(section(r92,'DCE-MR image analysis'));m165=' '.join(section(r165,'Analysis of Delayed Arterial Phase'))
check('four-slice mean vs selectedmaxima confound','four typical slices' in m92 and 'average value' in m92 and 'maximum DCE parameter values' in m165)
check('both request-only individualdata','reasonable request' in ' '.join(section(r92,'Data availability')) and 'reasonable request' in ' '.join(section(r165,'Availability of Data and Material')))
check('92 publicDOCX remains uninspected',len(r92.findall('.//supplementary-material'))==2,'Duplicate JATS descriptions, not two independent supplements')
check('165 no supplementary-material nodes in retrievedXML',not r165.findall('.//supplementary-material'),'XML node scope only; not all possible publication routes')
raw=HERE/'source-cache/PMC10646632-BioC.xml'
check('alternate HTTP200 invalid errorbody correctly rejected',sha(raw)=='3acc5f4c51ec704cd708d3379196db9f66442a96c9bf275773710e0de0196b52' and raw.read_bytes().startswith(b'[Error] : No result can be found.'))
check('freefloor',shutil.disk_usage(HERE).free>=10737418240)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS bounded source/method/coverage review','checks':CHECKS,'checks_count':len(CHECKS),'outcome_values_parsed':0,'images_inspected':0,'source_semantics':'Only histology/census/method/protocol/schema fields parsed. Method units/dose/timing are not physiological outcomes. Metadata/error bodies are not primary measurements.','repo_preflight':'Pending integrating lead; sparse worker did not claim full-repository gates passed.'}
(HERE/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(CHECKS),'failed':0,'free_bytes':shutil.disk_usage(HERE).free}))
