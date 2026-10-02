"""Synthetic, literal oracle tests. Run in cloud after compiling the C++ checker."""
import csv
import gzip
import itertools
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from run_extrema_confirmation import certificates

ENGINE=Path(sys.argv.pop(1)).resolve() if len(sys.argv)>1 and not sys.argv[1].startswith("-") else None
T="ACGTCAGGATCCTAGC"
def normalize(s):
    return "".join(s.split()).upper().replace("U","T")
def windows(records):
    return [s[p:p+16] for _,seq in records for s in [normalize(seq)]
            for p in range(max(0,len(s)-15)) if set(s[p:p+16])<=set("ACGT")]
def distance(t,w):
    return sum(a!=b for a,b in zip(t,w))
def gap(t,w):
    # Deliberately brute-force definition, no extension logic or automaton.
    return max([0]+[r-l for l in range(6) for r in range(11,17) if t[l:r]==w[l:r]])
def oracle(t,records):
    ws=windows(records)
    return min([16]+[distance(t,w) for w in ws]),max([0]+[gap(t,w) for w in ws])
def mutate(t,positions):
    s=list(t)
    for p in positions:
        s[p]=next(c for c in "ACGT" if c!=s[p])
    return "".join(s)

class CertificateTests(unittest.TestCase):
    def engine(self,queries,records,compressed=False,kind="archived"):
        with tempfile.TemporaryDirectory() as name:
            p=Path(name);q=p/"q.tsv";f=p/("f.fa.gz" if compressed else "f.fa")
            q.write_text("".join(f"{ident}\t{t}\t{h}\t{g}\n" for ident,t,h,g in queries))
            body="".join(">"+(tx if kind=="archived" else f"{tx}|g|-|-|name|OTHER|{len(normalize(s))}|type|")+"\n"+s+"\n" for tx,s in records).rstrip("\n")
            if compressed:
                f.write_bytes(gzip.compress(body.encode()))
            else:
                f.write_text(body)
            prefix=p/"out"
            subprocess.run([str(ENGINE),str(q),str(f),kind,str(prefix)],check=True,capture_output=True,timeout=15)
            with (p/"out-certificates.tsv").open() as fh:
                got=list(csv.DictReader(fh,delimiter="\t"))
            self.assertEqual(len(got),len(queries))
            for row,(ident,t,h,g) in zip(got,queries):
                ws=windows(records)
                expected=min([3]+[distance(t,w) for w in ws if distance(t,w)<=h])
                self.assertEqual(row["design_id"],ident)
                self.assertEqual(int(row["hamming_found"]),expected)
                self.assertEqual(row["gap_attained"]=="1",g>0 and any(gap(t,w)>=g for w in ws))
                self.assertEqual(row["gap_exceeded"]=="1",any(gap(t,w)>g for w in ws))
            return got
    def check(self,t,records,h,g):
        row=self.engine([("q",t,h,g)],records)
        # A second genuinely empty stratum collection exercises union combination.
        other=[dict(design_id="q",hamming_found="3",gap_attained="0",gap_exceeded="0")]
        return certificates([dict(design_id="q",union_hamming=h,union_gap=g)], [row,other])
    def test_first_and_last_window(self):
        for seq in (T+"NN", "NN"+T, T):
            self.check(T,[("EWSR1:x",seq)],0,16)
    def test_no_record_bridge(self):
        records=[("EWSR1:a",T[:8]),("FUS:b",T[8:])]
        self.engine([("q",T,0,16)],records)
        with self.assertRaises(ValueError):
            self.check(T,records,0,16)
    def test_ambiguity_anywhere_in_full_window(self):
        for p in (0,4,5,10,11,15):
            seq=T[:p]+"N"+T[p+1:]
            self.engine([("q"+str(g),T,2,g) for g in (0,6,12,16)], [("EWSR1:x",seq)])
    def test_alignment_at_short_record_ends(self):
        # Core/tract matches without 16-base flanks must not count.
        for s in (T[1:],T[:-1],T[5:11],T[2:14]):
            self.engine([("q"+str(g),T,2,g) for g in (0,6,12,16)],[("FUS:x",s)])
    def test_core_orientation_all_single_mismatches(self):
        for p in range(16):
            records=[("FUS:x",mutate(T,[p]))]
            h,g=oracle(T,records)
            self.check(T,records,h,g)
    def test_distance_two_and_mutated_certificates(self):
        records=[("FUS:x",mutate(T,[0,15]))]
        self.assertEqual(oracle(T,records),(2,14))
        self.check(T,records,2,14)
        for h,g in ((1,14),(2,13),(2,15),(2,0)):
            with self.assertRaises(ValueError):
                self.check(T,records,h,g)
    def test_overstated_hamming_fails(self):
        records=[("FUS:x",mutate(T,[0]))]
        h,g=oracle(T,records)
        self.assertEqual(h,1)
        with self.assertRaises(ValueError):
            self.check(T,records,2,g)
    def test_unattained_radius_two_fails(self):
        records=[("FUS:x",mutate(T,[0,1,15]))]
        self.assertEqual(oracle(T,records)[0],3)
        with self.assertRaises(ValueError):
            self.check(T,records,2,13)
    def test_zero_gap_and_core(self):
        records=[("FUS:x",mutate(T,[5]))]
        self.assertEqual(oracle(T,records),(1,0))
        self.check(T,records,1,0)
        with self.assertRaises(ValueError):
            self.check(T,records,1,6)
    def test_normalization_gzip_gencode(self):
        records=[("tx1"," \tNN"+T.lower().replace("t","u")+"\nN")]
        self.engine([("q",T,0,16)],records,compressed=True,kind="gencode")
    def test_duplicate_sequence_aliases(self):
        self.engine([("a",T,0,16),("b",T,0,16)],[("EWSR1:x",T)])
    def test_random_threshold_challenges(self):
        rng=random.Random(1729)
        queries=[];records=[]
        for i in range(15):
            t="".join(rng.choice("ACGT") for _ in range(16))
            records.append(("FUS:"+str(i),"NN"+mutate(t,rng.sample(range(16),i%3))+"NN"))
            queries.append((str(i),t))
        challenges=[]
        for ident,t in queries:
            for h,g in itertools.product(range(3),(0,6,7,10,12,14,15,16)):
                challenges.append((ident+"_"+str(h)+"_"+str(g),t,h,g))
        self.engine(challenges,records)
    def test_missing_or_duplicate_certificates_rejected(self):
        d=[dict(design_id="q",union_hamming=0,union_gap=16)]
        r=dict(design_id="q",hamming_found="0",gap_attained="1",gap_exceeded="0")
        for collections in ([[],[r]],[[r,r],[r]],[[r]]):
            with self.assertRaises(ValueError):
                certificates(d,collections)
    def test_invalid_challenge_rejected(self):
        r=dict(design_id="q",hamming_found="0",gap_attained="1",gap_exceeded="0")
        for h,g in ((-1,16),(3,16),(0,-1),(0,5),(0,17)):
            with self.assertRaises(ValueError):
                certificates([dict(design_id="q",union_hamming=h,union_gap=g)],[[r],[r]])
if __name__=="__main__":
    if ENGINE is None:
        raise SystemExit("Usage: test_extrema_certificate.py /path/to/compiled/extrema-certificate")
    unittest.main()
