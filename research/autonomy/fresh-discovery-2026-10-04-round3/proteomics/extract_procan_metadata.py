"""Stream every public ProCan Cohort1 annotation, discarding all protein columns."""
from pathlib import Path
import urllib.request,zipfile,json,hashlib,xml.etree.ElementTree as E,shutil,time,collections
P=Path(__file__).resolve().parent
assert shutil.disk_usage(P).free>=10*2**30
class RangeReader:
 def __init__(self,url,size): self.url=url;self.size=size;self.pos=0;self.cache=b'';self.start=0;self.calls=[];self.total=0
 def tell(self): return self.pos
 def seekable(self):return True
 def readable(self):return True
 def seek(self,n,whence=0):
  self.pos=n if whence==0 else self.pos+n if whence==1 else self.size+n
  assert 0<=self.pos<=self.size
  return self.pos
 def read(self,n=-1):
  n=min(n if n>=0 else self.size-self.pos,self.size-self.pos)
  if not n:return b''
  assert n<=2**20
  if not (self.start<=self.pos and self.pos+n<=self.start+len(self.cache)):
   start=self.pos;end=min(self.size-1,start+max(n,2**20)-1)
   assert self.total+end-start+1<85_000_000
   for attempt in range(3):
    try:
     with urllib.request.urlopen(urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{end}'}),timeout=35) as r:
      assert r.status==206 and r.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/')
      b=r.read(end-start+2)
     assert len(b)==end-start+1
     break
    except Exception:
     if attempt==2:raise
     time.sleep(1)
   self.start=start;self.cache=b;self.total+=len(b)
   self.calls.append({'start':start,'end':end,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  result=self.cache[self.pos-self.start:self.pos-self.start+n];self.pos+=len(result);return result
class HashingStream:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b
src=next(x for x in json.loads((P/'procan-pride-page0.json').read_text()) if x['fileName']=='cohort_1_processed_matrix.xlsx')
url=next(x['value'] for x in src['publicFileLocations'] if x['name']=='FTP Protocol').replace('ftp://','https://')
r=RangeReader(url,src['fileSizeBytes']);ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
rows=[];sheet_hash=None
with zipfile.ZipFile(r) as z:
 strings=[''.join(el.itertext()) for el in E.fromstring(z.read('xl/sharedStrings.xml'))]
 entry=z.getinfo('xl/worksheets/sheet1.xml')
 with z.open(entry) as f:
  h=HashingStream(f)
  for event,e in E.iterparse(h,events=('end',)):
   if e.tag.endswith('}row'):
    row={'source_row':int(e.attrib['r'])}
    for cell in e.findall('m:c',ns):
     coord=cell.attrib.get('r','');column=''.join(c for c in coord if c.isalpha())
     if column not in ['A','B','C','D']:continue
     value=cell.find('m:v',ns)
     if cell.attrib.get('t')=='s':v=strings[int(value.text)]
     elif cell.attrib.get('t')=='inlineStr':v=''.join(cell.find('m:is',ns).itertext())
     else:v=value.text if value is not None else ''
     row[column]=v
    rows.append(row);e.clear()
    if len(rows)%300==0: print('metadata rows',len(rows),flush=True)
  sheet_hash=h.h.hexdigest();sheet_bytes=h.n
 assert rows[0]=={'source_row':1,'A':'SampleID','B':'Cancer type','C':'Tissue type','D':'Cancer subtype'},rows[0]
 assert len(rows)==1261 and sheet_bytes==entry.file_size
 metadata=[{'source_row':x['source_row'],'sample_id':x.get('A',''),'cancer_type':x.get('B',''),'tissue_type':x.get('C',''),'cancer_subtype':x.get('D','')} for x in rows[1:]]
 receipt={'url':url,'source_metadata':src,'network_bytes':r.total,'range_requests':r.calls,'worksheet':{'path':entry.filename,'crc32':entry.CRC,'header_offset':entry.header_offset,'compressed_bytes':entry.compress_size,'uncompressed_bytes':entry.file_size,'uncompressed_sha256':sheet_hash},'all_rows':len(metadata),'purpose':'Decode all1260sample annotation rowsA:D; protein values were parsed structurally then discarded, never analyzed.'}
(P/'procan-all1260-sample-metadata.json').write_text(json.dumps(metadata,indent=2))
(P/'procan-all1260-extraction-receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({'rows':len(metadata),'unique_ids':len({x['sample_id'] for x in metadata}),'network_bytes':r.total,'sarcoma_subtypes':dict(collections.Counter(x['cancer_subtype'] for x in metadata if 'sarcoma' in (x['cancer_type']+' '+x['cancer_subtype']).lower()))}))
