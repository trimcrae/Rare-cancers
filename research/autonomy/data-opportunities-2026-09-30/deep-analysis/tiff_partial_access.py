import io,re,json,tempfile,urllib.request,hashlib
from pathlib import Path
import numpy as np
import tifffile
BLOCK=1024*1024;BUDGET=64*1024*1024;SEGMENT_CAP=8*1024*1024
PILOTS=[('https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/EWS_Opal/Panel2/EWS48a.tif',1230117148),('https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/EWS_Opal/Panel3/EWS105a.tif',643586587)]
class RangeUnavailable(RuntimeError):pass
class RangeBudget(RuntimeError):pass
class RangeIO(io.RawIOBase):
 def __init__(self,url,size):self.url=url;self.size=size;self.pos=0;self.cache={};self.downloaded=0;self.receipts=[];self.name=Path(url).name
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,offset,whence=0):
  new=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
  if new<0:raise ValueError('Negative seek')
  self.pos=new;return new
 def readinto(self,b):got=self.read(len(b));b[:len(got)]=got;return len(got)
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  if n>SEGMENT_CAP:raise RangeBudget('Single read>8MiB')
  end=min(self.size,self.pos+n);parts=[]
  while self.pos<end:
   block=self.pos//BLOCK;start=block*BLOCK;stop=min(self.size,start+BLOCK)-1
   if block not in self.cache:
    length=stop-start+1
    if self.downloaded+length>BUDGET:raise RangeBudget('Ranges>64MiB')
    request=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{stop}','Accept-Encoding':'identity','User-Agent':'EMC-public-data-reanalysis/1'})
    with urllib.request.urlopen(request,timeout=60) as res:
     record={'url':self.url,'final_url':res.geturl(),'status':res.status,'requested':[start,stop],'Content_Range':res.headers.get('Content-Range')}
     if res.status!=206:raise RangeUnavailable('Server ignored Range: '+json.dumps(record))
     match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',res.headers.get('Content-Range',''))
     if not match or tuple(map(int,match.groups()))!=(start,stop,self.size):raise RangeUnavailable('Unexpected Range '+json.dumps(record))
     payload=res.read(length+1)
    if len(payload)!=length:raise RangeUnavailable('Truncated/oversized range')
    record.update(bytes=length,sha256_partial=hashlib.sha256(payload).hexdigest(),whole_file_hash=False);self.receipts.append(record);self.cache[block]=payload;self.downloaded+=length
   within=self.pos-start;count=min(end-self.pos,len(self.cache[block])-within);parts.append(self.cache[block][within:within+count]);self.pos+=count
  return b''.join(parts)
def describe_and_decode(tif,stream,outdir,label):
 result=[];desc=tif.pages[0].description or '';(outdir/(label+'.description.txt')).write_text(desc)
 for i,page in enumerate(tif.pages):
  if i>=6:break
  offsets=page.dataoffsets;counts=page.databytecounts;rec={'page':i,'shape':list(page.shape),'dtype':str(page.dtype),'compression':str(page.compression),'is_tiled':bool(page.is_tiled),'tile_width':int(page.tilewidth),'tile_length':int(page.tilelength),'segments':len(offsets),'description':(page.description or '')[:2048]}
  if offsets:
   segment=len(offsets)//2;offset=int(offsets[segment]);length=int(counts[segment]);rec['selected_segment']={'index':segment,'offset':offset,'compressed_bytes':length,'selection':'Middle segment,first6pages,beforevalues'}
   try:
    if length>SEGMENT_CAP:raise RangeBudget('Compressed segment>8MiB')
    stream.seek(offset);payload=stream.read(length);assert len(payload)==length;rec['selected_segment']['sha256_payload']=hashlib.sha256(payload).hexdigest()
    tile=page.decode(payload,segment,jpegtables=page.jpegtables)[0]
    if tile is None:rec['tile_decode_status']='No decoded tile'
    else:
     tile=np.asarray(tile);good=tile[np.isfinite(tile)];rec['decoded_tile']={'shape':list(tile.shape),'finite_fraction':float(len(good)/tile.size),'q0_q50_q90_q99_q100':list(map(float,np.quantile(good,[0,.5,.9,.99,1]))) if len(good) else None};np.savez_compressed(outdir/(label+f'.page{i}.middle_segment.npz'),pixels=tile)
   except Exception as e:rec['tile_error_type']=type(e).__name__;rec['tile_error']=str(e)
  result.append(rec)
 return {'TIFF_pages':len(tif.pages),'series':[{'shape':list(s.shape),'axes':s.axes} for s in list(tif.series)[:6]],'page_metadata_and_middle_segments':result,'metadata_description_saved':str(outdir/(label+'.description.txt'))}
def full_pilot(url,size,outdir,label):
 assert (url,size) in PILOTS and size<=2*1024**3
 rec={'reason':'Rangeunsupported/budget; verifiedfullfilefallback','url':url,'manifest_bytes':size};h=hashlib.sha256();written=0
 with tempfile.TemporaryDirectory(prefix='emc-tiff-pilot-') as tmp:
  path=Path(tmp)/label;req=urllib.request.Request(url,headers={'User-Agent':'EMC-public-data-reanalysis/1','Accept-Encoding':'identity'})
  with urllib.request.urlopen(req,timeout=60) as response,path.open('wb') as dest:
   rec.update(status=response.status,final_url=response.geturl(),Content_Length=response.headers.get('Content-Length'));assert response.status==200;next_progress=128*1024*1024
   while True:
    chunk=response.read(BLOCK)
    if not chunk:break
    written+=len(chunk);assert written<=size;h.update(chunk);dest.write(chunk)
    if written>=next_progress:print('EMC_TIFF_FULL_PROGRESS '+json.dumps({'file':label,'bytes':written,'expected':size}),flush=True);next_progress+=128*1024*1024
  assert written==size;rec.update(bytes=written,sha256_full_file=h.hexdigest(),size_verified=True)
  with path.open('rb') as stream,tifffile.TiffFile(stream) as tif:rec['decoded']=describe_and_decode(tif,stream,outdir,label)
 return rec
def probe_tiff(url,size):
 outdir=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis/outputs');outdir.mkdir(parents=True,exist_ok=True);label=Path(url).name+'.'+url.split('/')[-2];stream=RangeIO(url,size);out={'url':url,'manifest_bytes':size,'scope':'Rawdecodingfeasibility,notcell/patientinference'}
 try:
  with tifffile.TiffFile(stream) as tif:out['range_decoded']=describe_and_decode(tif,stream,outdir,label)
 except Exception as e:out['range_error_type']=type(e).__name__;out['range_error']=str(e)
 out['ranges']=stream.receipts;out['range_downloaded_bytes']=stream.downloaded
 errors=[r.get('tile_error_type') for r in out.get('range_decoded',{}).get('page_metadata_and_middle_segments',[])]
 if out.get('range_error_type') in ['RangeUnavailable','RangeBudget'] or any(x in ['RangeUnavailable','RangeBudget'] for x in errors):
  try:out['full_pilot_fallback']=full_pilot(url,size,outdir,label)
  except Exception as e:out['full_pilot_error_type']=type(e).__name__;out['full_pilot_error']=str(e)
 return out
if __name__=='__main__':
 results=[probe_tiff(u,s) for u,s in PILOTS];print('EMC_TIFF_PARTIAL_BEGIN');print(json.dumps(results,allow_nan=False));print('EMC_TIFF_PARTIAL_END')
