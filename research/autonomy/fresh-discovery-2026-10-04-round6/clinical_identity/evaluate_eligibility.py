"""Reproduce the bounded five-cohort clinical identity gate from retained sources.
No EMC SUV or lesion-detection effect is calculated without an authentic case.
Optional --gu-source binds an unchanged R5 source for cohort-overlap checks.
"""
import argparse, collections, hashlib, html, json, pathlib, re, zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

D = pathlib.Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--gu-source', type=pathlib.Path)
args = parser.parse_args()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(D / 'liver2026-supp.docx') as z:
    root = ET.fromstring(z.read('word/document.xml'))
all_rows = []
for table_number, table in enumerate(root.findall('.//w:tbl', ns), 1):
    for tr in table.findall('w:tr', ns):
        cells = [''.join(n.text or '' for n in tc.findall('.//w:t', ns)) for tc in tr.findall('w:tc', ns)]
        if cells and cells[0].isdigit():
            assert len(cells) == 8, cells
            all_rows.append({'table': 'S'+str(table_number), 'case': cells[0], 'sex': cells[1], 'age': cells[2],
                             'histology': cells[3], 'FDG_positive': int(cells[4]), 'FDG_negative': int(cells[5]),
                             'FAPI_positive': int(cells[6]), 'FAPI_negative': int(cells[7])})
assert len(all_rows) == 76
assert collections.Counter(x['table'] for x in all_rows) == {'S1': 61, 'S2': 15}
assert all(x['FDG_positive'] + x['FDG_negative'] == x['FAPI_positive'] + x['FAPI_negative'] for x in all_rows)
emc_alias = re.compile(r'extraskeletal|myxoid.chondrosarcoma|NR4A3|NR4A2|\bEMC\b', re.I)
for row in all_rows:
    row['EMC_label_match'] = bool(emc_alias.search(row['histology']))
    row['identity_disposition'] = ('unresolved generic pleomorphic histology; not authenticated EMC' if row['histology'] == 'pleomorphic sarcoma'
                                   else 'published alternate diagnosis; no EMC authentication')
assert not any(x['EMC_label_match'] for x in all_rows)
mesenchymal = [x for x in all_rows if re.search(r'sarcoma|solitary fibrous|stromal tumor|chordoma', x['histology'], re.I)]
net = [x for x in all_rows if 'neuroendocrine' in x['histology']]
assert len(mesenchymal) == 10 and len(net) == 1
mesenchymal_lesions = sum(x['FDG_positive'] + x['FDG_negative'] for x in mesenchymal)
assert mesenchymal_lesions == 32
assert sum(x['FDG_positive'] + x['FDG_negative'] for x in net) == 5
main = (D / 'liver2026.html').read_text(encoding='utf-8')
main_text = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', main)))
table_html = (D / 'liver2026-table1.html').read_text(encoding='utf-8')
table1 = []
for tr in re.findall(r'<tr\b.*?</tr>', table_html, re.S):
    cells = [re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', cell))).strip() for cell in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', tr, re.S)]
    if len(cells) == 2 and re.fullmatch(r'\d+ \(\d+\)', cells[1]):
        table1.append({'histology': cells[0], 'patients': int(cells[1].split()[0]), 'lesions': int(re.search(r'\((\d+)\)', cells[1])[1])})
assert sum(x['patients'] for x in table1) == 76
assert sum(x['lesions'] for x in table1) == 189
assert not any(emc_alias.search(x['histology']) for x in table1)
tp = json.loads((D / 'primary-identity-search.json').read_text(encoding='utf-8'))['result']
timepoint_table = []
for label, count in re.findall(r'^([^\n|]+)\s+\|\s+(\d+)\s*$', tp, re.M):
    timepoint_table.append({'histology': label.strip(), 'patients': int(count)})
assert len(timepoint_table) == 14 and sum(x['patients'] for x in timepoint_table) == 43
assert next(x['patients'] for x in timepoint_table if x['histology']=='Sarcoma') == 2
h24 = json.loads((D / 'hirmas2024-exclusion-web.json').read_text(encoding='utf-8'))['result']
exclusion = 'Patients with sarcoma, pancreatic cancer, and pleural mesothelioma have been excluded from this analysis'
assert exclusion in h24
pages = [p.extract_text() for p in PdfReader(D / 'interobserver2023.pdf').pages]
assert len(pages) == 6
intertext = '\n'.join(pages)
assert 'Supplemental Data File 1' in intertext and 'Supplemental Data File 2' in intertext
inter_aliases = emc_alias.findall(intertext)
h23 = json.loads((D / 'hirmas2023-metadata.json').read_text())['resultList']['result'][0]
assert h23['id'] == '36581374'
assert '131/324' in h23['abstractText']
inputs = ['PLAN.json', 'liver2026.html', 'liver2026-table1.html', 'liver2026-supp.docx', 'interobserver2023.pdf',
          'primary-identity-search.json', 'hirmas2024-exclusion-web.json', 'hirmas2023-metadata.json']
