import collections,csv,datetime,hashlib,json,pathlib,re,xml.etree.ElementTree as E,zipfile
ROOT=pathlib.Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research');P=ROOT/'.cache/fresh-emc-public-route';Q=ROOT/'research/autonomy/zurich-ordinal-source-2026-09-06';O=pathlib.Path(__file__).parent
errors=[];checks=[];hashes={}
def read(p):
 b=p.read_bytes();hashes[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
def ck(x,n):
 checks.append({'check':n,'passed':bool(x)})
 if not x:errors.append(n)
x=read(P/'zurich-ncc-identity-crosswalk.json');freeze=read(P/'zurich-ncc-identity-freeze.json');rec=read(Q/'independent-verification/reconciliation.json')
for n,h in freeze['sha256'].items():ck(hashlib.sha256((P/n).read_bytes()).hexdigest()==h,'freeze hash '+n)
ck((P/'NCC-MOESM4.xlsx').read_bytes()==(ROOT/'research/autonomy/ncc-screen-source-2026-09-06/sources/NCC-MOESM4.xlsx').read_bytes(),'catalogue matches committed source')
ck((P/'zurich2023-fig5-ordinal-roster.csv').read_bytes()==(Q/'zurich2023-fig5-ordinal-roster.csv').read_bytes(),'first reader roster matches committed source')
# Independent XLSX extraction uses ZIP/XML; worker used openpyxl.
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(P/'NCC-MOESM4.xlsx') as z:
 ss=E.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(t.text or '' for t in si.iter('{'+ns['s']+'}t')) for si in ss]
 wb=E.fromstring(z.read('xl/workbook.xml'));rels=E.fromstring(z.read('xl/_rels/workbook.xml.rels'));mapping={r.attrib['Id']:r.attrib['Target'] for r in rels}
 sheet=next(s for s in wb.find('s:sheets',ns) if s.attrib['name']=='drug list');target=mapping[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
 target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
 data=E.fromstring(z.read(target));table={}
 for row in data.findall('.//s:sheetData/s:row',ns):
  values={}
  for c in row:
   col=re.sub('[0-9]','',c.attrib['r'])
   if col not in ('A','B','C'):continue
   v=c.find('s:v',ns)
   if v is not None:values[col]=strings[int(v.text)] if c.attrib.get('t')=='s' else v.text
   elif c.attrib.get('t')=='inlineStr':values[col]=''.join(t.text or '' for t in c.findall('.//s:t',ns))
  if int(row.attrib['r'])>=4 and values.get('A'):table[values['A']]=dict(catalogue_id=values['A'],cas=values['B'],ncc_name=values['C'],sheet='drug list',excel_row=int(row.attrib['r']))
ck(len(table)==221,'221 catalogue rows')
roster=list(csv.DictReader((Q/'zurich2023-fig5-ordinal-roster.csv').open(encoding='utf-8-sig')))
# Independently specified nominal candidate identities, reviewed without using NCC response values in this task.
expected_ids=['S2853','S1208','S1225','','S1148','S1149','','S1209','S1231','S1221','','S1135','S1214','S4505','S1229','S1150','S4269','','','S8048','','S7083 S4967','','S7108','S2807 S5069','S1085','S1068 S5190','S5716 S7158','','','S4484','S8205 S4929','S7625','S1023','S7397 S1040','','S7128','S1119 S4001','S1490','']
expected_unresolved={12:'hydrate_unresolved',22:'form_unresolved',25:'form_unresolved',27:'form_unresolved',28:'label_unresolved',31:'solvate_unresolved',32:'form_unresolved',35:'form_unresolved',36:'label_unresolved_absent',38:'form_unresolved'}
ck(len(x)==len(roster)==len(expected_ids)==40,'40 labels complete');csvrows=list(csv.DictReader((P/'zurich-ncc-identity-crosswalk.csv').open(encoding='utf-8-sig')));ck(len(csvrows)==40,'CSV 40 labels')
label_records=[]
for i,(r,original,ids,flat) in enumerate(zip(x,roster,expected_ids,csvrows),1):
 ck(r['roster_index']==i,'row index '+str(i));ck(r['zurich_label_verbatim']==original['source_drug_label'],'first reader literal label '+str(i))
 ir=next(v for v in rec['rows'] if v['panel']==original['panel'] and v['panel_row']==int(original['panel_row']))
 ck(ir['first_reader_label']==r['zurich_label_verbatim'],'independent reconciliation linkage '+str(i))
 label_records.append(dict(index=i,crosswalk_label=r['zurich_label_verbatim'],independent_literal=ir['independent_label'],exact_match=ir['label_exact_match']))
 ck([c['catalogue_id'] for c in r['candidates']]==ids.split(),'candidate-set review '+str(i))
 for c in r['candidates']:ck(c==table[c['catalogue_id']],'exact XLSX pointer '+c['catalogue_id'])
 status=expected_unresolved.get(i,'nominal_unique' if ids else 'absent');ck(r['status']==status,'status review '+str(i));ck(r['strict_nominal_include']==(status=='nominal_unique'),'strict rule '+str(i))
 for k in ['zurich_label_verbatim','status','rationale']:ck(flat[k]==r[k],'CSV agreement '+str(i)+k)
 ck(flat['candidate_ids']==' | '.join(c['catalogue_id'] for c in r['candidates']),'CSV IDs '+str(i));ck(flat['candidate_cas']==' | '.join(c['cas'] for c in r['candidates']),'CSV CAS '+str(i));ck(flat['candidate_names']==' | '.join(c['ncc_name'] for c in r['candidates']),'CSV names '+str(i));ck(flat['strict_nominal_include']==str(r['strict_nominal_include']),'CSV include '+str(i))
# Absent-source aliases are checked against only the catalogue identity text, never response tables.
aliases=['sn38','mitomycinc','oxaliplatin','puh71','hdm201','siremadlin','nvphdm201','derazantinib','arq087','azd5153','adavosertib','mk1775','azd1775','ipatasertib','gdc0068','we822','ve822','berzosertib','vx970','m6620','selpercatinib','loxo292']
names=[re.sub('[^a-z0-9]','',r['ncc_name'].lower()) for r in table.values()]
for alias in aliases:ck(not any(alias in n for n in names),'absent catalogue alias '+alias)
# Read explicit excluded rows to demonstrate no substitution of forms or different drugs.
excluded=['E2516','S1714','S9321','S5971','S1491','S7505','S2741','S7786']
exclusions={c:table[c] for c in excluded};chosen={c['catalogue_id'] for r in x for c in r['candidates']}
ck(not chosen.intersection(excluded),'all named wrong-form exclusions absent')
counts=dict(collections.Counter(r['status'] for r in x));ck(counts==freeze['counts'],'status counts');ck(sum(r['strict_nominal_include'] for r in x)==freeze['strict_nominal_labels']==20,'20 nominal labels');ck(sum(len(r['candidates']) for r in x)==freeze['candidate_ncc_rows']==36,'36 candidate rows')
notes=(P/'zurich-ncc-identity-source-notes.md').read_text();ck('not a claim of personal blinding' in notes,'personal blinding caveat retained');ck('not evidence of compatible assays' in notes,'assay compatibility caveat retained')
report=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Independent catalogue/label/source-pointer verification only; no response comparison statistic',method='ZIP/XML independent extraction; manually reviewed 40 label candidate sets and status rules',labels_checked=40,exact_label_matches_to_independent_reader=sum(r['exact_match'] for r in label_records),literal_differences=[r for r in label_records if not r['exact_match']],candidate_pointer_count=36,counts=counts,strict_nominal_labels=20,distinct_candidate_ncc_rows=len(chosen),no_candidate_labels=sum(not r['candidates'] for r in x),excluded_catalogue_records=exclusions,checks=checks,discrepancies=errors,limitations=['20 matches are nominal label matches only, not certified same formulation or compatible assay','Three HCI/HCl glyph ambiguities and one capitalization difference are inherited and retained','Abmaciclib and WE-822 remain unresolved','No response data were opened in this verification task; verifier previously inspected NCC responses in earlier tasks and is not personally outcome-blinded','No comprehensive synonym database or reagent authenticity verification is claimed'],verdict='verified nominal crosswalk' if not errors else 'repair required')
(O/'verification.json').write_text(json.dumps(report,indent=2)+'\n');hashes[str(pathlib.Path(__file__))]=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest();(O/'input-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['labels_checked','candidate_pointer_count','counts','strict_nominal_labels','no_candidate_labels','discrepancies','verdict']},indent=2))
assert not errors
