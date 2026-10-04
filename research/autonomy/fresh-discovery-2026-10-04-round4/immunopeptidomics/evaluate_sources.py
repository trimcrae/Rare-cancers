import json,pathlib,re,xml.etree.ElementTree as E
from pypdf import PdfReader
D=pathlib.Path(__file__).resolve().parent
def txt(n): return ' '.join(''.join(n.itertext()).split())
out={}
for name in ['chs2026','pediatric2021','pleural2022']:
 r=E.parse(D/(name+'.xml')).getroot()
 out[name]={'doi':[txt(x) for x in r.findall('.//article-id') if x.get('pub-id-type')=='doi'],
 'paragraphs':[txt(x) for x in r.findall('.//p') if re.search(r'cell line|patient|sample|HLA|mass spectrom|PRIDE|PXD|chondro|sarcoma',txt(x),re.I)],
 'tables':[txt(x) for x in r.findall('.//table-wrap')],
 'supplements':[{'text':txt(x),'links':[dict(y.attrib) for y in x.iter() if any('href' in k for k in y.attrib)]} for x in r.findall('.//supplementary-material')]}
pdf=[{'page':i+1,'text':p.extract_text()} for i,p in enumerate(PdfReader(D/'jci2023-supp.pdf').pages)]
(D/'jci2023-supp-pages.json').write_text(json.dumps(pdf,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'source-extracts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for k,v in out.items():
 print('\nSOURCE',k,v['doi'])
 for p in v['paragraphs']:
  if re.search(r'cell lines? (?:were|was|used|consist)|JJ012|CH2879|U2OS|PXD|patients with|patient cohort|consecutiv',p,re.I): print(p[:9000])
 print('SUPPLEMENTS',json.dumps(v['supplements']))
for p in pdf:
 if re.search(r'extraskeletal|myxoid',p['text'],re.I): print('JCIpage',p['page'],p['text'])
