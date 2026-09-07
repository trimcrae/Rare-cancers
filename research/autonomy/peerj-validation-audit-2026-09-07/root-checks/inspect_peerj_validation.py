from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, zipfile, xml.etree.ElementTree as ET

root = Path('C:/Users/mcrae/.codex/worktrees/next-emc-paper-20260907/EMC-Research')
out = Path(__file__).resolve().parent/'peerj-validation-source'
out.mkdir(exist_ok=True)
src = root/'research/autonomy/emc-temposeq-source-2026-09-07'
sha = lambda b: hashlib.sha256(b).hexdigest()
xml = (src/'article.xml').read_bytes()
tree = ET.fromstring(xml)
terms = ['GSE6481', 'GSE24369', 'z-score', 'cross-platform', 'source code', 'scripts', 'Data Availability', 'data availability', 'github', 'H1FX']
rows = []
for tag in ['p', 'caption', 'ref']:
    for el in tree.iter(tag):
        s = ''.join(el.itertext())
        matches = [x for x in terms if x.lower() in s.lower()]
        if matches:
            rows.append({'tag':tag,'id':el.get('id'),'matches':matches,'text':s})
links = [{'text':''.join(el.itertext()),'href':el.get('{http://www.w3.org/1999/xlink}href')} for el in tree.iter('ext-link')]
members = []
with zipfile.ZipFile(src/'supplementary-files.zip') as z:
    for name in z.namelist():
        data=z.read(name)
        members.append({'name':name,'bytes':len(data),'sha256':sha(data)})
        if name.endswith('s008.png'):
            (out/'figure-s6.png').write_bytes(data)
        if name.endswith('.docx'):
            import io
            with zipfile.ZipFile(io.BytesIO(data)) as d:
                dt=ET.fromstring(d.read('word/document.xml'))
                ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                paragraphs=[''.join(p.itertext()) for p in dt.findall('.//w:p',ns)]
                (out/(Path(name).stem+'.txt')).write_text('\n'.join(paragraphs)+'\n',encoding='utf-8',newline='\n')
report={'utc':datetime.now(timezone.utc).isoformat(),'article':str(src/'article.xml'),'article_sha256':sha(xml),'archive_sha256':sha((src/'supplementary-files.zip').read_bytes()),'selected_elements':rows,'external_links':links,'members':members}
(out/'source-inspection.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
for row in rows:
    if any(x in row['matches'] for x in ['GSE6481','GSE24369','z-score','data availability','Data Availability','source code','scripts','github']):
        print(json.dumps(row,ensure_ascii=False))
print(json.dumps({'external_links':links,'members':[r['name'] for r in members]},ensure_ascii=False))
