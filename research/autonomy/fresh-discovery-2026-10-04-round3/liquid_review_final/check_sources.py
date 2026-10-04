from pathlib import Path
import sys,json,hashlib,re,csv
from datetime import datetime,timezone
from pypdf import PdfReader
base=Path(__file__).parent
src=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round3/liquid_biomarker')
wheel=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round3/dlk1/xlrd-2.0.2-py2.py3-none-any.whl')
sys.path.insert(0,str(wheel));import xlrd
names=['RESULTS.txt','COVERAGE.txt','evaluation.json','heinhuis2020-Table S2.xls','axists2023-supp.pdf','axists2023-supp.txt','GSE124158-GPL18941-metadata.txt','GSE124158-GPL21263-identity-metadata.txt','asano2019-supp.txt','pastuszak-tables.json']
hashes=[{'file':str(src/n),'bytes':(src/n).stat().st_size,'sha256':hashlib.sha256((src/n).read_bytes()).hexdigest()} for n in names]
book=xlrd.open_workbook(src/'heinhuis2020-Table S2.xls')
sheets=[]
for sheet in book.sheets():
 rows=[sheet.row_values(i) for i in range(sheet.nrows)]
 hits=[{'row_1based':i+1,'values':r} for i,r in enumerate(rows) if re.search(r'extraskeletal|chondrosarcoma|NR4A[23]|\bEMC\b|patient|sample|histolog',str(r),re.I)]
 sheets.append({'name':sheet.name,'nrows':sheet.nrows,'ncols':sheet.ncols,'head':rows[:6],'eligibility_hits':hits})
meta=[]
for n in names:
 if n.startswith('GSE'):
  t=(src/n).read_text(encoding='utf8')
  sample_rows=[r for r in csv.reader(t.splitlines(),delimiter='\t') if r and r[0].startswith('!Sample_')]
  accession_rows=[r[1:] for r in sample_rows if r[0]=='!Sample_geo_accession']
  ids=set(accession_rows[0])
  diagnoses=[r[1:] for r in sample_rows if r[0]=='!Sample_characteristics_ch1' and len(r)>1 and r[1].startswith('patient diagnosis:')]
  meta.append({'file':n,'n_unique_GSM':len(ids),'sample_metadata_rows':len(sample_rows),'diagnosis_labels':sorted(set(sum(diagnoses,[]))),'alias_hits':re.findall(r'.{0,50}(?:extraskeletal|chondrosarcoma|NR4A3|\bEMC\b).{0,50}',t,re.I)})
pages=[]
for i,p in enumerate(PdfReader(src/'axists2023-supp.pdf').pages):
 text=p.extract_text() or ''
 if re.search(r'proteomic|ACTG1|Appendix 6',text,re.I):
  pages.append({'page_1based':i+1,'text':text})
out={'utc':datetime.now(timezone.utc).isoformat(),'source_hashes':hashes,'reader':{'path':str(wheel),'sha256':hashlib.sha256(wheel.read_bytes()).hexdigest()},'heinhuis_S2_full_sheets':sheets,'asano_metadata_check':meta,'axi_relevant_pages':pages}
(base/'source-crosscheck.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('S2',[(s['name'],s['nrows'],s['ncols'],len(s['eligibility_hits'])) for s in sheets])
print('S2heads', [s['head'][:3] for s in sheets]);print('GEO',meta);print('Axi pages',[p['page_1based'] for p in pages])
