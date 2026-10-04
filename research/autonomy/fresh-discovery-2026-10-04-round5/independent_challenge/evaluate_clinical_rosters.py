"""Reproduce clinical identity checks only; no SUV or treatment-effect analysis.

Sources are the previously retrieved primary files. Review of the interrupted
tissue sources is deliberately not resumed. No network access.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
from collections import Counter
import hashlib, json, datetime
from pypdf import PdfReader
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent
OWNER = Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round5/fapi_imaging')

def text(node):
    return ' '.join(' '.join(node.itertext()).split())

def source(path):
    b = path.read_bytes()
    return {'path': str(path), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def rows(path, table_id):
    return ET.parse(path).getroot().find('.//table-wrap[@id="' + table_id + '"]').findall('.//tbody/tr')

# Gu Table 1 has 45 individually numbered patient rows. Do not retain scan
# outcomes as evidence about EMC when no patient is labelled EMC.
gu = []
for tr in rows(ROOT/'gu2022.xml', 'Tab1'):
    v = [text(c) for c in tr]
    if v and v[0].isdigit():
        gu.append(dict(zip(['id', 'sex', 'age', 'histology', 'site', 'grade'], v[:6])))
assert len(gu) == 45
assert [int(x['id']) for x in gu] == list(range(1, 46))
assert all(not any(s in x['histology'].lower() for s in ['chondrosarcoma', 'extraskeletal', 'nr4a3']) for x in gu)

# Zhang preprint Table 1: retain its complete category totals and version;
# this is not an individual-ID roster and is not the final journal table.
zhang_pages = json.loads((ROOT/'zhang-preprint-eligibility-pages.json').read_text())
table_text = next(x['text'] for x in zhang_pages if x['page'] == 13)
zhang_labels = [('Solitary \x00brous tumor', 13), ('Desmoid tumor', 2),
    ('Dermato\x00brosarcoma protuberans', 1), ('Malignant solitary \x00brous tumor', 2),
    ('Myxo\x00brosarcoma', 1), ('High-grade \x00brosarcoma', 1)]
for label, n in zhang_labels:
    assert label+' '+str(n) in table_text
assert sum(n for _, n in zhang_labels) == 20

# Koerber Table 2 uses rowspans. Decode its first two columns explicitly;
# never mistake the second liposarcoma row for a new histology.
koerber = []
carry = None
for tr in rows(OWNER/'koerber2021.xml', 'Tab2'):
    cells = list(tr)
    if carry is not None:
        diagnosis, n = carry, text(cells[0])
        carry = None
    else:
        diagnosis, n = text(cells[0]), text(cells[1])
        if cells[0].get('rowspan') == '2':
            carry = diagnosis
    if diagnosis:
        koerber.append({'diagnosis': diagnosis, 'n': int(n)})
assert sum(x['n'] for x in koerber) == 15
assert sum(x['n'] for x in koerber if x['diagnosis'] == 'Sarcoma NOS') == 1

# Generic STS rows remain unresolved, irrespective of measured lesion counts.
novruzov = []
for tr in rows(OWNER/'novruzov2026.xml', 'Tab1'):
    v = [text(c) for c in tr]
    if v and v[0].startswith('STS-'):
        novruzov.append({'id': v[0], 'age': v[1], 'sex': v[2]})
assert len(novruzov) == 6
novruzov_supp = PdfReader(OWNER/'novruzov2026-supp.pdf')
assert len(novruzov_supp.pages) == 1
supp_text = novruzov_supp.pages[0].extract_text()
assert 'Acquisition Protocol' in supp_text
assert 'histolog' not in supp_text.lower()

ferdinandus = []
for tr in rows(OWNER/'ferdinandus2022.xml', 'tbl1'):
    v = [text(c) for c in tr]
    if v and v[0] in ['Sarcoma', 'Pancreatic cancer', 'Prostate cancer', 'Gastric cancer']:
        ferdinandus.append(v)

# Newly retained TS1 closes the generic main-table roster, while two ambiguous
# diagnoses remain. Store identity fields only, not treatment/uptake values.
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(OWNER/'ferdinandus2022-ts1.docx') as z:
    word = ET.fromstring(z.read('word/document.xml'))
ferdinandus_individual = []
for tr in word.findall('.//w:tr', ns)[1:]:
    v = [' '.join(t.text or '' for t in c.findall('.//w:t', ns)) for c in tr.findall('w:tc', ns)]
    ferdinandus_individual.append(dict(zip(['id', 'age', 'sex', 'entity', 'histopathology_and_location'], v[:5])))
assert len(ferdinandus_individual) == 21
assert sum(x['entity'] == 'Sarcoma' for x in ferdinandus_individual) == 16
ferdinandus_conventional = []
for p in ET.parse(OWNER/'ferdinandus2022.xml').getroot().findall('.//p'):
    if 'conventional chondrosarcoma' in text(p).lower():
        ferdinandus_conventional.append(text(p))
assert len(ferdinandus_conventional) == 1

dynamic = []
for tr in rows(OWNER/'dynamic2021.xml', 'T1'):
    v = [text(c) for c in tr]
    dynamic.append({'id': v[0], 'pathology': v[-1]})
assert len(dynamic) == 6
assert Counter(x['pathology'] for x in dynamic) == {'Lung Ca.': 3, 'No tumor': 3}

experience = []
in_neoplasm = False
for tr in rows(OWNER/'experience2024.xml', 'diagnostics-15-00218-t001'):
    v = [text(c) for c in tr]
    if v[0] == 'Primary Neoplasm':
        in_neoplasm = True
    elif in_neoplasm and v[0] == 'Cancer Staging':
        break
    elif in_neoplasm:
        experience.append({'diagnosis': v[0], 'n': int(v[1].split(',')[0])})
assert len(experience) == 12
assert sum(x['n'] for x in experience) == 48
assert all('sarcoma' not in x['diagnosis'].lower() for x in experience)

metadata = {}
for fname in ['yang2022-pubmed.xml', 'liu2026-pubmed.json', 'zhang2022-pubmed.json']:
    record = json.loads((ROOT/fname).read_text())['resultList']['result'][0]
    metadata[fname] = {k: record.get(k) for k in ['id', 'doi', 'title', 'isOpenAccess', 'inPMC', 'inEPMC', 'hasSuppl', 'fullTextUrlList']}

reviewed = [ROOT/x for x in ['gu2022.xml', 'zhang2022-preprint.pdf',
    'zhang-preprint-eligibility-pages.json', 'yang2022-pubmed.xml',
    'liu2026-pubmed.json', 'zhang2022-pubmed.json']]
reviewed += [OWNER/x for x in ['koerber2021.xml', 'novruzov2026.xml',
    'novruzov2026-supp.pdf', 'ferdinandus2022.xml', 'ferdinandus2022-ts1.docx',
    'dynamic2021.xml', 'experience2024.xml', 'PILOT-IF-ELIGIBLE.txt']]
out = {
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'analysis': 'Clinical identity and source-availability checks; no quantitative EMC pilot justified.',
    'sources': [source(p) for p in reviewed],
    'gu': {'patients': gu, 'histology_counts': dict(Counter(x['histology'] for x in gu)),
           'decision': 'All 45 source-labelled rows evaluated; no labelled EMC. Not a global absence claim.'},
    'zhang': {'version': 'Research Square rs-1463611/v1, Table 1 p13',
              'histology_counts': {k.replace('\x00', 'fi'): n for k, n in zhang_labels},
              'decision': 'Complete 20-patient category totals contain no EMC label; generic high-grade fibrosarcoma1 identity remains unresolved. Final journal table not recovered, no individual-ID roster.'},
    'koerber': {'table2_histology_rows': koerber,
                'decision': '15 accounted by Table2, including one unresolved sarcoma NOS; Table1 omits one myxofibrosarcoma. No explicit EMC label.'},
    'novruzov': {'generic_sts_rows': novruzov, 'supplement_text': supp_text,
                 'decision': 'All six STS labels unresolved subtype; sole supplement is acquisition protocol, not histology crosswalk.'},
    'ferdinandus': {'table1_tumor_entity_rows': ferdinandus,
                    'TS1_all21_identity_rows': ferdinandus_individual,
                    'conventional_chondrosarcoma_primary_context': ferdinandus_conventional,
                    'decision': 'All 21 source identities reviewed, 16 sarcomas. Sole chondrosarcoma described as conventional in main text; fibrosarcoma case2 and spindle-cell sarcoma case11 remain generic. No explicit EMC label.'},
    'dynamic2021': {'all6_identities': dynamic,
                    'decision': 'All six subjects accounted, three lung cancers and three no-tumor; no EMC. Same registration as Zhang does not make them its sarcoma patients.'},
    'experience2025': {'all48_histology_totals': experience,
                       'decision': 'Actual article is Diagnostics2025 DOI10.3390/diagnostics15020218, despite retained filename. Twelve named non-sarcoma categories total48; not an individual-ID roster.'},
    'metadata': metadata,
    'limits': ['No absence of EMC inferred from unavailable rosters.',
        'Nasal chondrosarcoma subtype unresolved; site does not reclassify it.',
        'No cross-series donor independence established; trial/institution overlap must remain explicit.',
        'Interrupted tissue review not resumed or certified by this script.']
}
(ROOT/'clinical-eligibility-evaluation.json').write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps({'Gu_rows': len(gu), 'Zhang_histology_total': sum(n for _, n in zhang_labels),
                  'Koerber_total': sum(x['n'] for x in koerber), 'Novruzov_unresolved_STS': len(novruzov),
                  'source_hashes': len(reviewed)}, indent=2))
