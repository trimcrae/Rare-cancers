"""Independent read-only R6 clinical identity check; never executes owner code."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,hashlib,json,re,datetime,collections
from pypdf import PdfReader
HERE=Path(__file__).resolve().parent
D=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round6/clinical_identity')
files=['RESULTS.txt','COVERAGE.json','eligibility-results.json','evaluate_eligibility.py','liver2026-supp.docx','liver2026-table1.html','primary-identity-search.json','interobserver2023.pdf','hirmas2023-metadata.json','hirmas2024-exclusion-web.json']
assert all((D/f).is_file() for f in files)
owner=json.loads((D/'eligibility-results.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(D/'liver2026-supp.docx') as z:root=E.fromstring(z.read('word/document.xml'))
w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
rows=[]
for t,table in enumerate(root.iter(w+'tbl'),1):
 for r in table.findall(w+'tr'):
  c=[''.join(x.itertext()) for x in []] # direct text nodes below avoid duplicated XML tree content
  c=[''.join(n.text or '' for n in cell.iter(w+'t')) for cell in r.findall(w+'tc')]
  if c and c[0].isdigit():rows.append([f'S{t}',*c])
assert len(rows)==76 and collections.Counter(x[0] for x in rows)=={'S1':61,'S2':15}
for ours,theirs in zip(rows,owner['liver2026']['all_individual_rows']):
 assert ours[:5]==[theirs[k] for k in ['table','case','sex','age','histology']]
 assert [int(x) for x in ours[5:]]==[theirs[k] for k in ['FDG_positive','FDG_negative','FAPI_positive','FAPI_negative']]
mes=[x for x in rows if any(s in x[4].lower() for s in ['sarcoma','solitary fibrous','stromal tumor','chordoma'])]
net=[x for x in rows if 'neuroendocrine' in x[4].lower()]
assert len(mes)==10 and sum(int(x[5])+int(x[6]) for x in mes)==32
assert len(net)==1 and int(net[0][5])+int(net[0][6])==5
alias=re.compile(r'extraskeletal|myxoid.chondrosarcoma|NR4A[23]|\bEMC\b',re.I)
assert not any(alias.search(x[4]) for x in rows)
raw=json.loads((D/'primary-identity-search.json').read_text(encoding='utf-8'))['result']
categories=[]
for line in raw.splitlines():
 cells=[x.strip() for x in line.split('|')]
 if len(cells)==2 and cells[1].isdigit():categories.append((cells[0],int(cells[1])))
assert len(categories)==14 and sum(n for _,n in categories)==43 and dict(categories)['Sarcoma']==2
pdf=PdfReader(D/'interobserver2023.pdf');pages=[p.extract_text() for p in pdf.pages];pt='\n'.join(pages)
assert len(pages)==6 and not alias.search(pt)
# Confirm that absence of an EMC label is not mistaken for exclusion of generic sarcoma.
contexts=[]
for m in re.finditer('sarcoma|Supplemental Data File|teaching|test case',pt,re.I):contexts.append(pt[max(0,m.start()-140):m.end()+200])
h23=json.loads((D/'hirmas2023-metadata.json').read_text(encoding='utf-8'))['resultList']['result'][0]
assert '131/324' in h23['abstractText']
h24=json.loads((D/'hirmas2024-exclusion-web.json').read_text(encoding='utf-8'))['result']
assert 'Patients with sarcoma, pancreatic cancer, and pleural mesothelioma have been excluded from this analysis' in h24
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'review':'read-only independent eligibility and value challenge; no downloads, source effects or new research',
'input_sha256':{f:hashlib.sha256((D/f).read_bytes()).hexdigest() for f in files},
'checks':{'all76_original_DOCX_rows_match':True,'S1':61,'S2':15,'all_source_condition_counts_match':True,'direct_EMC_label_hits':0,'ten_mesenchymal_labelled_cases_lesions':32,'one_neuroendocrine_case_lesions':5,'timepoint_all14_category_sum':43,'generic_timepoint_sarcomas':2,'original_PDF_pages':6,'Hirmas2024_original_exclusion_receipt_matches':True,'Hirmas2023_sarcoma131_of324_abstract_matches':True},
'generic_rows':[x[:5] for x in mes if 'pleomorphic' in x[4]],
'decision':'Agree with scoped shelving. No authenticated EMC comparison; no new disease finding. Labels lacking EMC are not a universal negative.',
'material_limits':['S1:4 pleomorphic sarcoma unresolved; no molecular diagnosis inferred','11/37 grouping corresponds arithmetically to10/32+neuroendocrine1/5, but no reclassification established','Both Naeimi sarcomas, all10 Mei sarcomas and all131 Hirmas2023 sarcomas remain unresolved individually','Four teaching cases/test material not assumed extra donors or non-EMC','Repeated scans/readers/lesions are not donors; Essen, Heidelberg and Fudan overlap remains unresolved','Primary indexed-text receipts are not original XML/PDF downloads','No global absence or exhaustion claim; accessible suitable unevaluated sources block advancement'],
'corrections_required':[],'independent_value':'No claimed new EMC result survives. Repeating known broad-sarcoma imaging performance or repairing an aggregate classification does not establish useful disease knowledge.'}
(HERE/'clinical-independent-review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out['checks'],indent=2));print('\n'.join(contexts)[:4000])