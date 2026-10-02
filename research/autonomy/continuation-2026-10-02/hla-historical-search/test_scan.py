import io,itertools,unittest
from scan_historical_fasta import scan,positions

class Oracle(unittest.TestCase):
    def test_exhaustive_short_patterns(self):
        for n in range(7):
            for s in map(''.join,itertools.product('AB',repeat=n)):
                for m in range(1,4):
                    for q in map(''.join,itertools.product('AB',repeat=m)):
                        self.assertEqual(list(positions(s,q)),[i for i in range(len(s)-len(q)+1) if s[i:i+len(q)]==q])
    def test_wrapping_decoys_boundaries(self):
        r=scan(io.BytesIO(b'>sp|a\nNMPC\nVQAQY\n>DECOY_sp|a\nNMPCVQAQY\n>sp|b\nNMPC\n>sp|c\nVQAQY\n'))
        q=r['queries']['NMPCVQAQY']
        self.assertEqual(dict(q['occurrences']),{'swissprot_target':1,'decoy':1})
        self.assertEqual(r['records'],4)
    def test_ambiguity_and_stop_not_removed(self):
        r=scan(io.BytesIO(b'>sp|a\nNMPCXVQAQY*NMPCVQAQY\n'))
        self.assertEqual(r['queries']['NMPCVQAQY']['occurrences']['swissprot_target'],1)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):scan(io.BytesIO(b'>sp|a\nAA\n>sp|a\nBB\n'))
    def test_invalid_rejected(self):
        with self.assertRaises(ValueError):scan(io.BytesIO(b'>sp|a\nAA-BB\n'))
    def test_witness_cap(self):
        r=scan(io.BytesIO(b'>sp|a\n'+b'A'*24+b'\n'),queries=('AA',))['queries']['AA']
        self.assertEqual(r['occurrences']['swissprot_target'],23)
        self.assertTrue(r['witnesses_capped']);self.assertEqual(len(r['witnesses']),20)

if __name__=='__main__':unittest.main()
