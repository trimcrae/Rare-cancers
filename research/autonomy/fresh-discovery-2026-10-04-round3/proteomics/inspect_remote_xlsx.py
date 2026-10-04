"""Range-read ZIP metadata; never download the79MB workbook or mass spectra."""
from pathlib import Path
import urllib.request,zipfile,json,io,hashlib,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
class RangeFile:
 def __init__(self,url,size):self.url=url;self.size=size;self.pos=0;self.calls=[];self.total=0
 def tell(self):return self.pos
 def seekable(self):return True
 def readable(self):return True
 def seek(self,offset,whence=0):
  self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
  assert self.pos>=0;return self.pos
 def read(self,n=-1):
  n=min(n if n>=0 else self.size-self.pos,self.size-self.pos)
  if n==0:return b''
  assert n<=2_000_000 and self.total+n<10_000_000,'Scoped range budget'
  start=self.pos;end=start+n-1
  with urllib.request.urlopen(urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{end}'}),timeout=30) as r:
   assert r.status==206 and r.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/')
   b=r.read(n+1)
  assert len(b)==n
  self.pos+=n;self.total+=n;self.calls.append({'start':start,'end':end,'bytes':n,'sha256':hashlib.sha256(b).hexdigest()});return b
source=next(x for x in json.loads((P/'procan-pride-page0.json').read_text()) if x['fileName']=='cohort_1_processed_matrix.xlsx')
url=next(x['value'] for x in source['publicFileLocations'] if x['name']=='FTP Protocol').replace('ftp://','https://')
remote=RangeFile(url,source['fileSizeBytes'])
out={'source':source,'purpose':'Find sample annotations without protein-value analysis or complete workbook download'}
with zipfile.ZipFile(remote) as z:
 out['members']=[{'name':i.filename,'compressed':i.compress_size,'bytes':i.file_size,'header_offset':i.header_offset} for i in z.infolist()]
 for name in ['xl/workbook.xml','xl/_rels/workbook.xml.rels']:
  b=z.read(name);n='procan-'+name.replace('/','-');(P/n).write_bytes(b)
  out[name]=b.decode();print(name,b.decode()[:2500])
out['requests']=remote.calls;out['downloaded_bytes']=remote.total
(P/'procan-remote-xlsx-structure.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('members',[(i['name'],i['compressed'],i['bytes']) for i in out['members']]);print('range bytes',remote.total)
