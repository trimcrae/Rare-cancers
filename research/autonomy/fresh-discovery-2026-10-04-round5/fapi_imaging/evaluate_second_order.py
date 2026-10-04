import pathlib,json,xml.etree.ElementTree as E
D=pathlib.Path(__file__).resolve().parent;r=E.parse(D/'experience2024.xml').getroot();o={'metadata':{x.get('pub-id-type'):x.text for x in r.findall('.//article-id')},'tables':[],'supplements':[]}
for t in r.findall('.//table-wrap'):o['tables'].append({'id':t.get('id'),'text':' '.join(t.itertext()),'rows':[[' '.join(c.itertext()) for c in row] for row in t.findall('.//tr')]})
for t in r.findall('.//supplementary-material'):o['supplements'].append(E.tostring(t,encoding='unicode'))
(D/'second-order-evaluation.json').write_text(json.dumps(o,indent=2),encoding='utf-8')
print(o['metadata']);print(o['supplements'])
for t in o['tables']:
 if any(q in t['text'].lower() for q in ['sarcoma','histolo','character']):print(t['id'],t['text'][:14000])
