"""Verify the source text survives Word serialization and upload hashes match."""
from pathlib import Path
import hashlib, json, re, zipfile
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = Path(__file__).resolve().parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def normalize(s):
    return re.sub(r'\s+', ' ', s).strip()

def expected_text(path):
    text = path.read_text(encoding='utf-8')
    if text.startswith('---\n'):
        text = text.split('---\n', 2)[2]
    parts = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('```'):
            continue
        line = re.sub(r'^#{1,6}\s+', '', line)
        if line.startswith('|'):
            cells = [x.strip() for x in line.strip('|').split('|')]
            if all(re.fullmatch(r'[: -]+', x) for x in cells):
                continue
        else:
            cells = [line]
        for cell in cells:
            cell = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', cell)
            parts.append(normalize(cell.replace('**', '').replace('`', '')))
    return Counter(parts)

def word_text(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    paragraphs = []
    for p in root.findall('.//w:body//w:p', NS):
        paragraphs.append(''.join(t.text or '' for t in p.findall('.//w:t', NS)))
    return Counter(normalize(p) for p in paragraphs if normalize(p))

def main():
    results = []
    for source, output in [('manuscript.md', 'ASO-manuscript.docx'),
                           ('supplementary-methods.md', 'ASO-supplementary-methods.docx')]:
        expected, actual = expected_text(ROOT/source), word_text(ROOT/'submission'/output)
        if expected != actual:
            raise AssertionError((source, 'missing', expected-actual, 'extra', actual-expected))
        results.append({'source': source, 'output': output, 'paragraph_and_cell_count': sum(actual.values()), 'text_preserved': True, 'method': 'Exact normalized paragraph/cell content and multiplicity; main tables moved to end for CBC'})
    manifest = json.loads((ROOT/'submission/build-manifest.json').read_text())
    for row in manifest:
        p = ROOT/'submission'/row['file']
        assert p.stat().st_size == row['bytes'], row['file']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], row['file']
    print(json.dumps({'status': 'pass', 'text': results, 'upload_hashes_verified': len(manifest)}, indent=2))

if __name__ == '__main__':
    main()
