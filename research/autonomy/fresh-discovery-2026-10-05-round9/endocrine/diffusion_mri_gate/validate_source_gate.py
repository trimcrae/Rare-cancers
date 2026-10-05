#!/usr/bin/env python3
"""Read-only source/schema validation. Never access case ADC/texture cells."""
import argparse, collections, hashlib, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def schema_only(path):
    with zipfile.ZipFile(path) as z:
        shared = ET.fromstring(z.read('xl/sharedStrings.xml'))
        strings = [''.join(n.itertext()) for n in shared.findall('s:si', NS)]
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    def value(c):
        v = c.find('s:v', NS)
        if v is None: return None
        return strings[int(v.text)] if c.get('t') == 's' else v.text
    headers, rows = [], []
    for row in sheet.findall('s:sheetData/s:row', NS):
        if row.get('r') == '1':
            headers = [value(c) for c in row.findall('s:c', NS)]
        else:
            # Deliberately select only ID and benign/malignant columns. No age,
            # sex, volume, ADC, texture or statistical result cell is parsed.
            selected = {re.sub(r'\d+', '', c.get('r')): value(c)
                        for c in row.findall('s:c', NS)
                        if re.sub(r'\d+', '', c.get('r')) in ('A', 'B')}
            if selected.get('A'): rows.append(selected)
    assert len(rows) == 40
    assert len({r['A'] for r in rows}) == 40
    assert collections.Counter(r['B'] for r in rows) == {'benign': 23, 'malignant': 17}
    assert not any(re.search('extraskeletal|chondrosarcoma|liposarcoma|myxofibrosarcoma|histolog|subtype', s, re.I) for s in strings)
    return {'headers': headers, 'rows': len(rows), 'label_counts': dict(collections.Counter(r['B'] for r in rows)), 'histologic_subtype_column_or_string': False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    portability = json.loads((ROOT/'PORTABILITY.json').read_text())
    errors, checked, unavailable = [], [], []
    for rec in portability['cache_only_inputs']:
        path = Path(rec['local_path'])
        if not path.exists():
            unavailable.append(rec['local_path']); continue
        if path.stat().st_size != rec['bytes'] or digest(path) != rec['sha256']:
            errors.append('cache binding mismatch: '+str(path))
        checked.append(str(path))
    data = json.loads((ROOT/'FOCUSED-OBSERVATIONS.json').read_text())
    for rec in data['exact_source_excerpts']:
        r = ET.parse(ROOT/'raw-cache'/rec['source']).getroot()
        body = r.find('body')
        text = ' '.join(''.join(body.itertext()).split())
        if rec['excerpt'] not in text:
            errors.append('source excerpt mismatch: '+rec['source'])
    external = Path(data['S1']['cache_path'])
    schema = schema_only(external) if external.exists() else None
    # Exact source case identifiers cannot be assigned from same age/sex,
    # numeric examples or figure file names. Source main text has no A1-A40 IDs.
    primary = Path(data['S1']['primary_xml_path'])
    raw_ids = []
    if primary.exists():
        body = ET.parse(primary).getroot().find('body')
        text = ' '.join(''.join(body.itertext()).split())
        raw_ids = sorted(set(re.findall(r'\bA(?:[1-9]|[1-3][0-9]|40)\b', text)))
        if raw_ids: errors.append('explicit primary IDs require a renewed linkage gate')
    result = {'schema': 'emc-diffusion-source-gate-validation/1', 'cache_inputs_checked': len(checked),
              'missing_local_cache_inputs': unavailable, 'source_excerpt_count': len(data['exact_source_excerpts']),
              'S1_schema_only': schema, 'main_body_case_ids': raw_ids, 'errors': errors,
              'case_ADC_or_texture_cells_accessed': False, 'numerical_stage_launched': False,
              'scope': 'Source byte bindings, focused literal excerpts and table identity/schema only; no independent clinical result reproduction.'}
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    if errors: raise SystemExit(1)

if __name__ == '__main__': main()
