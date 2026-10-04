from pathlib import Path
import json,hashlib,re,xml.etree.ElementTree as E
import openpyxl
P=Path(__file__).resolve().parent
w=openpyxl.load_workbook(P/'zullow2022-tableS1.xlsx',data_only=True)
out={'source_doi':'10.1016/j.molcel.2022.03.019','source_url':'https://ars.els-cdn.com/content/image/1-s2.0-S109727652200257X-mmc2.xlsx','sha256':hashlib.sha256((P/'zullow2022-tableS1.xlsx').read_bytes()).hexdigest(),'sheets':{}}
for s in w:
    rows=[{'row':i,'values':list(r)} for i,r in enumerate(s.values,1) if any(v is not None for v in r)]
    out['sheets'][s.title]=rows
(P/'zullow-tableS1-evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Zullow all specimen rows',json.dumps(out,ensure_ascii=False))
x=E.fromstring((P/'myoepithelial2025.xml').read_bytes())
data=[]
for e in x.iter():
    if e.tag in ('p','table-wrap','supplementary-material','ext-link'):
        t=' '.join(e.itertext())
        if any(k in t.lower() for k in ('chondrosarcoma','emcs','gse','nr4a3')):data.append({'tag':e.tag,'text':t,'attrib':e.attrib})
(P/'myoepithelial2025-eligible-evaluation.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print('Myoepithelial eligible',json.dumps(data,ensure_ascii=False)[:11000])

