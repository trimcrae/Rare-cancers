"""Verify primary source bytes and header-only metadata; no expression analysis."""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pypdf import PdfReader

P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((P/'manifest.json').read_text())
for item in manifest['files']:
    assert sha(P/item['file'])==item['sha256']
    assert (P/item['file']).stat().st_size==item['bytes']
for rec in json.loads((P/'retrieval-log.json').read_text()):
    if 'sha256' in rec:
        assert sha(P/rec['file'])==rec['sha256'] and (P/rec['file']).stat().st_size==rec['bytes']
receipt=json.loads((P/'article-retrieval.json').read_text(encoding='utf-8-sig'))
assert sha(P/'article.xml')==receipt['sha256']
with zipfile.ZipFile(P/'supplementary-response.bin') as z:
    assert z.testzip() is None
    for n in ['CAC2-45-1760-s001.pdf','CAC2-45-1760-s002.xlsx']:
        assert z.read(n)==(P/n).read_bytes()
pdf=PdfReader(P/'CAC2-45-1760-s001.pdf')
assert len(pdf.pages)==39
pages={str(i):pdf.pages[i-1].extract_text() for i in [3,4,12,13]}
assert '1,041' in pages['3'] and '12 EpS' in pages['3']
assert '1,041' in pages['12'] and '10 million' in pages['13']
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
inventory=json.loads((P/'xlsx-inventory.json').read_text())
with zipfile.ZipFile(P/'CAC2-45-1760-s002.xlsx') as z:
    wb=ET.fromstring(z.read('xl/workbook.xml'));sheets=wb.find('s:sheets',ns)
    assert [s.get('name') for s in sheets]==[s['sheet'] for s in inventory]
    rel={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    shared=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        shared=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    for sheet, item in zip(sheets,inventory):
        target=rel[sheet.get('{'+ns['r']+'}id')]
        path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        doc=ET.fromstring(z.read(path));rows=doc.findall('s:sheetData/s:row',ns)
        assert max(int(r.get('r')) for r in rows)==item['rows']
        expected=item['header_rows'];observed=[[None]*item['columns'] for _ in expected]
        for row in rows:
            ri=int(row.get('r'))-1
            if ri>=len(expected):continue
            for c in row:
                letters=''.join(ch for ch in c.get('r') if ch.isalpha());ci=0
                for ch in letters:ci=26*ci+ord(ch)-64
                v=c.find('s:v',ns);inline=c.find('s:is',ns)
                value=None
                if c.get('t')=='s':value=shared[int(v.text)]
                elif c.get('t')=='inlineStr':value=''.join(inline.itertext())
                elif v is not None:value=float(v.text) if c.get('t') not in ['str','e'] else v.text
                observed[ri][ci-1]=value
        assert observed==expected,item['sheet']
root=json.loads((P/'github-contents.json').read_text())
main=json.loads((P/'github-main.json').read_text())
assert {r['path'] for r in root}=={'LICENSE','Main','README.md'}
assert len(main)==5 and all(r['type']=='file' for r in main)
assert not any('1I' in r['path'] for r in main)
class Reader(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)
r=Reader();r.feed((P/'ega-dac-response.html').read_text());ega=' '.join(' '.join(r.parts).split())
assert 'EGAD50000001419' in ega and '33' in ega and 'EERT' in ega
out={'status':'passed','manifest_sha256':sha(P/'manifest.json'),'frozen_files_checked':len(manifest['files']),
     'supplement_archive_members_identical':True,'pdf_pages':39,'methods_pages_checked':[3,4,12,13],
     'coordinator_visually_inspected_worker_renders':[3,12,13], 'xlsx_sheet_headers_independently_checked':len(inventory),
     'GitHub_root_entries':[r['path'] for r in root],'GitHub_Main_entries':[r['path'] for r in main],
     'EGA_DAC_dataset':'EGAD50000001419','external_EMC_asset_identified':False,
     'scope':'Source availability/provenance. Does not establish universal absence, independent validation, or publication readiness.'}
(P/'coordinator-verification.json').write_bytes((json.dumps(out,indent=2)+'\n').encode())
(P/'coordinator-methods-extracts.json').write_bytes((json.dumps({'pdf_pages':pages,'EGA_DAC_text':ega},indent=2)+'\n').encode())
print(json.dumps(out,indent=2))
