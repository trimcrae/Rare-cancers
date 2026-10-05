#!/usr/bin/env python3
"""Independent exact-source clinical eligibility check; no source retrieval/images."""
import datetime,hashlib,io,json,pathlib,re,shutil,xml.etree.ElementTree as E,zipfile
BASE=pathlib.Path(__file__).resolve().parent;OWNER=pathlib.Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round9/clinical_measurements')
def binding(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def text(x):return ' '.join(x.itertext()).strip()
def root(pmc):return E.fromstring((OWNER/'source-cache'/(pmc+'-EPMC-JATS.xml')).read_bytes())
def table(pmc,i=0):return text(root(pmc).findall('.//table-wrap')[i])
freeze=json.loads((OWNER/'FREEZE.json').read_text());port=json.loads((OWNER/'PORTABILITY.json').read_text());errors=[];bindings=[binding(OWNER/'FREEZE.json')]
assert bindings[0]['sha256']=='630b77efcfde36825e4e11c4d5db1a61ce65e62c1d18e01598f28aecaf0f25fa'
for rec in freeze['files']+port['ignored_sources']:
 b=binding(OWNER/rec['path']);bindings.append(b)
 if b['sha256']!=rec['sha256'] or b['bytes']!=rec['bytes']:errors.append(rec['path'])
assert not errors
checks=[]
def check(n,test,e):
 assert test,n;checks.append({'check':n,'pass':True,'source_evidence':e})
check('firstline40_actual_EMC_footnote',all(s in table('PMC11443219') for s in ['n  = 40','Others','myofibroblastic sarcoma and extraskeletal myxoid chondrosarcoma']), 'Table1 Others2; both labels named, count one of each implied; no individual ID/outcome')
check('maintenance49_EMC1',any('Extraskeletal myxoid chondrosarcoma' in text(x) and '1 (2)' in text(x) for x in root('PMC10520347').findall('.//tr')),'Table1 explicitly one EMC; baseline49; Other7 exact response category remains unassigned')
t=table('PMC11164811');check('selum_EMC125_assigned_cohort',all(s in t for s in ['Selumetinib 125','Pembrolizumab 200','8 (57) c','extraskeletal myxoid chondrosarcoma']),'Table1 footnote c assigns EMC to125mg group; actual dose reductions/dates/lesions unknown')
rr=root('PMC12434394');myx=[x for x in rr.findall('.//tr') if 'Myxoid chondrosarcoma' in text(x)];check('Cnovyi_generic_myxo_cohort2',len(myx)==1 and '1 (25%)' in text(myx[0]),'Table1 generic myxoid chondrosarcoma1 in dosecohort2; not canonicalEMC or MDA-ID mapping')
check('AMXT56_actual_EMC1',any('Extraskeletal myxoid chondrosarcoma' in text(x) and '1 (2)' in text(x) for x in root('PMC12451337').findall('.//tr')),'Table2 EMC1, genericchondrosarcoma1/uterinesarcoma1/notreported1; no individual regimen/outcome map')
tr=table('PMC7286446');check('trabectedin_known_two_cases',all(s in tr for s in ['66','37','29','Extraskeletal myxoid chondrosarcoma','2 (3.0)','2 (5.4)','0 (0.0)']),'Table1 total66=comparative37+extension29; bothEMCs belong to comparative source trial, known priorcase reuse')
paras=[text(x) for x in root('PMC13396634').findall('.//p')];check('Taz_EMC_eligibility_not_enrolment',any('Cohort 3; includes' in x and 'extraskeletal myxoid chondrosarcoma' in x for x in paras),'Main enrollment criteria; Other32 subtype roster not established; source data consent/privacy restricted')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};z=zipfile.ZipFile(OWNER/'source-cache/Cnovyi-supplement.zip');g=json.loads((OWNER/'CNOVYI-BASELINE-AND-RESPONSE-TABLE-GATE.json').read_text());norm=lambda s:re.sub(r'\s+','',s).lower()
for suffix,key in [('table_s3_supps3.docx','all16_baseline_rows'),('table_s4_supps4.docx','all_S4_response_rows')]:
 n=next(n for n in z.namelist() if n.endswith(suffix));b=z.read(n);r=E.fromstring(zipfile.ZipFile(io.BytesIO(b)).read('word/document.xml'));t=r.find('.//w:tbl',ns)
 rows=[[' '.join(x.text or '' for x in c.findall('.//w:t',ns)) for c in tr.findall('w:tc',ns)] for tr in t.findall('w:tr',ns)]
 check('Cnovyi_'+suffix+'_all_rows_exact_normalized',[[norm(x) for x in row] for row in rows]==[[norm(x) for x in row] for row in g[key]],'All16baseline rows+header or all8response-table rows; whitespace-normalized DOCX cells, not cohort→patient inference')
z=zipfile.ZipFile(OWNER/'source-cache/Tazemetostat-EPMC-supplement.zip');n=next(n for n in z.namelist() if n.endswith('.docx'));d=E.fromstring(zipfile.ZipFile(io.BytesIO(z.read(n))).read('word/document.xml'));p=[' '.join(t.text or '' for t in x.findall('.//w:t',ns)) for x in d.findall('.//w:p',ns)];hit=next(x for x in p if '7 paired biopsies' in x)
check('Taz_all7paired_biopsy_labels',all(s in hit for s in ['1 SCCOHT','1 rhabdoid tumor','1 renal medullary carcinoma','1 nerve sheath tumor','1 myoepithelial carcinoma','2 patients with synovial sarcoma']),'All7source labels retained; none explicitlydeclaredEMC, no mechanism-transfer')
st=(OWNER/'source-cache/Selumetinib-text.txt').read_text();check('Selum_public_graphics_pending_not_axis_values',all(s in st for s in ['Online Resource 4','Patient off study drug','First occurrence of new lesion','Week since treatment initiation']),'Public14-page supplemental text includes captions/axes, not explicit EMC individual-lesion/date map; graphics not inspected during ban')
check('source_restrictions_not_public_individual_data',any('Source data are not provided' in s and 'privacy restrictions' in s for s in paras),'Taz privacy/request-only source data; publicplots distinct from unlocated/request-only tables')
assert shutil.disk_usage(BASE).free>=10737418240
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner_original_commit':'9eafdee750e12e5a706608ab7e702e841f2ce82c','original_freeze_files':len(freeze['files']),'cache_files':len(port['ignored_sources']),'hash_mismatches':errors,'checks':checks,'bindings':bindings,'scope':'Independent original source/condition/availability and value review; no image inspection, fresh retrieval, numerical growth calculation or repository preflight'}
(BASE/'ORIGINAL-SOURCE-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'bindings':len(bindings),'hash_errors':len(errors)},indent=2))
