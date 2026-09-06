"""Verify source receipts and packet JSON; no scientific experiments."""
from pathlib import Path
import datetime, hashlib, json
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
CACHE=ROOT.parents[2]/'.cache'/'ipd-partial-order-prior-art-2026-09-06'
receipt_path=ROOT/'sources'/'download-receipts.json'
rows=json.loads(receipt_path.read_text(encoding='utf-8'))
for row in rows:
    path=CACHE/row['name']
    if row['name']=='denoeux_rank.pdf' and 'error' in row and path.exists():
        row['attempts']=[{'client':'Python urllib with normal certificate verification','error':row.pop('error')}, {'client':'PowerShell Invoke-WebRequest with normal system trust','outcome':'download succeeded'}]
        row.update(status=200, local_path=str(path), bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), pdf_pages=len(PdfReader(path).pages))
    if 'sha256' in row:
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'], row['name']
receipt_path.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
for path in ROOT.rglob('*.json'):
    json.loads(path.read_text(encoding='utf-8'))
files=[]
for folder in [ROOT,CACHE]:
    for path in sorted(folder.rglob('*')):
        if path.is_file() and path.name!='manifest.json':
            files.append(dict(path=str(path.relative_to(ROOT.parents[2])),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
manifest=dict(base_revision='920fed4fff362b9cef8e97fb7b3356209c77c7af', verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), source_receipts_checked=sum('sha256' in r for r in rows), checks=['all downloaded source hashes match receipts','all packet JSON parses','PDF appendix p16 rendered using pypdfium2 and visually inspected'], limitations=['fitz import unavailable; pypdfium2 succeeded','no scientific experiment, benchmark, theorem proof, preflight or ultra review'], files=files)
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
