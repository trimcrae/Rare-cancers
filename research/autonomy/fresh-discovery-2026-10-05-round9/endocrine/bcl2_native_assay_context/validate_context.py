"""Verify BCL2 reagent/clinical material context; do not read outcome matrices."""
import pathlib,json,hashlib,xml.etree.ElementTree as E,re,os
P=pathlib.Path(__file__).resolve().parent
errors=[]
h=json.loads((P/'SOURCE-HASHES.json').read_text())
for section in ['existing_reused_records','new_originals','query_originals']:
 for x in h[section]:
  p=pathlib.Path(x['path'])
  if not p.exists() or p.stat().st_size!=x['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:errors.append('input byte binding:'+x['path'])
x=h['historical_source_recovery'];p=pathlib.Path(x['path'])
if hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:errors.append('historical source binding')
r=E.parse(P/'raw-cache/PMC2774148.xml').getroot()
found=[];coh=[]
for t in r.findall('.//table-wrap'):
 if t.get('id')=='tbl1':
  for row in t.findall('.//tbody/tr'):
   vals=[''.join(x.itertext()).strip() for x in row.findall('./td')+row.findall('./th')]
   if vals and re.search(r'bcl[- ]?2',vals[0],re.I):found.append(vals)
 elif t.get('id')=='tbl2':
  for row in t.findall('.//tbody/tr'):
   # ONLY histologic label/material count. Fresh stain-result columns remain closed.
   cells=row.findall('./td')+row.findall('./th')
   if cells:coh.append([''.join(x.itertext()).strip() for x in cells[:2]])
if found!=[['BCL2 oncoprotein','124','Dako','1:50','Lymph node']]:errors.append('BCL2 reagent/control row')
if coh[:2]!=[['Extraskeletal myxoid chondrosarcoma','2 conventional'],['','1 anaplastic']]:errors.append('all3 native material groups')
methods=' '.join(''.join(x.itertext()) for s in r.findall('.//sec') if s.findtext('title','')=='MATERIALS AND METHODS' for x in s.findall('./p'))
for expected in ['cytoplasmic reaction','counting 100 cells','1:400','1:50']:
 if expected not in methods:errors.append('BCL2 method literal:'+expected)
r=E.parse(P/'raw-cache/PMC12285907.xml').getroot()
case=' '.join(''.join(x.itertext()) for s in r.findall('.//sec') if s.findtext('title','')=='Case presentation' for x in s.findall('./p'))
if '12-year-old girl' not in case or 'positivity for S100, CD99, FLI1, and BCL2' not in case:errors.append('native-author case/qualitative BCL2 source')
c=json.loads((P/'NATIVE-ASSAY-CONTEXT.json').read_text())
if sum(x['n_material_cases'] for x in c['source_groups'][0]['material_groups'])!=3:errors.append('material count mismatch')
d=json.loads((P/'DECISION.json').read_text())
if d['new_outcome_matrices_opened'] or d['new_statistical_analysis'] or d['campaign_exhausted']:errors.append('scope/decision mismatch')
free=os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize
if free<10737418240:errors.append('storage floor')
print(json.dumps({'validation':'PASS' if not errors else 'FAIL','errors':errors,'checked':'source hashes, BCL2-only reagent/control row, all3native histology/material groups, source scoring/cytoplasmic literals, single author-case diagnostic claim, no matrix/analysis/exhaustion scope','claim_limits':'Input/source context only, not drug dependence, protein co-localization, therapeutic window, individual stain-score replication or all-public-body completeness','free_bytes':free}))
raise SystemExit(bool(errors))
