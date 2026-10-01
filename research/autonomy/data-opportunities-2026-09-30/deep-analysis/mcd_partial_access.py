import re,json,hashlib,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
FOOTER=8*1024*1024;ROI_CAP=64*1024*1024
FILES=[('MFS_TMA_1.mcd',12480847385),('MFS_TMA_2.mcd',12414529678),('USTS_TMA_1.mcd',10236093273),('USTS_TMA_2.mcd',10705578515)]
BASE='https://www.ebi.ac.uk/biostudies/files/S-BIAD1555/IMC/'
def digest(b):return hashlib.sha256(b).hexdigest()
def get_range(url,start,end,size,cap):
 assert 0<=start<=end<size and end-start+1<=cap
 req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}','User-Agent':'EMC-public-data-reanalysis/1','Accept-Encoding':'identity'})
 with urllib.request.urlopen(req,timeout=60) as res:
  receipt={'url':url,'final_url':res.geturl(),'status':res.status,'requested':[start,end],'Content_Range':res.headers.get('Content-Range'),'Content_Length':res.headers.get('Content-Length')}
  if res.status!=206:raise RuntimeError('Server ignored Range: '+json.dumps(receipt))
  match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',res.headers.get('Content-Range',''))
  if not match or tuple(map(int,match.groups()))!=(start,end,size):raise RuntimeError('Unexpected Content-Range: '+json.dumps(receipt))
  b=res.read(cap+1)
 assert len(b)==end-start+1
 receipt.update(bytes=len(b),sha256_partial=digest(b),whole_file_hash=False);return b,receipt
def local(t):return t.split('}')[-1]
def fields(e):return {local(c.tag):c.text for c in e if c.text is not None}
def probe_mcd(url,size):
 out={'url':url,'manifest_bytes':int(size),'selection':'Lowest-ID complete ROI<=64MiB,ValueBytes4; no signal selection','scope':'Pixel feasibility,not patient cell inference','ranges':[]}
 try:
  footer,rec=get_range(url,max(0,size-FOOTER),size-1,size,FOOTER);out['ranges'].append(rec)
  a=footer.rfind('<MCDSchema'.encode('utf-16-le'));b=footer.rfind('</MCDSchema>'.encode('utf-16-le'))
  if a<0 or b<a:
   cap=32*1024*1024;footer,rec=get_range(url,max(0,size-cap),size-1,size,cap);out['ranges'].append(rec);a=footer.rfind('<MCDSchema'.encode('utf-16-le'));b=footer.rfind('</MCDSchema>'.encode('utf-16-le'))
  assert a>=0 and b>=a,'XML absent from both suffixes'
  xml=footer[a:b+len('</MCDSchema>'.encode('utf-16-le'))].decode('utf-16-le');root=ET.fromstring(xml)
  outdir=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis/outputs');outdir.mkdir(parents=True,exist_ok=True);name=Path(url).name;(outdir/(name+'.schema.xml')).write_text(xml)
  ac=[fields(e) for e in root.iter() if local(e.tag)=='Acquisition'];channels=[fields(e) for e in root.iter() if local(e.tag)=='AcquisitionChannel'];rois=[fields(e) for e in root.iter() if local(e.tag)=='AcquisitionROI']
  out.update(schema_sha256=digest(xml.encode()),acquisitions=ac,channels=channels,acquisition_ROIs=rois,n_acquisitions=len(ac));usable=[]
  for row in ac:
   try:
    start=int(row['DataStartOffset']);end=int(row['DataEndOffset']);width=end-start+1
    if int(row.get('ValueBytes','4'))==4 and 0<width<=ROI_CAP and 0<=start<=end<size:usable.append((int(row['ID']),start,end,row))
   except (ValueError,KeyError,TypeError):continue
  if not usable:out['ROI_status']='No4byte ROI<=64MiB; rawaccessnotexhausted';return out
  aid,start,end,row=min(usable,key=lambda x:x[0]);ch=[c for c in channels if str(c.get('AcquisitionID'))==str(aid) and c.get('ChannelName') not in ['X','Y','Z']];ch.sort(key=lambda c:int(c.get('OrderNumber','0')));assert ch
  payload,rec=get_range(url,start,end,size,ROI_CAP);out['ranges'].append(rec);stride=len(ch)+3;assert len(payload)%(4*stride)==0
  values=np.frombuffer(payload,dtype='<f4').reshape(-1,stride);assert len(values)>0;summary=[]
  for k,c in enumerate(ch):
   v=values[:,k+3];good=v[np.isfinite(v)];summary.append({'metadata':c,'finite_count':int(len(good)),'finite_fraction':float(len(good)/len(v)),'q0_q50_q90_q99_q100':list(map(float,np.quantile(good,[0,.5,.9,.99,1]))) if len(good) else None})
  dest=outdir/(name+'.pilot_pixels.npz');np.savez_compressed(dest,pixels=values,channel_names=np.array([c.get('ChannelName','') for c in ch]),channel_labels=np.array([c.get('ChannelLabel','') for c in ch]))
  out['pilot']={'acquisition_id':aid,'description':row.get('Description'),'complete_ROI_bytes':len(payload),'pixels':len(values),'noncoordinate_channels':len(ch),'XYZ_first3':True,'coordinate_ranges':[[float(np.nanmin(values[:,k])),float(np.nanmax(values[:,k]))] for k in range(3)],'channel_summaries':summary,'saved_pixels':str(dest)}
  out['ROI_status']='Complete selected ROI decoded'
 except Exception as e:out['error']=type(e).__name__+': '+str(e)
 return out
if __name__=='__main__':
 result=[probe_mcd(BASE+n,s) for n,s in FILES];print('EMC_MCD_PARTIAL_BEGIN');print(json.dumps(result,allow_nan=False));print('EMC_MCD_PARTIAL_END')
