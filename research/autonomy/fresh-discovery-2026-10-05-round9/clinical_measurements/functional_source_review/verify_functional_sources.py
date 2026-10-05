import pathlib,json,hashlib,re,xml.etree.ElementTree as E,subprocess,datetime
SRC=pathlib.Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new')
OUT=pathlib.Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((SRC/'MANIFEST.json').read_text())
checks=[]
for x in manifest['exports']:
 b=(SRC/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'];checks.append({'path':x['path'],'sha256':sha(b)})
port=json.loads((SRC/'PORTABILITY.json').read_text())
for x in port['cache_only']:
 b=(SRC/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
reuse=json.loads((SRC/'REUSED-INPUTS.json').read_text())
for x in reuse['inputs']:
 b=pathlib.Path(x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
ro=json.loads((SRC/'PRIMARY-ROSTERS.json').read_text());row_results={}
norm=lambda s:re.sub(r'\s+','',s)
for n in ['integration2026','cho2024','serum2025']:
 root=E.parse(SRC/'raw-cache'/f'{n}.xml').getroot()
 table=next(t for t in root.findall('.//table-wrap') if t.find('label') is not None and ''.join(t.find('label').itertext()).strip()=='Table 1')
 rows=[[''.join(c.itertext()) for c in tr.findall('td')]for tr in table.findall('.//tbody/tr')]
 assert [[norm(c)for c in row]for row in rows]==[[norm(c)for c in row]for row in ro[n]['rows']]
 row_results[n]={'all_rows':len(rows),'every_cell_matches_after_whitespace_only_normalization':True}
cho=ro['cho2024']['rows'];assert sum(r[2]=='UPS'for r in cho)==6;assert sum(r[2]=='CHS'for r in cho)==1;assert sum(r[2]=='FS'for r in cho)==1
cr=E.parse(SRC/'raw-cache/cho2024.xml').getroot();cp=[' '.join(''.join(x.itertext()).split())for x in cr.findall('.//p')]
assert any('SNU-5373; primary, SNU-6217 A; relapse' in x for x in cp)
assert any('18 new sarcoma cell lines derived from 14 patients' in x for x in cp)
liv=json.loads((SRC/'LIVING-ROSTER.json').read_text());text=(SRC/'raw-cache/living2026-text.txt').read_text();assert liv['primary_table1_verbatim'] in text
start=text.index('TA B L E 1');end=text.index('Note: In patients',start);tb=text[start:end]
assert re.findall(r'TBB-S-\d+',tb)==[x['donor']for x in liv['donor_rows']]
assert re.findall(r'\bSAR\d+(?:A[1-4])?\b',tb)==[c for x in liv['donor_rows']for c in x['cultures']]
assert len(liv['donor_rows'])==19 and sum(len(x['cultures'])for x in liv['donor_rows'])==29
assert len(set(c for x in liv['donor_rows']for c in x['cultures']))==29
assert sum('Undifferentiated sarcoma' in x['diagnosis_literal']for x in liv['donor_rows'])==3
qtext=(SRC/'raw-cache/qpop2025-supp-text.txt').read_text();pages=[x for x in qtext.split('\f')if x.strip()]
info=subprocess.check_output(['pdfinfo',str(SRC/'raw-cache/41698_2025_851_MOESM1_ESM.pdf')],text=True)
assert re.search(r'Pages:\s+8\b',info) and len(pages)==8
assert 'Uncropped blots for Figure 6e' in pages[7]
for m in ['LPS141','FU-DDLS-1','MLS402','T778']:assert m in pages[7]
err=SRC/'QPOP-PAGE-COVERAGE-ERRATUM.json';assert sha(err.read_bytes())=='d08ebe3a5ee5a106863632507b082019513c8041227705e5d1a65fbfbed3f614'
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':'8f9c24d984ec90f78abf3430e964ce8bc92e5eb6','manifest_sha256':sha((SRC/'MANIFEST.json').read_bytes()),'original_exports_verified':len(checks),'original_exports':checks,'cache_files_verified':len(port['cache_only']),'cache_bindings':port['cache_only'],'reused_input_bindings_verified':len(reuse['inputs']),'roster_checks':row_results,'living':{'ordered_donor_ids':19,'ordered_culture_ids':29,'broad_UPS_donors':3,'SW1353':'separate commercial chondrosarcoma control, no authenticated EMC inference','known_repeats':'8 MPNST, 2 LMS, 3 MFS cultures are 3 donors; stages/regions/treatment conditions retained in complete Table1 verbatim'},'cho':{'lines':18,'patients':14,'UPS_conditions':6,'UPS_donors':4,'generic_CHS':1,'generic_FS':1,'other_named_entities':10,'same_donor':'6219A/B/E;6246C/D;5373primary/6217Arelapse','literal_eight_diagnosis_categories':'retained despite primary abstract seven-subtype wording'},'qpop':{'PDF_pages':8,'nonempty_text_pages':8,'erratum_sha256':sha(err.read_bytes()),'primary':'51 collected,45 successful samples;14 evaluable patients,27 treatment outcomes are distinct denominators, not independent donors','page8':'uncropped Fig6e labelled LPS141/FU-DDLS-1/MLS402/T778; source liposarcoma identities not new EMC conditions; no blot/intensity inspection','pending':'public graphical full45 histology/assay crosswalk uninspected; individual phenotypic raw data request-only, no outreach'},'method':'zero downloads; cached XML/plain text and PDF metadata only; no graphical/image/browser/UI inspection; source inputs read-only; no new functional response arithmetic','status':'PASS bounded source/identity/value shelving after additive QPOP page erratum','value':'Roster recovery and assay concordance/context repair are source progress. No authenticated new EMC numerical perturbation or novel useful controlled inference; no vulnerability, efficacy, global absence or search-exhaustion conclusion.'}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('PASS',len(checks),len(port['cache_only']),len(reuse['inputs']))
