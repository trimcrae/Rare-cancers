import pathlib,json,xml.etree.ElementTree as E
D=pathlib.Path(__file__).resolve().parent;r=E.parse(D/'dynamic2021.xml').getroot()
o={'tables':[{'id':x.get('id'),'text':' '.join(x.itertext()),'rows':[[' '.join(c.itertext()) for c in row] for row in x.findall('.//tr')]} for x in r.findall('.//table-wrap')], 'supplements':[E.tostring(x,encoding='unicode') for x in r.findall('.//supplementary-material')]}
(D/'citation-trail-evaluation.json').write_text(json.dumps(o,indent=2),encoding='utf-8')
for x in o['tables']:print(x['id'],x['text'][:14000])
print(o['supplements'])
