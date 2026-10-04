"""Optional source recovery, assembled from the worker's executed steps.

This assembled file has been syntax-checked, not rerun end to end. The original
worker executed the archive decoder and the source matching steps separately.
It uses public sources in memory and compares against the frozen map/controls;
it never rewrites the frozen map. A future run needs ~26 MB network retrieval.
The R reader supports this pinned serialization, not arbitrary R files.
"""
import collections
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tarfile
import urllib.request
import zlib

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / '.cache/python-deps'))
import numpy as np


class R:
    def __init__(self, b):
        self.b, self.p, self.refs = b, 7, []
        self.i(); self.i(); self.i()

    def i(self):
        n = struct.unpack_from('>i', self.b, self.p)[0]
        self.p += 4
        return n

    def obj(self):
        flag = self.i()
        typ, attr, tag = flag & 255, bool(flag & 512), bool(flag & 1024)
        if typ == 254:
            return None
        if typ == 255:
            return self.refs[(flag >> 8) - 1]
        if typ == 1:
            v = self.obj(); self.refs.append(v)
            return ('symbol', v)
        if typ == 9:
            n = self.i()
            if n < 0:
                return None
            v = self.b[self.p:self.p+n].decode(); self.p += n
            return v
        if typ == 2:
            at = self.obj() if attr else None
            ta = self.obj() if tag else None
            ca, cd = self.obj(), self.obj()
            return ('pair', ta, ca, cd, at)
        if typ in [10, 13, 14]:
            n = self.i()
            fmt, sz = ('d', 8) if typ == 14 else ('i', 4)
            v = struct.unpack_from('>' + str(n) + fmt, self.b, self.p)
            self.p += n * sz
        elif typ in [16, 19]:
            n = self.i(); v = [self.obj() for _ in range(n)]
        else:
            raise ValueError((self.p, flag, typ))
        at = self.obj() if attr else None
        return {'type': typ, 'v': v, 'a': at}


def main():
    archive_url = 'https://ftp.gwdg.de/pub/misc/bioconductor/packages/3.18/data/annotation/src/contrib/hugene10stv1probe_2.18.0.tar.gz'
    with urllib.request.urlopen(archive_url, timeout=40) as f:
        b = f.read(15_000_001)
    assert len(b) == 14_658_244
    archive_sha = hashlib.sha256(b).hexdigest()
    assert archive_sha == '2d2fc3d5627b0e7d5b86490f4f528a732d017278a86faf812311c81a7883c6b2'
    with tarfile.open(fileobj=io.BytesIO(b), mode='r:gz') as t:
        d = gzip.decompress(t.extractfile('hugene10stv1probe/data/hugene10stv1probe.rda').read())
    assert len(d) == 54_267_174
    r = R(d); cols = r.obj()[2]['v']
    assert r.p == len(d) and len(cols[0]['v']) == 861_493
    physical = {}
    for seq, x, y, pid in zip(cols[0]['v'], cols[1]['v'], cols[2]['v'], cols[3]['v']):
        pid = int(pid)
        assert pid == x + 1050*y + 1
        if pid in physical:
            assert physical[pid] == (x, y, seq)
        physical[pid] = (x, y, seq)
    assert len(physical) == 804_955

    gpl_url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL10739&targ=self&form=text&view=full'
    req = urllib.request.Request(gpl_url, headers={'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req, timeout=40) as f:
        prefix = f.read(10_000_000)
    assert prefix[:2] == b'\x1f\x8b'
    # This is a prefix, NOT an authenticated full-file hash or full download.
    s = zlib.decompressobj(31).decompress(prefix).decode('utf8', 'replace')
    table = s.split('!platform_table_begin', 1)[1].lstrip('\r\n')
    selected = [q for q in csv.DictReader(io.StringIO(table), delimiter='\t')
                if q.get('transcript_cluster_id') == '7985066']
    assert {int(q['ID']) for q in selected} == set(range(7985067, 7985080))
    assert sum(int(q['probe_count']) for q in selected) == 30

    seq_url = 'https://api.genome.ucsc.edu/getData/sequence?genome=hg19;chrom=chr15;start=76352319;end=76497124'
    with urllib.request.urlopen(seq_url, timeout=30) as f:
        reference_bytes = f.read(1_000_000)
    dna = json.loads(reference_bytes)['dna'].upper()
    origin = 76352319
    complement = str.maketrans('ACGT', 'TGCA')
    words = collections.defaultdict(list)
    for q in selected:
        child = int(q['ID']); start = int(q['RANGE_START'])-1; end = int(q['RANGE_STOP'])
        assert q['seqname'] == 'chr15'
        for a in range(start, end-24):
            plus = dna[a-origin:a-origin+25]
            words[plus].append((child, a, a+25, '+'))
            words[plus.translate(complement)[::-1]].append((child, a, a+25, '-'))
    recovered = []
    for pid, (x, y, seq) in physical.items():
        if seq not in words:
            continue
        assert len(words[seq]) == 1
        child, start, end, strand = words[seq][0]
        assert strand == '-'
        recovered.append(dict(physical_probe_id=pid, x=x, y=y, sequence=seq,
                              child_probeset=child, hg19_start0=start, hg19_end0=end))
    recovered.sort(key=lambda q: (q['child_probeset'], q['hg19_start0'], q['physical_probe_id']))
    assert len(recovered) == 30
    counts = collections.Counter(q['child_probeset'] for q in recovered)
    assert all(counts[int(q['ID'])] == int(q['probe_count']) for q in selected)
    frozen = list(csv.DictReader((BASE / 'probe-map.csv').open()))
    frozen = [{k: (v if k == 'sequence' else int(v)) for k, v in row.items()} for row in frozen]
    assert recovered == frozen

    targets = {q['physical_probe_id'] for q in recovered}
    pools = collections.defaultdict(list)
    for pid, (_, _, seq) in physical.items():
        if pid not in targets:
            pools[seq.count('G') + seq.count('C')].append(pid)
    pools = {k: sorted(v) for k, v in pools.items()}
    rng = np.random.default_rng(20261004)
    controls = [rng.choice(pools[q['sequence'].count('G') + q['sequence'].count('C')],
                          10, replace=False).tolist() for q in recovered]
    saved = json.loads((BASE / 'raw-array-results.json').read_text())
    assert controls == [q['controls'] for q in saved['controls']]
    out = {'archive_sha256': archive_sha, 'GPL10739_selected_rows': selected,
           'selected_rows_sha256': hashlib.sha256(json.dumps(selected, sort_keys=True).encode()).hexdigest(),
           'GPL_prefix_only_sha256': hashlib.sha256(prefix).hexdigest(),
           'reference_sha256': hashlib.sha256(reference_bytes).hexdigest(),
           'recovered_map': recovered, 'frozen_map_and_controls_verified': True}
    # Report only; do not mutate frozen evidence or prior output.
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
