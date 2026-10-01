import json,urllib.request,re,hashlib,datetime,zlib
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT
def main():
 path,receipt=sm.getfull('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174376&targ=self&form=text&view=full','GSE174376-primary-series.soft.txt',16*1024**2);text=path.read_text(errors='replace');assert '^SERIES = GSE174376' in text;lines=text.splitlines();files=sorted(set(l.split('=',1)[1].strip() for l in lines if l.startswith('!Series_supplementary_file') and '=' in l));result={'schema':'emc-pediatric-GEO-alternate-access/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primary_project':'SCPCP000005','primary_series':'GSE174376','series_receipt':receipt,'series_source_metadata':[l for l in lines if l.startswith(('!Series_title','!Series_summary','!Series_overall_design','!Series_sample_id','!Series_relation','!Series_supplementary_file'))],'public_supplementary_files':files,'header_probes':[],'scope':'Finite primary-source alternative to ScPCA token route; access/format only, no absent-expression or novelty inference'}
 for i,source in enumerate(files[:20]):
  actual=re.sub(r'^ftp://ftp.ncbi.nlm.nih.gov/','https://ftp.ncbi.nlm.nih.gov/',source);r={'source_url':source,'requested_url':actual}
  try:
   req=urllib.request.Request(actual,headers={'Range':'bytes=0-65535','Accept-Encoding':'identity','User-Agent':'EMC-public-data-reanalysis/1'})
   with urllib.request.urlopen(req,timeout=90) as response:
    b=response.read(65536);r.update(status='retrieved',http_status=response.status,final_url=response.geturl(),Content_Range=response.headers.get('Content-Range'),Content_Length=response.headers.get('Content-Length'),prefix_bytes=len(b),prefix_sha256=hashlib.sha256(b).hexdigest());saved=OUT/f'GSE174376-supplement-prefix-{i}.bin';saved.write_bytes(b);r['prefix_saved']=str(saved)
   if b.startswith(b'\x1f\x8b'):
    try:r['decompressed_prefix_text']=zlib.decompressobj(31).decompress(b,16384).decode('utf-8',errors='replace')[:8000]
    except Exception as e:r['prefix_decode_error']=str(e)
   elif b[:8]!=b'\x89HDF\r\n\x1a\n':r['prefix_text']=b.decode('utf-8',errors='replace')[:8000]
   else:r['format']='HDF5'
  except Exception as e:r.update(status='error',error_type=type(e).__name__,error=str(e),absence_claim=False)
  result['header_probes'].append(r)
 dest=OUT/'pediatric-GEO-alternate-access-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_GEO_ALTERNATE_ACCESS_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PEDIATRIC_GEO_ALTERNATE_ACCESS_END')
if __name__=='__main__':main()
