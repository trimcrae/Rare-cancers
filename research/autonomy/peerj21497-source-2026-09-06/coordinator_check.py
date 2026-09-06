"""Independent original ZIP/XML structural checks, with no expression contrasts."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
EXPECTED = {'CHRNA6': 3508, 'CD276': 2216, 'SSTR2': 8058, 'FAP': 6166,
            'CD248': 6193, 'CSPG4': 7155, 'MSLN': 3270}
ABSENT = ('PRAME', 'L1CAM', 'GPC3', 'ALPP', 'CDH17')


def run():
    manifest = json.loads((HERE / 'manifest.json').read_bytes())
    for item in manifest['files']:
        raw = (HERE / item['path']).read_bytes()
        assert len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256']
    name = 'peerj-14-21497-s009.xlsx'
    source = (HERE / name).read_bytes()
    article = (HERE / 'article.xml').read_text(encoding='utf-8')
    block = article[article.index('<supplementary-material id="supp-9"'):]
    block = block[:block.index('</supplementary-material>')]
    md5 = re.search(r'<\?suppdata-md5 ([a-f0-9]+)\?>', block).group(1)
    size = int(re.search(r'<\?suppdata-size (\d+)\?>', block).group(1))
    assert hashlib.md5(source).hexdigest() == md5 and len(source) == size == 1423709
    with zipfile.ZipFile(HERE / 'supplementaryFiles.response') as z:
        names = [n for n in z.namelist() if n.split('/')[-1] == name]
        assert len(names) == 1 and z.read(names[0]) == source
    with zipfile.ZipFile(HERE / name) as z:
        workbook = ET.fromstring(z.read('xl/workbook.xml'))
        sheets = workbook.find('s:sheets', NS)
        assert len(sheets) == 1 and sheets[0].attrib['name'] == 'EMC_Gene-expression_Log2CPM'
        shared = [''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = sheet.find('s:sheetData', NS)
        assert len(rows) == 9501
        cells = {}; kinds = {}
        for row in rows:
            assert len(row) == 13
            for cell in row:
                address = cell.attrib['r']
                assert address not in cells and cell.find('s:f', NS) is None
                value = cell.find('s:v', NS).text
                kind = cell.attrib.get('t', 'n')
                assert kind in ('s', 'n')
                cells[address] = shared[int(value)] if kind == 's' else value
                kinds[address] = kind
        assert len(cells) == 123513
    expected_samples = ['Si01', 'Si02', 'Si05', 'Si09', 'Si10', 'Si14', 'Si15',
                        'Si16', 'Si17', 'Si19', 'Si20', 'Si22']
    assert cells['A1'] == 'symbol'
    assert [cells[f'{col}1'] for col in 'BCDEFGHIJKLM'] == expected_samples
    string_labels = {cells[f'A{row}']: row for row in range(2, 9502) if kinds[f'A{row}'] == 's'}
    numeric_labels = {f'A{row}': cells[f'A{row}'] for row in range(2, 9502) if kinds[f'A{row}'] == 'n'}
    assert len(string_labels) == 9494 and len(numeric_labels) == 6
    assert all(string_labels[target] == row for target, row in EXPECTED.items())
    assert not any(target in string_labels for target in ABSENT)
    negative = 0
    for row in range(2, 9502):
        for column in 'BCDEFGHIJKLM':
            address = f'{column}{row}'
            assert kinds[address] == 'n'
            value = Decimal(cells[address])
            assert value.is_finite() and value != value.to_integral_value()
            negative += value < 0
    assert negative == 2894
    inventory = json.loads((HERE / 'workbook-inventory.json').read_bytes())
    preserved_values = 0
    for target in inventory['panel']:
        for row in target['rows']:
            assert cells[row['symbol_cell']] == target['target']
            for item in row['samples']:
                assert cells[item['cell']] == item['source_numeric_string']
                assert cells[re.sub(r'\d+$', '1', item['cell'])] == item['sample']
                preserved_values += 1
    assert preserved_values == 84
    return {'status': 'passed', 'worker_manifest_files': len(manifest['files']),
            'archive_member_and_primary_JATS_integrity': True, 'single_sheet': True,
            'feature_rows': 9500, 'sample_columns': 12, 'nonempty_source_cells_checked': len(cells),
            'numeric_measurement_cells': 114000, 'negative_transformed_cells': negative,
            'distinct_string_feature_labels': 9494, 'unresolved_numeric_labels': numeric_labels,
            'fixed_panel_rows_present': EXPECTED, 'fixed_panel_rows_absent_reason_unknown': ABSENT,
            'source_panel_values_verified_without_contrasts': preserved_values,
            'scope': 'Original source integrity, identifiers, shape and supplied value preservation; no detection threshold, expression contrast, patient-level effect or therapeutic claim.'}


if __name__ == '__main__':
    result = run()
    (HERE / 'coordinator-check-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
