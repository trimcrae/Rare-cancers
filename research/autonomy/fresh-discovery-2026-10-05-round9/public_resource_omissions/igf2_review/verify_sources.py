"""Independent hash, original assay, and clinical roster verification; no retrieval."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

OWNER = Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round9/clinical_measurements/igf2_gate')
HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pdftext(path):
    return subprocess.run(['pdftotext', '-layout', '-', '-'], input=path.read_bytes(),
                          capture_output=True, check=True).stdout.decode()

def main():
    freeze = OWNER / 'FREEZE.json'
    assert sha(freeze) == '626911f76f2d821ed872bd80e8e6c9bf936929c91d043f542fb4327d44ce0c1c'
    science = json.loads(freeze.read_text())
    for row in science['files']:
        path = OWNER / row['path']
        assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    portability = json.loads((OWNER / 'PORTABILITY.json').read_text())
    for row in portability['cache_only']:
        path = OWNER / row['path']
        assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    assert len(science['files']) == 22 and len(portability['cache_only']) == 28
    original = OWNER / 'source-cache/expression2009.pdf'
    assert sha(original) == 'a35e61fb830ec381a88b315631703c2843615df4e5c11a02dd094a3f310d9c66'
    text = pdftext(original)
    assert re.search(r'Extraskeletal myxoid\s+8\s+0', text)
    assert re.search(r'Solitary fibrous tumor\s+25\s+20\s+80', text)
    assert re.search(r'Synovial sarcoma\s+80\s+34', text)
    assert re.search(r'Myxoid liposarcoma\s+33\s+13', text)
    assert 'ab9574' in text and 'both the prohormone form' in text
    assert 'A score of 0–5 was consid' in text
    assert 'as the higher interpretable score' in text
    source = OWNER / 'source-cache/NICTH145.xml'
    assert sha(source) == '92b26ad394916e394389ad7bdf40324e819913234dc517804ffa3c85345b123a'
    root = ET.parse(source).getroot()
    tables = root.findall('.//table-wrap')
    table2 = tables[1]
    rows = [[" ".join("".join(cell.itertext()).split()) for cell in row]
            for row in table2.findall('.//tbody/tr')]
    roster = [row for row in rows if len(row) == 3 and row[1].isdigit()]
    assert len(roster) == 13 and sum(int(row[1]) for row in roster) == 100
    assert next(row for row in roster if row[0] == 'Not known')[1] == '7'
    footnotes = " ".join("".join(table2.itertext()).split())
    assert 'One case was diagnosed based on imaging study.' in footnotes
    masses = next(row for row in tables[0].findall('.//tbody/tr')
                  if 'Mass lesion on CT' in ''.join(row.itertext()))
    ct = [" ".join("".join(cell.itertext()).split()) for cell in masses]
    assert '61.3' in ct and '31' in ct
    supplement = OWNER / 'source-cache/NICTH145-supp.pdf'
    assert sha(supplement) == '536ceac1fb313108bb4862a1edeef458d8f06407ff6f8e5b3ee11318894833e1'
    supp = pdftext(supplement)
    assert re.search(r'Solitary fibrous tumor\s+21', supp)
    assert re.search(r'Liposarcoma\s+2', supp)
    assert re.search(r'Phyllodes tumor\s+2', supp)
    assert '7.5 kDa' in supp and '15 kDa' in supp
    result = {'owner_original_freeze_sha256': sha(freeze),
              'owner_science_files_verified': len(science['files']),
              'owner_cache_inputs_verified': len(portability['cache_only']),
              'Steigen_source_scope': 'All eight author-EMC observations below overexpression cutoff; published relevant comparators/antibody/duplicate-core scoring verified. No absence or serum inference.',
              'NICTH100_roster': roster,
              'NICTH_CT_row': ct,
              'NICTH_source_scope': '100/45 groups, thirteen pathology rows sum100; unknown7 and imaging-only lung case retained; normal CT denominator31; postoperative25=21SFT+2LPS+2phyllodes subset. No molecular EMC or tissue/RNA transfer.',
              'method': 'Read-only originals, in-memory independent pdftotext; no downloads/raw copies/image inspection/gene values or processing-mechanism analysis.'}
    (HERE / 'SOURCE-VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Verified22 frozen owner files,28 cache sources, Steigen assay rows and complete100-case NICTH pathology roster; no expression stage.')

if __name__ == '__main__':
    main()
