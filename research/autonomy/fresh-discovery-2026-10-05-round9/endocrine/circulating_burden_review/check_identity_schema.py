#!/usr/bin/env python3
"""Zero-copy identity/assay-scope check; no case biomarker/outcome cells."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

def text(e):
    return ' '.join(''.join(e.itertext()).split()) if e is not None else ''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    root = Path(args.source_root)
    hashes = {
      'PMC11545914.xml': '0d4ebab476609c4e734bdc8f1472bc396987ef5da459e592d8a2174efc94ed15',
      'PMC12909327.xml': '72d41ff1df622e84aa5a72f928266546e0140715a22879bd8a16432faf1aac0f',
      'PMC12497659.xml': '54ccf7eaf295a5942e6d6254603334f5dbd9a684de7941eefdb21df5f7bb470c',
    }
    trees, inputs = {}, []
    for name, expected in hashes.items():
        path = root/name
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, name
        trees[name] = ET.parse(path).getroot()
        inputs.append({'name': name, 'bytes': path.stat().st_size, 'sha256': actual})
    table = next(t for t in trees['PMC11545914.xml'].findall('.//table-wrap')
                 if t.get('id') == 'jcm-13-06539-t006')
    diagnoses = []
    for row in table.findall('.//tbody/tr'):
        cells = list(row)
        # Never read grade, metastasis or ctDNA detection cells.
        diagnoses.append({'case': text(cells[0]), 'diagnosis': text(cells[1])})
    assert len(diagnoses) == 5
    assert not any('chondrosarcoma' in d['diagnosis'].lower() for d in diagnoses)
    table = next(t for t in trees['PMC12497659.xml'].findall('.//table-wrap')
                 if t.get('id') == 'T2')
    labels = []
    for row in table.findall('.//tbody/tr'):
        cells = list(row)
        # Only histology labels/counts, not survival, assay or outcome cells.
        labels.append({'subtype': text(cells[0]), 'source_count': text(cells[1])})
    assert next(x for x in labels if x['subtype'] == 'others')['source_count'] == '36 (36)'
    letter = trees['PMC12909327.xml']
    assert letter.get('article-type') == 'letter'
    assert len(letter.findall('./body/p')) == 7
    docx_path = root/'TF2026-actual-published-supplement.docx'
    expected_docx = '872eb10c2e7a59e68720a121010603e8787cd5c1d40bdba9fc49acee41b43729'
    assert hashlib.sha256(docx_path.read_bytes()).hexdigest() == expected_docx
    wns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(docx_path) as z:
        document = ET.fromstring(z.read('word/document.xml'))
    # Only the first table's clinical histology label and count cells are used.
    # Table 2 statistical results and all TF/case-outcome fields remain closed.
    expected_counts = {'Leiomyosarcoma': 34, 'Liposarcoma': 29,
                       'Undifferentiated pleomorphic sarcoma': 21,
                       'Synovial sarcoma': 15, 'Angiosarcoma': 13, 'Others': 80}
    actual_counts = {}
    first_table = document.findall('.//w:tbl', wns)[0]
    for row in first_table.findall('w:tr', wns):
        cells = row.findall('w:tc', wns)
        if len(cells) < 2: continue
        label = ''.join(n.text or '' for n in cells[0].findall('.//w:t', wns)).strip()
        if label not in expected_counts: continue
        value = ''.join(n.text or '' for n in cells[1].findall('.//w:t', wns))
        actual_counts[label] = int(re.sub(r'\s+', '', value.split('(')[0]))
    assert actual_counts == expected_counts
    assert sum(actual_counts.values()) == 192
    inputs.append({'name': docx_path.name, 'bytes': docx_path.stat().st_size,
                   'sha256': expected_docx})
    evidence = []
    exact_quotes = {
        'PMC11545914.xml': ['The concentration of extracted cfDNA was determined via RT-qPCR using an 81 bp amplicon of the EIF2C1 gene on chromosome 1 and a dilution series of placenta DNA.',
                          'Prior to testing the cfDNA samples, sensitivity assays were conducted using tumor and blood DNA to determine the limits of detection of mutant DNA for each case.'],
        'PMC12497659.xml': ['The levels of circulating biomarkers were taken at the time of diagnosis of first pleural involvement.',
                          'The raw data supporting the conclusions of this article will be made available by the authors, without undue reservation.'],
        'PMC12909327.xml': ['The datasets generated and/or analysed during the current study are available from the corresponding author on reasonable request.'],
    }
    for name, quotes in exact_quotes.items():
        source_text = text(trees[name])
        for quote in quotes:
            assert quote in source_text, (name, quote)
            evidence.append({'source': name, 'quote': quote})
    result = {'scope': 'Identity/assay provenance only, no case biomarker values or outcome cells.',
              'inputs': inputs, 'management2024_five_assayed_diagnoses': diagnoses,
              'pleural2025_histology_labels_and_counts': labels,
              'new_TF2026_letter': {'article_type': 'letter', 'direct_main_body_paragraphs': 7,
                  'interpretation': 'Short primary research letter with direct main-text paragraphs; detailed methods and identity roster in supplementary material. Section-only absence is not missing main text.'},
              'new_TF2026_supplement': {'histology_counts': actual_counts,
                  'total_source_cohort': 192, 'unresolved_other': 80,
                  'unit': 'Aggregate diagnostic strata, not individual donor IDs/serial draws.',
                  'Table2_or_biomarker_values_accessed': False},
              'literal_primary_method_access_excerpts': evidence,
              'EMC_new_serial_case_values_accessed': False}
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'source_inputs': len(inputs), 'management_diagnoses': len(diagnoses),
                      'pleural_unresolved_other': 36, 'literal_quotes': len(evidence), 'errors': 0,
                      'case_analyte_or_outcome_cells_accessed': False}))

if __name__ == '__main__': main()
