import json,pathlib,zipfile,xml.etree.ElementTree as E
D=pathlib.Path(__file__).resolve().parent
out={}; ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for p in sorted(D.glob('ferdinandus2022-ts*.docx')):
 with zipfile.ZipFile(p) as z:r=E.fromstring(z.read('word/document.xml'))
 rows=[]
 for row in r.findall('.//w:tr',ns):rows.append([' '.join(x.text or '' for x in c.findall('.//w:t',ns)) for c in row.findall('w:tc',ns)])
 text=' '.join(x.text or '' for x in r.findall('.//w:t',ns));out[p.name]={'rows':rows,'text':text}
 print(p.name,rows if 'ts1' in p.name else text[:700])
(D/'supplement-evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for name in ['dynamic2021-metadata.json','kratochwil2019-metadata.json']:
 j=json.loads((D/name).read_text());print(name,j.get('resultList'))
