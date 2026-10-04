from pathlib import Path
from urllib.request import urlopen,Request
import io,json,hashlib,datetime,shutil
from pypdf import PdfReader
R=Path(__file__).resolve().parent
url='https://static-content.springer-cdn.com/esm/art%3A10.1038%2Fs41698-025-00851-7/MediaObjects/41698_2025_851_MOESM1_ESM.pdf'
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'scope':'entire supplement streamed in memory, all pages retained as text; no outcome computation'}
try:
 assert shutil.disk_usage(R).free>10*1024**3+1024**2
 with urlopen(Request(url,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=30) as x:
  b=x.read(20*1024**2+1);assert len(b)<=20*1024**2,'streamed source above20MiB limit';r['status']=x.status
 assert b.startswith(b'%PDF-'),'not PDF'
 pages=[p.extract_text() for p in PdfReader(io.BytesIO(b)).pages]
 r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),pages=len(pages))
 out=(json.dumps({'source_url':url,'source_sha256':r['sha256'],'pages':pages},ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 (R/'precision2025-supp-pages.json').write_bytes(out)
 r.update(retained_file='precision2025-supp-pages.json',retained_bytes=len(out),retained_sha256=hashlib.sha256(out).hexdigest())
except Exception as e:r['error']=str(e)
(R/'precision-supp-receipt.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,indent=2))