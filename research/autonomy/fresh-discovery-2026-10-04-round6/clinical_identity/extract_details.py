import pathlib,json,re,html,zipfile,xml.etree.ElementTree as E
from pypdf import PdfReader
D=pathlib.Path(__file__).resolve().parent
pages=[p.extract_text() for p in PdfReader(D/'interobserver2023.pdf').pages]
(D/'interobserver-pages.json').write_text(json.dumps(pages,indent=2),encoding='utf-8')
print('INTEROBSERVER'); print('\n'.join(pages[:3]))
h=(D/'liver2026-table1.html').read_text(encoding='utf-8')
tables=[html.unescape(re.sub('<[^>]+>',' | ',t)) for t in re.findall(r'<table\b.*?</table>',h,re.S)]
print('LIVER TABLES');print(json.dumps(tables,indent=2))
with zipfile.ZipFile(D/'liver2026-supp.docx') as z:x=E.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
ps=[''.join(p.itertext()) for p in []]
text=[''.join(p.itertext()) for p in []]
paras=[''.join(p.itertext()) for p in []]
supp=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in x.findall('.//w:p',ns)]
rows=[[''.join(t.text or '' for t in c.findall('.//w:t',ns)) for c in row.findall('w:tc',ns)] for row in x.findall('.//w:tr',ns)]
print('LIVER SUPP');print(json.dumps({'paragraphs':supp,'rows':rows},indent=2))
(D/'liver-extracted.json').write_text(json.dumps({'tables':tables,'supp_paragraphs':supp,'supp_rows':rows},indent=2),encoding='utf-8')
