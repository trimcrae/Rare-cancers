from pathlib import Path
import urllib.request,hashlib,io,json,shutil,re
from datetime import datetime,timezone
from pypdf import PdfReader,PdfWriter
base=Path(__file__).parent
assert shutil.disk_usage(base).free>10*1024**3+2*1024**2
url='https://s1p.studyres.com/store/data/008017800.pdf?k=AwAAAaEIbGwoAAACWAmBJQnteoXPD0pvrpnd5HAI1d7S'
receipt={'url':url,'source_class':'Third-party public mirror of the original MSTS program; publisher authentication remains pending.','utc':datetime.now(timezone.utc).isoformat()}
try:
 r=urllib.request.urlopen(url,timeout=30);b=r.read(40*1024**2+1)
 receipt.update({'status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'content_type':r.headers.get('content-type')})
 assert len(b)<=40*1024**2 and b.startswith(b'%PDF')
 reader=PdfReader(io.BytesIO(b));receipt['pages']=len(reader.pages);receipt['pdf_metadata']=dict(reader.metadata or {})
 hits=[]
 for i,page in enumerate(reader.pages):
  text=page.extract_text() or ''
  if 'MICRO-RNA ANALYSIS AND PATHOGENESIS' in text.upper() or ('miR-99a' in text and 'EMC' in text):hits.append({'page_1based':i+1,'text':text})
 writer=PdfWriter()
 for i in sorted({0}|{h['page_1based']-1 for h in hits}):writer.add_page(reader.pages[i])
 with (base/'msts2013-selected-original-pages.pdf').open('wb')as f:writer.write(f)
 (base/'msts2013-selected-text.json').write_text(json.dumps(hits,indent=2),encoding='utf8')
 print('SOURCE',len(b),len(reader.pages),[(h['page_1based'],len(h['text']))for h in hits])
 print('\n'.join(h['text']for h in hits if 'miR-99a' in h['text']))
except Exception as e:
 receipt['error']=str(e);print(type(e).__name__,str(e))
(base/'msts-mirror-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
