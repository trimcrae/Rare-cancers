"""Independent original-XLSX/HTML specimen link and field-semantics audit."""
from pathlib import Path
from zipfile import ZipFile
from html.parser import HTMLParser
import hashlib
import json
import re
import xml.etree.ElementTree as E

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent/'atlas-primary-provenance-2026-09-06'

class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def clean(path):
    parser = Reader()
    parser.feed(path.read_text(encoding='utf-8'))
    return ' '.join(' '.join(parser.parts).split())

ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with ZipFile(PRIOR/'2017-controls-table.xlsx') as archive:
    shared = [''.join(item.itertext()) for item in E.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si', ns)]
    sheet = E.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    rows = {}
    for row in sheet.findall('.//s:row', ns):
        cells = {}
        for cell in row.findall('s:c', ns):
            value = cell.find('s:v', ns)
            if value is not None:
                cells[re.sub(r'\d', '', cell.attrib['r'])] = shared[int(value.text)] if cell.attrib.get('t') == 's' else value.text
        if cells.get('A') in [str(i) for i in range(46, 52)]:
            rows[cells['A']] = cells
expected = {46: (3, '71/M', 'Buttock'), 47: (5, '35/F', 'Knee'), 48: (4, '40/M', 'Groin'), 49: (7, '48/F', 'Groin')}
assert len(rows) == 6
for new, (old, age, site) in expected.items():
    row = rows[str(new)]
    assert row['U'] == f'9736, Case {old}' and row['P'] == age and row['Q'] == site
    text = clean(HERE/f'mitelman-case{old}.html')
    assert f'Ref No: 9736 Case No: {old} Inv No: 1' in text
    assert f'Age {age.split("/")[0]} Country Sweden' in text
for number in ('50', '51'):
    assert 'U' not in rows[number]
helptext = clean(HERE/'mitelman-help.html')
for phrase in ('Case origin when stated in publication; otherwise, in general the residence of corresponding author.',
               'Tissue used for cytogenetic investigation.',
               'each consecutive investigation within a case or for a metastatic lesion at a different location.'):
    assert phrase in helptext
for inv, filename in [(1, 'mitelman-case7.html'), (2, 'mitelman-case7-inv2.html')]:
    assert f'Ref No: 9736 Case No: 7 Inv No: {inv}' in clean(HERE/filename)
records = json.loads((HERE/'retrievals.json').read_text())
for record in records:
    body = (HERE/record['file']).read_bytes()
    assert len(body) == record['bytes'] and hashlib.sha256(body).hexdigest() == record['sha256']
print(json.dumps(dict(passed=True, primary_xlsx_cases=6, explicit_case_links=4,
                     case7_investigations=2, field_definitions=3, original_responses=len(records),
                     scope='Original XML/HTML checks; no patient independence or expression claim.')))
