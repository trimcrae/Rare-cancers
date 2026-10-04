"""Read all original Davis DOCX text/tables in document order; no rendering."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,hashlib,re
D=Path(__file__).resolve().parent;p=D/'davis-supplement2.docx'
z=zipfile.ZipFile(p);root=E.fromstring(z.read('word/document.xml'))
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+N['w']+'}'
def text(el):return ''.join(t.text or '' for t in el.iter(W+'t'))
tables=[]
for i,t in enumerate(root.iter(W+'tbl')):
 rows=[]
 for row in t.findall('w:tr',N):rows.append([text(c)for c in row.findall('w:tc',N)])
 tables.append({'table_index':i,'rows':rows})
paras=[text(p)for p in root.iter(W+'p')]
out={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':'https://pmc-oa-opendata.s3.amazonaws.com/PMC5400622.1/oncotarget-08-21770-s002.docx','tables':tables,'paragraphs':paras,'note':'DOCX includes repeated headers and technical library QC; do not count table entries as independent patients. No image-only data transcribed by this script.'}
(D/'davis-extracted-tables.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([{'table':x['table_index'],'rows':len(x['rows']),'first':x['rows'][:2]}for x in tables],indent=2))
