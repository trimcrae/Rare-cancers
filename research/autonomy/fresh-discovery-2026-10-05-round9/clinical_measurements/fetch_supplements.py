"""Quiet permitted machine-readable clinical supplements; do not inspect images."""
from pathlib import Path
import urllib.request,json,datetime,hashlib,concurrent.futures,zipfile,io
ROOT=Path(__file__).resolve().parent
TASKS=[('Cnovyi','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12434394/supplementaryFiles','zip',15000000),('Tazemetostat','https://static-content.springer-cdn.com/esm/art%3A10.1038%2Fs41467-026-69708-2/MediaObjects/41467_2026_69708_MOESM1_ESM.docx','docx',5000000),('Selumetinib','https://static-content.springer-cdn.com/esm/art%3A10.1007%2Fs10637-024-01428-0/MediaObjects/10637_2024_1428_MOESM1_ESM.pdf','pdf',5000000)]
def fetch(x):
 name,url,ext,cap=x;rec={'source':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cap':cap,'mode':'file only; no rendering/image inspection'}
 try:
  with urllib.request.urlopen(url,timeout=30) as r:b=r.read(cap+1);rec['http_status']=r.status;rec['content_type']=r.headers.get('Content-Type');rec['advertised_length']=r.headers.get('Content-Length')
  assert len(b)<=cap,'size cap exceeded; incomplete not retained'
  q=ROOT/'source-cache'/f'{name}-supplement.{ext}';q.write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),cache_path=str(q.relative_to(ROOT)))
  if ext in ['zip','docx']:
   z=zipfile.ZipFile(io.BytesIO(b));rec['members']=[{'name':y.filename,'bytes':y.file_size} for y in z.infolist()];rec['valid']=True
  else:rec['valid']=b.startswith(b'%PDF')
 except Exception as e:rec['error']=type(e).__name__+':'+str(e)
 return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:r=list(ex.map(fetch,TASKS))
 ROOT.joinpath('SUPPLEMENT-ACCESS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps([{k:y.get(k) for k in ['source','bytes','valid','error','advertised_length']} for y in r]))
