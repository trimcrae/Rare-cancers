import pathlib,urllib.request,hashlib,datetime,io,json
from pypdf import PdfReader,PdfWriter
R=pathlib.Path(__file__).resolve().parent
u='https://filecache.investorroom.com/mr5ir_transcode2/148/download/transcode-march-2026.pdf'
try:
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as f:d=f.read(20*1024*1024+1);status=f.status
except Exception as e:
 (R/'march-receipt.json').write_text(json.dumps({'url':u,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initial_plain_urllib':'HTTP403','ordinary_header_retry_error':str(e)},indent=2));raise
assert len(d)<=20*1024*1024
r=PdfReader(io.BytesIO(d));w=PdfWriter();texts=[]
for i,p in enumerate(r.pages):
 t=p.extract_text() or ''
 if any(s in t.lower() for s in ['102-001','101-001','target engagement','thyroglobulin','pharmacokinetic','phase 0','trial – preliminary','subject tumor']):w.add_page(p);texts.append({'original_pdf_page':i+1,'text':t})
with (R/'march2026-selected.pdf').open('wb') as f:w.write(f)
(R/'march2026-selected-text.json').write_text(json.dumps(texts,indent=2),encoding='utf-8')
receipt={'url':u,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':status,'full_source_bytes_streamed_not_retained':len(d),'full_source_sha256':hashlib.sha256(d).hexdigest(),'full_pages':len(r.pages),'selected_pages':[t['original_pdf_page'] for t in texts],'selected_file_sha256':hashlib.sha256((R/'march2026-selected.pdf').read_bytes()).hexdigest()}
(R/'march-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2));print(json.dumps(texts,indent=2))
