"""Complete streamed TempO-Seq exact probe counting, no large disk artifacts."""
from pathlib import Path
import urllib.request,hashlib,json,zipfile,xml.etree.ElementTree as E,gzip,csv,io,collections,time,sys
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
MANIFEST='https://www.biospyder.com/s/190620HumanWholeTranscriptome20Manifest.xlsx'
ENA='https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA1357027&result=read_run&fields=run_accession,sample_accession,experiment_accession,sample_alias,fastq_bytes,fastq_md5,fastq_ftp&format=tsv'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def fetch(name,url):
 p=BASE/name
 if not p.exists():
  with urllib.request.urlopen(url,timeout=40) as r:b=r.read(5000001)
  assert len(b)<5000001;p.write_bytes(b)
 return p.read_bytes()
def probes():
 b=fetch('HWT2.0-manifest.xlsx',MANIFEST);z=zipfile.ZipFile(io.BytesIO(b))
 ss=[''.join(e.itertext()) for e in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
 rows=[]
 for row in E.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('s:sheetData/s:row',NS):
  vals=[]
  for c in row.findall('s:c',NS):
   v=c.find('s:v',NS);vals.append(ss[int(v.text)] if c.get('t')=='s' else v.text if v is not None else None)
  rows.append(vals)
 assert rows[0][:5]==['Probe Name','Gene Symbol','Entrez ID','ENSEMBL Gene ID','Probe Sequence']
 return rows[1:]
class HashReader:
 def __init__(self,raw):self.raw=raw;self.md5=hashlib.md5();self.sha=hashlib.sha256();self.bytes=0
 def read(self,n=-1):
  b=self.raw.read(n);self.md5.update(b);self.sha.update(b);self.bytes+=len(b);return b
def main():
 p=probes();lookup=collections.defaultdict(list);rcmap=bytes.maketrans(b'ACGT',b'TGCA')
 for i,r in enumerate(p):
  seq=r[4].encode();assert len(seq)==50;lookup[seq].append((i,'forward'));lookup[seq.translate(rcmap)[::-1]].append((i,'reverse'))
 runs=list(csv.DictReader(io.StringIO(fetch('PRJNA1357027-runs.tsv',ENA).decode()),delimiter='\t'));assert len(runs)==12
 assert len({r['sample_alias'] for r in runs})==12
 prefix='--gate' in sys.argv
 for r in sorted(runs,key=lambda r:r['sample_alias']):
  outpath=BASE/('raw-'+r['sample_alias']+'.json')
  if outpath.exists() and not prefix:continue
  url='https://'+r['fastq_ftp'];t=time.time();counts=[0]*len(p);reads=0;matched=0;ambig=0;ori=collections.Counter();lens=collections.Counter()
  with urllib.request.urlopen(url,timeout=45) as req:
   hr=HashReader(req)
   with gzip.GzipFile(fileobj=hr) as f:
    if prefix:
     for _ in range(10000):
      h=f.readline();s=f.readline().strip();plus=f.readline();q=f.readline().strip()
      if not h:break
      assert h.startswith(b'@') and plus.startswith(b'+') and len(s)==len(q)
      reads+=1;lens[len(s)]+=1;hit=lookup.get(s,[])
      if len(hit)==1:counts[hit[0][0]]+=1;matched+=1;ori[hit[0][1]]+=1
      elif hit:ambig+=1
    else:
     remainder=b''
     while True:
      chunk=f.read(8*1024*1024)
      if not chunk:break
      data=remainder+chunk;lines=data.split(b'\n');n=((len(lines)-1)//4)*4
      remainder=b'\n'.join(lines[n:])
      assert all(x.startswith(b'@') for x in lines[:n:4]) and all(x.startswith(b'+') for x in lines[2:n:4])
      seqs=lines[1:n:4];quals=lines[3:n:4];assert all(len(a)==len(b) for a,b in zip(seqs,quals))
      reads+=len(seqs)
      for s,nseq in collections.Counter(seqs).items():
       lens[len(s)]+=nseq;hit=lookup.get(s,[])
       if len(hit)==1:counts[hit[0][0]]+=nseq;matched+=nseq;ori[hit[0][1]]+=nseq
       elif hit:ambig+=nseq
     assert not remainder,repr(remainder[:100])
  result={'sample':r['sample_alias'],'run':r['run_accession'],'biosample':r['sample_accession'],'url':url,'utc':datetime.now(timezone.utc).isoformat(),'reads':reads,'matched_exact_unique':matched,'matched_fraction':matched/reads,'ambiguous':ambig,'orientation':dict(ori),'lengths':dict(lens),'compressed_bytes_read':hr.bytes,'compressed_md5':hr.md5.hexdigest(),'compressed_sha256':hr.sha.hexdigest(),'expected_bytes':int(r['fastq_bytes']),'expected_md5':r['fastq_md5'],'complete':not prefix,'elapsed_seconds':time.time()-t}
  if not prefix:
   assert hr.bytes==int(r['fastq_bytes']) and hr.md5.hexdigest()==r['fastq_md5']
   result['probe_counts']=[{'probe':x[0],'gene':x[1],'entrez':x[2],'ensembl':x[3],'count':n} for x,n in zip(p,counts)]
   outpath.write_text(json.dumps(result,indent=2)+'\n')
  else:(BASE/'raw-method-gate.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({k:v for k,v in result.items() if k!='probe_counts'}),flush=True)
  if prefix:break
if __name__=='__main__':main()