out = {'scope':'Identity evaluation, not a disease association or absence study',
       'input_sha256':{f:sha(D/f) for f in inputs},
       'liver2026':{'all_individual_rows':all_rows,'table1':table1,'case_count':76,'table1_count':76,
                    'table1_lesions':189,'EMC_labelled_cases':0,'unresolved_case':'S1:4 female59 pleomorphic sarcoma',
                    'reported_sarcoma_count':11,'sarcoma_or_SFT_GIST_chordoma_labelled_rows':mesenchymal,
                    'labelled_mesenchymal_rows':10,'labelled_mesenchymal_lesions':32,'neuroendocrine_rows':net,
                    'grouping_discrepancy':'Ten mesenchymal-labelled cases/32 lesions plus one neuroendocrine case/5 lesions would total the authors sarcoma11/37. This is an arithmetic correspondence, not a verified study crosswalk or a reclassification.',
                    'conditions':'All76 subjects had FAPI04/FDG scans within one week; newly diagnosed or at least3months from last treatment per inclusion criteria. Individual protocols/scan dates not released.',
                    'donor_overlap':'Fudan Shanghai Cancer Center, May2020-April2023, IRB2004216-25. Potential overlap with Gu2022 recurrentSTS May2020-May2021 under same center/IRB. No donor crosswalk; do not pool.'},
       'timepoint2023':{'all_categories':timepoint_table,'n':43,'sarcoma_n':2,'identity':'Generic sarcoma; no subtype or individual case ID in evaluated primary main article',
                        'conditions':['10min','1hour','3hours'],'independence':'3 scans each; not129donors','overlap':'Heidelberg S016/2018; overlap with prior Heidelberg series unresolved; no individual chronology.'},
       'hirmas2023':{'n':324,'sarcoma_n':131,'paired_FDG_all_entities_n':237,'evaluation':'Actual primary abstract evaluated; complete main and supplement not obtained. Sarcoma131 subtype/IDs unavailable in evaluated release.',
                     'overlap':'Essen Oct2018-Oct2021 registry; potential Kessler47/Lanzafame200/Pabst cohort overlap. Do not sum study n as donors.'},
       'hirmas2024':{'n':115,'paired_FDG_n':103,'sarcoma_eligibility':'Explicitly excluded in original Methods; this analyzed cohort is unsuitable for EMC comparison.',
                     'source_location':'Study Design and Participants, indexed primary JNM main body; receipt retained.'},
       'interobserver2023':{'n':50,'sarcoma_n':10,'original_pdf_pages_evaluated':6,'EMC_alias_matches_in_pdf':inter_aliases,
                            'identity':'Ten generic sarcomas; main Table1 has aggregate characteristics, Table5 broad entities, Figure2D generic sarcoma diverticulosis. No EMC-specific diagnosis/measurement.',
                            'conditions':'FAPI46 scans10-48min (mean14min), BiographmCT/Vision; 15observers are readers, not donors. Nine sarcoma cases had diagnostic CT; no same-case FDG comparison given.',
                            'supplement_gap':'Original manuscript identifies written guide SDF1, four teaching cases SDF2, and one test patient. Those cases cannot be assumed independent/additional donors or non-EMC; supplements not acquired.',
                            'overlap':'Essen+Bologna clinical databases; NCT04990882; same Essen ethics19-8991-BO/20-9485-BO as registry. No donor dates/crosswalk.'},
       'gate':{'authenticated_EMC_cases':0,'numeric_EMC_pilot_run':False,'decision':'SHELVE standalone paper for this bounded lane; unresolved evidence prevents an absence or exhaustive coverage claim.'}}
if args.gu_source:
    x=ET.parse(args.gu_source).getroot()
    selected=[''.join(p.itertext()) for p in x.findall('.//sec/p') if re.search(r'From May 2020 to May 2021|CFFSTS Trial', ''.join(p.itertext()))]
    out['verified_R5_Gu_reuse']={'path':str(args.gu_source),'sha256':sha(args.gu_source),'overlap_evidence_paragraphs':selected,
                               'purpose':'Verify institutional/time/IRB overlap only; prior all45 identity evaluation reused, not redone as new science.'}
(D/'eligibility-results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'assertions':'PASS','all_liver_rows':len(all_rows),'timepoint_category_sum':43,'EMC_authenticated':0,'numeric_EMC_pilot':False,'mesenchymal_label_count':10,'mesenchymal_lesions':32,'reported_sarcoma_count':11},indent=2))
