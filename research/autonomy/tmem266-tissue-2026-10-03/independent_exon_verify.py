"""Worker's independent NumPy per-base replay of actual selected data blocks."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import urllib.request
import zlib
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'.cache/python-deps'))
import numpy as np
d=json.loads((BASE/'culture-exon-coverage-results.json').read_text())
a=json.loads((BASE/'culture-exon-annotation.json').read_text())
start,end=76059836,76229121
results={}
for run,v in d['runs'].items():
    cov=np.zeros(end-start)
    rec=v['range_receipts'][-1]
    off,size=rec['offset'],rec['size']
    assert size<200000
    req=urllib.request.Request(v['url'],headers={
        'Range':f'bytes={off}-{off+size-1}','Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=25) as response:
        assert response.status==206
        b=response.read(size+1)
    assert len(b)==size and hashlib.sha256(b).hexdigest()==rec['sha256']
    raw=zlib.decompress(b)
    pos=0
    while pos<len(raw):
        chrom,first,last,step,span,kind,reserved,n=struct.unpack_from('<5IBBH',raw,pos)
        pos+=24
        assert kind==1 and chrom==14
        rows=np.frombuffer(raw,dtype=np.dtype([
            ('start','<u4'),('end','<u4'),('value','<f4')]),count=n,offset=pos)
        pos+=n*12
        for r in rows:
            lo=max(int(r['start']),start)
            hi=min(int(r['end']),end)
            if hi>lo:
                cov[lo-start:hi-start]=r['value']
    assert pos==len(raw)
    vals=[float(cov[x-start:y-start].sum()) for x,y in a['exons']]
    assert vals==[r['coverage_sum'] for r in v['exons']]
    results[run]={'pass':True,'download_bytes':len(b),'per_exon_sums':vals,
                  'total':sum(vals)}
output={'scope':'Independent actual-block replay, not generic BigWig reader validation',
        'runs':results,'pass':True}
(BASE/'independent-exon-verification.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output))
