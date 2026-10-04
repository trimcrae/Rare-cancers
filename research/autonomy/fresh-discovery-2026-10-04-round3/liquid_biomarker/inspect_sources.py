from pathlib import Path
import xml.etree.ElementTree as ET, json, re
B=Path(__file__).resolve().parent
out={}
for file in B.glob('*.xml'):
    root=ET.parse(file).getroot(); text=lambda x:' '.join(' '.join(x.itertext()).split())
    data={'title':[text(x) for x in root.findall('.//article-title')][:1], 'tables':[], 'supplements':[], 'sections':[]}
    for t in root.findall('.//table-wrap'): data['tables'].append({'id':t.get('id'),'text':text(t),'rows':[[text(c) for c in tr] for tr in t.findall('.//tr')]})
    for s in root.findall('.//supplementary-material'): data['supplements'].append({'text':text(s),'links':[x.attrib for x in s.iter() if 'href' in str(x.attrib)]})
    for s in root.findall('.//body/sec'):
        data['sections'].append({'title':text(s.find('title')) if s.find('title') is not None else '', 'text':text(s)})
    data['refs']=[text(x) for x in root.findall('.//ref')]
    out[file.name]=data
    print(file.name, data['title'], 'supplements',data['supplements'])
    for t in data['tables']:
        for row in t['rows']:
            if any(re.search(r'ExMC|extraskeletal|M2\b',c,re.I) for c in row):print(t['id'],row)
    for s in data['sections']:
        if file.name in ['structural2020.xml','omori2022.xml']:print(s['text'])
(B/'source_extracts.json').write_text(json.dumps(out,indent=2),encoding='utf8')
