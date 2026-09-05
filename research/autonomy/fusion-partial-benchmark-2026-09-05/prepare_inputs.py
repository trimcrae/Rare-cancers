from pathlib import Path
import shutil,hashlib,json,xml.etree.ElementTree as ET
import pypdfium2 as pdfium

out=Path('research/autonomy/fusion-partial-benchmark-2026-09-05'); src=Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/fusion-partial-inputs-2026-09-05')
(out/'inputs').mkdir(exist_ok=True); (out/'inspections').mkdir(exist_ok=True)
m=json.loads((src/'input-manifest.json').read_text())
for r in m['sources']+m['members']:
 b=(src/r['file']).read_bytes(); assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']; (out/'inputs'/r['file']).write_bytes(b)
shutil.copyfile(src/'input-manifest.json',out/'inputs/input-manifest.json')
x=ET.parse(out/'inputs/lee2023.xml')
(out/'inspections/article-text.txt').write_text('\n'.join(''.join(e.itertext()) for e in x.findall('.//sec'))+'\nPERMISSIONS\n'+ '\n'.join(''.join(e.itertext()) for e in x.findall('.//permissions')),encoding='utf-8')
for f in (out/'inputs').glob('*.pdf'):
 d=pdfium.PdfDocument(f); (out/'inspections'/(f.stem+'.txt')).write_text('\n'.join(f'PAGE {i+1}\n'+d[i].get_textpage().get_text_range() for i in range(len(d))),encoding='utf-8')
 print(f.name,len(d))
 d=pdfium.PdfDocument(f)
 for i in range(len(d)): d[i].render(scale=2).to_pil().save(out/'inspections'/f'{f.stem}-p{i+1}.png')
print('verified all source hashes and rendered all PDF pages')

