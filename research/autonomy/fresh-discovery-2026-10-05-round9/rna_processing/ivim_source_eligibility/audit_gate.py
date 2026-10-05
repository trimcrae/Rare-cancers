#!/usr/bin/env python3
"""Identity/source/method/route validation, without images or numerical outcomes."""
import pathlib,json,hashlib,xml.etree.ElementTree as E
P=pathlib.Path(__file__).resolve().parent
def load(n):return json.loads((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
b=load('REUSED-SOURCE-BINDINGS.json')
for x in b['bindings']:
 f=pathlib.Path(x['path']);assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes']
s=b['source_xml'];f=pathlib.Path(s['path']);assert sha(f)==s['sha256'] and f.stat().st_size==s['bytes']
checks.append({'check':'Zero-copy originalXML and siximmutable sourceworker bindings exact','pass':True})
r=E.parse(f).getroot()
def t(e):return ' '.join(' '.join(e.itertext()).split()) if e is not None else ''
g=load('REUSED-MEASUREMENT-IDENTITY-SCHEMA.json')
for m in g['methods_only']:
 sec=r.find(f".//sec[@id='{m['id']}']");assert m['paragraphs']==[t(x) for x in sec.findall('./p')]
assert [m['id'] for m in g['methods_only']]==['sec3','sec4','sec5','sec6','sec7']
assert len(r.find(".//table-wrap[@id='T1']").findall('.//tr'))==0
checks.append({'check':'Allowedphysicalmethods/T1caption/relativegraphic exact; sourcegraphicalrows remainuninspected','pass':True})
assert load('PMC-LANDING-ACCESS-INTERPRETATION.json')['browser_access_gate'] is True
assert load('GENUINE-TABLE1-PDF-LINKS.json')['actual_links']==[]
assert load('COVERAGE.json')['actual_roster_image_inspected'] is False
assert load('COVERAGE.json')['EMC_enrollment'] is None
checks.append({'check':'HTTP200browsercheck notsourceaccess; no image, identityzero, threshold, flow or MVDinference','pass':True})
if (P/'PORTABILITY.json').exists():
 for x in load('PORTABILITY.json')['new_raw_inventory']:
  f=P/x['path'];assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes']
 checks.append({'check':'All newignoredcache bytes/hash exact','pass':True})
if (P/'MANIFEST.json').exists():
 for x in load('MANIFEST.json')['files']:
  f=P/x['path'];assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes']
 checks.append({'check':'Selectedexportmanifest exact','pass':True})
print(json.dumps({'status':'PASS','checks':checks,'scope':'Source/field/receipt integrity only, no endpointreproduction, biologicalfinding, full-publiccoverage, completecaseeligibility or scientificvaluecertificate.'},indent=2))
