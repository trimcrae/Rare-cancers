"""Reproduce the bounded TNT evidence extraction; never infer a missing case crosswalk.
Run with installed Python and pypdf. No network or UI is used by this script.
The approximately -4% annotation is an independently checked visual reading,
not an exact numerical datum, and is preserved separately from source tables.
"""
from pathlib import Path
import hashlib, json, re, zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

P = Path(__file__).resolve().parent

def text(e):
    return ' '.join(' '.join(e.itertext()).split())

def rows(e):
    return [[text(c) for c in row if c.tag in ('td', 'th')] for row in e.findall('.//tr')]

receipts = json.loads((P / 'receipts.json').read_text(encoding='utf-8-sig'))
for receipt in receipts:
    content = (P / receipt['file']).read_bytes()
    assert len(content) == receipt['bytes'], receipt['file']
    assert hashlib.sha256(content).hexdigest() == receipt['sha256'], receipt['file']

root = ET.parse(P / 'tnt2023.xml').getroot()
tables = {e.get('id'): {'text': text(e), 'rows': rows(e)} for e in root.findall('.//table-wrap')}
figures = {e.get('id'): text(e) for e in root.findall('.//fig')}
emc_rows = [r for r in tables['T1']['rows'] if any('Extraskeletal myxoid chondrosarcoma' in c for c in r)]
assert emc_rows == [['Extraskeletal myxoid chondrosarcoma', '1 (2%)']], emc_rows
assert 'Week 6' in figures['f1'] and 'histologic subtype' in figures['f1']
assert 'rhabdomyosarcoma' in figures['f5'].lower()
assert 'chondrosarcoma' not in tables['T3']['text'].lower()
with zipfile.ZipFile(P / 'DataSheet_1.docx') as z:
    doc = ET.fromstring(z.read('word/document.xml'))
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
supp_tables = []
for table in doc.findall('.//w:tbl', ns):
    supp_tables.append([[ ''.join(cell.itertext()) for cell in row.findall('w:tc', ns)] for row in table.findall('w:tr', ns)])
assert len(supp_tables) == 5
# The supplement contains aggregate safety tables and numbered follow-up lists;
# it contains no histologic EMC label to crosswalk to the waterfall.
assert not any('chondrosarcoma' in str(t).lower() or 'Extra myx Chondro' in str(t) for t in supp_tables)
registry = json.loads((P / 'nct03886311.json').read_text())
assert registry['protocolSection']['identificationModule']['nctId'] == 'NCT03886311'
assert registry['hasResults'] is False

def abstract(filename):
    return re.sub('<[^>]*>', ' ', json.loads((P / filename).read_text())['message'].get('abstract', ''))

followups = {year: abstract(f'tnt{year}-crossref.json') for year in (2021, 2025)}
assert 'LMS/LPS' in followups[2025]
assert not any('myxoid chondrosarcoma' in a.lower() for a in followups.values())
tn_pages = [page.extract_text() or '' for page in PdfReader(P / 'tn2018-actual.pdf').pages]
joined = '\n'.join(tn_pages)
assert 'chondrosarcoma' in joined.lower()
assert not re.search(r'extra.?skeletal|myxoid\s+chondrosarcoma|NR4A3', joined, flags=re.I)
relevant_paragraphs = [text(e) for e in root.findall('.//p') if any(w in text(e).lower() for w in ('rhabdomyosarcoma', 'partial response', 'data availability', 'three patients', 'january 31', 'may 30'))]
result = {
    'evaluated_source_files': len(receipts),
    'source_bytes': sum(r['bytes'] for r in receipts),
    'source_hash_verification': 'PASS',
    'enrolled_emc_table_row': emc_rows[0],
    'one_published_emc_observation': {
        'figure_label': 'Extra myx Chondro',
        'time': 'Week 6',
        'measurement': 'Percent change in sum of longest target-lesion diameters',
        'visual_annotation': 'Small decrease, approximately 4%; exact value not provided',
        'annotation_method': 'Manual visual reading of original figure, independently repeated by microenvironment worker',
        'source_precision': 'Raster estimate only; no numerical confidence interval or precise percentage asserted',
        'patient_id': None,
        'overall_recist_category': None,
        'individual_pfs_os_durability': None,
        'individual_biomarkers': None,
        'molecular_diagnostic_support': 'Not reported; retain as authors histologic EMC',
        'treatment_attribution': 'Combination TNT only; cannot identify single-agent immune activity'
    },
    'main_table3_numbered_treatment_records': len(tables['T3']['rows'])-1,
    'supplement_tables': [{'index': i+1, 'row_count_including_headers':len(t), 'first_rows':t[:2], 'emc_crosswalk':'not provided'} for i,t in enumerate(supp_tables)],
    'paired_immune_portrait_diagnosis': 'rhabdomyosarcoma, explicitly stated in Figure 5',
    'registry_has_results': registry['hasResults'],
    'registry_status': registry['protocolSection']['statusModule'],
    '2018_tn_review': {'pages_evaluated':len(tn_pages), 'generic_chondrosarcoma_cases':2, 'one_chondrosarcoma_pr':'published aggregate histology statement', 'emc_eligibility':'unresolved; no myxoid or fusion subtype', 'overlap_with_tnt':'unresolved, same center; do not pool as independent'},
    'followup_report_dispositions': {'2020':'Protocol; no individual outcome', '2021':'Overlapping interim same NCT; no EMC case crosswalk', '2025':'LMS/LPS subset; unsuitable for additional EMC measurements'},
    'figures':figures,
    'main_tables':tables,
    'relevant_primary_paragraphs':relevant_paragraphs,
    'decision':'SHELVE standalone immune-response inference; coverage addition only, no new disease finding.'
}
(P / 'evaluation.json').write_text(json.dumps(result, indent=2, ensure_ascii=False),encoding='utf-8')
(P / 'supplement-reextraction.json').write_text(json.dumps(supp_tables,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ('evaluated_source_files','source_bytes','source_hash_verification','enrolled_emc_table_row','main_table3_numbered_treatment_records','decision')},indent=2))
