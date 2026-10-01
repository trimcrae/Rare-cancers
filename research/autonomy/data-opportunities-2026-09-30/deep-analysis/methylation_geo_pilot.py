#!/usr/bin/env python3
import concurrent.futures,csv,gzip,hashlib,io,json,pathlib,re,time,urllib.request
OUT=pathlib.Path(__file__).resolve().parent/'outputs'/'methylation-geo';OUT.mkdir(parents=True,exist_ok=True)
BASE='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140686/'
class CountReader:
 def __init__(self,r):self.r=r;self.n=0;self.h=hashlib.sha256()
 def read(self,n=-1):
  b=self.r.read(n);self.n+=len(b);self.h.update(b)
  if self.n>40*1024*1024:raise ValueError('pilot prefix exceeds 40 MiB')
  return b
 def seekable(self):return False
def parse_series(text):
 fields={}
 for line in text.splitlines():
  if line.startswith('!Sample_'):
   r=next(csv.reader([line],delimiter='\t'));fields.setdefault(r[0],[]).append(r[1:])
 gsms=fields['!Sample_geo_accession'][0];out=[]
 for i,gsm in enumerate(gsms):
  vals=[v[i] for rows in fields.values() for v in rows if len(v)==len(gsms)]
  idats=sorted(set(x for v in vals for x in re.findall(r'\b[0-9]+_R[0-9]+C[0-9]+\b',v)))
  refs=sorted(set(x for v in vals for x in re.findall(r'REFERENCE_SAMPLE\s*[0-9]+',v)))
  out.append({'gsm':gsm,'title':fields.get('!Sample_title',[['']*len(gsms)])[0][i],'idat_candidates':idats,'reference_id_candidates':refs})
 return out,sorted(fields)
def pilot(platform):
 rec={'platform':platform};start=time.time();url=BASE+'matrix/GSE140686-'+platform+'_series_matrix.txt.gz'
 req=lambda u:urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Rare-cancers-public-data-pilot/1'}),timeout=120)
 with req(url) as r:b=r.read(2_000_001)
 if len(b)>2_000_000:raise ValueError('series metadata oversized')
 text=gzip.decompress(b).decode();(OUT/(platform+'-series-metadata.txt')).write_text(text)
 mapping,fields=parse_series(text)
 rec['series']={'url':url,'compressed_bytes':len(b),'compressed_sha256':hashlib.sha256(b).hexdigest(),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'sample_count':len(mapping),'fields':fields,'sample_mapping':mapping}
 url=BASE+'suppl/GSE140686_'+platform+'_matrix_processed.txt.gz';rec['processed_url']=url
 with req(url) as r:
  rec['content_length']=int(r.headers['Content-Length']) if r.headers.get('Content-Length') else None
  c=CountReader(r);t=time.time();rows=0;uncompressed=0;first=[];header=None;seen_counts=set()
  with gzip.GzipFile(fileobj=c) as gz:
   while c.n<32*1024*1024:
    row=gz.readline()
    if not row:break
    if len(row)>2_000_000:raise ValueError('oversized row')
    uncompressed+=len(row);s=row.decode().rstrip('\r\n');r0=next(csv.reader([s],delimiter='\t'))
    if header is None:header=r0
    else:
     rows+=1;seen_counts.add(len(r0))
     if len(first)<10:first.append(r0)
  elapsed=time.time()-t
  rec.update(compressed_bytes_consumed=c.n,compressed_prefix_sha256=c.h.hexdigest(),stream_seconds=round(elapsed,3),compressed_bytes_per_second=c.n/elapsed,projected_complete_stream_seconds=rec['content_length']/(c.n/elapsed) if rec['content_length'] else None,uncompressed_bytes=uncompressed,measured_rows_consumed=rows,observed_row_column_counts=sorted(seen_counts),header=header,first_row_example=first[0][:8] if first else [],first_probe_ids=[x[0] for x in first])
  (OUT/(platform+'-measured-prefix.tsv')).write_text('\n'.join('\t'.join(x) for x in [header,*first])+'\n')
 rec['seconds']=round(time.time()-start,3);return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:result=list(ex.map(pilot,['GPL13534','GPL21145']))
(OUT/'pilot.json').write_text(json.dumps(result,indent=2)+'\n')
print('EMC_METHYLATION_GEO_PILOT_BEGIN');print(json.dumps(result,separators=(',',':')));print('EMC_METHYLATION_GEO_PILOT_END')
