from pathlib import Path
import urllib.request,json,hashlib,datetime,shutil,sys
sys.stdout.reconfigure(encoding='utf-8')
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
u='https://ars.els-cdn.com/content/image/1-s2.0-S0304383526000637-mmc1.pdf'
p=ROOT/'planaspaz2026-supplement.pdf'
if not p.exists():
 assert shutil.disk_usage(ROOT).free>10*1024**3+15*1024**2
 with urllib.request.urlopen(u,timeout=30) as r:
  b=r.read(12*1024**2+1)
  assert len(b)<=12*1024**2 and b[:5]==b'%PDF-'
 p.write_bytes(b)
b=p.read_bytes();r=PdfReader(p)
texts=[page.extract_text() for page in r.pages]
(ROOT/'planaspaz2026-supplement-text.txt').write_text('\n\n'.join('PAGE '+str(i+1)+'\n'+t for i,t in enumerate(texts)),encoding='utf-8')
(ROOT/'planaspaz2026-supplement-receipt.json').write_text(json.dumps({'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'pages':len(texts)},indent=2)+'\n')
for i,t in enumerate(texts):
 if 'EMC' in t or 'chondrosarcoma' in t.lower():
  print('EMC source label on PAGE',i+1)
print('Pages extracted',len(texts),'EMC exact-case label absent from text does not exclude image-only label')
