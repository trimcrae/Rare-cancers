import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
P=Path(__file__).resolve().parent
O=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/organoid_native_emc_source_gate')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):P.joinpath(n).write_text(json.dumps(x,indent=2)+'\n')
checks=[]
def check(label,ok):
 checks.append({'check':label,'pass':bool(ok)})
 assert ok,label
src=O/'raw-cache/PMC12686348.xml'
check('Gelatin original hash',sha(src)=='44f395ee6ba2733db5d1f4d1e27e508e5c232574748a2fd6ddc3d49c6f1eb9d2')
r=ET.fromstring(src.read_bytes())
def paras(sid):
 s=r.find('.//sec[@id="'+sid+'"]')
 return [' '.join(p.itertext()) for p in s.findall('p')]
def text(sid):return ' '.join(paras(sid))
roster=[]
for sid,pid,terms in [('sec4','1',['dedifferentiated liposarcoma']),('sec5','2',['DDLPS','well-differentiated','liposarcoma','WDLPS']),('sec6','3',['leiomyosarcoma'])]:
 s=r.find('.//sec[@id="'+sid+'"]')
 body=text(sid)
 check('Patient '+pid+' diagnostic whitelist matches',all(t.lower() in body.lower() for t in terms))
 roster.append({'source_id':sid,'patient_label':pid,'diagnostic_terms_only':terms,'confidence':'Author-labelled diagnosis, not independently molecularly reauthenticated','native_EMC':'No explicit EMC in this source-defined patient unit','donor_unit':'one patient; patient2 two masses not two donors' if pid=='2' else 'one patient'})
check('93T449 labelled liposarcoma',all(t in text('sec7') for t in ['liposarcoma','93T449','CVCL_U614','mycoplasma']))
check('2D precursor cultures',all(t in text('sec9') for t in ['2-dimensional','BME','20% gelatin']))
check('Fresh surgical specimen and pathologist confirmation',all(t in text('sec8') for t in ['freshly resected','pathologist confirmed','on ice']))
check('OCR DNA normalization and three formats',all(t in text('sec11') for t in ['2D','BME or gelatin','normalized to cellular DNA']))
check('OCR analyzer plate mismatch retained',all(t in text('sec11') for t in ['XFe24','96-well','XF24']))
check('ODT timing superficial selection surrogate',all(t in text('sec12') for t in ['day 0 to day 10','near the surface','presumed to be lipid']))
check('Data reasonable-request only in inspected statement','reasonable request' in text('sec24'))
raw=P/'raw-cache/RPDOX-EPMC-lite.json'
check('rPDOX metadata hash',sha(raw)=='74a329b90cd67e3bd57951600160f1c6697f0e38a2fd3545d4a5a567ddcc9534')
j=json.loads(raw.read_text());check('exact one rPDOX identity',j['hitCount']==1 and j['resultList']['result'][0]['pmid']=='42314236' and j['resultList']['result'][0]['doi']=='10.1016/j.biomaterials.2026.124382')
a=json.loads(P.joinpath('RPDOX-PUBLISHER-ACCESS.json').read_text());check('rPDOX request failed before accepted source',not a['accepted_scientific_methods_or_roster'] and 'Tunnel connection failed' in a['error'])
s=json.loads(O.joinpath('SUPPLEMENT-ACCESS.json').read_text());check('Gelatin supplement zero accepted bytes',s['bytes']==0 and not s['accepted'] and s['no_retry'])
write('INDEPENDENT-GELATIN-METHODS.json',{'source_path':str(src),'sha256':sha(src),'read_mask':'Direct Methods paragraphs only; after first-read correction exclude all descendant figures/captions, all Results/Discussion and RNA/Western/IHC outcomes. Patient paragraphs used only to assert diagnostic strings, not exported.','patient_units':roster,'separate_line':{'name':'93T449','RRID':'CVCL_U614','entity':'source-labelled liposarcoma','mycoplasma':'source says screened; assay result not inspected','unit':'not another native donor or EMC'},'assay_context':{'preparation':'fresh surgical tissue, pathologist confirmation within 1h, ice transport, primary 2D culture followed by BME/20% gelatin embedding','OCR':'three culture formats; DNA-normalized stress-test OCR; XFe24/XF24 with 96-well wording inconsistency; technical wells not donors; no OCR values inspected','ODT':'day0–10 superficial identifiable cells; RI/volume presumed lipid structures; not direct lipid chemistry, donor response or EMC phenotype','public_processed_data':'reasonable-request statement; no authenticated public numerical matrix; named TableS1 remains uninspected after one timeout'}})
write('VERIFICATION.json',{'network_calls':0,'scope':'Read-only retained-source verification; no result arrays parsed','assertions':checks,'count':len(checks),'all_pass':all(c['pass'] for c in checks)})
print(json.dumps({'checks':len(checks),'all_pass':True}))
