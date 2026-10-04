"""Bounded read-only BigWig range query; no dependency install or full downloads.

Full-resolution format checked against libBigWig bwRead.c and bwValues.c.
No zoom records. Enforce HTTP206/exact range and reproduce published gene sums.
"""
import hashlib
import json
from pathlib import Path
import struct
import urllib.request
import zlib

BASE = Path(__file__).resolve().parent
ANNOT_URL = ('https://api.genome.ucsc.edu/getData/track?genome=hg38;'
             'track=wgEncodeGencodeCompV26;chrom=chr15;start=76059836;end=76229121')
EXPECTED = {'SRR3380704': 1333, 'SRR3380705': 1694}

def digest(b):
    return hashlib.sha256(b).hexdigest()

def merge(intervals):
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1][1] = max(b, out[-1][1])
        else:
            out.append([a, b])
    return out

def annotation():
    with urllib.request.urlopen(ANNOT_URL, timeout=30) as r:
        b = r.read(100001)
    assert len(b) <= 100000
    raw = json.loads(b)
    genes = {}
    for t in raw['wgEncodeGencodeCompV26']:
        pairs = zip(map(int,t['exonStarts'].strip(',').split(',')),
                    map(int,t['exonEnds'].strip(',').split(',')))
        genes.setdefault(t['name2'], []).extend(pairs)
    unions = {g: merge(v) for g,v in genes.items()}
    exons = unions['TMEM266']
    shared = {}
    for g, intervals in unions.items():
        if g == 'TMEM266':
            continue
        overlaps = [(max(a,c), min(b,d)) for a,b in exons for c,d in intervals
                    if max(a,c) < min(b,d)]
        shared[g] = merge(overlaps)
    assert len(exons) == 15 and sum(b-a for a,b in exons) == 5265
    receipt = {'url': ANNOT_URL, 'bytes': len(b), 'sha256': digest(b),
               'assembly': 'hg38', 'annotation': 'GENCODE v26',
               'coordinate_system': '0-based half-open', 'exons': exons,
               'other_gene_exon_overlaps': shared, 'source_response': raw}
    (BASE/'culture-exon-annotation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return exons, merge([x for v in shared.values() for x in v])

class RemoteBW:
    def __init__(self, url):
        self.url, self.total, self.receipts, self.cache = url, 0, [], {}
        h = struct.unpack('<IHHQQQHHQQIQ', self.read(0,64))
        assert h[0] == 0x888ffc26 and h[1] == 4
        self.ct, self.index, self.uncompressed_size = h[3], h[5], h[10]
        self.chromosomes = {}
        magic, block, self.keysize, valsize, count, reserved = struct.unpack(
            '<IIIIQQ',self.read(self.ct,32))
        assert magic == 0x78ca8c91 and valsize == 8
        self.chrom_node(self.ct+32)
        assert len(self.chromosomes) == count
        ih = struct.unpack('<IIQIIIIQII',self.read(self.index,48))
        assert ih[0] == 0x2468ace0

    def read(self, offset, size):
        key = (offset,size)
        if key in self.cache:
            return self.cache[key]
        assert 0 < size <= 200000 and self.total+size <= 5_000_000
        req = urllib.request.Request(self.url,headers={
            'Range': f'bytes={offset}-{offset+size-1}', 'Accept-Encoding':'identity'})
        with urllib.request.urlopen(req,timeout=30) as r:
            assert r.status == 206, 'Server did not honor bounded range'
            cr = r.headers.get('Content-Range','')
            assert cr.startswith(f'bytes {offset}-{offset+size-1}/'), cr
            b = r.read(size+1)
        assert len(b) == size
        self.total += len(b)
        self.receipts.append({'offset':offset,'size':size,'sha256':digest(b),
                              'content_range':cr})
        self.cache[key] = b
        return b

    def chrom_node(self, offset):
        leaf, reserved, count = struct.unpack('<BBH',self.read(offset,4))
        width = self.keysize+8
        data = self.read(offset+4,count*width)
        for j in range(count):
            p = j*width
            name = data[p:p+self.keysize].rstrip(b'\0').decode()
            val = data[p+self.keysize:p+width]
            if leaf:
                self.chromosomes[name] = struct.unpack('<II',val)
            else:
                self.chrom_node(struct.unpack('<Q',val)[0])

    def blocks(self, offset, chrom, start, end):
        leaf, reserved, count = struct.unpack('<BBH',self.read(offset,4))
        width = 32 if leaf else 24
        data = self.read(offset+4,count*width)
        out = set()
        for j in range(count):
            row = struct.unpack_from('<IIIIQQ' if leaf else '<IIIIQ',data,j*width)
            sc,sb,ec,eb,child = row[:5]
            if (sc,sb) >= (chrom,end) or (ec,eb) <= (chrom,start):
                continue
            if leaf:
                out.add((child,row[5]))
            else:
                out.update(self.blocks(child,chrom,start,end))
        return out

    def intervals(self, chrom, start, end):
        cid = self.chromosomes[chrom][0]
        out = []
        for offset,size in sorted(self.blocks(self.index+48,cid,start,end)):
            compressed = self.read(offset,size)
            data = zlib.decompress(compressed) if self.uncompressed_size else compressed
            assert len(data) <= (self.uncompressed_size or len(data))
            p = 0
            while p < len(data):
                tid,first,last,step,span,kind,reserved,count = struct.unpack_from('<IIIIIBBH',data,p)
                p += 24
                assert kind in (1,2,3)
                for j in range(count):
                    if kind == 1:
                        a,b,v = struct.unpack_from('<IIf',data,p); p += 12
                    elif kind == 2:
                        a,v = struct.unpack_from('<If',data,p); b=a+span; p += 8
                    else:
                        v = struct.unpack_from('<f',data,p)[0]; p += 4
                        a=first+j*step; b=a+span
                    assert a < b and v >= 0
                    if tid == cid and a < end and b > start:
                        out.append((max(a,start),min(b,end),v))
            assert p == len(data)
        out.sort()
        assert all(out[i][1] <= out[i+1][0] for i in range(len(out)-1)), 'Overlapping coverage records'
        return out

def quantify(intervals, regions):
    counts = []
    for start,end in regions:
        pieces = [(max(a,start),min(b,end),v) for a,b,v in intervals
                  if a < end and b > start]
        counts.append({'start':start,'end':end,'length':end-start,
                       'coverage_sum':sum((b-a)*v for a,b,v in pieces),
                       'covered_bases':sum(b-a for a,b,v in pieces if v>0),
                       'max_coverage':max((v for a,b,v in pieces),default=0),
                       'coverage_segments':pieces})
    return counts

def main():
    exons,shared = annotation()
    result = {'scope':'One source-authenticated EMC culture, two technical runs',
              'coordinates':'hg38 / GENCODE v26 / 0-based half-open',
              'units':'Sum of aligned base coverage, not reads or molecules',
              'format_references':[
                  'https://raw.githubusercontent.com/dpryan79/libBigWig/master/bwRead.c',
                  'https://raw.githubusercontent.com/dpryan79/libBigWig/master/bwValues.c'],
              'runs':{}}
    for run, expected in EXPECTED.items():
        u=('https://duffel.rail.bio/recount3/human/data_sources/sra/base_sums/'
           f'67/SRP073267/{run[-2:]}/sra.base_sums.SRP073267_{run}.ALL.bw')
        bw=RemoteBW(u)
        intervals=bw.intervals('chr15',exons[0][0],exons[-1][1])
        rows=quantify(intervals,exons)
        shared_rows=quantify(intervals,shared)
        total=sum(r['coverage_sum'] for r in rows)
        shared_total=sum(r['coverage_sum'] for r in shared_rows)
        assert total == expected, (run,total,expected)
        result['runs'][run]={'url':u,'total_downloaded_bytes':bw.total,
             'gene_sum_reproduced':True,'gene_coverage_sum':total,
             'shared_exon_coverage':shared_total,'nonshared_exon_coverage':total-shared_total,
             'exons':rows,'shared_intervals':shared_rows,'range_receipts':bw.receipts}
        print(run, 'coverage', total, 'shared',shared_total,'unique',total-shared_total,
              'bytes',bw.total,flush=True)
    (BASE/'culture-exon-coverage-results.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    main()
