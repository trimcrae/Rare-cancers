"""Bounded method gate on all twelve libraries; not biological count estimates."""
import raw_probe_count as rpc
import urllib.request,hashlib,json,collections,csv,io,gzip,time
import numpy as np
from datetime import datetime,timezone
BASE=rpc.BASE
def main():
 p=rpc.probes();rc=bytes.maketrans(b'ACGT',b'TGCA');lookup=collections.defaultdict(list);front=collections.defaultdict(set);back=collections.defaultdict(set)
 for i,x in enumerate(p):
  s=x[4].encode();lookup[s].append((i,'forward'));lookup[s.translate(rc)[::-1]].append((i,'reverse'));front[s[:25]].add(i);back[s[25:]].add(i)
 url='https://www.biospyder.com/s/100739_homo_sapiens_wt_21_full_manifest_revB.csv'
 q=BASE/'HWT2.1-manifest.csv'
 if not q.exists():
  b=urllib.request.urlopen(url,timeout=30).read(8000001);assert len(b)<8000001;q.write_bytes(b)
 b=q.read_bytes();alt=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))));altseq={x['PROBE_SEQUENCE'].encode() for x in alt}
 runs=list(csv.DictReader(io.StringIO((BASE/'PRJNA1357027-runs.tsv').read_text()),delimiter='\t'))
 a=np.array([list(x[4].encode()) for x in p],dtype=np.uint8);results=[]
 for r in sorted(runs,key=lambda r:r['sample_alias']):
  hist=collections.Counter();lengths=collections.Counter();near=collections.Counter();altmatch=0
  with urllib.request.urlopen('https://'+r['fastq_ftp'],timeout=35) as req:
   hr=rpc.HashReader(req)
   with gzip.GzipFile(fileobj=hr) as f:
    for i in range(10000):
     h=f.readline();s=f.readline().strip();plus=f.readline();qual=f.readline().strip()
     assert h.startswith(b'@') and plus.startswith(b'+') and len(s)==len(qual)
     lengths[len(s)]+=1;hit=lookup.get(s,[])
     if len(hit)==1:hist['full_'+hit[0][1]]+=1
     elif hit:hist['ambiguous']+=1
     else:
      fh=front.get(s[:25],set());bh=back.get(s[25:],set())
      hist['different_halves' if fh and bh and not fh&bh else 'one_half' if fh or bh else 'neither_half']+=1
      if r['sample_alias']=='Si01' and i<200:near[int((a!=np.frombuffer(s,dtype=np.uint8)).sum(axis=1).min())]+=1
     altmatch+=s in altseq or s.translate(rc)[::-1] in altseq
  out={'sample':r['sample_alias'],'run':r['run_accession'],'reads_inspected':10000,'scope':'Method diagnostic prefix only; not population or expression estimate','counts':dict(hist),'lengths':dict(lengths),'alternate_v21_exact_matches':altmatch,'prefix_compressed_sha256':hr.sha.hexdigest(),'prefix_compressed_bytes':hr.bytes}
  if near:out['unmatched_first200_nearest_forward_probe_hamming']=dict(near)
  results.append(out);print(json.dumps(out),flush=True)
 genes=['MS4A1','CD79A','CD79B','CD37','PTPRC','CD3D','CD3E','CD3G','LST1','AIF1','FCER1G','PXN','H1FX','TYMS']
 manifest={'url':rpc.MANIFEST,'sha256':hashlib.sha256((BASE/'HWT2.0-manifest.xlsx').read_bytes()).hexdigest(),'probe_count':len(p),'distinct_genes':len({x[1] for x in p}),'v21_url':url,'v21_sha256':hashlib.sha256(b).hexdigest(),'v21_probe_count':len(alt),'same_forward_sequences':len({x[4].encode() for x in p}&altseq),'prespecified_gene_probes':{g:[x[0] for x in p if x[1]==g] for g in genes}}
 (BASE/'mapping-diagnostic-results.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'manifest':manifest,'runs':results},indent=2)+'\n')
if __name__=='__main__':main()
