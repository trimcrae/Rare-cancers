from pathlib import Path
import xml.etree.ElementTree as E,zipfile,json,re,html
B=Path(__file__).resolve().parent; ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};out={}
for f in B.glob('*.docx'):
    with zipfile.ZipFile(f) as z:r=E.fromstring(z.read('word/document.xml'))
    def tx(x):return ' '.join(t.text or '' for t in x.findall('.//w:t',ns))
    data={'paragraphs':[tx(p) for p in r.findall('.//w:p',ns)],'tables':[[[tx(c) for c in row.findall('w:tc',ns)] for row in table.findall('w:tr',ns)] for table in r.findall('.//w:tbl',ns)]}
    out[f.name]=data;print(f.name)
    if 'Methods' in f.name:
        for p in data['paragraphs']:
            if re.search('sensitivity|patient 3|VWDE|droplet|copies|mutant',p,re.I): print(p)
        for table in data['tables']:
            print('HEAD',table[:2])
            for row in table:
                if row[0].strip() in ['3','003'] or any(re.search('VWDE|ExMC',x) for x in row):print('EMC',row)
    else:print('\n'.join(data['paragraphs']))
(B/'supplement-extracts.json').write_text(json.dumps(out,indent=2),encoding='utf8')
f=B/'czachor2025.html';tx=html.unescape(re.sub('<[^>]+>',' ',f.read_text(encoding='utf8')));tx=' '.join(tx.split());(B/'czachor2025-text.txt').write_text(tx,encoding='utf8');print('CZACHOR',tx[tx.find('e23559'):tx.find('Fingerprint')])
for f in [B/'eastley2018.xml',B/'demoret2019.xml',B/'review-liquid2025.xml']:
    r=E.parse(f).getroot();tx=lambda x:' '.join(' '.join(x.itertext()).split());print('\n',f.name)
    for t in r.findall('.//table-wrap'):print(tx(t))
    if 'review' in f.name:
        for ref in r.findall('.//ref'):print(tx(ref))
