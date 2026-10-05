#!/usr/bin/env python3
"""Local source/hash and pre-value coverage checks. Never emits assay outcomes."""
import hashlib,json,pathlib,xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parent

def load(n): return json.loads((P/n).read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(e): return ' '.join(' '.join(e.itertext()).split())
checks=[]
port=load('PORTABILITY.json')
for b in port['raw_inventory']:
 f=P/b['path'];assert f.stat().st_size==b['bytes'];assert digest(f)==b['sha256']
checks.append({'check':'All original/local-cache inventory sizes and SHA256','n':len(port['raw_inventory']),'pass':True,'scope':'Local cached bytes, not fresh-checkout recovery or science-validity guarantee'})
r=ET.parse(P/'raw/PMC5846059.xml').getroot();table=r.find(".//table-wrap[@id='tbl1']");rows=[];active=False
for tr in table.findall('.//tbody/tr'):
 cells=[txt(x) for x in tr]
 if cells and cells[0]=='Histologic subtype':active=True;continue
 if active:
  if len(cells)>=2 and cells[1].isdigit():rows.append({'histologic_label':cells[0],'n':int(cells[1]),'printed_percent':cells[2] if len(cells)>2 else None})
  else:break
record=load('VORTEX-COMPLETE-HISTOLOGY-ROSTER.json');assert rows==record['all_histotype_rows'];assert sum(x['n'] for x in rows)==203
checks.append({'check':'Whole203 VorteX baseline histotype roster, including printed EMC typo/Other13/Unknown1','pass':True})
emc=[x for x in rows if 'Extraskeletal myxoid' in x['histologic_label']];assert len(emc)==1 and emc[0]['n']==4
checks.append({'check':'Four nominal authorEMC baseline cases; no assessable-core/marker extrapolation','pass':True})
f=load('PMC13536671-IDENTITY-CONDITION-GATE.json');subjects=[x for x in f['source_roster_fields'] if 'subject' in x];assert len(subjects)==5;assert all(x['numerical_oxygenation_proxy_values'].startswith('MASKED') for x in subjects)
checks.append({'check':'All five FMISO subject identifiers retained, every case tracer/IHC endpoint masked','pass':True})
e=load('PMC5117798-OXYGEN-IDENTITY-GATE.json');assert len(e['histology_roster'])==9 and sum(x['n'] for x in e['histology_roster'])==132
checks.append({'check':'Complete methods132 electrode-linked gene-cohort roster expands Table1Others39, no oxygen-row inference','pass':True})
c=load('COVERAGE.json');assert c['mandatory_EMC_conditions'][1]['assay_denominators']['EMC_specific_per_marker'] is None
assert load('SOURCE-GATE-CLOSED.json')['numerical_stage_authorized'] is False
assert load('DECISION.json')['findings_surviving']==0
checks.append({'check':'Per-case EMC assessability/identity unknown, older measured-source rosters pending, no numeric stage or biological absence assertion','pass':True})
if (P/'MANIFEST.json').exists():
 m=load('MANIFEST.json')
 for b in m['files']:
  f=P/b['path'];assert f.stat().st_size==b['bytes'];assert digest(f)==b['sha256']
 checks.append({'check':'Committed selected export bindings','n':len(m['files']),'pass':True})
print(json.dumps({'status':'PASS','checks':checks,'limitations':'Source receipt/identity/condition validation only. Independent challenger owns scientific-value review; no case endpoints, public-coverage exhaustion, publication-worthiness or private-source recovery certified.'},indent=2))
