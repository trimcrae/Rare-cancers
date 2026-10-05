"""Source-level independent audit; no survival or efficacy estimate."""
import pathlib,json,hashlib,xml.etree.ElementTree as E
P=pathlib.Path(__file__).resolve().parent
O=pathlib.Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/clinical_durability_source_gate')
S=O/'raw-cache/PMC3879193.xml'
errors=[]
if hashlib.sha256(S.read_bytes()).hexdigest()!='390e456b36664c767f2b06d5bc6c5ffc2afcf5f2d1074727dd5c06fc248bf8c7':errors.append('original source hash mismatch')
r=E.parse(S).getroot();tables=[]
for t in r.findall('.//table-wrap'):
 heads=[''.join(x.itertext()) for x in t.findall('.//thead//th')+t.findall('.//thead//td')]
 if 'PFS' in heads:tables.append((t,heads))
if len(tables)!=1:errors.append('expected unique PFS table')
t,heads=tables[0]
rows=[[''.join(x.itertext()).strip() for x in y.findall('./td')+y.findall('./th')] for y in t.findall('.//tbody/tr')]
owner=json.loads((O/'ALL11-SOURCE-INPUTS.json').read_text())
if len(rows)!=11 or len(owner['all11_source_rows'])!=11:errors.append('all11 coverage mismatch')
byid={x['source_case_id']:x for x in owner['all11_source_rows']}
for row in rows:
 if row[0] not in byid:errors.append('case key absent');continue
 if row[3]!='EMC' or row[4]!='yes':errors.append('native-EMC/source NR4A3 identity mismatch')
 if row[-1]!=byid[row[0]]['source_pfs_literal']:errors.append('literal PFS source mismatch')
 # Explicit asterisk maps surgery. Plain durations are not decoded into failures.
 hasstar='*' in row[-1]
 if hasstar != (row[0] in ['1','7','10']):errors.append('surgery-key mismatch')
foot=' '.join(''.join(x.itertext()) for x in t.findall('./table-wrap-foot'))
if 'censored at the time of surgical resection' not in foot:errors.append('asterisk source definition missing')
normalize=lambda s:' '.join(s.split())
quote=normalize(owner['postoperative_source_quote'])
if not any(quote in normalize(''.join(x.itertext())) for x in r.findall('.//p')):errors.append('postoperative source quotation mismatch')
res=json.loads((O/'MEASUREMENT-GATE-RESULTS.json').read_text())
if any(res[x] is not None for x in ['six_month_cif','six_month_bounds','clinical_failure_count']):errors.append('unsupported numerical estimate launched')
if res['bootstrap_run'] or res['survival_curve_reconstruction_performed']:errors.append('unsupported numerical/reconstruction stage')
print(json.dumps({'validation':'PASS' if not errors else 'FAIL','errors':errors,'source_cases_checked':11,'literal_identity_PFS_fields_checked':44,'complete_surgery_asterisk_case_ids':['1','7','10'],'terminal_event_vs_contact_mapping':'eight plain-duration states unmarked, not inferred from RECIST','interpretation':'Independent input/schema/estimand check; no endpoint probabilities, risk, efficacy or all-public-source completion claimed'}))
raise SystemExit(bool(errors))
