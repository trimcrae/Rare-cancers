from pathlib import Path
import zipfile,json,xml.etree.ElementTree as ET
from pypdf import PdfReader
root=Path.cwd()
for p in root.rglob('*.zip'):
 print('ARCHIVE',p.relative_to(root))
 with zipfile.ZipFile(p) as z:
  for a in z.infolist():print(a.filename,a.file_size)
for stem in ['emc-tissue-rna-prioritization-preprint','emc-tissue-rna-prioritization-supplementary-information']:
 p=root/'research/manuscripts/surface-targets'/f'{stem}.pdf'
 pdf=PdfReader(p);print('PDF',stem,'pages',len(pdf.pages))
 text='\n'.join(f'PAGE {i+1}\n'+page.extract_text() for i,page in enumerate(pdf.pages))
 (root/'review-results'/f'{stem}.txt').write_text(text,encoding='utf-8')
 print(text[-3000:])
p=root/'research/autonomy/atlas-hofvander-source-2026-09-06/hofvander2026.xml'
r=ET.parse(p).getroot()
for s in r.findall('.//sec'):
 title=s.find('title')
 if title is not None and any(x in ''.join(title.itertext()).lower() for x in ['material','patient','rna sequenc','data availability']):
  print('SOURCE SECTION',' '.join(s.itertext()))
